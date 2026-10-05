"""v3_tables.py — the census paper's quantities on the v3 battery: 105 models x 96 categories (census + expanded)
x 8 runs (analyze.py battery "combined"). Zero API calls. Writes probes/v3_tables.json and prints a summary.

Surprisal stays relative to the field it is measured in (leave-one-out against the other models' answers), and
each snapshot is pinned by its git tag. Two quantities sit beside it:
  * field drift: how far the field's own answer distribution moves between snapshots, measured on the same 44
    models (the v2 panel) so roster change is held out: their July runs 1-4 (transcripts/) against their
    September-October runs 5-8 (transcripts-extra/), on the 31 census categories;
  * roster robustness: leave-one-family-out, and a balanced field of one model per family.

    ../../.venv/bin/python v3_tables.py
"""
import json
import math
import random
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
import sys
sys.path.insert(0, str(HERE))
from analyze import analyze, answers, against, load  # noqa: E402

V3 = "combined"
FAMILY = {e["label"]: e["family"] for e in json.loads((HERE / "spec/models.json").read_text())["models"]}
HYBRIDS = json.loads((HERE / "spec/runs.json").read_text())["hybrids"]


def v2_panel():
    """The 44 models of the published v2 scorecard, from the consensus-arxiv-v2 tag."""
    out = subprocess.run(["git", "ls-tree", "--name-only", "consensus-arxiv-v2", "transcripts/"], cwd=HERE,
                         capture_output=True, text=True, check=True).stdout.split()
    return sorted(Path(p).stem for p in out)


def spearman(a, b):
    r = lambda v: np.argsort(np.argsort(v)).astype(float)
    return float(np.corrcoef(r(np.asarray(a)), r(np.asarray(b)))[0, 1])


def pools(ans):
    """category -> model -> Counter of that model's answers."""
    out = defaultdict(dict)
    for m, cats in ans.items():
        for c, xs in cats.items():
            out[c][m] = Counter(xs)
    return out


def surprisal(m, ans, field_models, P):
    """Mean per-answer surprisal of m's answers against the pooled answers of field_models (m excluded), add-one
    smoothed, as analyze.analyze computes it."""
    s = []
    for c, mine in ans[m].items():
        pool = Counter()
        for o in field_models:
            if o != m and o in P[c]:
                pool.update(P[c][o])
        if not pool or not mine:
            continue
        tot, vocab = sum(pool.values()), len(set(pool) | set(mine))
        s += [-math.log2((pool.get(a, 0) + 1) / (tot + vocab)) for a in mine]
    return float(np.mean(s)) if s else None


def jsd(p, q):
    keys = set(p) | set(q)
    P, Q = np.array([p.get(k, 0) for k in keys], float), np.array([q.get(k, 0) for k in keys], float)
    P, Q = P / P.sum(), Q / Q.sum()
    M = (P + Q) / 2
    kl = lambda a, b: float(np.sum(a[a > 0] * np.log2(a[a > 0] / b[a > 0])))
    return (kl(P, M) + kl(Q, M)) / 2


def main():
    random.seed(0)
    ans = answers(HERE, V3)
    res = analyze(HERE, V3, ans=ans)
    pm, pc = res["per_model"], res["per_category"]
    models = sorted(pm, key=lambda m: -pm[m]["surprisal"])
    out = {"battery": "census + expanded, 8 runs", "n_models": len(models), "n_categories": len(pc)}

    # 1. scorecard
    out["scorecard"] = [{"model": m, **{k: pm[m][k] for k in ("surprisal", "ci90", "modal_avoid", "novel_rate",
                                                              "self_distinct", "type") if k in pm[m]}} for m in models]
    # 2. continuity with v2: the 44 published models, v2 battery (31 x 4, field = the 44) vs v3 (96 x 8, field = 105)
    p44 = [m for m in v2_panel() if m in pm]
    c4 = answers(HERE, "census")
    v2 = analyze(HERE, "census", ans={m: c4[m] for m in p44 if m in c4})["per_model"]
    both = [m for m in p44 if m in v2]
    out["continuity"] = {"models": len(both),
                         "spearman_v2_vs_v3": spearman([v2[m]["surprisal"] for m in both], [pm[m]["surprisal"] for m in both]),
                         "v2_top5": sorted(both, key=lambda m: -v2[m]["surprisal"])[:5],
                         "v3_top5_of_these": sorted(both, key=lambda m: -pm[m]["surprisal"])[:5],
                         "v2_bottom5": sorted(both, key=lambda m: v2[m]["surprisal"])[:5],
                         "v3_bottom5_of_these": sorted(both, key=lambda m: pm[m]["surprisal"])[:5]}
    # 3. substrate: concentration and the runner-up consensus
    shares = sorted(((c, v["modal"], v["modal_share"]) for c, v in pc.items()), key=lambda x: -x[2])
    P = pools(ans)
    runner = []
    for c, modal, share in shares:
        if share < 0.75:
            continue
        rest = Counter()
        for cnt in P[c].values():
            rest.update({a: n for a, n in cnt.items() if a != modal})
        if rest:
            a, n = rest.most_common(1)[0]
            runner.append({"category": c, "modal": modal, "modal_share": share, "runner_up": a,
                           "runner_up_share_of_non_modal": n / sum(rest.values())})
    out["substrate"] = {"categories_modal_ge_80": sum(s >= 0.8 for _, _, s in shares),
                        "median_modal_share": float(np.median([s for _, _, s in shares])),
                        "top10": shares[:10], "runner_up": runner}
    # 4. roster robustness
    loo = [pm[m]["surprisal"] for m in models]
    lofo = [surprisal(m, ans, [o for o in models if FAMILY.get(o) != FAMILY.get(m)], P) for m in models]
    fams = defaultdict(list)
    for m in models:
        fams[FAMILY.get(m)].append(m)
    bal = []
    for _ in range(50):
        field = [random.choice(v) for v in fams.values()]
        bal.append(spearman(loo, [surprisal(m, ans, field, P) for m in models]))
    cats = sorted(pc)
    halves = []
    for _ in range(50):
        random.shuffle(cats)
        h = set(cats[:len(cats) // 2])
        a = [surprisal(m, {m: {c: x for c, x in ans[m].items() if c in h}}, models, P) for m in models]
        b = [surprisal(m, {m: {c: x for c, x in ans[m].items() if c not in h}}, models, P) for m in models]
        ok = [i for i in range(len(models)) if a[i] is not None and b[i] is not None]
        halves.append(spearman([a[i] for i in ok], [b[i] for i in ok]))
    r = float(np.median(halves))
    out["robustness"] = {"spearman_loo_vs_lofo": spearman(loo, lofo),
                         "balanced_field_one_per_family_median_spearman": float(np.median(bal)),
                         "split_half_median_spearman": r, "spearman_brown": 2 * r / (1 + r)}
    # 5. field drift on the same 44 models: July runs 1-4 vs Sept-Oct runs 5-8, 31 census categories
    july = {m: c4[m] for m in p44 if m in c4}
    later = load(HERE, "census", paths=sorted((HERE / "transcripts-extra").glob("*.json")))
    later = {m: later[m] for m in p44 if m in later}
    against(c4, later, HERE, "census")
    common = [m for m in july if m in later]
    drift = []
    for c in sorted({c for m in common for c in july[m]}):
        a = Counter(x for m in common for x in july[m].get(c, []))
        b = Counter(x for m in common for x in later[m].get(c, []))
        if a and b:
            drift.append({"category": c, "july_modal": a.most_common(1)[0][0], "later_modal": b.most_common(1)[0][0],
                          "jsd_bits": jsd(a, b)})
    # the noise floor for drift: two random halves of the same 8 answers per model, pooled over the same models
    floor = []
    both8 = answers(HERE, "census8")
    for _ in range(20):
        js = []
        for c in [d["category"] for d in drift]:
            a, b = Counter(), Counter()
            for m in common:
                xs = list(both8.get(m, {}).get(c, []))
                random.shuffle(xs)
                a.update(xs[:len(xs) // 2]); b.update(xs[len(xs) // 2:])
            if a and b:
                js.append(jsd(a, b))
        floor.append(float(np.mean(js)))
    out["field_drift_same_44"] = {"models": len(common), "categories": len(drift),
                                  "modal_changed": [d for d in drift if d["july_modal"] != d["later_modal"]],
                                  "mean_jsd_bits": float(np.mean([d["jsd_bits"] for d in drift])),
                                  "split_half_floor_mean_jsd_bits": float(np.mean(floor))}
    # 6. the hybrids with reasoning off, scored against the as-served field (each without its own served answers)
    off = load(HERE, "census", paths=sorted((HERE / "transcripts-off").glob("*.json")))
    off_e = load(HERE, "expanded", paths=sorted((HERE / "transcripts-expanded-off").glob("*.json")))
    against(answers(HERE, "census8"), off, HERE, "census")
    against(answers(HERE, "expanded"), off_e, HERE, "expanded")
    rows = []
    for m in HYBRIDS:
        if m not in pm or m not in off or m not in off_e:
            continue
        o = {**off[m], **off_e[m]}
        s_off = surprisal("_off", {"_off": o}, [x for x in models if x != m], P)
        rows.append({"model": m, "served": pm[m]["surprisal"], "off": s_off})
    out["reasoning_arm"] = {"models": len(rows), "mean_served": float(np.mean([r["served"] for r in rows])),
                            "mean_off": float(np.mean([r["off"] for r in rows])),
                            "more_conventional_as_served": sum(r["served"] < r["off"] for r in rows), "rows": rows}
    (HERE / "probes" / "v3_tables.json").write_text(json.dumps(out, indent=1, default=float) + "\n")

    print(f"v3: {len(models)} models x {len(pc)} categories x 8 runs")
    sc = {m: pm[m]["surprisal"] for m in models}
    print("most divergent: " + ", ".join(f"{m} {sc[m]:.2f}" for m in models[:6]))
    print("most conformist: " + ", ".join(f"{m} {sc[m]:.2f}" for m in models[-6:]))
    c = out["continuity"]
    print(f"\ncontinuity, the 44 v2 models: Spearman v2 vs v3 {c['spearman_v2_vs_v3']:.2f}")
    print(f"  v2 top5 {c['v2_top5']}\n  v3 top5 {c['v3_top5_of_these']}\n  v2 bottom5 {c['v2_bottom5']}\n  v3 bottom5 {c['v3_bottom5_of_these']}")
    s = out["substrate"]
    print(f"\nsubstrate: {s['categories_modal_ge_80']} of 96 categories with one answer >= 80%; median modal share {s['median_modal_share']:.0%}")
    print("  runner-up share of non-modal answers: " + ", ".join(f"{r['category']} {r['runner_up']} {r['runner_up_share_of_non_modal']:.0%}" for r in s["runner_up"][:8]))
    rb = out["robustness"]
    print(f"\nrobustness: LOO vs LOFO {rb['spearman_loo_vs_lofo']:.3f}; one model per family {rb['balanced_field_one_per_family_median_spearman']:.3f}; "
          f"split-half {rb['split_half_median_spearman']:.2f} (Spearman-Brown {rb['spearman_brown']:.2f})")
    d = out["field_drift_same_44"]
    print(f"\nfield drift, same {d['models']} models July vs Sept-Oct, {d['categories']} census categories: mean JSD {d['mean_jsd_bits']:.3f} bits "
          f"(split-half floor {d['split_half_floor_mean_jsd_bits']:.3f}); modal changed in {len(d['modal_changed'])}: "
          + ", ".join(f"{x['category']} {x['july_modal']}->{x['later_modal']}" for x in d["modal_changed"]))
    ra = out["reasoning_arm"]
    print(f"\nreasoning arm, {ra['models']} hybrids: surprisal as served {ra['mean_served']:.2f}, off {ra['mean_off']:.2f}; "
          f"more conventional as served in {ra['more_conventional_as_served']}")


if __name__ == "__main__":
    main()
