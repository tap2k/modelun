#!/usr/bin/env python3
"""Is the capability index just release date? ECI rises with generation, and so does census
concentration (the census paper's lineage finding). Correlate each instrument with ECI release
date, and re-run the census x conduct partial controlling for date instead of ECI, and for both."""
import datetime, io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    from build_matrix import cols, spearman, boot, resid, allm, per_marker, MARKERS
eci = cols["capability"]
dates = {}
for ln in open("eci_dates_2026-09-13.txt"):
    if ln.startswith("#") or ":" not in ln: continue
    k, v = ln.rsplit(":",1); dates[k.strip()] = datetime.date.fromisoformat(v.strip()).toordinal()
def rep(name, a, b):
    ms=[m for m in a if m in b]; x=[a[m] for m in ms]; y=[b[m] for m in ms]
    r=spearman(x,y); lo,hi=boot(x,y)
    print(f"{name:<44}n={len(ms):>3}  rho={r:>6.2f}  90% CI [{lo:.2f}, {hi:.2f}]{' *' if lo>0 or hi<0 else ''}")
print("release date as the control:")
rep("capability (ECI) x release date", eci, dates)
for c in ["census_conc","suggestib","format_tax","conduct_dep"]: rep(f"{c} x release date", cols[c], dates)
for mid in MARKERS: rep(f"  {mid} x release date", per_marker[mid], dates)
def partial2(a, b, ctrls, label):
    ms=[m for m in allm if m in cols[a] and m in cols[b] and all(m in c for c in ctrls)]
    # residualize on each control in turn (rank-based, sequential)
    ya=[cols[a][m] for m in ms]; yb=[cols[b][m] for m in ms]
    for c in ctrls:
        cv=[c[m] for m in ms]; ya=resid(ya,cv); yb=resid(yb,cv)
    r=spearman(ya,yb); lo,hi=boot(ya,yb)
    print(f"{a+' x '+b+' | '+label:<44}n={len(ms):>3}  rho={r:>6.2f}  90% CI [{lo:.2f}, {hi:.2f}]{' *' if lo>0 or hi<0 else ''}")
print("\ncensus x conduct, partialled:")
partial2("census_conc","conduct_dep",[],"nothing")
partial2("census_conc","conduct_dep",[eci],"ECI")
partial2("census_conc","conduct_dep",[dates],"date")
partial2("census_conc","conduct_dep",[dates,eci],"date then ECI")
print("\ncapability x conduct, partialled on date:")
partial2("capability","conduct_dep",[],"nothing")
partial2("capability","conduct_dep",[dates],"date")
partial2("capability","census_conc",[],"nothing")
partial2("capability","census_conc",[dates],"date")
partial2("suggestib","capability",[],"nothing")
partial2("suggestib","capability",[dates],"date")
