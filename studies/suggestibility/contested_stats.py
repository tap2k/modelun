"""contested_stats.py — the statistics for the contested-questions paper (paper-contested/).

Reads probes/contested/ (arms ask, tag, bare, belief, maybe and belief_q on 18 items x 2 mirror sides) and the four contested stage ladders, and writes paper-contested/gen/:

  stats.json            every number the text cites
  permodel_table.tex    per-model tag and belief effects with 95% intervals and BH marks
  items_table.tex       the 18 claims and mirrors, with per-item panel effects and the neutral lean
  stages_table.tex      tag, bare and belief effects by training stage
  vendor_table.tex      where vendors land on the neutral question

Statistics follow v2_stats: an effect is affirm(arm) - affirm(ask) per mirror side, averaged over the
two sides, then over items. Affirm is counted over every classified reply, so a hedge is non-agreement;
answered-only (affirm over yes and no replies) is the secondary measure. Per-model intervals are a
nested bootstrap (items, then replies within each item x arm x side cell), 95%, two-sided bootstrap p,
Benjamini-Hochberg at q = .05. Panel means and stratum contrasts resample items (within stratum) and
replies jointly across models.

    python studies/suggestibility/contested_stats.py
"""
import json, os
from pathlib import Path
import numpy as np
from analyze import classify
from probe_contested import ITEMS, STRATA, LEFT
import v2_stats as vs

STUDY = Path(__file__).resolve().parent
GEN = STUDY / "paper-contested" / ("gen-quick" if os.environ.get("QUICK") else "gen")  # QUICK output stays out of gen/
CODE = {"affirm": 1, "reject": 0, "hedge": -1}
ARMS = ("ask", "tag", "bare", "belief", "maybe")
EFFECTS = ("tag", "bare", "belief", "maybe")
STRATUM = {i: s for i, s, _, _ in ITEMS}
# The lab that made each model, from the OpenRouter slug prefix. Hosting and org prefixes map to the
# lab: meta and meta-llama are both Meta, qwen is Alibaba, inclusionai is Ant Group, z-ai is Zhipu.
LAB = {"anthropic": "Anthropic", "baidu": "Baidu", "bytedance-seed": "ByteDance", "cohere": "Cohere",
       "deepseek": "DeepSeek", "google": "Google", "gryphe": "Gryphe", "ibm-granite": "IBM",
       "inclusionai": "Ant Group", "meta": "Meta", "meta-llama": "Meta", "microsoft": "Microsoft",
       "minimax": "MiniMax", "mistralai": "Mistral AI", "moonshotai": "Moonshot AI",
       "nousresearch": "Nous Research", "nvidia": "NVIDIA", "openai": "OpenAI", "perplexity": "Perplexity",
       "qwen": "Alibaba", "stepfun": "StepFun", "tencent": "Tencent", "thinkingmachines": "Thinking Machines",
       "writer": "Writer", "x-ai": "xAI", "xiaomi": "Xiaomi", "z-ai": "Zhipu AI"}
B = 20 if os.environ.get("QUICK") else 2000   # QUICK=1: a fast check of the code paths
rng = np.random.default_rng(7)


def codes(replies):
    return np.array([CODE[c] for c in (classify(r) for r in replies if r) if c is not None], dtype=int)


def load():
    data, meta = {}, {}
    for p in sorted((STUDY / "probes" / "contested").glob("*.json")):
        d = json.loads(p.read_text())
        cells = {}
        for item, *_ in ITEMS:
            c = d["cells"].get(item, {})
            cc = {(a, s): codes(c.get(f"{a}_{s}", [])) for a in ARMS + ("belief_q",) for s in "xy"}
            if all(len(cc[(a, s)]) for a in ARMS for s in "xy"):
                cells[item] = cc
        if len(cells) >= 15:
            data[d["model"]] = cells
            meta[d["model"]] = {"slug": d["slug"], "vendor": LAB[d["slug"].split("/")[0]],
                                "spot": (d.get("arm_dates") or {}).get("belief_q") == "2026-09-30"}
    return data, meta


def rate(v, answered):
    if answered:
        v = v[v >= 0]
        return v.mean() if len(v) else np.nan
    return (v == 1).mean() if len(v) else np.nan


def item_effects(cells, arm, draw=None, answered=False, base="ask"):
    """item -> effect of `arm` against `base`, mean over the two mirror sides."""
    out = {}
    for item, c in cells.items():
        e = []
        for s in "xy":
            a, b = c[(arm, s)], c[(base, s)]
            if not len(a) or not len(b):
                continue
            if draw is not None:
                a, b = a[draw[(item, arm, s)]], b[draw[(item, base, s)]]
            e.append(rate(a, answered) - rate(b, answered))
        out[item] = np.nanmean(e) if e and not all(np.isnan(e)) else np.nan
    return out


def reply_draw(cells, arms):
    return {(item, a, s): rng.integers(0, len(c[(a, s)]), len(c[(a, s)]))
            for item, c in cells.items() for a in arms for s in "xy" if len(c[(a, s)])}


def per_model(cells, arm, answered=False, base="ask"):
    """v2_stats.per_model on this arm against `base`: nested bootstrap (items, then replies within each
    item x arm x side cell), B draws, 95% percentile interval, two-sided p = 2 min(P(boot <= 0),
    P(boot >= 0)) floored at 1/B. Items missing either arm on either side are dropped."""
    vc = {i: {**{("ask", s): c[(base, s)] for s in "xy"}, **{("tag", s): c[(arm, s)] for s in "xy"}}
          for i, c in cells.items() if all(len(c[(a, s)]) for a in (arm, base) for s in "xy")}
    vs.B = B
    r = vs.per_model(vc, answered=answered)
    return {"eff": r["tageff"], "ci95": r["ci95"], "p": r["p"], "n_items": len(vc)}


def panel(data, arm, answered=False, nboot=None, base="ask"):
    """Panel mean of a per-model effect, overall and by stratum, with stratum contrasts; items resampled
    within stratum and replies within cells, jointly for every model."""
    nboot = nboot or B // 2
    models = list(data)
    by = {st: [i for i, s, *_ in ITEMS if s == st] for st in STRATA}

    def stat(picks, draws):
        out = {}
        effs = {m: item_effects(data[m], arm, draws.get(m), answered, base) for m in models}
        for st, pick in picks.items():
            out[st] = float(np.nanmean([np.nanmean([effs[m][i] for i in pick if i in effs[m]]) for m in models]))
        out["all"] = float(np.nanmean([np.nanmean([effs[m][i] for st in STRATA for i in picks[st] if i in effs[m]])
                                       for m in models]))
        return out

    point = stat(by, {})
    boots = [stat({st: list(rng.choice(by[st], len(by[st]))) for st in STRATA},
                  {m: reply_draw(data[m], (arm, base)) for m in models}) for _ in range(nboot)]
    res = {}
    for k in ("all",) + STRATA:
        b = np.array([x[k] for x in boots])
        res[k] = {"mean": point[k], "ci95": [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]}
    for a, c in (("history", "policy"), ("history", "hot"), ("policy", "hot")):
        b = np.array([x[a] - x[c] for x in boots])
        res[f"{a}-{c}"] = {"diff": point[a] - point[c], "ci95": [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))],
                           "p": float(min(1.0, max(2 * min(np.mean(b <= 0), np.mean(b >= 0)), 1 / nboot)))}
    return res


def split_half(data, arm):
    """Per-model effect from samples 0-1 against samples 2-3 of every cell; Spearman-Brown reliability."""
    def half(cells, h):
        sub = {i: {k: v[h::2] for k, v in c.items()} for i, c in cells.items()}
        return np.nanmean(list(item_effects(sub, arm).values()))
    a = np.array([half(data[m], 0) for m in data]); b = np.array([half(data[m], 1) for m in data])
    ok = ~np.isnan(a) & ~np.isnan(b)
    r = np.corrcoef(a[ok], b[ok])[0, 1]
    return float(2 * r / (1 + r))


def spearman(a, b):
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


def hedge_rates(data):
    out = {}
    for st in STRATA + ("all",):
        items = [i for i, s, *_ in ITEMS if st == "all" or s == st]
        out[st] = {a: float(np.mean([np.mean([(data[m][i][(a, s)] == -1).mean() for i in items if i in data[m]
                                              for s in "xy"]) for m in data])) for a in ARMS}
    return out


def favored_split(data, arm):
    """Effect of `arm` on the side the model favors under the neutral question and on the other side.
    The favored side is picked with ask samples 0-1 and the effect uses ask samples 2-3, so selection
    noise does not regress into the effect. Items with a tie in the first half are skipped; their
    effect (both sides, same baseline samples) is reported separately, so the split reconciles with the
    panel effect: mean of the two sides on untied items, weighted with the tied items, per model."""
    fav, dis, tied, n_untied, n_all = [], [], [], 0, 0
    for cells in data.values():
        f_m, d_m, t_m = [], [], []
        for i, c in cells.items():
            sel = {s: c[("ask", s)][:2] for s in "xy"}
            if not all(len(v) for v in sel.values()) or not all(len(c[("ask", s)][2:]) for s in "xy"):
                continue
            n_all += 1
            ev = lambda s: rate(c[(arm, s)], False) - rate(c[("ask", s)][2:], False)
            rx, ry = (sel["x"] == 1).mean(), (sel["y"] == 1).mean()
            if rx == ry:
                t_m.append(np.nanmean([ev("x"), ev("y")]))
                continue
            n_untied += 1
            f, d = ("x", "y") if rx > ry else ("y", "x")
            f_m.append(ev(f)); d_m.append(ev(d))
        if f_m:
            fav.append(np.nanmean(f_m)); dis.append(np.nanmean(d_m))
        if t_m:
            tied.append(np.nanmean(t_m))
    fav, dis = np.array(fav), np.array(dis)
    ci = lambda v: [float(np.percentile(b, q)) for b in [[np.nanmean(v[rng.integers(0, len(v), len(v))]) for _ in range(2000)]]
                    for q in (2.5, 97.5)]
    return {"favored": float(np.nanmean(fav)), "favored_ci95": ci(fav), "disfavored": float(np.nanmean(dis)),
            "disfavored_ci95": ci(dis), "models": len(fav), "untied_mean": float(np.nanmean((fav + dis) / 2)),
            "tied_mean": float(np.nanmean(tied)) if tied else None, "share_untied": n_untied / n_all}


def lean(data, meta):
    """Neutral-question lean per model and item: ((yes to claim + no to mirror) - (yes to mirror + no to
    claim)) / 2, in [-1, 1]; hedges count toward neither side."""
    L = {}
    for m, cells in data.items():
        row = {}
        for i, c in cells.items():
            x, y = c[("ask", "x")], c[("ask", "y")]
            row[i] = (((x == 1).mean() + (y == 0).mean()) - ((y == 1).mean() + (x == 0).mean())) / 2
        L[m] = row
    field = {i: float(np.mean([L[m][i] for m in L if i in L[m]])) for i, *_ in ITEMS}
    vend = {}
    for m in L:
        vend.setdefault(meta[m]["vendor"], []).append(m)

    def summ(ms):
        side = [abs(L[m][i]) >= 0.25 for m in ms for i in L[m]]
        with_field = [np.sign(L[m][i]) == np.sign(field[i]) for m in ms for i in L[m]
                      if abs(L[m][i]) >= 0.25 and abs(field[i]) >= 0.1]
        return {"n": len(ms), "on_a_side": float(np.mean(side)), "with_field": float(np.mean(with_field)) if with_field else None}

    groups = {v: summ(ms) for v, ms in vend.items() if len(ms) >= 4}
    allm = list(L)
    perm = {}
    for v, ms in vend.items():
        if len(ms) < 4:
            continue
        obs = summ(ms)["on_a_side"] - summ([m for m in allm if m not in ms])["on_a_side"]
        null = []
        for _ in range(2000):
            pick = set(rng.choice(allm, len(ms), replace=False))
            null.append(summ(list(pick))["on_a_side"] - summ([m for m in allm if m not in pick])["on_a_side"])
        perm[v] = {"diff": obs, "p": float((1 + np.sum(np.abs(null) >= abs(obs))) / 2001)}
    return L, field, groups, perm, vend


def ladders():
    rows = []
    spec = [("OLMo 3.1 32B", "32b", ["base/raw", "sft/nosys", "dpo/nosys", "rl/nosys"]),
            ("OLMo 3 7B", "7b", ["base/raw", "sft/nosys", "dpo/nosys", "rl/nosys"]),
            ("Tulu 3 8B", "tulu", ["base/raw", "sft/chat", "dpo/chat", "rl/chat"]),
            ("Nemotron 3.5 Lightning", "nemotron", ["base/raw", "final/chat"])]
    for name, key, stages in spec:
        s = json.loads((STUDY / "probes" / f"contested_ladder_{key}.json").read_text())["summary"]
        for st in stages:
            a = s[st]["all"]
            rows.append({"pipeline": name, "stage": st.split("/")[0], "tag": a["effects"]["TAGeff"],
                         "bare": a["effects"]["BAREeff"], "belief": a["effects"]["BELIEFeff"],
                         "both_no_ask": a["mirror_pairs"]["ask"]["both_no"], "answered": a["answered"]})
    return rows


def main():
    GEN.mkdir(parents=True, exist_ok=True)
    data, meta = load()
    print(f"{len(data)} models")
    pm = {m: {a: per_model(data[m], a) for a in EFFECTS} for m in data}
    for m in data:
        for a in ("tag", "belief"):
            pm[m][a + "_answered"] = per_model(data[m], a, answered=True)
    for m in data:
        pm[m]["belief_vs_tag"] = per_model(data[m], "belief", base="tag")
    sig = {a: vs.bh({m: pm[m][a]["p"] for m in pm}, 0.05) for a in EFFECTS + ("belief_vs_tag",)}
    eff = {a: np.array([pm[m][a]["eff"] for m in data]) for a in EFFECTS}
    ms = list(data)
    resist = [m for m in ms if m in sig["tag"] and pm[m]["tag"]["eff"] < 0]
    S = {"models": len(ms), "items": len(ITEMS)}
    for a in EFFECTS:
        S[a] = {"below_zero": int((eff[a] < 0).sum()), "above_zero": int((eff[a] > 0).sum()),
                "sig_neg": sum(m in sig[a] and pm[m][a]["eff"] < 0 for m in ms),
                "sig_pos": sum(m in sig[a] and pm[m][a]["eff"] > 0 for m in ms),
                "panel": panel(data, a)}
        print(a, S[a]["panel"]["all"])
    for a in ("tag", "belief"):
        S[a]["panel_answered"] = panel(data, a, answered=True, nboot=B // 5)["all"]
    S["belief_gt_tag"] = int((eff["belief"] > eff["tag"]).sum())
    S["belief_vs_tag"] = {"panel": panel(data, "belief", base="tag")["all"],
                          "sig_pos": sum(m in sig["belief_vs_tag"] and pm[m]["belief_vs_tag"]["eff"] > 0 for m in ms),
                          "sig_neg": sum(m in sig["belief_vs_tag"] and pm[m]["belief_vs_tag"]["eff"] < 0 for m in ms)}
    S["sig_lists"] = {a: sorted(sig[a]) for a in sig}
    S["spearman_tag_belief"] = spearman(eff["tag"], eff["belief"])
    rel = {a: split_half(data, a) for a in ("tag", "belief")}
    S["reliability"] = rel
    S["spearman_tag_belief_disattenuated"] = S["spearman_tag_belief"] / float(np.sqrt(rel["tag"] * rel["belief"]))
    boot_r = []
    for _ in range(2000):
        idx = rng.integers(0, len(ms), len(ms))
        boot_r.append(spearman(eff["tag"][idx], eff["belief"][idx]))
    S["spearman_tag_belief_ci95"] = [float(np.percentile(boot_r, 2.5)), float(np.percentile(boot_r, 97.5))]
    labs = sorted({meta[m]["vendor"] for m in ms})
    idx_by_lab = {l: [k for k, m in enumerate(ms) if meta[m]["vendor"] == l] for l in labs}
    boot_c = []
    for _ in range(2000):
        idx = np.concatenate([idx_by_lab[l] for l in rng.choice(labs, len(labs))])
        boot_c.append(spearman(eff["tag"][idx], eff["belief"][idx]))
    S["spearman_tag_belief_ci95_labs"] = [float(np.percentile(boot_c, 2.5)), float(np.percentile(boot_c, 97.5))]
    S["resisters"] = {"n": len(resist),
                      "belief_at_or_above_zero": sum(pm[m]["belief"]["eff"] >= 0 for m in resist),
                      "belief_sig_pos": sum(m in sig["belief"] and pm[m]["belief"]["eff"] > 0 for m in resist),
                      "belief_gt_tag": sum(pm[m]["belief"]["eff"] > pm[m]["tag"]["eff"] for m in resist),
                      "belief_gt_tag_sig": sum(m in sig["belief_vs_tag"] and pm[m]["belief_vs_tag"]["eff"] > 0 for m in resist),
                      "belief_sig_neg": sum(m in sig["belief"] and pm[m]["belief"]["eff"] < 0 for m in resist),
                      "belief_mean": float(np.mean([pm[m]["belief"]["eff"] for m in resist])) if resist else None,
                      "tag_mean": float(np.mean([pm[m]["tag"]["eff"] for m in resist])) if resist else None,
                      "detail": {m: {"tag": pm[m]["tag"]["eff"], "belief": pm[m]["belief"]["eff"],
                                     "belief_sig": m in sig["belief"]} for m in resist}}
    # belief_q: "I think P. <question>" against the question, and against "I think P.", on every model
    # with the arm on at least 15 items. The first 20 (2026-09-30), a broad cross-section of models, were a spot check.
    full = lambda m: {i: c for i, c in data[m].items() if len(c[("belief_q", "x")]) and len(c[("belief_q", "y")])}
    bq = [m for m in ms if len(full(m)) >= 15]
    if bq:
        for m in bq:
            pm[m]["belief_q"] = per_model(full(m), "belief_q")
        bsig = vs.bh({m: pm[m]["belief_q"]["p"] for m in bq}, 0.05)
        for m in bq:
            pm[m]["belief_q_vs_belief"] = per_model(full(m), "belief_q", base="belief")
        dsig = vs.bh({m: pm[m]["belief_q_vs_belief"]["p"] for m in bq}, 0.05)
        sub = {m: full(m) for m in bq}
        spot = [m for m in bq if meta[m]["spot"]]
        S["belief_q"] = {"models": bq, "n": len(bq), "labs": len({meta[m]["vendor"] for m in bq}),
                         "panel": panel(sub, "belief_q")["all"], "belief_same": panel(sub, "belief")["all"],
                         "vs_belief": panel(sub, "belief_q", base="belief")["all"],
                         "sig_pos": sum(m in bsig and pm[m]["belief_q"]["eff"] > 0 for m in bq),
                         "sig_neg": sum(m in bsig and pm[m]["belief_q"]["eff"] < 0 for m in bq),
                         "spearman_belief_belief_q": spearman(np.array([pm[m]["belief"]["eff"] for m in bq]),
                                                              np.array([pm[m]["belief_q"]["eff"] for m in bq])),
                         "differ_sig": {m: pm[m]["belief_q_vs_belief"]["eff"] for m in bq if m in dsig},
                         "differ_20": sum(abs(pm[m]["belief_q_vs_belief"]["eff"]) >= 0.20 for m in bq),
                         "spot_n": len(spot),
                         "spot_belief_q": float(np.mean([pm[m]["belief_q"]["eff"] for m in spot])) if spot else None,
                         "spot_belief": float(np.mean([pm[m]["belief"]["eff"] for m in spot])) if spot else None}
    S["hedge"] = hedge_rates(data)
    # left/right asymmetry of the tag and belief on the nine items with a left-coded side
    for a in EFFECTS:
        lft, rgt = [], []
        for m in ms:
            for i, side in LEFT.items():
                if i not in data[m]:
                    continue
                c = data[m][i]; other = "y" if side == "x" else "x"
                lft.append(rate(c[(a, side)], False) - rate(c[("ask", side)], False))
                rgt.append(rate(c[(a, other)], False) - rate(c[("ask", other)], False))
        S[a]["left_claims"] = float(np.nanmean(lft)); S[a]["right_claims"] = float(np.nanmean(rgt))
    S["favored"] = {a: favored_split(data, a) for a in EFFECTS}
    L, field, groups, perm, vend = lean(data, meta)
    S["left_lean_items"] = sum((field[i] > 0) == (side == "x") for i, side in LEFT.items())
    S["labs"] = len({meta[m]["vendor"] for m in ms})
    S["lean"] = {"field": field, "vendors": groups, "perm_on_a_side": perm,
                 "on_a_side_all": float(np.mean([abs(L[m][i]) >= 0.25 for m in L for i in L[m]]))}
    item_tag = {i: float(np.nanmean([item_effects(data[m], "tag")[i] for m in ms if i in data[m]])) for i, *_ in ITEMS}
    item_bel = {i: float(np.nanmean([item_effects(data[m], "belief")[i] for m in ms if i in data[m]])) for i, *_ in ITEMS}
    absl = np.array([abs(field[i]) for i, *_ in ITEMS])
    S["items"] = {"tag": item_tag, "belief": item_bel,
                  "spearman_tag_abs_lean": spearman(np.array([item_tag[i] for i, *_ in ITEMS]), absl),
                  "spearman_belief_abs_lean": spearman(np.array([item_bel[i] for i, *_ in ITEMS]), absl)}
    S["stages"] = ladders()
    S["per_model"] = pm
    (GEN / "stats.json").write_text(json.dumps(S, indent=1, default=float) + "\n")

    num = lambda x: f"{100 * x:+.0f}".replace("-", "$-$")
    star = lambda m, a: "$^*$" if m in sig[a] else ""
    rows = [f"\\texttt{{{m}}} & {num(pm[m]['tag']['eff'])}{star(m, 'tag')} & [{num(pm[m]['tag']['ci95'][0])}, {num(pm[m]['tag']['ci95'][1])}] & "
            f"{num(pm[m]['belief']['eff'])}{star(m, 'belief')} & [{num(pm[m]['belief']['ci95'][0])}, {num(pm[m]['belief']['ci95'][1])}] \\\\"
            for m in sorted(ms, key=lambda m: pm[m]["tag"]["eff"])]
    head = ("\\resizebox{0.49\\textwidth}{!}{\\begin{tabular}[t]{lrrrr}\n\\toprule\nModel & Tag & 95\\% CI & Belief & 95\\% CI \\\\\n"
            "\\midrule\n")
    tab = lambda rs: head + "\n".join(rs) + "\n\\bottomrule\n\\end{tabular}}"
    half = (len(rows) + 1) // 2
    (GEN / "permodel_table.tex").write_text(tab(rows[:half]) + "\n\\hfill\n" + tab(rows[half:]) + "\n")

    it = []
    for i, st, (qx, sx), (qy, sy) in ITEMS:
        t = np.nanmean([item_effects(data[m], "tag")[i] for m in ms if i in data[m]])
        b = np.nanmean([item_effects(data[m], "belief")[i] for m in ms if i in data[m]])
        h = np.mean([(data[m][i][("ask", s)] == -1).mean() for m in ms if i in data[m] for s in "xy"])
        tx = lambda c: (c[0].upper() + c[1:]).replace("$", "\\$")
        it.append(f"{st} & {tx(sx)} & {tx(sy)} & {num(t)} & {num(b)} & {100 * h:.0f} & " + f"{field[i]:+.2f}".replace("-", "$-$") + " \\\\")
    (GEN / "items_table.tex").write_text("\n".join(it) + "\n")

    st_rows = []
    for r in S["stages"]:
        f = lambda e: f"{num(e[0])} [{num(e[1])}, {num(e[2])}]"
        st_rows.append(f"{r['pipeline']} & {r['stage']} & {f(r['tag'])} & {f(r['bare'])} & {f(r['belief'])} & {100 * r['both_no_ask']:.0f} \\\\")
    (GEN / "stages_table.tex").write_text("\n".join(st_rows) + "\n")

    pv = lambda p: "$<$.001" if p < 0.001 else f"{p:.3f}".lstrip("0")
    vrows = []
    for v, g in sorted(groups.items(), key=lambda kv: -kv[1]["on_a_side"]):
        wf = "" if g["with_field"] is None else f"{100 * g['with_field']:.0f}"
        vrows.append(f"{v} & {g['n']} & {100 * g['on_a_side']:.0f} & {wf} & {pv(perm[v]['p'])} \\\\")
    (GEN / "vendor_table.tex").write_text("\n".join(vrows) + "\n")
    print(json.dumps({k: v for k, v in S.items() if k not in ("per_model", "lean", "stages")}, indent=1, default=float)[:6000])




def numbers():
    """gen/numbers.tex (one macro per number the text cites), gen/arm_rows.tex and gen/fav_rows.tex,
    from gen/stats.json. Run after main(); it recomputes nothing."""
    S = json.loads((GEN / "stats.json").read_text())
    p = lambda x, d=1: "MISSING" if x is None else f"{100 * x:+.{d}f}".replace("-", "$-$")
    u = lambda x, d=1: f"{100 * x:.{d}f}"
    ci = lambda c, d=1: f"{p(c[0], d)}, {p(c[1], d)}"
    pn = S["tag"]["panel"]; bn = S["belief"]["panel"]
    hed = S["hedge"]
    rise = [100 * (hed[st]["tag"] - hed[st]["ask"]) for st in STRATA]
    fav = S["favored"]
    lean = S["lean"]["vendors"]
    N = {
        "TAG": u(-pn["all"]["mean"]), "TAGCI": ci(pn["all"]["ci95"]),
        "TAGNEG": S["tag"]["below_zero"], "TAGPOS": S["tag"]["above_zero"],
        "TAGSIGNEG": S["tag"]["sig_neg"], "TAGSIGPOS": S["tag"]["sig_pos"],
        "BARE": p(S["bare"]["panel"]["all"]["mean"]), "BARECI": ci(S["bare"]["panel"]["all"]["ci95"]),
        "MAYBE": p(S["maybe"]["panel"]["all"]["mean"]), "MAYBECI": ci(S["maybe"]["panel"]["all"]["ci95"]),
        "BEL": u(bn["all"]["mean"]), "BELCI": ci(bn["all"]["ci95"]), "BELSIGPOS": S["belief"]["sig_pos"],
        "TAGANS": p(S["tag"]["panel_answered"]["mean"]), "BELANS": p(S["belief"]["panel_answered"]["mean"]),
        "BGT": S["belief_gt_tag"],
        "SHT": p(pn["history"]["mean"]), "SPT": p(pn["policy"]["mean"]), "SHOT": p(pn["hot"]["mean"]),
        "SHTCI": ci(pn["history"]["ci95"]), "SPTCI": ci(pn["policy"]["ci95"]), "SHOTCI": ci(pn["hot"]["ci95"]),
        "DHP": p(pn["history-policy"]["diff"]), "DHPCI": ci(pn["history-policy"]["ci95"]),
        "DHPP": f"{pn['history-policy']['p']:.3f}".lstrip("0"),
        "DHH": p(pn["history-hot"]["diff"]), "DHHCI": ci(pn["history-hot"]["ci95"]),
        "DHHP": f"{pn['history-hot']['p']:.3f}".lstrip("0"),
        "DPH": p(pn["policy-hot"]["diff"]), "DPHCI": ci(pn["policy-hot"]["ci95"]),
        "SHB": p(bn["history"]["mean"]), "SPB": p(bn["policy"]["mean"]), "SHOTB": p(bn["hot"]["mean"]),
        "DHPB": p(bn["history-policy"]["diff"]), "DHPBCI": ci(bn["history-policy"]["ci95"]),
        "DHHB": p(bn["history-hot"]["diff"]), "DHHBCI": ci(bn["history-hot"]["ci95"]),
        "HASKH": u(hed["history"]["ask"], 0), "HASKP": u(hed["policy"]["ask"], 0), "HASKHOT": u(hed["hot"]["ask"], 0),
        "HRISELO": f"{min(rise):.1f}", "HRISEHI": f"{max(rise):.1f}",
        "TAGL": u(-S["tag"]["left_claims"]), "TAGR": u(-S["tag"]["right_claims"]),
        "BELL": u(S["belief"]["left_claims"]), "BELR": u(S["belief"]["right_claims"]),
        "FAVN": fav["tag"]["models"], "FAVT": u(-fav["tag"]["favored"]), "DIST": p(fav["tag"]["disfavored"]),
        "DISB": u(fav["belief"]["disfavored"]), "FAVBABS": u(-fav["belief"]["favored"]), "FAVBARE": u(-fav["bare"]["favored"]),
        "ITEMRHOT": f"{S['items']['spearman_tag_abs_lean']:.2f}",  # used inside math
        "ITEMRHOB": f"{S['items']['spearman_belief_abs_lean']:.2f}",
        "RHO": f"{S['spearman_tag_belief']:.2f}", "RHOCI": f"{S['spearman_tag_belief_ci95'][0]:.2f}, {S['spearman_tag_belief_ci95'][1]:.2f}",
        "RHOD": f"{S['spearman_tag_belief_disattenuated']:.2f}",
        "RHOCILAB": f"{S['spearman_tag_belief_ci95_labs'][0]:.2f}, {S['spearman_tag_belief_ci95_labs'][1]:.2f}",
        "FAVUNTIED": p(fav["tag"]["untied_mean"]), "FAVTIED": p(fav["tag"]["tied_mean"]),
        "FAVSHARE": u(fav["tag"]["share_untied"], 0),
        "FAVBUNTIED": p(fav["belief"]["untied_mean"]), "FAVBTIED": p(fav["belief"]["tied_mean"]),
        "BQRHO": f"{S['belief_q']['spearman_belief_belief_q']:.2f}", "BQDIFF20": S["belief_q"]["differ_20"],
        "BQDIFFSIG": len(S["belief_q"]["differ_sig"]),
        "RELT": f"{S['reliability']['tag']:.2f}", "RELB": f"{S['reliability']['belief']:.2f}",
        "RESN": S["resisters"]["n"], "RESBEL": S["resisters"]["belief_at_or_above_zero"],
        "RESBELSIG": S["resisters"]["belief_sig_pos"], "RESGT": S["resisters"]["belief_gt_tag"],
        "REST": p(S["resisters"]["tag_mean"]), "RESB": p(S["resisters"]["belief_mean"]),
        "BQN": S["belief_q"]["n"], "BQV": S["belief_q"]["labs"],
        "BQ": u(S["belief_q"]["panel"]["mean"]), "BQCI": ci(S["belief_q"]["panel"]["ci95"]),
        "BQB": u(S["belief_q"]["belief_same"]["mean"]), "BQBCI": ci(S["belief_q"]["belief_same"]["ci95"]),
        "BQD": p(S["belief_q"]["vs_belief"]["mean"]), "BQDCI": ci(S["belief_q"]["vs_belief"]["ci95"]),
        "BQSIGPOS": S["belief_q"]["sig_pos"], "BQSIGNEG": S["belief_q"]["sig_neg"],
        "BQSPOTN": S["belief_q"]["spot_n"], "BQSPOTQ": u(S["belief_q"]["spot_belief_q"] or 0),
        "BQSPOTB": u(S["belief_q"]["spot_belief"] or 0),
        "ONSIDE": u(S["lean"]["on_a_side_all"], 0),
        "OAI": u(lean["OpenAI"]["on_a_side"], 0), "ANT": u(lean["Anthropic"]["on_a_side"], 0),
        "GOO": u(lean["Google"]["on_a_side"], 0), "XAI": u(lean["xAI"]["with_field"], 0),
        "BVT": u(S["belief_vs_tag"]["panel"]["mean"]), "BVTCI": ci(S["belief_vs_tag"]["panel"]["ci95"]),
        "BVTSIGPOS": S["belief_vs_tag"]["sig_pos"], "BVTSIGNEG": S["belief_vs_tag"]["sig_neg"],
        "RESBVT": S["resisters"]["belief_gt_tag_sig"], "RESBELNEG": S["resisters"]["belief_sig_neg"],
        "LABS": S["labs"], "LRLEAN": S["left_lean_items"], "BELSIGNEG": S["belief"]["sig_neg"],
        "MODELS": S["models"],
    }
    pm = S["per_model"]
    neg = [m for m in pm if pm[m]["tag"]["eff"] < 0]
    N.update({"NEGBEL": p(np.mean([pm[m]["belief"]["eff"] for m in neg])),
              "NEGBELGE": sum(pm[m]["belief"]["eff"] >= 0 for m in neg),
              "NEGGT": sum(pm[m]["belief"]["eff"] > pm[m]["tag"]["eff"] for m in neg),
              "UNC": sum(pm[m]["tag"]["ci95"][1] < 0 for m in pm)})
    (GEN / "numbers.tex").write_text("".join(f"\\newcommand{{\\n{k}}}{{{v}}}\n" for k, v in N.items()))
    names = {"tag": "Tag (\\emph{right?})", "maybe": "Tentative (\\emph{maybe?})", "bare": "Bare claim", "belief": "Belief (\\emph{I think})"}
    rows = [f"{names[a]} & {p(S[a]['panel']['all']['mean'])} & [{ci(S[a]['panel']['all']['ci95'])}] & "
            f"{S[a]['below_zero']} / {S[a]['above_zero']} ({S[a]['sig_neg']} / {S[a]['sig_pos']}) \\\\" for a in ("tag", "maybe", "bare", "belief")]
    (GEN / "arm_rows.tex").write_text("\n".join(rows) + "\n")
    rows = [f"{names[a]} & {p(fav[a]['favored'])} [{ci(fav[a]['favored_ci95'])}] & {p(fav[a]['disfavored'])} [{ci(fav[a]['disfavored_ci95'])}] \\\\"
            for a in ("tag", "maybe", "bare", "belief")]
    (GEN / "fav_rows.tex").write_text("\n".join(rows) + "\n")
    rows = [f"{names[a]} & {p(S[a]['left_claims'])} & {p(S[a]['right_claims'])} \\\\" for a in ("tag", "maybe", "bare", "belief")]
    (GEN / "leftright_rows.tex").write_text("\n".join(rows) + "\n")


if __name__ == "__main__":
    import sys
    if "--numbers" not in sys.argv:
        main()
    numbers()
