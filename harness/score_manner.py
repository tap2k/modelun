#!/usr/bin/env python3
"""Score the human's manner pass (data/coding/manner_<version>.<coder>.jsonl, from the coding page
in --codebook mode) against each LLM coder's relabel under the same codebook version, on the arcs
the human coded. Per code: n human, n coder, both, kappa; per coder: mean kappa, recall, precision;
plus dominant-manner agreement (the human's first manner on an arc is the dominant one; is it
among the coder's present codes?) and trajectory agreement. This is the number the house claim
needs: human-LLM agreement on manner, measured on a directed manner pass rather than mapped from
open codes.

    python harness/score_manner.py --study studies/conduct --version v2 [--coder Tap]
"""
import json, sys, glob, argparse, collections, math
from pathlib import Path
ap = argparse.ArgumentParser(); ap.add_argument("--study", default="studies/conduct"); ap.add_argument("--version", default="v2"); ap.add_argument("--coder", default="Tap")
args = ap.parse_args(); study = Path(args.study)
hf = study / f"data/coding/manner_{args.version}.{args.coder}.jsonl"
if not hf.exists(): sys.exit(f"no human manner pass yet: {hf}")
H = [json.loads(l) for l in open(hf) if l.strip()]
harcs = sorted({r["arc"] for r in H if r.get("kind") == "code"})
hcodes = collections.defaultdict(set); hfirst = {}; htraj = {}
for r in sorted(H, key=lambda r: r["ts"]):
    if r.get("kind") == "code": hcodes[r["arc"]].add(r["code"]); hfirst.setdefault(r["arc"], r["code"])
    if r.get("kind") == "trajectory": htraj[r["arc"]] = r["code"]
def kappa(pairs):
    n = len(pairs)
    if not n: return float("nan")
    po = sum(1 for a, b in pairs if a == b) / n; pa = sum(a for a, _ in pairs) / n; pb = sum(b for _, b in pairs) / n
    pe = pa * pb + (1 - pa) * (1 - pb); return (po - pe) / (1 - pe) if pe < 1 else float("nan")
print(f"human {args.coder}: {len(harcs)} arcs, {sum(len(v) for v in hcodes.values())} manner codes, {len(htraj)} trajectories\n")
codes = sorted({c for v in hcodes.values() for c in v})
summary = []
for f in sorted(glob.glob(str(study / f"data/coding/relabel_{args.version}.llm-*.jsonl"))):
    name = Path(f).name[len(f"relabel_{args.version}."):-6]; rows = [json.loads(l) for l in open(f) if l.strip()]
    ccodes = collections.defaultdict(set); ctraj = {}
    for r in rows:
        if r["kind"] == "code" and r["arc"] in hcodes: ccodes[r["arc"]].add(r["code"])
        if r["kind"] == "trajectory": ctraj[r["arc"]] = r["code"]
    allc = sorted(set(codes) | {c for a in harcs for c in ccodes[a]})
    print(f"== {name} ==")
    print(f"{'code':<34}{'human':>6}{'coder':>6}{'both':>6}{'kappa':>7}")
    ks = []; hb = cb = both = 0
    for c in allc:
        pairs = [(c in hcodes[a], c in ccodes[a]) for a in harcs]
        nh = sum(1 for a in harcs if c in hcodes[a]); nc = sum(1 for a in harcs if c in ccodes[a]); nb = sum(1 for a in harcs if c in hcodes[a] and c in ccodes[a])
        k = kappa(pairs); ks.append(k) if not math.isnan(k) and (nh or nc) else None; hb += nh; cb += nc; both += nb
        print(f"{c:<34}{nh:>6}{nc:>6}{nb:>6}{k:>7.2f}")
    dom = [(hfirst[a] in ccodes[a]) for a in harcs if a in hfirst]
    tr = [(htraj[a] == ctraj.get(a)) for a in harcs if a in htraj and a in ctraj]
    mk = sum(ks) / len(ks) if ks else float("nan")
    print(f"mean kappa {mk:.2f}  recall {both/max(1,hb):.2f}  precision {both/max(1,cb):.2f}  dominant manner found by coder {sum(dom)/max(1,len(dom)):.2f} ({len(dom)})  trajectory agree {sum(tr)/max(1,len(tr)):.2f} ({len(tr)})\n")
    summary.append((name, mk, both / max(1, hb), both / max(1, cb), sum(dom) / max(1, len(dom))))
print(f"{'coder':<34}{'mean k':>8}{'recall':>8}{'prec':>8}{'dominant':>10}")
for name, mk, rc, pr, dm in summary: print(f"{name:<34}{mk:>8.2f}{rc:>8.2f}{pr:>8.2f}{dm:>10.2f}")
