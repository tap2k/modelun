#!/usr/bin/env python3
"""labels + transcripts → views/rate_data.js: screens for the subtract-only rating task.
Lineup screens for criteria with screen=lineup (6–8 spans from different replies);
in-context screens otherwise (one reply, one criterion, its spans highlighted).
  python build_rate.py [--criteria a,b,c] [--max-screens N] [--seed N] [--labels DIR]"""
import argparse, json, random, sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import atlas

ap = argparse.ArgumentParser()
ap.add_argument("--criteria", default=None, help="comma-separated ids (default: criteria marked first_pass)")
ap.add_argument("--max-screens", type=int, default=60)
ap.add_argument("--seed", type=int, default=1)
ap.add_argument("--labels", default=str(atlas.LABELS))
a = ap.parse_args()
CRITERIA, VERSION = atlas.criteria()
crits = a.criteria.split(",") if a.criteria else [c for c, x in CRITERIA.items() if x.get("first_pass")]
rng = random.Random(a.seed)
T = atlas.transcripts()
L = {p.stem: json.loads(p.read_text()) for p in Path(a.labels).glob("*.json")}
PROMPTS = atlas.prompts()

by_crit = defaultdict(list)
for m, lab in L.items():
    for s in lab["samples"]:
        reply = T[m]["cells"][s["anchor"]]["samples"][s["i"]]["reply"]
        for c in crits:
            subset = CRITERIA[c].get("first_pass_only")          # restrict a criterion to some of its anchors
            if subset and s["anchor"] not in subset:
                continue
            if s["spans"].get(c):
                by_crit[c].append({"model": m, "anchor": s["anchor"], "i": s["i"], "reply": reply, "spans": s["spans"][c]})

screens = []
for c, items in by_crit.items():
    rng.shuffle(items)
    base = {"criterion": c, "text": CRITERIA[c]["text"], "seeds": CRITERIA[c]["seeds"]}
    if CRITERIA[c]["screen"] == "lineup":
        pool = [{"model": it["model"], "anchor": it["anchor"], "i": it["i"], **sp} for it in items for sp in it["spans"]]
        rng.shuffle(pool)
        screens += [{**base, "type": "lineup", "cards": pool[k:k + 7]} for k in range(0, len(pool), 7)]
    else:
        screens += [{**base, "type": "context", **{k: it[k] for k in ("model", "anchor", "i", "reply", "spans")}} for it in items]
rng.shuffle(screens)
screens = screens[:a.max_screens]
(atlas.HERE / "views/rate_data.js").write_text("window.RATE = " + json.dumps({"criteria_version": VERSION, "prompts": PROMPTS, "screens": screens}, ensure_ascii=False) + ";\n")
print(f"→ rate_data.js  {len(screens)} screens; spans to rate: {sum(len(s.get('cards', s.get('spans', []))) for s in screens)}")
