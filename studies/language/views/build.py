"""
Build the language study's review site: views/data.js (+ a copy of the renderer).

Bakes every transcript and the scene list into one blob the page draws. No markers,
no judge, no store — this study is generate-and-view, so the blob is just transcripts +
scenes. The site imports the generic renderer from harness/viewer/core.js; this blob is
the data it draws. After running, open views/index.html directly (no server, no deps).

    python studies/language/views/build.py
"""

import json
import shutil
from pathlib import Path

VIEWS = Path(__file__).resolve().parent
STUDY = VIEWS.parent
REPO = STUDY.parent.parent
TRANSCRIPTS = STUDY / "transcripts"


def scene_blob(d):
    """Transcript -> per-scene {subtitle, runs} the site renders."""
    return {sid: {"subtitle": sc.get("subtitle", sid),
                  "runs": [[{"u": pn["u"], "reply": pn.get("reply")} for pn in run]
                           for run in sc["runs"]]}
            for sid, sc in d["scenes"].items()}


def main():
    spec = json.loads((STUDY / "spec" / "stimulus.json").read_text())
    # scene order + user turns come from the frozen spec, not from any one transcript
    scene_list = [{"id": s["id"], "subtitle": s.get("subtitle", s["id"]), "turns": s["turns"]}
                  for s in spec["scenes"]]

    models = {}
    for p in sorted(TRANSCRIPTS.glob("*.json")) if TRANSCRIPTS.exists() else []:
        d = json.loads(p.read_text())
        models[d["model"]] = {"slug": d.get("slug", ""), "scenes": scene_blob(d)}

    blob = {
        "system_prompt": spec.get("system_prompt", ""),
        "models": models,
        "scenes": scene_list,
    }
    VIEWS.mkdir(exist_ok=True)
    (VIEWS / "data.js").write_text("window.LANG = " + json.dumps(blob, ensure_ascii=False) + ";\n")
    # copy the generic renderer next to index.html so the page can load ./core.js
    shutil.copy(REPO / "harness" / "viewer" / "core.js", VIEWS / "core.js")
    print(f"wrote {VIEWS / 'data.js'} + core.js  ({len(models)} models, {len(scene_list)} scenes)")
    print(f"open {VIEWS / 'index.html'} in a browser")


if __name__ == "__main__":
    main()
