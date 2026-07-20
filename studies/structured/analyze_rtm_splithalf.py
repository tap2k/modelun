"""Concern-1 prototype: regression-to-the-mean / test-retest null for the census score.

Split the 4 plain-chat samples per cell into two halves (2+2), recompute per-model surprisal
on each half, and use the half-vs-half spread as an empirical noise null. Gives:
  (1) test-retest reliability r of the per-model census score (Spearman-Brown-corrected to n=4);
  (2) the RTM-predicted Δ for a model at baseline X:  (1 - r) * (X - mean);
  (3) each JSON-compressor's observed Δ in units of the pure-noise Δ-SD.
SD of a half-sample score (SD_2) ≈ SD of the 4-sample (json - plain) delta under pure noise,
so observed Δ_json / SD_2 is a conservative z for "is this more than re-measurement noise?".
"""
import importlib.util
import io
import math
import random
import statistics as st
from collections import Counter
from contextlib import redirect_stdout
from pathlib import Path

_spec = importlib.util.spec_from_file_location("fmt_analyze", Path(__file__).resolve().parent / "analyze.py")
A = importlib.util.module_from_spec(_spec)
with redirect_stdout(io.StringIO()):
    _spec.loader.exec_module(A)

labels, cats = A.labels, A.cats_json
s_plain, s_json = A.s_plain, A.s_fmt["json"]
mean_plain = sum(s_plain.values()) / len(labels)

# Precompute the guarded plain answers once (list per model per cat).
PLAIN = {l: {c: list(A.plain_answers(l, c)) for c in cats} for l in labels}

def half_tables(rng):
    """Randomly split each cell's samples into halves A and B (alternating after shuffle)."""
    tA, tB = {l: {} for l in labels}, {l: {} for l in labels}
    for l in labels:
        for c in cats:
            xs = PLAIN[l][c][:]
            rng.shuffle(xs)
            tA[l][c] = xs[0::2]
            tB[l][c] = xs[1::2]
    return tA, tB

R = 300
rng = random.Random(20260720)
sA_rep = {l: [] for l in labels}
sB_rep = {l: [] for l in labels}
rel_per_split = []
for _ in range(R):
    tA, tB = half_tables(rng)
    sA = A.surprisal(lambda l, c: tA[l][c], cats)
    sB = A.surprisal(lambda l, c: tB[l][c], cats)
    for l in labels:
        if not math.isnan(sA[l]):
            sA_rep[l].append(sA[l])
        if not math.isnan(sB[l]):
            sB_rep[l].append(sB[l])
    # test-retest correlation across models for this split
    xs = [sA[l] for l in labels]
    ys = [sB[l] for l in labels]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    vx = sum((x - mx) ** 2 for x in xs); vy = sum((y - my) ** 2 for y in ys)
    rel_per_split.append(cov / math.sqrt(vx * vy))

r2 = sum(rel_per_split) / len(rel_per_split)          # reliability of a 2-sample score
r4 = 2 * r2 / (1 + r2)                                  # Spearman-Brown up to 4 samples
print(f"test-retest reliability: r_2(2-sample) = {r2:.3f}  ->  r_4(4-sample, Spearman-Brown) = {r4:.3f}")

# per-model noise scale: SD of half-sample score ~= SD of the 4-sample json-plain delta
sd2 = {l: st.pstdev(sA_rep[l] + sB_rep[l]) for l in labels}

TARGETS = ["deepseek-v3.2", "gpt-4o-mini-2024-07-18", "gpt-4-turbo", "gpt-5.6-sol",
           "qwen3-235b-a22b-2507", "gemini-3.1-pro-preview", "hermes-4-70b",
           "llama-4-maverick", "llama-3.3-70b-instruct", "mythomax-l2-13b"]

print(f"\n{'model':26}{'plainX':>8}{'Δjson':>8}{'RTMpred':>9}{'noiseSD':>9}{'Δ/SD':>8}")
print("-" * 70)
for l in TARGETS:
    if l not in s_plain:
        print(f"  ?? {l} not found"); continue
    X = s_plain[l]
    dj = s_json[l] - X
    rtm = (1 - r4) * (X - mean_plain)     # expected regression under pure noise (toward the mean)
    z = dj / sd2[l] if sd2[l] else float("nan")
    print(f"{l:26}{X:>8.2f}{dj:>+8.2f}{-rtm:>+9.2f}{sd2[l]:>9.3f}{z:>8.1f}")

print(f"\nmean_plain = {mean_plain:.2f}; RTMpred column is the shrinkage RTM alone predicts "
      f"(negative for above-mean models).")
print(f"field-mean noise SD (median over models): {st.median(sd2.values()):.3f}")
