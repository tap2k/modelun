"""probe_brand_trend.py — within a lab, do newer releases leave the leader more, and agree with the field's pick more?

The lineage_trend.py design (census v3) on brand measures. Per model, over the 42 product categories:
  leave   share of categories where its modal answer differs from the panel's Name brand
  agree   share where its modal answer is the panel's consensus brand at that level
for the two-turn pick and for one-name Recommend. Within each family of >= 3 dated models, rank members by release
date; pooled statistic is the Spearman correlation between family-demeaned release rank and family-demeaned score;
null shuffles release order within each family (20,000 draws), two-sided. Reported for all families and for the six
major lineages (as in lineage_trend.py). The panel consensus includes each model itself (one of ~100).

    ../../.venv/bin/python probe_brand_trend.py      # -> probes/brand_trend.json
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "views"))
import brand_ladder as B  # noqa: E402
from build import release_dates  # noqa: E402

R = 20000
rng = np.random.default_rng(0)
MAJOR = ("claude", "gpt", "gemini", "grok", "qwen", "deepseek")


def scores(level):
    lv = B.levels()
    lad = json.loads((HERE / "probes" / "brand_ladder.json").read_text())["levels_specific"]
    name = {c: v[0] for c, v in lad["name"]["consensus"].items()}
    cons = {c: v[0] for c, v in lad[level]["consensus"].items()}
    out = {}
    for m, cats in lv[level].items():
        leave = agree = n = 0
        for c, xs in cats.items():
            picks = [x for x in xs if x != B.NO_PICK]
            if c in B.GENERIC or c not in cons or not picks:
                continue
            top = Counter(picks).most_common(1)[0][0]
            n += 1; leave += top != name[c]; agree += top == cons[c]
        if n >= 30:
            out[m] = {"leave": leave / n, "agree": agree / n}
    return out


def ranks(v):
    return np.argsort(np.argsort(v)).astype(float)


def pooled(order, sc):
    x, y = [], []
    for ms in order.values():
        r = np.arange(len(ms), dtype=float)
        s = np.array([sc[m] for m in ms])
        x += list(r - r.mean()); y += list(s - s.mean())
    return float(np.corrcoef(ranks(np.array(x)), ranks(np.array(y)))[0, 1])


def test(groups, sc):
    obs = pooled(groups, sc)
    null = np.array([pooled({f: list(rng.permutation(ms)) for f, ms in groups.items()}, sc) for _ in range(R)])
    return {"models": sum(len(v) for v in groups.values()), "spearman_demeaned": round(obs, 3),
            "p_two_sided": float((1 + (np.abs(null) >= abs(obs)).sum()) / (1 + R))}


def main():
    fam = {e["label"]: e["family"] for e in json.loads((HERE / "spec/models.json").read_text())["models"]}
    dates = release_dates()
    res = {}
    for level in ("pick2", "recommend_clamp"):
        s = scores(level)
        groups = defaultdict(list)
        for m in s:
            if m in dates and m in fam:
                groups[fam[m]].append(m)
        groups = {f: sorted(ms, key=lambda m: (dates[m], m)) for f, ms in groups.items() if len(ms) >= 3}
        major = {f: [m for m in groups.get(f, []) if not m.startswith("gemma")] for f in MAJOR if f in groups}
        for measure in ("leave", "agree"):
            sc = {m: v[measure] for m, v in s.items()}
            r = {"all": test(groups, sc), "major": test(major, sc),
                 "per_major": {f: round(float(np.corrcoef(np.arange(len(ms)), ranks(np.array([sc[m] for m in ms])))[0, 1]), 2)
                               for f, ms in major.items() if len(ms) >= 3}}
            res[f"{level}_{measure}"] = r
            print(f"{level:15} {measure:6} all n={r['all']['models']:3d} {r['all']['spearman_demeaned']:+.2f} p={r['all']['p_two_sided']:.3f}"
                  f"   major n={r['major']['models']:3d} {r['major']['spearman_demeaned']:+.2f} p={r['major']['p_two_sided']:.3f}   {r['per_major']}")
    (HERE / "probes" / "brand_trend.json").write_text(json.dumps(res, indent=1) + "\n")


if __name__ == "__main__":
    main()
