"""traits.py — is suggestibility one trait? Correlations across models between the study's measures.

Reads the per-model outputs the probes already write and reports Spearman correlations with a
permutation p (5,000 shuffles):

  tag effect, personal items (probes/righteffect_analysis.json)  vs  tag effect, contested items
  stance effect, personal items (probe_ablation)                  vs  belief effect, contested items
  tag effect vs belief effect, both on the contested items
  stance effect vs tag effect, both on the personal items
  tag effect, first collection vs retest (the reliability ceiling, probes/retest_analysis.json)

Run probe_righteffect, probe_ablation, probe_contested and probe_retest analyze first.

    python studies/suggestibility/traits.py        # writes probes/traits_analysis.json
"""
import json
from pathlib import Path
import numpy as np
import probe_ablation

STUDY = Path(__file__).resolve().parent
rng = np.random.default_rng(7)


def rank(a):
    a = np.asarray(a, float); r = np.empty(len(a)); r[a.argsort()] = np.arange(len(a))
    for v in np.unique(a):
        r[a == v] = r[a == v].mean()
    return r


def spearman(x, y, n=5000):
    rx, ry = rank(x), rank(y); rho = np.corrcoef(rx, ry)[0, 1]
    perm = np.array([np.corrcoef(rx, rng.permutation(ry))[0, 1] for _ in range(n)])
    return float(rho), float((np.sum(np.abs(perm) >= abs(rho)) + 1) / (n + 1))


def stance_effects():
    """STANCEeff per model, computed the way probe_ablation.analyze does (stance arm minus ask)."""
    return {m: v["stanceeff"] for m, v in probe_ablation.effects().items()}


def main():
    core = json.loads((STUDY / "probes" / "righteffect_analysis.json").read_text())["per_model"]
    con = json.loads((STUDY / "probes" / "contested_analysis.json").read_text())["per_model"]
    rt = json.loads((STUDY / "probes" / "retest_analysis.json").read_text())["per_model"]
    stance = stance_effects()
    m = {
        "tag_personal": {k: v["tageff"] for k, v in core.items()},
        "tag_contested": {k: v["tageff"] for k, v in con.items()},
        "belief_contested": {k: v["beliefeff"] for k, v in con.items()},
        "stance_personal": stance,
        "tag_personal_retest": {k: v["tageff_retest"] for k, v in rt.items()},
        "tag_personal_orig": {k: v["tageff_orig"] for k, v in rt.items()},
    }
    pairs = [("tag_personal", "tag_contested"), ("stance_personal", "belief_contested"),
             ("tag_contested", "belief_contested"), ("stance_personal", "tag_personal"),
             ("tag_personal_orig", "tag_personal_retest")]
    out = {}
    for a, b in pairs:
        ms = [k for k in m[a] if k in m[b] and m[a][k] is not None and m[b][k] is not None]
        rho, p = spearman([m[a][k] for k in ms], [m[b][k] for k in ms])
        out[f"{a}__vs__{b}"] = {"n": len(ms), "rho": rho, "p": p}
        print(f"{a:20} vs {b:20} n={len(ms):2}  rho={rho:+.2f}  p={p:.4f}")
    (STUDY / "probes" / "traits_analysis.json").write_text(json.dumps(out, indent=1))
    print("-> probes/traits_analysis.json")


if __name__ == "__main__":
    main()
