"""
gloss.py — concept-cluster the pickword answers.

Exact-word match measures LEXICAL convergence; प्रेम, प्यार, मोहब्बत count as three
answers when they are all "love." To test whether non-English converges harder at the
CONCEPT level (the naive-hypothesis question), gloss every unique word to a single
English concept via a strong multilingual model, tagging instruction-echo / filler as
FILLER, then recompute modal share on concepts.

    python studies/language/gloss.py            # build spec/gloss_map.json + print lexical-vs-concept
    python studies/language/gloss.py --show     # just print from the cached map

Cheap: ~1.2k unique words, one call per language, temp 0.
"""
import os
import re
import sys
import json
import time
import argparse
from pathlib import Path
from collections import Counter

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pickword as P

STUDY = Path(__file__).resolve().parent
MAP = STUDY / "spec" / "gloss_map.json"
API = "https://openrouter.ai/api/v1/chat/completions"
GLOSSER = "google/gemini-2.5-flash"

LANGNAME = {"en": "English", "es": "Spanish", "fr": "French", "de": "German", "pt": "Portuguese",
            "it": "Italian", "ru": "Russian", "ar": "Arabic", "hi": "Hindi", "mr": "Marathi",
            "bn": "Bengali", "pa": "Punjabi", "gu": "Gujarati", "ta": "Tamil", "te": "Telugu",
            "kn": "Kannada", "ml": "Malayalam", "ur": "Urdu", "zh": "Chinese", "ja": "Japanese",
            "ko": "Korean"}

PROMPT = """You are glossing single words that language models produced when asked to "pick a word" in {lang}.
For each word give ONE lowercase English word capturing its core meaning — a concept label (e.g. amor->love, \
प्रेम->love, 光->light, liberté->freedom). Group synonyms under the same English concept.
If an item is NOT a genuine content word but an instruction-echo, acknowledgment, greeting, filler or meta-word \
(e.g. the word for "word", "okay", "yes", "hello", "please", "clarify", "choose", "name"), output "FILLER".
Return ONLY a JSON object mapping each input word to its gloss. Input words:
{words}"""


def load_words():
    words = {}
    for p in sorted((STUDY / "transcripts_pickword").glob("*.json")):
        dd = json.loads(p.read_text())
        for lang, s in dd["scenes"].items():
            if lang not in P.RANGE:
                continue
            for r in s["runs"]:
                if r:
                    t = P.norm(r[0].get("reply"), lang)
                    if t:
                        words.setdefault(lang, set()).add(t)
    return {l: sorted(ws) for l, ws in words.items()}


def call(lang, words):
    msg = PROMPT.format(lang=LANGNAME.get(lang, lang), words=json.dumps(words, ensure_ascii=False))
    for _ in range(3):
        try:
            r = requests.post(API, headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
                              json={"model": GLOSSER, "messages": [{"role": "user", "content": msg}],
                                    "temperature": 0, "max_tokens": 8000}, timeout=90)
            r.raise_for_status()
            c = r.json()["choices"][0]["message"]["content"]
            c = re.sub(r"^```(json)?|```$", "", c.strip(), flags=re.M).strip()
            return json.loads(c[c.index("{"):c.rindex("}") + 1])
        except Exception as e:
            print(f"  {lang} retry: {e}", file=sys.stderr)
            time.sleep(3)
    return {}


def build():
    from dotenv import load_dotenv
    load_dotenv(STUDY.parent.parent / ".env")
    words = load_words()
    gmap = {}
    for lang in P.LANGS:
        if lang not in words:
            continue
        g = call(lang, words[lang])
        gmap[lang] = {w: (g.get(w) or "?").lower().strip() for w in words[lang]}
        print(f"  {lang}: {len(words[lang])} words glossed")
    MAP.write_text(json.dumps(gmap, ensure_ascii=False, indent=0))
    print(f"wrote {MAP}")
    return gmap


def concept_pool(lang, gmap, drop_filler=True):
    """Pool this language's answers, remapped word->concept, filler dropped."""
    pool = Counter()
    for p in sorted((STUDY / "transcripts_pickword").glob("*.json")):
        dd = json.loads(p.read_text())
        s = dd["scenes"].get(lang)
        if not s:
            continue
        for r in s["runs"]:
            if r:
                t = P.norm(r[0].get("reply"), lang)
                if not t:
                    continue
                c = gmap[lang].get(t, "?")
                if drop_filler and c == "filler":
                    continue
                pool[c] += 1
    return pool


def report(gmap):
    import math
    words = load_words()
    print(f"\n{'lang':4} {'lexical modal':>22} {'concept modal':>22}  {'lex%':>5} {'con%':>5} {'Δ':>5}")
    print("-" * 74)
    for lang in P.LANGS:
        if lang not in gmap:
            continue
        # lexical
        lp = Counter()
        for p in sorted((STUDY / "transcripts_pickword").glob("*.json")):
            s = json.loads(p.read_text())["scenes"].get(lang)
            if s:
                for r in s["runs"]:
                    if r:
                        t = P.norm(r[0].get("reply"), lang)
                        if t:
                            lp[t] += 1
        cp = concept_pool(lang, gmap)
        ln, cn = sum(lp.values()), sum(cp.values())
        lm, lc = lp.most_common(1)[0]
        cm, cc = cp.most_common(1)[0]
        ls, cs = lc / ln, cc / cn
        print(f"{lang:4} {lm + ' ' + f'{ls:.0%}':>22} {cm + ' ' + f'{cs:.0%}':>22}  "
              f"{ls:4.0%} {cs:4.0%} {cs - ls:+4.0%}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--show", action="store_true", help="use cached gloss_map.json")
    args = ap.parse_args()
    gmap = json.loads(MAP.read_text()) if args.show and MAP.exists() else build()
    report(gmap)


if __name__ == "__main__":
    main()
