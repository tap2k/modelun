#!/usr/bin/env python3
"""Reply length beside the codes: mean words per reply, per vendor and scene, and whether length
sorts by vendor (eta-squared with a permutation p) and tracks capability (Spearman against the
Epoch Capabilities Index and its dates). The same statistics the manner matrix uses, on a measured
column rather than a coded one, so the house claim can be read against something no judge touched.

    python harness/reply_length.py --study studies/conduct >> studies/conduct/data/coding/results/HOUSE-PROFILES-v2-<date>.md

The table covers every scene given to --table-scenes; the vendor test uses --scenes, the three
scenes every model has (the specimens lack make_it_better), so the per-model means are comparable.
"""
import json, sys, csv, argparse, collections, random, datetime, statistics
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "viewer"))
from arcs import load_arcs

ap = argparse.ArgumentParser()
ap.add_argument("--study", default="studies/conduct")
ap.add_argument("--scenes", default="facts,doctors_note,bad_plan", help="scenes the vendor test uses")
ap.add_argument("--table-scenes", default="facts,doctors_note,bad_plan,make_it_better")
ap.add_argument("--min-vendor", type=int, default=2, help="vendors with at least this many models enter the test")
args = ap.parse_args()
study = Path(args.study); H = Path("studies/cross-instrument")

arcs, reveal = load_arcs(study, (), specimens=True)
bench = {p.stem: json.loads(p.read_text()) for p in (study / "data/benchmark").glob("*.json")
         if p.name != "markers.json"}
vendor = {m: d.get("slug", "").split("/")[0] for m, d in bench.items()}

eci_rows = {r["Model"]: r for r in csv.DictReader(open(H / "eci_scores_2026-09-13.csv"))}
eci, dates = {}, {}
for ln in open(H / "eci_map_2026-09-13.tsv"):
    if ln.startswith("#") or "\t" not in ln:
        continue
    ours, theirs = ln.rstrip("\n").split("\t"); r = eci_rows[theirs]
    eci[ours] = float(r["eci"]); dates[ours] = datetime.date.fromisoformat(r["date"]).toordinal()

words = collections.defaultdict(list)                  # (model, scene) -> words per reply
for a in arcs:
    m = reveal[a["blind"]]
    for t in a["turns"]:
        if t.get("reply"):
            words[(m, a["scene"])].append(len(t["reply"].split()))

models = sorted({m for m, _ in words})
by_vendor = collections.defaultdict(list)
for m in models:
    by_vendor[vendor.get(m, "other")].append(m)

def scene_mean(ms, s):
    """The vendor's mean of its models' mean reply length, so a chatty model cannot outvote."""
    per_model = [statistics.mean(words[(m, s)]) for m in ms if (m, s) in words]
    return round(statistics.mean(per_model)) if per_model else None

def model_mean(m, scenes):
    sm = [statistics.mean(words[(m, s)]) for s in scenes if (m, s) in words]
    return statistics.mean(sm) if sm else None

def eta2(vals):
    groups = collections.defaultdict(list)
    for g, x in vals: groups[g].append(x)
    xs = [x for _, x in vals]; mu = sum(xs) / len(xs); ss_t = sum((x - mu) ** 2 for x in xs)
    ss_b = sum(len(v) * ((sum(v) / len(v)) - mu) ** 2 for v in groups.values())
    return ss_b / ss_t if ss_t else 0.0

def perm_p(vals, B=3000, seed=0):
    obs = eta2(vals); rnd = random.Random(seed)
    gs = [g for g, _ in vals]; xs = [x for _, x in vals]; k = 0
    for _ in range(B):
        rnd.shuffle(gs); k += eta2(list(zip(gs, xs))) >= obs - 1e-12
    return obs, k / B

def spearman(a, b):
    ks = [k for k in a if k in b]; n = len(ks)
    if n < 6: return float("nan"), n
    rk = lambda d: {k: i for i, k in enumerate(sorted(ks, key=lambda k: d[k]))}
    ra, rb = rk(a), rk(b); d2 = sum((ra[k] - rb[k]) ** 2 for k in ks)
    return 1 - 6 * d2 / (n * (n * n - 1)), n

table_scenes = args.table_scenes.split(",")
test_scenes = args.scenes.split(",")
today = datetime.date.today().isoformat()

print(f"\n## Reply length by vendor and scene (mean words per reply; per-model means averaged; {today})\n")
head = "    vendor     " + "".join(f"{s:>16}" for s in table_scenes)
print(head)
print("    panel      " + "".join(f"{scene_mean(models, s):>16}" for s in table_scenes))
for v in sorted(by_vendor, key=lambda v: -len(by_vendor[v])):
    ms = by_vendor[v]
    if len(ms) < args.min_vendor:
        continue
    print(f"    {v:<11}" + "".join(f"{scene_mean(ms, s):>16}" for s in table_scenes)
          + f"   ({len(ms)} models)")

means = {m: model_mean(m, test_scenes) for m in models}
means = {m: v for m, v in means.items() if v is not None}
big = {v for v in set(vendor.values()) if sum(1 for m in means if vendor.get(m) == v) >= args.min_vendor}
vals = [(vendor[m], means[m]) for m in means if vendor.get(m) in big]
e, p = perm_p(vals)
rho_e, n_e = spearman(means, eci); rho_d, n_d = spearman(means, dates)
print(f"\nVendor effect on mean reply length over {', '.join(test_scenes)} "
      f"({len(vals)} models, vendors with {args.min_vendor} or more): "
      f"eta-squared {e:.2f}, permutation p {p:.3f}. "
      f"Spearman against capability {rho_e:.2f} (n={n_e}), against release date {rho_d:.2f} (n={n_d}).")
