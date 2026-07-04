"""
Build the surprisal study's review site: views/data.js.

Bakes the scorecard, the models x answers grid, per-category field distributions (with
which models gave each answer), per-model-per-category surprisal (for the model drill-down),
and the metadata-axis cuts into one blob the page draws. Self-contained: this study's
transcripts are single-turn one-word answers, so the generic arc renderer (core.js) adds
nothing and is not copied — the view is one hash-routed index.html with no deps.

    python studies/surprisal/views/build.py
    open studies/surprisal/views/index.html
"""

import json
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
    "claude": ["claude-3-haiku", "claude-haiku-4.5", "claude-sonnet-4.6", "claude-opus-4.8", "claude-fable-5", "claude-sonnet-5"],
    "gpt": ["gpt-3.5-turbo", "gpt-4-turbo", "gpt-4o", "gpt-4o-mini-2024-07-18", "gpt-4.1", "gpt-5", "gpt-5.4", "gpt-5.5"],
    "gemini": ["gemini-2.5-flash", "gemini-3.1-pro-preview", "gemini-3.5-flash"],
    "deepseek": ["deepseek-chat-v3-0324", "deepseek-v3.2", "deepseek-v4-flash", "deepseek-r1"],
    "llama": ["llama-3.3-70b-instruct", "llama-4-maverick"],
    "qwen": ["qwen-2.5-72b-instruct", "qwen3-235b-a22b-2507"],
}


def main():
    result = analyze(STUDY)
    pm, pc = result["per_model"], result["per_category"]

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

    blob = {
        "models": [{"label": m, **{k: pm[m].get(k) for k in
                    ("surprisal", "modal_avoid", "novel_rate", "self_distinct", "type",
                     "origin", "open", "family", "ci90")}} for m in models],
        "cats": [{"id": c, "modal": pc[c]["modal"], "share": pc[c]["modal_share"],
                  "eff": dists[c]["eff"], "n_distinct": pc[c]["n_distinct"]} for c in cats],
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
