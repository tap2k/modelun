#!/usr/bin/env python3
"""Cross-instrument matrix: per-model scores from every published instrument, joined on the
model label, correlated with each other and with a capability index (Arena text, 2026-09-11)."""
import json, sys, math, itertools, random
from pathlib import Path
M = Path(__file__).resolve().parent.parent
cons = json.load(open(M/"consensus/analysis.json"))["per_model"]
sugg = json.load(open(M/"suggestibility/analysis.json"))["per_model"]
s = open(M/"structured/views/data.js").read(); fmt = json.loads(s[s.index("=")+1:].rstrip().rstrip(";"))["models"]
mk = json.load(open(M/"conduct/data/benchmark/markers.json"))["models"]
conduct = {}
for m, md in mk.items():
    v = [1 if x else 0 for mv in md.values() if mv.get("type")=="binary" for x in mv["runs"] if x is not None]
    if v: conduct[m] = sum(v)/len(v)
arena = {}
for ln in open("arena_2026-09-11.txt"):
    if ":" in ln: k, v = ln.rsplit(":",1); arena[k.strip()] = float(v)
cols = {
  "census_conc":   {m: -v["surprisal"] for m, v in cons.items()},   # higher = more concentrated
  "suggestib":     {m: v["suggestibility"] for m, v in sugg.items()},
  "format_tax":    {m: -v["delta"] for m, v in fmt.items()},          # higher = bigger drop under JSON
  "conduct_dep":   conduct,
  "capability":    arena,
}
names = list(cols)
allm = sorted(set().union(*[set(c) for c in cols.values()]))
def rank(x):
    # average ranks for ties, so results do not depend on input order
    s = sorted(range(len(x)), key=lambda i: x[i]); r=[0.0]*len(x); k=0
    while k < len(s):
        j = k
        while j+1 < len(s) and x[s[j+1]] == x[s[k]]: j += 1
        for t in range(k, j+1): r[s[t]] = (k+j)/2
        k = j+1
    return r
def spearman(a,b):
    ra, rb = rank(a), rank(b); n=len(a); ma=sum(ra)/n; mb=sum(rb)/n
    num=sum((x-ma)*(y-mb) for x,y in zip(ra,rb)); den=math.sqrt(sum((x-ma)**2 for x in ra)*sum((y-mb)**2 for y in rb))
    return num/den if den else float("nan")
def boot(a,b,B=2000,seed=0):
    rnd=random.Random(seed); n=len(a); rs=[]
    for _ in range(B):
        idx=[rnd.randrange(n) for _ in range(n)]
        rs.append(spearman([a[i] for i in idx],[b[i] for i in idx]))
    rs=[r for r in rs if r==r]; rs.sort()
    return rs[int(0.05*len(rs))], rs[int(0.95*len(rs))]
print("coverage:", {k: len(v) for k,v in cols.items()})
core = [m for m in allm if all(m in cols[c] for c in names if c!="capability")]
print(f"models on all four behavior instruments: {len(core)}")
print(f"of those with a capability score: {sum(1 for m in core if m in arena)}")
print()
print(f"{'pair':<28}{'n':>4}{'rho':>7}   90% CI")
for a,b in itertools.combinations(names,2):
    ms=[m for m in allm if m in cols[a] and m in cols[b]]
    if len(ms)<8: print(f"{a+' x '+b:<28}{len(ms):>4}   (too few)"); continue
    x=[cols[a][m] for m in ms]; y=[cols[b][m] for m in ms]
    r=spearman(x,y); lo,hi=boot(x,y)
    flag = " *" if (lo>0 or hi<0) else ""
    print(f"{a+' x '+b:<28}{len(ms):>4}{r:>7.2f}   [{lo:.2f}, {hi:.2f}]{flag}")
# partial correlations among behavior instruments controlling for capability, on the joint panel
joint=[m for m in core if m in arena]
if len(joint)>=10:
    print(f"\npartial Spearman among behavior instruments, controlling for capability (n={len(joint)}):")
    def resid(y,x):
        ry, rx = rank(y), rank(x); n=len(y); mx=sum(rx)/n; my=sum(ry)/n
        b=sum((a-mx)*(c-my) for a,c in zip(rx,ry))/max(1e-9,sum((a-mx)**2 for a in rx))
        return [c-(my+b*(a-mx)) for a,c in zip(rx,ry)]
    cap=[arena[m] for m in joint]
    beh=[c for c in names if c!="capability"]
    for a,b in itertools.combinations(beh,2):
        ea=resid([cols[a][m] for m in joint],cap); eb=resid([cols[b][m] for m in joint],cap)
        print(f"  {a+' x '+b:<26}{spearman(ea,eb):>7.2f}")
print("\njoint panel:", sorted(joint))
