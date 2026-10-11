"""probe_fingerprint_baselines.py — the §3 likelihood against simpler scorers on the same panel, folds and budgets.

Same four folds as probe_fingerprint.py: samples {0,1}, {2,3}, {4,5}, {6,7} held out in turn, profiles from the other
six. Questions are the ones every panel model answered at least eight times, so every profile has six samples and
the comparison is like for like. Scorers, each picking the best of the 94 profiles:

  likelihood a   the §3 score with pseudocount a (0.01, 0.1, 0.5, 1); a = 0.1 is the paper's
  jsd            nearest neighbour by mean Jensen-Shannon distance between the held-out answers and each profile
  modal          count of held-out answers equal to the profile's most common answer, ties broken at random

Each cell is the mean exact-model accuracy over 20 random question draws, with the standard deviation and range
across draws (each draw pools the four folds and all 94 models).

    ../../.venv/bin/python probe_fingerprint_baselines.py   # -> probes/fingerprint_baselines.json
"""
import json, math, random, sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from probe_fingerprint import FOLDS, panel

KS, DRAWS, ALPHAS = (10, 20, 40), 20, (0.01, 0.1, 0.5, 1.0)


def jsd(p, q):
    m = {a: (p.get(a, 0) + q.get(a, 0)) / 2 for a in set(p) | set(q)}
    kl = lambda x: sum(v * math.log2(v / m[a]) for a, v in x.items() if v)
    return math.sqrt(max(0.0, (kl(p) + kl(q)) / 2))


def tables(A, models, cats, per_q):
    """[scorer] -> [fold, true, cand, cat] array; higher is better for every scorer."""
    vocab = {c: len({a for m in models for a in A[m][c][:8]}) + 1 for c in cats}
    shape = (len(FOLDS), len(models), len(models), len(cats))
    out = {f"likelihood {a}": np.zeros(shape) for a in ALPHAS}
    out["jsd"], out["modal"] = np.zeros(shape), np.zeros(shape)
    for f, held in enumerate(FOLDS):
        for j, c in enumerate(cats):
            prof = [Counter(a for i, a in enumerate(A[m][c][:8]) if i not in held) for m in models]
            dist = [{a: n / 6 for a, n in p.items()} for p in prof]
            mode = [p.most_common(1)[0][0] for p in prof]
            for t, true in enumerate(models):
                obs = [A[true][c][i] for i in held[:per_q]]
                od = {a: n / len(obs) for a, n in Counter(obs).items()}
                for a in ALPHAS:
                    out[f"likelihood {a}"][f, t, :, j] = [sum(math.log((p[x] + a) / (6 + a * vocab[c])) for x in obs) for p in prof]
                out["jsd"][f, t, :, j] = [-jsd(od, d) for d in dist]
                out["modal"][f, t, :, j] = [sum(x == mo for x in obs) for mo in mode]
    return out


def main():
    A = panel()
    models = sorted(A)
    cats = sorted(c for c in {c for m in A for c in A[m]} if all(len(A[m].get(c, [])) >= 8 for m in models))
    idx = np.arange(len(models))
    rng = random.Random(0)
    draws = {k: [rng.sample(range(len(cats)), k) for _ in range(DRAWS)] for k in KS}
    tie = np.random.default_rng(0).random((len(FOLDS), len(models), len(models))) * 1e-6
    res = {"models": len(models), "questions": len(cats), "draws": DRAWS, "results": {}}
    for per_q in (1, 2):
        T = tables(A, models, cats, per_q)
        for name, M in T.items():
            for k in KS:
                accs = [float(((M[..., cols].mean(-1) if name == "jsd" else M[..., cols].sum(-1)) + tie).argmax(-1).__eq__(idx).mean())
                        for cols in draws[k]]
                key = f"{k}q_x{per_q}"
                res["results"].setdefault(key, {})[name] = {"mean": round(float(np.mean(accs)), 3), "sd": round(float(np.std(accs)), 3),
                                                            "min": round(min(accs), 3), "max": round(max(accs), 3)}
                print(f"{key:7s} {name:16s} {np.mean(accs):.1%} (sd {np.std(accs):.1%}, {min(accs):.0%}-{max(accs):.0%})")
    (HERE / "probes" / "fingerprint_baselines.json").write_text(json.dumps(res, indent=1) + "\n")


if __name__ == "__main__":
    main()
