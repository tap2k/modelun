"""run_formats.py — the census questions, asked for in structured formats.

JSON runs the full 31-category battery; XML and brackets run a 6-category control subset
(serialization vs mere structure). Roster, stimulus, and conditions come from ../consensus.

    ../../.venv/bin/python run_formats.py     # -> probes/format_register.json
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONSENSUS = HERE.parent / "consensus"
sys.path.insert(0, str(CONSENSUS))
from probe_lib import run_battery

STIM = json.loads((CONSENSUS / "spec/stimulus.json").read_text())
ALL_CATS = {s["id"]: s["turns"][0].split(" Reply with")[0].strip() for s in STIM["scenes"]}
SUB_CATS = {c: ALL_CATS[c] for c in
            ["color", "fruit", "condiment", "cheese", "tree", "any_word"]}
FORMATS = {
    "json":     ('Reply with JSON only, in the form {{"word": "<your answer>"}}.', "all"),
    "xml":      ("Reply with XML only, in the form <word>your answer</word>.", "sub"),
    "brackets": ("Reply with your answer inside square brackets only, like [answer].", "sub"),
}

models = json.loads((CONSENSUS / "spec/models.json").read_text())["models"]

if __name__ == "__main__":
    out = {}
    for fmt, (clause, scope) in FORMATS.items():
        cats = ALL_CATS if scope == "all" else SUB_CATS
        prompts = {c: f"{noun} {clause.format()}" for c, noun in cats.items()}
        path = HERE / "probes" / f"_format_{fmt}.json"
        run_battery(prompts, models, 4, path,
                    meta={"run_date": "2026-07-10", "note": f"format register probe: {fmt}"})
        out[fmt] = json.loads(path.read_text())
        path.unlink()
    (HERE / "probes" / "format_register.json").write_text(
        json.dumps({"formats": {k: v["prompts"] for k, v in out.items()},
                    "runs": 4, "run_date": "2026-07-10",
                    "replies": {k: v["replies"] for k, v in out.items()}},
                   indent=1, ensure_ascii=False) + "\n")
    print("-> probes/format_register.json")
