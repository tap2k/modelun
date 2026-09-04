"""probe_fable51.py — fresh chat snapshot of Fable 5 and Fable 5.1 (n=8), for the 5 -> 5.1 drop.

Wave 2 (2026-09-03) put claude-fable-5.1 at 1.24 bits against Fable 5's census 1.69 — most of the
way back to the Sonnet-5 floor. Two readings: the 5.1 release moved, or Fable 5's own serving has
drifted since July. This re-collects the full 31-category chat battery for BOTH under the census
conditions (no system prompt, temperature 1.0, max_tokens 1024), n=8, same day, so the two can be
scored leave-one-out against the frozen wave-1 field and compared to each other and to July.

    ../../.venv/bin/python probe_fable51.py   # -> probes/resnapshot_fable.json
"""
import json
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from probe_lib import run_battery

STIM = json.loads((HERE / "spec/stimulus.json").read_text())
PROMPTS = {s["id"]: s["turns"][0] for s in STIM["scenes"]}
ALLM = json.loads((HERE / "spec/models.json").read_text())["models"]
WANT = {"claude-fable-5", "claude-fable-5.1"}
MODELS = [m for m in ALLM if m["label"] in WANT]

if __name__ == "__main__":
    (HERE / "probes").mkdir(exist_ok=True)
    run_battery(PROMPTS, MODELS, 8, HERE / "probes/resnapshot_fable.json",
                meta={"run_date": date.today().isoformat(),
                      "note": "same-day chat snapshot of Fable 5 and Fable 5.1 (n=8): release change vs serving drift"})
