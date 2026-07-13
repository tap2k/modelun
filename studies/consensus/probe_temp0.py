"""probe_temp0.py — temperature-0 (greedy) re-run: how much deployed diversity survives being forced to the mode.

Re-runs the battery at temperature 0 (transcripts-temp0/) and compares to the frozen temp-1 study.
For each model it reports two deltas vs. the temp-1 answers:

  Δ self-distinctness  (temp1 -> temp0)
      drops toward the ~0.25 floor => provider honors the temperature parameter (near-deterministic)
      barely moves                 => provider serves a fixed config (parameter not honored)

  Δ surprisal          (temp0 answers scored against the frozen temp-1 field, leave-one-out)
      stays high  => the off-consensus answers are a stable default (survives greedy)
      collapses   => the temp-1 diversity was sampling spread (vanishes at greedy)

Holding the reference field fixed isolates the effect of the model's own answers changing.
    ../../.venv/bin/python probe_temp0.py
"""
import json, sys
from pathlib import Path
from collections import Counter
import numpy as np

HERE = Path(__file__).resolve().parent                      # studies/consensus
sys.path.insert(0, str(HERE))
from analyze import norm                                    # same normalization as the paper

T0_DIR = HERE / "transcripts-temp0"
if not T0_DIR.exists():
    sys.exit(f"no {T0_DIR} yet — run the temp-0 subset first.")

pm = json.loads((HERE / "analysis.json").read_text())["per_model"]   # frozen temp-1 metrics


def load_dir(d):
    """transcripts dir -> {label: {scene_id: [normalized answer per run]}} (mirrors analyze.load)."""
    out = {}
    for p in sorted(d.glob("*.json")):
        dd = json.loads(p.read_text())
        scenes = {}
        for sid, sc in dd["scenes"].items():
            toks = [t for t in (norm(run[0].get("reply")) for run in sc["runs"] if run) if t]
            if toks:
                scenes[sid] = toks
        out[dd["model"]] = scenes
    return out


field = load_dir(HERE / "transcripts")        # all 44 models, temp 1 (the frozen reference)
t0 = load_dir(T0_DIR)                          # subset, temp 0
cats = sorted({c for m in field for c in field[m]})

# plural-merge exactly as make_assets: build the stem map from the temp-1 pool, apply to both
stem = {}
for c in cats:
    pool = Counter(a for m in field for a in field[m].get(c, []))
    stem[c] = {w: w[:-1] for w in pool if w.endswith("s") and w[:-1] in pool}
merge = lambda A: {m: {c: [stem[c].get(a, a) for a in v] for c, v in sc.items()} for m, sc in A.items()}
field, t0 = merge(field), merge(t0)


def self_distinct(sc):
    v = [len(set(a)) / len(a) for a in sc.values() if a]
    return float(np.mean(v)) if v else float("nan")


def surprisal_vs_field(m, mine):
    """add-one smoothed leave-one-out surprisal of m's answers against the frozen temp-1 field."""
    ss = []
    for c in cats:
        a_mine = mine.get(c, [])
        others = [a for o in field if o != m for a in field[o].get(c, [])]
        if not a_mine or not others:
            continue
        pool = Counter(others)
        total, vocab = sum(pool.values()), len(set(others) | set(a_mine))
        ss += [-np.log2((pool.get(a, 0) + 1) / (total + vocab)) for a in a_mine]
    return float(np.mean(ss)) if ss else float("nan")


rows = []
for m in sorted(t0, key=lambda k: -pm.get(k, {}).get("surprisal", 0)):
    if m not in pm:
        print(f"  (skip {m}: not in frozen analysis.json)"); continue
    t1_su, t1_sd = pm[m]["surprisal"], pm[m]["self_distinct"]
    t0_su, t0_sd = surprisal_vs_field(m, t0[m]), self_distinct(t0[m])
    honored = "honored" if t0_sd <= t1_sd - 0.05 else "IGNORED"
    verdict = "held (stable default)" if t0_su >= t1_su - 0.30 else "collapsed (was scatter)"
    rows.append((m, t1_su, t0_su, t0_su - t1_su, t1_sd, t0_sd, t0_sd - t1_sd, honored, verdict))

hdr = f"{'model':22} {'surp t1':>7} {'t0':>6} {'Δ':>6}   {'sdist t1':>8} {'t0':>5} {'Δ':>6}   temp     surprisal"
print(hdr); print("-" * len(hdr))
for m, s1, s0, ds, d1, d0, dd, hon, vd in rows:
    print(f"{m:22} {s1:7.2f} {s0:6.2f} {ds:+6.2f}   {d1:8.2f} {d0:5.2f} {dd:+6.2f}   {hon:8} {vd}")

# ---- dumbbell plot: surprisal (left) and self-distinctness (right), temp1 -> temp0 ----
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
BLUE, AMBER = "#2a78d6", "#b07500"
labels = [r[0] for r in rows]; ys = np.arange(len(rows))[::-1]
fig, (axL, axR) = plt.subplots(1, 2, figsize=(10, 0.5 * len(rows) + 1.5), sharey=True)
for ax, i1, i0, title, floor in [(axL, 1, 2, "surprisal (bits)", None),
                                 (axR, 4, 5, "self-distinctness", 0.25)]:
    for y, r in zip(ys, rows):
        ax.plot([r[i1], r[i0]], [y, y], color="#cccccc", lw=1.4, zorder=1)
        ax.plot(r[i1], y, "o", ms=6, color=BLUE, zorder=2)
        ax.plot(r[i0], y, "o", ms=6, color=AMBER, zorder=3)
    if floor is not None:
        ax.axvline(floor, color="#999", ls=(0, (3, 3)), lw=0.8)
        ax.text(floor, len(rows) - 0.3, "temp-0 floor", fontsize=7, color="#666", ha="center")
    ax.set_title(title, fontsize=10); ax.set_axisbelow(True)
    ax.grid(axis="x", color="#eee", lw=0.6); ax.spines[["top", "right"]].set_visible(False)
axL.set_yticks(ys); axL.set_yticklabels(labels, fontsize=8); axL.tick_params(axis="y", length=0)
axL.plot([], [], "o", color=BLUE, label="temp 1 (frozen)"); axL.plot([], [], "o", color=AMBER, label="temp 0")
axL.legend(loc="lower right", fontsize=8, frameon=False)
fig.suptitle("temp-1 → temp-0: who honors temperature, whose divergence survives", fontsize=11)
fig.tight_layout()
out = HERE / "temp0_compare.png"; fig.savefig(out, dpi=150); print(f"\nplot -> {out}")
