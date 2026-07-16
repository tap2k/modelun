"""Build the structured study's review site: views/data.js.

Bakes the plain-vs-format scorecard (surprisal + delta), per-category field distributions
per format, and per-model per-category answers across formats into one blob the page draws.
Self-contained single-page viewer, same pattern as the consensus explorer.

    python studies/structured/views/build.py
    open studies/structured/views/index.html
"""
import json
import math
import re
import sys
from pathlib import Path
from collections import Counter

VIEWS = Path(__file__).resolve().parent
STUDY = VIEWS.parent
CONSENSUS = STUDY.parent / "consensus"
sys.path.insert(0, str(CONSENSUS))
from analyze import norm  # census junk guard  # noqa: E402

probe = json.loads((STUDY / "probes/format_register.json").read_text())
FORMATS = ["json", "xml", "yaml", "csv", "brackets"]
PATS = {"json": r'"word"\s*:\s*"([^"]+)"', "xml": r"<word>([^<]+)</word>",
        "brackets": r"\[([^\]]+)\]", "yaml": r"(?i)\bword\s*:\s*(.+)",
        "csv": r'(?im)^\s*"?word"?\s*\r?\n\s*(.+?)\s*$'}

def parse_word(fmt, reply):
    if not reply:
        return None
    m = re.search(PATS[fmt], reply)
    return norm(m.group(1)) if m else norm(reply)

labels = sorted(probe["replies"]["json"].keys())
CATS = {f: sorted(probe["replies"][f][labels[0]].keys()) for f in FORMATS}

# Echo guard: a wrapper format hands the model a fill-in slot ({"word":"<answer>"},
# [answer], word: …), and some models return the slot's own words — the category noun
# ("[city]" for "name a city") or the placeholder ("answer"/"word"). Those are real strings,
# so the census junk guard passes them, but they are non-answers, not divergence. Drop them.
# Applied to plain too (a no-op there — nothing to echo) so every column is scored alike.
def _head_noun(cat):
    for f in FORMATS:
        p = (probe.get("formats", {}).get(f) or {}).get(cat)
        m = re.match(r"Name (?:a |an |any |some )?(.+?)\.", p) if p else None
        if m:
            return m.group(1).split()[-1].lower()
    return None

ECHO = {c: {n for n in (_head_noun(c),) if n} | {"answer", "word"} for c in CATS["json"]}

def is_answer(w, cat):
    return w is not None and w not in ECHO[cat]

def fmt_answers(fmt, label, cat):
    return [w for w in (parse_word(fmt, r) for r in probe["replies"][fmt][label][cat]) if is_answer(w, cat)]

def plain_answers(label, cat):
    t = json.loads((CONSENSUS / "transcripts" / f"{label}.json").read_text())
    return [w for w in (norm(r[0].get("reply")) for r in t["scenes"][cat]["runs"]) if is_answer(w, cat)]

def surprisal(get, cats):
    per_cat = {c: {l: get(l, c) for l in labels} for c in cats}
    out = {}
    for l in labels:
        scores = []
        for c in cats:
            field = Counter(a for o in labels if o != l for a in per_cat[c][o])
            mine = per_cat[c][l]
            vc = len(set(field) | set(mine))
            n = sum(field.values())
            scores += [-math.log2((field[a] + 1) / (n + vc)) for a in mine]
        out[l] = round(sum(scores) / len(scores), 3) if scores else None
    return out

cats_json = CATS["json"]
s_plain = surprisal(plain_answers, cats_json)
s_fmt = {f: surprisal(lambda l, c, f=f: fmt_answers(f, l, c), CATS[f]) for f in FORMATS}
s_json = s_fmt["json"]

# per-category field distributions per column (plain + each format)
field = {}
for c in cats_json:
    cols = {"plain": Counter(a for l in labels for a in plain_answers(l, c))}
    for f in FORMATS:
        if c in CATS[f]:
            cols[f] = Counter(w for l in labels for w in fmt_answers(f, l, c))
    field[c] = {k: {"top": v.most_common(12), "n": sum(v.values()), "distinct": len(v)}
                for k, v in cols.items()}

# per-model drill-down: answers per category per column
models = {}
for l in labels:
    percat = {}
    for c in cats_json:
        cols = {"plain": plain_answers(l, c)}
        for f in FORMATS:
            if c in CATS[f]:
                cols[f] = fmt_answers(f, l, c)
        percat[c] = cols
    mq = {"plain": s_plain[l], **{f: s_fmt[f][l] for f in FORMATS}}
    models[l] = {"plain": s_plain[l], "json": s_json[l],
                 "delta": round(s_json[l] - s_plain[l], 3), "mq": mq, "cats": percat}

# format compliance per model: did the reply carry the requested wrapper, and did a
# usable answer survive parsing + junk guard? (n excludes null replies — API failures)
compliance = {}
for l in labels:
    compliance[l] = {}
    for f in FORMATS:
        n = wrapped = usable = 0
        for c in CATS[f]:
            for r in probe["replies"][f][l][c]:
                if r is None:
                    continue
                n += 1
                wrapped += bool(re.search(PATS[f], r))
                usable += is_answer(parse_word(f, r), c)
        compliance[l][f] = {"n": n, "wrapped": wrapped, "usable": usable}

# aggregate register gradient: field-mean surprisal per column + significance verdict.
# p-values from probe_significance.py (per-model sign-flip permutation, 20k draws).
SIG = {"json": (0.0002, "compresses"), "xml": (0.0022, "compresses"),
       "yaml": (0.80, "no net effect"), "csv": (0.35, "no net effect"),
       "brackets": (0.0089, "loosens")}

def field_mean(sf):
    vals = [v for v in sf.values() if v is not None]
    return round(sum(vals) / len(vals), 3) if vals else None

plain_mean = field_mean(s_plain)
gradient = {"plain_mean": plain_mean, "rows": []}
for f in FORMATS:
    mf = field_mean(s_fmt[f])
    p, verdict = SIG[f]
    gradient["rows"].append({"fmt": f, "mean": mf, "delta": round(mf - plain_mean, 3),
                             "p": p, "verdict": verdict})

data = {
    "meta": {"panel": len(labels), "run_date": probe.get("run_date", "2026-07-10"),
             "formats": FORMATS, "cats_full": cats_json,
             "cats_controls": CATS["xml"],
             "prompts": probe.get("formats", {})},
    "field": field,
    "models": models,
    "gradient": gradient,
    "compliance": compliance,
    "order": sorted(labels, key=lambda l: -s_plain[l]),
}
blob = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
(VIEWS / "data.js").write_text(f"const D = {blob};\n")
size = len(blob) // 1024
print(f"wrote {VIEWS/'data.js'}  ({len(labels)} models, {len(cats_json)} categories, {size}KB)")
print(f"open {VIEWS/'index.html'} in a browser")
