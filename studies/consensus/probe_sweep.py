"""probe_sweep.py — prompt-strength sweep for paper 2's headline figure.

Traces the model field's distribution as the system prompt pushes from neutral -> hard
anti-mode. Combined with L0 (baseline, no system prompt) and L3 (the steelman persona,
probes/persona.json) already collected, this gives a 5-rung ladder:

  L0  (none)        -- baseline                                  [have: main study]
  L1  natural       -- mild humanization, no diversity push      [this script]
  L2  random person -- persona, first thing to mind, no anti-mode[this script]
  L3  steelman      -- persona + "don't reach for the obvious"   [have: persona.json]
  L4  extreme       -- explicit "give an unusual answer"         [this script]

Prediction: JS(field, human) is U-shaped (undershoot -> best -> overshoot); effective-N
rises monotonically. No rung reaches the human distribution.

Same 20 human-overlap categories, our wordings, all 39 models, 4 runs. ~9360 calls.

    ../../.venv/bin/python probe_sweep.py   -> probes/sweep_L1.json, _L2.json, _L4.json
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from probe_lib import run_battery

HERE = Path(__file__).resolve().parent
LEVELS = {
    "L1": "Answer naturally, the way a real person would.",
    "L2": ("You are a random member of the public being asked this question. "
           "Give the first answer that comes to mind."),
    "L4": ("Give an unusual, non-obvious answer to this question -- something most people "
           "would not say."),
}
OVERLAP = {"tree","tool","flower","vegetable","herb","fish","fruit","color","fabric","metal",
           "instrument","city","animal","insect","bird","sport","dance","occupation","country","gemstone"}
stim = json.loads((HERE / "spec/stimulus.json").read_text())
PROMPTS = {s["id"]: s["turns"][0] for s in stim["scenes"] if s["id"] in OVERLAP}
assert len(PROMPTS) == 20, len(PROMPTS)
models = json.loads((HERE / "spec/models.json").read_text())["models"]

for lvl, sysprompt in LEVELS.items():
    print(f"=== {lvl}: {sysprompt[:50]}... ({len(PROMPTS)*len(models)*4} calls) ===", flush=True)
    run_battery(PROMPTS, models, 4, HERE / f"probes/sweep_{lvl}.json", system=sysprompt,
                meta={"level": lvl, "run_date": "2026-07-07"})
print("sweep complete", flush=True)
