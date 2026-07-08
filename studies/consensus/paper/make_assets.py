"""make_assets.py — regenerate every figure, table, and quoted number in the paper
from analysis.json + transcripts. Run from studies/consensus/paper/:

    ../../../.venv/bin/python make_assets.py

Outputs: figs/*.pdf, gen/scorecard_table.tex, gen/stats.json. main.tex quotes only
numbers that appear in gen/stats.json, so the paper is recomputable end-to-end.
"""

import sys
import json
from pathlib import Path
from collections import Counter

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
sys.path.insert(0, str(STUDY))
from analyze import load  # transcripts -> normalized answers (junk-guarded)

BLUE, AMBER, GRAY, GRID = "#2a78d6", "#b07500", "#52514e", "#d9d8d4"
plt.rcParams.update({
    "font.family": "sans-serif", "font.size": 8.5,
    "axes.edgecolor": GRAY, "axes.linewidth": 0.6,
    "xtick.color": GRAY, "ytick.color": GRAY,
    "text.color": "#0b0b0b", "axes.labelcolor": "#0b0b0b",
    "pdf.fonttype": 42,
})

(HERE / "figs").mkdir(exist_ok=True)
(HERE / "gen").mkdir(exist_ok=True)

analysis = json.loads((STUDY / "analysis.json").read_text())
pm, pc = analysis["per_model"], analysis["per_category"]

ans = load(STUDY)
models = sorted(m for m in ans if ans[m])
cats = sorted({c for m in models for c in ans[m]})
# plural merge, same as analyze.py
for c in cats:
    pool = Counter(a for m in models for a in ans[m].get(c, []))
    stems = {w: w[:-1] for w in pool if w.endswith("s") and w[:-1] in pool}
    for m in models:
        if c in ans[m]:
            ans[m][c] = [stems.get(a, a) for a in ans[m][c]]

stats = {"n_models": analysis["n_models"], "n_categories": analysis["n_categories"]}
stats["n_valid_answers"] = sum(v["n_answers"] for v in pm.values())
stats["n_cells_attempted"] = analysis["n_models"] * analysis["n_categories"] * 4

# ---------------------------------------------------------------- display names
def disp(label):
    return {
        "gpt-4o-mini-2024-07-18": "gpt-4o-mini",
        "ernie-4.5-vl-424b-a47b": "ernie-4.5-vl",
        "qwen3-235b-a22b-2507": "qwen3-235b",
        "qwen-2.5-72b-instruct": "qwen-2.5-72b",
        "llama-3.3-70b-instruct": "llama-3.3-70b",
        "hunyuan-a13b-instruct": "hunyuan-a13b",
        "mixtral-8x22b-instruct": "mixtral-8x22b",
        "gemini-3.1-pro-preview": "gemini-3.1-pro",
        "gemma-3-27b-it": "gemma-3-27b",
        "deepseek-chat-v3-0324": "deepseek-v3-0324",
    }.get(label, label)

order = sorted(pm, key=lambda m: -pm[m]["surprisal"])

# ---------------------------------------------------------------- fig 1: scorecard
fig, ax = plt.subplots(figsize=(5.6, 6.4))
ys = np.arange(len(order))[::-1]
for y, m in zip(ys, order):
    v = pm[m]
    lo, hi = v.get("ci90", [v["surprisal"]] * 2)
    ax.plot([lo, hi], [y, y], color=GRID, lw=1.4, zorder=1)
    ax.plot(v["surprisal"], y, "o", ms=4, color=BLUE, zorder=2)
ax.set_yticks(ys)
ax.set_yticklabels([disp(m) for m in order], fontsize=7)
ax.set_xlabel("answer-choice surprisal (bits), leave-one-out, 90% CI")
ax.spines[["top", "right", "left"]].set_visible(False)
ax.tick_params(axis="y", length=0)
ax.grid(axis="x", color=GRID, lw=0.5, alpha=0.6)
ax.set_axisbelow(True)
ax.set_ylim(-0.8, len(order) - 0.2)
fig.tight_layout()
fig.savefig(HERE / "figs" / "scorecard.pdf")
plt.close(fig)

# ---------------------------------------------------------------- fig 2: substrate
cat_rows = sorted(pc.items(), key=lambda kv: -kv[1]["modal_share"])
fig, ax = plt.subplots(figsize=(5.6, 5.4))
ys = np.arange(len(cat_rows))[::-1]
for y, (c, v) in zip(ys, cat_rows):
    hi = v["modal_share"] >= 0.8
    ax.barh(y, v["modal_share"], height=0.62, color=BLUE if hi else GRID,
            edgecolor="none", zorder=2)
    ax.text(v["modal_share"] + 0.012, y, f"{v['modal']}  {v['modal_share']:.0%}",
            va="center", fontsize=7, color="#0b0b0b")
ax.axvline(0.8, color=AMBER, lw=0.9, ls=(0, (4, 3)), zorder=1)
ax.text(0.8, len(cat_rows) - 0.1, "80%", color=AMBER, fontsize=7, ha="center")
ax.set_yticks(ys)
ax.set_yticklabels([c.replace("_", " ") for c, _ in cat_rows], fontsize=7)
ax.set_xlim(0, 1.12)
ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"])
ax.set_xlabel("share of the whole field's answers taken by the modal answer")
ax.spines[["top", "right", "left"]].set_visible(False)
ax.tick_params(axis="y", length=0)
fig.tight_layout()
fig.savefig(HERE / "figs" / "substrate.pdf")
plt.close(fig)

stats["categories_ge80"] = [
    {"cat": c, "modal": v["modal"], "share": round(v["modal_share"], 3)}
    for c, v in cat_rows if v["modal_share"] >= 0.8]
stats["categories_le40"] = [
    {"cat": c, "modal": v["modal"], "share": round(v["modal_share"], 3)}
    for c, v in cat_rows if v["modal_share"] <= 0.4]

# ---------------------------------------------------------------- fig 3: walks
WALKS = [
    ("Claude", ["claude-3-haiku", "claude-haiku-4.5", "claude-sonnet-4.6",
                "claude-opus-4.8", "claude-sonnet-5"],
     ["3-haiku", "haiku-4.5", "sonnet-4.6", "opus-4.8", "sonnet-5"]),
    ("GPT", ["gpt-3.5-turbo", "gpt-4-turbo", "gpt-4o", "gpt-4o-mini-2024-07-18",
             "gpt-4.1", "gpt-5", "gpt-5.4", "gpt-5.5"],
     ["3.5", "4-turbo", "4o", "4o-mini", "4.1", "5", "5.4", "5.5"]),
    ("Qwen", ["qwen-2.5-72b-instruct", "qwen3-235b-a22b-2507"], ["2.5-72b", "3-235b"]),
    ("Gemini", ["gemini-2.5-flash", "gemini-3.1-pro-preview", "gemini-3.5-flash"],
     ["2.5-flash", "3.1-pro", "3.5-flash"]),
    ("Llama", ["llama-3.3-70b-instruct", "llama-4-maverick"], ["3.3-70b", "4-maverick"]),
    ("DeepSeek", ["deepseek-chat-v3-0324", "deepseek-v3.2", "deepseek-v4-flash"],
     ["v3-0324", "v3.2", "v4-flash"]),
]
fig, axes = plt.subplots(2, 3, figsize=(5.6, 3.3), sharey=True)
for axi, (name, labels, ticks) in zip(axes.flat, WALKS):
    xs = np.arange(len(labels))
    vals = [pm[l]["surprisal"] for l in labels]
    axi.plot(xs, vals, "-o", color=BLUE, lw=1.4, ms=3.5)
    if name == "Claude":  # fable-5 plotted beside its mainline generation
        axi.plot([4], [pm["claude-fable-5"]["surprisal"]], "o", ms=4, color=AMBER)
        axi.annotate("fable-5", (4, pm["claude-fable-5"]["surprisal"]),
                     textcoords="offset points", xytext=(2, 5),
                     fontsize=6.5, color=AMBER, ha="right")
    axi.set_title(name, fontsize=8)
    axi.set_xticks(xs)
    axi.set_xticklabels(ticks, fontsize=6, rotation=45, ha="right")
    axi.set_ylim(0.9, 3.0)
    axi.spines[["top", "right"]].set_visible(False)
    axi.grid(axis="y", color=GRID, lw=0.5, alpha=0.6)
    axi.set_axisbelow(True)
for axi in axes[:, 0]:
    axi.set_ylabel("surprisal (bits)", fontsize=7)
fig.tight_layout()
fig.savefig(HERE / "figs" / "walks.pdf")
plt.close(fig)

# ------------------------------------------------- fig 4 + stats: runner-up consensus
runner = []
for c, v in cat_rows:
    pool = Counter(a for m in models for a in ans[m].get(c, []))
    if len(pool) < 3:
        continue
    (modal, n1), (second, n2) = pool.most_common(2)
    nonmodal = sum(pool.values()) - n1
    runner.append({"cat": c, "modal": modal, "modal_share": n1 / sum(pool.values()),
                   "runner_up": second, "runner_share_of_nonmodal": n2 / nonmodal,
                   "n_nonmodal": nonmodal})
runner_hi = [r for r in runner if r["modal_share"] >= 0.75]
runner_hi.sort(key=lambda r: -r["runner_share_of_nonmodal"])
stats["runner_up"] = runner_hi

fig, ax = plt.subplots(figsize=(5.6, 3.4))
ys = np.arange(len(runner_hi))[::-1]
for y, r in zip(ys, runner_hi):
    ax.barh(y, r["runner_share_of_nonmodal"], height=0.62, color=BLUE, zorder=2)
    ax.text(r["runner_share_of_nonmodal"] + 0.012, y,
            f"{r['runner_up']}  {r['runner_share_of_nonmodal']:.0%}",
            va="center", fontsize=7)
ax.set_yticks(ys)
ax.set_yticklabels([f"{r['cat'].replace('_',' ')}  (modal: {r['modal']})"
                    for r in runner_hi], fontsize=7)
ax.set_xlim(0, 1.12)
ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"])
ax.set_xlabel("share of the field's non-modal answers taken by the runner-up")
ax.spines[["top", "right", "left"]].set_visible(False)
ax.tick_params(axis="y", length=0)
fig.tight_layout()
fig.savefig(HERE / "figs" / "runnerup.pdf")
plt.close(fig)

# ---------------------------------------------------- human vs model concentration
hn_path = STUDY / "probes" / "humannorms.json"
if hn_path.exists():
    hn = json.loads(hn_path.read_text())
    hrows = hn["per_category"]  # sorted by model share desc
    fig, ax = plt.subplots(figsize=(5.6, 5.2))
    ys = np.arange(len(hrows))[::-1]
    for y, r in zip(ys, hrows):
        ax.plot([r["human_modal_first"], r["model_modal_share"]], [y, y],
                color=GRID, lw=1.2, zorder=1)
        ax.plot(r["human_modal_first"], y, "o", ms=5, color=AMBER, zorder=3)
        ax.plot(r["model_modal_share"], y, "o", ms=5, color=BLUE, zorder=3)
    ax.set_yticks(ys)
    ax.set_yticklabels([r["category"] for r in hrows], fontsize=7.5)
    ax.set_xlim(0, 1.0)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"])
    ax.set_xlabel("share of the modal answer  (human first response vs model field)")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color=GRID, lw=0.5, alpha=0.6)
    ax.set_axisbelow(True)
    ax.plot([], [], "o", color=AMBER, label="human (VO 2004, first response)")
    ax.plot([], [], "o", color=BLUE, label="model field")
    ax.legend(loc="lower right", fontsize=7.5, frameon=False)
    fig.tight_layout()
    fig.savefig(HERE / "figs" / "humannorms.pdf")
    plt.close(fig)

# ---------------------------------------------------------------- scorecard table
rows = []
for i, m in enumerate(order, 1):
    v = pm[m]
    ci = v.get("ci90", [float("nan")] * 2)
    rows.append(
        f"{i} & \\texttt{{{disp(m)}}} & {v['surprisal']:.2f} & "
        f"[{ci[0]:.2f}, {ci[1]:.2f}] & {v['modal_avoid']:.0%} & {v['novel_rate']:.0%} & "
        f"{v['self_distinct']:.0%} & {v['type']} \\\\".replace("%", "\\%"))
# \bottomrule lives in this file: a booktabs rule straight after \input hits a
# TeX alignment edge case (Misplaced \noalign) at the file boundary
(HERE / "gen" / "scorecard_table.tex").write_text("\n".join(rows) + "\n\\bottomrule\n")

# ---------------------------------------------------------------- quoted stats
def pool_of(c):
    return Counter(a for m in models for a in ans[m].get(c, []))

aw = pool_of("any_word")
stats["any_word"] = {"top": aw.most_common(8), "n": sum(aw.values()),
                     "n_distinct": len(aw),
                     "serendipity_share": aw["serendipity"] / sum(aw.values())}
fr = pool_of("fruit")
stats["fruit"] = {"top": fr.most_common(6), "orange": fr.get("orange", 0),
                  "n": sum(fr.values())}
vg = pool_of("vegetable")
stats["vegetable"] = {"top": vg.most_common(6), "tomato": vg.get("tomato", 0),
                      "n": sum(vg.values())}
co = pool_of("country")
stats["country"] = {"top": co.most_common(4), "n": sum(co.values()),
                    "us_variants": sum(n for a, n in co.items()
                                       if a in ("usa", "america", "us"))}

by_origin = {}
for m, v in pm.items():
    by_origin.setdefault(v["origin"], []).append(v["surprisal"])
stats["origin_means"] = {k: round(float(np.mean(v)), 2) for k, v in by_origin.items()}

stats["headline"] = {disp(m): {"surprisal": round(pm[m]["surprisal"], 2),
                               "rank": order.index(m) + 1,
                               "novel": round(pm[m]["novel_rate"], 3),
                               "avoid": round(pm[m]["modal_avoid"], 3),
                               "type": pm[m]["type"]}
                     for m in order}

# cohort x category-concentration cell: do the newest flagships snap to the mode
# hardest exactly where a strong mode exists? Cohorts defined explicitly: NEWEST =
# the 2026-era mainline flagships; OLDEST = each major family's oldest panel member.
NEWEST = ["claude-sonnet-5", "claude-opus-4.8", "gpt-5", "gpt-5.5", "qwen3-235b-a22b-2507"]
OLDEST = ["gpt-3.5-turbo", "claude-3-haiku", "gpt-4-turbo", "gemini-2.5-flash",
          "qwen-2.5-72b-instruct"]
peaked = {c for c, v in pc.items() if v["modal_share"] >= 0.8}
diffuse = {c for c, v in pc.items() if v["modal_share"] <= 0.4}

def cohort_surprisal(cohort, catset):
    ss = []
    for m in cohort:
        for c in catset:
            mine = ans[m].get(c, [])
            others = [a for o in models if o != m for a in ans[o].get(c, [])]
            if not mine or not others:
                continue
            pool = Counter(others)
            total, vocab = sum(pool.values()), len(set(others) | set(mine))
            ss.extend(-np.log2((pool.get(a, 0) + 1) / (total + vocab)) for a in mine)
    return round(float(np.mean(ss)), 2)

stats["cohorts"] = {
    "newest": NEWEST, "oldest": OLDEST,
    "newest_peaked": cohort_surprisal(NEWEST, peaked),
    "oldest_peaked": cohort_surprisal(OLDEST, peaked),
    "newest_diffuse": cohort_surprisal(NEWEST, diffuse),
    "oldest_diffuse": cohort_surprisal(OLDEST, diffuse),
}

med = float(np.median([v["surprisal"] for v in pm.values()]))
stats["median_surprisal"] = round(med, 2)
HEIRLOOMS = ["hermes-4-70b", "wizardlm-2-8x22b", "mixtral-8x22b-instruct",
             "mythomax-l2-13b", "gpt-4o-mini-2024-07-18", "gpt-4o"]
stats["heirlooms_above_median"] = {disp(m): pm[m]["surprisal"] > med for m in HEIRLOOMS}

# prompt list for Appendix B, from the frozen stimulus. The shared "Reply with one
# word only." suffix is factored into the appendix preamble, not repeated per item.
stim = json.loads((STUDY / "spec" / "stimulus.json").read_text())
SUFFIX = " Reply with one word only."
prompt_lines = [f"\\item {s['turns'][0].replace(SUFFIX, '')}" for s in stim["scenes"]]
(HERE / "gen" / "prompts.tex").write_text("\n".join(prompt_lines) + "\n")

(HERE / "gen" / "stats.json").write_text(json.dumps(stats, indent=1) + "\n")
print("assets written:", *[p.name for p in sorted((HERE / 'figs').glob('*.pdf'))],
      "gen/scorecard_table.tex gen/stats.json")
