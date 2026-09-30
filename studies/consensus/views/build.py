"""
Build the consensus study's review site: views/data.js.

Bakes the scorecard, the models x answers grid, per-category field distributions (with
which models gave each answer), per-model-per-category surprisal (for the model drill-down),
and the metadata-axis cuts into one blob the page draws. Self-contained: this study's
transcripts are single-turn one-word answers, so the generic arc renderer (core.js) adds
nothing and is not copied — the view is one hash-routed index.html with no deps.

    python studies/consensus/views/build.py
    open studies/consensus/views/index.html
"""

import json
import csv
import math
import sys
from pathlib import Path
from collections import Counter

import numpy as np

VIEWS = Path(__file__).resolve().parent
STUDY = VIEWS.parent
sys.path.insert(0, str(STUDY))
from analyze import load, analyze  # noqa: E402

# chronological order within lineages, for the generation-walk view (release order,
# maintained by hand — models.json carries no generation field)
WALKS = {
    "claude": ["claude-3-haiku", "claude-opus-4.1", "claude-sonnet-4.5", "claude-haiku-4.5", "claude-opus-4.5", "claude-opus-4.6", "claude-sonnet-4.6", "claude-opus-4.7", "claude-opus-4.8", "claude-fable-5", "claude-sonnet-5", "claude-opus-5", "claude-fable-5.1", "claude-opus-5.5", "claude-sonnet-5.5"],
    "gpt": ["gpt-3.5-turbo", "gpt-4-turbo", "gpt-4o", "gpt-4o-mini-2024-07-18", "gpt-4.1", "gpt-5", "gpt-5.4", "gpt-5.4-mini", "gpt-5.5", "gpt-5.6-luna", "gpt-5.6-terra", "gpt-5.6-sol", "gpt-6-astra", "gpt-6-luna", "gpt-6-sol", "gpt-6.1-sol"],
    "gemini": ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-3-flash-preview", "gemini-3.1-pro-preview", "gemini-3.1-flash-lite", "gemini-3.5-flash", "gemini-3.6-flash", "gemini-3.8-flash"],
    "deepseek": ["deepseek-chat-v3-0324", "deepseek-v3.2", "deepseek-v4-flash", "deepseek-v4-pro", "deepseek-r1"],
    "llama": ["llama-3.3-70b-instruct", "llama-4-scout", "llama-4-maverick"],
    "grok": ["grok-4.20", "grok-4.3", "grok-4.5", "grok-4.6", "grok-4.7"],
    "qwen": ["qwen-2.5-72b-instruct", "qwen3-235b-a22b-2507", "qwen3.5-9b", "qwen3.5-27b", "qwen3.5-122b-a10b", "qwen3.6-35b-a3b", "qwen3.7-plus", "qwen3.8-2.4t-a95b"],
    "glm": ["glm-4.7", "glm-5.3-flash", "glm-5.3"],
    "kimi": ["kimi-k2", "kimi-k2.5", "kimi-k3"],
}


VENDOR = {"anthropic": "Anthropic", "openai": "OpenAI", "google": "Google", "x-ai": "xAI",
          "meta": "Meta", "meta-llama": "Meta", "deepseek": "DeepSeek", "moonshotai": "Moonshot",
          "qwen": "Qwen", "z-ai": "Z.ai", "mistralai": "Mistral", "minimax": "MiniMax",
          "cohere": "Cohere", "baidu": "Baidu", "tencent": "Tencent", "stepfun": "StepFun",
          "nvidia": "NVIDIA", "ibm-granite": "IBM", "microsoft": "Microsoft", "writer": "Writer",
          "perplexity": "Perplexity", "nousresearch": "Nous", "gryphe": "Gryphe"}


def release_dates():
    """label -> release date: the ECI file carried in cross-instrument, else conduct's looked-up dates."""
    xi = STUDY.parent / "cross-instrument"
    eci = {r["Model"]: r["date"] for r in csv.DictReader((xi / "eci_scores_2026-09-13.csv").open())}
    out = {}
    for ln in (xi / "eci_map_2026-09-13.tsv").read_text().splitlines():
        if ln.startswith("#") or "\t" not in ln:
            continue
        ours, theirs = ln.split("\t")[:2]
        if eci.get(theirs):
            out[ours] = eci[theirs]
    for ln in (STUDY.parent / "conduct" / "spec" / "release-dates.tsv").read_text().splitlines():
        p = ln.split("\t")
        if not ln.startswith("#") and len(p) >= 2:
            out.setdefault(p[0], p[1][:10])
    return out


def main():
    result = analyze(STUDY)
    pm, pc = result["per_model"], result["per_category"]

    # the actual prompt text per category (the clean question, sans one-word clamp)
    stim = json.loads((STUDY / "spec" / "stimulus.json").read_text())
    prompts = {s["id"]: s["turns"][0].split(" Reply with")[0].strip() for s in stim["scenes"]}

    ans = load(STUDY)
    models = [m for m in sorted(pm, key=lambda x: -pm[x]["surprisal"]) if m in ans]
    cats = sorted(pc, key=lambda c: -pc[c]["modal_share"])

    # plural merge, same as analyze
    for c in cats:
        pool = Counter(a for m in models for a in ans[m].get(c, []))
        stems = {w: w[:-1] for w in pool if w.endswith("s") and w[:-1] in pool}
        for m in models:
            if c in ans[m]:
                ans[m][c] = [stems.get(a, a) for a in ans[m][c]]

    # grid cells + per-model-per-category surprisal
    grid, cat_surp = {}, {}
    for m in models:
        row, srow = {}, {}
        for c in cats:
            mine = ans[m].get(c, [])
            others = [a for o in models if o != m for a in ans[o].get(c, [])]
            if not mine or not others:
                row[c] = None
                continue
            pool = Counter(others)
            tot, vocab = sum(pool.values()), len(set(others) | set(mine))
            modal = pool.most_common(1)[0][0]
            cnt = Counter(mine)
            entries = []
            for a, n in cnt.most_common():
                st = "novel" if pool.get(a, 0) == 0 else ("modal" if a == modal else "off")
                entries.append({"a": a, "n": n, "st": st, "share": round(pool.get(a, 0) / tot, 3)})
            row[c] = entries
            srow[c] = round(float(np.mean([-math.log2((pool.get(a, 0) + 1) / (tot + vocab)) for a in mine])), 2)
        grid[m] = row
        cat_surp[m] = srow

    # per-category field distribution, with the models behind each answer
    dists = {}
    for c in cats:
        by_answer = {}
        for m in models:
            for e in (grid[m][c] or []):
                d = by_answer.setdefault(e["a"], {"n": 0, "models": []})
                d["n"] += e["n"]
                d["models"].append(m + (f" ×{e['n']}" if e["n"] > 1 else ""))
        tot = sum(d["n"] for d in by_answer.values())
        ps = sorted(by_answer.items(), key=lambda kv: -kv[1]["n"])
        H = -sum((d["n"] / tot) * math.log2(d["n"] / tot) for _, d in ps)
        dists[c] = {"total": tot, "eff": round(2 ** H, 1),
                    "answers": [{"a": a, "n": d["n"], "share": round(d["n"] / tot, 3),
                                 "models": d["models"]} for a, d in ps]}

    # axis cuts
    def mean_of(ms):
        ms = [m for m in ms if m in pm]
        return round(float(np.mean([pm[m]["surprisal"] for m in ms])), 2) if ms else None

    origins = sorted({pm[m].get("origin") for m in models if pm[m].get("origin")})
    axes = {
        "open_vs_closed": {"open": mean_of([m for m in models if pm[m].get("open")]),
                           "closed": mean_of([m for m in models if not pm[m].get("open")])},
        "origin": {o: mean_of([m for m in models if pm[m].get("origin") == o]) for o in origins},
        "walks": {f: [{"m": m, "s": pm[m]["surprisal"]} for m in ws if m in pm] for f, ws in WALKS.items()},
    }

    slug = {r["label"]: r["slug"] for r in json.loads((STUDY / "spec" / "models.json").read_text())["models"]}
    dates = release_dates()
    blob = {
        "models": [{"label": m, "vendor": VENDOR.get(slug.get(m, "").split("/")[0], slug.get(m, "").split("/")[0]),
                    "released": dates.get(m), **{k: pm[m].get(k) for k in
                    ("surprisal", "modal_avoid", "novel_rate", "self_distinct", "type",
                     "origin", "open", "family", "ci90")}} for m in models],
        "cats": [{"id": c, "prompt": prompts.get(c, ""), "modal": pc[c]["modal"],
                  "share": pc[c]["modal_share"], "eff": dists[c]["eff"],
                  "n_distinct": pc[c]["n_distinct"]} for c in cats],
        "grid": grid,
        "cat_surp": cat_surp,
        "dists": dists,
        "axes": axes,
    }
    out = VIEWS / "data.js"
    out.write_text("window.SURP = " + json.dumps(blob) + ";\n")
    print(f"wrote {out}  ({len(models)} models, {len(cats)} categories, {out.stat().st_size // 1024}KB)")
    print(f"open {VIEWS / 'index.html'} in a browser")


if __name__ == "__main__":
    main()
