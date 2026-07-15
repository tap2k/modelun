"""
analyze.py — One-Word Census across languages: does the monoculture replicate,
and is the prototype the same word or a culturally different one?

Mechanical, exact-match on normalized tokens (no embeddings, no judge), like the
consensus study — but the normalizer is SCRIPT-AWARE:
  en : a-z
  es : a-z + accents (aeiou-acute, n-tilde, u-diaeresis) -- accents preserved
       (ano vs anio are different words), never stripped
  hi : Devanagari block U+0900-U+097F; the sentence-final danda (danda/double
       danda) is stripped as punctuation; .lower() is a harmless no-op

Field-level report per language: modal answer + share + distinct count per
category, and how many of the pilot categories hit the >=80% monoculture bar.

    ../../.venv/bin/python analyze.py --lang es --transcripts transcripts_es
    ../../.venv/bin/python analyze.py --lang hi --transcripts transcripts_hi
    # English baseline reuses the consensus transcripts, filtered to the pilot set:
    ../../.venv/bin/python analyze.py --lang en --transcripts ../consensus/transcripts
"""
import re
import json
import argparse
from pathlib import Path
from collections import Counter

PILOT_CATS = ["color", "animal", "fruit", "tree", "flower", "bird", "country", "any_word"]

EMOJI = re.compile(r'[\U0001F000-\U0001FAFF☀-➿]')
# punctuation incl. Spanish inverted marks, the Devanagari danda, and Arabic marks
PUNCT = re.compile(r'[*_`#>\[\]().,!?"\':;¿¡।॥،؟۔]')
JUNK = re.compile(r'\[/?INST\]|<[^>]*>', re.I)
WORD = {
    "en": re.compile(r'^[a-z\-]+$|^\d+$'),
    "es": re.compile(r'^[a-záéíóúñü\-]+$|^\d+$'),
    "hi": re.compile(r'^[ऀ-ॿ\-]+$|^\d+$'),
    "mr": re.compile(r'^[ऀ-ॿ\-]+$|^\d+$'),           # Marathi shares the Devanagari block
    "ur": re.compile(r'^[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿\-]+$|^\d+$'),  # Urdu in the Arabic block
}


def norm(ans, lang):
    """Reply -> one normalized token, in the target language's script. Last valid
    word (handles models that ignore the one-word clamp). Junk/essay guard as in
    consensus. Single-code-point tokens are never answers."""
    if not ans:
        return None
    if JUNK.search(ans) or len(ans.split()) > 15:
        return None
    a = EMOJI.sub(' ', PUNCT.sub(' ', ans.strip().lower()))
    wre = WORD[lang]
    words = [w for w in a.split() if wre.match(w) and (len(w) > 1 or w.isdigit())]
    return words[-1] if words else None


def load(d, lang, cats=None):
    out = {}
    for p in sorted(Path(d).glob("*.json")):
        dd = json.loads(p.read_text())
        scenes = {}
        for sid, s in dd["scenes"].items():
            if cats is not None and sid not in cats:
                continue
            toks = [t for t in (norm(r[0].get("reply"), lang) for r in s["runs"] if r) if t]
            if toks:
                scenes[sid] = toks
        out[dd["model"]] = scenes
    return out


def main():
    ap = argparse.ArgumentParser(description="One-Word Census convergence, one language.")
    ap.add_argument("--lang", required=True, choices=["en", "es", "hi", "ur", "mr"])
    ap.add_argument("--transcripts", required=True, help="transcripts dir")
    ap.add_argument("--pilot", action="store_true", help="restrict to the 8 pilot categories")
    args = ap.parse_args()

    ans = load(args.transcripts, args.lang, PILOT_CATS if args.pilot else None)
    ans = {m: sc for m, sc in ans.items() if sc}
    present = {c for sc in ans.values() for c in sc}

    def _share(c):
        pool = Counter(a for m in ans for a in ans[m].get(c, []))
        return pool.most_common(1)[0][1] / sum(pool.values()) if pool else 0
    cats = sorted(present, key=lambda c: -_share(c))

    print(f"\n=== {args.lang.upper()}  ({len(ans)} models, {len(cats)} categories) ===")
    print(f"  {'category':10} {'modal':>14}  share  distinct   top-3")
    print("  " + "-" * 62)
    ge80, shares = 0, []
    for c in cats:
        pool = Counter(a for m in ans for a in ans[m].get(c, []))
        n = sum(pool.values())
        (modal, cnt), = pool.most_common(1)
        share = cnt / n
        shares.append(share)
        ge80 += share >= 0.8
        top3 = "  ".join(f"{w} {v/n:.0%}" for w, v in pool.most_common(3))
        print(f"  {c:10} {modal:>14}  {share:4.0%}   {len(pool):5}    {top3}")
    print("  " + "-" * 62)
    print(f"  {args.lang}: >=80% modal in {ge80}/{len(cats)} categories | mean modal share {sum(shares)/len(shares):.0%}")


if __name__ == "__main__":
    main()
