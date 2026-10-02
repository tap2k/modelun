"""probe_choose.py — "Name a X" vs "Choose a X" across the panel.

The census asks for an example ("Name a fruit"); one verb changed asks for a pick ("Choose a fruit"). Same
91-model panel, 8 samples, both batteries: core (transcripts/ + transcripts-extra/, 4+4, vs transcripts-choose/)
and expanded (transcripts-expanded/ vs transcripts-expanded-choose/). Only models with every scene answered
under both verbs are compared. Per model and category, both verbs use the same number of answers (the smaller
of the two, up to 8), and a cell with fewer than 4 scoreable answers under either verb is dropped, so one
unscoreable reply does not drop a model.

Per battery: the share of answers on each category's consensus answer, leave-one-out surprisal (bits, add-one
smoothed), distinct favorites across models, which consensus answers change, and whether a model's surprisal
(its distance from the field) keeps its rank across verbs.

    ../../.venv/bin/python probe_choose.py     # -> probes/choose.json
"""
import json, math, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from analyze import answers, against, load


def read(dirs, battery, field):
    out = {}
    for d in dirs:
        for m, cats in against(field, load(HERE, battery, paths=sorted((HERE / d).glob("*.json"))), HERE, battery).items():
            for c, xs in cats.items():
                out.setdefault(m, {}).setdefault(c, []).extend(xs)
    return out


def paired(N, C, cats, floor=4):
    """Same answer count per model and category under both verbs; cells below floor dropped from both."""
    PN, PC = {}, {}
    for m in set(N) & set(C):
        for c in cats:
            k = min(len(N[m].get(c, [])), len(C[m].get(c, [])), 8)
            if k >= floor:
                PN.setdefault(m, {})[c] = N[m][c][:k]
                PC.setdefault(m, {})[c] = C[m][c][:k]
    return PN, PC


def stats(A, models, cats):
    per_cat, per_model = {}, Counter()
    for c in cats:
        ms = [m for m in models if c in A[m]]
        pool = Counter(x for m in ms for x in A[m][c])
        n = sum(pool.values())
        s = []
        for m in ms:
            others = pool - Counter(A[m][c])
            tot, vocab = sum(others.values()), len(set(others) | set(A[m][c]))
            v = [-math.log2((others[a] + 1) / (tot + vocab)) for a in A[m][c]]
            s += v; per_model[m] += sum(v) / len(v) / len(A[m])
        top, k = pool.most_common(1)[0]
        favs = {Counter(A[m][c]).most_common(1)[0][0] for m in ms}
        per_cat[c] = {"consensus": top, "share": round(k / n, 3), "surprisal": round(sum(s) / len(s), 3),
                      "distinct_favorites": len(favs)}
    return per_cat, per_model


def spearman(a, b):
    ks = sorted(a)
    ra = {k: r for r, k in enumerate(sorted(ks, key=a.get))}
    rb = {k: r for r, k in enumerate(sorted(ks, key=b.get))}
    n = len(ks)
    return 1 - 6 * sum((ra[k] - rb[k]) ** 2 for k in ks) / (n * (n * n - 1))


def battery(name_dirs, choose_dir, battery_name, spec):
    field = answers(HERE, battery_name)
    cats = [s["id"] for s in json.loads((HERE / "spec" / spec).read_text())["scenes"]]
    N, C = read(name_dirs, battery_name, field), read([choose_dir], battery_name, field)
    N, C = paired(N, C, cats)
    models = sorted(N)
    (pn, mn), (pc, mc) = stats(N, models, cats), stats(C, models, cats)
    avg = lambda p, k: round(sum(v[k] for v in p.values()) / len(p), 3)
    flips = {c: [pn[c]["consensus"], pc[c]["consensus"], pn[c]["share"], pc[c]["share"]]
             for c in cats if pn[c]["consensus"] != pc[c]["consensus"]}
    sharper = {c: [pc[c]["consensus"], pn[c]["share"], pc[c]["share"]] for c in cats if pc[c]["share"] > pn[c]["share"]}
    cells = sum(len(N[m]) for m in models)
    return {"models": len(models), "categories": len(cats), "cells": f"{cells}/{len(models) * len(cats)}",
            "name": {k: avg(pn, k) for k in ("share", "surprisal", "distinct_favorites")},
            "choose": {k: avg(pc, k) for k in ("share", "surprisal", "distinct_favorites")},
            "consensus_changed": f"{len(flips)}/{len(cats)}", "flips": flips, "choose_sharper": sharper,
            "model_surprisal_rank_rho": round(spearman(mn, mc), 3),
            "per_category": {c: {"name": pn[c], "choose": pc[c]} for c in cats}}


def main():
    res = {"core": battery(["transcripts", "transcripts-extra"], "transcripts-choose", "census", "stimulus.json"),
           "expanded": battery(["transcripts-expanded"], "transcripts-expanded-choose", "expanded", "stimulus_expanded.json")}
    (HERE / "probes" / "choose.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
    for b, r in res.items():
        print(f"{b}: {r['models']} models x {r['categories']} categories; name {r['name']} | choose {r['choose']}; "
              f"consensus changed {r['consensus_changed']}; choose sharper in {len(r['choose_sharper'])}; "
              f"model surprisal rank rho {r['model_surprisal_rank_rho']}")


if __name__ == "__main__":
    main()
