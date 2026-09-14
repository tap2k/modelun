#!/usr/bin/env python3
"""The matrix on the full panel: capability from the Epoch Capabilities Index (covers the older
half of the panel that Arena lacks), plus release date, so capability and generation can be
told apart where the panel allows. Also the taste/consequential split and per-marker conduct."""
import csv, json, math, itertools
from pathlib import Path
from build_matrix import spearman, boot, rank, cols
H = Path(__file__).resolve().parent; M = H.parent
eci = {r["Model"]: (float(r["eci"]), r["date"]) for r in csv.DictReader(open(H/"eci_scores_2026-09-13.csv"))}
cap, date = {}, {}
for ln in open(H/"eci_map_2026-09-13.tsv"):
    if ln.startswith("#") or "\t" not in ln: continue
    ours, theirs = ln.rstrip("\n").split("\t")
    if theirs in eci:
        cap[ours] = eci[theirs][0]; y, m, d = eci[theirs][1].split("-"); date[ours] = int(y)*365 + int(m)*30 + int(d)
sugg = json.load(open(M/"suggestibility/analysis.json"))["per_model"]
mk = json.load(open(M/"conduct/data/benchmark/markers.json"))["models"]
per_marker = {}
for m, md in mk.items():
    for mid, mv in md.items():
        if mv.get("type") == "binary":
            r = [1 if x else 0 for x in mv["runs"] if x is not None]
            if r: per_marker.setdefault(mid, {})[m] = sum(r)/len(r)
C = {k: v for k, v in cols.items() if k != "capability"}
C["capability_eci"] = cap; C["release_date"] = date
C["shift_taste"] = {m: v["shift_taste"] for m, v in sugg.items()}
C["shift_conseq"] = {m: v["shift_consequential"] for m, v in sugg.items()}
for mid, d in per_marker.items(): C["mk:"+mid] = d
def corr(a, b, label=None):
    ms = [m for m in C[a] if m in C[b]]
    if len(ms) < 8: return
    x = [C[a][m] for m in ms]; y = [C[b][m] for m in ms]; r = spearman(x, y); lo, hi = boot(x, y)
    print(f"{(label or a+' x '+b):<44}n={len(ms):>3}  rho={r:>6.2f}  90% CI [{lo:.2f}, {hi:.2f}]{' *' if lo>0 or hi<0 else ''}")
def partial(a, b, z):
    ms = [m for m in C[a] if m in C[b] and m in C[z]]
    if len(ms) < 10: return
    def resid(y, x):
        ry, rx = rank(y), rank(x); n = len(y); mx = sum(rx)/n; my = sum(ry)/n
        bb = sum((p-mx)*(q-my) for p, q in zip(rx, ry)) / max(1e-9, sum((p-mx)**2 for p in rx))
        return [q-(my+bb*(p-mx)) for p, q in zip(rx, ry)]
    z_ = [C[z][m] for m in ms]; ea = resid([C[a][m] for m in ms], z_); eb = resid([C[b][m] for m in ms], z_)
    r = spearman(ea, eb); lo, hi = boot(ea, eb)
    print(f"  {a+' x '+b+' | '+z:<42}n={len(ms):>3}  rho={r:>6.2f}  90% CI [{lo:.2f}, {hi:.2f}]{' *' if lo>0 or hi<0 else ''}")
print("ECI coverage:", {k: sum(1 for m in C[k] if m in cap) for k in ["census_conc","suggestib","format_tax","conduct_dep"]}, "| ECI x date rho:", f"{spearman([cap[m] for m in cap],[date[m] for m in cap]):.2f}")
print("\n== instruments vs capability (ECI) and vs release date ==")
for k in ["census_conc","suggestib","shift_taste","shift_conseq","format_tax","conduct_dep"]:
    corr(k, "capability_eci"); corr(k, "release_date")
print("\n== instruments vs each other, raw ==")
for a, b in itertools.combinations(["census_conc","suggestib","format_tax","conduct_dep"], 2): corr(a, b)
print("\n== partialled on capability (ECI), then on release date ==")
for a, b in itertools.combinations(["census_conc","suggestib","format_tax","conduct_dep"], 2):
    partial(a, b, "capability_eci"); partial(a, b, "release_date")
print("\n== capability partialled on date (does any capability signal survive generation?) ==")
for k in ["census_conc","suggestib","shift_taste","shift_conseq","conduct_dep"]: partial(k, "capability_eci", "release_date")
print("\n== per marker ==")
for mid in per_marker:
    corr("mk:"+mid, "census_conc"); corr("mk:"+mid, "capability_eci"); corr("mk:"+mid, "release_date")
for a, b in itertools.combinations(sorted(per_marker), 2): corr("mk:"+a, "mk:"+b)
