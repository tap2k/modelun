"""make_assets.py — regenerate the paper's figures from the study's probe data.

The "right?" reflex: per-model TAGeff (P(affirm | "…right?") − P(affirm | neutral ask),
counterbalanced, bootstrap CI), the per-family generational walks, and the baseline-conditional
view. Run from studies/suggestibility/paper/:

    ../../../.venv/bin/python make_assets.py

Outputs: figs/right_scorecard.pdf, figs/right_walks.pdf, figs/right_baseline.pdf.
Same figures as the blog/explorer, rendered for LaTeX (vector PDF, embeddable fonts).
"""
import sys
import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
sys.path.insert(0, str(STUDY))
from analyze import classify            # noqa: E402
from probe_righteffect import ITEMS     # noqa: E402
from lineage import FAM                 # noqa: E402  model -> (family, generation index)

FIGS = HERE / "figs"
FIGS.mkdir(exist_ok=True)

# --- validated dataviz palette (blue = resist / red = sycophantic) ---
BLUE, RED, GRAY = "#2a78d6", "#e34948", "#b8b7b2"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e7e6e2"
CAT = {"GPT": "#2a78d6", "Claude": "#eb6834", "Gemini": "#1baf7a", "Grok": "#4a3aa7",
       "Qwen": "#e87ba4", "DeepSeek": "#eda100", "GLM": "#008300"}
plt.rcParams.update({
    "font.family": "sans-serif", "font.size": 8.5,
    "axes.edgecolor": GRID, "axes.linewidth": 0.6,
    "xtick.color": INK2, "ytick.color": INK2,
    "text.color": INK, "axes.labelcolor": INK2,
    "pdf.fonttype": 42,
})

GENLABEL = {
    "gpt-3.5-turbo": "3.5", "gpt-4-turbo": "4t", "gpt-4o": "4o", "gpt-4o-mini-2024-07-18": "4o-m",
    "gpt-4.1": "4.1", "gpt-5": "5", "gpt-5.4": "5.4", "gpt-5.5": "5.5", "gpt-5.6-luna": "5.6",
    "gpt-5.6-sol": "5.6", "gpt-5.6-terra": "5.6",
    "claude-3-haiku": "3-h", "claude-haiku-4.5": "h4.5", "claude-sonnet-4.6": "s4.6",
    "claude-opus-4.8": "o4.8", "claude-sonnet-5": "s5", "claude-fable-5": "f5",
    "gemini-2.5-flash": "2.5", "gemini-3.1-pro-preview": "3.1", "gemini-3.5-flash": "3.5",
    "grok-4.20": "4.20", "grok-4.3": "4.3", "grok-4.5": "4.5",
    "qwen-2.5-72b-instruct": "2.5", "qwen3-235b-a22b-2507": "3",
    "deepseek-chat-v3-0324": "v3", "deepseek-r1": "r1", "deepseek-v3.2": "v3.2", "deepseek-v4-flash": "v4",
    "glm-4.7": "4.7", "glm-5.2": "5.2",
}


def arate(reps):
    labs = [classify(r) for r in reps if r is not None]
    return (sum(l == "affirm" for l in labs) / len(labs)) if labs else None


def compute():
    tx = {json.loads(p.read_text())["model"]: json.loads(p.read_text())["scenes"]
          for p in (STUDY / "transcripts").glob("*.json")}
    rng = np.random.default_rng(7)
    out = {}
    for p in sorted((STUDY / "probes" / "righteffect").glob("*.json")):
        d = json.loads(p.read_text())
        m = d["model"]
        if m == "run" or m not in tx:
            continue
        per = []
        for sid, _, _, _ in ITEMS:
            ask = [r[0].get("reply") for r in tx[m].get(sid + "__askx", {}).get("runs", []) +
                   tx[m].get(sid + "__asky", {}).get("runs", []) if r]
            tag = d["tag"].get(sid, {}).get("x", []) + d["tag"].get(sid, {}).get("y", [])
            a, t = arate(ask), arate(tag)
            if a is not None and t is not None:
                per.append((t - a, a))
        if not per:
            continue
        effs = [e[0] for e in per]
        boots = [float(np.mean(rng.choice(effs, len(effs)))) for _ in range(2000)]
        out[m] = {"tageff": float(np.mean(effs)), "lo": float(np.percentile(boots, 5)),
                  "hi": float(np.percentile(boots, 95)), "ask": float(np.mean([e[1] for e in per])),
                  "channel": "openrouter"}
    for p in sorted((STUDY / "probes" / "righteffect_glm").glob("*.json")):
        d = json.loads(p.read_text())
        out[d["model"]] = {"tageff": d["tageff"], "lo": d["ci"][0], "hi": d["ci"][1],
                           "ask": None, "channel": "deepinfra"}
    return out


def fig_scorecard(data):
    rows = sorted([(m, v) for m, v in data.items() if v["channel"] == "openrouter"],
                  key=lambda r: r[1]["tageff"])
    n = len(rows)
    fig, ax = plt.subplots(figsize=(8.8, 11))
    GUT = -0.50
    for i, (m, v) in enumerate(rows):
        e = v["tageff"]
        floor = v["ask"] is not None and v["ask"] < 0.10
        c = BLUE if e < 0 else RED
        ax.barh(i, e, height=0.62, color=(GRAY if floor else c),
                edgecolor=(c if floor else "none"), linewidth=1.2, zorder=3)
        ax.plot([v["lo"], v["hi"]], [i, i], color=INK2, lw=1.1, alpha=0.5, zorder=4)
        ax.text(GUT, i, m + (" °" if floor else ""), va="center", ha="right", fontsize=7.4, color=INK2)
    ax.axvline(0, color=INK, lw=1.1, zorder=5)
    ax.set_ylim(-0.8, n - 0.2)
    ax.set_xlim(-0.82, 0.46)
    ax.set_yticks([])
    ax.set_xticks([-0.4, -0.2, 0, 0.2, 0.4])
    ax.set_xticklabels(["−40%", "−20%", "0", "+20%", "+40%"], fontsize=8, color=INK2)
    for s in ("top", "left", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_bounds(-0.4, 0.4)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(length=0)
    ax.set_xlabel("TAGeff  =  P(affirm | “…right?”)  −  P(affirm | neutral ask)\n"
                  "° floor-limited: baseline affirm < 10%, so the tag has little to move (uninformative)",
                  fontsize=8.5, color=INK2, linespacing=1.8)
    ax.text(-0.2, n - 0.2, "◀ RESISTS the bid", ha="center", fontsize=10, color=BLUE, fontweight="bold")
    ax.text(0.2, n - 0.2, "VALIDATES harder ▶", ha="center", fontsize=10, color=RED, fontweight="bold")
    ax.set_title("The “right?” reflex across 43 models", fontsize=14, color=INK, pad=18, loc="left", fontweight="bold")
    fig.savefig(FIGS / "right_scorecard.pdf", bbox_inches="tight")
    plt.close(fig)


def fig_walks(data):
    fams = ["GPT", "Claude", "Gemini", "Grok", "Qwen", "DeepSeek", "GLM"]
    fig, axes = plt.subplots(2, 4, figsize=(12, 5.6), sharey=True)
    axes = axes.ravel()
    ymax = 0.36
    for ax, fam in zip(axes, fams):
        pts = sorted([(FAM[m][1], data[m]["tageff"], GENLABEL[m]) for m in data if m in FAM and FAM[m][0] == fam],
                     key=lambda p: p[0])
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        ax.axhspan(0, ymax, color=RED, alpha=0.05)
        ax.axhspan(-ymax, 0, color=BLUE, alpha=0.05)
        ax.axhline(0, color=INK, lw=0.9)
        ax.plot(xs, ys, "-o", color=CAT[fam], lw=2, ms=6, zorder=5, markeredgecolor="white", markeredgewidth=1.2)
        for x, y, lbl in pts:
            ax.annotate(lbl, (x, y), textcoords="offset points", xytext=(0, 9 if y >= 0 else -14),
                        ha="center", fontsize=7, color=INK2)
        ax.set_title(fam + ("  †" if fam == "GLM" else ""), fontsize=11, color=CAT[fam], fontweight="bold", loc="left")
        ax.set_xticks([])
        ax.set_xlim(min(xs) - 0.6, max(xs) + 0.6)
        for s in ("top", "right", "bottom"):
            ax.spines[s].set_visible(False)
        ax.spines["left"].set_color(GRID)
        ax.tick_params(length=0, labelsize=7)
    axes[0].set_ylim(-ymax, ymax)
    axes[0].set_yticks([-0.2, 0, 0.2])
    axes[0].set_yticklabels(["−20%", "0", "+20%"], fontsize=7.5)
    lg = axes[7]
    lg.axis("off")
    lg.text(0.0, 0.9, "older → newer  (left → right)", fontsize=8.5, color=INK2)
    lg.text(0.0, 0.66, "red band = validates harder", fontsize=8.5, color=RED)
    lg.text(0.0, 0.50, "blue band = resists", fontsize=8.5, color=BLUE)
    lg.text(0.0, 0.22, "† GLM via DeepInfra (thinking-off);\n   within-GLM trend valid, channel differs",
            fontsize=7, color=INK2)
    fig.suptitle("Response to “…right?” flips from sycophantic to resistant across generations",
                 fontsize=13, color=INK, fontweight="bold", x=0.02, ha="left", y=0.99)
    fig.text(0.02, 0.93, "US labs first and hardest; Qwen & GLM catching up; DeepSeek the lone laggard.",
             fontsize=9.5, color=INK2, ha="left")
    fig.tight_layout(rect=[0, 0, 1, 0.9])
    fig.savefig(FIGS / "right_walks.pdf", bbox_inches="tight")
    plt.close(fig)


def fig_baseline(data):
    rows = [(m, v) for m, v in data.items() if v["channel"] == "openrouter" and v["ask"] is not None]
    fig, ax = plt.subplots(figsize=(7.6, 5.4))
    ax.axhline(0, color=INK, lw=1)
    ax.axvspan(0, 0.10, color=GRAY, alpha=0.25, zorder=0)
    for m, v in rows:
        ax.scatter(v["ask"], v["tageff"], s=34, color=(BLUE if v["tageff"] < 0 else RED),
                   edgecolor="white", linewidth=0.8, zorder=3)
    for m, v in rows:
        if m in ("mythomax-l2-13b", "deepseek-v3.2", "claude-fable-5", "gpt-5.6-luna",
                 "gpt-3.5-turbo", "mixtral-8x22b-instruct"):
            ax.annotate(m, (v["ask"], v["tageff"]), textcoords="offset points", xytext=(5, 4), fontsize=6.8, color=INK2)
    ax.text(0.05, ax.get_ylim()[1] * 0.86, "floor-limited\n(uninformative)", fontsize=7.5, color=INK2, ha="center")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("bottom", "left"):
        ax.spines[s].set_color(GRID)
    ax.tick_params(length=0, labelsize=8)
    ax.set_xlabel("baseline affirm rate  (P affirm | neutral ask)", fontsize=9.5, color=INK2)
    ax.set_ylabel("TAGeff", fontsize=9.5, color=INK2)
    ax.set_xlim(0, 1)
    ax.set_title("The signal lives where models actually take a position", fontsize=12.5, color=INK, fontweight="bold", loc="left", pad=12)
    fig.savefig(FIGS / "right_baseline.pdf", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    data = compute()
    print(f"computed {len(data)} models")
    fig_scorecard(data)
    fig_walks(data)
    fig_baseline(data)
    print(f"wrote figs/right_scorecard.pdf, right_walks.pdf, right_baseline.pdf to {FIGS}")
