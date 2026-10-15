"""probe_brand_logprob.py — at each training stage, how likely is the panel's Name brand, and its pick brand, under each verb?

The sampled stage ladders (stage_brands, stage_pick) score the pick only on the lists that name both brands, which
leaves 13-19 categories per stage, and they cannot reach the base model, which does not hold a conversation. This
probe measures the same contrast by forward passes, on every brand category and every stage, base included.

Verbs (clamped, one name asked for; a reply that is the brand is scored by its log-probability):
  name        "Name a soda brand. Reply with the name only."
  choose      "Choose a soda brand. Reply with the name only."
  recommend   "Can you recommend a soda brand? Reply with the name only."
  recommend2  "What soda brand would you recommend? Reply with the name only."        (paraphrase)
  recommend3  "I'm looking for a soda brand. Any suggestions? Reply with the name only."  (paraphrase)
The two paraphrases are spec/perturb/stimulus_brands_recommend2/3.json with the clamp appended, so the Recommend
shift is read against a paraphrase floor (Jack et al.).

Candidates per category: the panel's top five answers under clamped Name, Choose and Recommend and its top three
two-turn picks (as served, brand_ladder.levels()). Each candidate's log-probability sums its spellings (as scored,
first letter capitalised, each word capitalised). The base stage reads "<question>\\nAnswer: <brand>", tuned stages the
no-system-prompt chat turn (probe_verb_ladder.tuned_framing).

The two-turn pick with the list held fixed: turn 1 is a fixed three-item list of the panel's Name brand, its pick
brand and a third brand (its next Recommend answer), in both orders of the first two; turn 2 is "Which one would you
pick?", and the reply is scored from "I'd pick ". The base stage reads the same exchange as "Q:"/"A:" text. Only
categories whose panel pick differs from its Name brand.

    ../../.venv/bin/python probe_brand_logprob.py run olmo3-7b       # -> probes/brand_logprob/<pipeline>.json
    ../../.venv/bin/python probe_brand_logprob.py score              # -> probes/brand_logprob.json

The own-list check (ownlist): the same forced "I'd pick " score, but turn 1 is the SFT stage's own sampled Recommend
reply, on the lists that name both panel brands (probe_verb_ladder.head_to_head_runs, the lists the sampled K=5
held-fixed picks used). It tests whether the fixed three-item list gives the same stage steps as the stage's own
long, described lists.

    ../../.venv/bin/python probe_brand_logprob.py ownlist olmo3-7b   # -> probes/brand_logprob/ownlist/<pipeline>.json
    ../../.venv/bin/python probe_brand_logprob.py ownscore           # -> probes/brand_logprob_ownlist.json
"""
import json, math, random, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "harness"))
OUT = HERE / "probes" / "brand_logprob"
PIPES = ("olmo3-7b", "tulu3-8b", "olmo31-32b", "nemotron35-lightning")
CLAMP = " Reply with the name only."
PICK = "Which one would you pick?"
LEAD = "I'd pick "
VERB_FILES = {"name": ("stimulus_brands.json", "stimulus_brands_ext.json", "stimulus_brands_ext2.json"),
              "choose": ("perturb/stimulus_brands_choose.json", "perturb/stimulus_brands_ext_choose.json",
                         "perturb/stimulus_brands_ext2_choose.json"),
              "recommend": ("perturb/stimulus_brands_recommend_clamp.json", "perturb/stimulus_brands_ext2_recommend_clamp.json"),
              "recommend2": ("perturb/stimulus_brands_recommend2.json",),
              "recommend3": ("perturb/stimulus_brands_recommend3.json",)}


def questions():
    """verb -> category -> the clamped question."""
    out = {}
    for verb, files in VERB_FILES.items():
        for f in files:
            for s in json.loads((HERE / "spec" / f).read_text())["scenes"]:
                q = s["turns"][0]
                out.setdefault(verb, {})[s["id"].split("__")[0]] = q if q.endswith(CLAMP) else q + CLAMP
    return out


def free_recommend():
    """category -> the free Recommend question (turn 1 of the two-turn pick)."""
    return {s["id"].split("__")[0]: s["turns"][0] for f in ("stimulus_brands_pick.json", "stimulus_brands_ext2_pick.json")
            for s in json.loads((HERE / "spec" / f).read_text())["scenes"]}


def panel():
    """category -> panel brands (name, choose, recommend, pick, third) and the candidate list, from the API panel as
    served. Generic categories (company, brand) left out."""
    import brand_ladder as B
    lv = B.levels()
    agg = {k: B.agg(lv[k]) for k in ("name", "choose", "recommend_clamp", "pick2")}
    out = {}
    for c in sorted(agg["pick2"]):
        if c in B.GENERIC or c not in agg["name"]:
            continue
        common = lambda k, n: [a for a, _ in agg[k].get(c, {}).most_common(n + 1) if a != B.NO_PICK][:n]
        row = {"name": B.top(agg["name"][c])[0], "choose": B.top(agg["choose"].get(c, {}))[0],
               "recommend": B.top(agg["recommend_clamp"].get(c, {}))[0], "pick": B.top(agg["pick2"][c])[0]}
        row["third"] = next((a for a in common("recommend_clamp", 5) if a not in (row["name"], row["pick"])), None)
        row["candidates"] = list(dict.fromkeys(common("name", 5) + common("choose", 5) + common("recommend_clamp", 5)
                                               + common("pick2", 3)))
        out[c] = row
    return out


def display(a):
    """A canonical (lowercase) brand as a list item would write it."""
    return " ".join(w[:1].upper() + w[1:] for w in a.split())


def forms(a):
    return list(dict.fromkeys([a, a[:1].upper() + a[1:], display(a)]))


def logprob(model, tok, prefix, answer, lead):
    """Log-probability of `answer` continuing `prefix` token ids, summed over its spellings."""
    import mlx.core as mx
    totals = []
    for form in forms(answer):
        ans = tok.encode(lead + form, add_special_tokens=False)
        logits = model(mx.array([list(prefix) + ans]))[0]
        lp = logits - mx.logsumexp(logits, axis=-1, keepdims=True)
        totals.append(float(sum(lp[len(prefix) + i - 1, t].item() for i, t in enumerate(ans))))
    m = max(totals)
    return round(m + math.log(sum(math.exp(x - m) for x in totals)), 4)


def turn1(order):
    return "Here are a few good options:\n\n" + "\n".join(f"{i}. **{display(a)}**" for i, a in enumerate(order, 1))


def pick_prefix(tok, st, framing, q1, a1):
    """Token ids of the two-turn exchange up to the forced reply opening, in the stage's framing."""
    if framing == "raw":
        return tok.encode(f"Q: {q1}\nA: {a1}\nQ: {PICK}\nA: {LEAD.strip()}")
    from probe_verb_ladder import pick2_encode
    return list(pick2_encode(tok, st, framing, q1, a1)) + tok.encode(LEAD.strip(), add_special_tokens=False)


def run(pipe):
    import local
    from probe_verb_ladder import stages, tuned_framing
    qs, rec, pn = questions(), free_recommend(), panel()
    path = OUT / f"{pipe}.json"
    res = json.loads(path.read_text()) if path.exists() else {"pipeline": pipe, "panel": pn, "stages": {}}
    for st in stages(pipe):
        if st["stage"] in res["stages"]:
            print(f"skip {st['label']}: already scored", flush=True)
            continue
        base = st["stage"] == "base"
        f = "raw" if base else tuned_framing(st)
        model, tok = local.load(st)
        row = {"framing": f, "revision": local.revision(st["repo"], st["weights"]), "verbs": {}, "pick": {}}
        for verb, cq in qs.items():
            for c, p in pn.items():
                if c in cq:
                    pre = local.encode(tok, st, f, cq[c])
                    row["verbs"].setdefault(verb, {})[c] = {a: logprob(model, tok, pre, a, " " if base else "")
                                                             for a in p["candidates"]}
        for c, p in pn.items():
            if p["pick"] == p["name"] or not p["third"] or c not in rec:
                continue
            for key, order in (("name_first", (p["name"], p["pick"], p["third"])),
                               ("pick_first", (p["pick"], p["name"], p["third"]))):
                pre = pick_prefix(tok, st, f, rec[c], turn1(order))
                row["pick"].setdefault(c, {})[key] = {a: logprob(model, tok, pre, a, " ") for a in order}
        res["stages"][st["stage"]] = row
        OUT.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(res, indent=1) + "\n")
        print(f"logprob {st['label']}: {len(pn)} categories, {len(row['pick'])} pick lists", flush=True)
        del model
        local.free()


def boot(xs, n=2000, seed=0):
    """Mean and 90% bootstrap interval over categories."""
    if not xs:
        return None
    rng = random.Random(seed)
    ms = sorted(sum(rng.choice(xs) for _ in xs) / len(xs) for _ in range(n))
    return {"mean": round(sum(xs) / len(xs), 3), "ci90": [round(ms[int(.05 * n)], 3), round(ms[int(.95 * n)], 3)], "n": len(xs)}


def score():
    """Per pipeline and stage, over categories whose panel pick (or Recommend brand) differs from its Name brand:
      gap[verb]   mean log P(target) - log P(name brand) under the verb (log-odds of target over Name, in nats)
      shift[verb] gap under the verb minus gap under Name: how far the verb moves the stage toward the target
      pick_h2h    P(pick) / (P(pick) + P(name)) on the fixed list, averaged over the two orders
      order_gap   the same with the pick listed first minus listed second (the position effect)
    and the change in each between consecutive stages, paired by category, with a bootstrap interval."""
    out = {}
    for f in sorted(OUT.glob("*.json")):
        d = json.loads(f.read_text())
        pn, rows = d["panel"], {}
        for stage, r in d["stages"].items():
            row = {}
            for tgt in ("pick", "recommend"):
                cats = [c for c, p in pn.items() if p[tgt] and p[tgt] != p["name"]]
                gap = {v: {c: r["verbs"][v][c][pn[c][tgt]] - r["verbs"][v][c][pn[c]["name"]]
                           for c in cats if c in r["verbs"].get(v, {})} for v in r["verbs"]}
                row[tgt] = {"gap": {v: boot(list(g.values())) for v, g in gap.items()},
                            "shift": {v: boot([g[c] - gap["name"][c] for c in g if c in gap["name"]])
                                      for v, g in gap.items() if v != "name"},
                            "_shift": {v: {c: g[c] - gap["name"][c] for c in g if c in gap["name"]}
                                       for v, g in gap.items() if v != "name"}}
            h2h, order = {}, {}
            for c, o in r["pick"].items():
                p = pn[c]
                share = lambda lp: 1 / (1 + math.exp(lp[p["name"]] - lp[p["pick"]]))
                h2h[c] = (share(o["name_first"]) + share(o["pick_first"])) / 2
                order[c] = share(o["pick_first"]) - share(o["name_first"])
            row["pick_h2h"], row["order_gap"], row["_h2h"] = boot(list(h2h.values())), boot(list(order.values())), h2h
            rows[stage] = row
        names = list(d["stages"])
        steps = {}
        for a, b in zip(names, names[1:]):
            s = {"pick_h2h": boot([rows[b]["_h2h"][c] - rows[a]["_h2h"][c] for c in rows[b]["_h2h"] if c in rows[a]["_h2h"]])}
            for v in rows[b]["pick"]["_shift"]:
                x, y = rows[a]["pick"]["_shift"].get(v, {}), rows[b]["pick"]["_shift"][v]
                s[f"shift_{v}"] = boot([y[c] - x[c] for c in y if c in x])
            steps[f"{a}->{b}"] = s
        for row in rows.values():
            row.pop("_h2h")
            for t in ("pick", "recommend"):
                row[t].pop("_shift")
        out[d["pipeline"]] = {"stages": rows, "steps": steps}
        print(f"\n{d['pipeline']}")
        for stage, row in rows.items():
            sh = row["pick"]["shift"]
            print(f"  {stage:6} pick-over-Name shift: " + "  ".join(f"{v} {sh[v]['mean']:+.2f} {sh[v]['ci90']}" for v in sh if sh[v])
                  + (f"   fixed-list pick {row['pick_h2h']['mean']:.0%} {row['pick_h2h']['ci90']}, order {row['order_gap']['mean']:+.2f}"
                     if row["pick_h2h"] else ""))
        for k, s in steps.items():
            print(f"  {k:12} " + "  ".join(f"{v} {x['mean']:+.2f} {x['ci90']}" for v, x in s.items() if x))
    (HERE / "probes" / "brand_logprob.json").write_text(json.dumps(out, indent=1) + "\n")


def ownlist(pipe):
    import local
    from probe_verb_ladder import stages, tuned_framing, pick2_encode, head_to_head_runs
    sp = json.loads((HERE / "probes" / "stage_pick.json").read_text())["panel_brands"]
    sts = stages(pipe)
    sft = next(s for s in sts if s["stage"] == "sft")
    rec_path = local.path(HERE / "probes" / f"verb_ladder_{pipe}" / "recommend", sft, tuned_framing(sft))
    rec = json.loads(rec_path.read_text())
    runs = head_to_head_runs(rec)
    path = OUT / "ownlist" / f"{pipe}.json"
    res = json.loads(path.read_text()) if path.exists() else {"pipeline": pipe, "turn1": str(rec_path.relative_to(HERE)),
                                                              "panel": sp, "stages": {}}
    for st in sts:
        if st["stage"] == "base" or st["stage"] in res["stages"]:
            continue
        f = tuned_framing(st)
        model, tok = local.load(st)
        row = {"framing": f, "revision": local.revision(st["repo"], st["weights"]), "lists": {}}
        for sid, ks in runs.items():
            c = sid.split("__")[0]
            pair = (sp[c]["name"], sp[c]["pick"])
            for k in ks:
                t1 = rec["scenes"][sid]["runs"][k][0]
                pre = list(pick2_encode(tok, st, f, t1["u"], t1["reply"])) + tok.encode(LEAD.strip(), add_special_tokens=False)
                row["lists"].setdefault(c, {})[str(k)] = {a: logprob(model, tok, pre, a, " ") for a in pair}
        res["stages"][st["stage"]] = row
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(res, indent=1) + "\n")
        print(f"ownlist {st['label']}: {len(row['lists'])} categories, {sum(map(len, row['lists'].values()))} lists", flush=True)
        del model
        local.free()


def ownscore():
    """Per pipeline and stage: P(pick) / (P(pick) + P(name)) on the SFT stage's own lists, averaged per category then over
    categories; and the paired step between stages."""
    out = {}
    for f in sorted((OUT / "ownlist").glob("*.json")):
        d = json.loads(f.read_text())
        pn = d["panel"]
        share = {}
        for stage, r in d["stages"].items():
            share[stage] = {c: sum(1 / (1 + math.exp(lp[pn[c]["name"]] - lp[pn[c]["pick"]])) for lp in ls.values()) / len(ls)
                            for c, ls in r["lists"].items()}
        names = list(share)
        out[d["pipeline"]] = {"stages": {s: boot(list(v.values())) for s, v in share.items()},
                              "steps": {f"{a}->{b}": boot([share[b][c] - share[a][c] for c in share[b] if c in share[a]])
                                        for a, b in zip(names, names[1:])}}
        print(f"\n{d['pipeline']} (SFT's own lists)")
        for s, x in out[d["pipeline"]]["stages"].items():
            print(f"  {s:6} pick share {x['mean']:.0%} {x['ci90']} ({x['n']} categories)")
        for s, x in out[d["pipeline"]]["steps"].items():
            print(f"  {s:10} {x['mean']:+.2f} {x['ci90']}")
    (HERE / "probes" / "brand_logprob_ownlist.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "run":
        run(sys.argv[2])
    elif len(sys.argv) > 1 and sys.argv[1] == "score":
        score()
    elif len(sys.argv) > 2 and sys.argv[1] == "ownlist":
        ownlist(sys.argv[2])
    elif len(sys.argv) > 1 and sys.argv[1] == "ownscore":
        ownscore()
    else:
        print(__doc__)
