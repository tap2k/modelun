#!/usr/bin/env bash
# Build the arXiv source package: arxiv/ (staged sources) and conduct-arxiv.tar.gz.
# Both are gitignored and regenerable. Run from this directory after make_assets.py.
#
#   ./make_arxiv.sh
#
# arXiv compiles with pdflatex and wants the .bbl rather than a BibTeX run, so the package
# carries main.bbl. Full-line comments are stripped because arXiv publishes the source.
set -euo pipefail
cd "$(dirname "$0")"

rm -rf arxiv conduct-arxiv.tar.gz
mkdir -p arxiv/figs arxiv/gen arxiv/.build

# 1. the .bbl, from a clean build of the real source
tectonic --keep-intermediates --outdir arxiv/.build main.tex >/dev/null 2>&1
cp arxiv/.build/main.bbl arxiv/main.bbl
rm -rf arxiv/.build

# 2. sources: \pdfoutput=1 in the first lines tells arXiv to use pdflatex
{ echo '\pdfoutput=1'; grep -v '^%' main.tex; } > arxiv/main.tex
cp references.bib arxiv/
cp figs/hold_fold.pdf arxiv/figs/
cp gen/*.tex arxiv/gen/

# 3. every file the source asks for is in the package
for f in $(grep -o -E '\\(input|includegraphics)(\[[^]]*\])?\{[^}]+\}' arxiv/main.tex | sed -E 's/.*\{([^}]+)\}/\1/'); do
  [ -e "arxiv/$f" ] || [ -e "arxiv/$f.tex" ] || [ -e "arxiv/$f.pdf" ] || { echo "missing from package: $f" >&2; exit 1; }
done

# 4. the package compiles on its own, to a PDF the same size as main.pdf
#    (checked with tectonic, which is XeTeX: the \pdfoutput line is for arXiv's pdflatex and is
#    left out of the check copy, so this proves the file set, not the pdflatex run)
rm -rf arxiv-check && cp -r arxiv arxiv-check && sed -i '' '1d' arxiv-check/main.tex
(cd arxiv-check && tectonic main.tex >/dev/null 2>&1)
echo "bytes: main.pdf $(wc -c < main.pdf), package $(wc -c < arxiv-check/main.pdf)"
rm -rf arxiv-check

tar -czf conduct-arxiv.tar.gz -C arxiv .
echo "wrote conduct-arxiv.tar.gz:"; tar -tzf conduct-arxiv.tar.gz | grep -v '/$' | sed 's/^/  /'

# 5. the abstract as plain text for the submission form (arXiv's limit is 1920 characters)
python3 - <<'PY'
import re
a = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', open('main.tex').read(), re.S).group(1)
for tex, txt in [('\\noindent', ''), ('\\medskip', '\n\n'), ('$-0.64$', '-0.64'), ('$p\\leq0.001$', 'p <= 0.001'), ('$\\alpha$', 'alpha'), ('$\\kappa$', 'kappa')]:
    a = a.replace(tex, txt)
t = '\n\n'.join(' '.join(p.split()) for p in a.split('\n\n') if p.strip())
assert not re.search(r'[\\$]', t), 'TeX left in the plain-text abstract'
open('arxiv-abstract.txt', 'w').write(t + '\n'); print(f'wrote arxiv-abstract.txt, {len(t)} characters')
PY
