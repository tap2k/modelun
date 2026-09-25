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

## The ACL rewrite (2026-09-25)

`body.tex` was rewritten for ARR from the arXiv text; the arXiv v1 text is at the tag. Claims are
stated at the strength the data support: the reversal is "at or above zero, then below it" with
the origins' significance named (only Qwen-2.5 and Grok-4.3 are significantly positive), the walks
are called non-monotonic, "the sign is a clock" and "a pattern-match, not a principle" are gone,
and the "maybe?" result is 70 of 70 with the proposition effect reported beside it rather than
read as rubber-stamping. Added: related work up front, a held-out section and table on the 25
wave-2 models (`../heldout_wave2.py`), the 70-model ablation and tentative-tag figures, a
per-model appendix table, Ethical considerations. Removed: the release-date slope (-5.9 points a
year, cluster p .19), which had no script behind it and is superseded by the held-out test. The
BH counts (5 and 17) are now computed by `make_assets.py`. The anonymous build's main text ends
on page 7. Still open: a human check of the classifier on a sample of replies, which two reviewers
asked for, and a run-to-run check on the tag arm.

## Status 2026-09-25

The classifier was checked by hand on 100 replies (`../validation/`, 98.9% agreement on affirm
versus not, reweighted), and the paper reports it. The Responsible NLP checklist answers are in
`responsible-nlp-checklist.md`. Left before ARR: Tapan's read of the rewritten text, and the
anonymized supplement (a zip of `studies/suggestibility/` without the name or repository URL).
A run-to-run check on the tag arm would answer a reviewer point but is not needed to submit.
