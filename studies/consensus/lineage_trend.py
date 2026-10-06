"""lineage_trend.py — does conformity rise within lineages, or only across a roster whose newer windows hold more
conformist labs? (census v3, "conformity rises within lineages")

Within each family of >= 3 models with release dates, rank its members by release date and correlate rank with
surprisal. Pooled statistic: Spearman between family-demeaned release rank and family-demeaned surprisal. Null:
shuffle release order within each family (20,000 draws), two-sided. Reported for every family of >= 3, and for the
six major providers (MAJOR: each has five or more releases in the panel; Google's lineage is Gemini, without the
open-weight Gemma models), with and without Claude's generation-5 releases (Fable 5 on), which break its walk.
Surprisal is the v3 scorecard (probes/v3_tables.json); dates are views/build.py release_dates().

    ../../.venv/bin/python lineage_trend.py   -> probes/lineage_trend_v3.json
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "views"))
from build import release_dates  # noqa: E402

R = 20000
rng = np.random.default_rng(0)
sc = {r["model"]: r["surprisal"] for r in json.loads((HERE / "probes/v3_tables.json").read_text())["scorecard"]}
fam = {e["label"]: e["family"] for e in json.loads((HERE / "spec/models.json").read_text())["models"]}
dates = release_dates()

groups = defaultdict(list)
for m in sc:
    if m in dates:
        groups[fam[m]].append(m)
groups = {f: sorted(ms, key=lambda m: (dates[m], m)) for f, ms in groups.items() if len(ms) >= 3}
undated = sorted(m for m in sc if m not in dates)


def ranks(v):
    return np.argsort(np.argsort(v)).astype(float)


def pooled(order):
    """order: family -> member list in the (possibly shuffled) release order."""
    x, y = [], []
    for ms in order.values():
        r = np.arange(len(ms), dtype=float)
        s = np.array([sc[m] for m in ms])
        x += list(r - r.mean()); y += list(s - s.mean())
    return float(np.corrcoef(ranks(np.array(x)), ranks(np.array(y)))[0, 1])


MAJOR = ("claude", "gpt", "gemini", "grok", "qwen", "deepseek")


def test(g):
    obs = pooled(g)
    null = np.array([pooled({f: list(rng.permutation(ms)) for f, ms in g.items()}) for _ in range(R)])
    return {"models": sum(len(v) for v in g.values()), "spearman_demeaned": round(obs, 3),
            "p_two_sided": float((1 + (np.abs(null) >= abs(obs)).sum()) / (1 + R))}


obs = pooled(groups)
null = np.array([pooled({f: list(rng.permutation(ms)) for f, ms in groups.items()}) for _ in range(R)])
major = {f: [m for m in groups[f] if not m.startswith("gemma")] for f in MAJOR}
cut = major["claude"].index("claude-fable-5")
major_pre5 = {**major, "claude": major["claude"][:cut]}
per_family = {f: {"n": len(ms), "spearman": round(float(np.corrcoef(np.arange(len(ms)), ranks(np.array([sc[m] for m in ms])))[0, 1]), 2),
                  "walk": [[m, dates[m], round(sc[m], 2)] for m in ms]} for f, ms in sorted(groups.items())}
res = {"families": len(groups), "models": sum(len(v) for v in groups.values()), "of": len(sc), "undated": undated,
       "spearman_demeaned": round(obs, 3), "p_two_sided": float((1 + (np.abs(null) >= abs(obs)).sum()) / (1 + R)),
       "draws": R, "major": test(major), "major_claude_before_gen5": test(major_pre5),
       "major_without_claude": test({f: v for f, v in major.items() if f != "claude"}),
       "major_walks": {f: [[m, dates[m], round(sc[m], 2)] for m in ms] for f, ms in major.items()},
       "major_per_lineage": {f: round(float(np.corrcoef(np.arange(len(ms)), ranks(np.array([sc[m] for m in ms])))[0, 1]), 2)
                             for f, ms in major.items()},
       "per_family": per_family}
print(f"{res['models']} of {res['of']} models in {res['families']} families of >= 3: demeaned Spearman {obs:+.2f}, "
      f"p = {res['p_two_sided']:.4f}")
for k in ("major", "major_claude_before_gen5", "major_without_claude"):
    print(f"  {k:26} n={res[k]['models']:3d}  {res[k]['spearman_demeaned']:+.2f}  p = {res[k]['p_two_sided']:.4f}")
for f, d in sorted(per_family.items(), key=lambda x: x[1]["spearman"]):
    print(f"  {f:12} n={d['n']:2d}  {d['spearman']:+.2f}")
if undated:
    print("undated (left out):", undated)
(HERE / "probes/lineage_trend_v3.json").write_text(json.dumps(res, indent=1) + "\n")
print("-> probes/lineage_trend_v3.json")
