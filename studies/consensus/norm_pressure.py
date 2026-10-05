"""norm_pressure.py — do models move off a brand more when it is a widely shared norm?

Hypothesis (Tapan, 2026-10-05): the more models share a clamped brand, the more pressure a model feels to come off it
when the question changes, and that pressure may vary across model generations.

Unit: one model on one category. For each move from an origin step to a destination step, the outcome is whether the
model keeps its origin brand (its most common answer at the destination equals its most common answer at the origin).
A destination answer naming no brand is left out. Moves:
  the verb (clamped):  Name -> Choose, Name -> Recommend, Name -> two-turn pick
  the clamp:           Name -> free Name, Choose -> free Choose, Recommend -> free Recommend

Predictors, all leave-one-out over the other models:
  popularity      share of other models whose origin brand is the same brand
  pull            share of the other models that did NOT hold the brand at the origin and give it at the destination: how
                  much the destination question draws models to this brand, measured without its holders. (The share of
                  all other models giving it at the destination is the wrong control: it counts the other holders who
                  kept it, so at a fixed destination share a more popular origin brand must have lost more holders, and
                  a negative popularity effect follows from the arithmetic.)
  stability       share of the model's own origin runs that give its origin brand
  category        fixed effects, so models are compared within a category
The hypothesis predicts a negative popularity effect with the pull held fixed: a brand many models share is left more
than an equally attractive brand few models share. Generation: popularity x release date (years), and the same within lab family.

Logistic regression fitted by Newton's method, standard errors clustered by model. Effects are reported as the average
change in the probability of keeping per +10 points of popularity. A within-category permutation of popularity
(200 draws) gives a null for the popularity effect. Leaves out sonar and the company/brand categories (brand_ladder).
Zero API calls. Writes probes/norm_pressure.json.

    ../../.venv/bin/python norm_pressure.py
"""
import importlib.util
import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import brand_ladder as B  # noqa: E402

MOVES = [("verb", "Name -> Choose", "name", "choose"), ("verb", "Name -> Recommend", "name", "recommend_clamp"),
         ("verb", "Name -> two-turn pick", "name", "pick2"), ("clamp", "Name", "name", "free_name"),
         ("clamp", "Choose", "choose", "free_choose"), ("clamp", "Recommend", "recommend_clamp", "recommend")]
FAMILY = {e["label"]: e["family"] for e in json.loads((HERE / "spec/models.json").read_text())["models"]}
DRAWS = 200


def release_dates():
    spec = importlib.util.spec_from_file_location("viewbuild", HERE / "views" / "build.py")
    vb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vb)
    return vb.release_dates()


def modal(xs):
    xs = [x for x in xs if x != B.NO_PICK]
    return Counter(xs).most_common(1)[0][0] if xs else None


def rows(lv, a, b, cats):
    org = {m: {c: modal(xs) for c, xs in cs.items()} for m, cs in lv[a].items()}
    dst = {m: {c: modal(xs) for c, xs in cs.items()} for m, cs in lv[b].items()}
    out = []
    for c in cats:
        oh = [m for m in org if org[m].get(c)]
        dh = [m for m in dst if dst[m].get(c)]
        for m in oh:
            d, x = org[m][c], dst.get(m, {}).get(c)
            if x is None:
                continue
            others_o = [k for k in oh if k != m]
            non = [k for k in others_o if org[k][c] != d and dst.get(k, {}).get(c)]
            xs = [y for y in lv[a][m][c] if y != B.NO_PICK]
            out.append({"m": m, "c": c, "kept": int(x == d),
                        "pop": sum(org[k][c] == d for k in others_o) / len(others_o),
                        "pull": sum(dst[k][c] == d for k in non) / len(non) if non else 0.0,
                        "stab": sum(y == d for y in xs) / len(xs)})
    return out


def logit(X, y, groups, ridge):
    """Newton's method with a small ridge on the fixed effects (some categories keep every brand); returns the
    coefficients, the model-clustered covariance and the fitted probabilities."""
    beta = np.zeros(X.shape[1])
    R = np.diag(ridge)
    for _ in range(100):
        p = 1 / (1 + np.exp(-X @ beta))
        H = X.T @ (X * (p * (1 - p))[:, None]) + R
        step = np.linalg.solve(H, X.T @ (y - p) - R @ beta)
        beta += step
        if np.abs(step).max() < 1e-8:
            break
    p = 1 / (1 + np.exp(-X @ beta))
    Hi = np.linalg.inv(X.T @ (X * (p * (1 - p))[:, None]) + R)
    S = np.zeros((X.shape[1], X.shape[1]))
    for g in np.unique(groups):
        s = X[groups == g].T @ (y[groups == g] - p[groups == g])
        S += np.outer(s, s)
    G = len(np.unique(groups))
    return beta, Hi @ S @ Hi * G / (G - 1), p


def design(rs, terms, fe):
    """terms: list of (name, function of a row); fe: the row key for fixed effects (one dummy per level, no intercept)."""
    levels = sorted({r[fe] for r in rs})
    X = np.array([[f(r) for _, f in terms] + [float(r[fe] == L) for L in levels] for r in rs])
    ridge = np.array([0.0] * len(terms) + [1e-2] * len(levels))
    return X, ridge


def effect(rs, terms, fe="c"):
    X, ridge = design(rs, terms, fe)
    y = np.array([r["kept"] for r in rs], float)
    g = np.array([r["m"] for r in rs])
    beta, V, p = logit(X, y, g, ridge)
    w = (p * (1 - p)).mean()
    return {name: {"coef": float(beta[i]), "se": float(np.sqrt(V[i, i])),
                   "ame_per_10pts": float(w * beta[i] * 0.1)} for i, (name, _) in enumerate(terms)}


def permuted(rs, terms, draws, rng):
    """Null for the popularity coefficient: popularity shuffled among the models of each category."""
    by = {}
    for i, r in enumerate(rs):
        by.setdefault(r["c"], []).append(i)
    out = []
    for _ in range(draws):
        pops = np.array([r["pop"] for r in rs])
        for idx in by.values():
            pops[idx] = rng.permutation(pops[idx])
        out.append(effect([{**r, "pop": pops[i]} for i, r in enumerate(rs)], terms)["popularity"]["coef"])
    return np.array(out)


def main():
    rng = np.random.default_rng(0)
    lv = B.levels()
    cats = sorted({c for m in lv["name"] for c in lv["name"][m]} - B.GENERIC)
    rel = release_dates()
    years = lambda m: (date.fromisoformat(rel[m]) - date(2025, 1, 1)).days / 365.25
    base = [("popularity", lambda r: r["pop"]), ("pull", lambda r: r["pull"]), ("stability", lambda r: r["stab"])]
    out = []
    print(f"{'move':10} {'contrast':24} {'n':>5} {'kept':>5}   per +10 pts popularity (AME, keep probability)")
    print(f"{'':42}{'raw':>14} {'+controls':>22} {'perm p':>7}   {'x release yr':>14} {'within family':>14}")
    for kind, lab, a, b in MOVES:
        rs = rows(lv, a, b, cats)
        raw = effect(rs, base[:1])["popularity"]
        full = effect(rs, base)
        null = permuted(rs, base, DRAWS, rng)
        p_perm = float((np.abs(null) >= abs(full["popularity"]["coef"])).mean())
        dated = [r for r in rs if r["m"] in rel]
        for r in dated:
            r["yr"] = years(r["m"])
        mu = np.mean([r["yr"] for r in dated])
        gen_terms = base + [("release", lambda r: r["yr"] - mu), ("pop_x_release", lambda r: r["pop"] * (r["yr"] - mu))]
        gen = effect(dated, gen_terms)
        for r in dated:
            r["cf"] = r["c"] + "|" + FAMILY.get(r["m"], "?")
        fam = effect(dated, gen_terms, fe="cf")
        row = {"move": kind, "contrast": lab, "n": len(rs), "kept": float(np.mean([r["kept"] for r in rs])),
               "raw": raw, "controlled": full, "perm_p_popularity": p_perm,
               "generation": {"models_dated": len({r["m"] for r in dated}), "fit": gen},
               "within_family": fam}
        out.append(row)
        f = lambda e: f"{100 * e['ame_per_10pts']:+5.1f} ({e['coef'] / e['se']:+5.1f}z)"
        print(f"{kind:10} {lab:24} {len(rs):5} {row['kept']:5.0%}   {f(raw):>14} {f(full['popularity']):>22} {p_perm:7.3f}"
              f"   {gen['pop_x_release']['coef']:+6.2f} ({gen['pop_x_release']['coef'] / gen['pop_x_release']['se']:+4.1f}z)"
              f" {fam['pop_x_release']['coef']:+6.2f} ({fam['pop_x_release']['coef'] / fam['pop_x_release']['se']:+4.1f}z)")
        print(f"{'':42}controls: pull {f(full['pull'])}, stability {f(full['stability'])}")
    (HERE / "probes" / "norm_pressure.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
