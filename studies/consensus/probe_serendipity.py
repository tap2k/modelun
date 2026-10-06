"""probe_serendipity.py — the field's favourite word across release dates, prompt wordings and languages (census v3).

Share of replies containing "serendip" (any language's form: serendipia, serendipidade, serendipità, sérendipité),
per model, then pooled by release cohort. Prompts:
  census    "Pick a word." (census any_word, transcripts/ + transcripts-extra/, 8 runs)
  pick      "Pick any word." (language study pickword, en, + its extra runs)
  say       "Say any word." (pickword paraphrase, en)
  favorite  "What is your favorite word?" (pickword en_fav)
  beautiful "What is the most beautiful word in the English language?" (pickword en_beautiful)
  pt es it fr de   pickword in that language
Cohorts by release date (views/build.py release_dates()). Within lineages: each major provider's walk on "pick", and
the pooled family-demeaned Spearman of release rank against share (lineage_trend.py's statistic). Zero API calls.

    ../../.venv/bin/python probe_serendipity.py   -> probes/serendipity_v3.json
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LANG = HERE.parent / "language"
sys.path.insert(0, str(HERE / "views"))
from build import release_dates  # noqa: E402

FORM = ("serendip", "sérendip")
COHORTS = [("before 2025", "0000", "2025-01-01"), ("2025", "2025-01-01", "2026-01-01"),
           ("2026 H1", "2026-01-01", "2026-07-01"), ("2026 H2", "2026-07-01", "9999")]
MAJOR = ("claude", "gpt", "gemini", "grok", "qwen", "deepseek")
models = sorted(json.loads((HERE / "probes/v3_tables.json").read_text())["scorecard"], key=lambda r: r["model"])
models = [r["model"] for r in models]
dates = release_dates()
fam = {e["label"]: e["family"] for e in json.loads((HERE / "spec/models.json").read_text())["models"]}


def replies(dirs, scene):
    out = defaultdict(list)
    for d in dirs:
        for p in sorted(d.glob("*.json")):
            sc = json.loads(p.read_text())["scenes"].get(scene)
            for r in (sc or {}).get("runs", []):
                if r and r[0].get("reply"):
                    out[json.loads(p.read_text())["model"]].append(r[0]["reply"].lower())
    return out


def share(xs):
    return sum(any(f in x for f in FORM) for x in xs) / len(xs)


PW = [LANG / "transcripts_pickword", LANG / "transcripts_pickword_extra"]
PROMPTS = {"census": ([HERE / "transcripts", HERE / "transcripts-extra"], "any_word"),
           "pick": (PW, "en"), "say": ([LANG / "transcripts_pickword_paraphrase"], "en"),
           "favorite": (PW, "en_fav"), "beautiful": (PW, "en_beautiful"),
           **{lang: (PW, lang) for lang in ("pt", "es", "it", "fr", "de")}}

res = {"models_in_field": len(models), "prompts": {}}
per = {}
for k, (dirs, scene) in PROMPTS.items():
    rs = replies(dirs, scene)
    per[k] = {m: share(rs[m]) for m in models if rs.get(m)}
    coh = {}
    for name, lo, hi in COHORTS:
        ms = [m for m in per[k] if lo <= dates.get(m, "") < hi]
        if ms:
            coh[name] = {"models": len(ms), "share": round(float(np.mean([per[k][m] for m in ms])), 3)}
    res["prompts"][k] = {"models": len(per[k]), "share": round(float(np.mean(list(per[k].values()))), 3),
                         "undated": sorted(m for m in per[k] if m not in dates), "cohorts": coh}


def ranks(v):
    return np.argsort(np.argsort(v, kind="stable"), kind="stable").astype(float)


def pooled(g, k):
    x, y = [], []
    for ms in g.values():
        r = np.arange(len(ms), dtype=float); s = np.array([per[k][m] for m in ms])
        x += list(r - r.mean()); y += list(s - s.mean())
    return float(np.corrcoef(ranks(np.array(x)), ranks(np.array(y)))[0, 1])


rng = np.random.default_rng(0)
walks = {}
for k in ("census", "pick"):
    g = {f: sorted((m for m in per[k] if fam.get(m) == f and m in dates), key=lambda m: (dates[m], m)) for f in MAJOR}
    obs = pooled(g, k)
    null = np.array([pooled({f: list(rng.permutation(ms)) for f, ms in g.items()}, k) for _ in range(2000)])
    walks[k] = {"spearman_demeaned_major": round(obs, 3), "p_two_sided": float((1 + (np.abs(null) >= abs(obs)).sum()) / 2001),
                "walks": {f: [[m, dates[m], round(per[k][m], 2)] for m in ms] for f, ms in g.items()}}
res["within_lineage"] = walks
res["per_model"] = {k: {m: round(v, 3) for m, v in d.items()} for k, d in per.items()}

for k, d in res["prompts"].items():
    print(f"{k:10} n={d['models']:3d}  {d['share']:5.0%}  " + "  ".join(f"{c} {v['share']:.0%} ({v['models']})" for c, v in d["cohorts"].items()))
for k, w in walks.items():
    print(f"within lineage, {k}: major-provider demeaned Spearman {w['spearman_demeaned_major']:+.2f}, p = {w['p_two_sided']:.4f}")
(HERE / "probes/serendipity_v3.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
print("-> probes/serendipity_v3.json")
