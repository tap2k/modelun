"""probe_novel_audit.py — category-membership audit of every field-novel answer.

Addresses the "surprisal = capability degradation" critique: novel answers (the
answers no other model gave) are where a low-capability model could inflate its score
with non-answers the junk guard misses. The junk guard checks artifacts, length, and
single letters; it never checks whether an answer is a MEMBER of its category. This
audit closes that gap by hand-labeling every novel answer, then recomputing the
headline scores for the most-divergent models under a worst-case reclassification.

No new API calls: everything derives from the frozen transcripts.

PRE-SPECIFIED RUBRIC (fixed before recompute, citable for camera-ready). Each novel
(model, category, answer) is labeled on category membership:
  valid       — unambiguous category member (persimmon for fruit; crocodile for animal).
                For any_word, ANY real word qualifies (the category is "a word").
  contested   — membership is arguable or referent-by-ellipsis (lava for dessert = lava
                cake; a spelling variant of a real member). Flagged for adjudication.
  wrong       — a real word that is not a member of the category (dolphin for fish;
                pineapple for tree).
  degenerate  — misspelling, non-word, hallucinated token, category-name-as-answer, or a
                template/extraction artifact the junk guard missed (jones for city;
                an IPA fragment; "Copper ASSISTANT: Zinc").
Only `wrong` and `degenerate` are treated as failed cells in the recompute; `valid` and
`contested` count as answers. A novel answer being unusual is the SIGNAL, not a defect —
crocodile is novel only because the field said lion; it is not degradation.

    ../../.venv/bin/python probe_novel_audit.py
      -> probes/novel_audit.csv        (every novel answer, labeled, with rationale)
      -> probes/extraction_audit.csv   (every >1-word passed cell, extraction checked)
      -> console: validity %, per-model split, reclassification deltas & rank changes
"""

import csv
import json
import math
import sys
from pathlib import Path
from collections import Counter

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from analyze import norm

# ---- load transcripts, keeping raw replies alongside normalized tokens ----
raw = {}
for p in sorted((HERE / "transcripts").glob("*.json")):
    d = json.loads(p.read_text())
    scenes = {}
    for sid, sc in d["scenes"].items():
        cells = [(norm(run[0].get("reply")), run[0].get("reply"))
                 for run in sc["runs"] if run]
        cells = [(t, r) for t, r in cells if t]
        if cells:
            scenes[sid] = cells
    raw[d["model"]] = scenes

models = sorted(m for m in raw if raw[m])
cats = sorted({c for m in models for c in raw[m]})
for c in cats:  # plural merge, identical to analyze.py
    pool = Counter(t for m in models for t, _ in raw[m].get(c, []))
    stems = {w: w[:-1] for w in pool if w.endswith("s") and w[:-1] in pool}
    for m in models:
        if c in raw[m]:
            raw[m][c] = [(stems.get(t, t), r) for t, r in raw[m][c]]

# ---- hand-labels (keyed by category|answer|model; the audit's substantive content) ----
# Anything not listed defaults to "valid" — the overwhelming majority are unimpeachable
# category members that are simply not the crowd's pick. Only exceptions are recorded.
WRONG = {
    ("fish", "dolphin", "mythomax-l2-13b"): "dolphin is a mammal, not a fish",
    ("tree", "pineapple", "hunyuan-a13b-instruct"): "pineapple is not a tree",
}
DEGENERATE = {
    ("country", "kroa", "hermes-4-70b"): "IPA fragment '(kroa:ʃi.a)' for Croatia; extraction artifact",
    ("city", "jones", "gemma-3-27b-it"): "'jones' is not a city; hallucinated token (recurs across categories)",
    ("hobby", "jones", "gemma-3-27b-it"): "'jones' is not a hobby; same hallucinated token",
    ("metal", "jones", "gemma-3-27b-it"): "'jones' is not a metal; same hallucinated token",
    ("metal", "zinc", "wizardlm-2-8x22b"): "template leak 'Copper ASSISTANT: Zinc'; answer ambiguous/contaminated",
    ("cheese", "cheese", "command-a"): "answered the category name itself",
}
CONTESTED = {
    ("dessert", "lava", "hermes-4-70b"): "'Lava.' — bare lava is not a dessert; reads as lava cake by ellipsis [ADJUDICATE]",
    ("dinosaur", "trex", "deepseek-r1"): "'Trex' = T. rex, a valid dinosaur; spelling variant of the modal referent [ADJUDICATE]",
}

def label_for(cat, ans, model):
    k = (cat, ans, model)
    if k in DEGENERATE:
        return "degenerate", DEGENERATE[k]
    if k in WRONG:
        return "wrong", WRONG[k]
    if k in CONTESTED:
        return "contested", CONTESTED[k]
    if cat == "any_word":
        return "valid", "any real word satisfies the 'pick a word' category"
    return "valid", "unambiguous category member; novel only because no other model chose it"

# ---- collect and label every field-novel answer ----
novel = []
for m in models:
    for c in cats:
        others = Counter(t for o in models if o != m for t, _ in raw[o].get(c, []))
        for t, r in raw[m].get(c, []):
            if others.get(t, 0) == 0:
                lab, why = label_for(c, t, m)
                novel.append({"model": m, "category": c, "answer": t,
                              "raw_reply": (r or "").replace("\n", " ").strip()[:120],
                              "label": lab, "rationale": why})

with (HERE / "probes" / "novel_audit.csv").open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["model", "category", "answer", "raw_reply", "label", "rationale"])
    w.writeheader()
    w.writerows(sorted(novel, key=lambda x: (x["label"], x["category"], x["answer"])))

# ---- extraction-leak audit: every passed cell whose raw reply is >1 word ----
ext = []
for m in models:
    for c in cats:
        for t, r in raw[m].get(c, []):
            if r and len(r.split()) > 1:
                is_novel = all(t not in [x for x, _ in raw[o].get(c, [])]
                               for o in models if o != m)
                ext.append({"model": m, "category": c, "extracted": t,
                            "n_words": len(r.split()),
                            "raw_reply": r.replace("\n", " ").strip()[:120],
                            "is_novel": is_novel})
with (HERE / "probes" / "extraction_audit.csv").open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["model", "category", "extracted", "n_words", "raw_reply", "is_novel"])
    w.writeheader()
    w.writerows(sorted(ext, key=lambda x: -x["n_words"]))

# ---- surprisal recompute with a reclassification set dropped as failed cells ----
def surprisal(drop=frozenset()):
    """mean -log2 P(answer | field), leave-one-out, add-one smoothed. `drop` is a set of
    (model, category, answer) treated as failed cells (removed from the answering model)."""
    out = {}
    for m in models:
        ss = []
        for c in cats:
            mine = [t for t, _ in raw[m].get(c, []) if (m, c, t) not in drop]
            others = [t for o in models if o != m for t, _ in raw[o].get(c, [])]
            if not mine or not others:
                continue
            pool = Counter(others)
            total, vocab = sum(pool.values()), len(set(others) | set(mine))
            ss.extend(-math.log2((pool.get(a, 0) + 1) / (total + vocab)) for a in mine)
        out[m] = float(np.mean(ss)) if ss else float("nan")
    return out

def novel_rate(drop=frozenset()):
    out = {}
    for m in models:
        n = k = 0
        for c in cats:
            others = Counter(t for o in models if o != m for t, _ in raw[o].get(c, []))
            for t, _ in raw[m].get(c, []):
                if (m, c, t) in drop:
                    continue
                n += 1
                k += (others.get(t, 0) == 0)
        out[m] = k / n if n else float("nan")
    return out

drop = frozenset((r["model"], r["category"], r["answer"])
                 for r in novel if r["label"] in ("wrong", "degenerate"))

base_s, base_n = surprisal(), novel_rate()
recl_s, recl_n = surprisal(drop), novel_rate(drop)
order = sorted(models, key=lambda m: -base_s[m])
rank = {m: i + 1 for i, m in enumerate(order)}
rrank = {m: i + 1 for i, m in enumerate(sorted(models, key=lambda m: -recl_s[m]))}

# ---- report ----
lab_counts = Counter(r["label"] for r in novel)
tot = len(novel)
good = lab_counts["valid"] + lab_counts["contested"]
print(f"\n=== NOVEL-ANSWER AUDIT ===  {tot} novel answers across {len(models)} models")
for k in ("valid", "contested", "wrong", "degenerate"):
    print(f"  {k:11} {lab_counts[k]:4}  ({lab_counts[k]/tot:.1%})")
print(f"  valid+contested: {good}/{tot} = {good/tot:.1%}")

print("\n=== per-model validity (models with any novel answers) ===")
bym = {}
for r in novel:
    bym.setdefault(r["model"], Counter())[r["label"]] += 1
for m in sorted(bym, key=lambda m: -sum(bym[m].values())):
    c = bym[m]
    n = sum(c.values())
    bad = c["wrong"] + c["degenerate"]
    print(f"  {m:24} n={n:2}  valid+cont={ (c['valid']+c['contested'])/n:.0%}"
          f"  wrong={c['wrong']} degen={c['degenerate']}" + ("  <-- bad>0" if bad else ""))

print("\n=== reclassification: wrong+degenerate -> failed cells (top-8 divergent) ===")
print(f"  dropped {len(drop)} cells: " + ", ".join(f"{m}/{c}/{a}" for m, c, a in sorted(drop)))
print(f"  {'model':24} {'surp':>6} {'->':>2} {'surp′':>6} {'Δ':>6}  {'novel':>6} {'->':>7}  rank")
for m in order[:8]:
    dr = recl_s[m] - base_s[m]
    rk = f"{rank[m]}" if rank[m] == rrank[m] else f"{rank[m]}->{rrank[m]}"
    print(f"  {m:24} {base_s[m]:6.2f} {'':>2} {recl_s[m]:6.2f} {dr:+6.2f}  "
          f"{base_n[m]:6.1%} {'->':>3} {recl_n[m]:5.1%}  rank {rk}")

# extraction summary
leak_novel = [e for e in ext if e["is_novel"]]
print(f"\n=== extraction audit === {len(ext)} passed cells >1 word; "
      f"{len(leak_novel)} of them novel: "
      + ", ".join(f"{e['model']}/{e['category']}/{e['extracted']}" for e in leak_novel))
print("wrote probes/novel_audit.csv, probes/extraction_audit.csv")
