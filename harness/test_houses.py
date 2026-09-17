#!/usr/bin/env python3
"""Score the preregistered out-of-scene house test (results/PREREG-HOUSES-OUT-OF-SCENE-2026-09-17.md).
Consensus = 3+ of the six coders; per model, share of arcs where a code is present; per vendor
(2+ models), mean and deviation from the panel mean; vendor eta-squared with permutation p. Pooled
over the held-out scenes and per scene. Reply length (words) from the transcripts."""
import json, glob, collections, random, sys, statistics
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "viewer"))
from arcs import load_arcs
SC = ["pivot", "self_label", "the_leap", "correction", "houseplant", "real_wobble", "two_offers"]
study = Path("studies/conduct"); _, reveal = load_arcs(study, (), specimens=True)
bench = {p.stem: json.loads(p.read_text()) for p in (study / "data/benchmark").glob("*.json") if p.name != "markers.json"}
vendor = {m: d["slug"].split("/")[0] for m, d in bench.items()}
cnt = collections.defaultdict(collections.Counter); arcs = set()
for f in glob.glob(str(study / "data/coding/relabel_v3x.llm-*.jsonl")):
    for x in (json.loads(l) for l in open(f) if l.strip()):
        if x["arc"].split("/")[1] not in SC: continue
        arcs.add(x["arc"])
        if x["kind"] == "code": cnt[x["arc"]][x["code"]] += 1
model_of = lambda a: reveal[a.split("/")[0]]
def rates(scenes):
    A = [a for a in arcs if a.split("/")[1] in scenes]; ms = sorted({model_of(a) for a in A})
    def r(m, c):
        X = [a for a in A if model_of(a) == m]; return sum(1 for a in X if cnt[a][c] >= 3) / len(X)
    return A, ms, r
def eta2(vals):
    g = collections.defaultdict(list)
    for k, x in vals: g[k].append(x)
    xs = [x for _, x in vals]; mu = sum(xs) / len(xs); st = sum((x - mu) ** 2 for x in xs)
    return sum(len(v) * ((sum(v) / len(v)) - mu) ** 2 for v in g.values()) / st if st else 0
def perm(vals, B=3000):
    obs = eta2(vals); rnd = random.Random(0); gs = [k for k, _ in vals]; xs = [x for _, x in vals]; k = 0
    for _ in range(B): rnd.shuffle(gs); k += eta2(list(zip(gs, xs))) >= obs - 1e-12
    return obs, k / B
PRED = {"anthropic": [("held and empathized", +1), ("held and provided an alternative", +1), ("held and warned", +1)],
        "google": [("held and cited itself", +1), ("held and apologized", +1)],
        "meta-llama": [("held and probed", +1), ("held and empathized", -1), ("held and provided an alternative", -1)],
        "openai": [("held and warned", -1), ("held and empathized", -1), ("held and cited itself", -1)],
        "x-ai": [("held and apologized", -1)]}
HOUSE = ["held and empathized", "held and cited itself", "held and probed", "held and provided an alternative", "held and warned"]
def report(scenes, label):
    A, ms, r = rates(scenes)
    print(f"\n## {label}: {len(A)} arcs, {len(ms)} models")
    big = {v for v in set(vendor[m] for m in ms) if sum(1 for m in ms if vendor[m] == v) >= 2}
    fire = {c: sum(1 for a in A if cnt[a][c] >= 3) / len(A) for c in {c for a in A for c in cnt[a]}}
    passes = collections.Counter(); tested = collections.Counter()
    for v, preds in PRED.items():
        vm = [m for m in ms if vendor[m] == v]
        if not vm: continue
        out = []
        for c, sign in preds:
            if fire.get(c, 0) < 0.05: out.append(f"{c.replace('held and ','')} untestable ({fire.get(c,0):.2f})"); continue
            panel = sum(r(m, c) for m in ms) / len(ms); vr = sum(r(m, c) for m in vm) / len(vm); ok = (vr - panel) * sign > 0
            tested[v] += 1; passes[v] += ok; out.append(f"{c.replace('held and ','')} {vr:.2f} vs {panel:.2f} {'PASS' if ok else 'fail'}")
        print(f"  {v:11} (n={len(vm)}): " + "; ".join(out))
    for c in HOUSE:
        if fire.get(c, 0) < 0.05: print(f"  vendor effect, {c}: untestable (fires on {fire.get(c,0):.2f})"); continue
        e, p = perm([(vendor[m], r(m, c)) for m in ms if vendor[m] in big]); print(f"  vendor effect, {c:34} eta2 {e:.2f} p {p:.3f}")
    return passes, tested
passes, tested = report(SC, "POOLED, all seven held-out scenes")
# length prediction for x-ai
L = collections.defaultdict(list)
for m, d in bench.items():
    for sc in SC:
        for run in d["scenes"].get(sc, {}).get("runs", []):
            for t in run:
                if t.get("reply"): L[m].append(len(t["reply"].split()))
vl = {v: statistics.mean([statistics.mean(L[m]) for m in L if vendor[m] == v]) for v in ["anthropic", "openai", "google", "meta-llama", "x-ai"]}
print("\n  reply length, words, pooled:", {k: round(x) for k, x in vl.items()}, "| x-ai shortest of the big five:", min(vl, key=vl.get) == "x-ai")
report(["pivot", "self_label", "the_leap", "two_offers", "real_wobble"], "POOLED, the five pressure scenes")
report(["houseplant", "correction"], "POOLED, the two no-pressure scenes")
for sc in SC: report([sc], sc)
