"""probe_exactword.py — Experiment A: re-run the categories whose VO wording differs from
our prompt, using VO's EXACT category noun, so the human-vs-model comparison is apples-to-
apples. All 39 models, 4 runs. See probe_lib.run_battery.

    ../../.venv/bin/python probe_exactword.py   -> probes/exactword.json
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from probe_lib import run_battery

HERE = Path(__file__).resolve().parent
PROMPTS = {
    "animal":     "Name a four-footed animal. Reply with one word only.",
    "tool":       "Name a carpenter's tool. Reply with one word only.",
    "gemstone":   "Name a precious stone. Reply with one word only.",
    "occupation": "Name an occupation or profession. Reply with one word only.",
    "dance":      "Name a type of dance. Reply with one word only.",
    "fabric":     "Name a type of fabric. Reply with one word only.",
}
models = json.loads((HERE / "spec/models.json").read_text())["models"]
print(f"Experiment A: {len(PROMPTS)} cats x {len(models)} models x 4 = {len(PROMPTS)*len(models)*4} calls", flush=True)
run_battery(PROMPTS, models, 4, HERE / "probes/exactword.json",
            meta={"run_date": "2026-07-07", "note": "VO exact-wording rerun"})
