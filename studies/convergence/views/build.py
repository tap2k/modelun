"""
Build the convergence study's review site: views/data.js (+ a copy of the renderer).

Bakes transcripts + scenes (for the reused transcript/compare views) AND analysis.json
(the convergence results — per-prompt similarity, per-model cross-family drift) into one
blob the page draws. Matplotlib is a repo dep, but we keep the site buildless and
self-contained: the results view draws its own bars/table from the numbers in JS, so
there is no PNG to host and the page stays a single no-deps open-in-browser file.

    python studies/convergence/analyze.py            # first: transcripts -> analysis.json
    python studies/convergence/views/build.py        # then: analysis.json -> data.js
    open studies/convergence/views/index.html
"""

import json
import shutil
from pathlib import Path

VIEWS = Path(__file__).resolve().parent
STUDY = VIEWS.parent
REPO = STUDY.parent.parent
TRANSCRIPTS = STUDY / "transcripts"


def scene_blob(d):
    return {sid: {"subtitle": sc.get("subtitle", sid),
                  "runs": [[{"u": pn["u"], "reply": pn.get("reply")} for pn in run]
                           for run in sc["runs"]]}
            for sid, sc in d["scenes"].items()}


def main():
    spec = json.loads((STUDY / "spec" / "stimulus.json").read_text())
    scene_list = [{"id": s["id"], "subtitle": s.get("subtitle", s["id"]), "turns": s["turns"]}
                  for s in spec["scenes"]]
    meta = {m["label"]: m for m in json.loads((STUDY / "spec" / "models.json").read_text())["models"]}

    models = {}
    for p in sorted(TRANSCRIPTS.glob("*.json")) if TRANSCRIPTS.exists() else []:
        d = json.loads(p.read_text())
        models[d["model"]] = {"slug": d.get("slug", ""), "meta": meta.get(d["model"], {}),
                              "scenes": scene_blob(d)}

    analysis_path = STUDY / "analysis.json"
    analysis = json.loads(analysis_path.read_text()) if analysis_path.exists() else None

    blob = {
        "system_prompt": spec.get("system_prompt", "") or "(none — models' naked default)",
        "models": models,
        "scenes": scene_list,
        "analysis": analysis,
    }
    VIEWS.mkdir(exist_ok=True)
    (VIEWS / "data.js").write_text("window.CONV = " + json.dumps(blob, ensure_ascii=False) + ";\n")
    shutil.copy(REPO / "harness" / "viewer" / "core.js", VIEWS / "core.js")
    n_an = len(analysis["per_prompt"]) if analysis else 0
    print(f"wrote {VIEWS / 'data.js'} + core.js  ({len(models)} models, {len(scene_list)} scenes, "
          f"{n_an} analyzed prompts)")
    if not analysis:
        print("  (no analysis.json yet — run analyze.py to populate the Results tab)")
    print(f"open {VIEWS / 'index.html'} in a browser")


if __name__ == "__main__":
    main()
