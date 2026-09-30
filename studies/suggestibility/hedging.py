"""hedging.py — hedging as a model's own disposition, read from the suggestibility study's outputs.

A hedge is a reply that is neither a leading Yes nor a leading No under the Yes/No clamp (analyze.classify).
Three readings, all from files this study already writes:

  1. Stability: per-model hedge rate on the contested probe's plain questions against the plant-arm
     hedge rate on the core personal-choice items (analysis.json). Spearman, permutation p.
  2. Vendor: contested hedge rate grouped by the roster slug's vendor (vendors with >= 3 models),
     Kruskal-Wallis H with a permutation p and an epsilon-squared effect size.
  3. Decomposition: how each contested arm moves Yes, No and hedge against the plain question
     (the d_* fields of probes/contested_analysis.json; run probe_contested.py analyze first), and
     for models whose Yes falls under the tag, whether they resist with a No or by declining.

Correlations with the other studies and with capability and release date are cross-instrument
questions and live in ../cross-instrument/.

    python studies/suggestibility/hedging.py        # writes probes/hedging_analysis.json
"""
import collections, json
from pathlib import Path
import numpy as np

STUDY = Path(__file__).resolve().parent
rng = np.random.default_rng(7)
N = 5000


def rank(a):
    a = np.asarray(a, float); r = np.empty(len(a)); r[a.argsort()] = np.arange(len(a))
    for v in np.unique(a):
        r[a == v] = r[a == v].mean()
    return r


def spearman(x, y):
    rx, ry = rank(x), rank(y); rho = np.corrcoef(rx, ry)[0, 1]
    perm = np.array([np.corrcoef(rx, rng.permutation(ry))[0, 1] for _ in range(N)])
    return float(rho), float((np.sum(np.abs(perm) >= abs(rho)) + 1) / (N + 1))


def kruskal(groups):
    vals = np.concatenate(groups); r = rank(vals); n = len(vals); sizes = [len(g) for g in groups]
    def H(rr):
        out, i = 0.0, 0
        for s in sizes:
            out += rr[i:i + s].sum() ** 2 / s; i += s
        return 12 / (n * (n + 1)) * out - 3 * (n + 1)
    h = H(r); perm = np.array([H(rng.permutation(r)) for _ in range(N)])
    return float(h), float((np.sum(perm >= h) + 1) / (N + 1)), float((h - len(groups) + 1) / (n - len(groups)))


def main():
    core = json.loads((STUDY / "analysis.json").read_text())["per_model"]
    cont = json.loads((STUDY / "probes" / "contested_analysis.json").read_text())["per_model"]
    slugs = [l.strip() for l in (STUDY / "spec" / "models.txt").read_text().splitlines() if l.strip() and not l.startswith("#")]
    vendor = {s.split("/")[-1]: s.split("/")[0] for s in slugs}
    out = {}

    ms = [m for m in cont if m in core]
    rho, p = spearman([cont[m]["hedge_ask"] for m in ms], [core[m]["plant_hedge"] for m in ms])
    out["stability"] = {"n": len(ms), "rho": rho, "p": p}
    print(f"contested hedge (question) vs core-item hedge (plant): n={len(ms)} rho={rho:+.2f} p={p:.4f}")

    for key, label in (("hedge_ask", "plain questions"), ("hedge_ask_hot", "partisan plain questions")):
        g = collections.defaultdict(list)
        for m, v in cont.items():
            if v.get(key) is not None and m in vendor:
                g[vendor[m]].append(v[key])
        big = {k: v for k, v in g.items() if len(v) >= 3}
        h, p, eps = kruskal(list(big.values()))
        means = {k: float(np.mean(v)) for k, v in sorted(big.items(), key=lambda kv: -np.mean(kv[1]))}
        out[f"vendor_{key}"] = {"vendors": len(big), "n": sum(map(len, big.values())), "H": h, "p": p,
                                "epsilon2": eps, "mean_by_vendor": means, "n_by_vendor": {k: len(v) for k, v in big.items()}}
        print(f"vendor, {label}: {len(big)} vendors, n={out[f'vendor_{key}']['n']}, H={h:.1f}, p={p:.4f}, eps2={eps:.2f}")
        print("   " + ", ".join(f"{k} {v:.0%}({len(big[k])})" for k, v in means.items()))

    arms = ("tag", "bare", "belief")
    dec = {a: {o: float(np.mean([v[f"d_{o}_{a}"] for v in cont.values() if v.get(f"d_{o}_{a}") is not None]))
               for o in ("affirm", "reject", "hedge")} for a in arms}
    out["decomposition_panel_mean"] = dec
    for a in arms:
        print(f"{a:7} dYes {dec[a]['affirm']:+.1%}  dNo {dec[a]['reject']:+.1%}  dHedge {dec[a]['hedge']:+.1%}")
    resisters = {m: ("No" if v["d_reject_tag"] >= v["d_hedge_tag"] else "declining")
                 for m, v in cont.items() if v["d_affirm_tag"] <= -0.05}
    out["tag_resistance_via"] = resisters
    c = collections.Counter(resisters.values())
    print(f"models whose Yes falls >= 5 points under the tag: {len(resisters)} ({c['No']} with a No, {c['declining']} by declining)")

    (STUDY / "probes" / "hedging_analysis.json").write_text(json.dumps(out, indent=1))
    print("-> probes/hedging_analysis.json")


if __name__ == "__main__":
    main()
