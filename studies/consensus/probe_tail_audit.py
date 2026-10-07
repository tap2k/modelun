"""probe_tail_audit.py — is the scorecard's divergent tail divergence, or failure to answer? (census v3, review fix)

Reviewers read the top of the scorecard as possible instruction-following failure: the normalizer takes a reply's
last word ("Fedora is a type of hat" -> hat), and Phi-4 repeats category words. Per model, on the v3 battery
(analyze.py "combined": 96 categories x 8 runs, the paper's answers, rebuilt here reply by reply and checked equal
to answers()):
  failed      share of cells with no usable answer (no reply, or the junk guard drops it)
  multiword   share of answers whose cleaned reply has more than one word (compound names the census joins,
              "golden retriever", are not counted)
  echo        share of answers equal to a word of the category's own noun phrase ("hat" for "Name a hat")
  novel       share of answers no other model gave (analyze.py's novel_rate)
Then the scorecard re-scored by analyze.py's method (leave-one-out, add-one smoothed) with echoes and multi-word
answers dropped from every model, the field included: Spearman of all 105 scores before and after, and the top 10
before and after. Zero API calls.

    ../../.venv/bin/python probe_tail_audit.py   -> probes/tail_audit_v3.json
"""
import json
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from analyze import (BATTERIES, HEADS, PUNCT, VARIANT_TABLE, analyze, answers, clean, compound, fold,  # noqa: E402
                     norm)

PARTS = ("census8", "expanded")


def spearman(x, y):
    r = lambda v: np.argsort(np.argsort(v)).astype(float)
    return float(np.corrcoef(r(np.array(x)), r(np.array(y)))[0, 1])


STOP = {"a", "an", "the", "of", "name", "pick", "reply", "with", "one", "only", "word"}


def category_words(prompt):
    """'Name a board game. Reply with one word only.' -> {'board', 'game', 'boards', 'games'}; 'Pick a word.' ->
    {'word'}."""
    head = re.split(r"\.\s", prompt, maxsplit=1)[0].lower()
    ws = [w for w in re.findall(r"[a-z]+", head) if w not in STOP - {"word"}]
    ws = [w for w in ws if w not in {"name", "pick"}]
    return set(ws) | {w + "s" for w in ws}


def rows(battery):
    """{model: {category: [(answer, multiword, echo)]}} before the variant and plural merges, and
    {model: [cells, failed]}."""
    out, cells = {}, {}
    for d in BATTERIES[battery][0]:
        for p in sorted((HERE / d).glob("*.json")):
            t = json.loads(p.read_text())
            m = t["model"]
            cm = cells.setdefault(m, [0, 0])
            for sid, sc in t["scenes"].items():
                heads = HEADS.get(sid)
                for run in sc["runs"]:
                    cm[0] += 1
                    reply = run[0].get("reply") if run else None
                    joined = heads and compound(reply, heads)
                    a = joined or norm(reply)
                    if not a:
                        cm[1] += 1
                        continue
                    c = clean(reply) or ""
                    nwords = len([w for w in PUNCT.sub(" ", fold(c.lower())).split() if re.search(r"[a-z0-9]", w)])
                    cw = category_words(run[0]["u"])
                    out.setdefault(m, {}).setdefault(sid, []).append([a, bool(nwords > 1 and not joined), a in cw])
    return out, cells


def merged(battery):
    """rows() with answers()'s variant merge (null drops the answer and its flags) and plural merge applied."""
    r, cells = rows(battery)
    var = json.loads((HERE / "answer_variants.json").read_text())
    var = var["variants"] if VARIANT_TABLE[battery] == "census" else var["expanded"]["variants"]
    for m in r:
        for c in r[m]:
            if c in var:
                r[m][c] = [[var[c].get(a, a), mw, e] for a, mw, e in r[m][c] if var[c].get(a, a)]
    for c in {c for m in r for c in r[m]}:
        pool = {x[0] for m in r for x in r[m].get(c, [])}
        for m in r:
            for x in r[m].get(c, []):
                if x[0].endswith("s") and x[0][:-1] in pool:
                    x[0] = x[0][:-1]
    return r, cells


R, CELLS = {}, {}
for b in PARTS:
    r, cl = merged(b)
    for m, cats in r.items():
        R.setdefault(m, {}).update(cats)
    for m, (n, f) in cl.items():
        c = CELLS.setdefault(m, [0, 0])
        c[0] += n; c[1] += f

ref = answers(HERE, "combined")
mine = {m: {c: [x[0] for x in v] for c, v in cats.items()} for m, cats in R.items()}
assert {m: {c: v for c, v in cats.items() if v} for m, cats in mine.items() if cats} == \
       {m: {c: v for c, v in cats.items() if v} for m, cats in ref.items() if cats}, "rebuild differs from answers()"

before = analyze(HERE, "combined", ans=ref)["per_model"]
kept = {m: {c: [x[0] for x in v if not (x[1] or x[2])] for c, v in cats.items()} for m, cats in R.items()}
kept = {m: {c: v for c, v in cats.items() if v} for m, cats in kept.items()}
after = analyze(HERE, "combined", ans=kept)["per_model"]

models = sorted(before)
per = {}
for m in models:
    flat = [x for v in R[m].values() for x in v]
    per[m] = {"surprisal": round(before[m]["surprisal"], 3), "surprisal_clean": round(after[m]["surprisal"], 3),
              "failed": round(CELLS[m][1] / CELLS[m][0], 4), "multiword": round(np.mean([x[1] for x in flat]), 4),
              "echo": round(np.mean([x[2] for x in flat]), 4), "novel": round(before[m]["novel_rate"], 4),
              "novel_clean": round(after[m]["novel_rate"], 4)}
s0 = [per[m]["surprisal"] for m in models]; s1 = [per[m]["surprisal_clean"] for m in models]
top0 = sorted(models, key=lambda m: -per[m]["surprisal"])[:10]
top1 = sorted(models, key=lambda m: -per[m]["surprisal_clean"])[:10]
rank1 = {m: i + 1 for i, m in enumerate(sorted(models, key=lambda m: -per[m]["surprisal_clean"]))}
res = {"battery": "combined (census8 + expanded), 8 runs", "models": len(models),
       "field": {k: round(float(np.mean([per[m][k] for m in models])), 4) for k in ("failed", "multiword", "echo")},
       "dropped_answers": int(sum(len(v) for c in R.values() for v in c.values()) - sum(len(v) for c in kept.values() for v in c.values())),
       "spearman_before_after": round(spearman(s0, s1), 4),
       "top10_before": top0, "top10_after": top1, "top10_overlap": len(set(top0) & set(top1)),
       "top10_rank_after": {m: rank1[m] for m in top0}, "per_model": per}
for m in top0:
    p = per[m]
    print(f"{m:28} {p['surprisal']:.2f} -> {p['surprisal_clean']:.2f} (rank {rank1[m]:3d})  failed {p['failed']:.1%}  "
          f"multiword {p['multiword']:.1%}  echo {p['echo']:.1%}  novel {p['novel']:.1%} -> {p['novel_clean']:.1%}")
print(f"field: {res['field']}; dropped {res['dropped_answers']} answers; Spearman before/after {res['spearman_before_after']:.3f}; "
      f"top-10 overlap {res['top10_overlap']}")
(HERE / "probes/tail_audit_v3.json").write_text(json.dumps(res, indent=1) + "\n")
print("-> probes/tail_audit_v3.json")
