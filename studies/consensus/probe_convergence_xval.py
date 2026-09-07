"""probe_convergence_xval.py — does one-word conformity predict open-ended convergence?

Construct check for the census, zero new API calls. The convergence study asked the same kind of
question (pick something, no clamp, free prose) and embedded the replies; its per-model
`uniqueness` is 1 - mean cosine to other families' replies on the same prompt (higher = more
distinct in open text), `self_consistency` is within-model cosine across runs. The census scores
the discrete one-word choice. If the two agree across the shared models, the cheap census reads
through to open-ended generation; if not, its claim stops at short-answer defaults.

    ../../.venv/bin/python probe_convergence_xval.py   # -> probes/convergence_xval.json + table
"""
import json
from pathlib import Path

import numpy as np


def pearsonr(x, y):
    return float(np.corrcoef(x, y)[0, 1])


def spearmanr(x, y, perms=20000, seed=7):
    """Spearman rho + two-sided permutation p (no scipy in the venv)."""
    rx, ry = np.argsort(np.argsort(x)), np.argsort(np.argsort(y))
    rho = pearsonr(rx, ry)
    rng = np.random.default_rng(seed)
    null = np.array([pearsonr(rx, rng.permutation(ry)) for _ in range(perms)])
    return rho, float(np.mean(np.abs(null) >= abs(rho)))

HERE = Path(__file__).resolve().parent
census = json.load(open(HERE / "analysis.json"))["per_model"]
conv = json.load(open(HERE.parent / "convergence/analysis.json"))["per_model"]
shared = sorted(set(census) & set(conv))

pairs = {
    "surprisal ~ uniqueness":            ("surprisal", "uniqueness"),
    "surprisal ~ conformity_field":      ("surprisal", "conformity_field"),
    "modal_avoid ~ uniqueness":          ("modal_avoid", "uniqueness"),
    "self_distinct ~ 1-self_consistency": ("self_distinct", "self_consistency"),
    "self_distinct ~ exact_dup_rate":    ("self_distinct", "exact_dup_rate"),
}
out = {"n": len(shared), "models": shared, "pairs": {}}
print(f"{len(shared)} shared models\n")
print(f"{'pair':38}{'spearman':>10}{'p':>8}{'pearson':>9}")
for name, (a, b) in pairs.items():
    x = np.array([census[m][a] for m in shared])
    y = np.array([conv[m][b] for m in shared])
    if b == "self_consistency":
        y = 1 - y
    rho, p = spearmanr(x, y); r = pearsonr(x, y)
    out["pairs"][name] = {"spearman": rho, "p": p, "pearson": r}
    print(f"{name:38}{rho:10.2f}{p:8.3f}{r:9.2f}")

print(f"\n{'model':26}{'census bits':>12}{'uniqueness':>12}{'conf_field':>12}")
for m in sorted(shared, key=lambda m: -census[m]["surprisal"]):
    print(f"{m:26}{census[m]['surprisal']:12.2f}{conv[m]['uniqueness']:12.3f}{conv[m]['conformity_field']:12.3f}")
s2 = [m for m in shared if m != "ernie-4.5-vl-424b-a47b"]   # convergence's known verbosity outlier (its README)
x = np.array([census[m]["surprisal"] for m in s2]); y = np.array([conv[m]["uniqueness"] for m in s2])
rho, p = spearmanr(x, y)
out["pairs"]["surprisal ~ uniqueness (no ernie)"] = {"spearman": rho, "p": p, "pearson": pearsonr(x, y), "n": len(s2)}
print(f"\nsurprisal ~ uniqueness without ernie: n={len(s2)} spearman {rho:.2f} p={p:.3f} pearson {pearsonr(x, y):.2f}")
out["table"] = {m: {"census_surprisal": census[m]["surprisal"], **{k: conv[m][k] for k in ("uniqueness", "conformity_field", "self_consistency", "exact_dup_rate")}} for m in shared}
(HERE / "probes/convergence_xval.json").write_text(json.dumps(out, indent=1) + "\n")
