"""run_formats.py — the census questions, asked for in structured formats.

Five format columns (json, xml, brackets, yaml, csv) on the full 31-category battery, 4 runs,
merged into probes/format_register.json per model. Roster, stimulus, and conditions come from
../consensus; the prompt strings are frozen (asserted equal to the ones already in the file).

    ../../.venv/bin/python run_formats.py                 # every roster model not yet in the file
    ../../.venv/bin/python run_formats.py claude-opus-5   # named labels (re-collects them)
"""
import json
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONSENSUS = HERE.parent / "consensus"
sys.path.insert(0, str(CONSENSUS))
from probe_lib import run_battery

OUT = HERE / "probes" / "format_register.json"
STIM = json.loads((CONSENSUS / "spec/stimulus.json").read_text())
NOUNS = {s["id"]: s["turns"][0].split(" Reply with")[0].strip() for s in STIM["scenes"]}
FORMATS = {
    "json":     'Reply with JSON only, in the form {"word": "<your answer>"}.',
    "xml":      "Reply with XML only, in the form <word>your answer</word>.",
    "brackets": "Reply with your answer inside square brackets only, like [answer].",
    "yaml":     "Reply with YAML only, in the form `word: <your answer>`.",
    "csv":      "Reply with CSV only: a header row `word`, then one data row with your answer.",
}
PROMPTS = {f: {c: f"{n} {clause}" for c, n in NOUNS.items()} for f, clause in FORMATS.items()}

roster = json.loads((CONSENSUS / "spec/models.json").read_text())["models"]

if __name__ == "__main__":
    reg = json.loads(OUT.read_text())
    for f in FORMATS:
        assert reg["formats"][f] == PROMPTS[f], f"{f} prompt text drifted from the frozen file"
    want = set(sys.argv[1:]) or {m["label"] for m in roster} - set(reg["replies"]["json"])
    models = [m for m in roster if m["label"] in want]
    print(f"collecting {len(models)} models x {len(FORMATS)} formats x {len(NOUNS)} cats x 4 runs", flush=True)
    today = date.today().isoformat()
    for f in FORMATS:
        # probe_lib applies `extra` to a whole call, so pinned models (spec/models.json "provider") run separately
        for pin in sorted({m.get("provider") for m in models}, key=str):
            group = [m for m in models if m.get("provider") == pin]
            extra = {"provider": {"order": [pin], "allow_fallbacks": False}} if pin else None
            tmp = HERE / "probes" / f"_format_{f}.json"
            rep = run_battery(PROMPTS[f], group, 4, tmp, extra=extra)
            tmp.unlink()
            reg["replies"][f].update(rep)
    reg.setdefault("run_dates", {}).update({m["label"]: today for m in models})
    OUT.write_text(json.dumps(reg, indent=1, ensure_ascii=False) + "\n")
    print(f"-> {OUT}  ({len(reg['replies']['json'])} models)", flush=True)
