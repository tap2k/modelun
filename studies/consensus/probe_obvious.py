"""probe_obvious.py — does preference training move judgments away from the obvious answer, defined without the panel?

"Obvious" is the base model's own view: a candidate's log-probability as the reply to the Name question at the base
stage (normalised over the category's candidates). For every category, brand (probe_brand_logprob.py, all 42) and
census (probe_answer_logprob.py, every category with candidates), per pipeline and stage step:

  top_share   the probability, under the judgment verb (brands: Recommend; census: Choose), of the base model's
              Name favourite, and its change from one stage to the next; the same under Name as a control
  rank_slope  the within-category Spearman correlation between a candidate's base Name log-probability and the change
              in its judgment-minus-Name log-probability over the step (negative: the step favours less obvious
              candidates when a judgment is asked for), averaged over categories

Each with a 90% bootstrap interval over categories. Zero model calls; reads the stored log-probabilities.

    ../../.venv/bin/python probe_obvious.py        # -> probes/obvious.json
"""
import json, math, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from probe_brand_logprob import boot  # noqa: E402

PIPES = ("olmo3-7b", "tulu3-8b", "olmo31-32b")
STEPS = (("base", "sft"), ("sft", "dpo"), ("dpo", "rl"))


def norm(lp):
    """log-softmax over a category's candidates."""
    m = max(lp.values())
    z = m + math.log(sum(math.exp(v - m) for v in lp.values()))
    return {a: v - z for a, v in lp.items()}


def spearman(x, y):
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        for k, i in enumerate(order):
            r[i] = k
        return r
    rx, ry = ranks(x), ranks(y)
    n = len(x)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else 0.0


def brand_tables(p):
    """stage -> verb -> category -> {candidate: normalised log-prob}, for name and recommend."""
    d = json.loads((HERE / "probes" / "brand_logprob" / f"{p}.json").read_text())
    return {st: {v: {c: norm(lp) for c, lp in r["verbs"][v].items()} for v in ("name", "recommend")}
            for st, r in d["stages"].items()}


def census_tables(p):
    d = json.loads((HERE / "probes" / f"answer_logprob_{p}.json").read_text())["categories"]
    out = {}
    for c, row in d.items():
        for v, by in row.items():
            if v == "candidates":
                continue
            for st, probs in by.items():
                out.setdefault(st, {}).setdefault({"choose": "recommend"}.get(v, v), {})[c] = \
                    norm({a: math.log(max(x, 1e-4)) for a, x in probs.items()})
    return out


def analyse(t):
    """t: stage -> {'name','recommend'} -> category -> normalised log-probs ('recommend' holds the judgment verb)."""
    cats = [c for c in t["base"]["name"] if all(c in t[s]["recommend"] and c in t[s]["name"] for s in t)]
    top = {c: max(t["base"]["name"][c], key=t["base"]["name"][c].get) for c in cats}
    res = {"categories": len(cats), "top_share": {}, "steps": {}}
    for s in t:
        for v in ("recommend", "name"):
            res["top_share"].setdefault(v, {})[s] = boot([math.exp(t[s][v][c][top[c]]) for c in cats])
    for a, b in STEPS:
        if a not in t or b not in t:
            continue
        slopes, dtop, dtop_name = [], [], []
        for c in cats:
            base = t["base"]["name"][c]
            gap = lambda s, x: t[s]["recommend"][c][x] - t[s]["name"][c][x]
            xs = list(base)
            if len(xs) >= 3:
                slopes.append(spearman([base[x] for x in xs], [gap(b, x) - gap(a, x) for x in xs]))
            dtop.append(math.exp(t[b]["recommend"][c][top[c]]) - math.exp(t[a]["recommend"][c][top[c]]))
            dtop_name.append(math.exp(t[b]["name"][c][top[c]]) - math.exp(t[a]["name"][c][top[c]]))
        res["steps"][f"{a}->{b}"] = {"rank_slope": boot(slopes), "top_share_change": boot(dtop),
                                     "top_share_change_name": boot(dtop_name)}
    return res


def runner_up(p):
    """The base model's second choice under Name against the panel's pick brand, over the categories where the pick
    differs from Name: how often they coincide, and whether DPO raises the pick's Recommend odds over the Name brand
    more than the runner-up's (the squeezing account predicts the runner-up)."""
    d = json.loads((HERE / "probes" / "brand_logprob" / f"{p}.json").read_text())
    pn, S = d["panel"], d["stages"]
    same = n = more = 0
    for c, b in pn.items():
        if b["pick"] == b["name"]:
            continue
        base = S["base"]["verbs"]["name"][c]
        ru = next(a for a in sorted(base, key=lambda a: -base[a]) if a != b["name"])
        n += 1
        if ru == b["pick"]:
            same += 1
            continue
        rec = lambda st, x: S[st]["verbs"]["recommend"][c][x] - S[st]["verbs"]["recommend"][c][b["name"]]
        more += (rec("dpo", b["pick"]) - rec("sft", b["pick"])) > (rec("dpo", ru) - rec("sft", ru))
    return {"categories": n, "runner_up_is_pick": same, "pick_gains_more": more, "compared": n - same}


def main():
    out = {}
    for p in PIPES:
        out[p] = {"brands": analyse(brand_tables(p)), "census": analyse(census_tables(p)), "runner_up": runner_up(p)}
        print(f"{p} runner-up: {out[p]['runner_up']}")
        for dom in ("brands", "census"):
            r = out[p][dom]
            print(f"\n{p} {dom} ({r['categories']} categories): base-Name favourite's share under the judgment verb / under Name")
            for s in r["top_share"]["recommend"]:
                print(f"  {s:5} {r['top_share']['recommend'][s]['mean']:.0%}  /  {r['top_share']['name'][s]['mean']:.0%}")
            for k, x in r["steps"].items():
                print(f"  {k:9} favourite under judgment {x['top_share_change']['mean']:+.2f} {x['top_share_change']['ci90']}"
                      f"  under Name {x['top_share_change_name']['mean']:+.2f}   rank slope {x['rank_slope']['mean']:+.2f} {x['rank_slope']['ci90']}")
    (HERE / "probes" / "obvious.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
