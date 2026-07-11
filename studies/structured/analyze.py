"""analyze.py — the format columns vs the plain-chat census baseline.

Per format column: field concentration, sharpener-vs-reindexer diagnostics, and per-model
answer-choice surprisal computed WITHIN the column (leave-one-out, add-one smoothed — the
census formula). Headline: per-model Δ-surprisal (json − plain) over the shared categories.
"""
import json
import math
import re
import sys
from pathlib import Path
from collections import Counter

HERE = Path(__file__).resolve().parent
CONSENSUS = HERE.parent / "consensus"
sys.path.insert(0, str(CONSENSUS))
from analyze import norm  # the census junk guard: template artifacts, >15 words, acks, single letters

probe = json.loads((HERE / "probes/format_register.json").read_text())
FORMATS = list(probe["replies"].keys())

PATS = {"json": r'"word"\s*:\s*"([^"]+)"',
        "xml": r"<word>([^<]+)</word>",
        "brackets": r"\[([^\]]+)\]",
        "yaml": r"(?i)\bword\s*:\s*(.+)",
        "csv": r'(?im)^\s*"?word"?\s*\r?\n\s*(.+?)\s*$'}

def parse_word(fmt, reply):
    """Extract from the format wrapper if present, then census-normalize (junk-guarded).
    Unwrapped replies fall back to the census rule directly — a malformed-JSON essay's
    last word must NOT read as a novel answer (the reka-flash lesson)."""
    if not reply:
        return None
    m = re.search(PATS[fmt], reply)
    return norm(m.group(1)) if m else norm(reply)

def fmt_answers(fmt, label, cat):
    return [w for w in (parse_word(fmt, r) for r in probe["replies"][fmt][label][cat]) if w]

def plain_answers(label, cat):
    t = json.loads((CONSENSUS / "transcripts" / f"{label}.json").read_text())
    return [w for w in (norm(r[0].get("reply")) for r in t["scenes"][cat]["runs"]) if w]

def parse_rate(fmt, label):
    """Share of non-None raw replies that survive parsing+junk guard."""
    tot = ok = 0
    for c in CATS[fmt]:
        for r in probe["replies"][fmt][label][c]:
            if r is not None:
                tot += 1
                ok += parse_word(fmt, r) is not None
    return ok / tot if tot else 0.0

labels = sorted(probe["replies"][FORMATS[0]].keys())
CATS = {f: sorted(probe["replies"][f][labels[0]].keys()) for f in FORMATS}

def surprisal(get_answers, cats):
    """Census formula: per model, mean -log2 P(answer | field of other models), add-one."""
    per_cat = {c: {l: get_answers(l, c) for l in labels} for c in cats}
    out = {}
    for l in labels:
        scores = []
        for c in cats:
            mine = per_cat[c][l]
            field = Counter(a for o in labels if o != l for a in per_cat[c][o])
            vc = len(set(field) | set(mine))
            n = sum(field.values())
            scores += [-math.log2((field[a] + 1) / (n + vc)) for a in mine]
        out[l] = sum(scores) / len(scores) if scores else float("nan")
    return out

# ---- field concentration + sharpener diagnostics ----
print(f"panel: {len(labels)} models; json cats: {len(CATS['json'])}\n")
for f in FORMATS:
    same = novel = 0
    tail_p_sum = tail_q_sum = 0.0
    for c in CATS[f]:
        p = Counter(a for l in labels for a in plain_answers(l, c))
        q = Counter(a for l in labels for a in fmt_answers(f, l, c))
        same += q.most_common(1)[0][0] == p.most_common(1)[0][0]
        novel += sum(k for w, k in q.items() if w not in p) / sum(q.values())
        top2 = {w for w, _ in p.most_common(2)}
        tail_p_sum += sum(k for w, k in p.items() if w not in top2) / sum(p.values())
        tail_q_sum += sum(k for w, k in q.items() if w not in top2) / sum(q.values())
    n = len(CATS[f])
    print(f"{f:9} same-mode {same}/{n} | plain-unseen mass {novel/n:.1%} | "
          f"tail mass {tail_p_sum/n:.1%} -> {tail_q_sum/n:.1%}")

# ---- headline: Δ-surprisal per format vs plain, over each format's categories ----
cats_json = CATS["json"]
s_plain = surprisal(plain_answers, cats_json)
s_fmt = {f: surprisal(lambda l, c, f=f: fmt_answers(f, l, c), CATS[f]) for f in FORMATS}
s_json = s_fmt["json"]

print(f"\nΔ-surprisal (format − plain), sorted by plain; each format over its own categories:")
hdr = "".join(f"{f:>9}" for f in FORMATS)
print(f"{'model':26} {'plain':>6}{hdr}")
for l in sorted(labels, key=lambda x: -s_plain[x]):
    cells = "".join(f"{s_fmt[f][l]-s_plain[l]:>+9.2f}" for f in FORMATS)
    print(f"{l:26} {s_plain[l]:>6.2f}{cells}")
mp = sum(s_plain.values()) / len(labels)
means = "".join(f"{sum(s_fmt[f].values())/len(labels)-mp:>+9.2f}" for f in FORMATS)
print(f"{'FIELD MEAN Δ':26} {mp:>6.2f}{means}")

# ---- self-distinctness per column: does the register move the temperature or the mode? ----
def selfd(get, cats):
    out = {}
    for l in labels:
        vals = [len(set(a)) / len(a) for c in cats if (a := get(l, c))]
        out[l] = sum(vals) / len(vals) if vals else float("nan")
    return out

sd = {"plain": selfd(plain_answers, cats_json)}
for f in FORMATS:
    sd[f] = selfd(lambda l, c, f=f: fmt_answers(f, l, c), CATS[f])
print("\nself-distinctness (distinct answers / runs), field mean per column:")
print("  " + "  ".join(f"{k} {sum(v.values())/len(labels):.2f}" for k, v in sd.items()))
print("  biggest json narrowing:", ", ".join(
    f"{l} {sd['plain'][l]:.2f}->{sd['json'][l]:.2f}"
    for l in sorted(labels, key=lambda x: sd['json'][x]-sd['plain'][x])[:4]))

# ---- mode flips: categories where the json field mode differs from plain ----
print("\nmode flips (json vs plain field mode):")
for c in cats_json:
    p = Counter(a for l in labels for a in plain_answers(l, c))
    q = Counter(a for l in labels for a in fmt_answers("json", l, c))
    if q and p and q.most_common(1)[0][0] != p.most_common(1)[0][0]:
        (pm, pn), (qm, qn) = p.most_common(1)[0], q.most_common(1)[0]
        print(f"  {c}: plain {pm} {pn/sum(p.values()):.0%} -> json {qm} {qn/sum(q.values()):.0%} "
              f"(runner-up in json: {q.most_common(2)[1] if len(q)>1 else '—'})")

# ---- parse survival for the models whose surprisal ROSE under json ----
print("\nparse+junk survival rate (json), models with positive Δ:")
for l in sorted(labels, key=lambda x: s_plain[x] - s_json[x]):
    if s_json[l] > s_plain[l]:
        print(f"  {l:26} {parse_rate('json', l):.0%}")
