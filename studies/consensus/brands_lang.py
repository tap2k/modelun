#!/usr/bin/env python3
"""brands_lang.py — scoring and a first summary for the brand Name battery across languages (spec 1.0-brands-lang).

An answer is brands.brand_name() with latin_only=False (in other languages a mixed-script name is the name:
"카카오 T", "Яндекс Go"), then mapped through spec/brands_lang_aliases.json, a per-category table from every
distinct answer in the pilot to one lowercase Latin name, so the same brand counts once across scripts
(可口可乐, コカ・コーラ, कोका-कोला -> coca-cola). The table was drafted by four Claude agents on 2026-10-03
(3,111 answers) plus the strings the scorer fixes of that day produced, following the brands.py conventions
(English canonical names where the brand appears in English, product lines into their family, iPhone into Apple);
null marks a non-answer (a generic word, a refusal, a fragment). It needs review, and the full panel will add
strings it does not cover: those score as themselves and are listed by --unmapped.

    python3 brands_lang.py                 # -> probes/brands_lang_pilot.json, per category x language
    python3 brands_lang.py --unmapped      # answers the alias table does not cover
"""
import collections, json, sys
from pathlib import Path

from brands import brand_name

HERE = Path(__file__).resolve().parent
ALIASES = json.loads((HERE / "spec" / "brands_lang_aliases.json").read_text())
PILOT = HERE / "transcripts-brands-lang-pilot"
MISSING = object()


def score(reply, category):
    """Canonical brand for one reply, or None for a non-answer."""
    a = brand_name(reply or "", latin_only=False)
    if not a:
        return None
    m = ALIASES.get(category, {}).get(a, MISSING)
    return a if m is MISSING else m


def cells(root=PILOT):
    """(model, lang, category, reply) for every run of every scene under root/<lang>/<model>.json."""
    for f in sorted(root.glob("*/*.json")):
        d = json.loads(f.read_text())
        for sid, s in d["scenes"].items():
            cat, lang = sid.rsplit("__", 1)
            for r in s["runs"]:
                yield d["model"], lang, cat, r[0].get("reply")


def summary(root=PILOT):
    counts = collections.defaultdict(collections.Counter)      # (cat, lang) -> brand -> n
    n_cells = collections.Counter()
    for model, lang, cat, reply in cells(root):
        n_cells[(cat, lang)] += 1
        b = score(reply, cat)
        if b:
            counts[(cat, lang)][b] += 1
    cats = sorted({c for c, _ in counts})
    langs = sorted({l for _, l in counts}, key=lambda l: (l != "en", l))
    out = {}
    for c in cats:
        en = counts[(c, "en")].most_common(1)[0][0] if counts[(c, "en")] else None
        row = {}
        for l in langs:
            cnt = counts[(c, l)]
            valid = sum(cnt.values())
            if not valid:
                continue
            top, n = cnt.most_common(1)[0]
            row[l] = {"top": top, "top_share": round(n / valid, 3), "valid": valid, "cells": n_cells[(c, l)],
                      "english_top_share": round(cnt[en] / valid, 3) if en else None,
                      "answers": dict(cnt.most_common(5))}
        out[c] = {"english_top": en, "by_language": row}
    return out


def main():
    if "--unmapped" in sys.argv:
        miss = collections.Counter()
        for model, lang, cat, reply in cells():
            a = brand_name(reply or "", latin_only=False)
            if a and a not in ALIASES.get(cat, {}):
                miss[(cat, lang, a)] += 1
        for (c, l, a), n in miss.most_common():
            print(n, c, l, a)
        return
    s = summary()
    (HERE / "probes" / "brands_lang_pilot.json").write_text(json.dumps(
        {"note": "Brand Name battery across languages, five-model pilot (transcripts-brands-lang-pilot), scored by "
                 "brands_lang.score. Per category and language: the top brand, its share of valid answers, and the "
                 "share that gave the English top brand.", "categories": s}, ensure_ascii=False, indent=1) + "\n")
    print(f"probes/brands_lang_pilot.json: {len(s)} categories")


if __name__ == "__main__":
    main()
