"""probe_smoothing.py — is the scorecard an artifact of the add-one smoothing constant?

Recompute headline surprisal under alternative smoothing constants (add-0.5/2/0.1) and an
alternative vocabulary convention (V_c = support of the field only, vs the shipped union of
field and model support), and report Spearman rank correlation against the shipped add-one
ranking plus top/bottom stability. No new API calls.

    ../../.venv/bin/python probe_smoothing.py   -> probes/smoothing.json
"""

import json
import math
import sys
from pathlib import Path
from collections import Counter

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from analyze import load

ans = load(HERE)
models = sorted(m for m in ans if ans[m])
cats = sorted({c for m in models for c in ans[m]})
for c in cats:  # plural merge, identical to analyze.py
    pool = Counter(a for m in models for a in ans[m].get(c, []))
    stems = {w: w[:-1] for w in pool if w.endswith("s") and w[:-1] in pool}
    for m in models:
        if c in ans[m]:
            ans[m][c] = [stems.get(a, a) for a in ans[m][c]]

def mean_surp(alpha=1.0, vc="union"):
    out = {}
    for m in models:
        ss = []
        for c in cats:
            mine = ans[m].get(c, [])
            others = [a for o in models if o != m for a in ans[o].get(c, [])]
            if not mine or not others:
                continue
            pool = Counter(others)
            total = sum(pool.values())
            vocab = len(set(others) | set(mine)) if vc == "union" else len(set(others))
            ss += [-math.log2((pool.get(a, 0) + alpha) / (total + alpha * vocab)) for a in mine]
        out[m] = float(np.mean(ss))
    return out

def spearman(x, y):
    rx, ry = np.argsort(np.argsort(x)), np.argsort(np.argsort(y))
    return float(np.corrcoef(rx, ry)[0, 1])

base = mean_surp()
b = [base[m] for m in models]
top6 = sorted(models, key=lambda m: -base[m])[:6]
last = min(models, key=lambda m: base[m])

variants, out = [(0.5, "union", "add-0.5"), (2.0, "union", "add-2.0"),
                 (0.1, "union", "add-0.1"), (1.0, "others", "Vc=others-only")], []
for alpha, vc, name in variants:
    alt = mean_surp(alpha, vc)
    av = [alt[m] for m in models]
    rec = {"variant": name, "rho": round(spearman(b, av), 4),
           "top6_identical": sorted(models, key=lambda m: -alt[m])[:6] == top6,
           "last_identical": min(models, key=lambda m: alt[m]) == last}
    out.append(rec)
    print(f"{name:16} rho={rec['rho']:.4f}  top6={rec['top6_identical']}  last={rec['last_identical']}")

result = {"shipped": "add-1, Vc=union", "min_rho": min(r["rho"] for r in out),
          "all_top6_identical": all(r["top6_identical"] for r in out),
          "all_last_identical": all(r["last_identical"] for r in out), "variants": out}
(HERE / "probes").mkdir(exist_ok=True)
(HERE / "probes" / "smoothing.json").write_text(json.dumps(result, indent=1) + "\n")
print("-> probes/smoothing.json")
