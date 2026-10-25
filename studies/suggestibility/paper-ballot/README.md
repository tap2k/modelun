# Ballot paper (draft)

Standalone arXiv note on probe_contested_ballot.py. Tag `ballot-arxiv-v1` on publish.

Every number in `main.tex` and every table comes from `../ballot_stats.py`, which reads the committed files under
`../probes/contested_ballot/` and `../probes/contested_assert_analysis.json`. `gen/numbers.tex` lists the headline
values for checking the text after a rerun.

    python studies/suggestibility/ballot_stats.py     # -> gen/
    tectonic main.tex

To check before submitting: the bib entries for Exler et al. and Cen et al. (first names) and Miyazaki and Hall.
