"""probe_perturb.py — does the census's convergence survive small prompt changes?

Fifteen panel models (one current model per lab, plus older and smaller open models) are asked the 31
census categories, 8 samples each, under four specs in spec/perturb/: a same-day rerun of the original
(base), a generic system prompt (sysgen, "You are a helpful assistant."), a made-up identity (ava, "You are
Ava, a friendly assistant."), and one verb changed (choose, "Choose a color..." for "Name a color...").
Transcripts in transcripts-perturb/<variant>/.

Two questions, each against base and against base's own sampling noise (runs 0-3 vs 4-7, scaled to the
same sample size):
  convergence  does each model's answer stay concentrated? (top-answer share, distinct answers)
  item         does it converge on the same answer? (distribution overlap = 1 - total variation;
               whether the model's modal answer and the 15-model pooled modal answer match base)

    ../../.venv/bin/python probe_perturb.py      # -> probes/perturb.json
"""
import json, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from analyze import answers, against, load

VARIANTS = ["base", "sysgen", "ava", "choose"]


def variant(v, field):
    ans = load(HERE, "census", paths=sorted((HERE / "transcripts-perturb" / v).glob("*.json")))
    return against(field, ans, HERE)


def overlap(a, b):
    ca, cb = Counter(a), Counter(b)
    na, nb = len(a), len(b)
    return 1 - 0.5 * sum(abs(ca[t] / na - cb[t] / nb) for t in set(ca) | set(cb))


def top(xs):
    return Counter(xs).most_common(1)[0] if xs else (None, 0)


def summarize(V, ref, cmp_fn=None):
    """Per variant: mean top share, distinct answers, and against ref: overlap, modal kept, pooled modal kept."""
    out = {}
    models = sorted(set(ref) & set(V))
    cats = sorted({c for m in models for c in ref[m]})
    conc, dist, ov, keep = [], [], [], []
    for m in models:
        for c in cats:
            a, b = V[m].get(c, []), ref[m].get(c, [])
            if len(a) < 2 or len(b) < 2:
                continue
            conc.append(top(a)[1] / len(a)); dist.append(len(set(a)))
            ov.append(overlap(a, b)); keep.append(top(a)[0] == top(b)[0])
    pooled = sum(top([x for m in models for x in V[m].get(c, [])])[0] == top([x for m in models for x in ref[m].get(c, [])])[0]
                 for c in cats)
    n = len(conc)
    return {"cells": n, "top_share": round(sum(conc) / n, 3), "distinct": round(sum(dist) / n, 2),
            "overlap_with_ref": round(sum(ov) / n, 3), "model_modal_kept": round(sum(keep) / n, 3),
            "pooled_modal_kept": f"{pooled}/{len(cats)}"}


def main():
    field = answers(HERE)
    A = {v: variant(v, field) for v in VARIANTS}
    half = lambda D, s: {m: {c: xs[s] for c, xs in cats.items()} for m, cats in D.items()}
    res = {"noise_floor_base_half_vs_half": summarize(half(A["base"], slice(0, 4)), half(A["base"], slice(4, 8)))}
    for v in VARIANTS[1:]:
        res[v] = {"full": summarize(A[v], A["base"]),
                  "half_vs_base_half": summarize(half(A[v], slice(0, 4)), half(A["base"], slice(4, 8)))}
    res["base_full"] = summarize(A["base"], A["base"])
    flips = {}
    for v in VARIANTS[1:]:
        cats = sorted({c for m in A["base"] for c in A["base"][m]})
        mods = sorted(set(A["base"]) & set(A[v]))
        flips[v] = {c: [top([x for m in mods for x in A["base"][m].get(c, [])])[0], top([x for m in mods for x in A[v][m].get(c, [])])[0]]
                    for c in cats
                    if top([x for m in mods for x in A["base"][m].get(c, [])])[0] != top([x for m in mods for x in A[v][m].get(c, [])])[0]}
    res["pooled_flips"] = flips
    (HERE / "probes" / "perturb.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps(res, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
