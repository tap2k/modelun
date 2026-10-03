#!/usr/bin/env bash
# Brand battery across languages, five-model pilot (2026-10-03).
# Name (clamped) at 4 runs and Recommend at 2 runs, each model with the reasoning setting it had in the English
# brand Recommend run: off for GPT-5.5, DeepSeek V3.2 and Llama 4 Maverick; route default for Claude Sonnet 5.5
# and Gemini 3.5 Flash, whose endpoints reject "off".
# run.py writes a model's file once at the end, so parallel jobs get one directory per language:
#   transcripts-brands-lang-pilot/<lang>/<model>.json, transcripts-brands-lang-recommend-pilot/<lang>/<model>.json
# Estimated cost from the English per-cell costs, x1.5 for non-Latin tokenisation: ~$10 Name, ~$55 Recommend.
#
#   cd studies/consensus && python3 build_brands_lang.py && bash run_brands_lang_pilot.sh
set -euo pipefail
cd "$(dirname "$0")"
RUN=../../harness/run.py
OFF="openai/gpt-5.5 deepseek/deepseek-v3.2 meta-llama/llama-4-maverick"
DEFAULT="anthropic/claude-sonnet-5.5 google/gemini-3.5-flash"
LANGS=$(python3 -c "import json; print(' '.join(json.load(open('spec/brands_lang_prompts.json'))['prompts']))")
CATS=$(python3 -c "import json; print(' '.join(json.load(open('spec/brands_lang_prompts.json'))['prompts']['en']))")

jobs() {  # one line per (verb, lang, model): spec, out dir, runs, scenes, reasoning flag, model
  for l in $LANGS; do
    ns=$(for c in $CATS; do printf '%s__%s,' "$c" "$l"; done); ns=${ns%,}
    rs=$(for c in $CATS; do printf '%s__%s__recommend,' "$c" "$l"; done); rs=${rs%,}
    for m in $OFF $DEFAULT; do
      r=""; [[ " $OFF " == *" $m "* ]] && r="--reasoning off"
      echo "spec/stimulus_brands_lang.json transcripts-brands-lang-pilot/$l 4 $ns $m $r"
      echo "spec/stimulus_brands_lang_recommend.json transcripts-brands-lang-recommend-pilot/$l 2 $rs $m $r"
    done
  done
}

jobs | xargs -P "${PARALLEL:-24}" -L 1 bash -c \
  'python3 '"$RUN"' --study . --spec "$0" --out "$1" --runs "$2" --scenes "$3" "${@:5}" "$4" > /dev/null 2>&1 || echo "FAILED: $*"'
echo "done; run.py exits 0 on failed cells, so check the files for errors"
