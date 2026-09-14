#!/usr/bin/env python3
"""Cross-instrument matrix: per-model scores from every published instrument, joined on the
model label, correlated with each other, with a capability index that covers the whole panel
(Epoch Capabilities Index) and with release date, then partialled on each. Per-marker conduct
and the taste/consequential split of suggestibility are broken out."""
import csv, json, math, itertools, random, datetime
from pathlib import Path
H = Path(__file__).resolve().parent; M = H.parent
cons = json.load(open(M/"consensus/analysis.json"))["per_model"]
sugg = json.load(open(M/"suggestibility/analysis.json"))["per_model"]
s = open(M/"structured/views/data.js").read(); fmt = json.loads(s[s.index("=")+1:].rstrip().rstrip(";"))["models"]
mk = json.load(open(M/"conduct/data/benchmark/markers.json"))["models"]
MARKERS = ["caved_on_fact", "forged_document", "cheerled_bad_plan", "snapped_to_task"]
conduct, per_marker = {}, {}
for m, md in mk.items():
    v = []
    for mid, mv in md.items():
        if mv.get("type") != "binary": continue
        r = [1 if x else 0 for x in mv["runs"] if x is not None]
        if r: per_marker.setdefault(mid, {})[m] = sum(r)/len(r); v += r
    if v: conduct[m] = sum(v)/len(v)
arena = {}
for ln in open(H/"arena_2026-09-11.txt"):
    if ":" in ln: k, v = ln.rsplit(":",1); arena[k.strip()] = float(v)
eci_rows = {r["Model"]: r for r in csv.DictReader(open(H/"eci_scores_2026-09-13.csv"))}
eci, dates = {}, {}
for ln in open(H/"eci_map_2026-09-13.tsv"):
    if ln.startswith("#") or "\t" not in ln: continue
    ours, theirs = ln.rstrip("\n").split("\t")
    r = eci_rows[theirs]; eci[ours] = float(r["eci"]); dates[ours] = datetime.date.fromisoformat(r["date"]).toordinal()
cols = {
  "census_conc":   {m: -v["surprisal"] for m, v in cons.items()},   # higher = more concentrated
  "suggestib":     {m: v["suggestibility"] for m, v in sugg.items()},
  "sugg_taste":    {m: v["shift_taste"] for m, v in sugg.items()},
  "sugg_conseq":   {m: v["shift_consequential"] for m, v in sugg.items()},
  "format_tax":    {m: -v["delta"] for m, v in fmt.items()},          # higher = bigger drop under JSON
  "conduct_dep":   conduct,
  "capability":    eci,
  "release_date":  dates,
  "cap_arena":     arena,
}
BEH = ["census_conc", "suggestib", "format_tax", "conduct_dep"]
CTRL = ["capability", "release_date", "cap_arena"]
allm = sorted(set().union(*[set(c) for c in cols.values()]))
def rank(x):
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
def resid(y,x):
    ry, rx = rank(y), rank(x); n=len(y); mx=sum(rx)/n; my=sum(ry)/n
    b=sum((a-mx)*(c-my) for a,c in zip(rx,ry))/max(1e-9,sum((a-mx)**2 for a in rx))
    return [c-(my+b*(a-mx)) for a,c in zip(rx,ry)]
def series(a, b, ctrls=()):
    """x, y for the models carrying a, b and every control, residualized on the controls in turn."""
    A = cols[a] if isinstance(a, str) else a; Bc = cols[b] if isinstance(b, str) else b
    ms=[m for m in allm if m in A and m in Bc and all(m in cols[c] for c in ctrls)]
    x=[A[m] for m in ms]; y=[Bc[m] for m in ms]
    for c in ctrls:
        cv=[cols[c][m] for m in ms]; x=resid(x,cv); y=resid(y,cv)
    return ms, x, y
def line(label, a, b, ctrls=(), minn=8):
    ms, x, y = series(a, b, ctrls)
    if len(ms) < minn: print(f"{label:<46}n={len(ms):>3}  (too few)"); return
    r=spearman(x,y); lo,hi=boot(x,y)
    print(f"{label:<46}n={len(ms):>3}  rho={r:>6.2f}  90% CI [{lo:.2f}, {hi:.2f}]{' *' if lo>0 or hi<0 else ''}")
if __name__ == "__main__":
    print("coverage:", {k: len(v) for k,v in cols.items()})
    core=[m for m in allm if all(m in cols[c] for c in BEH)]
    print(f"models on all four behavior instruments: {len(core)}; with ECI {sum(1 for m in core if m in eci)}; with Arena {sum(1 for m in core if m in arena)}")
    line("capability (ECI) x cap_arena", "capability", "cap_arena")
    line("capability (ECI) x release_date", "capability", "release_date")
    print("\n== instruments vs each other, raw ==")
    for a,b in itertools.combinations(BEH,2): line(a+" x "+b, a, b)
    print("\n== instruments vs capability, vs release date, and capability | date ==")
    for k in ["census_conc","suggestib","sugg_taste","sugg_conseq","format_tax","conduct_dep"]:
        line(k+" x capability", k, "capability"); line(k+" x release_date", k, "release_date")
        line("  "+k+" x capability | release_date", k, "capability", ["release_date"])
    print("\n== instrument pairs partialled on capability, on release date, and on both ==")
    for a,b in itertools.combinations(BEH,2):
        line("  "+a+" x "+b+" | capability", a, b, ["capability"])
        line("  "+a+" x "+b+" | release_date", a, b, ["release_date"])
        line("  "+a+" x "+b+" | date then capability", a, b, ["release_date","capability"])
    print("\n== per marker (departure rate) ==")
    for mid in MARKERS:
        for c in ["census_conc","capability","release_date"]: line(mid+" x "+c, per_marker[mid], c)
        line("  "+mid+" x census_conc | release_date", per_marker[mid], "census_conc", ["release_date"])
    for a,b in itertools.combinations(MARKERS,2): line(a+" x "+b, per_marker[a], per_marker[b])
    print("\njoint panel (four instruments + ECI):", sorted(m for m in core if m in eci))
