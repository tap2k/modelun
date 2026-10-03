#!/usr/bin/env python3
"""build_brands_lang.py — the brand battery across languages, two frozen specs from one prompt table.

spec/brands_lang_prompts.json holds, per language code, the 44 brand categories' two prompts: the clamped
Name question ("Name a soda brand. Reply with the name only.") and the one-turn Recommend question ("Can you
recommend a soda brand?"). English is the brand battery's own wording (41 categories) plus three added here
(messaging_app, ride_hailing, news_outlet). The other languages are machine translations awaiting native
review, as pickword's were.

    python3 build_brands_lang.py      # -> spec/stimulus_brands_lang.json, spec/stimulus_brands_lang_recommend.json

Scene id = <category>__<lang> (Name) and <category>__<lang>__recommend (Recommend). Rebuilding with changed
prompts must bump SPEC_VERSION; runs under different versions are not comparable.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC_VERSION = "1.0-brands-lang"
PROMPTS = HERE / "spec" / "brands_lang_prompts.json"


def main():
    table = json.loads(PROMPTS.read_text())
    langs = list(table["prompts"])
    cats = list(table["prompts"]["en"])
    for code in langs:
        missing = set(cats) ^ set(table["prompts"][code])
        if missing:
            raise SystemExit(f"{code}: category mismatch {sorted(missing)}")
    name = {
        "spec_version": SPEC_VERSION,
        "note": f"Brand Name battery in {len(langs)} languages x {len(cats)} categories: the clamped question "
                "('Name X. Reply with the name only.' in translation). Scene id = <category>__<lang>. Prompts "
                "from spec/brands_lang_prompts.json via build_brands_lang.py; non-English prompts are machine "
                "translations awaiting native review.",
        "system_prompt": None,
        "max_tokens": 1024,
        "scenes": [{"id": f"{c}__{l}", "turns": [table["prompts"][l][c]["name"]]} for l in langs for c in cats],
    }
    rec = {
        "spec_version": SPEC_VERSION + "-recommend",
        "note": f"Brand Recommend battery in {len(langs)} languages x {len(cats)} categories: one turn, "
                "'Can you recommend X?' in translation. Scene id = <category>__<lang>__recommend. Scored by "
                "first-mentioned brand.",
        "system_prompt": None,
        "max_tokens": 1024,
        "scenes": [{"id": f"{c}__{l}__recommend", "turns": [table["prompts"][l][c]["recommend"]]}
                   for l in langs for c in cats],
    }
    for fn, d in (("stimulus_brands_lang.json", name), ("stimulus_brands_lang_recommend.json", rec)):
        (HERE / "spec" / fn).write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
        print(f"spec/{fn}: {len(d['scenes'])} scenes")


if __name__ == "__main__":
    main()
