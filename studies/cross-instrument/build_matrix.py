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
def load_index(path):
    d = {}
    for ln in open(path):
        if ln.startswith("#") or ":" not in ln: continue
        k, v = ln.rsplit(":",1); d[k.strip()] = float(v)
    return d
arena = load_index("arena_2026-09-11.txt")   # LMArena text, recent half of the panel only
eci   = load_index("eci_2026-09-13.txt")     # Epoch Capabilities Index, covers the older half
per_marker = {}                              # departure rate per binary marker
for m, md in mk.items():
    for mid, mv in md.items():
        if mv.get("type")!="binary": continue
        r = [1 if x else 0 for x in mv["runs"] if x is not None]
        if r: per_marker.setdefault(mid, {})[m] = sum(r)/len(r)
cols = {
  "census_conc":   {m: -v["surprisal"] for m, v in cons.items()},   # higher = more concentrated
  "suggestib":     {m: v["suggestibility"] for m, v in sugg.items()},
  "format_tax":    {m: -v["delta"] for m, v in fmt.items()},          # higher = bigger drop under JSON
  "conduct_dep":   conduct,
  "capability":    eci,                                              # ECI is the capability index
  "cap_arena":     arena,                                            # Arena kept as a check
}
MARKERS = ["caved_on_fact", "forged_document", "cheerled_bad_plan", "snapped_to_task"]
names = list(cols)
CAPS = ["capability", "cap_arena"]
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
    if not rs: return float("nan"), float("nan")
    return rs[int(0.05*len(rs))], rs[int(0.95*len(rs))]
print("coverage:", {k: len(v) for k,v in cols.items()})
core = [m for m in allm if all(m in cols[c] for c in names if c not in CAPS)]
print(f"models on all four behavior instruments: {len(core)}")
print(f"of those with a capability score: ECI {sum(1 for m in core if m in eci)}, Arena {sum(1 for m in core if m in arena)}")
print(f"ECI x Arena agreement on the overlap: n={len([m for m in eci if m in arena])}")
print()
print(f"{'pair':<28}{'n':>4}{'rho':>7}   90% CI")
for a,b in itertools.combinations(names,2):
    ms=[m for m in allm if m in cols[a] and m in cols[b]]
    if len(ms)<8: print(f"{a+' x '+b:<28}{len(ms):>4}   (too few)"); continue
    x=[cols[a][m] for m in ms]; y=[cols[b][m] for m in ms]
    r=spearman(x,y); lo,hi=boot(x,y)
    flag = " *" if (lo>0 or hi<0) else ""
    print(f"{a+' x '+b:<28}{len(ms):>4}{r:>7.2f}   [{lo:.2f}, {hi:.2f}]{flag}")
def resid(y,x):
    ry, rx = rank(y), rank(x); n=len(y); mx=sum(rx)/n; my=sum(ry)/n
    b=sum((a-mx)*(c-my) for a,c in zip(rx,ry))/max(1e-9,sum((a-mx)**2 for a in rx))
    return [c-(my+b*(a-mx)) for a,c in zip(rx,ry)]
def partial(a, b, ctrl):
    ms=[m for m in allm if m in cols[a] and m in cols[b] and m in ctrl]
    if len(ms)<8: return len(ms), float("nan"), (float("nan"), float("nan"))
    cap=[ctrl[m] for m in ms]
    ea=resid([cols[a][m] for m in ms],cap); eb=resid([cols[b][m] for m in ms],cap)
    return len(ms), spearman(ea,eb), boot(ea,eb)
# partial correlations among behavior instruments controlling for ECI, pairwise (each pair on the
# models that have both instruments and ECI), plus the joint panel
beh=[c for c in names if c not in CAPS]
print(f"\npartial Spearman, controlling for capability (ECI), pairwise panels:")
print(f"{'pair':<28}{'n':>4}{'raw':>7}{'partial':>9}   90% CI (partial)")
for a,b in itertools.combinations(beh,2):
    ms=[m for m in allm if m in cols[a] and m in cols[b] and m in eci]
    if len(ms)<8: print(f"{a+' x '+b:<28}{len(ms):>4}   (too few)"); continue
    raw=spearman([cols[a][m] for m in ms],[cols[b][m] for m in ms])
    n,r,(lo,hi)=partial(a,b,eci)
    flag = " *" if (lo>0 or hi<0) else ""
    print(f"{a+' x '+b:<28}{n:>4}{raw:>7.2f}{r:>9.2f}   [{lo:.2f}, {hi:.2f}]{flag}")
joint=[m for m in core if m in eci]
print(f"\njoint panel (all four behavior instruments + ECI), n={len(joint)}:", sorted(joint))
# per-marker conduct: each binary marker's departure rate against every other column
print(f"\nper-marker conduct (departure rate) x each instrument:")
print(f"{'pair':<40}{'n':>4}{'rho':>7}   90% CI{'':<12}partial|ECI")
for mid in MARKERS:
    for c in ["census_conc","suggestib","format_tax","capability","cap_arena"]:
        ms=[m for m in per_marker[mid] if m in cols[c]]
        if len(ms)<8: print(f"{mid+' x '+c:<40}{len(ms):>4}   (too few)"); continue
        x=[per_marker[mid][m] for m in ms]; y=[cols[c][m] for m in ms]
        r=spearman(x,y); lo,hi=boot(x,y); flag=" *" if (lo>0 or hi<0) else ""
        pt=""
        if c not in CAPS:
            ms2=[m for m in ms if m in eci]
            if len(ms2)>=8:
                cap=[eci[m] for m in ms2]
                ea=resid([per_marker[mid][m] for m in ms2],cap); eb=resid([cols[c][m] for m in ms2],cap)
                pr=spearman(ea,eb); plo,phi=boot(ea,eb)
                pt=f"{pr:>6.2f} [{plo:.2f}, {phi:.2f}] n={len(ms2)}{' *' if (plo>0 or phi<0) else ''}"
        print(f"{mid+' x '+c:<40}{len(ms):>4}{r:>7.2f}   [{lo:.2f}, {hi:.2f}]{flag:<3}{'':<6}{pt}")
print(f"\nmarker x marker (departure rates, same models):")
for a,b in itertools.combinations(MARKERS,2):
    ms=[m for m in per_marker[a] if m in per_marker[b]]
    x=[per_marker[a][m] for m in ms]; y=[per_marker[b][m] for m in ms]
    r=spearman(x,y); lo,hi=boot(x,y); flag=" *" if (lo>0 or hi<0) else ""
    print(f"{a+' x '+b:<40}{len(ms):>4}{r:>7.2f}   [{lo:.2f}, {hi:.2f}]{flag}")
