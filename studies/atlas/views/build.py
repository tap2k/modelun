#!/usr/bin/env python3
"""transcripts/*.json + spec → views/data.js for the transcript viewer (views/index.html)."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import atlas

T = atlas.transcripts()
out = {}
for m, d in T.items():
    cells = {}
    for aid, c in d["cells"].items():
        ss = []
        for s in c["samples"]:
            vis, rt, cost = atlas.usage_split(s.get("usage"))
            ss.append({"reply": s.get("reply"), "error": s.get("error"), "finish": s.get("finish_reason"),
                       "words": len((s.get("reply") or "").split()), "out": vis, "reason": rt, "cost": cost})
        cells[aid] = {"template": c["template"], "prompt": c["prompt"], "samples": ss}
    out[m] = {"slug": d["slug"], "cells": cells}
sp = atlas.spec()
data = {"spec_version": sp["spec_version"], "anchors": [{"id": a["id"], "verb": t["id"], "text": a["text"]} for t, a, _ in atlas.iter_anchors(sp)],
        "models": list(T), "short": {m: atlas.short(m) for m in T}, "n": sp["sampling"]["n_per_cell"], "data": out}
(atlas.HERE / "views/data.js").write_text("window.ATLAS = " + json.dumps(data, ensure_ascii=False) + ";\n")
print(f"→ views/data.js  {len(T)} models, {len(data['anchors'])} anchors, {sum(len(c['samples']) for d in out.values() for c in d['cells'].values())} samples")
