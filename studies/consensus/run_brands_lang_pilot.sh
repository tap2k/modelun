#!/usr/bin/env bash
# Brand Name battery across languages, five-model pilot (2026-10-03).
# The clamped Name question only, 8 runs as in the English brand battery, each model with the reasoning setting it
# had there: off for GPT-5.5, DeepSeek V3.2 and Llama 4 Maverick; route default for Claude Sonnet 5.5 and
# Gemini 3.5 Flash, whose endpoints reject "off".
# xargs -L 1 joins a line ending in a blank to the next one, so every job line ends in the model slug.
# run.py writes a model's file once at the end, so parallel jobs get one directory per language:
#   transcripts-brands-lang-pilot/<lang>/<model>.json
# Estimated cost from the English per-cell costs, x1.5 for non-Latin tokenisation: ~$20.
#
#   cd studies/consensus && python3 build_brands_lang.py && bash run_brands_lang_pilot.sh
set -euo pipefail
cd "$(dirname "$0")"
RUN=../../harness/run.py
OFF="openai/gpt-5.5 deepseek/deepseek-v3.2 meta-llama/llama-4-maverick"
DEFAULT="anthropic/claude-sonnet-5.5 google/gemini-3.5-flash"
LANGS=$(python3 -c "import json; print(' '.join(json.load(open('spec/brands_lang_prompts.json'))['prompts']))")
CATS=$(python3 -c "import json; print(' '.join(json.load(open('spec/brands_lang_prompts.json'))['prompts']['en']))")

jobs() {  # one line per (lang, model): out dir, scenes, reasoning (off | default), model
  for l in $LANGS; do
    ns=$(for c in $CATS; do printf '%s__%s,' "$c" "$l"; done); ns=${ns%,}
    for m in $OFF $DEFAULT; do
      r=default; [[ " $OFF " == *" $m "* ]] && r=off
      echo "transcripts-brands-lang-pilot/$l $ns $r $m"
    done
  done
}

jobs | xargs -P "${PARALLEL:-24}" -L 1 bash -c \
  'r=(); [ "$2" = off ] && r=(--reasoning off)
   python3 '"$RUN"' --study . --spec spec/stimulus_brands_lang.json --out "$0" --runs 8 --scenes "$1" "${r[@]}" "$3" > /dev/null 2>&1 || echo "FAILED: $0 $3"'
echo "done; run.py exits 0 on failed cells, so check the files for errors"
