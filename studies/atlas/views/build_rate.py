#!/usr/bin/env python3
"""labels/*.json + transcripts → views/rate_data.js: screens for the subtract-only rating task.

Lineup screens: one short-phrase criterion, 6–8 spans from different replies.
In-context screens: one reply, one sentence-level criterion, its spans highlighted.
  python build_rate.py [--criteria a,b,c] [--max-screens N] [--seed N]
"""
import argparse, json, random, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
sys.path.insert(0, str(STUDY))
CRIT = json.loads((STUDY / "spec/criteria.json").read_text())
PROMPT_VERSION = CRIT["version"]
CRITERIA = {c["id"]: c for c in CRIT["criteria"]}
LINEUP = {c["id"] for c in CRIT["criteria"] if c["screen"] == "lineup"}
FIRST_PASS = [c["id"] for c in CRIT["criteria"] if c.get("first_pass")]
RESIST_ONLY = {c["id"]: set(c["first_pass_only"]) for c in CRIT["criteria"] if c.get("first_pass_only")}

ap = argparse.ArgumentParser()
ap.add_argument("--criteria", default=",".join(FIRST_PASS))
ap.add_argument("--max-screens", type=int, default=60)
ap.add_argument("--seed", type=int, default=1)
a = ap.parse_args()
crits = a.criteria.split(",")
rng = random.Random(a.seed)

T = {p.stem: json.loads(p.read_text()) for p in (STUDY / "transcripts").glob("*.json")}
PROMPTS = {aid: c["prompt"] for t in T.values() for aid, c in t["cells"].items()}
L = {p.stem: json.loads(p.read_text()) for p in (STUDY / "labels").glob("*.json")}

items = []   # one per (model, anchor, i, criterion) with spans
for m, lab in L.items():
    for s in lab["samples"]:
        reply = T[m]["cells"][s["anchor"]]["samples"][s["i"]]["reply"]
        for c in crits:
            if c in RESIST_ONLY and s["anchor"] not in RESIST_ONLY[c]: continue
            spans = s["spans"].get(c) or []
            if spans:
                items.append({"model": m, "anchor": s["anchor"], "i": s["i"], "criterion": c, "reply": reply, "spans": spans})

screens = []
for c in crits:
    cs = [it for it in items if it["criterion"] == c]
    rng.shuffle(cs)
    text, seeds = CRITERIA[c]["text"], CRITERIA[c]["seeds"]
    if c in LINEUP:
        pool = [{"model": it["model"], "anchor": it["anchor"], "i": it["i"], "span": sp["span"], "label": sp.get("label")}
                for it in cs for sp in it["spans"]]
        rng.shuffle(pool)
        for k in range(0, len(pool), 7):
            screens.append({"type": "lineup", "criterion": c, "text": text, "seeds": seeds, "cards": pool[k:k + 7]})
    else:
        for it in cs:
            screens.append({"type": "context", "criterion": c, "text": text, "seeds": seeds,
                            "model": it["model"], "anchor": it["anchor"], "i": it["i"], "reply": it["reply"], "spans": it["spans"]})

rng.shuffle(screens)
screens = screens[:a.max_screens]
out = {"prompt_version": PROMPT_VERSION, "prompts": PROMPTS, "screens": screens}
(HERE / "rate_data.js").write_text("window.RATE = " + json.dumps(out, ensure_ascii=False) + ";\n")
print(f"→ rate_data.js  {len(screens)} screens from {len(items)} items; spans to rate: {sum(len(s.get('cards', s.get('spans', []))) for s in screens)}")
