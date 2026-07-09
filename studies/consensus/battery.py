"""battery.py — battery-side robustness: is the scorecard an artifact of category selection?

Zero new API calls (frozen transcripts only). Three readouts, complementing robustness.py's
roster-side tests:

  * LOCO      — leave-one-category-out: rank correlation of the 39-model scorecard after
                dropping each category.
  * split-half — random 15/16 category splits; rank correlation between the two half-battery
                scorecards. Spearman-Brown 2r/(1+r) estimates full-battery reliability.
  * item-rest — per-category discrimination: correlation of each category's per-model mean
                surprisal with the rest-of-battery score, plus between-model SD.

Findings (2026-07-09, frozen data): LOCO >= 0.982 for every category (no single prompt carries
the rankings). Split-half median rho = 0.625 (Spearman-Brown ~ 0.77): tier membership is solid,
adjacent mid-field ranks are noisy. Item-rest splits the battery in two: discrimination
concentrates in the DIFFUSE categories (country, any_word, sport, emotion, ... r = 0.3-0.5);
the PEAKED categories (tree, tool, fruit, ... 80-95% modes) sit at a ceiling and rank nobody --
they document the substrate (S4.1), the diffuse half drives the scorecard (S4.2). Implication
for battery growth: new categories should target the diffuse profile; another `tree` buys no
reliability.

    ../../.venv/bin/python battery.py
"""

import math
import sys
from pathlib import Path
from collections import Counter

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from analyze import load  # noqa: E402


def spear(x, y):
    r = lambda v: np.argsort(np.argsort(v)).astype(float)
    return float(np.corrcoef(r(np.asarray(x)), r(np.asarray(y)))[0, 1])


def main():
    ans = load(HERE)
    models = sorted(m for m in ans if ans[m])
    cats = sorted({c for m in models for c in ans[m]})
    for c in cats:  # plural merge, identical to analyze.py
        pool = Counter(a for m in models for a in ans[m].get(c, []))
        stems = {w: w[:-1] for w in pool if w.endswith("s") and w[:-1] in pool}
        for m in models:
            if c in ans[m]:
                ans[m][c] = [stems.get(a, a) for a in ans[m][c]]

    # per-model per-category per-answer surprisals (same scoring as analyze.py)
    pcs = {m: {} for m in models}
    for m in models:
        for c in cats:
            mine = ans[m].get(c, [])
            others = [a for o in models if o != m for a in ans[o].get(c, [])]
            if not mine or not others:
                continue
            pool = Counter(others)
            total, vocab = sum(pool.values()), len(set(others) | set(mine))
            pcs[m][c] = [-math.log2((pool.get(a, 0) + 1) / (total + vocab)) for a in mine]

    def score(m, use):
        s = [x for c in use if c in pcs[m] for x in pcs[m][c]]
        return float(np.mean(s)) if s else np.nan

    full = [score(m, cats) for m in models]

    # LOCO
    locos = sorted((spear(full, [score(m, [k for k in cats if k != c]) for m in models]), c)
                   for c in cats)
    print(f"LOCO rank corr: min {locos[0][0]:.3f} ({locos[0][1]})  "
          f"median {locos[len(locos) // 2][0]:.3f}")

    # split-half + Spearman-Brown
    rng = np.random.default_rng(7)
    rhos = []
    for _ in range(200):
        perm = list(rng.permutation(cats))
        rhos.append(spear([score(m, perm[:15]) for m in models],
                          [score(m, perm[15:]) for m in models]))
    med = float(np.median(rhos))
    print(f"split-half (200 draws): median rho {med:.3f}  5th pct "
          f"{np.percentile(rhos, 5):.3f}  Spearman-Brown reliability {2 * med / (1 + med):.2f}")

    # item-rest discrimination
    print(f"\n{'category':18s} item-rest r   between-model SD (bits)")
    rows = []
    for c in cats:
        ms = [m for m in models if c in pcs[m]]
        item = [float(np.mean(pcs[m][c])) for m in ms]
        rest = [float(np.mean([x for k in cats if k != c and k in pcs[m] for x in pcs[m][k]]))
                for m in ms]
        rows.append((spear(item, rest), float(np.std(item)), c))
    for r, sd, c in sorted(rows, reverse=True):
        print(f"{c:18s}    {r:+.2f}         {sd:.2f}{'   <-- weak' if r < 0.2 else ''}")
    print(f"\nmedian item-rest: {np.median([r for r, _, _ in rows]):.2f}")


if __name__ == "__main__":
    main()
