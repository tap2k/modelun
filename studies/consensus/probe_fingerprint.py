"""probe_fingerprint.py — can a model be identified from its one-word answers alone?

Each panel model's answers to the 96 census + expanded categories (8 per category: transcripts/ + transcripts-extra/,
and transcripts-expanded/) form its profile. A test set is one or two held-out answers per question for a random
set of k questions; it is assigned to the model whose profile gives it the highest likelihood (per-category answer
counts, add-0.1 smoothed over the category's whole vocabulary). Four-fold: samples {0,1}, {2,3}, {4,5}, {6,7} are
held out in turn and the profile is built from the other six, so every answer is used and none is scored against
itself. Reported: exact-model and family accuracy by number of questions and answers per question. Closed set:
it picks among profiled models, so a new model can only be matched to its nearest profiled relative.

    ../../.venv/bin/python probe_fingerprint.py           # -> probes/fingerprint.json
    ../../.venv/bin/python probe_fingerprint.py --subset  # greedy best question set, added to the same file
"""
import json, math, random, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from analyze import answers, against, load

KS = (1, 3, 5, 10, 20, 40, 96)
FOLDS = ((0, 1), (2, 3), (4, 5), (6, 7))


def panel():
    core = answers(HERE)
    extra = against(core, load(HERE, "census", paths=sorted((HERE / "transcripts-extra").glob("*.json"))), HERE)
    exp = answers(HERE, "expanded")
    A = {m: {**{c: core[m][c] + extra[m].get(c, []) for c in core[m]}, **exp[m]} for m in core if m in extra and m in exp}
    models = sorted(m for m in A if sum(len(v) >= 8 for v in A[m].values()) >= 90)
    return {m: A[m] for m in models}


def accuracy(A, fam, k, per_q, trials, rng):
    models, cats = sorted(A), sorted({c for m in A for c in A[m]})
    vocab = {c: len({a for m in models for a in A[m].get(c, [])}) + 1 for c in cats}
    hit = fhit = n = 0
    for _ in range(trials):
        cs = rng.sample(cats, k)
        for held in FOLDS:
            prof = {m: {c: Counter(a for i, a in enumerate(A[m].get(c, [])[:8]) if i not in held) for c in cs} for m in models}
            for true in models:
                obs = [(c, A[true][c][i]) for c in cs for i in held[:per_q] if i < len(A[true].get(c, []))]
                score = lambda m: sum(math.log((prof[m][c][a] + 0.1) / (sum(prof[m][c].values()) + 0.1 * vocab[c])) for c, a in obs)
                best = max(models, key=score)
                hit += best == true; fhit += fam.get(best) == fam.get(true); n += 1
    return round(hit / n, 3), round(fhit / n, 3)


def main():
    A = panel()
    fam = {r["label"]: r.get("family") for r in json.loads((HERE / "spec" / "models.json").read_text())["models"]}
    rng = random.Random(0)
    res = {"models": len(A), "chance": round(1 / len(A), 4), "by_questions": {}}
    for per_q in (1, 2):
        for k in KS:
            exact, family = accuracy(A, fam, k, per_q, trials=10 if k < 96 else 1, rng=rng)
            res["by_questions"][f"{k}q_x{per_q}"] = {"exact": exact, "family": family}
            print(f"{k:3d} questions x {per_q} answer(s): exact {exact:.0%}, family {family:.0%}")
    (HERE / "probes" / "fingerprint.json").write_text(json.dumps(res, indent=1) + "\n")


if __name__ == "__main__" and "--subset" not in sys.argv:
    main()


def best_subset(A, fam, size=25, select_folds=FOLDS[:2], eval_folds=FOLDS[2:]):
    """Greedy forward selection of questions for identification with two answers per question. Questions are
    chosen on select_folds (mean log-probability of the true model, softmax over models) and scored on
    eval_folds, whose answers played no part in the choice."""
    import numpy as np
    models, cats = sorted(A), sorted({c for m in A for c in A[m] if all(len(A[x].get(c, [])) >= 8 for x in A)})
    vocab = {c: len({a for m in models for a in A[m][c]}) + 1 for c in cats}

    def ll(folds):   # [fold, true, cand, cat]: log-likelihood of true's two held-out answers under cand's profile
        out = np.zeros((len(folds), len(models), len(models), len(cats)))
        for f, held in enumerate(folds):
            for j, c in enumerate(cats):
                prof = [Counter(a for i, a in enumerate(A[m][c][:8]) if i not in held) for m in models]
                for t, true in enumerate(models):
                    obs = [A[true][c][i] for i in held]
                    out[f, t, :, j] = [sum(math.log((p[a] + 0.1) / (6 + 0.1 * vocab[c])) for a in obs) for p in prof]
        return out

    S, E = ll(select_folds), ll(eval_folds)
    idx = np.arange(len(models))
    acc = lambda M, cols: float((M[..., cols].sum(-1).argmax(-1) == idx).mean())
    chosen, cur, trace = [], np.zeros(S.shape[:3]), []
    for _ in range(size):
        best, best_obj = None, -1e18
        for j in range(len(cats)):
            if j in chosen:
                continue
            tot = cur + S[..., j]
            obj = (tot[:, idx, idx] - np.log(np.exp(tot - tot.max(-1, keepdims=True)).sum(-1)) - tot.max(-1)).mean()
            if obj > best_obj:
                best, best_obj = j, obj
        chosen.append(best); cur += S[..., best]
        trace.append({"k": len(chosen), "question": cats[best], "eval_exact": round(acc(E, chosen), 3)})
    rng = random.Random(1)
    rand = {k: round(float(np.mean([acc(E, rng.sample(range(len(cats)), k)) for _ in range(30)])), 3) for k in (5, 10, 15, 20, 25)}
    return trace, rand


if __name__ == "__main__" and "--subset" in sys.argv:
    A = panel()
    trace, rand = best_subset(A, None)
    for t in trace:
        print(f"{t['k']:2d} +{t['question']:18s} chosen-set accuracy {t['eval_exact']:.0%}" + (f"   random {t['k']}-set {rand[t['k']]:.0%}" if t['k'] in rand else ""))
    res = json.loads((HERE / "probes" / "fingerprint.json").read_text())
    res["best_subset_x2"] = {"selected_on": "folds {0,1},{2,3}", "scored_on": "folds {4,5},{6,7}", "greedy": trace, "random_mean": rand}
    (HERE / "probes" / "fingerprint.json").write_text(json.dumps(res, indent=1) + "\n")
