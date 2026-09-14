#!/usr/bin/env python3
"""Judge accuracy against the human directed pass. For each marker: the human verdicts in
data/coding/directed.<coder>.jsonl (held/departed per (model, scene, run)) against the judge's
adjudicated value in data/benchmark/markers.json. Reports TPR (judge says departed when the human
did), TNR (judge says held when the human did), agreement, Cohen's kappa, n. No judge without a
baseline; every judged number carries its accuracy.

    python harness/judge_accuracy.py --study studies/conduct [--coder Tap]
"""
import json, sys, argparse, glob
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "viewer"))
from arcs import load_arcs

ap = argparse.ArgumentParser(); ap.add_argument("--study", default="studies/conduct"); ap.add_argument("--coder", default=None); ap.add_argument("--salt", default="conduct-2026-09")
args = ap.parse_args()
study = Path(args.study)
_, reveal = load_arcs(study, (), args.salt)
mk = json.load(open(study / "data/benchmark/markers.json"))["models"]
files = glob.glob(str(study / "data/coding/directed.*.jsonl"))
if args.coder: files = [f for f in files if f.endswith(f"directed.{args.coder}.jsonl")]
rows = [json.loads(l) for f in files for l in open(f) if l.strip()]
if not rows: sys.exit("no directed labels yet")
by = {}
for r in rows:
    if not r.get("verdict"): continue
    by[(r["coder"], reveal.get(r["blind"], r["blind"]), r["scene"], r["run"])] = r
per = {}
for (coder, model, scene, run), r in by.items():
    mid = r["marker"]; jv = mk.get(model, {}).get(mid, {}).get("runs", [None, None])[run]
    if jv is None: continue
    h = 1 if r["verdict"] == "departed" else 0; j = 1 if jv else 0
    d = per.setdefault((coder, mid), {"tp": 0, "tn": 0, "fp": 0, "fn": 0})
    if h and j: d["tp"] += 1
    elif not h and not j: d["tn"] += 1
    elif j and not h: d["fp"] += 1
    else: d["fn"] += 1
print(f"{'coder':<10}{'marker':<20}{'n':>4}{'TPR':>7}{'TNR':>7}{'agree':>7}{'kappa':>7}")
for (coder, mid), d in sorted(per.items()):
    n = sum(d.values()); tpr = d["tp"] / max(1, d["tp"] + d["fn"]); tnr = d["tn"] / max(1, d["tn"] + d["fp"])
    po = (d["tp"] + d["tn"]) / n
    ph = (d["tp"] + d["fn"]) / n; pj = (d["tp"] + d["fp"]) / n; pe = ph * pj + (1 - ph) * (1 - pj)
    kappa = (po - pe) / (1 - pe) if pe < 1 else float("nan")
    print(f"{coder:<10}{mid:<20}{n:>4}{tpr:>7.2f}{tnr:>7.2f}{po:>7.2f}{kappa:>7.2f}")
