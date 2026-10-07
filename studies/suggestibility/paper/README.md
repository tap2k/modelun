# paper — the suggestibility preprint (arXiv v1, then ACL Rolling Review)

"Tag Questions and the Generational Reversal of Sycophancy Across 45 Language Models."
arXiv:2607.23976, pinned by tag `suggestibility-arxiv-v1`. Going to ACL Rolling Review for the
October 2026 cycle (deadline 2026-10-12), through the review lottery: no designated service
contributor.

The paper's text is `body.tex`, shared by every build. `main.tex` is the arXiv build (plain
article, named), `main-acl.tex` the ACL build (named), `main-acl-review.tex` the anonymous ACL
build for ARR. Each wrapper sets `\ifanon`, which `body.tex` uses for the passages that identify
the author. `acl.sty` and `acl_natbib.bst` are the official ACL style files. Edit `body.tex`;
never fork the text per venue. `responsible-nlp-checklist.md` holds the ARR checklist answers.

```bash
tectonic main.tex               # -> main.pdf, the arXiv build
tectonic main-acl-review.tex    # -> the anonymous ACL build for ARR
tectonic main-acl.tex           # -> the named ACL build
python3 make_assets.py          # -> figs/, gen/ (v1: the July 45 by default; --all for v2, all 105)
```

## The 2026-09-25 rewrite

`body.tex` was rewritten from the arXiv v1 text (at the tag) against four rounds of model reviews.
Claims are stated at the strength the data support: the reversal is "at or above zero, then below
it" with the origins' significance named, the walks are called non-monotonic, and the tentative
tag is 70 of 70 with the proposition effect beside it. Added: a held-out section on the 25 wave-2
models (`../heldout_wave2.py`), the 70-model ablation numbers, the unstated-alternative check
(`../probe_named.py`, `../NAMED-2026-09-25.md`), a hand check of the classifier
(`../validation/`), a per-model table with bootstrap p, and a Broader impact statement. Removed: an
untraced release-date slope. Every number traces to `make_assets.py`, `gen/`, or a dated result
file one level up.

The venue went ACL Rolling Review, then TMLR (2026-09-25, because ARR's October policy requires a
qualified service contributor or a lottery), then back to ARR after TMLR desk-rejected it on
2026-09-27. The TMLR build is at `f046b0f`.

## Submission package

Kept privately under the planning folder's `arr-submission/`: the anonymous PDF, the checklist
answers, the abstract as plain text, and `supplement.zip` (`git archive` of `studies/suggestibility/` without the paper's
LaTeX sources, with the explorer's source link removed and the repository name replaced; a scan for
the author's name, institution, email and repository finds nothing in it).
