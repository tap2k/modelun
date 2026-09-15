#!/usr/bin/env python3
"""House profiles from a directed relabel: per vendor, manner rates against the panel mean, the
codes that set the vendor apart, and for each such code the quotes the coders agreed on most,
with model and scene. Material for caricatures; the numbers are in manner_matrix.py.

    python harness/house_profiles.py --study studies/conduct --version v1 > studies/conduct/data/coding/HOUSE-PROFILES-<date>.md
"""
import json, sys, glob, argparse, collections, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "viewer"))
from arcs import load_arcs
ap = argparse.ArgumentParser(); ap.add_argument("--study", default="studies/conduct"); ap.add_argument("--version", default="v1"); ap.add_argument("--min-coders", type=int, default=3)
args = ap.parse_args(); study = Path(args.study)
_, reveal = load_arcs(study, (), specimens=True)
bench = {p.stem: json.loads(p.read_text()) for p in (study / "data/benchmark").glob("*.json") if p.name != "markers.json"}
vendor = {m: d.get("slug", "").split("/")[0] for m, d in bench.items()}
files = sorted(glob.glob(str(study / f"data/coding/relabel_{args.version}.llm-*.jsonl"))); coders = [Path(f).name[len(f"relabel_{args.version}."):-6] for f in files]
R = [json.loads(l) for f in files for l in open(f) if l.strip()]
arcs = sorted({r["arc"] for r in R}); model_of = lambda a: reveal[a.split("/")[0]]; scene_of = lambda a: a.split("/")[1]
traj = {}; pres = collections.defaultdict(collections.Counter); quotes = collections.defaultdict(collections.Counter)
for r in R:
    if r["kind"] == "trajectory" and r["code"]: traj.setdefault(r["arc"], collections.Counter())[r["code"]] += 1
    if r["kind"] == "code": pres[r["arc"]][r["code"]] += 1; quotes[(r["arc"], r["code"])][r["quote"]] += 1
codes = sorted({r["code"] for r in R if r["kind"] == "code"})
models = sorted(set(map(model_of, arcs)))
def rate(m, code):
    A = [a for a in arcs if model_of(a) == m]; return sum(1 for a in A if pres[a][code] >= args.min_coders) / len(A)
def fold(m):
    A = [a for a in arcs if model_of(a) == m]; return sum(1 for a in A if traj.get(a, {}).get("FOLDED", 0) * 2 > sum(traj.get(a, {}).values())) / len(A)
panel = {c: sum(rate(m, c) for m in models) / len(models) for c in codes}
vendors = collections.defaultdict(list)
for m in models: vendors[vendor[m]].append(m)
order = sorted(vendors, key=lambda v: -len(vendors[v]))
print(f"# House profiles, codebook {args.version} (2026-09-14)\n\nPer vendor: fold rate, manner rates as deviation from the panel mean (+ means the vendor does it more), the codes that set the vendor apart (largest absolute deviation), and for each the quotes the coders agreed on most (count of coders out of {len(coders)}). Panel = {len(models)} models incl. specimens. Consensus = at least {args.min_coders} coders.\n")
for v in order:
    ms = vendors[v]; n = len(ms)
    vr = {c: sum(rate(m, c) for m in ms) / n for c in codes}
    dev = sorted(codes, key=lambda c: -(vr[c] - panel[c]))
    print(f"\n## {v}  ({n} models: {', '.join(ms)})\n")
    print(f"Fold rate: {sum(fold(m) for m in ms)/n:.2f} (panel {sum(fold(m) for m in models)/len(models):.2f}). Per model: " + ", ".join(f"{m} {fold(m):.2f}" for m in ms) + "\n")
    print("| code | vendor | panel | dev |\n|---|---|---|---|")
    for c in dev: print(f"| {c} | {vr[c]:.2f} | {panel[c]:.2f} | {vr[c]-panel[c]:+.2f} |")
    top = [c for c in dev if vr[c] - panel[c] > 0.08][:4]; low = [c for c in reversed(dev) if panel[c] - vr[c] > 0.08][:2]
    for c in top + low:
        tag = "does more" if c in top else "does less"
        print(f"\n**{c}** ({tag}: vendor {vr[c]:.2f}, panel {panel[c]:.2f})\n")
        if c in low: continue
        # best-agreed quotes among this vendor's arcs where the code is present by consensus
        cand = []
        for a in arcs:
            if model_of(a) in ms and pres[a][c] >= args.min_coders:
                q, k = quotes[(a, c)].most_common(1)[0]; cand.append((k, pres[a][c], a, q))
        cand.sort(key=lambda t: (-t[0], -t[1]))
        seen = set()
        for k, kc, a, q in cand:
            if model_of(a) in seen and len(seen) >= 2: continue
            seen.add(model_of(a)); print(f"- {model_of(a)}, {scene_of(a)} ({kc} coders; quote by {k}): \"{q.strip()[:220]}\"")
            if len(seen) >= 3: break
    # scene sketch: what the vendor does per scene (top two codes per scene)
    print("\nBy scene (top codes, share of the vendor's arcs in that scene):")
    for s in ["facts", "doctors_note", "bad_plan", "make_it_better"]:
        A = [a for a in arcs if model_of(a) in ms and scene_of(a) == s]
        if not A: continue
        cc = collections.Counter(c for a in A for c in codes if pres[a][c] >= args.min_coders)
        fr = sum(1 for a in A if traj.get(a, {}).get("FOLDED", 0) * 2 > sum(traj.get(a, {}).values())) / len(A)
        print(f"- {s}: folded {fr:.2f}; " + ", ".join(f"{re.sub(r'^(held|folded) (and |but )?','',c)} {k/len(A):.2f}" for c, k in cc.most_common(3)))
