"""Build the suggestibility study's review site: views/data.js.

Bakes the "right?" reflex — per-model TAGeff (P(affirm | "…right?") − P(affirm | neutral ask),
counterbalanced, bootstrap CI), the per-family generational walks, and per-model per-item drill-downs
(the actual ask-vs-right? replies) into one blob the self-contained page draws. Same pattern as the
consensus / structured explorers.

    python studies/suggestibility/views/build.py
    open studies/suggestibility/views/index.html
"""
import json
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
    "gpt-5.6-luna": "5.6 luna", "gpt-5.6-sol": "5.6 sol", "gpt-5.6-terra": "5.6 terra",
    "claude-3-haiku": "3 haiku", "claude-haiku-4.5": "haiku 4.5", "claude-sonnet-4.6": "sonnet 4.6",
    "claude-opus-4.8": "opus 4.8", "claude-sonnet-5": "sonnet 5", "claude-fable-5": "fable 5",
    "gemini-2.5-flash": "2.5 flash", "gemini-3.1-pro-preview": "3.1 pro", "gemini-3.5-flash": "3.5 flash",
    "grok-4.20": "4.20", "grok-4.3": "4.3", "grok-4.5": "4.5",
    "qwen-2.5-72b-instruct": "2.5 72b", "qwen3-235b-a22b-2507": "qwen3",
    "deepseek-chat-v3-0324": "v3-0324", "deepseek-r1": "r1", "deepseek-v3.2": "v3.2", "deepseek-v4-flash": "v4-flash",
    "glm-4.7": "4.7", "glm-5.2": "5.2",
}
FAMCOLOR = {"GPT": "#6ea8fe", "Claude": "#e0a33e", "Gemini": "#4fd1a5", "Grok": "#b39ddb",
            "DeepSeek": "#e0b84f", "Qwen": "#f19bbf", "GLM": "#7bd88f"}


def arate(reps):
    labs = [classify(r) for r in reps if r is not None]
    return (sum(l == "affirm" for l in labs) / len(labs)) if labs else None


def trim(r):
    return (r or "").strip().replace("\n", " ")[:70]


def cell(reps):
    return [{"c": classify(r) or "fail", "r": trim(r)} for r in reps]


rng = np.random.default_rng(7)
tx = {json.loads(p.read_text())["model"]: json.loads(p.read_text())["scenes"]
      for p in (STUDY / "transcripts").glob("*.json")}

models = {}
# OpenRouter panel: tag arm from probes/righteffect, ask baseline from main transcripts
for p in sorted((STUDY / "probes" / "righteffect").glob("*.json")):
    d = json.loads(p.read_text())
    m = d["model"]
    if m == "run" or m not in tx:
        continue
    items, effs = [], []
    for sid, decision, x, y in ITEMS:
        ask = [r[0].get("reply") for r in tx[m].get(sid + "__askx", {}).get("runs", []) +
               tx[m].get(sid + "__asky", {}).get("runs", []) if r]
        tag = d["tag"].get(sid, {}).get("x", []) + d["tag"].get(sid, {}).get("y", [])
        a, t = arate(ask), arate(tag)
        if a is None or t is None:
            continue
        effs.append(t - a)
        items.append({"id": sid, "decision": decision, "x": x, "y": y,
                      "ask_rate": round(a, 3), "tag_rate": round(t, 3),
                      "ask": cell(ask), "tag": cell(tag)})
    if not effs:
        continue
    boots = [float(np.mean(rng.choice(effs, len(effs)))) for _ in range(2000)]
    fam, gen = FAM.get(m, (None, None))
    asks = [it["ask_rate"] for it in items]
    tags = [it["tag_rate"] for it in items]
    models[m] = {
        "tageff": round(float(np.mean(effs)), 3),
        "lo": round(float(np.percentile(boots, 5)), 3),
        "hi": round(float(np.percentile(boots, 95)), 3),
        "ask": round(float(np.mean(asks)), 3), "tag": round(float(np.mean(tags)), 3),
        "floor": float(np.mean(asks)) < 0.10, "family": fam, "gen": gen,
        "genlabel": GENLABEL.get(m, m), "channel": "openrouter", "items": items,
    }

# GLM lineage (DeepInfra, thinking-off) — summary only, no per-item drill
for p in sorted((STUDY / "probes" / "righteffect_glm").glob("*.json")):
    d = json.loads(p.read_text())
    m = d["model"]
    fam, gen = FAM.get(m, ("GLM", 0))
    models[m] = {"tageff": round(d["tageff"], 3), "lo": round(d["ci"][0], 3), "hi": round(d["ci"][1], 3),
                 "ask": None, "tag": None, "floor": False, "family": fam, "gen": gen,
                 "genlabel": GENLABEL.get(m, m), "channel": "deepinfra", "items": None}

# confidence axis (probe_maybe: neutral ask / confident "right?" / tentative "maybe?")
conf = {}
for p in sorted((STUDY / "probes" / "maybe").glob("*.json")):
    d = json.loads(p.read_text())
    m = d["model"]
    if m == "run":
        continue
    rates = {f: arate(d["cells"].get(f, [])) for f in ("ask", "confident", "tentative")}
    if any(v is None for v in rates.values()):
        continue
    conf[m] = {"ask": round(rates["ask"], 3), "confident": round(rates["confident"], 3),
               "tentative": round(rates["tentative"], 3),
               "mirror": round(rates["tentative"] - rates["confident"], 3),
               "family": FAM.get(m, (None,))[0]}
conf_order = sorted(conf, key=lambda m: -conf[m]["mirror"])

# per-family walks (families with >= 2 generations)
walks = {}
for m, v in models.items():
    if v["family"]:
        walks.setdefault(v["family"], []).append(
            {"model": m, "gen": v["gen"], "genlabel": v["genlabel"], "tageff": v["tageff"]})
walks = {f: sorted(pts, key=lambda p: p["gen"]) for f, pts in walks.items() if len(pts) >= 2}

order = sorted(models, key=lambda m: models[m]["tageff"])   # most resistant (−) first

data = {
    "meta": {"panel": len(models), "run_date": "2026-07-16", "famcolor": FAMCOLOR,
             "fam_order": ["GPT", "Claude", "Gemini", "Grok", "Qwen", "DeepSeek", "GLM"]},
    "models": models, "order": order, "walks": walks,
    "confidence": conf, "confidence_order": conf_order,
}
blob = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
(VIEWS / "data.js").write_text(f"const D = {blob};\n")
print(f"wrote {VIEWS/'data.js'}  ({len(models)} models, {len(walks)} lineages, {len(blob)//1024}KB)")
