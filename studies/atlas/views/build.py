#!/usr/bin/env python3
"""transcripts/*.json + spec → views/data.js. Open views/index.html afterwards."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
spec = json.loads((STUDY / "spec/stimulus.json").read_text())
panel = json.loads((STUDY / "spec/models.json").read_text())["models"]
order = [m["label"] for m in panel]

models = {}
for f in sorted((STUDY / "transcripts").glob("*.json")):
    d = json.loads(f.read_text())
    cells = {}
    for aid, c in d["cells"].items():
        samples = []
        for s in c["samples"]:
            u = s.get("usage") or {}
            ct = u.get("completion_tokens", 0)
            rt = (u.get("completion_tokens_details") or {}).get("reasoning_tokens") or 0
            samples.append({
                "reply": s.get("reply"), "error": s.get("error"),
                "finish": s.get("finish_reason"), "date": s.get("run_date"),
                "words": len((s.get("reply") or "").split()),
                "in": u.get("prompt_tokens", 0), "out": ct - rt, "reason": rt,
                "cost": u.get("cost", 0)})
        cells[aid] = {"template": c["template"], "prompt": c["prompt"], "samples": samples}
    models[d["model"]] = {"slug": d["slug"], "version": d.get("spec_version"), "cells": cells}

labels = [m for m in order if m in models] + [m for m in models if m not in order]
anchors = [{"id": a["id"], "verb": t["id"], "text": a["text"], "template": t["template"]}
           for t in spec["templates"] for a in t["anchors"] + t.get("rotation", [])]
data = {"spec_version": spec["spec_version"], "anchors": anchors, "models": labels, "data": models}
(HERE / "data.js").write_text("window.ATLAS = " + json.dumps(data, ensure_ascii=False) + ";\n")
n = sum(len(c["samples"]) for m in models.values() for c in m["cells"].values())
print(f"→ {HERE/'data.js'}  {len(labels)} models, {len(anchors)} anchors, {n} samples")
