"""
Build the convergence review site: views/data.js — just the answers.

Convergence tried to measure open-ended similarity with embeddings and hit confound after
confound (see OBSERVATIONS.md); its scored numbers were walked back. So this site shows only
the RAW ANSWERS — every model's reply to each open-ended prompt, read side by side. No scores,
no rankings. The reader judges convergence by eye. (The confound journey lives in the repo;
the measured successor is studies/consensus/.)

    python studies/convergence/views/build.py
    open studies/convergence/views/index.html
"""

import json
from pathlib import Path

VIEWS = Path(__file__).resolve().parent
STUDY = VIEWS.parent
TRANSCRIPTS = STUDY / "transcripts"


def main():
    spec = json.loads((STUDY / "spec" / "stimulus.json").read_text())
    scenes = [{"id": s["id"], "prompt": s["turns"][0]} for s in spec["scenes"]]

    models = {}
    for p in sorted(TRANSCRIPTS.glob("*.json")):
        d = json.loads(p.read_text())
        by_scene = {}
        for sid, sc in d["scenes"].items():
            # all runs' replies for this prompt (skip failed cells)
            replies = [run[0].get("reply") for run in sc["runs"] if run and run[0].get("reply")]
            if replies:
                by_scene[sid] = replies
        if by_scene:
            models[d["model"]] = by_scene

    blob = {"scenes": scenes, "models": models}
    (VIEWS / "data.js").write_text("window.CONV = " + json.dumps(blob, ensure_ascii=False) + ";\n")
    print(f"wrote {VIEWS / 'data.js'}  ({len(models)} models, {len(scenes)} prompts)")


if __name__ == "__main__":
    main()
