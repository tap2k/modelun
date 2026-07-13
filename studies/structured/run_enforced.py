"""run_enforced.py — the enforced structured-output column.

Same JSON-clause prompt as the `json` column of run_formats.py, but with OpenRouter
`response_format` json_schema enforcement (strict). This isolates decoder-level
enforcement from the mere request: compare three columns on the same models ---
plain (census transcripts) / requested-json (format_register.json) / enforced (here).

Scope: only a subset of models that support strict json_schema. Models that don't
support it degrade to low compliance / nulls and are flagged by analyze.py's
compliance machinery exactly like any other non-compliant model.

    ../../.venv/bin/python run_enforced.py   # -> probes/enforced_json.json
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
CLAUSE = 'Reply with JSON only, in the form {"word": "<your answer>"}.'
PROMPTS = {c: f"{noun} {CLAUSE}" for c, noun in ALL_CATS.items()}

# Strict object schema: exactly the shape the clause requests, now enforced at the decoder.
SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "word",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {"word": {"type": "string"}},
            "required": ["word"],
            "additionalProperties": False,
        },
    },
}

# Full 44-model roster: an empirical support probe (2026-07-13) confirmed every provider on
# the panel accepts response_format json_schema through OpenRouter and returns valid enforced
# JSON, so the enforced column spans the same panel as the plain and requested-json columns.
# NOTE on mechanism: OpenRouter delivers response_format natively for some providers and
# gateway-mediated for others, so this column measures the response_format pathway *as served*
# (what a real deployment gets), not uniformly decoder-level token masking. See paper limitations.
MODELS = json.loads((CONSENSUS / "spec/models.json").read_text())["models"]

if __name__ == "__main__":
    out = HERE / "probes" / "enforced_json.json"
    run_battery(PROMPTS, MODELS, 4, out,
                extra={"response_format": SCHEMA},
                meta={"run_date": "2026-07-13",
                      "note": "enforced structured-output column: json clause + "
                              "response_format json_schema (strict). Compare vs plain "
                              "(census) and requested-json (format_register.json)."})
    print("-> probes/enforced_json.json")
