# paper — the suggestibility preprint (arXiv v1, then ACL Rolling Review)

"Tag Questions and the Generational Reversal of Sycophancy Across 45 Language Models."
arXiv:2607.23976, pinned by tag `suggestibility-arxiv-v1`. Being revised for ACL Rolling Review
(decided 2026-09-25).

The paper's text is `body.tex`, shared by every build. The wrappers hold only the template, the
author block and the bibliography style: `main.tex` is the arXiv build (plain article, named),
`main-acl.tex` the ACL build (named), `main-acl-review.tex` the ACL build for ACL Rolling Review
(anonymous). Each wrapper sets `\ifanon`, which `body.tex` uses for the passages that identify the
author. `acl.sty` and `acl_natbib.bst` are the official ACL style files. Edit `body.tex`; never fork
the text per venue.

```bash
tectonic main.tex               # -> main.pdf, the arXiv build
tectonic main-acl-review.tex    # -> the anonymous ACL build for ACL Rolling Review
tectonic main-acl.tex           # -> the named ACL build
python3 make_assets.py          # -> figs/; note it now draws the current panel, not the July 45
```

The 2026-09-25 model reviews (kept privately) scored the arXiv text 4, 4, 5 and 8. Their objections
are to interpretation rather than measurement: the reversal is mostly zero to negative, the
"maybe?" arm changes the proposition, the ablation does not show "a pattern-match, not a
principle", and the out-of-sample confirmation is two models. GPT and Gemini also ask for the
rule-based classifier to be validated on a sample of replies.
