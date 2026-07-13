"""Roster-dependence checks for the surprisal metric ("aren't you just measuring the panel?").

The metric is panel-relative BY CONSTRUCTION (the panel-mean score is the field's entropy;
the median-split typing is panel-relative; novel-rate deflates with panel size). What this
script tests is whether the RANKINGS are roster artifacts. Three checks, zero new API calls:
  1. LOFO — leave-one-FAMILY-out: score each model against a field with ALL its
     relatives removed. If rankings shift a lot, sibling contamination is real.
  2. Balanced field — one random model per family (200 draws): does the ranking
     survive when no family can dominate the reference distribution?
  3. Random subsample — random 15-model fields (200 draws): rank stability under
     arbitrary roster perturbation.
Result on the 2026-07-04 data: rho = 0.989 LOO-vs-LOFO; the top 4 and sonnet-5-last hold
in every draw of both resampling checks. See OBSERVATIONS.md "Roster-dependence check".

    python studies/consensus/robustness.py
"""
import sys, json, math
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np

STUDY = Path(__file__).resolve().parent
sys.path.insert(0, str(STUDY))
from analyze import load

ans = load(STUDY)
models = sorted(m for m in ans if ans[m])
cats = sorted({c for m in models for c in ans[m]})

# plural merge, same as analyze.py
for c in cats:
    pool = Counter(a for m in models for a in ans[m].get(c, []))
    stems = {w: w[:-1] for w in pool if w.endswith('s') and w[:-1] in pool}
    for m in models:
        if c in ans[m]:
            ans[m][c] = [stems.get(a, a) for a in ans[m][c]]

meta = {m['label']: m for m in json.loads((STUDY / 'spec' / 'models.json').read_text())['models']}
fam = {m: (meta.get(m, {}).get('family') or m) for m in models}
fam_sizes = Counter(fam.values())
print("families (size>1):", {f: n for f, n in fam_sizes.most_common() if n > 1})

# --- release-era tiers (coarse, hand-assigned here, NOT in the frozen spec) ---
# The reference field's MODE MASS is set by whichever release cohort dominates the roster,
# and the roster is recency-skewed. This buckets models into three release eras so a
# cohort-UNIFORM reference field can be drawn (equal models per era), neutralizing the
# skew. Boundaries are coarse on purpose — the test only needs the newest cohort to stop
# dominating the mode, not fine dating (half the roster is beyond the assigner's cutoff).
#   0 = heirloom / ~2023-early-2024   1 = ~late-2024-2025   2 = 2026 / newest flagships
ERA = {
    # tier 0 — old
    'claude-3-haiku': 0, 'gpt-3.5-turbo': 0, 'gpt-4-turbo': 0, 'mixtral-8x22b-instruct': 0,
    'mythomax-l2-13b': 0, 'wizardlm-2-8x22b': 0,
    # tier 1 — mid
    'gpt-4o': 1, 'gpt-4o-mini-2024-07-18': 1, 'gpt-4.1': 1, 'gpt-5': 1,
    'gemini-2.5-flash': 1, 'gemma-3-27b-it': 1, 'llama-3.3-70b-instruct': 1,
    'llama-4-maverick': 1, 'qwen-2.5-72b-instruct': 1, 'qwen3-235b-a22b-2507': 1,
    'deepseek-chat-v3-0324': 1, 'deepseek-r1': 1, 'ernie-4.5-vl-424b-a47b': 1,
    'hunyuan-a13b-instruct': 1, 'command-a': 1, 'palmyra-x5': 1, 'sonar': 1, 'hermes-4-70b': 1,
    # tier 2 — newest
    'claude-haiku-4.5': 2, 'claude-sonnet-4.6': 2, 'claude-opus-4.8': 2, 'claude-sonnet-5': 2,
    'claude-fable-5': 2, 'gpt-5.4': 2, 'gpt-5.5': 2, 'gpt-5.6-sol': 2, 'gpt-5.6-terra': 2,
    'gpt-5.6-luna': 2, 'gemini-3.1-pro-preview': 2, 'gemini-3.5-flash': 2, 'grok-4.3': 2,
    'grok-4.20': 2, 'grok-4.5': 2, 'deepseek-v3.2': 2, 'deepseek-v4-flash': 2, 'glm-4.7': 2,
    'kimi-k2.5': 2, 'granite-4.1-8b': 2,
}
missing = [m for m in models if m not in ERA]
if missing:
    print("WARNING: no era assigned (excluded from cohort draw):", missing)
era = {m: ERA[m] for m in models if m in ERA}
by_era = defaultdict(list)
for m, e in era.items():
    by_era[e].append(m)
print("era sizes:", {e: len(by_era[e]) for e in sorted(by_era)})

def surprisal(m, field):
    """mean -log2 P(answer | field's answers), add-one smoothed. field excludes m already."""
    ss = []
    for c in cats:
        mine = ans[m].get(c, [])
        others = [a for o in field for a in ans[o].get(c, [])]
        if not mine or not others:
            continue
        pool = Counter(others)
        total, vocab = sum(pool.values()), len(set(others) | set(mine))
        ss.extend(-math.log2((pool.get(a, 0) + 1) / (total + vocab)) for a in mine)
    return float(np.mean(ss))

def ranks(scores):
    order = sorted(scores, key=lambda m: -scores[m])
    return {m: i + 1 for i, m in enumerate(order)}

def spearman(r1, r2):
    ks = list(r1)
    a = np.array([r1[k] for k in ks], float)
    b = np.array([r2[k] for k in ks], float)
    return float(np.corrcoef(a, b)[0, 1])

# --- baseline LOO (reproduce analyze.py) and LOFO ---
loo = {m: surprisal(m, [o for o in models if o != m]) for m in models}
lofo = {m: surprisal(m, [o for o in models if fam[o] != fam[m]]) for m in models}
r_loo, r_lofo = ranks(loo), ranks(lofo)

print(f"\nLOO vs LOFO: spearman rho = {spearman(r_loo, r_lofo):.3f}")
print(f"{'model':30} {'LOO':>5} {'LOFO':>5} {'d_surp':>7} {'rankLOO':>8} {'rankLOFO':>9} {'drank':>6}")
for m in sorted(models, key=lambda m: -(lofo[m] - loo[m])):
    print(f"{m:30} {loo[m]:5.2f} {lofo[m]:5.2f} {lofo[m]-loo[m]:+7.2f} "
          f"{r_loo[m]:8d} {r_lofo[m]:9d} {r_loo[m]-r_lofo[m]:+6d}")

# --- balanced field: one model per family, 200 draws ---
rng = np.random.default_rng(7)
by_fam = defaultdict(list)
for m in models:
    by_fam[fam[m]].append(m)

def draw_ranks(field_fn, n_draws=200):
    rank_acc = defaultdict(list)
    for _ in range(n_draws):
        for m in models:
            field = field_fn(m)
            rank_acc[m].append(surprisal(m, field))
        # rank within this draw
        last = {m: rank_acc[m][-1] for m in models}
        rr = ranks(last)
        for m in models:
            rank_acc[m][-1] = rr[m]
    return {m: (float(np.median(v)), float(np.percentile(v, 5)), float(np.percentile(v, 95)))
            for m, v in rank_acc.items()}

def balanced_field(m):
    return [rng.choice([x for x in by_fam[f] if x != m])
            for f in by_fam if [x for x in by_fam[f] if x != m]]

def random_field(m):
    pool = [o for o in models if o != m]
    return list(rng.choice(pool, 15, replace=False))

# cohort-uniform: K models per release era (K = smallest era - 1, so m's own era can spare it).
K_ERA = min(len(v) for v in by_era.values()) - 1
def cohort_field(m):
    field = []
    for e in by_era:
        pool = [x for x in by_era[e] if x != m]
        field += list(rng.choice(pool, K_ERA, replace=False))
    return field

bal = draw_ranks(balanced_field)
sub = draw_ranks(random_field)
coh = draw_ranks(cohort_field)
print(f"\ncohort-uniform field: {K_ERA} models/era x {len(by_era)} eras = {K_ERA*len(by_era)}-model reference")

print("\nrank stability (median rank [5th,95th pct] across 200 draws)")
print(f"{'model':30} {'era':>3} {'full-LOO':>8} {'balanced':>16} {'random15':>16} {'cohort-unif':>16}")
for m in sorted(models, key=lambda m: r_loo[m]):
    b, s, c = bal[m], sub[m], coh[m]
    print(f"{m:30} {era.get(m,'?'):>3} {r_loo[m]:8d} {b[0]:6.0f} [{b[1]:2.0f},{b[2]:2.0f}] "
          f"{s[0]:8.0f} [{s[1]:2.0f},{s[2]:2.0f}] {c[0]:8.0f} [{c[1]:2.0f},{c[2]:2.0f}]")

# headline: does the recency-neutralized field preserve the ranking / keep sonnet-5 at the floor?
r_coh_med = ranks({m: -coh[m][0] for m in models})  # rank of the median cohort-rank (lower rank# = more divergent)
print(f"\nLOO vs cohort-uniform (median ranks): spearman rho = {spearman(r_loo, r_coh_med):.3f}")
last = max(models, key=lambda m: r_loo[m])
print(f"panel-last under full-LOO: {last} (rank {r_loo[last]}) -> cohort-uniform median rank {coh[last][0]:.0f} [{coh[last][1]:.0f},{coh[last][2]:.0f}]")
top4 = sorted(models, key=lambda m: r_loo[m])[:4]
print("top-4 under full-LOO, their cohort-uniform median [5,95]:")
for m in top4:
    print(f"  {m:30} {coh[m][0]:.0f} [{coh[m][1]:.0f},{coh[m][2]:.0f}]")
