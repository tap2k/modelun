#!/usr/bin/env bash
# Build the arXiv source package: arxiv/ (staged sources) and fingerprint-arxiv.tar.gz.
# Both are gitignored and regenerable. Run from this directory after ../fingerprint_paper.py.
#
#   ./make_arxiv.sh
#
# arXiv compiles with pdflatex and wants the .bbl rather than a BibTeX run, so the package
# carries main.bbl. The gen/ tables are inlined into a single main.tex, and full-line comments
# are stripped because arXiv publishes the source.
set -euo pipefail
cd "$(dirname "$0")"

rm -rf arxiv fingerprint-arxiv.tar.gz
mkdir -p arxiv/.build

# 1. the .bbl, from a clean build of the real source
tectonic --keep-intermediates --outdir arxiv/.build main.tex >/dev/null 2>&1
cp arxiv/.build/main.bbl arxiv/main.bbl
rm -rf arxiv/.build

# 2. one source file: \pdfoutput=1 tells arXiv to use pdflatex; gen/ tables inlined
python3 - <<'PY'
import re
src = open("main.tex").read()
src = src.replace("\\makeatletter\\newcommand{\\rows}[1]{\\@@input #1 }\\makeatother\n", "")
src = re.sub(r"\\(?:rows|input)\{(gen/[^}]+)\}", lambda m: "\n" + open(m.group(1)).read().strip(), src)
lines = [l for l in src.splitlines() if not l.lstrip().startswith("%")]
assert not any("gen/" in l for l in lines), "a gen/ reference was not inlined"
open("arxiv/main.tex", "w").write("\\pdfoutput=1\n" + "\n".join(lines) + "\n")
PY
cp references.bib arxiv/

# 3. the package builds on its own. tectonic is XeTeX, where \pdfoutput makes hyperref pick the
# pdfTeX driver, so the check builds a copy without that first line; arXiv's pdflatex keeps it.
mkdir -p arxiv/.check && cp arxiv/main.bbl arxiv/references.bib arxiv/.check/
tail -n +2 arxiv/main.tex > arxiv/.check/main.tex
(cd arxiv/.check && tectonic main.tex >/dev/null 2>&1) || { echo "arxiv/main.tex does not build" >&2; exit 1; }
mv arxiv/.check/main.pdf arxiv/main.pdf && rm -rf arxiv/.check
echo "pages: main.pdf $(pdfinfo main.pdf | awk '/Pages/{print $2}'), package $(pdfinfo arxiv/main.pdf | awk '/Pages/{print $2}')"
tar -czf fingerprint-arxiv.tar.gz -C arxiv main.tex main.bbl references.bib
echo "-> arxiv/main.pdf, fingerprint-arxiv.tar.gz"

# 4. the abstract as plain text for the submission form (arXiv's limit is 1920 characters)
python3 - <<'PY'
import re
a = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', open('main.tex').read(), re.S).group(1)
for tex, txt in [('\\noindent', ''), ("``", '"'), ("''", '"'), ('\\%', '%'), ('~', ' ')]:
    a = a.replace(tex, txt)
t = ' '.join(a.split())
assert not re.search(r'[\\$]', t), 'TeX left in the plain-text abstract'
assert len(t) <= 1920, f'abstract is {len(t)} characters, over arXiv\'s 1920'
open('arxiv-abstract.txt', 'w').write(t + '\n'); print(f'wrote arxiv-abstract.txt, {len(t)} characters')
PY
