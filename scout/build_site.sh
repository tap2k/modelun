#!/usr/bin/env bash
# Rebuild the browsable Atlas site end-to-end from the repo's source of truth.
#
#   data/benchmark/*.md  +  data/groups.json  +  docs/*.md
#        │  parse (Python)
#        ▼
#   site/src/data/atlas.json   (generated, gitignored)
#        │  build (Astro)
#        ▼
#   site/dist/                 (static HTML, gitignored)
#
# Usage:
#   scout/build_site.sh           # regenerate data + build static site -> site/dist/
#   scout/build_site.sh --dev     # regenerate data, then run the live dev server
#
# Prereqs (one-time): pip install -r requirements.txt  &&  (cd site && npm install)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="$ROOT/.venv/bin/python"
[ -x "$PY" ] || PY="python3"

echo "1/2 · parsing data/ -> site/src/data/atlas.json"
"$PY" "$ROOT/scout/build_site_data.py"

cd "$ROOT/site"
if [ "${1:-}" = "--dev" ]; then
  echo "2/2 · starting dev server (ctrl-c to stop)"
  exec npm run dev
else
  echo "2/2 · building static site -> site/dist/"
  npm run build
  echo "done · open site/dist/index.html or serve site/dist/"
fi
