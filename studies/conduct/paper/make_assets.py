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
# the second, preregistered set (spec/stimulus-v2.json), coded under v2w2; drawn beside the first
SCENES2 = [("boiling", "boil"), ("reference", "ref"), ("review", "review"), ("exclude", "excl"),
           ("dropout", "drop"), ("lease", "lease")]
VEND = {"anthropic": "Anthropic", "openai": "OpenAI", "google": "Google", "meta-llama": "Meta",
        "x-ai": "xAI", "deepseek": "DeepSeek", "qwen": "Qwen", "moonshotai": "Moonshot"}
# Mistral (2) and Cohere (2) draw under "Other vendors" with the singletons; they stay in the vendor test.

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
# it (22); 60 models carry v2 labels.
#
# Membership used to be "has labels", which was only accidentally 60: the benchmark directory
# holds more transcripts than that, and they are excluded solely because nobody has coded them
# yet. Code two of them and this file would quietly report 62 while the prose still said 60.
# panel.txt names the 60 this paper reports, and _panel_check below fails if the label set and
# the list disagree in either direction. Delete panel.txt to follow the labels again.
reveal, vendor = {}, {}
for p in sorted((STUDY / "data" / "benchmark").glob("*.json")):
    if p.name == "markers.json":
        continue
    d = json.loads(p.read_text())
    bid = blind(d["model"], SALT)
    reveal[bid] = d["model"]
    vendor[d["model"]] = d.get("slug", "/").split("/")[0]

# ---- the frozen panel, pinned -----------------------------------------------------------
_panel_f = HERE / "panel.txt"
if _panel_f.exists():
    _pinned = {l.strip() for l in _panel_f.read_text().splitlines()
               if l.strip() and not l.startswith("#")}
    _v2 = set()
    for _p in sorted((STUDY / "data" / "coding").glob("relabel_v2.llm-*.jsonl")):
        for _ln in _p.read_text().splitlines():
            if _ln.strip():
                _v2.add(json.loads(_ln)["blind"])
    _coded = {reveal[b] for b in _v2 if b in reveal}
    _new = _coded - _pinned
    _lost = _pinned - _coded
    # --panel-only: models coded since the panel was pinned (appended waves) are left out of the
    # figure and tables, explicitly, so the pinned n stands. Widening the panel is still an edit
    # to panel.txt.
    PANEL_ONLY = "--panel-only" in sys.argv
    if PANEL_ONLY and _new and not _lost:
        print(f"panel-only: leaving out {len(_new)} coded models not in panel.txt: {', '.join(sorted(_new))}")
        reveal = {b: m for b, m in reveal.items() if m in _pinned}
        _new = set()
    if _new or _lost:
        raise SystemExit(
            "panel.txt and the coded set disagree, so the paper's n would move silently.\n"
            + (f"  newly coded, not in panel.txt ({len(_new)}): {', '.join(sorted(_new))}\n" if _new else "")
            + (f"  in panel.txt, no longer coded ({len(_lost)}): {', '.join(sorted(_lost))}\n" if _lost else "")
            + "  Widen the panel by editing panel.txt, deliberately, and restate n in the prose.")

# ---- release dates, so a lab's rows read as its release history ------------------------
_eci = {r["Model"]: r for r in csv.DictReader(open(XI / "eci_scores_2026-09-13.csv"))}
dates = {}
for _ln in open(XI / "eci_map_2026-09-13.tsv"):
    if _ln.startswith("#") or "\t" not in _ln:
        continue
    _ours, _theirs = _ln.rstrip("\n").split("\t")
    dates[_ours] = _eci[_theirs]["date"]
for _ln in open(STUDY / "spec" / "release-dates.tsv"):          # the six the snapshot misses
    if _ln.startswith("#") or "\t" not in _ln:
        continue
    _m, _d = _ln.split("\t")[:2]
    dates.setdefault(_m.strip(), _d.strip())

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

# ---- the second set: consensus per arc from the v2w2 labels, models by their own transcripts --
reveal2 = {}
for p in sorted((STUDY / "data" / "wave2").glob("*.json")):
    d = json.loads(p.read_text()); reveal2[blind(d["model"], SALT)] = d["model"]
    vendor.setdefault(d["model"], d.get("slug", "/").split("/")[0])
votes2 = collections.defaultdict(collections.Counter)
for p in sorted((STUDY / "data" / "coding").glob("relabel_v2w2.llm-*.jsonl")):
    for line in p.read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            if r["kind"] == "trajectory" and r["code"]:
                votes2[(r["blind"], r["scene"], r["run"])][r["code"]] += 1
cells2, n_tied2 = {}, 0
for key, c in votes2.items():
    held, folded = c.get("HELD", 0), c.get("FOLDED", 0)
    if held == folded: n_tied2 += 1; cells2[key] = "TIED"; continue
    cells2[key] = "FOLDED" if folded > held else "HELD"
by_model = {r["model"]: r for r in rows}
for bid, model in reveal2.items():
    mine = {(sc, run): v for (b, sc, run), v in cells2.items() if b == bid}
    if not mine: continue
    resolved = sum(1 for v in mine.values() if v != "TIED")
    f2 = sum(1 for v in mine.values() if v == "FOLDED") / max(1, resolved)
    if model in by_model:
        by_model[model]["cells2"] = mine; by_model[model]["folds2"] = f2
    else:   # appended after the first set was pinned: drawn with blanks on the first set
        r = {"model": model, "vendor": vendor.get(model, "other"), "cells": {}, "date": dates.get(model),
             "folds": None, "n": 0, "cells2": mine, "folds2": f2, "appended": True}
        rows.append(r); by_model[model] = r
n_rows2 = sum(1 for r in rows if "cells2" in r)

by = collections.defaultdict(list)
for r in rows:
    by[r["vendor"] if r["vendor"] in VEND else "other"].append(r)
def _mean_fold(rs):
    xs = [x["folds"] for x in rs if x["folds"] is not None]
    return sum(xs) / len(xs) if xs else 1.0
order = sorted(by, key=lambda v: (v == "other", _mean_fold(by[v])))

# ---- the grid: one column, both scene sets side by side ------------------------------------
blocks = [(v, sorted(by[v], key=lambda x: (x["date"] is None, x["date"] or "", x["model"])))
          for v in order]
CW, CH, GAPX, GAPSET = 0.62, 0.70, 0.45, 1.3      # cell, gap between scenes, gap between the sets
xs1 = [i * (2 * CW + GAPX) for i in range(len(SCENES))]
x2start = xs1[-1] + 2 * CW + GAPSET
xs2 = [x2start + i * (2 * CW + GAPX) for i in range(len(SCENES2))]
right = xs2[-1] + 2 * CW
n_lines = sum(len(b[1]) + 2 for b in blocks)
fig, ax = plt.subplots(figsize=(6.3, min(8.6, 0.105 * n_lines + 0.9)))
ax.set_axis_off()

y = 0.0
for i, (_, label) in enumerate(SCENES):
    ax.text(xs1[i] + CW, y + 0.5, label, fontsize=6.6, color=GRAY, ha="center")
for i, (_, label) in enumerate(SCENES2):
    ax.text(xs2[i] + CW, y + 0.5, label, fontsize=6.6, color=GRAY, ha="center")
ax.text((xs1[0] + xs1[-1] + 2 * CW) / 2, y + 1.25, "first set", fontsize=6.6, color=GRAY, ha="center")
ax.text((xs2[0] + right) / 2, y + 1.25, "second set (preregistered)", fontsize=6.6, color=GRAY, ha="center")
y -= 0.55
def _cell(x, y, t):
    if t is None:        # not run on this set
        return
    face = {"FOLDED": BLUE, "TIED": GRID}.get(t, "white")
    ax.add_patch(Rectangle((x, y), CW - 0.09, CH - 0.10, facecolor=face,
                           edgecolor=BLUE if t == "FOLDED" else GRID, linewidth=0.6, zorder=2))
for v, rs in blocks:
    ax.text(-4.6, y + 0.45, VEND.get(v, "Other vendors").upper(), fontsize=6.6, color=GRAY, ha="left", va="center")
    y -= 1.15
    for r in rs:
        name = r["model"] if len(r["model"]) <= 24 else r["model"][:23] + "\u2026"
        ax.text(-0.35, y + CH / 2, name, fontsize=5.9, ha="right", va="center")
        for i, (sid, _) in enumerate(SCENES):
            for run_i in (0, 1):
                _cell(xs1[i] + run_i * CW, y, r["cells"].get((sid, run_i)) if r["cells"] else None)
        for i, (sid, _) in enumerate(SCENES2):
            for run_i in (0, 1):
                _cell(xs2[i] + run_i * CW, y, r["cells2"].get((sid, run_i)) if "cells2" in r else None)
        p1 = f"{round(100 * r['folds'])}%" if r["folds"] is not None else "\u2013"
        p2 = f"{round(100 * r['folds2'])}%" if r.get("folds2") is not None else "\u2013"
        ax.text(right + 0.3, y + CH / 2, f"{p1:>4} {p2:>4}", fontsize=5.8, color=GRAY, ha="left", va="center", family="monospace")
        y -= 1.0
    y -= 0.55
bottom = y

# legend: the encoding is fill, so it survives grayscale and colour-blind readers
ly = bottom - 0.5
for i, (face, edge, label) in enumerate([(BLUE, BLUE, "folded"), ("white", GRID, "held"),
                                         (GRID, GRID, "no consensus")]):
    lx = i * (CW + 1.9)
    ax.add_patch(Rectangle((lx, ly), CW - 0.09, CH - 0.10, facecolor=face, edgecolor=edge, lw=0.6))
    ax.text(lx + CW + 0.15, ly + CH / 2, label, fontsize=6.6, va="center")
ax.text(lx + CW + 4.2, ly + CH / 2, "blank: not run on that set", fontsize=6.6, va="center", color=GRAY)

ax.set_xlim(-5.0, right + 3.6)
ax.set_ylim(ly - 0.8, 1.9)
fig.tight_layout(pad=0.2)
fig.savefig(HERE / "figs" / "hold_fold.pdf")
plt.close(fig)

# ---- the scatter: fold rate against capability, one point per model, one panel per set ------
eci = {}
for _ln in open(XI / "eci_map_2026-09-13.tsv"):
    if _ln.startswith("#") or "\t" not in _ln:
        continue
    _ours, _theirs = _ln.rstrip("\n").split("\t")
    eci[_ours] = float(_eci[_theirs]["eci"])

def _ranks(xs):
    """Ranks with ties averaged, as the paper's correlations use."""
    idx = sorted(range(len(xs)), key=lambda i: xs[i]); rk = [0.0] * len(xs); i = 0
    while i < len(idx):
        j = i
        while j + 1 < len(idx) and xs[idx[j + 1]] == xs[idx[i]]:
            j += 1
        for k in range(i, j + 1):
            rk[idx[k]] = (i + j) / 2 + 1
        i = j + 1
    return rk
def spearman(x, y):
    rx, ry = _ranks(x), _ranks(y); mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    return num / (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5

HUE = {"anthropic": "#c2562f", "openai": "#1f7a52", "google": "#2a78d6", "meta-llama": "#7b4fb3"}
fig, axs = plt.subplots(1, 2, figsize=(3.1, 1.75), sharey=True)
rho = {}
for ax, key, title in [(axs[0], "folds", "first set"), (axs[1], "folds2", "second set")]:
    pts = [(eci[r["model"]], r[key], r["vendor"]) for r in rows
           if r.get(key) is not None and r["model"] in eci]
    rho[key] = (spearman([p[0] for p in pts], [p[1] for p in pts]), len(pts))
    for x, yv, v in sorted(pts, key=lambda p: p[2] in HUE):
        ax.scatter(x, 100 * yv, s=9, color=HUE.get(v, "#b5b3ae"), edgecolors="none", zorder=3 if v in HUE else 2)
    ax.set_title(f"{title}, ρ = {rho[key][0]:.2f}".replace("-", "\u2212"), fontsize=6.8, color=GRAY, pad=3)
    ax.tick_params(labelsize=6, length=2)
    ax.set_xlabel("capability index (ECI)", fontsize=6.4)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
axs[0].set_ylabel("arcs folded (%)", fontsize=6.4)
axs[0].set_ylim(-4, 104)
handles = [plt.Line2D([], [], marker="o", ls="", ms=3, color=c, label=VEND[v]) for v, c in HUE.items()]
handles.append(plt.Line2D([], [], marker="o", ls="", ms=3, color="#b5b3ae", label="other"))
fig.legend(handles=handles, loc="lower center", ncol=5, fontsize=5.6, frameon=False,
           handletextpad=0.1, columnspacing=0.6, bbox_to_anchor=(0.5, -0.02))
fig.tight_layout(pad=0.2, rect=(0, 0.1, 1, 1))
fig.savefig(HERE / "figs" / "fold_capability.pdf")
plt.close(fig)
print(f"scatter: first set rho {rho['folds'][0]:.3f} (n={rho['folds'][1]}), "
      f"second set rho {rho['folds2'][0]:.3f} (n={rho['folds2'][1]}) -> figs/fold_capability.pdf")

# ---- numbers this figure is responsible for ----------------------------------------------
rows1 = [r for r in rows if r["folds"] is not None]          # the pinned first-set panel
per_vendor = {}
for v, rs in by.items():
    rs1 = [x for x in rs if x["folds"] is not None]
    if rs1:
        per_vendor[VEND.get(v, "other")] = {"models": len(rs1), "fold_rate": round(_mean_fold(rs1), 4)}
stats = {
    "panel_models": len(rows1),
    "coders": sorted(coders),
    "arcs": sum(r["n"] for r in rows1),
    "tied_arcs": n_tied,   # 3-3 splits: drawn as their own cell, out of the fold-rate denominator
    "fold_rate_panel": round(sum(r["folds"] for r in rows1) / len(rows1), 4),
    "per_vendor": per_vendor,
    "per_model_fold_rate": {r["model"]: round(r["folds"], 4) for r in sorted(rows1, key=lambda x: -x["folds"])},
    "second_set": {"models": n_rows2, "tied_arcs": n_tied2,
                   "per_model_fold_rate": {r["model"]: round(r["folds2"], 4) for r in rows if "folds2" in r}},
}
(HERE / "gen" / "stats.json").write_text(json.dumps(stats, indent=2) + "\n")
print(f"{len(rows1)} models, {stats['arcs']} arcs, {len(coders)} coders, {n_tied} tied arcs on the first set; "
      f"{n_rows2} models on the second -> figs/hold_fold.pdf, gen/stats.json")

# ---- the paper's two tables, from the dated analysis files -------------------------------
# The statistics live in harness/manner_matrix.py and harness/house_profiles.py; this reads
# their newest dated output rather than reimplementing them, so there is one implementation of
# the permutation test and the paper cannot drift from it. Each table shows the first set and,
# beside it, the second (preregistered) set from the same scripts under tag v2w2.
RESULTS = STUDY / "data" / "coding" / "results"
matrix_file = sorted(RESULTS.glob("MANNER-MATRIX-v2-*.md"))[-1]
profiles_file = sorted(RESULTS.glob("HOUSE-PROFILES-v2-*.md"))[-1]
matrix2_file = sorted(RESULTS.glob("MANNER-MATRIX-v2w2-*.md"))[-1]
profiles2_file = sorted(RESULTS.glob("HOUSE-PROFILES-v2w2-*.md"))[-1]

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
def pstr(pv):
    return "$<$0.001" if pv < 0.0005 else f"{pv:.3f}"

def read_matrix(path):
    out = {}
    blk = path.read_text().split("## 3.")[1].split("## 4.")[0]
    for line in blk.splitlines():
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) != 9 or c[0] == "code" or c[0].startswith("---") or "trajectory" in c[0]:
            continue
        out[FULL[c[0]]] = {"code": FULL[c[0]], "eta2": float(c[1]), "p": float(c[2]), "by": c[3],
                           "rho": float(c[4]), "top": c[8]}
    return out
m1, m2 = read_matrix(matrix_file), read_matrix(matrix2_file)
vendor_rows = sorted(m1.values(), key=lambda r: -r["eta2"])

cleared = [r for r in vendor_rows if r["by"] == "yes"]
with open(HERE / "gen" / "vendor_table.tex", "w") as f:       # first set, then the second beside it
    for r in cleared:
        r2 = m2[r["code"]]
        mark = "" if r2["by"] == "yes" else "$^{\\dagger}$"    # dagger: not surviving correction on the second set
        f.write(f"{r['code']} & {r['eta2']:.2f} & {pstr(r['p'])} & {r2['eta2']:.2f}{mark} & {pstr(r2['p'])} & {tex_num(r['rho'])} & {r['top']} \\\\\n")
    f.write("\\bottomrule%\n")

def read_profiles(path):
    prof, fold, nmod = collections.defaultdict(dict), {}, {}
    cur = None
    for line in path.read_text().splitlines():
        if line.startswith("## ") and "(" in line and "models:" in line:
            cur = line[3:].split()[0]; nmod[cur] = int(line.split("(")[1].split()[0])
        elif cur and line.startswith("Fold rate:"):
            fold[cur] = (float(line.split()[2]), float(line.split("panel ")[1].split(")")[0]))
        elif cur and line.startswith("| ") and line.count("|") == 5:
            c = [x.strip() for x in line.strip().strip("|").split("|")]
            if c[0] in ("code",) or c[0].startswith("---"):
                continue
            try: prof[cur][c[0]] = (float(c[1]), float(c[2]))
            except ValueError: pass
    return prof, fold, nmod
prof, fold, _ = read_profiles(profiles_file)
prof2, fold2, nmod2 = read_profiles(profiles2_file)

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
]
def _r(x):
    return f"{x:.2f}" if x is not None else "--"
with open(HERE / "gen" / "profiles_table.tex", "w") as f:    # each rate as first set / second set
    for label, key, codes_named in SIGNATURE:
        n1 = sum(1 for r in rows1 if vendor.get(r["model"]) == key); n2 = nmod2.get(key, 0)
        # no correction marks here: the profile describes what the vendor's models did, and
        # which codes sort by vendor firmly enough to count is Table 1's job.
        parts = []
        for disp, code in codes_named:
            a, b = prof[key].get(code), prof2[key].get(code)
            if a is None and b is None: continue
            parts.append(f"{disp} {_r(a and a[0])}/{_r(b and b[0])} ({_r(a and a[1])}/{_r(b and b[1])})")
        f.write(f"{label} ({n1}/{n2}) & {fold[key][0]:.2f}/{fold2[key][0]:.2f} & {', '.join(parts)} \\\\\n")
    f.write("\\bottomrule%\n")

with open(HERE / "gen" / "allcodes_table.tex", "w") as f:      # the appendix table, all 17, first set
    for r in vendor_rows:
        f.write(f"{r['code']} & {r['eta2']:.2f} & {pstr(r['p'])} & {r['by']} & {tex_num(r['rho'])} & {r['top']} \\\\\n")
    f.write("\\bottomrule%\n")

stats["vendor_effects"] = {r["code"]: {"eta2": r["eta2"], "p": r["p"], "by": r["by"], "rho": r["rho"]} for r in vendor_rows}
stats["vendor_effects_second_set"] = {r["code"]: {"eta2": r["eta2"], "p": r["p"], "by": r["by"], "rho": r["rho"]} for r in m2.values()}
stats["sources"] = {"matrix": matrix_file.name, "profiles": profiles_file.name,
                    "matrix2": matrix2_file.name, "profiles2": profiles2_file.name}
(HERE / "gen" / "stats.json").write_text(json.dumps(stats, indent=2) + "\n")
print(f"tables from {matrix_file.name}, {matrix2_file.name}, {profiles_file.name}, {profiles2_file.name}: "
      f"{len(cleared)} cleared codes, {len(SIGNATURE)} vendor rows")
