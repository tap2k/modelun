"""
analyze.py — the consensus study's spine: Contract-A transcripts -> answer-choice metrics.

The datum is a model's DISCRETE CHOICE on a wide-answer-space category ("Name a color."),
one-word-clamped. Everything is exact-match on normalized tokens: no embeddings, no judge,
no cleaner — mechanical and recomputable from the transcripts with stdlib + numpy.

Per model:
  surprisal   = mean -log2 P(answer | all OTHER models' answers), leave-one-out, add-one
                smoothed. High = picks answers the field doesn't. (The headline.)
  modal_avoid = fraction of answers != the field's modal answer for that category
  novel_rate  = fraction of answers NO other model ever gave (the strongest tell)
  self_distinct = distinct answers / runs, within-model (spread axis)
The (surprisal x self_distinct) median-split gives the 2x2 typing:
  true-contrarian (stable different defaults) / explorer (samples off-modal) /
  consensus-fixed / consensus-sampler.

Provenance: this metric was reverse-engineered from deepseek-v3.2's behavior in the
convergence study and validated by a scratch probe (see studies/convergence/OBSERVATIONS.md):
deepseek #1 with 25% novel answers; ernie-4.5 INVERTED from embedding-#1 to dead last once
verbosity couldn't help (the smoking-gun for the verbosity confound); tree->oak 58/58.

    python studies/consensus/analyze.py [--study studies/consensus]
"""

import re
import unicodedata
import json
import math
import argparse
from pathlib import Path
from collections import Counter

import numpy as np

EMOJI = re.compile(r'[\U0001F000-\U0001FAFF☀-➿]')
PUNCT = re.compile(r'[*_`#>\[\]().,!?"\':;]')
WORD = re.compile(r'^[a-z][a-z0-9&\-]*$|^\d+$')


JUNK = re.compile(r'<think>|<thought>|\bthinking\b', re.I)
ACK = re.compile(r'^\s*(okay|ok|sure|certainly|alright)[.!]?\s*$', re.I)


# v3 scoring (2026-10-01, after a category-by-category review of all three batteries). v2's numbers
# reproduce from the consensus-arxiv-v2 tag.
THINK_END = re.compile(r'</think>|</thought>', re.I)
TEMPLATE = re.compile(r'\[/?INST\]|<\|[^|>]*\|>', re.I)
STOP_AT = re.compile(r'</output>|</user>|</end>|<start>|</输出>|\bASSISTANT:|^###|\n###|```|"\},\{|\[Binary_ID\]', re.I)
TAG = re.compile(r'<[^>]*>')
NOT_ANSWER = {'the', 'a', 'an', 'let', 'with', 'but', 'and', 'or', 'of', 'to', 'okay', 'specify', 'context', 'please'}


LEAD_IN_LINE = re.compile(r"^\s*(?:(?:sure|okay|ok|here|since you)\b.*|i'?ll just\b.*|i will\b.*|.*\s.*:|thought|thinking)\s*$", re.I)
ASIDE = re.compile(r"^\s*(?:\*[^*]+\*|\(.*\))\s*$")
LEAK = re.compile(r"^\s*(?:the user\b|okay, the user|\d+\.\s|\*?hmm\b|let me\b|we need to\b|we are to\b|a chat between\b)", re.I)
SELF_CORRECT = re.compile(r"^\s*wait\b", re.I)


def clean(ans):
    """Strip what wraps an answer before scoring: everything up to a closed reasoning block, chat-template
    tokens, a leading 'ASSISTANT:', anything after a stop marker (a leaked next turn, a code fence, JSON
    debris), leftover tags. Then take the first line that is an answer, skipping lead-ins ('Sure, here is
    one:'), a bare 'thought' marker, and asides ('*ponders*') when an answer follows: a model's choice is
    its first answer, not its afterthought ('Cadbury\n\nor if you meant...'). A self-correction ('Wait,
    that's two words. One word: Stonehenge') replaces it. A reply that opens as leaked reasoning ('The user
    wants...') and reasoning that never closed are junk, as before."""
    if not ans:
        return None
    if re.search(r'<think>|<thought>', ans, re.I) and not THINK_END.search(ans):
        return None                      # reasoning that never closed: no answer, only a leak
    parts = THINK_END.split(ans)
    a = TEMPLATE.sub(' ', parts[-1])
    a = re.sub(r'^\s*ASSISTANT:\s*', '', a, flags=re.I)
    a = STOP_AT.split(a)[0]
    a = TAG.sub(' ', a)
    lines = [x.strip() for x in a.split('\n') if re.search(r'\w', x)]
    if lines and LEAK.match(lines[0]):
        return None
    for ln in lines:
        if SELF_CORRECT.match(ln):
            return ln
    for i, ln in enumerate(lines):
        if LEAD_IN_LINE.match(ln) or (ASIDE.match(ln) and i < len(lines) - 1):
            continue
        return ln
    return None


def fold(text):
    return ''.join(ch for ch in unicodedata.normalize('NFKD', text) if not unicodedata.combining(ch))


def norm(ans):
    """Reply -> one normalized token. clean() first, then the last word (sentence-final answer position)
    handles models that ignore the clamp ('A common color is blue.' -> 'blue').
    Junk guard: an unclosed reasoning leak and essays (>15 words) are failed cells, NOT answers; a
    truncated chain-of-thought's last word would otherwise read as a fake 'novel' answer (reka-flash-3
    scored 4.85 on exactly this junk). Bare acknowledgments ('Okay.') are failed cells too, single-letter
    tokens are never answers, and neither are function words ('the', 'let'). Accents fold (souffle);
    '&' and letter-led digits survive (m&m, k2)."""
    ans = clean(ans)
    if not ans:
        return None
    if JUNK.search(ans) or ACK.match(ans) or len(ans.split()) > 15:
        return None
    a = EMOJI.sub(' ', PUNCT.sub(' ', fold(ans.strip().lower())))
    words = [w for w in a.split() if WORD.match(w) and (len(w) > 1 or w.isdigit())]
    return words[-1] if words and words[-1] not in NOT_ANSWER else None


# Generic head nouns per category: "<word> <head>" is one name, joined ("soysauce", "goldenretriever").
HEADS = {"sauce": {"sauce"}, "dog_breed": {"retriever", "shepherd", "terrier", "spaniel"},
         "toy": {"bear", "cube"}, "hat": {"hat", "cap"}, "weapon": {"weapon"}, "soup": {"soup"},
         "reptile": {"dragon"}, "landmark": {"tower"}, "plant": {"flytrap", "lily"}}


def compound(reply, heads):
    """A two- or three-word answer ending in a generic head noun of its category ('Soy sauce', 'Golden
    retriever') is one name: join it, so the last-word rule neither splits it nor merges it with others."""
    r = clean(reply)
    if not r:
        return None
    w = [x for x in PUNCT.sub(' ', fold(r.lower())).split() if x not in NOT_ANSWER]
    if 2 <= len(w) <= 3 and w[-1] in heads and all(WORD.match(x) for x in w):
        return ''.join(w)
    return None


# Each battery: its transcripts dir, its spec, and how a reply becomes a canonical answer.
BATTERIES = {"census": ("transcripts", "stimulus.json"),
             "expanded": ("transcripts-expanded", "stimulus_expanded.json"),
             "brands": ("transcripts-brands", "stimulus_brands.json")}


def scorer(battery):
    """(reply -> answer, plural_merge). Brands score whole names (brands.brand_name), whose alias table
    does the variant merging, so the census's one-word plural merge does not run on them."""
    if battery == "brands":
        from brands import brand_name
        return brand_name, False
    return norm, True


def load(study_dir, battery="census"):
    """<battery transcripts>/*.json (Contract A) -> {label: {scene_id: [answer per run]}}"""
    normf, _ = scorer(battery)
    out = {}
    for p in sorted((study_dir / BATTERIES[battery][0]).glob("*.json")):
        d = json.loads(p.read_text())
        scenes = {}
        for sid, sc in d["scenes"].items():
            heads = HEADS.get(sid) if normf is norm else None
            toks = [(heads and compound(run[0].get("reply"), heads)) or normf(run[0].get("reply"))
                    for run in sc["runs"] if run]
            toks = [t for t in toks if t]
            if toks:
                scenes[sid] = toks
        out[d["model"]] = scenes
    return out


COMBINED = ("census", "expanded")   # same template and scoring: together, one 96-category census


def answers(study_dir, battery="census"):
    """load(), the variant merge (answer_variants.json: "variants" for the census, "expanded" for the expanded
    battery), then the plural merge within each category pool (cats/cat -> cat when both occur)."""
    if battery == "combined":
        out = {}
        for b in COMBINED:
            for m, cats in answers(study_dir, b).items():
                out.setdefault(m, {}).update(cats)
        return out
    ans = load(study_dir, battery)
    if battery in ("census", "expanded"):
        var = json.loads((study_dir / "answer_variants.json").read_text())
        var = var["variants"] if battery == "census" else var["expanded"]["variants"]
        for m in ans:
            for c in ans[m]:
                if c in var:   # a variant mapped to null is a fragment, not an answer
                    ans[m][c] = [x for x in (var[c].get(a, a) for a in ans[m][c]) if x]
    if scorer(battery)[1]:
        models = [m for m in ans if ans[m]]
        for c in {c for m in models for c in ans[m]}:
            pool = Counter(a for m in models for a in ans[m].get(c, []))
            stems = {w: w[:-1] for w in pool if w.endswith('s') and w[:-1] in pool}
            for m in models:
                if c in ans[m]:
                    ans[m][c] = [stems.get(a, a) for a in ans[m][c]]
    return ans


def analyze(study_dir, battery="census", ans=None):
    """ans: answers(study_dir, battery), when the caller already has it."""
    ans = ans if ans is not None else answers(study_dir, battery)
    models = sorted(m for m in ans if ans[m])
    cats = sorted({c for m in models for c in ans[m]})

    per_model, per_cat_surp = {}, {m: {} for m in models}  # per-answer surprisals by category
    for m in models:
        surp, avoid, novel, selfd = [], [], [], []
        for c in cats:
            mine = ans[m].get(c, [])
            others = [a for o in models if o != m for a in ans[o].get(c, [])]
            if not mine or not others:
                continue
            pool = Counter(others)
            total, vocab = sum(pool.values()), len(set(others) | set(mine))
            modal = pool.most_common(1)[0][0]
            cat_s = []
            for a in mine:
                p = (pool.get(a, 0) + 1) / (total + vocab)
                cat_s.append(-math.log2(p))
                avoid.append(0.0 if a == modal else 1.0)
                novel.append(1.0 if pool.get(a, 0) == 0 else 0.0)
            surp.extend(cat_s)
            per_cat_surp[m][c] = cat_s
            selfd.append(len(set(mine)) / len(mine))
        per_model[m] = {
            "surprisal": float(np.mean(surp)),
            "modal_avoid": float(np.mean(avoid)),
            "novel_rate": float(np.mean(novel)),
            "self_distinct": float(np.mean(selfd)),
            "n_answers": len(surp),
        }

    # 2x2 typing by median split
    med_s = float(np.median([v["surprisal"] for v in per_model.values()]))
    med_d = float(np.median([v["self_distinct"] for v in per_model.values()]))
    for m, v in per_model.items():
        hi_s, hi_d = v["surprisal"] > med_s, v["self_distinct"] > med_d
        v["type"] = ("explorer" if hi_s and hi_d else
                     "true-contrarian" if hi_s else
                     "consensus-sampler" if hi_d else "consensus-fixed")

    # bootstrap 90% CI: resample categories, pool per-answer surprisals — same
    # answer-weighted estimand as the headline mean (a per-category-mean bootstrap
    # would target a different quantity when cells fail unevenly)
    rng = np.random.default_rng(7)
    for m in models:
        cs = list(per_cat_surp[m])
        if not cs:
            continue
        boots = [float(np.mean([s for c in rng.choice(cs, len(cs))
                                for s in per_cat_surp[m][c]]))
                 for _ in range(2000)]
        per_model[m]["ci90"] = [float(np.percentile(boots, 5)), float(np.percentile(boots, 95))]

    # per-category field view: modal answer + concentration
    per_cat = {}
    for c in cats:
        pool = Counter(a for m in models for a in ans[m].get(c, []))
        if not pool:
            continue
        modal, n = pool.most_common(1)[0]
        per_cat[c] = {"modal": modal, "modal_share": n / sum(pool.values()),
                      "n_distinct": len(pool), "n_answers": sum(pool.values())}

    # metadata passthrough
    meta_path = study_dir / "spec" / "models.json"
    meta = {m["label"]: m for m in json.loads(meta_path.read_text())["models"]} if meta_path.exists() else {}
    for m in per_model:
        per_model[m].update({k: meta.get(m, {}).get(k) for k in ("family", "origin", "open")})

    return {"per_model": per_model, "per_category": per_cat,
            "n_models": len(models), "n_categories": len(cats)}


def main():
    ap = argparse.ArgumentParser(description="Surprisal analysis: transcripts -> analysis.json")
    ap.add_argument("--study", default=str(Path(__file__).resolve().parent))
    ap.add_argument("--battery", choices=BATTERIES, default="census",
                    help="census writes analysis.json; another battery writes analysis_<battery>.json")
    args = ap.parse_args()
    study_dir = Path(args.study)

    result = analyze(study_dir, args.battery)
    out = study_dir / ("analysis.json" if args.battery == "census" else f"analysis_{args.battery}.json")
    out.write_text(json.dumps(result, indent=1) + "\n")
    print(f"→ {out}  ({result['n_models']} models × {result['n_categories']} categories)\n")

    pm = result["per_model"]
    print(f"{'model':<20}{'surprisal':>10}{'CI90':>15}{'avoid':>7}{'novel':>7}{'selfd':>7}   type")
    for m in sorted(pm, key=lambda x: -pm[x]["surprisal"]):
        v = pm[m]
        ci = f"[{v['ci90'][0]:.2f},{v['ci90'][1]:.2f}]" if "ci90" in v else ""
        print(f"{m:<20}{v['surprisal']:>10.2f}{ci:>15}{v['modal_avoid']:>7.0%}"
              f"{v['novel_rate']:>7.0%}{v['self_distinct']:>7.0%}   {v['type']}")

    pc = result["per_category"]
    full = sorted((c for c, v in pc.items() if v["modal_share"] >= 0.8),
                  key=lambda c: -pc[c]["modal_share"])
    tags = ", ".join("{}→{}({:.0%})".format(c, pc[c]["modal"], pc[c]["modal_share"]) for c in full)
    print("\nhigh-convergence categories (modal ≥80%): " + tags)


if __name__ == "__main__":
    main()
