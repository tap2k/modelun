"""
Plot the marker grid from data/benchmark/markers.json.

Rows = models (by vendor family, oldest->newest). Columns = the six markers, grouped
by dimension (TONGUE | HANDS | HEART). Binary cells are colored by verdict
(hold / split / departure / contested); graded cells by category (run-0, else run-1),
drawn pale when the two runs disagree.

    python studies/conduct/views/plot.py                # -> reads/markers_grid.png
"""

import json
import argparse
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parent.parent

FAMILIES = [
    ("OpenAI", ["gpt-3.5-turbo-instruct", "gpt-3.5-turbo", "gpt-4-turbo", "gpt-4o",
                "gpt-4o-mini-2024-07-18", "gpt-4.1", "gpt-5", "gpt-5.4-mini", "gpt-5.4"]),
    ("Anthropic", ["claude-3-haiku", "claude-3.5-haiku", "claude-sonnet-4", "claude-opus-4",
                   "claude-opus-4.5", "claude-haiku-4.5", "claude-sonnet-4.6", "claude-opus-4.8"]),
    ("Google", ["gemma-2-27b-it", "gemini-2.5-flash", "gemini-2.5-pro", "gemma-3-27b-it",
                "gemini-3-flash-preview", "gemini-3.1-pro-preview", "gemini-3.5-flash"]),
    ("Meta-Llama", ["llama-3-70b-instruct", "llama-3.3-70b-instruct", "llama-4-scout", "llama-4-maverick"]),
    ("Qwen", ["qwen3-235b-a22b-2507", "qwen3-235b-a22b-thinking-2507", "qwen3.7-plus"]),
    ("Other", ["mythomax-l2-13b", "hermes-3-llama-3.1-70b", "deepseek-r1", "mixtral-8x22b-instruct",
               "kimi-k2", "grok-4.3", "command-r-plus-08-2024"]),
]
RANK = {lab: (fi, i) for fi, (_, labs) in enumerate(FAMILIES) for i, lab in enumerate(labs)}
FAM = {lab: fam for fam, labs in FAMILIES for lab in labs}

# columns: TONGUE (3) | HANDS (2) | HEART (1)
COLS = ["caved_on_fact", "cheerled_bad_plan", "self_label_response",
        "forged_document", "leap_help", "snapped_to_task"]
SHORT = {"caved_on_fact": "Cave\nfacts", "cheerled_bad_plan": "Cheerlead\ntrader",
         "self_label_response": "Self-story\n(graded)", "forged_document": "Forge\nnote",
         "leap_help": "Leap\n(graded)", "snapped_to_task": "Snap\npivot"}
DIM_BREAKS = [3, 5]  # vertical separators after these column indices

GREEN, BLUE, AMBER, RED, GREY = "#2e7d32", "#1565c0", "#f9a825", "#c62828", "#bdbdbd"


def lighten(hexc, f=0.55):
    """Blend a hex color toward white by fraction f (pale = the two runs differed)."""
    r, g, b = (int(hexc[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % tuple(int(c + (255 - c) * f) for c in (r, g, b))


# one grammar, two channels: hue = severity (green best -> red worst), pale = runs differed.
# binary split is "departed in one of two runs" -> pale red, NOT its own hue.
VERDICT = {"stable-hold": GREEN, "split": lighten(RED), "stable-departure": RED, "contested": GREY}
# graded category -> (severity color, 1-letter house lean for the static PNG)
CAT = {
    "names_comfortable_story": (GREEN, "T"), "equips_delivery": (BLUE, "C"),
    "soft_out": (AMBER, "A"), "harsh_overcorrect": (RED, "x"),
    "redirects_first": (GREEN, "T"), "helps_with_grounding": (BLUE, "C"),
    "helps_blind": (AMBER, "A"), "refuses": (RED, "w"),
}


def cell(model_markers, mid):
    """-> (facecolor, glyph). Binary by verdict; graded by category (run-0, falling back
    to run-1). Unstable graded cells (runs differ / one unlabeled) are drawn pale; grey
    only when BOTH runs are unlabeled (a real data gap)."""
    rec = model_markers.get(mid)
    if not rec:
        return "#ffffff", "?"
    if rec["type"] == "binary":
        v = rec["verdict"]
        return VERDICT.get(v, "#ffffff"), {"stable-departure": "●", "split": "◐", "stable-hold": "", "contested": "·"}[v]
    cat = rec["runs"][0] or rec["runs"][1]   # run-0 lean; fall back to run-1 if it didn't bin
    if cat is None:
        return GREY, "·"
    color, letter = CAT.get(cat, (GREY, "?"))
    if not rec["verdict"].startswith("stable:"):  # runs differ or one unlabeled -> pale
        color = lighten(color)
    return color, letter


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--markers", default=str(ROOT / "data" / "benchmark" / "markers.json"))
    ap.add_argument("--out", default=str(ROOT / "reads" / "markers_grid.png"))
    args = ap.parse_args()

    blob = json.loads(Path(args.markers).read_text())
    models = sorted(blob["models"], key=lambda m: RANK.get(m, (99, 99)))
    n, c = len(models), len(COLS)

    fig, ax = plt.subplots(figsize=(0.95 * c + 3, 0.34 * n + 2))
    for yi, m in enumerate(models):
        mk = blob["models"][m]
        for xi, mid in enumerate(COLS):
            color, glyph = cell(mk, mid)
            ax.add_patch(plt.Rectangle((xi - 0.5, yi - 0.5), 1, 1, facecolor=color, edgecolor="white"))
            if glyph:
                r, g, b = (int(color[i:i + 2], 16) for i in (1, 3, 5))
                dark = r * .299 + g * .587 + b * .114 > 150  # pale cell -> dark glyph
                ax.text(xi, yi, glyph, ha="center", va="center", color="#333" if dark else "white", fontsize=8)
    ax.set_xlim(-0.5, c - 0.5); ax.set_ylim(n - 0.5, -0.5)
    ax.set_xticks(range(c)); ax.set_xticklabels([SHORT[m] for m in COLS], fontsize=8)
    ax.set_yticks(range(n)); ax.set_yticklabels(models, fontsize=7)
    for b in DIM_BREAKS:
        ax.axvline(b - 0.5, color="black", lw=1.5)
    prev = None
    for yi, m in enumerate(models):
        if FAM.get(m) != prev:
            if yi:
                ax.axhline(yi - 0.5, color="black", lw=0.8)
            prev = FAM.get(m)
    ax.set_title("Marker grid — TONGUE | HANDS | HEART\n"
                 "hue = severity (green held → red departed) · pale = the two runs differed · grey = contested\n"
                 "binary: ●departed ◐split   graded: T/C/A/x/w = house lean", fontsize=9)
    legend = [Patch(facecolor=GREEN, label="held / Therapist"),
              Patch(facecolor=BLUE, label="Coach"),
              Patch(facecolor=AMBER, label="Apologist"),
              Patch(facecolor=RED, label="departed / fail"),
              Patch(facecolor=VERDICT["split"], label="split (runs differ)"),
              Patch(facecolor=GREY, label="contested")]
    ax.legend(handles=legend, bbox_to_anchor=(0.5, -0.05), loc="upper center", ncol=6, fontsize=7, frameon=False)
    plt.tight_layout()
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(args.out, dpi=150, bbox_inches="tight")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
