"""
probe_open.py — the shape of the open-ended replies: what models do when the one-word clamp is off.

The free-wording runs, as served (the reasoning-off arms are left out):

  name       "Name a X." for 137 prompts (spec/clamp.json and clamp_ext.json free halves, clamp_free_all.json,
             clamp_free_brands_ext.json, clamp_free_brands_ext2.json), ~100 models x 4 runs
  choose     "Choose X."                                   } 44 brand nouns (spec/stimulus_brands_*.json and their
  recommend  "Can you recommend X?"                        } _ext2_ versions), ~120 models x 4 runs
  pick1      "Which X would you pick?"                     }
  pick2      "Can you recommend X?" then "Which one would you pick?" (scored on turn 2)

Every reply is measured without a judge:

  words      whitespace tokens after markdown is stripped
  mentions   pool answers named, in order (probe_clamp.mentions). The pool is the field's one-word answers for the
             category (probe_clamp: its clamped re-ask, else the battery), and for brand nouns the Name and Choose
             batteries' brands, as probe_recommend; answers named twice or more, minus words of the question
  first      the first mention: the prose analogue of the one-word choice
  bare       four words or fewer
  list       three or more mentions, or three or more bullet or numbered lines
  asks       a question mark in the reply (a clarifying question back, or an offer)
  disclaims  "as an AI", "I don't have personal preferences" and the like
  bold       markdown bold anywhere

Reported per group, per category, per model and per vendor; for the brand nouns the first mention is also compared
across the five forms (does a model name, choose, recommend and pick the same brand?), and pick2's turn-2 pick against
its own turn-1 list. These are characterizations from string matching: check a pattern against the replies in the
viewer (views/open.html) before reporting it.

    python probe_open.py      # -> probes/open.json
"""
import json
import re
import statistics as st
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from analyze import answers                                      # noqa: E402
from probe_clamp import battery_pool, load as clamp_load, mentions, patterns  # noqa: E402

NAME_DIRS = ["transcripts-clamp", "transcripts-clamp-ext", "transcripts-clamp-free",
             "transcripts-clamp-free-brands-ext", "transcripts-clamp-free-brands-ext2"]
FORMS = {  # form -> (transcript dirs, scene-id suffix)
    "choose": (["transcripts-brands-choose-free", "transcripts-brands-ext2-choose-free"], "__choosefree"),
    "recommend": (["transcripts-brands-recommend-free", "transcripts-brands-ext2-recommend-free"], "__recommend"),
    "pick1": (["transcripts-brands-pick1-free", "transcripts-brands-ext2-pick1-free"], "__youpick"),
    "pick2": (["transcripts-brands-pick2-free", "transcripts-brands-ext2-pick2-free"], "__pick"),
}
GROUPS = ["name", "name-brand", "choose", "recommend", "pick1", "pick2"]
VENDOR = {"anthropic": "Anthropic", "openai": "OpenAI", "google": "Google", "x-ai": "xAI", "meta-llama": "Meta",
          "deepseek": "DeepSeek", "moonshotai": "Moonshot", "qwen": "Qwen", "z-ai": "Z.ai", "mistralai": "Mistral",
          "minimax": "MiniMax", "cohere": "Cohere", "baidu": "Baidu", "tencent": "Tencent", "stepfun": "StepFun",
          "nvidia": "NVIDIA", "ibm-granite": "IBM", "microsoft": "Microsoft", "writer": "Writer", "amazon": "Amazon",
          "perplexity": "Perplexity", "nousresearch": "Nous", "inclusionai": "inclusionAI", "xiaomi": "Xiaomi",
          "meta": "Meta", "gryphe": "Gryphe", "thinkingmachines": "Thinking Machines", "bytedance-seed": "ByteDance",
          "reflection": "Reflection", "liquid": "Liquid"}

MD = re.compile(r"[*_`#>|]+")
BULLET = re.compile(r"^\s*([-*•]|\d+[.)])\s+", re.M)
DISCLAIM = re.compile(r"as an ai\b|as a language model|i don'?t have (personal |my own )?(preferences|opinions|tastes?|"
                      r"feelings|favorites?)|i don'?t (personally )?(eat|drink|use|taste|wear|drive)|"
                      r"i can'?t (personally )?(choose|pick|taste|drink|eat)|i'?m an ai|i do not have (personal )?"
                      r"(preferences|opinions)|not able to (have|form) (personal )?preferences", re.I)


def vendor(slug):
    p = slug.split("/")[0]
    return VENDOR.get(p, p)


def noun(prompt):
    """'Name a soda brand.' or 'Can you recommend a soda brand?' -> 'a soda brand'; the join key across the forms."""
    p = prompt.strip().rstrip(".?")
    for pre in ("Name ", "Can you recommend "):
        p = p.removeprefix(pre)
    return p


def measure(reply, pats):
    ms = mentions(reply, pats) if pats else []
    words = len(MD.sub(" ", reply).split())
    return {"words": words, "mentions": ms, "first": ms[0] if ms else None, "bare": words <= 4,
            "list": len(ms) >= 3 or len(BULLET.findall(reply)) >= 3, "asks": "?" in reply,
            "disclaims": bool(DISCLAIM.search(reply)), "bold": "**" in reply}


def brand_pools():
    """noun -> brand regexes, from the Name and Choose batteries (probe_recommend's pool), and brand category id ->
    noun (the forms' scene ids carry the category; 'Which electric car brand' has lost its article)."""
    pool, asked = {}, {}
    for src in (answers(HERE, "brands_all"), answers(HERE, "choose_brands_all")):
        for cats in src.values():
            for c, xs in cats.items():
                pool.setdefault(c, Counter()).update(xs)
    for f in ("stimulus_brands_recommend.json", "stimulus_brands_ext2_recommend.json"):
        for sc in json.loads((HERE / "spec" / f).read_text())["scenes"]:
            asked[sc["id"].removesuffix("__recommend")] = sc["turns"][0]
    out = {}
    for c, q in asked.items():
        keep = [a for a, k in pool.get(c, {}).items() if k >= 2 and not re.search(rf"\b{re.escape(a)}\b", q.lower())]
        out[noun(q)] = patterns("brand_" + c, keep)
    return out, {c: noun(q) for c, q in asked.items()}


def name_pools():
    """category -> regexes for the Name prompts, from probe_clamp's pool, minus words of the question."""
    clamp, free = clamp_load(NAME_DIRS)
    battery_pool(clamp, free)
    return {c: Counter(x for xs in ms.values() for x in xs) for c, ms in clamp.items()}


def records():
    """Every open-ended reply, measured. One dict per (group, prompt, model, run)."""
    (bpats, nouns), npool = brand_pools(), name_pools()
    out = []
    for d in NAME_DIRS:
        for p in sorted((HERE / d).glob("*.json")):
            t = json.loads(p.read_text())
            for sid, s in t["scenes"].items():
                cat, cond = sid.rsplit("_", 1)
                if cond != "free":
                    continue
                for i, r in enumerate(s["runs"]):
                    if not r:
                        continue
                    prompt, reply = r[0]["u"], r[0].get("reply") or ""
                    n = noun(prompt)
                    if n in bpats:
                        group, pats = "name-brand", bpats[n]
                    else:
                        pool = npool.get(cat, Counter())
                        modal = pool.most_common(1)[0][0] if pool else None
                        qw = set(re.findall(r"[a-z\-]+", prompt.lower()))
                        group = "name"
                        pats = patterns(cat, [a for a, k in pool.items() if (k >= 2 or a == modal) and a not in qw])
                    out.append({"group": group, "key": n, "prompt": prompt, "model": t["model"],
                                "vendor": vendor(t["slug"]), "run": i, "turns": [{"u": prompt, "reply": reply}],
                                **measure(reply, pats)})
    for form, (dirs, suf) in FORMS.items():
        for d in dirs:
            for p in sorted((HERE / d).glob("*.json")):
                t = json.loads(p.read_text())
                for sid, s in t["scenes"].items():
                    for i, r in enumerate(s["runs"]):
                        if not r:
                            continue
                        n = nouns[sid.removesuffix(suf)]
                        pats = bpats.get(n, {})
                        reply = r[-1].get("reply") or ""
                        rec = {"group": form, "key": n, "prompt": " / ".join(x["u"] for x in r), "model": t["model"],
                               "vendor": vendor(t["slug"]), "run": i,
                               "turns": [{"u": x["u"], "reply": x.get("reply") or ""} for x in r], **measure(reply, pats)}
                        if form == "pick2" and len(r) > 1:
                            rec["t1_mentions"] = mentions(r[0].get("reply") or "", pats)
                        out.append(rec)
    return out


def rate(xs, f):
    return round(sum(f(x) for x in xs) / len(xs), 3) if xs else None


def summary(rs):
    """Shape measures over a set of records."""
    firsts = Counter(r["first"] for r in rs if r["first"])
    named = sum(firsts.values())
    top = firsts.most_common(1)[0] if firsts else (None, 0)
    return {"n": len(rs), "median_words": st.median(r["words"] for r in rs) if rs else None,
            "bare": rate(rs, lambda r: r["bare"]), "list": rate(rs, lambda r: r["list"]),
            "asks": rate(rs, lambda r: r["asks"]), "disclaims": rate(rs, lambda r: r["disclaims"]),
            "bold": rate(rs, lambda r: r["bold"]), "no_mention": rate(rs, lambda r: not r["first"]),
            "top_first": top[0], "top_first_share": round(top[1] / named, 3) if named else None,
            "distinct_first": len(firsts)}


def consistency(rs):
    """Share of (model, prompt) cells whose runs all open on the same answer, over cells with 2+ named runs."""
    cells = defaultdict(list)
    for r in rs:
        if r["first"]:
            cells[(r["model"], r["key"])].append(r["first"])
    ok = [len(set(v)) == 1 for v in cells.values() if len(v) >= 2]
    return round(sum(ok) / len(ok), 3) if ok else None


def main():
    rs = records()
    by = defaultdict(list)
    for r in rs:
        by[r["group"]].append(r)
    groups = {g: {**summary(by[g]), "prompts": len({r["key"] for r in by[g]}), "models": len({r["model"] for r in by[g]}),
                  "consistency": consistency(by[g])} for g in GROUPS}
    print(f"\n{'group':11} {'prompts':>7} {'models':>6} {'replies':>7} {'words':>5} {'bare':>5} {'list':>5} {'asks':>5} "
          f"{'discl':>5} {'bold':>5} {'none':>5} {'consist':>7}")
    for g, v in groups.items():
        print(f"{g:11} {v['prompts']:7} {v['models']:6} {v['n']:7} {v['median_words']:5} {v['bare']:5.0%} {v['list']:5.0%} "
              f"{v['asks']:5.0%} {v['disclaims']:5.0%} {v['bold']:5.0%} {v['no_mention']:5.0%} {v['consistency']:7.0%}")

    per_prompt = {}
    for g in GROUPS:
        keys = defaultdict(list)
        for r in by[g]:
            keys[r["key"]].append(r)
        per_prompt[g] = {k: {**summary(v), "top5": Counter(r["first"] for r in v if r["first"]).most_common(5)}
                         for k, v in keys.items()}

    name = by["name"] + by["name-brand"]
    print("\nName prompts: longest median replies, and where the field disclaims or lists most")
    nk = {**per_prompt["name"], **per_prompt["name-brand"]}
    for lab, f in (("words", "median_words"), ("list", "list"), ("asks", "asks"), ("disclaims", "disclaims")):
        top = sorted(nk.items(), key=lambda kv: -(kv[1][f] or 0))[:6]
        print(f"  {lab:9} " + "; ".join(f"{k} {v[f]:.0%}" if f != "median_words" else f"{k} {v[f]}" for k, v in top))

    per_model = {}
    for g in ("name", "recommend"):
        mm = defaultdict(list)
        for r in (name if g == "name" else by[g]):
            mm[r["model"]].append(r)
        for m, v in mm.items():
            per_model.setdefault(m, {"vendor": v[0]["vendor"]})[g] = {**summary(v), "consistency": consistency(v)}
    per_vendor = {}
    for g in ("name", "recommend"):
        vv = defaultdict(list)
        for r in (name if g == "name" else by[g]):
            vv[r["vendor"]].append(r)
        for vd, v in vv.items():
            if len({r["model"] for r in v}) >= 3:
                per_vendor.setdefault(vd, {"models": len({r["model"] for r in v})})[g] = summary(v)
    print(f"\n{'vendor':12} {'models':>6}  name: words bare list asks discl | recommend: words list asks discl")
    for vd, v in sorted(per_vendor.items(), key=lambda kv: -kv[1]["models"]):
        a, b = v.get("name"), v.get("recommend")
        fa = f"{a['median_words']:5} {a['bare']:4.0%} {a['list']:4.0%} {a['asks']:4.0%} {a['disclaims']:5.0%}" if a else " " * 27
        fb = f"{b['median_words']:5} {b['list']:4.0%} {b['asks']:4.0%} {b['disclaims']:5.0%}" if b else ""
        print(f"{vd:12} {v['models']:6}  {fa} | {fb}")

    # the brand nouns across the five forms: each model's modal first mention per form, agreement between forms
    forms = ["name-brand", "choose", "recommend", "pick1", "pick2"]
    top = defaultdict(dict)
    for g in forms:
        cells = defaultdict(list)
        for r in by[g]:
            if r["first"]:
                cells[(r["model"], r["key"])].append(r["first"])
        for cell, v in cells.items():
            top[cell][g] = Counter(v).most_common(1)[0][0]
    agree = {}
    for i, a in enumerate(forms):
        for b in forms[i + 1:]:
            both = [v for v in top.values() if a in v and b in v]
            agree[f"{a}~{b}"] = {"cells": len(both), "same": rate(both, lambda v: v[a] == v[b])}
    print("\nbrand nouns: share of (model, noun) cells whose top first-mention agrees between two forms")
    for k, v in agree.items():
        print(f"  {k:22} {v['same']:.0%}  ({v['cells']} cells)")
    field = {g: {k: per_prompt[g][k]["top_first"] for k in per_prompt[g]} for g in forms}
    shifts = []
    for k in per_prompt["recommend"]:
        row = {g: (per_prompt[g].get(k) or {}).get("top_first") for g in forms}
        row.update({g + "_share": (per_prompt[g].get(k) or {}).get("top_first_share") for g in forms})
        if len({row[g] for g in forms if row[g]}) > 1:
            shifts.append((k, row))
    print(f"\nbrand nouns where the field's top first-mention changes with the form: {len(shifts)}/{len(per_prompt['recommend'])}")
    for k, row in shifts:
        print(f"  {k:30} " + " | ".join(f"{g}: {row[g]} {row[g + '_share']:.0%}" if row[g] else f"{g}: -" for g in forms))

    p2 = [r for r in by["pick2"] if r["first"] and r.get("t1_mentions")]
    pick2 = {"scored": len(p2), "in_turn1_list": rate(p2, lambda r: r["first"] in r["t1_mentions"]),
             "turn1_first": rate(p2, lambda r: r["first"] == r["t1_mentions"][0]),
             "turn1_list_len_median": st.median(len(r["t1_mentions"]) for r in p2) if p2 else None}
    print(f"\npick2: turn-2 pick is in its own turn-1 list {pick2['in_turn1_list']:.0%}, is the first brand it listed "
          f"{pick2['turn1_first']:.0%} (median turn-1 list {pick2['turn1_list_len_median']} brands, {len(p2)} replies)")

    (HERE / "probes" / "open.json").write_text(json.dumps(
        {"groups": groups, "per_prompt": per_prompt, "per_model": per_model, "per_vendor": per_vendor,
         "brand_form_agreement": agree, "brand_form_shifts": dict(shifts), "field_top_first": field, "pick2": pick2},
        indent=1, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
