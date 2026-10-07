"""probe_modal_score.py — a per-model score that does not depend on sampling spread (census v3, review request).

Mode surprisal: for each model and category, the model's most frequent answer (ties share the weight equally),
scored against the pooled answers of every other model with the scorecard's add-one smoothing; the model's score is
the mean over categories. A model that samples widely but whose first choice is the field's scores low, so the
score separates what a model prefers from how far it spreads. Reported against the shipped scorecard: Spearman over
all models, the top and bottom ten, and the correlation of each score with self-distinctness. Zero API calls.

    ../../.venv/bin/python probe_modal_score.py   -> probes/modal_score_v3.json
"""
import json
import math
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from analyze import analyze, answers  # noqa: E402
from v3_tables import pools, spearman  # noqa: E402

ans = answers(HERE, "combined")
pm = analyze(HERE, "combined", ans=ans)["per_model"]
P = pools(ans)
models = sorted(pm)


def mode_surprisal(m):
    s = []
    for c, mine in ans[m].items():
        if not mine:
            continue
        pool = Counter()
        for o, cnt in P[c].items():
            if o != m:
                pool.update(cnt)
        if not pool:
            continue
        own = Counter(mine)
        top = max(own.values())
        modes = [a for a, n in own.items() if n == top]
        tot, vocab = sum(pool.values()), len(set(pool) | set(mine))
        s.append(np.mean([-math.log2((pool.get(a, 0) + 1) / (tot + vocab)) for a in modes]))
    return float(np.mean(s))


ms = {m: mode_surprisal(m) for m in models}
full = {m: pm[m]["surprisal"] for m in models}
sd = {m: pm[m]["self_distinct"] for m in models}
order = lambda d, rev: sorted(models, key=lambda m: -d[m] if rev else d[m])
res = {"models": len(models),
       "spearman_mode_vs_scorecard": round(spearman([ms[m] for m in models], [full[m] for m in models]), 3),
       "pearson_scorecard_vs_self_distinct": round(float(np.corrcoef([full[m] for m in models], [sd[m] for m in models])[0, 1]), 3),
       "pearson_mode_vs_self_distinct": round(float(np.corrcoef([ms[m] for m in models], [sd[m] for m in models])[0, 1]), 3),
       "top10_mode": [[m, round(ms[m], 2)] for m in order(ms, True)[:10]],
       "bottom10_mode": [[m, round(ms[m], 2)] for m in order(ms, False)[:10]],
       "top10_scorecard": order(full, True)[:10], "bottom10_scorecard": order(full, False)[:10],
       "per_model": {m: {"mode_surprisal": round(ms[m], 3), "surprisal": round(full[m], 3)} for m in models}}
print(f"mode surprisal vs scorecard: Spearman {res['spearman_mode_vs_scorecard']:+.3f}; "
      f"r with self-distinctness: scorecard {res['pearson_scorecard_vs_self_distinct']:+.2f}, mode {res['pearson_mode_vs_self_distinct']:+.2f}")
print("top10 mode:", res["top10_mode"])
print("bottom10 mode:", res["bottom10_mode"])
print("top10 scorecard:", res["top10_scorecard"])
print("bottom10 scorecard:", res["bottom10_scorecard"])
(HERE / "probes/modal_score_v3.json").write_text(json.dumps(res, indent=1) + "\n")
print("-> probes/modal_score_v3.json")
