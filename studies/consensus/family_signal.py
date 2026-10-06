"""family_signal.py — do same-family models share off-modal answers beyond what their depth propensity predicts?
(paper §4.6, "Family resemblance survives the propensities")

Similarity s(A,B) = sum over categories of rarity-weighted matches between A's and B's off-modal run answers
(fraction of run pairs equal, weight -log2 field share of the word). D = mean within-family s - mean
between-family s, over families with >= 2 models. Nearest-neighbour recovery: is a model's most similar model
in its family?

Depth null: keep every run's field-rank band (modal / rank 2-3 / rank >= 4) and redraw the off-modal word from
the field's answers in that band, weighted by field counts. It keeps each model's avoidance and depth
propensity and breaks which word it chose.

Vectorised port of the private lineage/scripts/family_signal.py (same statistic, same null).
    ../../.venv/bin/python family_signal.py          # v2: the 44 models of consensus-arxiv-v2, census, 4 runs
    ../../.venv/bin/python family_signal.py --v3     # v3 field (census + expanded, 8 runs) -> probes/family_signal_v3.json
"""
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from analyze import answers, load  # noqa: E402

V3 = "--v3" in sys.argv
R = 1000
rng = np.random.default_rng(0)

if V3:
    ans = answers(HERE, "combined")
else:   # as published: the v2 panel from its tag, scored with load()
    v2 = {Path(p).stem for p in subprocess.run(["git", "ls-tree", "--name-only", "consensus-arxiv-v2", "transcripts/"],
                                               cwd=HERE, capture_output=True, text=True, check=True).stdout.split()}
    ans = {m: a for m, a in load(HERE).items() if m in v2}
ans = {m: a for m, a in ans.items() if a}
fam = {e["label"]: e["family"] for e in json.loads((HERE / "spec/models.json").read_text())["models"]}
models = sorted(ans)
cats = sorted({c for m in models for c in ans[m]})
famv = np.array([fam[m] for m in models])
sizes = Counter(famv)

# per category: vocabulary, field rank band, weight, and each model's runs as vocab indices
CAT = []
for c in cats:
    field = Counter(w for m in models for w in ans[m].get(c, []))
    vocab = [w for w, _ in field.most_common()]
    idx = {w: i for i, w in enumerate(vocab)}
    counts = np.array([field[w] for w in vocab], float)
    weight = -np.log2(counts / counts.sum())
    band = np.array([0] + [1 if r <= 3 else 2 for r in range(2, len(vocab) + 1)])
    runs = [np.array([idx[w] for w in ans[m].get(c, [])], int) for m in models]
    pools = {b: (np.flatnonzero(band == b), counts[band == b] / counts[band == b].sum()) for b in (1, 2) if (band == b).any()}
    CAT.append((len(vocab), weight, band, runs, pools))


def sim_matrix(runs_by_cat):
    S = np.zeros((len(models), len(models)))
    for (V, weight, band, _, _), runs in zip(CAT, runs_by_cat):
        X = np.zeros((len(models), V))
        for i, r in enumerate(runs):
            if len(r):
                np.add.at(X[i], r, 1.0 / len(r))
        X[:, 0] = 0.0                                        # the modal answer never counts
        S += (X * weight) @ X.T
    np.fill_diagonal(S, 0.0)
    return S


def resample():
    out = []
    for V, weight, band, runs, pools in CAT:
        new = []
        for r in runs:
            r = r.copy()
            for b, (cand, p) in pools.items():
                sel = band[r] == b
                if sel.any():
                    r[sel] = rng.choice(cand, size=sel.sum(), p=p)
            new.append(r)
        out.append(new)
    return out


keep = np.array([sizes[f] >= 2 for f in famv])
same = famv[:, None] == famv[None, :]
iu = np.triu_indices(len(models), 1)
kk = (keep[:, None] & keep[None, :])[iu]


def stat(S):
    s, w = S[iu][kk], same[iu][kk]
    return s[w].mean() - s[~w].mean()


def nn(S):
    S = S.copy(); np.fill_diagonal(S, -np.inf)
    best = S.argmax(1)
    return int(sum(famv[best[i]] == famv[i] for i in range(len(models)) if keep[i])), int(keep.sum())


S = sim_matrix([r for _, _, _, r, _ in CAT])
D, (hits, n) = stat(S), nn(S)
null_D, null_nn = [], []
for _ in range(R):
    Sr = sim_matrix(resample())
    null_D.append(stat(Sr)); null_nn.append(nn(Sr)[0])
null_D, null_nn = np.array(null_D), np.array(null_nn)
p = lambda obs, null: float((1 + (null >= obs).sum()) / (1 + len(null)))
within = S[iu][kk][same[iu][kk]].mean()
res = {"field": f"{len(models)} models x {len(cats)} categories", "draws": R,
       "D": round(float(D), 3), "within_mean": round(float(within), 3),
       "depth_null_D": [round(float(null_D.mean()), 3), round(float(null_D.std()), 3)],
       "z_D": round(float((D - null_D.mean()) / null_D.std()), 1), "p_D": p(D, null_D),
       "nn_hits": hits, "nn_n": n, "depth_null_nn": [round(float(null_nn.mean()), 1), round(float(null_nn.std()), 1)],
       "p_nn": p(hits, null_nn),
       "label_chance_nn": round(sum((sizes[famv[i]] - 1) / (len(models) - 1) for i in range(len(models)) if keep[i]), 1)}
print(json.dumps(res, indent=1))
if V3:
    (HERE / "probes" / "family_signal_v3.json").write_text(json.dumps(res, indent=1) + "\n")
    print("-> probes/family_signal_v3.json")
