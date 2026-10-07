"""lineage_tier.py — does the within-lineage trend survive tier control? (census v3, review check)

lineage_trend.py walks each major provider's releases in date order, which mixes tiers (Gemini 2.5 Pro to 3.6 Flash;
Haiku, Sonnet and Opus; GPT mini). Here each major-provider model is assigned a tier by name, and the same statistic
(family-demeaned Spearman of release rank against surprisal, within-walk permutation null, 20,000 draws, seed 0) is
run (a) on lineage x tier walks of three or more, and (b) on the flagship tier alone. A stricter variant (c) splits
Claude by line (Haiku, Sonnet, Opus, Fable) and keeps walks of three or more; (d) and (e) repeat (a) without Claude
and with Claude's walks cut before Fable 5, as lineage_trend.py does.

Tier rule: small = a name part (after - or .) starting haiku, mini, nano, flash or lite, or is a Qwen open model of 35B total parameters
or fewer (qwen3.5-9b, qwen3.5-27b, qwen3.6-35b-a3b, qwen3.8-27b). Everything else is flagship.

    ../../.venv/bin/python lineage_tier.py   -> probes/lineage_tier_v3.json
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "views"))
from build import release_dates  # noqa: E402

R = 20000
MAJOR = ("claude", "gpt", "gemini", "grok", "qwen", "deepseek")
SMALL = re.compile(r"(^|[-.])(haiku|mini|nano|flash|lite)")  # "mini" must not match "gemini"
SMALL_QWEN = {"qwen3.5-9b", "qwen3.5-27b", "qwen3.6-35b-a3b", "qwen3.8-27b"}
sc = {r["model"]: r["surprisal"] for r in json.loads((HERE / "probes/v3_tables.json").read_text())["scorecard"]}
fam = {e["label"]: e["family"] for e in json.loads((HERE / "spec/models.json").read_text())["models"]}
dates = release_dates()
major = {f: sorted((m for m in sc if fam.get(m) == f and m in dates and not m.startswith("gemma")),
                   key=lambda m: (dates[m], m)) for f in MAJOR}


def tier(m):
    return "small" if SMALL.search(m) or m in SMALL_QWEN else "flagship"


def claude_line(m):
    return next((k for k in ("haiku", "sonnet", "opus", "fable") if k in m), "other")


def ranks(v):
    return np.argsort(np.argsort(v)).astype(float)


def pooled(g):
    x, y = [], []
    for ms in g.values():
        r = np.arange(len(ms), dtype=float); s = np.array([sc[m] for m in ms])
        x += list(r - r.mean()); y += list(s - s.mean())
    return float(np.corrcoef(ranks(np.array(x)), ranks(np.array(y)))[0, 1])


def test(g):
    g = {k: v for k, v in g.items() if len(v) >= 3}
    rng = np.random.default_rng(0)
    obs = pooled(g)
    null = np.array([pooled({k: list(rng.permutation(v)) for k, v in g.items()}) for _ in range(R)])
    return {"walks": len(g), "models": sum(map(len, g.values())), "spearman_demeaned": round(obs, 3),
            "p_two_sided": float((1 + (np.abs(null) >= abs(obs)).sum()) / (1 + R)),
            "per_walk": {k: {"n": len(v), "spearman": round(float(np.corrcoef(np.arange(len(v)), ranks(np.array([sc[m] for m in v])))[0, 1]), 2),
                             "walk": [[m, dates[m], round(sc[m], 2)] for m in v]} for k, v in g.items()}}


by_tier = {f"{f}/{tier(m)}": [] for f, ms in major.items() for m in ms}
for f, ms in major.items():
    for m in ms:
        by_tier[f"{f}/{tier(m)}"].append(m)
strict = dict(by_tier)
claude = strict.pop("claude/flagship") + strict.pop("claude/small", [])
for m in sorted(claude, key=lambda m: (dates[m], m)):
    strict.setdefault(f"claude/{claude_line(m)}", []).append(m)
strict = {k: sorted(v, key=lambda m: (dates[m], m)) for k, v in strict.items()}

res = {"rule": "small = a name part starting haiku|mini|nano|flash|lite, or Qwen open model <= 35B total; else flagship",
       "tiers": {m: tier(m) for ms in major.values() for m in ms},
       "all_major": test(major),
       "lineage_x_tier": test(by_tier),
       "flagship_only": test({f: [m for m in ms if tier(m) == "flagship"] for f, ms in major.items()}),
       "lineage_x_tier_claude_by_line": test(strict),
       "lineage_x_tier_without_claude": test({k: v for k, v in by_tier.items() if not k.startswith("claude")}),
       "lineage_x_tier_claude_before_gen5": test({k: [m for m in v if not (k.startswith("claude") and dates[m] >= dates["claude-fable-5"])]
                                                  for k, v in by_tier.items()})}
KEYS = ("all_major", "lineage_x_tier", "flagship_only", "lineage_x_tier_claude_by_line", "lineage_x_tier_without_claude",
        "lineage_x_tier_claude_before_gen5")
for k in KEYS:
    d = res[k]
    print(f"{k:30} walks={d['walks']:2d} n={d['models']:3d}  {d['spearman_demeaned']:+.2f}  p = {d['p_two_sided']:.4f}")
    for w, v in d["per_walk"].items():
        print(f"    {w:18} n={v['n']:2d} {v['spearman']:+.2f}")
(HERE / "probes/lineage_tier_v3.json").write_text(json.dumps(res, indent=1) + "\n")
print("-> probes/lineage_tier_v3.json")
