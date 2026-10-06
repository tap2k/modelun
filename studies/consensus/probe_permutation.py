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
from analyze import answers

# --v3: the v3 field (census + expanded, 8 runs; analyze.py battery "combined") -> probes/<name>_v3.json
V3 = "--v3" in sys.argv

ans = answers(HERE, "combined" if V3 else "census")
models = sorted(m for m in ans if ans[m])
cats = sorted({c for m in models for c in ans[m]})

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

(HERE / "probes").mkdir(exist_ok=True)
if V3:   # the paper's within-lab pairs, on the v3 field
    result = [paired_perm(a, b) for a, b in [("claude-fable-5", "claude-sonnet-5"), ("gpt-5.6-sol", "gpt-5.6-luna"),
                                             ("claude-fable-5.1", "claude-sonnet-5.5")] if a in cell and b in cell]
else:
    result = paired_perm("claude-fable-5", "claude-sonnet-5")
out = "permutation_v3.json" if V3 else "permutation.json"
(HERE / "probes" / out).write_text(json.dumps(result, indent=1) + "\n")
for r in (result if V3 else [result]):
    print(f"{r['model_a']} vs {r['model_b']}: obs {r['obs_diff_bits']:.2f} bits over "
          f"{r['n_categories']} cats, paired-perm p = {r['p_two_sided']:.4f}")
print(f"-> probes/{out}")
