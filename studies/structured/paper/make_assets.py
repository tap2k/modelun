"""make_assets.py — figures for the structured-output paper.

Regenerates figs/*.pdf from the committed probe data + census transcripts.

    ../../../.venv/bin/python make_assets.py

Outputs: figs/openvsjson.pdf — per-model answer-choice surprisal, open chat vs JSON,
as a connected dumbbell (the census humannorms style). Palette +
rcParams match studies/consensus/paper/make_assets.py.
"""
import sys
import json
import math
import re
from pathlib import Path
from collections import Counter

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
CONSENSUS = STUDY.parent / "consensus"
sys.path.insert(0, str(CONSENSUS))
from analyze import norm

BLUE, AMBER, GRAY, GRID = "#2a78d6", "#b07500", "#52514e", "#d9d8d4"
plt.rcParams.update({
    "font.family": "sans-serif", "font.size": 8.5,
    "axes.edgecolor": GRAY, "axes.linewidth": 0.6,
    "xtick.color": GRAY, "ytick.color": GRAY,
    "text.color": "#0b0b0b", "axes.labelcolor": "#0b0b0b",
    "pdf.fonttype": 42,
})
(HERE / "figs").mkdir(exist_ok=True)

reg = json.loads((STUDY / "probes/format_register.json").read_text())
JP = re.compile(r'"word"\s*:\s*"([^"]+)"')


def pj(r):
    if not r:
        return None
    m = JP.search(r)
    return norm(m.group(1)) if m else norm(r)


labels = sorted(reg["replies"]["json"].keys())
cats = sorted(reg["replies"]["json"][labels[0]].keys())

# echo guard (see ../views/build.py): drop the category noun / template placeholder.
def _head_noun(cat):
    p = (reg.get("formats", {}).get("json") or {}).get(cat)
    m = re.match(r"Name (?:a |an |any |some )?(.+?)\.", p) if p else None
    return m.group(1).split()[-1].lower() if m else None

ECHO = {c: {n for n in (_head_noun(c),) if n} | {"answer", "word"} for c in cats}
def _ok(w, c):
    return w is not None and w not in ECHO[c]


def ja(l, c):
    return [w for w in (pj(r) for r in reg["replies"]["json"][l][c]) if _ok(w, c)]


def pa(l, c):
    t = json.loads((CONSENSUS / "transcripts" / f"{l}.json").read_text())
    return [w for w in (norm(r[0].get("reply")) for r in t["scenes"][c]["runs"]) if _ok(w, c)]


def surprisal(get):
    per = {c: {l: get(l, c) for l in labels} for c in cats}
    out = {}
    for l in labels:
        sc = []
        for c in cats:
            mine = per[c][l]
            field = Counter(a for o in labels if o != l for a in per[c][o])
            vc = len(set(field) | set(mine))
            n = sum(field.values())
            sc += [-math.log2((field[a] + 1) / (n + vc)) for a in mine]
        out[l] = sum(sc) / len(sc) if sc else float("nan")
    return out


sp, sj = surprisal(pa), surprisal(ja)


def nice(l):
    return (l.replace("-2024-07-18", "").replace("-instruct", "")
             .replace("-a22b-2507", "").replace("-a13b", "").replace("-vl-424b-a47b", "")
             .replace("-8x22b", "").replace("-l2-13b", "").replace("-70b", ""))


order = sorted(labels, key=lambda x: sp[x])  # ascending -> highest MQ at top
ys = np.arange(len(order))
OPEN = "#b9bcc4"  # neutral gray for the open-chat baseline dot

fig, ax = plt.subplots(figsize=(5.8, 8.4))
for y, l in zip(ys, order):
    col = AMBER if sj[l] > sp[l] + 1e-9 else BLUE
    ax.plot([sp[l], sj[l]], [y, y], color=col, lw=1.7, alpha=0.85,
            solid_capstyle="round", zorder=2)
    ax.plot(sp[l], y, "o", ms=4.3, color=OPEN, markeredgecolor="white",
            markeredgewidth=0.5, zorder=3)
    ax.plot(sj[l], y, "o", ms=5.6, color=col, markeredgecolor="white",
            markeredgewidth=0.5, zorder=4)

ax.set_yticks(ys)
ax.set_yticklabels([nice(l) for l in order], fontsize=6.6)
ax.set_ylim(-0.9, len(order) - 0.1)
ax.set_xlim(0.6, 3.4)
ax.set_xlabel("answer-choice surprisal (bits)")
ax.spines[["top", "right", "left"]].set_visible(False)
ax.tick_params(axis="y", length=0)
ax.grid(axis="x", color=GRID, lw=0.5, alpha=0.6)
ax.set_axisbelow(True)

mp, mj = sum(sp.values()) / len(labels), sum(sj.values()) / len(labels)

from matplotlib.lines import Line2D
ax.legend(handles=[
    Line2D([], [], marker="o", color="none", markerfacecolor=OPEN, markersize=6, label="open chat"),
    Line2D([], [], marker="o", color="none", markerfacecolor=BLUE, markersize=6, label="JSON: more generic"),
    Line2D([], [], marker="o", color="none", markerfacecolor=AMBER, markersize=6, label="JSON: more distinctive"),
], loc="lower right", bbox_to_anchor=(1.0, 1.005), ncol=3, fontsize=7,
    frameon=False, columnspacing=1.1, handletextpad=0.3, borderaxespad=0)
fig.tight_layout()
fig.savefig(HERE / "figs" / "openvsjson.pdf", bbox_inches="tight")
print("wrote figs/openvsjson.pdf")
print(f"field mean {mp:.2f} -> {mj:.2f}; "
      f"{sum(1 for l in labels if sj[l] < sp[l])}/{len(labels)} compress (blue), "
      f"{sum(1 for l in labels if sj[l] > sp[l])} diverge (amber)")
