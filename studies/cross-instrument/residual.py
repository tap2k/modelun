#!/usr/bin/env python3
"""Who is off the diagonal? Rank-regress conduct departure on census concentration and list
the residuals: negative = holds under pressure MORE than its default-concentration predicts
(spontaneous and principled); positive = caves more than predicted."""
from build_matrix import cols, rank
cc, cd = cols["census_conc"], cols["conduct_dep"]
ms = sorted(m for m in cc if m in cd)
x = [cc[m] for m in ms]; y = [cd[m] for m in ms]
rx, ry = rank(x), rank(y); n = len(ms); mx = sum(rx)/n; my = sum(ry)/n
b = sum((a-mx)*(c-my) for a, c in zip(rx, ry)) / sum((a-mx)**2 for a in rx)
res = {m: ry[i] - (my + b*(rx[i]-mx)) for i, m in enumerate(ms)}
print(f"n={n}; rank slope {b:.2f}. residual in rank units; negative = holds more than predicted.")
print(f"{'model':<34}{'census_conc':>12}{'conduct_dep':>12}{'residual':>10}")
for m in sorted(ms, key=lambda m: res[m]):
    print(f"{m:<34}{cc[m]:>12.2f}{cd[m]:>12.2f}{res[m]:>10.1f}")
