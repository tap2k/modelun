"""probe_persona.py — Experiment B: does an anti-mode persona system prompt let the model
FIELD recover the human spread, or just move to a different collapsed mode? Steelman prompt
(the one most likely to work). Same 20 human-overlap categories, our exact wordings (only the
system prompt differs from baseline), all 39 models, 4 runs.

    ../../.venv/bin/python probe_persona.py   -> probes/persona.json
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from probe_lib import run_battery

HERE = Path(__file__).resolve().parent
SYSTEM = ("You are one of many different people being asked this question. Answer with a "
          "real, natural response a person might give off the top of their head -- and don't "
          "just reach for the single most obvious answer.")
OVERLAP = {"tree","tool","flower","vegetable","herb","fish","fruit","color","fabric","metal",
           "instrument","city","animal","insect","bird","sport","dance","occupation","country","gemstone"}
stim = json.loads((HERE / "spec/stimulus.json").read_text())
PROMPTS = {s["id"]: s["turns"][0] for s in stim["scenes"] if s["id"] in OVERLAP}
assert len(PROMPTS) == 20, len(PROMPTS)
models = json.loads((HERE / "spec/models.json").read_text())["models"]
print(f"Experiment B: {len(PROMPTS)} cats x {len(models)} models x 4 = {len(PROMPTS)*len(models)*4} calls", flush=True)
run_battery(PROMPTS, models, 4, HERE / "probes/persona.json", system=SYSTEM,
            meta={"run_date": "2026-07-07"})
