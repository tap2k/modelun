#!/usr/bin/env bash
# Build the arXiv source package: arxiv/ (staged sources) and cross-instrument-arxiv.tar.gz.
# Both are gitignored and regenerable. Run from this directory.
#
#   ./make_arxiv.sh
#
# arXiv compiles with pdflatex and wants the .bbl rather than a BibTeX run, so the package
# carries main.bbl. body.tex is inlined into a single main.tex, and full-line comments are
# stripped because arXiv publishes the source.
set -euo pipefail
cd "$(dirname "$0")"

rm -rf arxiv cross-instrument-arxiv.tar.gz
mkdir -p arxiv/.build

# 1. the .bbl, from a clean build of the preprint source
tectonic --keep-intermediates --outdir arxiv/.build arxiv.tex >/dev/null 2>&1
cp arxiv/.build/arxiv.bbl arxiv/main.bbl
rm -rf arxiv/.build

# 2. one source file: \pdfoutput=1 tells arXiv to use pdflatex; body.tex inlined
python3 - <<'PY'
src = open("arxiv.tex").read().replace("\\input{body}", open("body.tex").read())
lines = [l for l in src.splitlines() if not l.lstrip().startswith("%")]
open("arxiv/main.tex", "w").write("\\pdfoutput=1\n" + "\n".join(lines) + "\n")
PY
cp references.bib arxiv/

# 3. nothing the source asks for is missing
for f in $(grep -o -E '\\(input|includegraphics)(\[[^]]*\])?\{[^}]+\}' arxiv/main.tex | sed -E 's/.*\{([^}]+)\}/\1/'); do
  [ -e "arxiv/$f" ] || [ -e "arxiv/$f.tex" ] || [ -e "arxiv/$f.pdf" ] || { echo "missing from package: $f" >&2; exit 1; }
done

# 4. the package builds on its own. tectonic is XeTeX, where \pdfoutput makes hyperref pick the
# pdfTeX driver, so the check builds a copy without that first line; arXiv's pdflatex keeps it.
mkdir -p arxiv/.check && cp arxiv/main.bbl arxiv/references.bib arxiv/.check/
tail -n +2 arxiv/main.tex > arxiv/.check/main.tex
(cd arxiv/.check && tectonic main.tex >/dev/null 2>&1) || { echo "arxiv/main.tex does not build" >&2; exit 1; }
mv arxiv/.check/main.pdf arxiv/main.pdf && rm -rf arxiv/.check
tar -czf cross-instrument-arxiv.tar.gz -C arxiv main.tex main.bbl references.bib
echo "-> arxiv/main.pdf, cross-instrument-arxiv.tar.gz"
