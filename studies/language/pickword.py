"""
pickword.py — the One-Word Census's headline prompt ("Pick a word.") asked in
44 languages. Does every language collapse onto a single word, and is it the same
word or a culturally different one? (English serendipity, Spanish sol, Hindi jeevan.)

Mechanical, exact-match on normalized tokens, like consensus/analyze.py — but the
normalizer is keyed by scene id, which IS the language code, and each language maps
to its script's Unicode block:

  latin(+accents): en es fr de pt it     cyrillic: ru        arabic: ar ur
  devanagari:      hi mr                 bengali:  bn        gurmukhi: pa
  gujarati:        gu                    tamil:    ta        telugu:   te
  kannada:         kn                    malayalam: ml
  han/kana:        zh ja                 hangul:   ko

CJK/Hangul are space-free scripts where a single character is a valid word, so the
>=2-codepoint guard is relaxed to >=1 for those.

    ../../.venv/bin/python pickword.py --transcripts transcripts_pickword
    ../../.venv/bin/python pickword.py --transcripts transcripts_pickword --lang hi   # one language
"""
import re
import json
import argparse
from pathlib import Path
from collections import Counter

# scene-id order = report order (baseline, international, then Indian languages)
LANGS = ["en", "es", "fr", "de", "pt", "it", "ru", "ar",
         "hi", "mr", "bn", "pa", "gu", "ta", "te", "kn", "ml", "ur",
         "zh", "ja", "ko",
         "nl", "pl", "uk", "tr", "el", "he", "fa",
         "id", "ms", "jv", "tl", "vi", "th", "my",
         "ne", "sd", "sdd",
         "sw", "am", "yo", "ha",
         "yue", "zht"]

LATIN     = r'a-zß-ɏɐ-ʯḀ-ỿ̀-ͯ'
CYRILLIC  = r'Ѐ-ӿ'
ARABIC    = r'؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿'
DEVANAGARI= r'ऀ-ॿ'
BENGALI   = r'ঀ-৿'
GURMUKHI  = r'਀-੿'
GUJARATI  = r'઀-૿'
TAMIL     = r'஀-௿'
TELUGU    = r'ఀ-౿'
KANNADA   = r'ಀ-೿'
MALAYALAM = r'ഀ-ൿ'
HAN       = r'㐀-䶿一-鿿'
KANA      = r'぀-ヿ'
HANGUL    = r'가-힣ᄀ-ᇿ㄰-㆏'
ETHIOPIC  = r'ሀ-፿'
THAI      = r'฀-๿'
HEBREW    = r'֐-׿יִ-ﭏ'
GREEK     = r'Ͱ-Ͽἀ-῿'
MYANMAR   = r'က-႟'

RANGE = {
    "en": r'a-z', "es": LATIN, "fr": LATIN, "de": LATIN, "pt": LATIN, "it": LATIN,
    "ru": CYRILLIC, "ar": ARABIC, "ur": ARABIC,
    "hi": DEVANAGARI, "mr": DEVANAGARI, "bn": BENGALI, "pa": GURMUKHI,
    "gu": GUJARATI, "ta": TAMIL, "te": TELUGU, "kn": KANNADA, "ml": MALAYALAM,
    "zh": HAN, "ja": HAN + KANA, "ko": HANGUL,
    # --- expansion (2026-07-20) ---
    "tl": LATIN, "id": LATIN, "ms": LATIN, "jv": LATIN, "vi": LATIN,
    "tr": LATIN, "pl": LATIN, "nl": LATIN, "sw": LATIN, "yo": LATIN, "ha": LATIN,
    "th": THAI, "my": MYANMAR, "am": ETHIOPIC, "he": HEBREW, "el": GREEK,
    "uk": CYRILLIC, "fa": ARABIC, "sd": ARABIC, "ne": DEVANAGARI, "sdd": DEVANAGARI,
    "yue": HAN, "zht": HAN,
}
WORD = {l: re.compile(fr'^[{r}\-]+$|^\d+$') for l, r in RANGE.items()}
CJK_LIKE = {"zh", "ja", "ko", "yue", "zht"}   # single character is a valid word

EMOJI = re.compile(r'[\U0001F000-\U0001FAFF☀-➿]')
# latin/CJK/arabic/indic punctuation; danda, arabic full-stop, CJK full/half marks
PUNCT = re.compile(r'[*_`#>\[\](){}.,!?"\'’:;¿¡।॥،؟۔٪。、！？：；（）「」『』・…—–]')
JUNK  = re.compile(r'\[/?INST\]|<[^>]*>', re.I)


def norm(ans, lang):
    """Reply -> one normalized token in the target language's script. Last valid
    word (handles ignored one-word clamp). Junk/essay guard. For alphabetic scripts
    a lone code point is never a word; for CJK/Hangul it can be."""
    if not ans:
        return None
    if JUNK.search(ans) or len(ans.split()) > 15:
        return None
    a = EMOJI.sub(' ', PUNCT.sub(' ', ans.strip().lower()))
    wre = WORD[lang]
    minlen = 1 if lang in CJK_LIKE else 2
    words = [w for w in a.split() if wre.match(w) and (len(w) >= minlen or w.isdigit())]
    return words[-1] if words else None


def load(d):
    """model -> {lang: [tokens]}, plus raw run counts per (model,lang) for compliance."""
    out, raw = {}, {}
    for p in sorted(Path(d).glob("*.json")):
        dd = json.loads(p.read_text())
        scenes = {}
        for lang, s in dd["scenes"].items():
            if lang not in RANGE:
                continue
            runs = [r for r in s["runs"] if r]
            toks = [t for t in (norm(r[0].get("reply"), lang) for r in runs) if t]
            scenes[lang] = toks
            raw[(dd["model"], lang)] = (len(toks), len(runs))
        out[dd["model"]] = scenes
    return out, raw


def main():
    ap = argparse.ArgumentParser(description="Pick-a-word convergence across languages.")
    ap.add_argument("--transcripts", required=True, help="pickword transcripts dir")
    ap.add_argument("--lang", help="restrict to one language code")
    args = ap.parse_args()

    ans, raw = load(args.transcripts)
    langs = [args.lang] if args.lang else [l for l in LANGS if l in RANGE]

    print(f"\n=== PICK A WORD  ({len(ans)} models) ===")
    print(f"  {'lang':4} {'modal':>14}  share  distinct  compliance   top-3")
    print("  " + "-" * 74)
    ge50, shares = 0, []
    for l in langs:
        pool = Counter(a for m in ans for a in ans[m].get(l, []))
        if not pool:
            print(f"  {l:4} {'(no data)':>14}")
            continue
        n = sum(pool.values())
        got = sum(v for v, _ in (raw.get((m, l), (0, 0)) for m in ans))
        tot = sum(t for _, t in (raw.get((m, l), (0, 0)) for m in ans))
        comp = got / tot if tot else 0
        (modal, cnt), = pool.most_common(1)
        share = cnt / n
        shares.append(share)
        ge50 += share >= 0.5
        top3 = "  ".join(f"{w} {v/n:.0%}" for w, v in pool.most_common(3))
        print(f"  {l:4} {modal:>14}  {share:4.0%}   {len(pool):5}    {comp:5.0%}     {top3}")
    print("  " + "-" * 74)
    if shares:
        print(f"  >=50% modal in {ge50}/{len(shares)} languages | mean modal share {sum(shares)/len(shares):.0%}")


if __name__ == "__main__":
    main()
