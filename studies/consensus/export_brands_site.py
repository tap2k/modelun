"""Export the brand-battery numbers behind the business-facing brands page (convovo.ai/brands and its prototype).

Writes one JSON file: a simplified grid (key categories x one flagship model per lab), each category's top
brands across the whole panel, top-brand shares by release half-year, and one open model's training ladder
(OLMo 3.1 32B, base/SFT/DPO/RL) for "name a brand". Scoring is analyze.answers(study, "brands") (whole-name,
brands.py); release dates come from views/build.release_dates().

    ../../.venv/bin/python export_brands_site.py OUT.json
"""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "views"))
from analyze import answers          # noqa: E402
from brands import brand_name         # noqa: E402
import build                          # noqa: E402

CATS = ["coffee_chain", "soda", "car_brand", "search_engine", "smartphone", "running_shoe", "ai_assistant",
        "airline", "payment_app", "luxury"]
MODELS = [("OpenAI", "gpt-6.1-sol"), ("Anthropic", "claude-opus-5.5"), ("Google", "gemini-3.8-flash"),
          ("xAI", "grok-4.7"), ("Meta", "muse-spark-1.3"), ("DeepSeek", "deepseek-v4-pro"),
          ("Alibaba", "qwen3.8-2.4t-a95b"), ("Mistral", "mistral-small-2603"),
          ("NVIDIA", "nemotron-3-ultra-550b-a55b"), ("Moonshot", "kimi-k3"), ("Z.ai", "glm-5.3")]
TREND_CATS = ["ai_assistant", "running_shoe", "hotel", "payment_app", "smartphone", "soda"]
LADDER = HERE / "probes" / "olmo_census_32b_expanded"   # Contract A, one file per stage
STAGES = ["base", "sft", "dpo", "rl"]


def half(d):
    return f"{d[:4]} H{1 if int(d[5:7]) <= 6 else 2}"


def main(out):
    ans = answers(HERE, "brands")
    dates = {m: str(d) for m, d in build.release_dates().items()}
    prompts = {s["id"]: s["turns"][0].split(" Reply with")[0]
               for s in json.loads((HERE / "spec" / "stimulus_brands.json").read_text())["scenes"]}
    grid = []
    for lab, m in MODELS:
        row = {"lab": lab, "model": m, "released": dates.get(m, "")[:7], "cells": {}}
        for c in CATS:
            a = ans.get(m, {}).get(c, [])
            if a:
                top, k = Counter(a).most_common(1)[0]
                row["cells"][c] = {"brand": top, "k": k, "n": len(a)}
        grid.append(row)
    field = {}
    for c in sorted({c for m in ans.values() for c in m}):
        cnt = Counter(x for m in ans.values() for x in m.get(c, []))
        n = sum(cnt.values())
        field[c] = {"prompt": prompts.get(c, c), "n": n, "models": sum(1 for m in ans.values() if m.get(c)),
                    "top": [{"brand": b, "share": round(k / n, 4)} for b, k in cnt.most_common(4)]}
    trends = {}
    for c in TREND_CATS:
        bins = {}
        for m, cats in ans.items():
            if m in dates and dates[m] and c in cats:
                bins.setdefault(half(dates[m]), []).extend(cats[c])
        top = [b for b, _ in Counter(x for v in bins.values() for x in v).most_common(4)]
        trends[c] = {"prompt": prompts.get(c, c), "brands": top,
                     "bins": [{"bin": b, "models": sum(1 for m in ans if m in dates and dates[m] and half(dates[m]) == b and c in ans[m]),
                               "answers": len(v), "share": {t: round(v.count(t) / len(v), 3) for t in top}}
                              for b, v in sorted(bins.items()) if b >= "2024 H1"]}
    stages = {t["stage"]: t["scenes"] for t in (json.loads(f.read_text()) for f in LADDER.glob("*.json"))}
    panel = Counter(x for m in ans.values() for x in m.get("brand", []))   # ties break toward brands the panel names
    ladder = []
    for st in STAGES:
        replies = [run[-1]["reply"] for run in stages[st]["brand"]["runs"]]
        cnt = Counter(x for x in map(brand_name, replies) if x)
        top = sorted(cnt.items(), key=lambda kv: (-kv[1], -panel.get(kv[0], 0), kv[0]))[:6]
        ladder.append({"stage": st, "n": len(replies), "top": top})
    meta = {"panel_models": len(ans), "categories": len(field), "answers_per_model": 8,
            "spec": "1.0-brands", "ladder_model": "OLMo 3.1 32B (8-bit), 20 samples per stage"}
    Path(out).write_text(json.dumps({"meta": meta, "cats": CATS, "grid": grid, "field": field,
                                     "trends": trends, "ladder": ladder}, indent=1, ensure_ascii=False))
    print(f"wrote {out}")


if __name__ == "__main__":
    main(sys.argv[1])
