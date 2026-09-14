#!/usr/bin/env python3
"""Regenerate the paper's tables from the frozen data. Every number in main.tex comes from here
(gen/*.tex, gen/stats.json) or from the dated result files in the study directory."""
import sys, io, json, itertools, contextlib, datetime
from pathlib import Path
H = Path(__file__).resolve().parent; sys.path.insert(0, str(H.parent))
import os; os.chdir(H.parent)
with contextlib.redirect_stdout(io.StringIO()):
    from build_matrix import cols, spearman, boot, resid, allm, per_marker, MARKERS, eci, arena, core
dates = {}
for ln in open("eci_dates_2026-09-13.txt"):
    if ln.startswith("#") or ":" not in ln: continue
    k, v = ln.rsplit(":",1); dates[k.strip()] = datetime.date.fromisoformat(v.strip()).toordinal()
os.chdir(H); (H/"gen").mkdir(exist_ok=True)
LABEL = {"census_conc":"census","suggestib":"suggestibility","format_tax":"format tax",
         "conduct_dep":"conduct","capability":"capability"}
def cell(x, y):
    r = spearman(x, y); lo, hi = boot(x, y)
    s = f"{r:.2f} [{lo:.2f}, {hi:.2f}]"
    return (r"\textbf{"+s+"}") if (lo > 0 or hi < 0) else s
def pair(a, b, ctrls=()):
    ms = [m for m in allm if m in cols[a] and m in cols[b] and all(m in c for c in ctrls)]
    x = [cols[a][m] for m in ms]; y = [cols[b][m] for m in ms]
    for c in ctrls:
        cv = [c[m] for m in ms]; x = resid(x, cv); y = resid(y, cv)
    return len(ms), x, y
stats = {}
# Table 1: raw matrix, and the same pairs partialled on ECI and on release date
beh = ["census_conc","suggestib","format_tax","conduct_dep"]
rows = []
for a, b in itertools.combinations(beh + ["capability"], 2):
    n, x, y = pair(a, b); raw = cell(x, y)
    if "capability" in (a, b):
        n2, x2, y2 = pair(a, b, [dates]); pe = "--"; pd_ = cell(x2, y2); nn = f"{n} / {n2}"
    else:
        n1, x1, y1 = pair(a, b, [eci]); n2, x2, y2 = pair(a, b, [dates])
        pe = cell(x1, y1); pd_ = cell(x2, y2); nn = f"{n} / {n1}"
    rows.append(f"{LABEL[a]} $\\times$ {LABEL[b]} & {nn} & {raw} & {pe} & {pd_} \\\\")
    stats[f"{a}x{b}"] = {"n": n, "raw": spearman(*pair(a,b)[1:]), "partial_eci": None if "capability" in (a,b) else spearman(x1,y1), "partial_date": spearman(x2,y2)}
open("gen/matrix_table.tex","w").write("\n".join(rows)+"\n\\bottomrule%\n")
# Table 2: per-marker
rows = []
MLAB = {"caved_on_fact":"caved on fact","forged_document":"forged document","cheerled_bad_plan":"cheerled bad plan","snapped_to_task":"snapped to task"}
for mid in MARKERS:
    out = [MLAB[mid]]
    for c in ["census_conc","capability"]:
        ms = [m for m in per_marker[mid] if m in cols[c]]
        x = [per_marker[mid][m] for m in ms]; y = [cols[c][m] for m in ms]
        out.append(f"{cell(x,y)} ({len(ms)})")
    ms = [m for m in per_marker[mid] if m in cols["census_conc"] and m in dates]
    x = resid([per_marker[mid][m] for m in ms],[dates[m] for m in ms]); y = resid([cols["census_conc"][m] for m in ms],[dates[m] for m in ms])
    out.append(f"{cell(x,y)} ({len(ms)})")
    rows.append(" & ".join(out)+" \\\\")
ms = [m for m in per_marker["cheerled_bad_plan"] if m in per_marker["snapped_to_task"]]
stats["cheerled_x_snapped"] = {"n": len(ms), "rho": spearman([per_marker["cheerled_bad_plan"][m] for m in ms],[per_marker["snapped_to_task"][m] for m in ms])}
open("gen/marker_table.tex","w").write("\n".join(rows)+"\n\\bottomrule%\n")
stats["coverage"] = {k: len(v) for k, v in cols.items()}
stats["core"] = len(core); stats["core_eci"] = sum(1 for m in core if m in eci); stats["core_arena"] = sum(1 for m in core if m in arena)
ms = [m for m in eci if m in arena]; stats["eci_x_arena"] = {"n": len(ms), "rho": spearman([eci[m] for m in ms],[arena[m] for m in ms])}
ms = [m for m in eci if m in dates]; stats["eci_x_date"] = {"n": len(ms), "rho": spearman([eci[m] for m in ms],[dates[m] for m in ms])}
json.dump(stats, open("gen/stats.json","w"), indent=1)
print(json.dumps(stats, indent=1))
