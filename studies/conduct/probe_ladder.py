"""probe_ladder.py — the six conduct scenes on OLMo 3.1 32B's SFT, DPO and RL stages, local (2026-10-18).

The frozen stimulus (spec/stimulus.json, clamp as the system message) through each stage's chat template,
2 runs at temperature 1, max 1200 tokens, by harness/local.py run_dialog. The base stage has no chat turn
and is not run. Transcripts in probes/ladder_32b/ (never data/benchmark/), judged and adjudicated there:

    ../../.venv/bin/python probe_ladder.py
    D=probes/ladder_32b
    for j in qwen/qwen3.7-plus google/gemma-4-31b-it deepseek/deepseek-v4.1-flash; do
      ../../.venv/bin/python ../../harness/judge.py --study . --judge $j --subjects $D/olmo31-32b-*.json --out $D/labels
    done
    ../../.venv/bin/python ../../harness/adjudicate.py --study . --labels-dir $D/labels --bench $D --out $D/markers.json

DeepSeek V4.1 Flash timed out (180 s) on the DPO transcript three times; those cells rest on the other two judges.
"""
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "harness"))
import local

spec = json.loads((HERE / "spec" / "stimulus.json").read_text())
for name in ("sft", "dpo", "rl"):
    st = local.stage("olmo31-32b", name)
    local.run_dialog(spec, st, 2, HERE / "probes" / "ladder_32b" / f"{st['label']}.json")
    local.free()
