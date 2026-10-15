"""probe_self_preference.py — do models favour their own maker's products?

For each vendor that sells a product in a brand category (OWN below), the share of its own models' brand answers that
name that product, against the share among every other vendor's models, per level (clamped Name, clamped Recommend,
the two-turn pick). Answers that name no brand are left out. Zero API calls; reads the panel as brand_ladder.levels()
scores it.

    ../../.venv/bin/python probe_self_preference.py        # -> probes/self_preference.json
"""
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import brand_ladder as B  # noqa: E402
from brand_confounds import VENDOR  # noqa: E402

VENDOR = {**VENDOR, **{m: "meta-llama" for m, v in VENDOR.items() if v == "meta"}}
OWN = {"anthropic": {"ai_assistant": {"claude"}, "ai_company": {"anthropic"}},
       "openai": {"ai_assistant": {"chatgpt"}, "ai_company": {"openai"}},
       "google": {"ai_assistant": {"gemini", "google assistant", "google gemini"},
                  "ai_company": {"google", "deepmind", "google deepmind"}, "search_engine": {"google"},
                  "smartphone": {"google pixel", "google"}, "browser": {"chrome"}, "cloud": {"google cloud"}},
       "x-ai": {"ai_assistant": {"grok"}, "ai_company": {"xai"}},
       "meta-llama": {"ai_assistant": {"meta ai"}, "ai_company": {"meta"}, "social_network": {"facebook", "instagram"},
                      "messaging_app": {"whatsapp"}},
       "microsoft": {"ai_assistant": {"copilot", "microsoft copilot", "cortana"}, "search_engine": {"bing"},
                     "browser": {"microsoft edge", "edge"}, "cloud": {"azure", "microsoft azure"}},
       "qwen": {"ai_assistant": {"qwen", "tongyi qianwen"}, "cloud": {"alibaba cloud"}},
       "deepseek": {"ai_assistant": {"deepseek"}, "ai_company": {"deepseek"}},
       "mistralai": {"ai_assistant": {"le chat", "mistral"}, "ai_company": {"mistral ai", "mistral"}},
       "moonshotai": {"ai_assistant": {"kimi"}, "ai_company": {"moonshot ai"}},
       "nvidia": {"ai_company": {"nvidia"}}}
LEVELS = ("name", "recommend_clamp", "pick2")


def main():
    lv = B.levels()
    out = {}
    for v, cats in OWN.items():
        for c, brands in cats.items():
            row = {}
            for k in LEVELS:
                own = [x for m, cs in lv[k].items() if VENDOR.get(m) == v for x in cs.get(c, []) if x != B.NO_PICK]
                oth = [x for m, cs in lv[k].items() if VENDOR.get(m) != v for x in cs.get(c, []) if x != B.NO_PICK]
                row[k] = {"own_share": round(sum(x in brands for x in own) / len(own), 3) if own else None, "own_n": len(own),
                          "others_share": round(sum(x in brands for x in oth) / len(oth), 3) if oth else None}
            out[f"{v}|{c}"] = row
    (HERE / "probes" / "self_preference.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"{'vendor | category':34} " + "  ".join(f"{k:>22}" for k in LEVELS) + "   (own models / other models)")
    for key, row in out.items():
        if row["name"]["own_n"] == 0:
            continue
        cell = lambda r: f"{r['own_share']:.0%} / {r['others_share']:.0%} (n {r['own_n']})" if r["own_share"] is not None else "--"
        print(f"{key:34} " + "  ".join(f"{cell(row[k]):>22}" for k in LEVELS))


if __name__ == "__main__":
    main()
