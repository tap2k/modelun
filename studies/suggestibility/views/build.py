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
cmodels = {}
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
citems = [{"id": i, "stratum": st, "x": cx, "y": cy,
           "prompts": {f"{a}_{s}": PC.prompt(a, q, cl).replace(" " + PC.CLAMP, "")
                       for a in PC.ARMS + PC.EXTRA_ARMS for s, (q, cl) in (("x", (qx, cx)), ("y", (qy, cy)))}}
          for i, st, (qx, cx), (qy, cy) in PC.ITEMS]
cdata = {"meta": {"n": len(cmodels), "strata": list(PC.STRATA), "arms": list(PC.ARMS), "extra": list(PC.EXTRA_ARMS),
                  "vendors": sorted({v["vendor"] for v in cmodels.values()})},
         "models": cmodels, "order": sorted(cmodels, key=lambda m: cmodels[m]["tageff"]), "items": citems}
cblob = json.dumps(cdata, ensure_ascii=False, separators=(",", ":"))
(VIEWS / "data_contested.js").write_text(f"const C = {cblob};\n")
print(f"wrote {VIEWS/'data_contested.js'}  ({len(cmodels)} models, {len(citems)} items, {len(cblob)//1024}KB)")
