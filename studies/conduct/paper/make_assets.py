#!/usr/bin/env python3
"""Regenerate the paper's figure and the numbers it quotes from the frozen labels.

    python3 make_assets.py      # -> figs/hold_fold.pdf, gen/stats.json

Trajectory consensus is the majority of the six LLM coders on codebook v2
(data/coding/relabel_v2.llm-*.jsonl), over the three scenes the codebook was built on. Blind ids
are reversed with the same salt the coding page used (harness/viewer/arcs.py), so the rows here
are the same arcs every coder saw.
"""
import sys, csv, json, collections
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parent.parent
sys.path.insert(0, str(ROOT))
from harness.viewer.arcs import blind      # the coding page's blind ids; never reimplement the salt

XI = ROOT / "studies" / "cross-instrument"
SALT = "conduct-2026-09"
SCENES = [("facts", "facts"), ("doctors_note", "note"), ("bad_plan", "plan")]
SCENE_IDS = {s for s, _ in SCENES}
VEND = {"anthropic": "Anthropic", "openai": "OpenAI", "google": "Google", "meta-llama": "Meta",
        "x-ai": "xAI", "deepseek": "DeepSeek", "qwen": "Qwen", "moonshotai": "Moonshot",
        "mistralai": "Mistral", "cohere": "Cohere"}

BLUE, GRAY, GRID = "#2a78d6", "#52514e", "#d9d8d4"
plt.rcParams.update({
    "font.family": "sans-serif", "font.size": 8.5,
    "axes.edgecolor": GRAY, "axes.linewidth": 0.6,
    "xtick.color": GRAY, "ytick.color": GRAY,
    "text.color": "#0b0b0b", "axes.labelcolor": "#0b0b0b",
    "pdf.fonttype": 42,
})
(HERE / "figs").mkdir(exist_ok=True)
(HERE / "gen").mkdir(exist_ok=True)

# ---- the panel, and blind id -> model (same salt as the coding page) ----------------------
# The coded panel is the frozen panel (spec/models.txt, 38) plus the dated specimens coded with
# it (22); 60 models carry v2 labels. Membership here is "has labels", not the frozen list.
reveal, vendor = {}, {}
for p in sorted((STUDY / "data" / "benchmark").glob("*.json")):
    if p.name == "markers.json":
        continue
    d = json.loads(p.read_text())
    bid = blind(d["model"], SALT)
    reveal[bid] = d["model"]
    vendor[d["model"]] = d.get("slug", "/").split("/")[0]

# ---- release dates, so a lab's rows read as its release history ------------------------
_eci = {r["Model"]: r for r in csv.DictReader(open(XI / "eci_scores_2026-09-13.csv"))}
dates = {}
for _ln in open(XI / "eci_map_2026-09-13.tsv"):
    if _ln.startswith("#") or "\t" not in _ln:
        continue
    _ours, _theirs = _ln.rstrip("\n").split("\t")
    dates[_ours] = _eci[_theirs]["date"]

# ---- trajectory consensus: majority of the six coders per arc ----------------------------
votes = collections.defaultdict(collections.Counter)
coders = set()
for p in sorted((STUDY / "data" / "coding").glob("relabel_v2.llm-*.jsonl")):
    for line in p.read_text().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if r.get("kind") != "trajectory" or not r.get("code"):
            continue
        if r["scene"] not in SCENE_IDS:
            continue
        coders.add(r["coder"])
        votes[(r["blind"], r["scene"], r["run"])][r["code"]] += 1

cells, n_tied = {}, 0
for key, c in votes.items():
    held, folded = c.get("HELD", 0), c.get("FOLDED", 0)
    if held == folded:
        n_tied += 1
        cells[key] = "TIED"                        # 3-3; drawn as its own cell, never as held
        continue
    cells[key] = "FOLDED" if folded > held else "HELD"

rows = []
for bid, model in reveal.items():
    mine = {(s, r): v for (b, s, r), v in cells.items() if b == bid}
    if not mine:
        continue
    resolved = sum(1 for v in mine.values() if v != "TIED")
    rows.append({"model": model, "vendor": vendor.get(model, "other"), "cells": mine,
                 "date": dates.get(model),
                 "folds": sum(1 for v in mine.values() if v == "FOLDED") / max(1, resolved),
                 "n": len(mine)})

by = collections.defaultdict(list)
for r in rows:
    by[r["vendor"] if r["vendor"] in VEND else "other"].append(r)
order = sorted(by, key=lambda v: (v == "other", sum(x["folds"] for x in by[v]) / len(by[v])))

# ---- the grid, two columns so it fits one page --------------------------------------------
blocks = [(v, sorted(by[v], key=lambda x: (x["date"] is None, x["date"] or "", x["model"])))
          for v in order]
units = [len(b[1]) + 2 for b in blocks]            # rows plus the vendor header and its gap
half, run, cut = sum(units) / 2, 0, len(blocks)
for i, u in enumerate(units):                      # split on the block boundary nearest the middle
    if run + u / 2 >= half:
        cut = i
        break
    run += u
columns = [blocks[:cut], blocks[cut:]]

CW, CH, GAPX = 0.62, 0.70, 0.60                    # cell width, height, gap between scenes
XOFF = 11.6                                        # distance between the two columns
xs0 = [i * (2 * CW + GAPX) for i in range(len(SCENES))]
right0 = xs0[-1] + 2 * CW
tallest = max(sum(len(b[1]) + 2 for b in col) for col in columns)
fig, ax = plt.subplots(figsize=(6.3, 0.125 * tallest + 0.85))
ax.set_axis_off()

for ci, col in enumerate(columns):
    dx = ci * XOFF
    xs = [x + dx for x in xs0]
    right = right0 + dx
    y = 0.0
    for i, (_, label) in enumerate(SCENES):
        ax.text(xs[i] + CW, y + 0.5, label, fontsize=7, color=GRAY, ha="center")
    y -= 0.55
    for v, rs in col:
        ax.text(dx - 4.5, y + 0.45, VEND.get(v, "Other vendors").upper(), fontsize=6.6,
                color=GRAY, ha="left", va="center")
        y -= 1.15
        for r in rs:
            name = r["model"] if len(r["model"]) <= 24 else r["model"][:23] + "\u2026"
            if r["date"] is None:
                name += " \u00b7"        # no release date in the snapshot; sorted to the end
            ax.text(dx - 0.35, y + CH / 2, name, fontsize=6.6, ha="right", va="center")
            for i, (sid, _) in enumerate(SCENES):
                for run_i in (0, 1):
                    x = xs[i] + run_i * CW
                    t = r["cells"].get((sid, run_i))
                    face = {"FOLDED": BLUE, "TIED": GRID}.get(t, "white")
                    ax.add_patch(Rectangle((x, y), CW - 0.09, CH - 0.10,
                                           facecolor=face,
                                           edgecolor=BLUE if t == "FOLDED" else GRID,
                                           linewidth=0.6, zorder=2))
            ax.text(right + 0.3, y + CH / 2, f"{round(100 * r['folds'])}%", fontsize=6.4,
                    color=GRAY, ha="left", va="center")
            y -= 1.0
        y -= 0.55
    bottom = y if ci == 0 else min(bottom, y)

# legend: the encoding is fill, so it survives grayscale and colour-blind readers
ly = bottom - 0.5
for i, (face, edge, label) in enumerate([(BLUE, BLUE, "folded"), ("white", GRID, "held"),
                                         (GRID, GRID, "no consensus")]):
    lx = i * (CW + 1.7)
    ax.add_patch(Rectangle((lx, ly), CW - 0.09, CH - 0.10, facecolor=face, edgecolor=edge, lw=0.6))
    ax.text(lx + CW + 0.15, ly + CH / 2, label, fontsize=7, va="center")

ax.set_xlim(-5.0, XOFF + right0 + 1.5)
ax.set_ylim(min(ly, bottom) - 0.8, 0.9)
fig.tight_layout(pad=0.2)
fig.savefig(HERE / "figs" / "hold_fold.pdf")
plt.close(fig)

# ---- numbers this figure is responsible for ----------------------------------------------
per_vendor = {}
for v, rs in by.items():
    per_vendor[VEND.get(v, "other")] = {
        "models": len(rs),
        "fold_rate": round(sum(x["folds"] for x in rs) / len(rs), 4),
    }
stats = {
    "panel_models": len(rows),
    "coders": sorted(coders),
    "arcs": sum(r["n"] for r in rows),
    "tied_arcs": n_tied,   # 3-3 splits: drawn as their own cell, out of the fold-rate denominator
    "fold_rate_panel": round(sum(r["folds"] for r in rows) / len(rows), 4),
    "per_vendor": per_vendor,
    "per_model_fold_rate": {r["model"]: round(r["folds"], 4) for r in
                            sorted(rows, key=lambda x: -x["folds"])},
}
(HERE / "gen" / "stats.json").write_text(json.dumps(stats, indent=2) + "\n")
print(f"{len(rows)} models, {stats['arcs']} arcs, {len(coders)} coders, "
      f"{n_tied} tied arcs -> figs/hold_fold.pdf, gen/stats.json")

# ---- the paper's two tables, from the dated analysis files -------------------------------
# The statistics live in harness/manner_matrix.py and harness/house_profiles.py; this reads
# their newest dated output rather than reimplementing them, so there is one implementation of
# the permutation test and the paper cannot drift from it.
RESULTS = STUDY / "data" / "coding" / "results"
matrix_file = sorted(RESULTS.glob("MANNER-MATRIX-v2-*.md"))[-1]
profiles_file = sorted(RESULTS.glob("HOUSE-PROFILES-v2-*.md"))[-1]

FULL = {"folded: apologized": "folded and apologized", "conceded": "folded and conceded",
        "encouraged": "folded and encouraged", "produced": "folded and produced",
        "folded: warned": "folded and warned", "held: apologized": "held and apologized",
        "cited itself": "held and cited itself", "defended the fact": "held and defended the fact",
        "diverted": "held and diverted", "empathized": "held and empathized",
        "explained": "held and explained", "gave the user an out": "held and gave the user an out",
        "probed": "held and probed", "provided an alternative": "held and provided an alternative",
        "supported the person": "held and supported the person",
        "supported with evidence": "held and supported with evidence", "held: warned": "held and warned"}

def tex_num(x, digits=2):
    return f"${x:.{digits}f}$" if x >= 0 else f"$-{abs(x):.{digits}f}$"

vendor_rows, by_flag = [], {}
blk = matrix_file.read_text().split("## 3.")[1].split("## 4.")[0]
for line in blk.splitlines():
    c = [x.strip() for x in line.strip().strip("|").split("|")]
    if len(c) != 9 or c[0] == "code" or c[0].startswith("---") or "trajectory" in c[0]:
        continue
    e, pv, rho = float(c[1]), float(c[2]), float(c[4])
    by_flag[FULL[c[0]]] = c[3]
    vendor_rows.append({"code": FULL[c[0]], "eta2": e, "p": pv, "by": c[3], "rho": rho, "top": c[8]})
vendor_rows.sort(key=lambda r: -r["eta2"])

cleared = [r for r in vendor_rows if r["by"] == "yes"]
with open(HERE / "gen" / "vendor_table.tex", "w") as f:
    for r in cleared:
        pstr = "$<$0.001" if r["p"] < 0.0005 else f"{r['p']:.3f}"
        f.write(f"{r['code']} & {r['eta2']:.2f} & {pstr} & {tex_num(r['rho'])} & {r['top']} \\\\\n")
    f.write("\\bottomrule%\n")

# per-vendor rates and the panel mean, from the profiles file
prof, fold = collections.defaultdict(dict), {}
cur = None
for line in profiles_file.read_text().splitlines():
    if line.startswith("## ") and "(" in line and "models:" in line:
        cur = line[3:].split()[0]
    elif cur and line.startswith("Fold rate:"):
        fold[cur] = (float(line.split()[2]), float(line.split("panel ")[1].split(")")[0]))
    elif cur and line.startswith("| ") and line.count("|") == 5:
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if c[0] in ("code",) or c[0].startswith("---"):
            continue
        try: prof[cur][c[0]] = (float(c[1]), float(c[2]))
        except ValueError: pass

# which codes each row names is an editorial choice, kept explicit here
SIGNATURE = [
    ("Anthropic", "anthropic", [("empathized", "held and empathized"), ("warned", "held and warned"),
                                ("alternative", "held and provided an alternative")]),
    ("Meta", "meta-llama", [("produced", "folded and produced"), ("folded and warned", "folded and warned"),
                            ("probed", "held and probed")]),
    ("OpenAI", "openai", [("warned", "held and warned"), ("empathized", "held and empathized"),
                          ("cited itself", "held and cited itself")]),
    ("Google", "google", [("cited itself", "held and cited itself"),
                          ("folded and apologized", "folded and apologized")]),
    ("x-ai", "x-ai", [("warned", "held and warned"),
                      ("supported with evidence", "held and supported with evidence")]),
]
with open(HERE / "gen" / "profiles_table.tex", "w") as f:
    for label, key, codes_named in SIGNATURE:
        n_models = sum(1 for r in rows if vendor.get(r["model"]) == key)
        sig = ", ".join(f"{disp} {prof[key][code][0]:.2f} ({prof[key][code][1]:.2f})"
                        for disp, code in codes_named if code in prof[key])
        if key == "x-ai":
            sig += "; never folds"
        f.write(f"{label} ({n_models}) & {fold[key][0]:.2f} & {sig} \\\\\n")
    f.write("\\bottomrule%\n")

with open(HERE / "gen" / "allcodes_table.tex", "w") as f:      # the appendix table, all 17
    for r in vendor_rows:
        pstr = "$<$0.001" if r["p"] < 0.0005 else f"{r['p']:.3f}"
        f.write(f"{r['code']} & {r['eta2']:.2f} & {pstr} & {r['by']} & {tex_num(r['rho'])} & {r['top']} \\\\\n")
    f.write("\\bottomrule%\n")

stats["vendor_effects"] = {r["code"]: {"eta2": r["eta2"], "p": r["p"], "by": r["by"], "rho": r["rho"]}
                           for r in vendor_rows}
stats["sources"] = {"matrix": matrix_file.name, "profiles": profiles_file.name}
(HERE / "gen" / "stats.json").write_text(json.dumps(stats, indent=2) + "\n")
print(f"tables from {matrix_file.name} and {profiles_file.name}: "
      f"{len(cleared)} cleared codes, {len(SIGNATURE)} vendor rows")
