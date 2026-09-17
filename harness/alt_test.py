#!/usr/bin/env python3
"""Alternative Annotator Test (Calderon, Reichart, Dror, ACL 2025, arXiv:2501.10970) on the
held-out fifty, manner codes under one codebook version.

Leave one human out. On each arc that human coded, score the machine coder and the left-out human
by their alignment with the remaining humans. The machine wins the arc when its score is at least
the human's; the human wins when its score is at least the machine's. A one-sample t-test asks
whether the human's advantage (human wins minus machine wins) is below epsilon. The p-values over
the left-out humans are corrected by Benjamini-Yekutieli at q. Winning rate is the share of humans
whose null is rejected (pass at 0.5 or above); advantage probability is the machine's mean win rate.

Instances are arcs. A label is the set of manner codes present on the arc (empty set allowed).
Alignment is the Jaccard similarity of two code sets, 1 when both are empty; per-code accuracy
over the codebook's codes is reported as a sensitivity check.

Two references. Raw: each human's marks as made (adjudication additions left out, ruled-out marks
kept). Adjudicated: accepted additions in, ruled-out marks out.

Stdlib only; the t distribution is computed from the regularized incomplete beta function.
`--validate DIR` runs the discrete and continuous datasets shipped with the authors' code
(github.com/nitaytech/AltTest, data/) with their epsilons, to check this implementation.

    python harness/alt_test.py --study studies/conduct --version v2
    python harness/alt_test.py --validate path/to/AltTest/data
"""
import argparse, collections, glob, json, math
from pathlib import Path

# ---- t distribution, stdlib -------------------------------------------------------------------
def _betacf(a, b, x):
    qab, qap, qam = a + b, a + 1, a - 1; c, d = 1.0, 1 - qab * x / qap
    d = 1 / (d if abs(d) > 1e-300 else 1e-300); h = d
    for m in range(1, 300):
        m2 = 2 * m; aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1 + aa * d; d = 1 / (d if abs(d) > 1e-300 else 1e-300); c = 1 + aa / c if abs(1 + aa / c) > 1e-300 else 1e-300; h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1 + aa * d; d = 1 / (d if abs(d) > 1e-300 else 1e-300); c = 1 + aa / c if abs(1 + aa / c) > 1e-300 else 1e-300; de = d * c; h *= de
        if abs(de - 1) < 1e-14: break
    return h

def betainc(a, b, x):
    if x <= 0: return 0.0
    if x >= 1: return 1.0
    lb = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    if x < (a + 1) / (a + b + 2): return math.exp(lb) * _betacf(a, b, x) / a
    return 1 - math.exp(lb) * _betacf(b, a, 1 - x) / b

def t_cdf(t, df):
    tail = 0.5 * betainc(df / 2, 0.5, df / (df + t * t))
    return tail if t < 0 else 1 - tail

def ttest_less(xs, mu):
    """One-sample t-test, H1: mean < mu. Zero variance: p is 0 if the mean is below mu, else 1."""
    n = len(xs); m = sum(xs) / n; var = sum((x - m) ** 2 for x in xs) / (n - 1)
    if var == 0: return 0.0 if m < mu else 1.0
    return t_cdf((m - mu) / math.sqrt(var / n), n - 1)

def by_rejected(ps, q):
    m = len(ps); hm = sum(1 / i for i in range(1, m + 1)); order = sorted(range(m), key=lambda i: ps[i]); k = -1
    for r, i in enumerate(order):
        if ps[i] <= (r + 1) / m * q / hm: k = r
    return set(order[:k + 1])

# ---- the test ---------------------------------------------------------------------------------
def alt_test(llm, humans, score, epsilon, q=0.05, min_humans=2, min_instances=30):
    per = {}
    who = collections.defaultdict(list)
    for h, anns in humans.items():
        for i in anns: who[i].append(h)
    keep = {i for i in who if len(who[i]) >= min_humans and i in llm}
    ps, adv, names = [], [], []
    for h, anns in humans.items():
        inst = [i for i in anns if i in keep]
        if len(inst) < min_instances: continue
        lw, hw = [], []
        for i in inst:
            rest = [humans[o][i] for o in who[i] if o != h]
            hs, ls = score(anns[i], rest), score(llm[i], rest)
            lw.append(1 if ls >= hs else 0); hw.append(1 if hs >= ls else 0)
        ps.append(ttest_less([a - b for a, b in zip(hw, lw)], epsilon)); adv.append(sum(lw) / len(lw)); names.append(h)
        per[h] = {"n": len(inst), "machine_wins": sum(lw) / len(lw), "human_wins": sum(hw) / len(hw)}
    rej = by_rejected(ps, q)
    for k, h in enumerate(names): per[h].update(p=ps[k], rejected=k in rej)
    return len(rej) / len(names), sum(adv) / len(adv), per

def mean_over(f):
    return lambda pred, anns: sum(f(pred, a) for a in anns) / len(anns)

def jaccard(a, b):
    return 1.0 if not a and not b else len(a & b) / len(a | b)

# ---- validation against the authors' shipped datasets -----------------------------------------
def validate(d):
    sets = {"wax": ("acc", .1), "lgbteen": ("acc", .2), "mtbench": ("acc", .2), "framing": ("acc", .15), "cebab_aspects": ("acc", .1),
            "summeval": ("rmse", .2), "10k_prompts": ("rmse", .15), "cebab_stars": ("rmse", .1), "lesion": ("rmse", .15)}
    fns = {"acc": mean_over(lambda p, a: float(p == a)), "rmse": lambda p, anns: -math.sqrt(sum((p - a) ** 2 for a in anns) / len(anns))}
    for name, (fn, eps) in sets.items():
        H = json.load(open(Path(d) / name / "human_annotations.json")); L = json.load(open(Path(d) / name / "llm_annotations.json"))
        for llm, ann in L.items():
            wr, ap, _ = alt_test(ann, H, fns[fn], eps)
            print(f"{name} {llm} [{'PASSED' if wr >= 0.5 else 'FAILED'}]:\tWinning Rate={wr:.2f}\tAdvantage Probability={ap:.2f}")

# ---- the conduct data --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--study", default="studies/conduct"); ap.add_argument("--version", default="v2")
    ap.add_argument("--humans", default="Tap,Jay,Liam"); ap.add_argument("--epsilon", type=float, default=0.1)
    ap.add_argument("--sensitivity", default="0.15,0.2"); ap.add_argument("--q", type=float, default=0.05)
    ap.add_argument("--validate")
    a = ap.parse_args()
    if a.validate: return validate(a.validate)
    cod = Path(a.study) / "data/coding"
    def human(name, adjudicated):
        rows = [json.loads(l) for l in open(cod / f"manner_{a.version}.{name}.jsonl") if l.strip()]
        out = {r["arc"]: set() for r in rows}
        for r in rows:
            if r.get("kind") != "code": continue
            if adjudicated and r.get("rejected"): continue
            if not adjudicated and r.get("adjudicated"): continue
            out[r["arc"]].add(r["code"])
        return {k: frozenset(v) for k, v in out.items()}
    arcs = set.intersection(*[set(human(h, False)) for h in a.humans.split(",")])
    machines = {}
    for f in sorted(glob.glob(str(cod / f"relabel_{a.version}.llm-*.jsonl"))):
        name = Path(f).name[len(f"relabel_{a.version}.llm-"):-6]; m = {}
        for r in map(json.loads, open(f)):
            if r["arc"] in arcs: m.setdefault(r["arc"], set()); m[r["arc"]].add(r["code"]) if r["kind"] == "code" else None
        machines[name] = {k: frozenset(v) for k, v in m.items()}
    maj = {}
    for arc in arcs:
        c = collections.Counter(x for m in machines.values() for x in m.get(arc, ()))
        maj[arc] = frozenset(x for x, n in c.items() if n >= 3)
    machines["majority of six (3+)"] = maj
    codes = sorted({x for m in machines.values() for v in m.values() for x in v} |
                   {x for h in a.humans.split(",") for adj in (False, True) for v in human(h, adj).values() for x in v})
    scores = {"jaccard": mean_over(jaccard), "per-code accuracy": mean_over(lambda p, q: 1 - len(p ^ q) / len(codes))}
    epsilons = [a.epsilon] + [float(x) for x in a.sensitivity.split(",") if x]
    print(f"arcs {len(arcs)}; humans {a.humans}; codes in use {len(codes)}; BY q={a.q}; machine coverage " +
          ", ".join(f"{k.split('_')[-1]} {len(v)}" for k, v in machines.items() if not k.startswith("majority")))
    for ref in ("raw", "adjudicated"):
        H = {h: {k: v for k, v in human(h, ref == "adjudicated").items() if k in arcs} for h in a.humans.split(",")}
        for sname, sf in scores.items():
            print(f"\n## reference: {ref}; alignment: {sname}")
            print(f"{'machine coder':<30}" + "".join(f"{'eps '+str(e):>12}" for e in epsilons) + f"{'adv prob':>10}   per human: machine wins / human wins / p (eps {a.epsilon})")
            for name, m in machines.items():
                res = [alt_test(m, H, sf, e, a.q) for e in epsilons]
                per = res[0][2]
                detail = "  ".join(f"{h} {v['machine_wins']:.2f}/{v['human_wins']:.2f}/{v['p']:.3f}{'*' if v['rejected'] else ''}" for h, v in per.items())
                print(f"{name:<30}" + "".join(f"{r[0]:>12.2f}" for r in res) + f"{res[0][1]:>10.2f}   {detail}")

if __name__ == "__main__":
    main()
