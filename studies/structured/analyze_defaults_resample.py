"""analyze_defaults_resample.py — resolve the W1 null from the high-n re-sample.

For each stable-default cell we now have N=20 samples in chat and in JSON. This lets us:
  (1) estimate each default's true per-sample probability in chat (are they rock-solid or
      wobbly? — this is what made the n=4 null unidentifiable),
  (2) test per cell whether the JSON distribution really shifted (Fisher exact on the
      default-word count), with BH-FDR across cells, and
  (3) confirm the clean flips (Terra mustard->ketchup, Fable-acquired words) as measured
      effects rather than n=4 anecdotes.

    ../../.venv/bin/python analyze_defaults_resample.py
"""
import json
import re
import sys
import statistics as st
from pathlib import Path
from collections import Counter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "consensus"))
from analyze import norm

try:
    from scipy.stats import fisher_exact
    def fisher(c_chat, n_chat, c_json, n_json):
        return fisher_exact([[c_chat, n_chat - c_chat], [c_json, n_json - c_json]])[1]
except Exception:
    from math import comb
    def fisher(c_chat, n_chat, c_json, n_json):  # two-sided hypergeometric
        a, b, c, dd = c_chat, n_chat - c_chat, c_json, n_json - c_json
        n, r1, r2, c1 = a + b + c + dd, a + b, c + dd, a + c
        p0 = comb(r1, a) * comb(r2, c1 - a) / comb(n, c1)
        s = 0.0
        for x in range(max(0, c1 - r2), min(r1, c1) + 1):
            px = comb(r1, x) * comb(r2, c1 - x) / comb(n, c1)
            if px <= p0 + 1e-12:
                s += px
        return min(1.0, s)

d = json.loads((HERE / "probes/defaults_resample.json").read_text())
rep = d["replies"]
JP = re.compile(r'"word"\s*:\s*"([^"]+)"')


def pj(r):
    if not r:
        return None
    m = JP.search(r)
    return norm(m.group(1)) if m else norm(r)


cells = []
for l in rep:
    for c in rep[l]:
        cell = rep[l][c]
        W, fm = cell["default"], cell["field_modal"]
        chat = [x for x in (norm(r) if r else None for r in cell["plain"]) if x]
        js = [x for x in (pj(r) for r in cell["json"]) if x]
        if len(chat) < 5 or len(js) < 5:
            continue
        cc, cj = Counter(chat), Counter(js)
        jmode, jk = cj.most_common(1)[0]
        cells.append({
            "l": l, "c": c, "W": W, "fm": fm,
            "nchat": len(chat), "njson": len(js),
            "pchat": cc[W] / len(chat), "pjson": cj[W] / len(js),
            "jmode": jmode, "jrate": jk / len(js),
            "p": fisher(cc[W], len(chat), cj[W], len(js)),
        })

M = len(cells)
print(f"cells analyzed: {M}  (N={d['n']} per register)\n")

# (1) how solid are chat defaults, really?
pc = [x["pchat"] for x in cells]
print("chat per-sample probability of the default:")
print(f"  mean {st.mean(pc):.2f}  median {st.median(pc):.2f}  "
      f">=0.90: {sum(p>=0.9 for p in pc)}/{M}  <0.75: {sum(p<0.75 for p in pc)}/{M}")
print("  => this is what n=4 could not see; it sets the noise floor for retention.\n")

# (2) per-cell significant shift, BH-FDR q=.10
ps = sorted((x["p"], i) for i, x in enumerate(cells))
q, kmax = 0.10, 0
for rank, (p, _i) in enumerate(ps, 1):
    if p <= rank / M * q:
        kmax = rank
sig = {ps[r - 1][1] for r in range(1, kmax + 1)}
print(f"register SIGNIFICANTLY shifts the default (Fisher, BH-FDR q=.10): "
      f"{len(sig)}/{M} = {len(sig)/M:.0%}")
print(f"  (a no-change null yields ~{q:.0%} false positives; observed {len(sig)/M:.0%})\n")

# proper retention: default is still the JSON mode
held = sum(1 for x in cells if x["jmode"] == x["W"])
reverted = sum(1 for x in cells if x["jmode"] == x["fm"])
print(f"default still the JSON mode:      {held}/{M} = {held/M:.0%}")
print(f"reverted to the crowd's answer:   {reverted}/{M} = {reverted/M:.0%}\n")

# (3) clean flips: significant + a NEW specific json mode held at high rate
flips = [x for i, x in enumerate(cells)
         if i in sig and x["jmode"] != x["W"] and x["jrate"] >= 0.6]
print(f"clean flips (sig + new JSON mode >=60%): {len(flips)}")
for x in sorted(flips, key=lambda x: -x["jrate"])[:15]:
    tgt = "crowd" if x["jmode"] == x["fm"] else "other"
    print(f"  {x['l']:22s} {x['c']:12s} {x['W']} {x['pchat']:.0%} -> "
          f"{x['jmode']} {x['jrate']:.0%} ({tgt})  p={x['p']:.1e}")
