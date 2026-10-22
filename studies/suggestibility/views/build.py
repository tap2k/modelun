"""Build the suggestibility study's review site: views/data.js.

Bakes the "right?" reflex — per-model TAGeff (P(affirm | "…right?") − P(affirm | neutral ask),
counterbalanced, bootstrap CI), the per-family generational walks, and per-model per-item drill-downs
(the actual ask-vs-right? replies) into one blob the self-contained page draws. Same pattern as the
consensus / structured explorers.

    python studies/suggestibility/views/build.py
    open studies/suggestibility/views/index.html
"""
import csv
import json
import shutil
import sys
from pathlib import Path

import numpy as np

VIEWS = Path(__file__).resolve().parent
STUDY = VIEWS.parent
sys.path.insert(0, str(STUDY))
from analyze import classify            # noqa: E402  yes/no/hedge classifier (judge-free)
from probe_righteffect import ITEMS     # noqa: E402  the 20 frozen decisions
from lineage import FAM                 # noqa: E402  model -> (family, generation index)

# generation label + color per family (explorer style — readable labels, dark-theme hues)
GENLABEL = {
    "gpt-3.5-turbo": "3.5", "gpt-4-turbo": "4-turbo", "gpt-4o": "4o", "gpt-4o-mini-2024-07-18": "4o-mini",
    "gpt-4.1": "4.1", "gpt-5": "5", "gpt-5.4": "5.4", "gpt-5.5": "5.5",
    "gpt-5.6-luna": "5.6 luna", "gpt-5.6-sol": "5.6 sol", "gpt-5.6-terra": "5.6 terra", "gpt-6-astra": "6 astra",
    "claude-3-haiku": "3 haiku", "claude-haiku-4.5": "haiku 4.5", "claude-sonnet-4.6": "sonnet 4.6",
    "claude-opus-4.8": "opus 4.8", "claude-sonnet-5": "sonnet 5", "claude-fable-5": "fable 5",
    "claude-opus-5": "opus 5", "claude-fable-5.1": "fable 5.1",
    "gemini-2.5-flash": "2.5 flash", "gemini-3.1-pro-preview": "3.1 pro", "gemini-3.5-flash": "3.5 flash",
    "gemini-3.6-flash": "3.6 flash", "gemini-3.1-flash-lite": "3.1 flash lite", "gemini-3.8-flash": "3.8 flash",
    "grok-4.20": "4.20", "grok-4.3": "4.3", "grok-4.5": "4.5", "grok-4.6": "4.6",
    "qwen-2.5-72b-instruct": "2.5 72b", "qwen3-235b-a22b-2507": "qwen3",
    "qwen3.5-9b": "3.5 9b", "qwen3.5-27b": "3.5 27b", "qwen3.5-122b-a10b": "3.5 122b", "qwen3.6-35b-a3b": "3.6 35b", "qwen3.8-2.4t-a95b": "3.8 2.4t", "qwen3.8-27b": "3.8 27b",
    "deepseek-chat-v3-0324": "v3-0324", "deepseek-r1": "r1", "deepseek-v3.2": "v3.2", "deepseek-v4-flash": "v4-flash", "deepseek-v4-pro": "v4-pro",
    "glm-4.7": "4.7", "glm-5.2": "5.2",
    "claude-opus-4.1": "opus 4.1", "claude-sonnet-4.5": "sonnet 4.5", "claude-opus-4.5": "opus 4.5",
    "claude-opus-4.6": "opus 4.6", "claude-opus-4.7": "opus 4.7", "claude-opus-5.5": "opus 5.5", "claude-sonnet-5.5": "sonnet 5.5", "claude-haiku-5.5": "haiku 5.5",
    "gpt-5.4-mini": "5.4 mini", "gpt-6-luna": "6 luna", "gpt-6-sol": "6 sol", "gpt-6.1-sol": "6.1 sol",
    "gemini-2.5-pro": "2.5 pro", "gemini-3-flash-preview": "3 flash", "grok-4.7": "4.7", "qwen3.7-plus": "3.7 plus",
}
FAMCOLOR = {"GPT": "#6ea8fe", "Claude": "#e0a33e", "Gemini": "#4fd1a5", "Grok": "#b39ddb",
            "DeepSeek": "#e0b84f", "Qwen": "#f19bbf"}


def arate(reps):
    labs = [classify(r) for r in reps if r is not None]
    return (sum(l == "affirm" for l in labs) / len(labs)) if labs else None


def trim(r):
    return (r or "").strip().replace("\n", " ")[:70]


def cell(reps):
    return [{"c": classify(r) or "fail", "r": trim(r)} for r in reps]


import grid_stats as GS   # noqa: E402  the 3 wordings x 3 cues grid and its statistics

WORDINGS = list(GS.WORDINGS)
CUES = ("neutral", "right", "maybe")


def code(r):
    """One reply as a letter (a affirm, r reject, h hedge, f failed) plus its text when it is not a bare yes/no."""
    if not r:
        return "f"
    c = {"affirm": "a", "reject": "r", "hedge": "h"}.get(classify(r), "f")
    t = r.strip().replace("\n", " ")
    return c if t.rstrip(".!").lower() in ("yes", "no") else c + t[:80]


g = json.loads((STUDY / "probes" / "grid_stats.json").read_text())
gsum, gres = g["summary"], g["per_model"]
replies = GS.load()     # wording -> model -> cue -> item -> side -> replies
rd = lambda x: round(x, 3) if isinstance(x, float) else x
models = {}
for m in gres["original"]:
    fam, gen = FAM.get(m, (None, None))
    v = {"family": fam, "gen": gen, "genlabel": GENLABEL.get(m, m), "w": {}}
    for w in WORDINGS:
        r = gres[w].get(m)
        if r is None:
            continue
        v["w"][w] = {"neutral": rd(r["affirm_neutral"]), "right": rd(r["affirm_right"]), "maybe": rd(r["affirm_maybe"]),
                     **{k: {"e": rd(r[k]["tageff"]), "lo": rd(r[k]["ci95"][0]), "hi": rd(r[k]["ci95"][1]), "sig": r[k]["sig"]}
                        for k in ("tag", "gap")}}
    v["items"] = {w: {sid: [[code(x) for s in "xy" for x in replies[w][m][c].get(sid, {}).get(s, [])] for c in CUES]
                      for sid, *_ in ITEMS}
                  for w in WORDINGS if m in replies[w]}
    models[m] = v

data = {
    "meta": {"panel": len(models), "famcolor": FAMCOLOR, "wordings": WORDINGS,
             "fam_order": ["GPT", "Claude", "Gemini", "Grok", "Qwen", "DeepSeek"],
             "summary": {w: {k: rd(x) if not isinstance(x, dict) else {kk: rd(vv) for kk, vv in x.items()}
                             for k, x in gsum[w].items()} for w in WORDINGS},
             "corr": {k: rd(x["pearson"]) for k, x in gsum["correlations"].items()}},
    "items": [{"id": sid, "decision": d, "x": x, "y": y} for sid, d, x, y in ITEMS],
    "models": models,
}
blob = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
(VIEWS / "data.js").write_text(f"const D = {blob};\n")
print(f"wrote {VIEWS/'data.js'}  ({len(models)} models, {len(blob)//1024}KB)")

# shared styling for the study sites (copied, like core.js; the copy is gitignored)
shutil.copy(STUDY.parent.parent / "harness" / "viewer" / "base.css", VIEWS / "base.css")

# --- contested probe (probe_contested.py): its own blob, data_contested.js, drawn by contested.html ---
import probe_contested as PC   # noqa: E402

VENDOR = {"anthropic": "Anthropic", "openai": "OpenAI", "google": "Google", "x-ai": "xAI", "meta": "Meta",
          "meta-llama": "Meta", "deepseek": "DeepSeek", "moonshotai": "Moonshot", "qwen": "Qwen", "z-ai": "Z.ai",
          "mistralai": "Mistral", "minimax": "MiniMax", "cohere": "Cohere", "baidu": "Baidu", "tencent": "Tencent",
          "stepfun": "StepFun", "nvidia": "NVIDIA", "ibm-granite": "IBM", "microsoft": "Microsoft", "writer": "Writer",
          "perplexity": "Perplexity", "nousresearch": "Nous", "gryphe": "Gryphe"}


def release_dates():
    """label -> release date, read the way the consensus view does: the ECI file in cross-instrument,
    else the conduct study's looked-up dates."""
    xi = STUDY.parent / "cross-instrument"
    eci = {r["Model"]: r["date"] for r in csv.DictReader((xi / "eci_scores_2026-09-13.csv").open())}
    out = {}
    for ln in (xi / "eci_map_2026-09-13.tsv").read_text().splitlines():
        if not ln.startswith("#") and "\t" in ln:
            ours, theirs = ln.split("\t")[:2]
            if eci.get(theirs):
                out[ours] = eci[theirs]
    for ln in (STUDY.parent / "conduct" / "spec" / "release-dates.tsv").read_text().splitlines():
        f = ln.split("\t")
        if not ln.startswith("#") and len(f) >= 2:
            out.setdefault(f[0], f[1][:10])
    return out


released = release_dates()

ca = json.loads((STUDY / "probes" / "contested_analysis.json").read_text())["per_model"]
vendor = {s.split("/")[-1]: s.split("/")[0] for s in
          (l.strip() for l in (STUDY / "spec" / "models.txt").read_text().splitlines()) if s and not s.startswith("#")}
KEEP = ["tageff", "tageff_ci90", "tageff_answered", "bareeff", "beliefeff", "beliefeff_answered", "belief_q_eff",
        "hedge_ask", "hedge_tag", "d_affirm_tag", "d_reject_tag", "d_hedge_tag",
        "d_affirm_belief", "d_reject_belief", "d_hedge_belief", "both_no_ask", "tageff_left", "tageff_right"]
KEEP += [f"{k}_{st}" for st in PC.STRATA for k in ("tageff", "bareeff", "beliefeff", "hedge_ask")]
cmodels, full = {}, {}     # full: each model's replies, for contested_replies/ below
for p in sorted(PC.OUT.glob("*.json")):
    d = json.loads(p.read_text()); m = d["model"]
    if m not in ca:
        continue
    r = ca[m]
    v = {k: (round(r[k], 3) if isinstance(r.get(k), float) else r.get(k)) for k in KEEP if k in r}
    if r.get("tageff_ci90"):
        v["tageff_ci90"] = [round(x, 3) for x in r["tageff_ci90"]]
    v["via"] = ("-" if r["d_affirm_tag"] > -0.05 else "No" if r["d_reject_tag"] >= r["d_hedge_tag"] else "declining")
    v["vendor"] = VENDOR.get(vendor.get(m, ""), vendor.get(m, "?"))
    v["released"] = released.get(m)
    v["items"] = {item: {key: cell(reps) for key, reps in c.items()} for item, c in d["cells"].items()}
    cmodels[m] = v
    full[m] = {item: {key: [(r or "").strip() for r in reps] for key, reps in c.items()} for item, c in d["cells"].items()}
citems = [{"id": i, "stratum": st, "x": cx, "y": cy,
           "prompts": {f"{a}_{s}": PC.prompt(a, q, cl).replace(" " + PC.CLAMP, "")
                       for a in PC.ARMS + PC.EXTRA_ARMS for s, (q, cl) in (("x", (qx, cx)), ("y", (qy, cy)))}}
          for i, st, (qx, cx), (qy, cy) in PC.ITEMS]
cdata = {"meta": {"n": len(cmodels), "strata": list(PC.STRATA),
                  "vendors": sorted({v["vendor"] for v in cmodels.values()})},
         "models": cmodels, "order": sorted(cmodels, key=lambda m: cmodels[m]["tageff"]), "items": citems}
cblob = json.dumps(cdata, ensure_ascii=False, separators=(",", ":"))
(VIEWS / "data_contested.js").write_text(f"const C = {cblob};\n")
print(f"wrote {VIEWS/'data_contested.js'}  ({len(cmodels)} models, {len(citems)} items, {len(cblob)//1024}KB)")
# the full replies, one file per model, loaded when a reply is clicked (local only, like consensus ladder_replies/)
rd = VIEWS / "contested_replies"
rd.mkdir(exist_ok=True)
for m, f in full.items():
    (rd / f"{m}.js").write_text("(window.CR = window.CR || {})[" + json.dumps(m) + "] = "
                                + json.dumps(f, ensure_ascii=False, separators=(",", ":")) + ";\n")
print(f"wrote {rd}/  ({sum(f.stat().st_size for f in rd.glob('*.js')) // 1024}KB in {len(cmodels)} files)")

# --- positions (probe_contested_assert.py): data_positions.js, drawn by positions.html. Run its analyze first. ---
import probe_contested_assert as PA   # noqa: E402
from lineage import FAM, EXTRA   # noqa: E402
from probe_contested_unclamped import POLES   # noqa: E402

pa = json.loads((STUDY / "probes" / "contested_assert_analysis.json").read_text())
fam = {**FAM, **EXTRA}
roster = [l.strip() for l in (STUDY / "spec" / "models.txt").read_text().splitlines() if l.strip() and not l.startswith("#")]
# both instruments, toggled in the view: told to take a side (assert_clamp) and no instruction (the contested probe's ask arm)
def declined(cells):
    s = "".join(c["x"] + c["y"] for c in cells).replace("-", "")
    return round(s.count("h") / len(s), 3) if s else None
pdecl = {m: {inst: declined([c[inst] for c in its.values() if inst in c]) for inst in ("clamp", "assert_clamp")}
         for m, its in pa["per_model"].items()}
pmodels = [{"label": s.split("/")[-1], "slug": s, "family": fam.get(s.split("/")[-1], (None,))[0],
            "generation": fam.get(s.split("/")[-1], (None, None))[1], "released": released.get(s.split("/")[-1])} for s in roster if s.split("/")[-1] in pa["per_model"]]
preplies = {"assert_clamp": {}, "clamp": {}}
for inst, m, i, x, y in PA.records():      # cut at 600 characters; a one-word answer is the usual case
    preplies[inst].setdefault(m, {})[i] = {"x": [(r or "")[:600] for r in x], "y": [(r or "")[:600] for r in y]}
pdata = {"items": [{"id": i, "stratum": st, "poles": list(POLES[i]), "qx": qx, "qy": qy} for i, st, (qx, _), (qy, _) in PC.ITEMS],
         "assert": PA.ASSERT, "models": pmodels, "summary": pa["summary"], "cells": pa["per_model"], "replies": preplies, "declines": pdecl}
pblob = json.dumps(pdata, ensure_ascii=False, separators=(",", ":"))
(VIEWS / "data_positions.js").write_text(f"const P = {pblob};\n")
print(f"wrote {VIEWS/'data_positions.js'}  ({len(pmodels)} models, {len(pblob)//1024}KB)")

# --- ballot (probe_contested_ballot.py): data_ballot.js, drawn by ballot.html, and ballot_replies/<state>.js with every
# answer, its search queries and cited links, loaded when a race is opened. Run its analyze first.
import probe_contested_ballot as PB   # noqa: E402

bov = json.loads(PB.OVERRIDES.read_text())
brecs = {p.stem: json.loads(p.read_text()) for p in sorted(PB.OUT.glob("*.json"))}
bmodels = sorted(brecs, key=lambda m: -len(brecs[m]["cells"]))
bverdict, bfull = {}, {}
for m in bmodels:
    for rid, c in brecs[m]["cells"].items():
        cs = PB.codes(m, rid, c["draws"], bov)
        bverdict.setdefault(m, {})[rid] = PB.verdict(cs, m)
        st = PB.RACE[rid]["state"]
        bfull.setdefault(st, {}).setdefault(rid, {})[m] = [
            {"code": k, "reply": d["reply"], "searches": d["searches"], "queries": d["queries"], "cited": d["cited"]}
            for k, d in zip(cs, c["draws"]) if d]

# sources: per model, how many answers' searches returned each domain, over the races with one D and one R, split by how
# the answer was coded. "retrieved" is the common measure: both hosts list the pages a search returned, while GPT's
# "cited" (links in its reply) has no Grok counterpart. A domain's type is a rough, rule-based label for the view.
import re   # noqa: E402
from urllib.parse import urlparse   # noqa: E402
BSOCIAL = {"x.com", "twitter.com", "reddit.com", "youtube.com", "facebook.com", "instagram.com", "tiktok.com", "threads.net",
           "linkedin.com", "substack.com", "medium.com"}
BSCORECARD = {"tpaction.com", "analysis.limitedgov.org"}   # advocacy groups' legislator scorecards, not news


def btype(d):
    if re.search(r"\.(gov|mil)$|\.gov\.|\.[a-z]{2}\.us$", d):
        return "government"
    if "wikipedia.org" in d or d in ("britannica.com", "wikiwand.com"):
        return "reference"
    if d in BSOCIAL:
        return "social"
    if d in BSCORECARD:
        return "voter guide / election data"
    if re.search(r"ballot|vote|elect|candidate|civic|reps|govtrack|voteview|opensecrets|politicalgroup|chamberlight|greenpapers"
                 r"|270towin|cookpolitical|fec|campaign|reprecord|powervoter", d):
        return "voter guide / election data"
    return "news and other"


bmain = [m for m in bmodels if len(brecs[m]["cells"]) > 100]
bsrc_n, bsrc, blinks = {}, {}, {}   # blinks: per model and bucket, retrieved links by domain type
for m in bmain:
    n = bsrc_n.setdefault(m, {"all": 0, "D": 0, "R": 0, "decline": 0, "searches": 0})
    lk = blinks.setdefault(m, {b: {} for b in ("all", "D", "R", "decline")})
    for rid, c in brecs[m]["cells"].items():
        if PB.RACE[rid].get("other"):
            continue
        for k, d in zip(PB.codes(m, rid, c["draws"], bov), c["draws"]):
            n["searches"] += d.get("searches") or 0
            buckets = ["all"] + ([k] if k in ("D", "R", "decline") else [])
            for b in buckets:
                n[b] += 1
                for u in d.get("retrieved") or []:
                    t = btype(urlparse(u).netloc.lower().removeprefix("www."))
                    lk[b][t] = lk[b].get(t, 0) + 1
            for dom in {urlparse(u).netloc.lower().removeprefix("www.") for u in d.get("retrieved") or []}:
                cnt = bsrc.setdefault(dom, {}).setdefault(m, {"all": 0, "D": 0, "R": 0, "decline": 0})
                for b in buckets:
                    cnt[b] += 1
share = lambda dom, m: bsrc[dom].get(m, {}).get("all", 0) / bsrc_n[m]["all"]
btop = sorted(bsrc, key=lambda dom: -max(share(dom, m) for m in bmain))[:40]
bsources = {"n": bsrc_n, "links": blinks, "domains": [{"d": dom, "t": btype(dom), "c": bsrc[dom]} for dom in btop]}

bpage = PB.page_data()       # the same data convovo.ai/ballot gets, for the third candidates' names
bdata = {"prompt": PB.USER_TURN, "models": [{"id": m, "name": PB.NAMES.get(m, m), "date": brecs[m]["date"]} for m in bmodels],
         "races": [{k: r[k] for k in ("office", "state", "district", "D", "R", "I", "incumbent", "pvi", "other", "candidates", "others", "note") if r.get(k)}
                   | {"id": PB.race_id(r), "n": r["n"]} for r in PB.RACES], "verdicts": bverdict,
         "picks": {m["id"]: {rid: c["pick"] for rid, c in m["cells"].items() if c.get("pick")} for m in bpage["models"]},
         "sources": bsources}
bblob = json.dumps(bdata, ensure_ascii=False, separators=(",", ":"))
(VIEWS / "data_ballot.js").write_text(f"const B = {bblob};\n")
brd = VIEWS / "ballot_replies"
brd.mkdir(exist_ok=True)
for st, f in bfull.items():
    (brd / f"{st}.js").write_text("(window.BR = window.BR || {})[" + json.dumps(st) + "] = "
                                  + json.dumps(f, ensure_ascii=False, separators=(",", ":")) + ";\n")
print(f"wrote {VIEWS/'data_ballot.js'} ({len(bblob)//1024}KB) and {brd}/ ({sum(f.stat().st_size for f in brd.glob('*.js')) // 1024}KB in {len(bfull)} files)")
