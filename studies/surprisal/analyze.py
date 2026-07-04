"""
analyze.py — the surprisal study's spine: Contract-A transcripts -> answer-choice metrics.

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

    python studies/surprisal/analyze.py [--study studies/surprisal]
"""

import re
import json
import math
import argparse
from pathlib import Path
from collections import Counter

import numpy as np

EMOJI = re.compile(r'[\U0001F000-\U0001FAFF☀-➿]')
PUNCT = re.compile(r'[*_`#>\[\]().,!?"\':;]')
WORD = re.compile(r'^[a-z\-]+$|^\d+$')


def norm(ans):
    """Reply -> one normalized token. Last alphabetic word (sentence-final answer position)
    handles models that ignore the clamp ('A common color is blue.' -> 'blue')."""
    if not ans:
        return None
    a = EMOJI.sub(' ', PUNCT.sub(' ', ans.strip().lower()))
    words = [w for w in a.split() if WORD.match(w)]
    return words[-1] if words else None


def load(study_dir):
    """transcripts/*.json (Contract A) -> {label: {scene_id: [normalized answer per run]}}"""
    out = {}
    for p in sorted((study_dir / "transcripts").glob("*.json")):
        d = json.loads(p.read_text())
        scenes = {}
        for sid, sc in d["scenes"].items():
            toks = [norm(run[0].get("reply")) for run in sc["runs"] if run]
            toks = [t for t in toks if t]
            if toks:
                scenes[sid] = toks
        out[d["model"]] = scenes
    return out


def analyze(study_dir):
    ans = load(study_dir)
    models = sorted(m for m in ans if ans[m])
    cats = sorted({c for m in models for c in ans[m]})

    # plural merge within each category pool (cats/cat -> cat when both occur)
    for c in cats:
        pool = Counter(a for m in models for a in ans[m].get(c, []))
        stems = {w: w[:-1] for w in pool if w.endswith('s') and w[:-1] in pool}
        for m in models:
            if c in ans[m]:
                ans[m][c] = [stems.get(a, a) for a in ans[m][c]]

    per_model, per_cat_surp = {}, {m: {} for m in models}
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
            per_cat_surp[m][c] = float(np.mean(cat_s))
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

    # bootstrap 90% CI over categories
    rng = np.random.default_rng(7)
    for m in models:
        cs = list(per_cat_surp[m])
        if not cs:
            continue
        boots = [float(np.mean([per_cat_surp[m][c] for c in rng.choice(cs, len(cs))]))
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
    args = ap.parse_args()
    study_dir = Path(args.study)

    result = analyze(study_dir)
    out = study_dir / "analysis.json"
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
