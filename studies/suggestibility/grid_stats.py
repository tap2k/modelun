"""grid_stats.py — the paper's core grid: three wordings by three cues on the 20 decision items.

  wording     neutral                         right?                               maybe?
  original    Is X the better choice?         X is the better choice, right?       X is the better choice, maybe?
  named       D: X or Y. Is X the better...   D: X or Y. X is the better..., right?  ..., maybe?
  should      Should I go with X?             I should go with X, right?           I should go with X, maybe?

Sources: original = transcripts/ (neutral), probes/righteffect/ (right?), probes/maybetag/ (maybe?);
named = probes/named_panel/; should = probe_should_panel.load() (probes/maybe + probes/should for the
first 70 models, probes/should_panel/ for the rest).

Per model and wording: the tag effect (right? - neutral) and the confidence gap (maybe? - right?),
each with v2_stats' nested bootstrap (items, then replies), 95% intervals, BH at q = .05 within the
wording. Per wording: the within-family release-order test (lineage.FAM; mean within-family Spearman
weighted by family size, release order permuted within family). Writes probes/grid_stats.json and
paper/gen/grid_stats.json, paper/gen/grid_table.tex.

    python studies/suggestibility/grid_stats.py
    python studies/suggestibility/grid_stats.py --slope   # split-half check of the baseline slope
"""
import json
from pathlib import Path
import numpy as np
import v2_stats as vs
import probe_should_panel as sp
from probe_righteffect import ITEMS
from lineage import FAM, EXTRA

STUDY = Path(__file__).resolve().parent
GEN = STUDY / "paper" / "gen"
WORDINGS = ("original", "named", "should")


def side_cells(get):
    """{item: {x: [...], y: [...]}} from get(item, side) -> replies."""
    return {sid: {s: get(sid, s) for s in "xy"} for sid, *_ in ITEMS}


def load():
    """wording -> model -> {neutral, right, maybe: {item: {x, y}}}."""
    out = {w: {} for w in WORDINGS}
    tx = {p.stem: json.loads(p.read_text())["scenes"] for p in (STUDY / "transcripts").glob("*.json")}
    for p in (STUDY / "probes" / "righteffect").glob("*.json"):
        m, mp = p.stem, STUDY / "probes" / "maybetag" / p.name
        if m not in tx or not mp.exists():
            continue
        r, mb = json.loads(p.read_text())["tag"], json.loads(mp.read_text())["tag"]
        out["original"][m] = {
            "neutral": side_cells(lambda i, s: [run[0].get("reply") for run in tx[m].get(f"{i}__ask{s}", {}).get("runs", []) if run]),
            "right": side_cells(lambda i, s: r.get(i, {}).get(s, [])),
            "maybe": side_cells(lambda i, s: mb.get(i, {}).get(s, []))}
    for p in (STUDY / "probes" / "named_panel").glob("*.json"):
        a = json.loads(p.read_text())["arms"]
        out["named"][p.stem] = {"neutral": a["named_ask"], "right": a["named_tag"], "maybe": a["named_maybe"]}
    for m, a in sp.load().items():
        out["should"][m] = {"neutral": a["should"], "right": a["confident"], "maybe": a["tentative"]}
    return out


def cells(arms, base, other):
    out = {}
    for sid, *_ in ITEMS:
        c = {}
        for s in "xy":
            c[("ask", s)] = vs.codes(arms[base].get(sid, {}).get(s, []))
            c[("tag", s)] = vs.codes(arms[other].get(sid, {}).get(s, []))
        if all(len(v) for v in c.values()):
            out[sid] = c
    return out


def affirm(arms, arm):
    rates = [np.mean([(vs.codes(arms[arm].get(sid, {}).get(s, [])) == 1).mean() for s in "xy"])
             for sid, *_ in ITEMS if all(len(vs.codes(arms[arm].get(sid, {}).get(s, []))) for s in "xy")]
    return float(np.mean(rates)) if rates else None


def ranks(x):
    """Ranks with ties given their average rank, as Spearman's rho uses."""
    x = np.asarray(x, float)
    r = np.argsort(np.argsort(x)).astype(float)
    for v in np.unique(x):
        r[x == v] = r[x == v].mean()
    return r


def release_order(vals, fam=FAM, equal=False):
    """Mean within-family Spearman of value on release order, weighted by family size (or equally); permutation p."""
    fams = {}
    for m, v in vals.items():
        if m in fam:
            fams.setdefault(fam[m][0], []).append((fam[m][1], v))
    data = [(np.array([g for g, _ in f]), np.array([v for _, v in f])) for f in fams.values() if len({g for g, _ in f}) > 1]

    def stat(gs):   # models of one generation tie, and share their average rank
        return float(np.average([np.corrcoef(ranks(g), ranks(y))[0, 1] for g, (_, y) in zip(gs, data)],
                                weights=[1 if equal else len(g) for g in gs]))
    obs = stat([g for g, _ in data])
    rng = np.random.default_rng(7)   # each test draws the same permutations, so tables agree
    perm = np.array([stat([rng.permutation(g) for g, _ in data]) for _ in range(5000)])
    return {"rho": obs, "p": float(max(np.mean(np.abs(perm) >= abs(obs)), 1 / len(perm))),
            "models": int(sum(len(g) for g, _ in data)), "families": len(data)}


def main():
    grid = load()
    res, summary = {}, {}
    for w in WORDINGS:
        res[w] = {}
        for m, arms in grid[w].items():
            ct, cg = cells(arms, "neutral", "right"), cells(arms, "right", "maybe")
            if len(ct) < 15 or len(cg) < 15:
                continue
            res[w][m] = {"tag": vs.per_model(ct, seed=vs.model_seed(m, f"{w}_tag")),
                         "gap": vs.per_model(cg, seed=vs.model_seed(m, f"{w}_gap")),
                         **{f"affirm_{a}": affirm(arms, a) for a in ("neutral", "right", "maybe")}}
        for k in ("tag", "gap"):
            sig = vs.bh({m: r[k]["p"] for m, r in res[w].items()}, 0.05)
            for m, r in res[w].items():
                r[k]["sig"] = m in sig
        rw = res[w]
        t = np.array([r["tag"]["tageff"] for r in rw.values()]); g = np.array([r["gap"]["tageff"] for r in rw.values()])
        summary[w] = {"models": len(rw),
                      **{f"affirm_{a}": float(np.mean([r[f"affirm_{a}"] for r in rw.values()])) for a in ("neutral", "right", "maybe")},
                      "tag_mean": float(t.mean()), "tag_below_zero": int((t < 0).sum()), "tag_above_zero": int((t > 0).sum()),
                      "tag_sig_neg": sum(r["tag"]["sig"] and r["tag"]["tageff"] < 0 for r in rw.values()),
                      "tag_sig_pos": sum(r["tag"]["sig"] and r["tag"]["tageff"] > 0 for r in rw.values()),
                      "gap_mean": float(g.mean()), "gap_above_zero": int((g > 0).sum()),
                      "gap_sig_pos": sum(r["gap"]["sig"] and r["gap"]["tageff"] > 0 for r in rw.values()),
                      "gap_sig_neg": sum(r["gap"]["sig"] and r["gap"]["tageff"] < 0 for r in rw.values()),
                      "release_tag": release_order({m: r["tag"]["tageff"] for m, r in rw.items()}),
                      "release_gap": release_order({m: r["gap"]["tageff"] for m, r in rw.items()})}
    common = sorted(set.intersection(*(set(res[w]) for w in WORDINGS)))
    corr = {}
    for i, a in enumerate(WORDINGS):
        for b in WORDINGS[i + 1:]:
            for k in ("tag", "gap"):
                x = [res[a][m][k]["tageff"] for m in common]; y = [res[b][m][k]["tageff"] for m in common]
                corr[f"{k}_{a}_{b}"] = {"pearson": float(np.corrcoef(x, y)[0, 1]),
                                        "spearman": float(np.corrcoef(ranks(np.array(x)), ranks(np.array(y)))[0, 1])}
    summary["common_models"] = len(common)
    summary["correlations"] = corr
    (STUDY / "probes" / "grid_stats.json").write_text(json.dumps({"summary": summary, "per_model": res}, indent=1) + "\n")
    GEN.mkdir(exist_ok=True)
    (GEN / "grid_stats.json").write_text(json.dumps(summary, indent=1) + "\n")
    num = lambda x: f"{100 * x:+.1f}".replace("-", "$-$")
    pc = lambda x: f"{100 * x:.0f}"
    pv = lambda p: "$<$.001" if p < 0.001 else f"{p:.3f}".lstrip("0")
    rows = []
    for w, label in zip(WORDINGS, ("Implicit", "Both named", "Sufficiency")):
        s = summary[w]
        rows.append(f"{label} & {s['models']} & {pc(s['affirm_neutral'])} & {pc(s['affirm_right'])} & {pc(s['affirm_maybe'])} & "
                    f"{num(s['tag_mean'])} & {s['tag_sig_neg']} / {s['tag_sig_pos']} & {num(s['gap_mean'])} & "
                    f"{s['gap_above_zero']} & {s['release_tag']['rho']:+.2f} ({pv(s['release_tag']['p'])}) \\\\".replace("-0.", "$-$0."))
    (GEN / "grid_table.tex").write_text("\n".join(rows) + "\n\\bottomrule\n")
    tables()
    robustness()
    baseline_slope()
    print(json.dumps(summary, indent=1))


def tables():
    """The per-model grid table and the family-order table, from probes/grid_stats.json."""
    res = json.loads((STUDY / "probes" / "grid_stats.json").read_text())["per_model"]
    num = lambda r, k: f"{100 * r[k]['tageff']:+.0f}".replace("-", "$-$") + ("$^*$" if r[k]["sig"] else "")
    def cols(w, m):
        r = res[w].get(m)
        if r is None:
            return "--- & --- & ---"
        floor = "$^\\dagger$" if r["affirm_neutral"] < 0.10 else ""
        return f"{100 * r['affirm_neutral']:.0f}{floor} & {num(r, 'tag')} & {num(r, 'gap')}"
    ms = sorted(res["original"], key=lambda m: res["original"][m]["tag"]["tageff"])
    head = ("\\begin{tabular}{l rrr rrr rrr}\n\\toprule\n & \\multicolumn{3}{c}{Implicit} & \\multicolumn{3}{c}{Both named} "
            "& \\multicolumn{3}{c}{Sufficiency} \\\\\n\\cmidrule(lr){2-4}\\cmidrule(lr){5-7}\\cmidrule(lr){8-10}\n"
            "Model" + " & Neut. & Tag & Gap" * 3 + " \\\\\n\\midrule\n")
    rows = [f"\\texttt{{{m}}} & " + " & ".join(cols(w, m) for w in WORDINGS) + " \\\\" for m in ms]
    half = (len(rows) + 1) // 2
    tab = lambda rs: head + "\n".join(rs) + "\n\\bottomrule\n\\end{tabular}"
    (GEN / "grid_permodel.tex").write_text(tab(rows[:half]) + "\n\n\\clearpage\n" + tab(rows[half:]) + "\n")
    fams = {}
    for m, (f, g) in FAM.items():
        fams.setdefault(f, {}).setdefault(g, []).append(m)
    lines = [f"\\noindent\\textbf{{{f}}}: " + " $<$ ".join(", ".join(f"\\texttt{{{m}}}" for m in sorted(gens[g])) for g in sorted(gens)) + "\\par\\smallskip"
             for f, gens in fams.items()]
    (GEN / "lineage_table.tex").write_text("{\\sloppy\n" + "\n".join(lines) + "\n}\n")


def robustness():
    """The release test of the tag effect under alternative choices, per wording, plus the label-swap and retest
    collections of the original wording. Writes paper/gen/release_robust.tex and probes/release_robust.json."""
    res = json.loads((STUDY / "probes" / "grid_stats.json").read_text())["per_model"]
    ls = json.loads((STUDY / "probes" / "labelswap_analysis.json").read_text())["per_model"]
    rt = json.loads((STUDY / "probes" / "retest_analysis.json").read_text())["per_model"]
    out, rows = {}, []
    for w in WORDINGS:
        t = {m: r["tag"]["tageff"] for m, r in res[w].items()}
        nf = {m: v for m, v in t.items() if res[w][m]["affirm_neutral"] >= 0.10}
        v = {"as reported": release_order(t), "floor-limited excluded": release_order(nf),
             "families weighted equally": release_order(t, equal=True),
             "13 families": release_order(t, {**FAM, **EXTRA}),
             "13 families, no floor-limited": release_order(nf, {**FAM, **EXTRA})}
        loo = [release_order({m: x for m, x in t.items() if FAM.get(m, ("",))[0] != f})
               for f in sorted({f for f, _ in FAM.values()})]
        v["leaving out one family"] = {"rho": [min(r["rho"] for r in loo), max(r["rho"] for r in loo)],
                                       "p": max(r["p"] for r in loo)}
        out[w] = v
    out["original_letters"] = release_order({m: r["tageff_letters"] for m, r in ls.items()})
    out["original_retest"] = release_order({m: r["tageff_retest"] for m, r in rt.items()})
    (STUDY / "probes" / "release_robust.json").write_text(json.dumps(out, indent=1) + "\n")
    pv = lambda p: "$<$.001" if p < 0.001 else f"{p:.3f}".lstrip("0")
    rh = lambda r: (f"{r['rho'][0]:+.2f}..{r['rho'][1]:+.2f} ($\\le${pv(r['p'])})" if isinstance(r["rho"], list)
                    else f"{r['rho']:+.2f} ({pv(r['p'])})").replace("-", "$-$")
    for k in out["original"]:
        rows.append(f"{k[0].upper() + k[1:]} & " + " & ".join(rh(out[w][k]) for w in WORDINGS) + " \\\\")
    rows.append("\\midrule")
    rows.append(f"Letters in place of yes/no & {rh(out['original_letters'])} & & \\\\")
    rows.append(f"Retest collection & {rh(out['original_retest'])} & & \\\\")
    (GEN / "release_robust.tex").write_text("\n".join(rows) + "\n\\bottomrule\n")


def baseline_slope():
    """Within-model slope of the tag effect on the neutral rate across the three wordings, with the
    neutral rate's sampling noise kept out of it: each neutral cell's replies are split in two, one
    half instruments the other (slope of right? on neutral = cov(R, N_a) / cov(N_b, N_a), models
    demeaned), and the tag-effect slope is that minus 1. Intervals resample models. Writes
    probes/baseline_slope.json."""
    grid = load()
    res = json.loads((STUDY / "probes" / "grid_stats.json").read_text())["per_model"]
    common = sorted(set.intersection(*(set(res[w]) for w in WORDINGS)))

    def halves(cells, rng):
        a, b = [], []
        for sid, *_ in ITEMS:
            ha, hb = [], []
            for s in "xy":
                c = vs.codes(cells.get(sid, {}).get(s, []))
                if len(c) < 2:
                    break
                i = rng.permutation(len(c))
                ha.append((c[i[:len(c) // 2]] == 1).mean()); hb.append((c[i[len(c) // 2:]] == 1).mean())
            if len(ha) == 2:
                a.append(np.mean(ha)); b.append(np.mean(hb))
        return np.mean(a), np.mean(b)

    rng = np.random.default_rng(7)
    rows = {m: np.array([(res[w][m]["affirm_neutral"], res[w][m]["affirm_right"], *halves(grid[w][m]["neutral"], rng))
                         for w in WORDINGS]) for m in common}

    def slope(ms):
        d = np.concatenate([rows[m] - rows[m].mean(0) for m in ms])
        n, r, a, b = d.T
        return {"reported": float(np.sum(n * (r - n)) / np.sum(n * n)), "split": float(np.sum(a * r) / np.sum(a * b) - 1)}

    out = slope(common)
    br = np.random.default_rng(3)
    boot = [slope([common[i] for i in br.integers(0, len(common), len(common))])["split"] for _ in range(2000)]
    out["split_ci95"] = [float(x) for x in np.percentile(boot, [2.5, 97.5])]
    out["models"] = len(common)
    (STUDY / "probes" / "baseline_slope.json").write_text(json.dumps(out, indent=1) + "\n")
    print("baseline slope", json.dumps(out))


if __name__ == "__main__":
    import sys
    if "--slope" in sys.argv:
        baseline_slope()
    elif "--tables" in sys.argv:
        tables(); robustness()
    else:
        main()
