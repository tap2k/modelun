#!/usr/bin/env python3
"""Is the census-conduct correlation just distributional peakedness? Split the conduct signal
into run-to-run STABILITY (same verdict both runs) and departure DIRECTION (held vs departed),
and correlate census concentration with each. Concentration predicting stability and not
direction = temperature; predicting direction = conduct."""
import json, math, random, itertools
from pathlib import Path
from build_matrix import spearman, boot, cols
M = Path(__file__).resolve().parent.parent
mk = json.load(open(M/"conduct/data/benchmark/markers.json"))["models"]
stab, direc, per_marker = {}, {}, {}
for m, md in mk.items():
    s=[]; d=[]
    for mid, mv in md.items():
        if mv.get("type")!="binary": continue
        r=[x for x in mv["runs"] if x is not None]
        if len(r)==2: s.append(1 if r[0]==r[1] else 0)
        for x in r: d.append(1 if x else 0)
        per_marker.setdefault(mid,{})[m]=sum(1 if x else 0 for x in r)/len(r) if r else None
    if s: stab[m]=sum(s)/len(s)
    if d: direc[m]=sum(d)/len(d)
cc=cols["census_conc"]; ss=cols["suggestib"]
def report(name, a, b):
    ms=[m for m in a if m in b and b[m] is not None]
    x=[a[m] for m in ms]; y=[b[m] for m in ms]; r=spearman(x,y); lo,hi=boot(x,y)
    print(f"{name:<48}n={len(ms):>3}  rho={r:>6.2f}  90% CI [{lo:.2f}, {hi:.2f}]{' *' if lo>0 or hi<0 else ''}")
print("conduct decomposed:")
report("census_conc x conduct STABILITY (same verdict both runs)", cc, stab)
report("census_conc x conduct DIRECTION (departure rate)", cc, direc)
report("suggestib   x conduct STABILITY", ss, stab)
report("suggestib   x conduct DIRECTION", ss, direc)
print("\nper marker, census_conc x departure rate:")
for mid, d in per_marker.items(): report(f"  {mid}", cc, d)
print("\nsame decomposition with census self-distinctness (1 - repeat rate within a model) as the peakedness measure:")
cons = json.load(open(M/"consensus/analysis.json"))["per_model"]
peak = {m: -v["self_distinct"] for m,v in cons.items()}
report("peakedness x conduct STABILITY", peak, stab)
report("peakedness x conduct DIRECTION", peak, direc)
