"""add_control_formats.py — merge additional format columns into probes/format_register.json.

yaml + csv discriminate "serialization register generally" from "fitted to JSON/XML
specifically": all four are data formats, but only json/xml are function-calling registers.
Runs the 6-category control subset and merges (does not touch existing columns).
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
SUB = ["color", "fruit", "condiment", "cheese", "tree", "any_word"]
NEW_FORMATS = {
    "yaml": "Reply with YAML only, in the form `word: <your answer>`.",
    "csv":  "Reply with CSV only: a header row `word`, then one data row with your answer.",
}

models = json.loads((CONSENSUS / "spec/models.json").read_text())["models"]
PATH = HERE / "probes" / "format_register.json"

if __name__ == "__main__":
    reg = json.loads(PATH.read_text())
    for fmt, clause in NEW_FORMATS.items():
        prompts = {c: f"{ALL_CATS[c]} {clause}" for c in SUB}
        tmp = HERE / "probes" / f"_format_{fmt}.json"
        run_battery(prompts, models, 4, tmp,
                    meta={"run_date": "2026-07-10", "note": f"control format: {fmt}"})
        d = json.loads(tmp.read_text())
        reg["formats"][fmt] = d["prompts"]
        reg["replies"][fmt] = d["replies"]
        tmp.unlink()
    PATH.write_text(json.dumps(reg, indent=1, ensure_ascii=False) + "\n")
    print("-> merged yaml + csv into format_register.json")
