# paper — the suggestibility preprint (arXiv v1, then TMLR)

"Tag Questions and the Generational Reversal of Sycophancy Across 45 Language Models."
arXiv:2607.23976, pinned by tag `suggestibility-arxiv-v1`. Submitted to TMLR (decided
2026-09-25).

The paper's text is `body.tex`, shared by both builds. `main.tex` is the arXiv build (plain
article, named); `main-tmlr.tex` is the anonymous TMLR submission. Each wrapper sets `\ifanon`,
which `body.tex` uses for the passages that identify the author. `tmlr.sty`, `tmlr.bst` and
`fancyhdr.sty` are the official TMLR style files (github.com/JmlrOrg/tmlr-style-file at 7bf90ef,
license in `tmlr-LICENSE`). Edit `body.tex`; never fork the text per venue.

```bash
tectonic main.tex         # -> main.pdf, the arXiv build
tectonic main-tmlr.tex    # -> main-tmlr.pdf, the anonymous TMLR submission
python3 make_assets.py    # -> figs/, gen/ (the July 45 by default; --all for the 70)
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

The rewrite was first fitted to ACL Rolling Review (ACL builds, Responsible NLP checklist). ARR's
October 2026 sustainable-reviewing policy requires a qualified service contributor per submission
or a lottery for review, so the paper went to TMLR instead, which has no service requirement and
accepts on whether claims are supported by evidence. The ACL builds and checklist are at `fbdbe6a`.

## Submission package

Kept privately under the planning folder's `tmlr-submission/`: the anonymous PDF, the abstract as
plain text, and `supplement.zip` (`git archive` of `studies/suggestibility/` without the paper's
LaTeX sources, with the explorer's source link removed and the repository name replaced; a scan for
the author's name, institution, email and repository finds nothing in it).
