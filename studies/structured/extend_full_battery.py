"""extend_full_battery.py — take xml/brackets/yaml/csv from the 6-category control subset
to the full 31-category battery, merging into probes/format_register.json.

Runs only the categories each format doesn't already have; existing columns untouched.
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
CLAUSES = {
    "xml":      "Reply with XML only, in the form <word>your answer</word>.",
    "brackets": "Reply with your answer inside square brackets only, like [answer].",
    "yaml":     "Reply with YAML only, in the form `word: <your answer>`.",
    "csv":      "Reply with CSV only: a header row `word`, then one data row with your answer.",
}

models = json.loads((CONSENSUS / "spec/models.json").read_text())["models"]
PATH = HERE / "probes" / "format_register.json"

if __name__ == "__main__":
    reg = json.loads(PATH.read_text())
    for fmt, clause in CLAUSES.items():
        have = set(reg["replies"][fmt][models[0]["label"]].keys())
        todo = {c: p for c, p in ALL_CATS.items() if c not in have}
        if not todo:
            print(f"{fmt}: already full")
            continue
        prompts = {c: f"{noun} {clause}" for c, noun in todo.items()}
        tmp = HERE / "probes" / f"_extend_{fmt}.json"
        run_battery(prompts, models, 4, tmp,
                    meta={"run_date": "2026-07-10", "note": f"full-battery extension: {fmt}"})
        d = json.loads(tmp.read_text())
        for lab, cats in d["replies"].items():
            reg["replies"][fmt][lab].update(cats)
        reg["formats"][fmt].update(d["prompts"])
        tmp.unlink()
        print(f"{fmt}: +{len(todo)} categories")
    reg["note"] = reg.get("note", "") + " | control formats extended to full 31-cat battery 2026-07-10 evening"
    PATH.write_text(json.dumps(reg, indent=1, ensure_ascii=False) + "\n")
    print("-> probes/format_register.json (all formats full battery)")
