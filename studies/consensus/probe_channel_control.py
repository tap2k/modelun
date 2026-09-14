"""probe_channel_control.py — what moved the census through the Agent SDK: the channel or the reasoning?

The via-Max rows (probes/<label>_sdk_thinking*.json, 2026-09-14) read more divergent than the same
models via OpenRouter, and spent zero thinking tokens doing it. Two OpenRouter arms, same day, n=8,
census conditions otherwise:
  residual  — no thinking, with a system prompt reproducing the three lines the CLI injects
              (account email, date, Agent SDK framing; harness/backends/context_probe_2026-09-14.json)
  thinking  — OpenRouter's reasoning switch at low, no system prompt
Score each with `recheck.py --score probes/channel_control_<arm>.json` against the model's transcript.

    ../../.venv/bin/python probe_channel_control.py residual|thinking
"""
import sys
import json
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from probe_lib import run_battery

STIM = json.loads((HERE / "spec/stimulus.json").read_text())
PROMPTS = {s["id"]: s["turns"][0] for s in STIM["scenes"]}
ROSTER = json.loads((HERE / "spec/models.json").read_text())["models"]
MODELS = [m for m in ROSTER if m["label"] in {"claude-sonnet-5", "claude-opus-5", "claude-fable-5.1"}]
RESIDUAL = ("You are a Claude agent, built on Anthropic's Claude Agent SDK.\n\n"
            "# userEmail\nThe user's email address is t@maussindustries.com. Use it only to identify the user, such as "
            "for authorship, attribution, or filtering their own work. Never send it to an unrelated service, such as in "
            "a request header, URL, or payload, unless the user explicitly asks.\n# currentDate\nToday's date is "
            f"{date.today().isoformat()}.\n\nIMPORTANT: this context may or may not be relevant to your tasks. You should "
            "not respond to this context unless it is highly relevant to your task.")

if __name__ == "__main__":
    arm = sys.argv[1]
    out = HERE / "probes" / f"channel_control_{arm}.json"
    assert not out.exists(), out
    kw = {"system": RESIDUAL} if arm == "residual" else {"extra": {"reasoning": {"effort": "low"}}}
    run_battery(PROMPTS, MODELS, 8, out, meta={"run_date": date.today().isoformat(), "arm": arm,
                "note": "OpenRouter control for the via-Max census rows: residual = the CLI's injected context as a "
                        "system prompt, no thinking; thinking = reasoning low, no system prompt"}, **kw)
