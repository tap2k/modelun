"""probe_permutation.py — paired permutation test for the within-lab dissociation.

The Fable-5 vs Sonnet-5 gap (1.76 vs 1.06) is the paper's marquee within-lab result,
but the marginal bootstrap CIs overlap slightly. A paired permutation over categories
has far more power because it controls for category difficulty: under the null that the
two models are exchangeable, relabeling which answers came from which model WITHIN each
category is valid. Statistic = mean over categories of (mean surprisal_A - mean
surprisal_B); 10k permutations; two-sided p.

Note: per-answer surprisals are scored leave-one-out against the full 39-model field, so a
permuted label shifts one model in/out of the reference pool --- a negligible effect at
this panel size, and the same for both models. No new API calls.

    ../../.venv/bin/python probe_permutation.py   -> probes/permutation.json
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

# per (model, category) leave-one-out surprisals, add-one smoothed
cell = {m: {} for m in models}
for m in models:
    for c in cats:
        mine = ans[m].get(c, [])
        others = [a for o in models if o != m for a in ans[o].get(c, [])]
        if not mine or not others:
            continue
        pool = Counter(others)
        total, vocab = sum(pool.values()), len(set(others) | set(mine))
        cell[m][c] = [-math.log2((pool.get(a, 0) + 1) / (total + vocab)) for a in mine]

def paired_perm(mA, mB, nperm=10000, seed=7):
    rng = np.random.default_rng(seed)
    shared = [c for c in cats if cell[mA].get(c) and cell[mB].get(c)]
    obs = (np.mean([np.mean(cell[mA][c]) for c in shared])
           - np.mean([np.mean(cell[mB][c]) for c in shared]))
    hits = 0
    for _ in range(nperm):
        dA, dB = [], []
        for c in shared:
            pooled = np.array(cell[mA][c] + cell[mB][c])
            nA = len(cell[mA][c])
            perm = rng.permutation(pooled)
            dA.append(perm[:nA].mean())
            dB.append(perm[nA:].mean())
        if abs(np.mean(dA) - np.mean(dB)) >= abs(obs):
            hits += 1
    return {"model_a": mA, "model_b": mB, "n_categories": len(shared),
            "obs_diff_bits": float(obs), "n_perm": nperm,
            "p_two_sided": (hits + 1) / (nperm + 1)}

result = paired_perm("claude-fable-5", "claude-sonnet-5")
(HERE / "probes").mkdir(exist_ok=True)
(HERE / "probes" / "permutation.json").write_text(json.dumps(result, indent=1) + "\n")
print(f"Fable-5 vs Sonnet-5: obs {result['obs_diff_bits']:.2f} bits over "
      f"{result['n_categories']} cats, paired-perm p = {result['p_two_sided']:.4f}")
print("-> probes/permutation.json")
