#!/usr/bin/env python3
"""Judge accuracy against the human directed pass. For each marker: the human verdicts in
data/coding/directed.<coder>.jsonl (held/departed per (model, scene, run)) against a judge's
labels. Reports TPR (judge says departed when the human did), TNR (judge says held when the human
did), agreement, Cohen's kappa, n. No judge without a baseline; every judged number carries its
accuracy.

Which judge: by default the adjudicated store (data/benchmark/markers.json, one judge so far);
with --judge <slug> the raw labels of that judge under <study>/markers/<slug with __>/ (written
by harness/judge.py), quote-verified the way adjudicate.py verifies them (a departure whose
trigger quote is not verbatim in the run's replies is dropped; a hold needs no quote).

--by-vendor adds the mode-sharing test: the judge's disagreement rate with the human on subject
models from the judge's own vendor against the rest, per marker, with a two-sided Fisher p.

    python harness/judge_accuracy.py --study studies/conduct [--coder Tap] [--judge openai/gpt-5.4-mini] [--by-vendor]
"""
import json, sys, argparse, glob, re
from math import comb
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).resolve().parent / "viewer"))
from arcs import load_arcs

ap = argparse.ArgumentParser()
ap.add_argument("--study", default="studies/conduct"); ap.add_argument("--coder", default=None)
ap.add_argument("--salt", default="conduct-2026-09")
ap.add_argument("--judge", default=None, help="raw labels of this judge slug (default: the adjudicated store)")
ap.add_argument("--by-vendor", action="store_true", help="split disagreements by judge-vendor == subject-vendor")
args = ap.parse_args()
study = Path(args.study)
_, reveal = load_arcs(study, (), args.salt)
bench = {p.stem: json.loads(p.read_text()) for p in (study / "data/benchmark").glob("*.json") if p.name != "markers.json"}
vendor = lambda slug: slug.split("/")[0] if "/" in slug else slug
subject_vendor = {m: vendor(d.get("slug", "")) for m, d in bench.items()}

def norm(s): return re.sub(r"\s+", " ", (s or "").replace("’", "'").replace("“", '"').replace("”", '"')).strip().lower()
def reply_text(model, scene, run):
    runs = bench[model]["scenes"][scene]["runs"]; return norm(" \n ".join((t.get("reply") or "") for t in runs[run]))

# judge label: (model, marker, run) -> True/False/None
def judge_label(model, mid, scene, run):
    if args.judge:
        f = study / "markers" / args.judge.replace("/", "__") / f"{model}.json"
        if not f.exists(): return None
        blob = json.loads(f.read_text())
        if "_error" in blob: return None
        node = (blob.get("markers") or {}).get(mid, {}).get(f"run{run}")
        if not node or node.get("value") is None: return None
        v = bool(node["value"])
        if v:  # a departure needs a verbatim quote
            q = norm(node.get("trigger_quote", "") or "")
            if len(q) < 6 or q not in reply_text(model, scene, run): return None
        return v
    v = MK.get(model, {}).get(mid, {}).get("runs", [None, None])[run]
    return None if v is None else bool(v)

MK = json.load(open(study / "data/benchmark/markers.json"))["models"] if not args.judge else {}
judge_name = args.judge or "adjudicated:" + ",".join(json.load(open(study / "data/benchmark/markers.json"))["_meta"]["judges"])
jvendor = vendor(judge_name.split(":")[-1].split(",")[0])

files = glob.glob(str(study / "data/coding/directed.*.jsonl"))
if args.coder: files = [f for f in files if f.endswith(f"directed.{args.coder}.jsonl")]
rows = [json.loads(l) for f in files for l in open(f) if l.strip()]
if not rows: sys.exit("no directed labels yet")
by = {}
for r in rows:
    if not r.get("verdict"): continue
    by[(r["coder"], reveal.get(r["blind"], r["blind"]), r["scene"], r["run"])] = r
per, cells = {}, []  # cells: (coder, mid, model, h, j)
for (coder, model, scene, run), r in by.items():
    mid = r["marker"]; jv = judge_label(model, mid, scene, run)
    if jv is None: continue
    h = 1 if r["verdict"] == "departed" else 0; j = 1 if jv else 0
    cells.append((coder, mid, model, h, j))
    d = per.setdefault((coder, mid), {"tp": 0, "tn": 0, "fp": 0, "fn": 0})
    if h and j: d["tp"] += 1
    elif not h and not j: d["tn"] += 1
    elif j and not h: d["fp"] += 1
    else: d["fn"] += 1
print(f"judge: {judge_name}")
print(f"{'coder':<10}{'marker':<20}{'n':>4}{'TPR':>7}{'TNR':>7}{'agree':>7}{'kappa':>7}{'over':>6}{'miss':>6}")
for (coder, mid), d in sorted(per.items()):
    n = sum(d.values()); tpr = d["tp"] / max(1, d["tp"] + d["fn"]); tnr = d["tn"] / max(1, d["tn"] + d["fp"])
    po = (d["tp"] + d["tn"]) / n
    ph = (d["tp"] + d["fn"]) / n; pj = (d["tp"] + d["fp"]) / n; pe = ph * pj + (1 - ph) * (1 - pj)
    kappa = (po - pe) / (1 - pe) if pe < 1 else float("nan")
    print(f"{coder:<10}{mid:<20}{n:>4}{tpr:>7.2f}{tnr:>7.2f}{po:>7.2f}{kappa:>7.2f}{d['fp']:>6}{d['fn']:>6}")

if args.by_vendor:
    def fisher(a, b, c, d):
        n = a + b + c + d; r1 = a + b; c1 = a + c
        p_obs = comb(r1, a) * comb(n - r1, c1 - a) / comb(n, c1); p = 0.0
        for i in range(max(0, c1 - (n - r1)), min(r1, c1) + 1):
            pi = comb(r1, i) * comb(n - r1, c1 - i) / comb(n, c1)
            if pi <= p_obs + 1e-12: p += pi
        return p
    print(f"\nmode-sharing: judge vendor = {jvendor}; disagreement on own-vendor subjects vs the rest")
    print(f"{'marker':<20}{'own':>10}{'rate':>6}{'rest':>10}{'rate':>6}{'over/own':>9}{'p':>8}")
    mids = sorted({c[1] for c in cells}) + ["ALL"]
    for mid in mids:
        own = [c for c in cells if (mid == "ALL" or c[1] == mid) and subject_vendor.get(c[2]) == jvendor]
        rest = [c for c in cells if (mid == "ALL" or c[1] == mid) and subject_vendor.get(c[2]) != jvendor]
        do = sum(1 for c in own if c[3] != c[4]); dr = sum(1 for c in rest if c[3] != c[4])
        oo = sum(1 for c in own if c[3] == 0 and c[4] == 1)
        if not own or not rest: continue
        p = fisher(do, len(own) - do, dr, len(rest) - dr)
        print(f"{mid:<20}{f'{do}/{len(own)}':>10}{do/len(own):>6.2f}{f'{dr}/{len(rest)}':>10}{dr/len(rest):>6.2f}{oo:>9}{p:>8.3f}")
