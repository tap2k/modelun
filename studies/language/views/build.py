"""
Build the pickword panel view: views/data.js (window.PICK).

The pickword study is one prompt ("Pick a word.") asked in 44 languages across 44
models. This bakes, for the viewer:
  - per-language field stats: modal, share, distinct, effective-N, compliance, and the
    base-rate Zipf of the modal word (wordfreq, where the language is covered)
  - the models x languages grid, each cell the model's word(s), classed modal/off/novel
    relative to that language's field (leave-one-out)
  - per-language field distribution with the models behind each answer + a gloss
  - per-model cross-lingual stats: compliance, novel-rate, modal-avoidance

    python studies/language/views/build.py
    open studies/language/views/index.html
"""
import json
import math
import sys
from pathlib import Path
from collections import Counter

VIEWS = Path(__file__).resolve().parent
STUDY = VIEWS.parent
sys.path.insert(0, str(STUDY))
import pickword as P  # noqa: E402
from gloss import FILLER  # noqa: E402

GMAP = {}
_mp = STUDY / "spec" / "gloss_map.json"
if _mp.exists():
    GMAP = json.loads(_mp.read_text())

from wordfreq import zipf_frequency, available_languages  # noqa: E402

AV = set(available_languages())

LANGMETA = {
    "en": ("English", "Latin"), "es": ("Spanish", "Latin"), "fr": ("French", "Latin"),
    "de": ("German", "Latin"), "pt": ("Portuguese", "Latin"), "it": ("Italian", "Latin"),
    "ru": ("Russian", "Cyrillic"), "ar": ("Arabic", "Arabic"),
    "hi": ("Hindi", "Devanagari"), "mr": ("Marathi", "Devanagari"), "bn": ("Bengali", "Bengali"),
    "pa": ("Punjabi", "Gurmukhi"), "gu": ("Gujarati", "Gujarati"), "ta": ("Tamil", "Tamil"),
    "te": ("Telugu", "Telugu"), "kn": ("Kannada", "Kannada"), "ml": ("Malayalam", "Malayalam"),
    "ur": ("Urdu", "Arabic"), "zh": ("Chinese", "Han"), "ja": ("Japanese", "Han+Kana"),
    "ko": ("Korean", "Hangul"),
    "nl": ("Dutch", "Latin"), "pl": ("Polish", "Latin"), "uk": ("Ukrainian", "Cyrillic"),
    "tr": ("Turkish", "Latin"), "el": ("Greek", "Greek"), "he": ("Hebrew", "Hebrew"),
    "fa": ("Persian", "Arabic"), "id": ("Indonesian", "Latin"), "ms": ("Malay", "Latin"),
    "jv": ("Javanese", "Latin"), "tl": ("Tagalog", "Latin"), "vi": ("Vietnamese", "Latin"),
    "th": ("Thai", "Thai"), "my": ("Burmese", "Myanmar"), "ne": ("Nepali", "Devanagari"),
    "sd": ("Sindhi", "Arabic"), "sdd": ("Sindhi", "Devanagari"), "sw": ("Swahili", "Latin"),
    "am": ("Amharic", "Ge'ez"), "yo": ("Yoruba", "Latin"), "ha": ("Hausa", "Latin"),
    "yue": ("Cantonese", "Han"), "zht": ("Chinese (Trad.)", "Han"),
}


def zipf(w, l):
    l = {"zht": "zh"}.get(l, l)  # wordfreq's zh list covers traditional characters
    if l not in AV:
        return None
    z = zipf_frequency(w, l)
    return round(z, 2) if z else None


# dropped from the published panel: prompt-echo / greeting-default modal, or <85% in-script
# compliance (mostly very-low-resource; sdd/yue are AI-mistranslated prompts awaiting native review).
EXCLUDE = {"sdd", "yue", "tr", "th", "yo", "ha", "jv"}


def main():
    ans, raw = P.load(str(STUDY / "transcripts_pickword"))
    models = sorted(ans)
    langs = [l for l in P.LANGS if l not in EXCLUDE and any(ans[m].get(l) for m in models)]

    # grid: leave-one-out classification per (model, lang)
    grid = {}
    for m in models:
        row = {}
        for l in langs:
            mine = ans[m].get(l, [])
            others = [a for o in models if o != m for a in ans[o].get(l, [])]
            if not mine or not others:
                row[l] = None
                continue
            pool = Counter(others)
            tot = sum(pool.values())
            modal = pool.most_common(1)[0][0]
            entries = []
            for a, n in Counter(mine).most_common():
                st = "novel" if pool.get(a, 0) == 0 else ("modal" if a == modal else "off")
                entries.append({"a": a, "n": n, "st": st, "share": round(pool.get(a, 0) / tot, 3)})
            row[l] = entries
        grid[m] = row

    # per-language field distribution + stats
    langrows, dists = [], {}
    for l in langs:
        by_answer = {}
        for m in models:
            for e in (grid[m][l] or []):
                d = by_answer.setdefault(e["a"], {"n": 0, "models": []})
                d["n"] += e["n"]
                d["models"].append(m + (f" ×{e['n']}" if e["n"] > 1 else ""))
        tot = sum(d["n"] for d in by_answer.values())
        ps = sorted(by_answer.items(), key=lambda kv: -kv[1]["n"])
        H = -sum((d["n"] / tot) * math.log2(d["n"] / tot) for _, d in ps) if tot else 0
        modal, mcnt = ps[0][0], ps[0][1]["n"]
        # compliance: in-script replies / total runs, meaned across models
        got = sum(raw.get((m, l), (0, 0))[0] for m in models)
        totruns = sum(raw.get((m, l), (0, 0))[1] for m in models)
        z5 = [zipf(a, l) for a, _ in ps[:5]]
        z5 = [z for z in z5 if z is not None]
        name, script = LANGMETA[l]
        gm = GMAP.get(l, {})
        top5 = [{"a": a, "share": round(d["n"] / tot, 3), "gloss": gm.get(a, "")}
                for a, d in ps[:5]]
        # concept convergence: remap word->concept via glosser map, drop filler and unglossed words
        cmodal, cshare = None, None
        if gm:
            cpool = Counter()
            for a, d in ps:
                c = gm.get(a)
                if c and c not in FILLER:
                    cpool[c] += d["n"]
            if cpool:
                ctot = sum(cpool.values())
                cmodal, ccnt = cpool.most_common(1)[0]
                cshare = round(ccnt / ctot, 3)
        langrows.append({
            "code": l, "name": name, "script": script, "modal": modal,
            "share": round(mcnt / tot, 3), "n_distinct": len(ps), "eff": round(2 ** H, 1),
            "compliance": round(got / totruns, 3) if totruns else 0,
            "zipf": zipf(modal, l), "meanz5": round(sum(z5) / len(z5), 2) if z5 else None,
            "top5": top5, "cmodal": cmodal, "cshare": cshare,
        })
        dists[l] = {"total": tot, "eff": round(2 ** H, 1),
                    "answers": [{"a": a, "n": d["n"], "share": round(d["n"] / tot, 3),
                                 "gloss": gm.get(a, ""),
                                 "models": d["models"]} for a, d in ps]}

    # per-model cross-lingual stats
    mrows = []
    for m in models:
        nruns = novel = off = fill = 0
        for l in langs:
            c = grid[m][l]
            if not c:
                continue
            gm = GMAP.get(l, {})
            for e in c:
                nruns += e["n"]
                if e["st"] == "novel":
                    novel += e["n"]
                if e["st"] != "modal":
                    off += e["n"]
                if gm.get(e["a"]) in FILLER:
                    fill += e["n"]
        gotall = sum(raw.get((m, l), (0, 0))[0] for l in langs)
        totall = sum(raw.get((m, l), (0, 0))[1] for l in langs)
        mrows.append({"label": m,
                      "compliance": round(gotall / totall, 3) if totall else 0,
                      "novel_rate": round(novel / nruns, 3) if nruns else 0,
                      "modal_avoid": round(off / nruns, 3) if nruns else 0,
                      "filler_rate": round(fill / nruns, 3) if nruns else 0})
    mrows.sort(key=lambda r: -r["filler_rate"])

    blob = {"langs": langrows, "grid": grid, "dists": dists, "models": mrows,
            "n_models": len(models)}
    out = VIEWS / "data.js"
    out.write_text("window.PICK = " + json.dumps(blob, ensure_ascii=False) + ";\n")
    print(f"wrote {out}  ({len(models)} models, {len(langs)} languages, {out.stat().st_size // 1024}KB)")
    print(f"open {VIEWS / 'index.html'}")


if __name__ == "__main__":
    main()
