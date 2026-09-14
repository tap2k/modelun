"""probe_sdk_thinking.py — the one-word census through the Claude Agent SDK on the Max plan, reasoning on.

Same battery and conditions as `probe_fable51.py` (no system prompt, max_tokens 1024, n=8 by default)
but through the second backend (`harness/backends/agent_sdk.py`): default sampling (temperature is
refused), an effort level in place of it, the thinking trace stored as a summary. Output labels are
the OpenRouter labels from spec/models.json so `recheck.py --score <file>` compares today's via-Max
answers with the model's via-OpenRouter transcript against the frozen wave-1 field.

    ../../.venv/bin/python probe_sdk_thinking.py claude-sonnet-5 [--effort low] [--runs 8]
        -> probes/<label>_sdk_thinking.json           (low effort)
        -> probes/<label>_sdk_thinking_<effort>.json  (other efforts)
"""
import sys
import json
import argparse
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from probe_lib import run_battery

STIM = json.loads((HERE / "spec/stimulus.json").read_text())
PROMPTS = {s["id"]: s["turns"][0] for s in STIM["scenes"]}
LABELS = {"claude-sonnet-5": "claude-sonnet-5", "claude-opus-5": "claude-opus-5", "claude-fable-5-1": "claude-fable-5.1"}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("model", choices=sorted(LABELS))
    ap.add_argument("--effort", default="low")
    ap.add_argument("--runs", type=int, default=8)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    label = LABELS[a.model]
    out = HERE / "probes" / (f"{label}_sdk_thinking.json" if a.effort == "low" else f"{label}_sdk_thinking_{a.effort}.json")
    if out.exists():
        sys.exit(f"{out} exists; not overwriting")
    run_battery(PROMPTS, [{"label": label, "slug": f"sdk:{a.model}"}], a.runs, out, workers=a.workers, effort=a.effort,
                meta={"run_date": date.today().isoformat(),
                      "note": "census via the Claude Agent SDK on the Max plan, reasoning on; trace is a summary; default sampling"})
