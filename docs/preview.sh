#!/usr/bin/env bash
# Preview the combined review site locally — builds and assembles the same tree
# .github/workflows/pages.yml deploys, then serves it.
#
#   docs/preview.sh [port]      # default port 8000
set -euo pipefail
cd "$(dirname "$0")/.."
PORT="${1:-8000}"
SITE="$(mktemp -d)/site"

# use the repo venv (matplotlib/numpy for the conduct plots) regardless of the caller's shell
PY=python3; [ -x .venv/bin/python ] && PY=.venv/bin/python

"$PY" studies/conduct/views/plot.py
"$PY" studies/conduct/views/build.py
"$PY" studies/language/views/build.py
"$PY" studies/consensus/views/build.py
"$PY" studies/convergence/views/build.py
"$PY" studies/structured/views/build.py

mkdir -p "$SITE"
cp docs/site-index.html "$SITE/index.html"
cp -r studies/conduct/views     "$SITE/conduct"
cp -r studies/language/views    "$SITE/language"
cp -r studies/consensus/views   "$SITE/consensus"
cp -r studies/convergence/views "$SITE/convergence"
cp -r studies/structured/views  "$SITE/structured"

echo
echo "serving http://localhost:$PORT  (ctrl-c to stop)"
python3 -m http.server -d "$SITE" "$PORT"
