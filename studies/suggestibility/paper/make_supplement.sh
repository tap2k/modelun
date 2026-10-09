#!/usr/bin/env bash
# Build the anonymized ARR supplement: supplement/ (staged) and supplement.zip. Both are gitignored
# and regenerable. Run from this directory; it archives the committed state (HEAD).
#
#   ./make_supplement.sh
#
# The study directory without the paper sources or the contested paper, plus the repository
# licenses. Identifying strings are replaced, then a scan for the author's name, institution, email,
# repository and arXiv IDs must find nothing, or the build fails.
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(git rev-parse --show-toplevel)"

rm -rf supplement supplement.zip
mkdir supplement
git -C "$ROOT" archive --prefix=suggestibility/ HEAD:studies/suggestibility | tar -x -C supplement
S=supplement/suggestibility

# 1. what reviewers do not need, and what names the author
rm -rf "$S/paper-contested"
(cd "$S/paper" && rm -f -- *.tex *.pdf *.bib *.sty *.bst README.md make_arxiv.sh make_supplement.sh .gitignore)
cp "$ROOT/LICENSE-DATA" "$S/"
sed 's/^Copyright (c) \(.*\) Tapan Parikh$/Copyright (c) \1 Anonymous authors/' "$ROOT/LICENSE" > "$S/LICENSE"

# 2. identifying strings
grep -rIl -e modelun -e /Users/parikh/ "$S" | while read -r f; do
  sed -i '' -e 's/modelun/study-repo/g' -e 's#/Users/parikh/#/Users/author/#g' "$f"
done
sed -i '' '/<a class="src" href="https:\/\/github.com/d' "$S/views/index.html" "$S/views/contested.html"
perl -0pi -e 's/\(\[arXiv:2607\.23976\]\(https:\/\/arxiv\.org\/abs\/2607\.23976\), source in `paper\/main\.tex`\)/(preprint link withheld for review)/;
              s/Labelled blind by Tapan/Labelled blind by the author/; s/Cornell abstention line/abstention line/' "$S/README.md"

# 3. the scan
hits=$(grep -rIl -i -E 'parikh|tapan|tap2k|cornell|tsp53|convovo|maussindustries|modelun|2607\.23976|2609\.30012' supplement || true)
[ -z "$hits" ] || { echo "identifying text remains in:" >&2; echo "$hits" >&2; exit 1; }

(cd supplement && zip -q -r -X ../supplement.zip suggestibility)
echo "wrote supplement.zip: $(du -h supplement.zip | cut -f1), $(unzip -l supplement.zip | tail -1 | awk '{print $2}') files; scan clean"
