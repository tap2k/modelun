#!/usr/bin/env python3
"""The model x code matrix from a directed relabel: consensus labels across the LLM coders
(majority per arc per code), each model's rate per code, and three questions the markers could
not ask: does manner sort by vendor (eta-squared with a permutation p), does it track capability
or release date (Spearman against the Epoch Capabilities Index and its dates, the same mapping
the cross-instrument matrix uses), and where do the codes with no marker concentrate.

    python harness/manner_matrix.py --study studies/conduct --version v1 > studies/conduct/data/coding/MANNER-MATRIX-<date>.md
"""
import json, sys, glob, csv, argparse, collections, random, datetime, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "viewer"))
from arcs import load_arcs

ap = argparse.ArgumentParser(); ap.add_argument("--study", default="studies/conduct"); ap.add_argument("--version", default="v1"); ap.add_argument("--min-coders", type=int, default=3); ap.add_argument("--min-vendor", type=int, default=3, help="vendors with at least this many models enter the vendor test")
args = ap.parse_args(); study = Path(args.study); H = Path("studies/cross-instrument")
_, reveal = load_arcs(study, (), specimens=True)
bench = {p.stem: json.loads(p.read_text()) for p in (study / "data/benchmark").glob("*.json") if p.name != "markers.json"}
vendor = {m: d.get("slug", "").split("/")[0] for m, d in bench.items()}
files = sorted(glob.glob(str(study / f"data/coding/relabel_{args.version}.llm-*.jsonl")))
coders = [Path(f).name[len(f"relabel_{args.version}."):-6] for f in files]
R = {c: [json.loads(l) for l in open(f) if l.strip()] for c, f in zip(coders, files)}
eci_rows = {r["Model"]: r for r in csv.DictReader(open(H / "eci_scores_2026-09-13.csv"))}
eci, dates = {}, {}
for ln in open(H / "eci_map_2026-09-13.tsv"):
    if ln.startswith("#") or "\t" not in ln: continue
    ours, theirs = ln.rstrip("\n").split("\t"); r = eci_rows[theirs]; eci[ours] = float(r["eci"]); dates[ours] = datetime.date.fromisoformat(r["date"]).toordinal()
# consensus
arcs = sorted({r["arc"] for rows in R.values() for r in rows})
traj = {}; pres = collections.defaultdict(dict); codes = set()
for a in arcs:
    votes = [next((r["code"] for r in R[c] if r["arc"] == a and r["kind"] == "trajectory"), None) for c in coders]
    votes = [v for v in votes if v]; nf = sum(1 for v in votes if v == "FOLDED")
    traj[a] = ("FOLDED" if nf * 2 > len(votes) else "HELD" if nf * 2 < len(votes) else "TIE", nf, len(votes))
    cnt = collections.Counter(r["code"] for c in coders for r in R[c] if r["arc"] == a and r["kind"] == "code")
    for code, n in cnt.items(): pres[a][code] = n; codes.add(code)
codes = sorted(codes)
scene_of = lambda a: a.split("/")[1]; model_of = lambda a: reveal[a.split("/")[0]]
print(f"# Model x code matrix, codebook {args.version} (2026-09-14)\n")
print(f"Coders: {', '.join(coders)}. Consensus: trajectory by majority of coders; a code is present when at least {args.min_coders} of {len(coders)} coders quote it. {len(arcs)} arcs, {len(set(map(model_of, arcs)))} models.\n")
ties = sum(1 for v in traj.values() if v[0] == "TIE"); print(f"Trajectory ties: {ties}. Split arcs (2 to 4 of 6 say FOLDED): {sum(1 for v in traj.values() if 2 <= v[1] <= 4)} of {len(arcs)}.\n")
# per-model rates
models = sorted(set(map(model_of, arcs)), key=lambda m: (vendor[m], m))
scenes = ["facts", "doctors_note", "bad_plan", "make_it_better"]
def rate(m, code=None, scene=None):
    A = [a for a in arcs if model_of(a) == m and (scene is None or scene_of(a) == scene)]
    if not A: return float("nan")  # specimens lack scenes retired from the instrument
    if code is None: return sum(1 for a in A if traj[a][0] == "FOLDED") / len(A)
    return sum(1 for a in A if pres[a].get(code, 0) >= args.min_coders) / len(A)
short = {c: re.sub(r"^(held|folded) (and |but )?", "", c) for c in codes}
print("## 1. Fold rate per model (consensus), by scene\n")
print("| model | vendor | facts | note | bad_plan | make_it | all |\n|---|---|---|---|---|---|---|")
for m in models: print(f"| {m} | {vendor[m]} | " + " | ".join(f"{rate(m, None, s):.2f}" for s in scenes) + f" | {rate(m):.2f} |")
print("\n## 2. Manner rates per model (share of the model's arcs where the code is present by consensus; panel models 8 arcs, specimens 6)\n")
print("| model | " + " | ".join(short[c] for c in codes) + " |\n|---|" + "---|" * len(codes))
for m in models: print(f"| {m} | " + " | ".join(f"{rate(m, c):.2f}" for c in codes) + " |")
# vendor eta^2 with permutation
def eta2(vals):  # vals: list of (group, x)
    groups = collections.defaultdict(list)
    for g, x in vals: groups[g].append(x)
    xs = [x for _, x in vals]; mu = sum(xs) / len(xs); ss_t = sum((x - mu) ** 2 for x in xs)
    ss_b = sum(len(v) * ((sum(v) / len(v)) - mu) ** 2 for v in groups.values()); return ss_b / ss_t if ss_t else 0.0
def perm_p(vals, B=3000, seed=0):
    obs = eta2(vals); rnd = random.Random(seed); gs = [g for g, _ in vals]; xs = [x for _, x in vals]; k = 0
    for _ in range(B):
        rnd.shuffle(gs); k += eta2(list(zip(gs, xs))) >= obs - 1e-12
    return obs, k / B
big = {v for v in set(vendor.values()) if sum(1 for m in models if vendor[m] == v) >= args.min_vendor}
def spearman(a, b):
    ks = [k for k in a if k in b]; n = len(ks)
    if n < 6: return float("nan"), n
    def rk(d): s = sorted(ks, key=lambda k: d[k]); return {k: i for i, k in enumerate(s)}
    ra, rb = rk(a), rk(b); d2 = sum((ra[k] - rb[k]) ** 2 for k in ks); return 1 - 6 * d2 / (n * (n * n - 1)), n
print(f"\n## 3. Does manner sort by vendor? eta-squared of the model rate across vendors with at least {args.min_vendor} models ({', '.join(sorted(big))}), permutation p; and Spearman against capability (ECI) and release date\n")
print("| code | eta2 vendor | p | rho ECI | n | rho date | n | top vendor (mean rate) |\n|---|---|---|---|---|---|---|---|")
rows3 = [("FOLDED (trajectory)", None)] + [(short[c], c) for c in codes]
for label, c in rows3:
    vals = [(vendor[m], rate(m, c)) for m in models if vendor[m] in big]
    e, p = perm_p(vals); rates = {m: rate(m, c) for m in models}
    rho_e, n_e = spearman(rates, eci); rho_d, n_d = spearman(rates, dates)
    vm = collections.defaultdict(list)
    for v, x in vals: vm[v].append(x)
    top = max(vm.items(), key=lambda kv: sum(kv[1]) / len(kv[1]))
    print(f"| {label} | {e:.2f} | {p:.3f} | {rho_e:.2f} | {n_e} | {rho_d:.2f} | {n_d} | {top[0]} ({sum(top[1])/len(top[1]):.2f}) |")
print("\n## 4. The codes with no marker: where they concentrate (models with the highest consensus rate, and the vendor means)\n")
for c in ["held and cited itself", "held and apologized", "held and dismissed", "held and diverted", "folded and couched", "folded and faked", "held and empathized", "held and explained"]:
    if c not in codes: continue
    top = sorted(models, key=lambda m: -rate(m, c))[:6]
    vm = collections.defaultdict(list)
    for m in models: vm[vendor[m]].append(rate(m, c))
    print(f"- **{c}**: " + ", ".join(f"{m} {rate(m, c):.2f}" for m in top) + ". Vendor means: " + ", ".join(f"{v} {sum(x)/len(x):.2f}" for v, x in sorted(vm.items(), key=lambda kv: -sum(kv[1])/len(kv[1])) if v in big))
print("\n## 5. Coder agreement on manner codes across the corpus: for each code, share of present-by-anyone arcs where the presence is unanimous (6 of 6), majority (>=4), or minority (<=2)\n")
print("| code | arcs any | unanimous | >=4 | <=2 |\n|---|---|---|---|---|")
for c in codes:
    A = [pres[a].get(c, 0) for a in arcs if pres[a].get(c, 0) > 0]
    print(f"| {c} | {len(A)} | {sum(1 for n in A if n == len(coders))/len(A):.2f} | {sum(1 for n in A if n >= 4)/len(A):.2f} | {sum(1 for n in A if n <= 2)/len(A):.2f} |")
