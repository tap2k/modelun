"""pairwise.py — are any two models' answer CHOICES associated, beyond population structure?

Trigger: gpt-4-turbo and claude-fable-5 both say gouda + mustard + mango. Pair affinity,
or something the whole field does? Three nulls of increasing strictness — a ladder where
each level conditions away a population structure the previous level mistook for affinity:

  L1  rarity-weighted co-occurrence vs a random-partner null       ->  2/741 survive FDR
      confound: avoidance propensity (two habitual modal-avoiders beat a mostly-
      conformist null without any coupling)
  L2  + condition on avoidance: given both went off-modal, same off-modal answer?
                                                                   -> 15/741 survive
      confound: depth propensity — WHERE a model lands off-modal is a stable trait
      (opus-4.8 hits the field's #2-#3 100% of the time; hermes goes rank>=5 half
      the time). Two "runner-up club" members co-land on gouda/mustard/mango against
      any null that pools in the deep divers.
  L3  + condition on depth: deep-tail answers only (field rank>=4), null drawn from
      the field's deep-tail distribution, Monte Carlo p-values (the normal
      approximation overstates 1-2-match statistics badly)
                                                                   ->  0/741 survive

Verdict: no certified pairwise affinity. What looks like it is three population-level
structures: the modal consensus (the study's headline), the RUNNER-UP consensus (the
off-modal distribution has its own mode: mustard takes 93% of non-ketchup answers),
and a one-dimensional depth-propensity trait. Given a model's position on that trait,
its specific choices are exchangeable with the field's — even divergence is converged.
Caveat: 31 categories x 4 runs is low power; weak true affinities would be invisible.

Prints the two structure tables plus all three test levels.

    python studies/consensus/pairwise.py
"""
import sys
import json
import math
from pathlib import Path
from collections import Counter

import numpy as np

STUDY = Path(__file__).resolve().parent
sys.path.insert(0, str(STUDY))
from analyze import load

NSIM = 5000
DEEP_RANK = 4          # field rank >= this counts as deep-tail
FDR_Q = 0.05


def setup():
    ans = load(STUDY)
    models = sorted(m for m in ans if ans[m])
    cats = sorted({c for m in models for c in ans[m]})
    for c in cats:                                   # plural merge, as in analyze.py
        pool = Counter(a for m in models for a in ans[m].get(c, []))
        stems = {w: w[:-1] for w in pool if w.endswith('s') and w[:-1] in pool}
        for m in models:
            if c in ans[m]:
                ans[m][c] = [stems.get(a, a) for a in ans[m][c]]
    full = {c: Counter(a for m in models for a in ans[m].get(c, [])) for c in cats}
    modal = {c: full[c].most_common(1)[0][0] for c in cats}
    rank = {c: {a: i + 1 for i, (a, _) in enumerate(full[c].most_common())} for c in cats}
    return ans, models, cats, full, modal, rank


def p_one_sided(z):
    return 0.5 * (1 - math.erf(z / math.sqrt(2)))


def bh_keep(pairs):
    """pairs sorted by p ascending -> number kept at FDR_Q"""
    keep = 0
    for r, (p, *_) in enumerate(pairs, 1):
        if p <= FDR_Q * r / len(pairs):
            keep = r
    return keep


def show(title, pairs, keep, top=6):
    print(f"\n{title}: BH-FDR q={FDR_Q} keeps {keep} of {len(pairs)}")
    for r, (p, A, B, note) in enumerate(pairs[:top], 1):
        star = '*' if r <= keep else ' '
        print(f" {star}{A} × {B:32} p={p:.2e}  {note}")


def structure_tables(ans, models, cats, full, modal, rank):
    print("runner-up concentration (modal share >= 50%): the off-modal distribution has a mode too")
    print(f"{'category':18} {'modal':>14} {'share':>6}  {'#2':>12} {'#2 share of off-modal':>22}")
    for c in cats:
        total = sum(full[c].values())
        (m1, n1), *rest = full[c].most_common()
        if n1 / total < 0.5 or not rest:
            continue
        m2, n2 = rest[0]
        print(f"{c:18} {m1:>14} {n1/total:6.0%}  {m2:>12} {n2/(total-n1):22.0%}")

    print("\ndepth propensity (of each model's distinct off-modal answers, how deep it lands)")
    print(f"{'model':30} {'n_off':>5} {'#2-3':>6} {'#>=5':>6}")
    rows = []
    for m in models:
        offs = [(c, a) for c in cats for a in set(ans[m].get(c, [])) if a != modal[c]]
        n = len(offs)
        r23 = sum(2 <= rank[c][a] <= 3 for c, a in offs)
        dp = sum(rank[c][a] >= 5 for c, a in offs)
        rows.append((r23 / n if n else 0, m, n, dp / n if n else 0))
    for share, m, n, dshare in sorted(rows, reverse=True):
        print(f"{m:30} {n:5d} {share:6.0%} {dshare:6.0%}")


def level1(ans, models, cats):
    """rarity-weighted shared-answer score vs exchangeable-random-partner null (exact mu/var)."""
    M, C = len(models), len(cats)
    w, sets = {}, [[set(ans[m].get(c, [])) for c in cats] for m in models]
    for c in cats:
        pool = Counter(a for m in models for a in ans[m].get(c, []))
        tot, vocab = sum(pool.values()), len(pool)
        w[c] = {a: -math.log2((n + 1) / (tot + vocab)) for a, n in pool.items()}
    W = np.zeros((M, M, C))
    for i in range(M):
        for j in range(M):
            for k, c in enumerate(cats):
                if i != j:
                    W[i, j, k] = sum(w[c][a] for a in sets[i][k] & sets[j][k])
    best = {}
    for i in range(M):
        for j in range(M):
            if i == j:
                continue
            col = W[i, [o for o in range(M) if o not in (i, j)], :]
            var = col.var(axis=0).sum()
            z = (W[i, j, :].sum() - col.mean(axis=0).sum()) / math.sqrt(var) if var else 0.0
            key = (min(i, j), max(i, j))
            best[key] = min(best.get(key, math.inf), z)      # conservative direction
    pairs = sorted((p_one_sided(z), models[i], models[j], f"z={z:.2f}")
                   for (i, j), z in best.items())
    show("L1 rarity-weighted, random-partner null", pairs, bh_keep(pairs))


def conditional_z(ans, models, cats, modal, choice_sets, A, B, restrict):
    """analytic z for: A's choices fixed, B's redrawn from the field's conditional
    distribution (leave-two-out, add-one smoothed), per category where both chose.
    restrict filters which field answers form the null pool."""
    S = E = V = 0.0
    for c in cats:
        SA, SB = choice_sets[A][c], choice_sets[B][c]
        if not SA or not SB:
            continue
        pool = Counter(a for m in models if m not in (A, B)
                       for a in ans[m].get(c, []) if restrict(c, a))
        vocab = set(pool) | SA | SB
        tot = sum(pool.values()) + len(vocab)
        q = {a: (pool.get(a, 0) + 1) / tot for a in vocab}
        k = len(SB)
        S += sum(-math.log2(q[a]) for a in SA & SB)
        for a in SA:
            P, wa = 1 - (1 - q[a]) ** k, -math.log2(q[a])
            E += P * wa
            V += P * (1 - P) * wa ** 2                       # ignores neg. dependence: conservative
    return S, ((S - E) / math.sqrt(V) if V > 0 else 0.0)


def level2(ans, models, cats, modal):
    offs = {m: {c: set(a for a in ans[m].get(c, []) if a != modal[c]) for c in cats}
            for m in models}
    restrict = lambda c, a: a != modal[c]
    pairs = []
    for i, A in enumerate(models):
        for B in models[i + 1:]:
            _, z1 = conditional_z(ans, models, cats, modal, offs, A, B, restrict)
            _, z2 = conditional_z(ans, models, cats, modal, offs, B, A, restrict)
            z = min(z1, z2)
            pairs.append((p_one_sided(z), A, B, f"z={z:.2f}"))
    pairs.sort()
    show("L2 avoidance-conditioned (off-modal only)", pairs, bh_keep(pairs))


def level3(ans, models, cats, rank):
    deep = {m: {c: set(a for a in ans[m].get(c, []) if rank[c][a] >= DEEP_RANK) for c in cats}
            for m in models}
    rng = np.random.default_rng(7)

    def mc_p(A, B):
        null, S, nm = np.zeros(NSIM), 0.0, 0
        for c in cats:
            SA, SB = deep[A][c], deep[B][c]
            if not SA or not SB:
                continue
            pool = Counter(a for m in models if m not in (A, B)
                           for a in ans[m].get(c, []) if rank[c][a] >= DEEP_RANK)
            vocab = sorted(set(pool) | SA | SB)
            cnt = np.array([pool.get(a, 0) + 1 for a in vocab], float)
            q = cnt / cnt.sum()
            w = -np.log2(q)
            inA = np.array([a in SA for a in vocab])
            S += sum(w[i] for i, a in enumerate(vocab) if a in SA and a in SB)
            nm += len(SA & SB)
            k = len(SB)
            draws = rng.choice(len(vocab), size=(NSIM, k), p=q)
            hit = inA[draws] * w[draws]
            for s in range(k):                                # distinct answers: count dups once
                dup = (draws[:, s:s + 1] == draws[:, :s]).any(axis=1) if s else np.zeros(NSIM, bool)
                null += np.where(dup, 0.0, hit[:, s])
        return ((1 + (null >= S).sum()) / (NSIM + 1) if S > 0 else 1.0), nm

    pairs = []
    for i, A in enumerate(models):
        for B in models[i + 1:]:
            pab, nm = mc_p(A, B)
            pba, _ = mc_p(B, A)
            pairs.append((max(pab, pba), A, B, f"deep matches={nm}"))
    pairs.sort()
    show(f"L3 depth-conditioned (rank>={DEEP_RANK} only, {NSIM} MC sims/direction)",
         pairs, bh_keep(pairs), top=10)


if __name__ == "__main__":
    ans, models, cats, full, modal, rank = setup()
    structure_tables(ans, models, cats, full, modal, rank)
    level1(ans, models, cats)
    level2(ans, models, cats, modal)
    level3(ans, models, cats, rank)
