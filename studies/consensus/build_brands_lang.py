#!/usr/bin/env python3
"""build_brands_lang.py — the brand battery's Name question across languages, frozen from one prompt table.

The census instrument in other languages, as the language study's deep run does for the census categories: the
clamped Name question ("Name a soda brand. Reply with the name only."), one turn, no other verbs.
spec/brands_lang_prompts.json holds it per language code for 44 categories. English is the brand battery's own
wording (41 categories) plus three added here (messaging_app, ride_hailing, news_outlet). The other languages are
machine translations awaiting native review, as pickword's were; spec/brands_lang_notes.md has the translators'
flags.

    python3 build_brands_lang.py      # -> spec/stimulus_brands_lang.json

Scene id = <category>__<lang>. Rebuilding with changed prompts must bump SPEC_VERSION; runs under different
versions are not comparable.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC_VERSION = "1.0-brands-lang"
PROMPTS = HERE / "spec" / "brands_lang_prompts.json"


def main():
    table = json.loads(PROMPTS.read_text())["prompts"]
    langs, cats = list(table), list(table["en"])
    for code in langs:
        missing = set(cats) ^ set(table[code])
        if missing:
            raise SystemExit(f"{code}: category mismatch {sorted(missing)}")
    spec = {
        "spec_version": SPEC_VERSION,
        "note": f"Brand Name battery in {len(langs)} languages x {len(cats)} categories: the clamped question "
                "('Name X. Reply with the name only.' in translation). Scene id = <category>__<lang>. Prompts "
                "from spec/brands_lang_prompts.json via build_brands_lang.py; non-English prompts are machine "
                "translations awaiting native review.",
        "system_prompt": None,
        "max_tokens": 1024,
        "scenes": [{"id": f"{c}__{l}", "turns": [table[l][c]]} for l in langs for c in cats],
    }
    (HERE / "spec" / "stimulus_brands_lang.json").write_text(json.dumps(spec, indent=1, ensure_ascii=False) + "\n")
    print(f"spec/stimulus_brands_lang.json: {len(spec['scenes'])} scenes")


if __name__ == "__main__":
    main()
