# Fingerprint paper (draft)

"Forty Questions: Identifying a Language Model from One-Word Answers". One text, `main.tex`, for arXiv.

Every table reads from `gen/`, written by `../fingerprint_paper.py` from the committed probe outputs
(`../probes/fingerprint*.json`, `provider_audit.json`, `reference_contamination.json`). Numbers in the text are
written out; `gen/numbers.tex` lists the headline values for checking them after a rerun. Each paragraph's
source is in a `%` comment below it.

    python studies/consensus/fingerprint_paper.py     # rewrite gen/
    tectonic main.tex                                 # build

The panel is pinned at 94 models (`AFTER_PANEL` in `../probe_fingerprint.py`). Tag the panel
`consensus-fingerprint-arxiv-v1` when the paper is posted.
