#!/usr/bin/env python3
"""Regenerate the paper's tables from the frozen data. Every number in main.tex comes from here
(gen/*.tex, gen/stats.json) or from the dated result files in the study directory."""
import sys, io, json, itertools, contextlib, datetime
from pathlib import Path
H = Path(__file__).resolve().parent; sys.path.insert(0, str(H.parent))
import os; os.chdir(H.parent)
from build_matrix import cols, spearman, boot, resid, allm, per_marker, MARKERS, eci, arena, BEH
dates = cols["release_date"]

# ---- pin the conduct panel ------------------------------------------------------------
# The adjudicated store grows as models are judged; this paper's numbers must not move
# because it grew. panel.txt names the conduct models this paper reports, and widening it
# is a decision to re-report rather than a side effect of a judge pass. Delete the file to
# report whatever the store currently holds.
_panel_f = H / "panel.txt"
if _panel_f.exists():
    _panel = {l.strip() for l in _panel_f.read_text().splitlines()
              if l.strip() and not l.startswith("#")}
    _have = set(cols["conduct_dep"])
    _gone = _panel - _have
    if _gone:
        raise SystemExit(f"panel.txt lists {len(_gone)} models the store no longer scores: "
                         + ", ".join(sorted(_gone)))
    _dropped = _have - _panel
    cols["conduct_dep"] = {m: v for m, v in cols["conduct_dep"].items() if m in _panel}
    # per_marker feeds the marker-level stats (the house pair in section 1) and is read
    # straight from the store, so it needs the same pin or those numbers move on their own.
    for _mid in list(per_marker):
        per_marker[_mid] = {m: v for m, v in per_marker[_mid].items() if m in _panel}
    print(f"conduct panel pinned to {len(cols['conduct_dep'])} models "
          f"({len(_dropped)} scored but not reported)", file=sys.stderr)

core = [m for m in allm if all(m in cols[c] for c in BEH)]
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
for k in ["sugg_taste","sugg_conseq","sugg_shift"]:
    n0,x0,y0 = pair(k,"capability"); n1,x1,y1 = pair(k,"capability",[dates])
    stats[k] = {"n": n0, "raw": spearman(x0,y0), "raw_ci": boot(x0,y0), "partial_date": spearman(x1,y1), "partial_date_ci": boot(x1,y1)}
ms = [m for m in cols["suggestib"] if m in cols["sugg_shift"]]
stats["tageff_x_shift"] = {"n": len(ms), "rho": spearman([cols["suggestib"][m] for m in ms],[cols["sugg_shift"][m] for m in ms])}
ms = [m for m in per_marker["cheerled_bad_plan"] if m in per_marker["snapped_to_task"]]
stats["cheerled_x_snapped"] = {"n": len(ms), "rho": spearman([per_marker["cheerled_bad_plan"][m] for m in ms],[per_marker["snapped_to_task"][m] for m in ms])}
open("gen/marker_table.tex","w").write("\n".join(rows)+"\n\\bottomrule%\n")
stats["coverage"] = {k: len(v) for k, v in cols.items()}
stats["core"] = len(core); stats["core_eci"] = sum(1 for m in core if m in eci); stats["core_arena"] = sum(1 for m in core if m in arena)
ms = [m for m in eci if m in arena]; stats["eci_x_arena"] = {"n": len(ms), "rho": spearman([eci[m] for m in ms],[arena[m] for m in ms])}
ms = [m for m in eci if m in dates]; stats["eci_x_date"] = {"n": len(ms), "rho": spearman([eci[m] for m in ms],[dates[m] for m in ms])}
# fold rate over all four markers by release: the generation claim in 3.3
_c = cols["conduct_dep"]; ms = sorted((m for m in _c if m in dates), key=dates.get); _k = len(ms)//3
_new = [m for m in ms if dates[m] >= datetime.date(2025, 7, 1).toordinal()]
stats["conduct_by_date"] = {"n": len(ms), "rho_date": spearman([_c[m] for m in ms], [dates[m] for m in ms]),
    "oldest_third_n": _k, "oldest_third_fold": sum(_c[m] for m in ms[:_k])/_k,
    "post_mid2025_n": len(_new), "post_mid2025_fold": sum(_c[m] for m in _new)/len(_new)}
json.dump(stats, open("gen/stats.json","w"), indent=1)
print(json.dumps(stats, indent=1))
