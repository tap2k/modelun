#!/usr/bin/env python3
"""The generational claim tested on the models added after the July freeze (wave 2).

The arXiv paper (tag suggestibility-arxiv-v1) reports 45 models. Wave 2 added 25, run 2026-09-04/06
on the same frozen tag arm (at --max-tokens 8192, which the files record). This reads each lineage's
July models and its wave-2 additions from probes/righteffect_analysis.json and reports, per family,
the July endpoint and every new model's TAGeff with its 90% bootstrap interval.

    python3 heldout_wave2.py > HELDOUT-WAVE2-<date>.md
"""
import json, subprocess, datetime, collections
from pathlib import Path
from lineage import FAM

HERE = Path(__file__).resolve().parent
per = json.loads((HERE / "probes" / "righteffect_analysis.json").read_text())["per_model"]
tagged = subprocess.run(["git", "ls-tree", "--name-only", "suggestibility-arxiv-v1", str(HERE / "probes" / "righteffect") + "/"],
                        capture_output=True, text=True, check=True).stdout.split()
july = {Path(p).stem for p in tagged}
new = sorted(set(per) - july)

def fmt(m):
    r = per[m]; lo, hi = r["ci90"]; sig = "yes" if hi < 0 else ("positive" if lo > 0 else "no")
    return f"{100 * r['tageff']:+.0f} [{100 * lo:+.0f}, {100 * hi:+.0f}]", sig

print(f"# Held-out test of the generational reversal on the wave-2 models ({datetime.date.today()})\n")
print(f"July panel {len(july)} models (the arXiv tag); wave 2 adds {len(new)}. TAGeff in points, 90% bootstrap "
      "interval; 'resists' means the interval is below zero.\n")
fam = collections.defaultdict(list)
for m, (f, g) in FAM.items():
    if m in per: fam[f].append((g, m))
print("| family | July endpoint | wave-2 model (generation) | TAGeff [90% CI] | resists |\n|---|---|---|---|---|")
for f, ms in fam.items():
    ms.sort(); old = [m for g, m in ms if m in july]; last = old[-1] if old else None
    for g, m in ms:
        if m in july: continue
        e, s = fmt(m)
        print(f"| {f} | {last} {fmt(last)[0] if last else ''} | {m} (g{g}) | {e} | {s} |")
print("\nWave-2 models outside the tracked families:\n")
for m in new:
    if m not in FAM:
        e, s = fmt(m); print(f"- {m}: {e}, resists {s}")
sig = lambda ms: sum(per[m]["ci90"][1] < 0 for m in ms)
pos = lambda ms: sum(per[m]["ci90"][0] > 0 for m in ms)
print(f"\nSignificant resisters: July {sig(july)} of {len(july)}, wave 2 {sig(new)} of {len(new)}. "
      f"Significantly sycophantic: July {pos(july)}, wave 2 {pos(new)}. (The paper's counts use BH over "
      "bootstrap p and a floor guard, so they differ from these interval counts.)")
