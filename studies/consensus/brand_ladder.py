"""brand_ladder.py — the brand verb ladder: does a model's one-word brand default survive as the question gets
more like a real conversation?

Nine levels, the same 44 brand categories and the same panel, every model as served (spec/runs.json ids; each
level reads the 41-category run and its brands-ext2-* run for the three categories added on 2026-10-03):

  name         "Name a soda brand. Reply with the name only."   brands, -ext, -ext2       whole-name scorer
  free_name    "Name a soda brand."                              free-all, free-brands-ext(2), clamp-ext   first mention
  choose       "Choose a soda brand. Reply with the name only."  brands-choose, -ext-, -ext2-choose   whole-name scorer
  free_choose  "Choose a soda brand."                            brands-(ext2-)choose-free     committed brand
  pick1_clamp  "Which soda brand would you pick? Reply with the name only."   brands-(ext2-)pick1-clamp   whole-name
  pick1        "Which soda brand would you pick?"                brands-(ext2-)pick1-free      committed brand
  recommend_clamp "Can you recommend a soda brand? Reply with the name only."  brands-(ext2-)recommend-clamp  whole-name
  recommend    "Can you recommend a soda brand?"                 brands-(ext2-)recommend-free  first mention
  pick2        recommend, then "Which one would you pick?"       brands-(ext2-)pick2-free      committed brand, turn 2

A free reply is reduced to one brand in one of two ways. "First mention" (free Name, Recommend) is the first brand
from the Name and Choose answer pools that the reply names. "Committed brand" (free Choose, both picks) is the brand
the reply commits to: the brand it opens with, or the one that follows "I'd pick", "I choose", "let's go with", "my
pick is" and similar, mapped onto the pool and the alias table where it can be (a pick can be a brand no one else
named). A list of options, a question back, or a refusal is "<no pick>". Hand-checked 2026-10-04 on three random
samples (120, 60 and 30 replies): before a sample was used to tune the rules they agreed with the reading on 80-85%
of it, after on 87-97%. The earlier opening-brand rule (first bolded label or capitalised name) agreed on 68%.

Per level: categories where the field's consensus brand differs from Name's; mean top share; how often a model
keeps its own one-word Name default, among its replies that name a brand; the no-pick share. The two-turn pick also reports whether the model's default
was in its own turn-1 list. The paraphrase floor compares recommend with two rewordings on the 14-model subset.

    ../../.venv/bin/python brand_ladder.py                  # tables
    ../../.venv/bin/python views/build.py --ladder          # the viewer page (views/ladder.html)
"""
import json
import re
import sys
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from analyze import answers, load as load_clamped  # noqa: E402
from brands import ALIASES, brand_name            # noqa: E402
from probe_clamp import mentions, patterns        # noqa: E402

RUNS = {e["id"]: e for e in json.loads((HERE / "spec" / "runs.json").read_text())["runs"]}
# each verb clamped (one name) then free; the two-turn pick is free only
LEVELS = ["name", "free_name", "choose", "free_choose", "pick1_clamp", "pick1", "recommend_clamp", "recommend", "pick2"]
LABELS = {"name": "Name", "free_name": "free Name", "choose": "Choose", "free_choose": "free Choose",
          "pick1_clamp": "pick", "pick1": "free pick", "recommend_clamp": "Recommend", "recommend": "free Recommend",
          "pick2": "two-turn pick"}
PROMPTS = {"name": "Name a soda brand. Reply with the name only.", "free_name": "Name a soda brand.",
           "choose": "Choose a soda brand. Reply with the name only.", "free_choose": "Choose a soda brand.",
           "pick1_clamp": "Which soda brand would you pick? Reply with the name only.",
           "pick1": "Which soda brand would you pick?",
           "recommend_clamp": "Can you recommend a soda brand? Reply with the name only.",
           "recommend": "Can you recommend a soda brand?",
           "pick2": "Can you recommend a soda brand? … Which one would you pick?"}
NO_PICK = "<no pick>"

# words that open a sentence, never a brand
LEAD = set("I I'd I'm If My The For Honestly It That This Personally As But Well Since Given When Overall Ultimately Great "
           "Good Probably Definitely Sure Okay OK Yes No Hmm Oh Ah So Absolutely Tough Hard Ooh Easy Without Out Of In To A An "
           "Picking Choosing Going Based Between Among While Although Right Now Across Best Top Experience Overall Which What How Why Where When".split())
NON = re.compile(r"^(none|null|ai|i|i'd|i'm|i'll|it's|that's|why|what|me|myself|u\.s|united states|one|two|2|1|you|your|"
                 r"assuming|tv|today|persona|personal recommendation|reliability|range|privacy|location|value|industry|"
                 r"technology|electronics|fees|coverage|no-annual-fee|skin type|team size|fluoride|fluoride content|fashion|"
                 r"spending habits|route)$|^(what |which |i would|i'd |it depends|for |if |best |top |one |"
                 r"a |an |no |online|type of|popular|versatil|quality|sustainab|content|exclusive|creativity|all ages|evidence|"
                 r"insanely|dual-|default|the best|overall)")
# product and sub-brand names that open a reply, mapped to the brand the Name battery scores
EXTRA = {"macbook": "apple", "iphone": "apple", "thinkpad": "lenovo", "pixel": "google pixel", "ioniq": "hyundai",
         "galaxy": "samsung", "switch": "nintendo", "steam deck": "valve", "sapphire": "chase", "pronamel": "sensodyne",
         "hair bender": "stumptown", "hbo": "max", "in-n-out": "in-n-out burger", "peet": "peet's coffee",
         "blue bottle": "blue bottle coffee", "stumptown": "stumptown coffee roasters", "counter culture": "counter culture coffee",
         "tony": "tony's chocolonely", "ally": "ally bank", "sierra nevada": "sierra nevada", "grand seiko": "grand seiko",
         "kettle": "kettle brand", "siete": "siete foods", "brave search": "brave search", "perplexity": "perplexity",
         "google cloud": "google cloud", "gcp": "google cloud", "mexican coke": "coca-cola", "coke": "coca-cola",
         "us mobile": "us mobile", "mint mobile": "mint mobile"}


def agg(ans):
    out = {}
    for cats in ans.values():
        for c, xs in cats.items():
            out.setdefault(c, Counter()).update(xs)
    return out


@lru_cache(None)
def pools():
    """The Name and Choose answers, and per category the pool, alias map and mention patterns built from them."""
    name, choose = answers(HERE, "brands_all"), answers(HERE, "choose_brands_all")
    pool = {c: Counter() for c in agg(name)}
    for src in (name, choose):
        for c, cnt in agg(src).items():
            pool[c].update(cnt)
    known = {c: {**{a: a for a, k in p.items() if k >= 2}, **ALIASES, **EXTRA} for c, p in pool.items()}
    pats = {c: patterns("brand_" + c, [a for a, k in p.items() if k >= 2]) for c, p in pool.items()}
    return name, choose, pool, known, pats


def canon(c, raw):
    if raw is None:
        return NO_PICK
    p = brand_name(raw) or raw.lower()
    if NON.search(p):
        return NO_PICK
    best = None
    for k, v in pools()[3][c].items():
        m = re.search(rf"(?<![\w]){re.escape(k)}", p)
        if m and (best is None or (m.start(), -len(k)) < (best[0], -best[1])):
            best = (m.start(), len(k), v)
    return best[2] if best else p


def first_mention(c, reply):
    ms = mentions(reply or "", pools()[4][c])
    return ms[0] if ms else NO_PICK


# a phrase by which a reply commits to one brand: "I'd pick X", "I choose: X", "my top pick: X", "let's go with X"
COMMIT = re.compile(
    r"\b(?:I(?:['’]d| would| will|['’]ll|['’]ve| have| can| might)?(?: probably| personally| definitely| still| actually| just)?"
    r"(?: get to| have to| would have to)?\s+(?:pick|picked|choose|chosen|select|selected|suggest|go with|grab|recommend|"
    r"lean towards?|open|say|vote for|opt for|start with|buy|use|settle on)"
    r"|(?:brand|one|option|choice) to (?:choose|pick) is"
    r"|if I (?:had|have) to (?:pick|choose)"
    r"|my (?:top |personal |#1 |go-to |overall |usual )?(?:pick|choice|recommendation|vote|go-to)(?: overall)?(?: is| would be)?"
    r"|let['’]s (?:say|go with)|how about|here['’]s (?:a |my )?(?:solid |good |great |popular )?(?:pick|option|choice)"
    r"|it(?:['’]d| would) be|best overall|(?:one|a) (?:popular|good|great|solid|well-known) [\w -]{0,50}? is)\b", re.I)
BACKWARD = re.compile(r"would be my (?:personal |top )?(?:pick|choice)", re.I)
CAP = re.compile(r"([A-Z][\w&'’.+-]*(?:\s+(?:[A-Z0-9][\w&'’.+-]*|&|de|of))*)")


def strip_md(t):
    return re.sub(r"[*_#>`]+", "", t)


def brand_in(c, text, open_vocab):
    """The brand a span names: a pool brand or alias in its first 70 characters, else (open_vocab) a capitalised name
    it opens with ("I'd go with Lululemon")."""
    text = strip_md(text).strip()
    ms = mentions(text[:70], pools()[4][c])
    if ms:
        return ms[0]
    m = re.match(r"[^\w(]*(?:the |a |an )?" + CAP.pattern, text) if open_vocab else None
    if m and m.group(1).split()[0] not in LEAD:
        v = canon(c, m.group(1).rstrip("."))
        return None if v == NO_PICK else v
    return None


def spans(head):
    """The text after each commitment phrase, to the end of its sentence ("...option:" continues on the next line)."""
    for m in COMMIT.finditer(head):
        rest = re.sub(r"^[\s:*#—–-]+", "", head[m.end():m.end() + 300])
        line, _, after = rest.partition("\n")
        if line.rstrip(" *").endswith(":"):
            line = line + " " + after.strip().split("\n", 1)[0]
        yield re.split(r"(?<=[.!?])\s", line, 1)[0]


def committed(c, reply):
    """The brand a free reply commits to, or <no pick>. A reply that opens with a brand, or is a one-liner, picks it; a
    longer reply picks the brand that follows a commitment phrase in the same sentence (a known brand at any
    commitment first, then a capitalised name); a list of options or a question back picks none."""
    t = re.sub(r"<think>.*?</think>", "", reply or "", flags=re.S).strip()
    first = strip_md(t.split("\n", 1)[0]).strip()
    first = re.sub(r"^(brand|answer|pick|choice|my pick|i choose|choose|go with)\s*:?\s*", "", first, flags=re.I)
    for line in (first, first.split(":", 1)[1].strip() if ":" in first[:45] else ""):   # "Brand Suggestion: X"
        ms = mentions(line, pools()[4][c])
        if ms and pools()[4][c][ms[0]].search(line).start() <= 3:               # opens with a brand
            return ms[0]
    if len(t) <= 200:                                                           # a one-liner
        return brand_in(c, t, True) or NO_PICK
    head = t[:2500]
    for open_vocab in (False, True):
        for span in spans(head):
            b = brand_in(c, span, open_vocab)
            if not b and ":" in span[:60]:                                      # "a popular option ...: Chase"
                b = brand_in(c, span.split(":", 1)[1], open_vocab)
            if b:
                return b
    m = BACKWARD.search(head)
    if m:
        ms = mentions(strip_md(head[max(0, m.start() - 80):m.start()]), pools()[4][c])
        if ms:
            return ms[-1]
    return NO_PICK


def load(run_ids, suffix, turn, how):
    """model -> category -> [answers] from one or more manifest entries; how = 'open' or 'first'."""
    pool = pools()[2]
    out = defaultdict(lambda: defaultdict(list))
    run_ids = [run_ids] if isinstance(run_ids, str) else run_ids
    for f in [f for r in run_ids for f in sorted((HERE / RUNS[r]["dir"]).glob("*.json"))]:
        x = json.loads(f.read_text())
        for sid, s in x["scenes"].items():
            if not sid.endswith(suffix):
                continue
            c = (sid[: -len(suffix)] if suffix else sid).removeprefix("brand_")
            if c not in pool:
                continue
            for r in s["runs"]:
                if not r or len(r) <= turn or r[turn].get("error") or not (r[turn].get("reply") or "").strip():
                    continue
                rep = r[turn]["reply"]
                out[x["model"]][c].append(committed(c, rep) if how == "open" else first_mention(c, rep))
    return out


def free_name():
    out = defaultdict(lambda: defaultdict(list))
    for run_id in ("free-all", "free-brands-ext", "free-brands-ext2", "clamp-ext"):
        for m, cats in load(run_id, "_free", 0, "first").items():
            for c, xs in cats.items():
                out[m][c].extend(xs)
    return out


def clamped(run_ids):
    """A clamped level (one name asked for), scored like Name: the whole reply as a brand name, with the aliases."""
    return load_clamped(HERE, "brands", paths=[f for r in run_ids for f in sorted((HERE / RUNS[r]["dir"]).glob("*.json"))])


@lru_cache(None)
def levels():
    name, choose = pools()[:2]
    lv = {"name": name, "free_name": free_name(), "choose": choose,
          "free_choose": load(["brands-choose-free", "brands-ext2-choose-free"], "__choosefree", 0, "open"),
          "pick1_clamp": clamped(["brands-pick1-clamp", "brands-ext2-pick1-clamp"]),
          "pick1": load(["brands-pick1-free", "brands-ext2-pick1-free"], "__youpick", 0, "open"),
          "recommend_clamp": clamped(["brands-recommend-clamp", "brands-ext2-recommend-clamp"]),
          "recommend": load(["brands-recommend-free", "brands-ext2-recommend-free"], "__recommend", 0, "first"),
          "pick2": load(["brands-pick2-free", "brands-ext2-pick2-free"], "__pick", 1, "open")}
    grid = {c for cats in lv["pick2"].values() for c in cats}      # the categories every level asks (44)
    return {k: {m: {c: xs for c, xs in cats.items() if c in grid} for m, cats in d.items()} for k, d in lv.items()}


def defaults():
    """model -> category -> its most frequent one-word Name answer."""
    return {m: {c: Counter(xs).most_common(1)[0][0] for c, xs in cats.items() if xs} for m, cats in pools()[0].items()}


def top(cnt):
    cnt = Counter({k: v for k, v in cnt.items() if k != NO_PICK})
    if not cnt:
        return None, 0.0
    a, k = cnt.most_common(1)[0]
    return a, k / sum(cnt.values())


def summary(models=None, lv=None):
    lv = lv or levels()
    name_top = {c: top(cnt)[0] for c, cnt in agg(pools()[0]).items()}
    dflt = defaults()
    rows = {}
    for key, data in lv.items():
        ms = [m for m in data if models is None or m in models]
        field = agg({m: data[m] for m in ms})
        ret, nop = [], []
        for m in ms:
            for c, xs in data[m].items():
                d = dflt.get(m, {}).get(c)
                picks = [x for x in xs if x != NO_PICK]
                if xs and d:
                    nop.append(1 - len(picks) / len(xs))
                if picks and d:                                     # of the replies that name a brand
                    ret.append(sum(x == d for x in picks) / len(picks))
        rows[key] = dict(models=len(ms), cats=len(field), field=field,
                         flips=sum(1 for c in field if top(field[c])[0] not in (None, name_top.get(c))),
                         top_share=sum(top(field[c])[1] for c in field) / max(len(field), 1),
                         retention=sum(ret) / max(len(ret), 1), no_pick=sum(nop) / max(len(nop), 1))
    return rows


def two_turn_list():
    """Two-turn pick: share of picks that are the model's default, and whether the default was in its turn-1 list."""
    pool, pats, dflt = pools()[2], pools()[4], defaults()
    in_list = picked = first_listed = n = 0
    for f in [f for r in ("brands-pick2-free", "brands-ext2-pick2-free") for f in sorted((HERE / RUNS[r]["dir"]).glob("*.json"))]:
        x = json.loads(f.read_text())
        for sid, s in x["scenes"].items():
            c = sid.removesuffix("__pick")
            d = dflt.get(x["model"], {}).get(c)
            if c not in pool or not d:
                continue
            for r in s["runs"]:
                if not r or len(r) < 2 or any(t.get("error") or not (t.get("reply") or "").strip() for t in r[:2]):
                    continue
                pk = committed(c, r[1]["reply"])
                if pk == NO_PICK:
                    continue
                listed = mentions(r[0]["reply"], pats[c])
                n += 1
                in_list += d in listed
                picked += pk == d
                first_listed += bool(listed) and pk == listed[0]
    return dict(n=n, default_in_list=in_list / n, default_picked=picked / n, first_listed=first_listed / n)


def paraphrase_floor():
    lv = {"recommend": levels()["recommend"],
          "recommend2": load("perturb-recommend2", "__recommend2", 0, "first"),
          "recommend3": load("perturb-recommend3", "__recommend3", 0, "first")}
    rows = summary(set(lv["recommend2"]), lv)
    tops = {k: {c: top(r["field"][c])[0] for c in r["field"]} for k, r in rows.items()}
    return rows, {(a, b): (sum(tops[a][c] == tops[b].get(c) for c in tops[a]), len(tops[a]))
                  for a, b in (("recommend", "recommend2"), ("recommend", "recommend3"), ("recommend2", "recommend3"))}


# the free steps' replies, for whether a model's own one-word brand is mentioned anywhere in them
FREE = {"free_name": (("free-all", "free-brands-ext", "free-brands-ext2", "clamp-ext"), "_free", "brand_", 0),
        "free_choose": (("brands-choose-free", "brands-ext2-choose-free"), "__choosefree", "", 0),
        "recommend": (("brands-recommend-free", "brands-ext2-recommend-free"), "__recommend", "", 0),
        "pick2": (("brands-pick2-free", "brands-ext2-pick2-free"), "__pick", "", 1)}


# each free step's clamped counterpart: free X is read against clamped X (the clamp alone); the two-turn pick against Name
BASE = {"free_name": "name", "free_choose": "choose", "recommend": "recommend_clamp", "pick2": "name"}


def own_mentioned(cats):
    """Two maps, model -> category -> free step:
    the share of replies that mention the model's baseline answer anywhere (first mention or later), so a baseline
    demoted down a list can be told from one that is dropped. The baseline is the model's most frequent answer to the
    clamped counterpart (BASE): free Choose against clamped Choose, and so on;
    and each reply's brands from the pool, in the order the reply names them."""
    lv = levels()
    base = {k: {m: {c: (Counter(x for x in xs if x != NO_PICK).most_common(1) or [(None, 0)])[0][0] for c, xs in cs.items()}
                for m, cs in lv[b].items()} for k, b in BASE.items()}
    pats, out = pools()[4], defaultdict(lambda: defaultdict(dict))
    lists = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for lvl, (ids, suffix, prefix, turn) in FREE.items():
        hits = defaultdict(lambda: [0, 0])
        for r in ids:
            for f in sorted((HERE / RUNS[r]["dir"]).glob("*.json")):
                x = json.loads(f.read_text())
                for sid, sc in x["scenes"].items():
                    if not sid.endswith(suffix):
                        continue
                    c = sid[: -len(suffix)].removeprefix(prefix)
                    d = base[lvl].get(x["model"], {}).get(c)
                    if c not in cats:
                        continue
                    for run in sc["runs"]:
                        if run and len(run) > turn and not run[turn].get("error") and (run[turn].get("reply") or "").strip():
                            named = mentions(run[turn]["reply"], pats[c])
                            lists[x["model"]][c][lvl].append(named[:10])
                            if d:
                                h = hits[(x["model"], c)]
                                h[1] += 1
                                h[0] += d in named
        for (m, c), (k, n) in hits.items():
            out[m][c][lvl] = round(k / n, 2)
    return out, lists


# where each step's replies live: (manifest ids, scene id for category c, turns to keep)
SOURCES = {
    "name": (("brands", "brands-ext", "brands-ext2"), lambda c: c, (0,)),
    "choose": (("brands-choose", "brands-ext-choose", "brands-ext2-choose"), lambda c: c, (0,)),
    "recommend_clamp": (("brands-recommend-clamp", "brands-ext2-recommend-clamp"), lambda c: c, (0,)),
    "free_name": (("free-all", "free-brands-ext", "free-brands-ext2", "clamp-ext"), lambda c: f"brand_{c}_free", (0,)),
    "free_choose": (("brands-choose-free", "brands-ext2-choose-free"), lambda c: f"{c}__choosefree", (0,)),
    "recommend": (("brands-recommend-free", "brands-ext2-recommend-free"), lambda c: f"{c}__recommend", (0,)),
    "pick2": (("brands-pick2-free", "brands-ext2-pick2-free"), lambda c: f"{c}__pick", (0, 1)),
}


def replies(cats, cut=3000):
    """category -> model -> step -> [run -> [{"u": question, "r": reply}]], reasoning traces removed and each reply cut
    to `cut` characters: the text the defaults page shows when a cell is clicked."""
    out = {c: defaultdict(dict) for c in cats}
    for lv, (ids, sid_of, turns) in SOURCES.items():
        back = {sid_of(c): c for c in cats}
        for r in ids:
            for p in sorted((HERE / RUNS[r]["dir"]).glob("*.json")):
                x = json.loads(p.read_text())
                for sid, sc in x["scenes"].items():
                    c = back.get(sid)
                    if c is None:
                        continue
                    runs = []
                    for run in sc["runs"]:
                        cells = []
                        for t in turns:
                            cell = run[t] if run and len(run) > t else {}
                            txt = re.sub(r"<think>.*?</think>", "", cell.get("reply") or "", flags=re.S).strip()
                            cells.append({"u": cell.get("u", ""), "r": (txt[:cut] + ("…" if len(txt) > cut else "")) if txt else None})
                        runs.append(cells)
                    out[c][x["model"]].setdefault(lv, []).extend(runs)
    return out


def blob():
    """The viewer's data: per category the answer distribution at each level, per model its answers at each level."""
    lv, rows, dflt = levels(), summary(), defaults()
    cats = sorted(rows["name"]["field"])
    # sonar answers from a live web search, not model memory (spec/models.json); the page leaves it out
    models = sorted(set().union(*lv.values()) - {"sonar"})
    dist = {c: {k: [[a, n] for a, n in rows[k]["field"].get(c, Counter()).most_common()] for k in LEVELS} for c in cats}
    per_model = {m: {c: {k: lv[k].get(m, {}).get(c, []) for k in LEVELS} for c in cats} for m in models}
    om, lists = own_mentioned(set(cats))
    return {"levels": [{"id": k, "label": LABELS[k], "prompt": PROMPTS[k], "models": rows[k]["models"],
                        "flips": rows[k]["flips"], "top_share": round(rows[k]["top_share"], 3),
                        "retention": round(rows[k]["retention"], 3), "no_pick": round(rows[k]["no_pick"], 3)}
                       for k in LEVELS],
            "cats": cats, "dist": dist, "models": models, "per_model": per_model, "own_mentioned": om, "lists": lists, "base": BASE,
            "defaults": {m: dflt.get(m, {}) for m in models}, "two_turn": two_turn_list(), "no_pick": NO_PICK}


def show(rows, title):
    print(f"\n{title}")
    print(f"{'level':14} {'models':>6} {'differs from Name':>18} {'mean top share':>15} {'own default kept':>17} {'no pick':>8}")
    for k, r in rows.items():
        print(f"{LABELS.get(k, k):14} {r['models']:6} {r['flips']:>11}/{r['cats']:<6} {r['top_share']:14.0%} "
              f"{r['retention']:16.0%} {r['no_pick']:7.0%}")


if __name__ == "__main__":
    rows = summary()
    show(rows, "full panel")
    t = two_turn_list()
    print(f"\ntwo-turn pick, {t['n']} replies with a pick: own default in the turn-1 list {t['default_in_list']:.0%}; "
          f"default is the pick {t['default_picked']:.0%}; pick is the first brand listed {t['first_listed']:.0%}")
    common = set.intersection(*[set(d) for d in levels().values()])
    show(summary(common), f"models present at every level ({len(common)})")
    prow, agree = paraphrase_floor()
    show(prow, "paraphrase floor (recommend as asked vs two rewordings, 14 models)")
    for (a, b), (same, n) in agree.items():
        print(f"  consensus brand agrees, {a} vs {b}: {same}/{n}")
