"""run_resnapshot.py — a fresh chat snapshot of the GPT-5.6 tiers, for citing drift.

The structured study's within-run re-sample showed gpt-5.6-terra drifted off an earlier
census default (condiment mustard -> ketchup) between runs — plausibly because the 5.6
release was still being tuned in production. This re-collects the full 31-category chat
battery for sol/terra/luna so the census edits can quote a second snapshot. Same conditions
as the census; n=8 for a firmer current estimate.

    ../../.venv/bin/python run_resnapshot.py   # -> probes/resnapshot_56.json
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from probe_lib import run_battery

STIM = json.loads((HERE / "spec/stimulus.json").read_text())
PROMPTS = {s["id"]: s["turns"][0] for s in STIM["scenes"]}
ALLM = json.loads((HERE / "spec/models.json").read_text())["models"]
WANT = {"gpt-5.6-sol", "gpt-5.6-terra", "gpt-5.6-luna"}
MODELS = [m for m in ALLM if m["label"] in WANT]

if __name__ == "__main__":
    (HERE / "probes").mkdir(exist_ok=True)
    run_battery(PROMPTS, MODELS, 8, HERE / "probes/resnapshot_56.json",
                meta={"run_date": "2026-07-15",
                      "note": "fresh chat snapshot of the GPT-5.6 tiers (n=8) for census drift citation"})
