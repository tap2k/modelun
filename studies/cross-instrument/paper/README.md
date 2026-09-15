# paper — the October short paper (Agent Evaluation Science Fall 2026)

"Low-Cost Behavioral Assays for Language Models: Fixed Prompts, Two Ways of Scoring, and What They Found." Reordered 2026-09-15 (Tapan): (1) the method, fixed prompts with two scoring routes (exact match on clamped replies; qualitative coding on open replies, judge validated per code); (2) findings, each assay on its own (census + language; tag question; conduct: generation and house); (3) validation, what the assays track (the matrix, one table) and the judge (Table 2); (4) what it is for. The validity check is the closing section, not the story. Earlier versions in git history (39e4ef1 validity check; 1ea6553 program paper, check-led). Abstract registration 2026-10-20, paper 2026-10-25, OpenReview venue `evalscience.org/AgentEvalSci/2026`. Draft, not yet submitted.

```bash
python3 make_assets.py    # -> gen/matrix_table.tex, gen/marker_table.tex, gen/stats.json
tectonic main.tex         # -> main.pdf
```

Every number in `main.tex` traces to `gen/stats.json` or to the dated result files one level up
(`RESULTS-2026-09-13-eci.txt`, `RESIDUAL-READ-2026-09-13.md`). If
`build_matrix.py` or the ECI mapping changes, rerun `make_assets.py` and re-check the prose.

Short papers are 4 to 6 pages excluding references (CFP checked 2026-09-14), so the draft fits as
is. 2026-09-14: the suggestibility column is the tag effect (the arXiv headline; `../RESULTS-2026-09-14-tageff.txt`),
not the ask-vs-plant shift; under it the taste/stakes split no longer separates. Judge accuracy against the human directed pass folded in 2026-09-14 (§4.1, Table 2, two lessons in §5), from `../../conduct/data/coding/JUDGE-ACCURACY-2026-09-14.md`; the residual-read rescoring of the top-ranked model was withdrawn (human held both runs).

Result restated 2026-09-14 (abstract, §5 What survives): the generation signal read by date is convergence on the two right-answer conduct items (zero variance after mid-2025, six vendors) against a persisting vendor split on the two judgment-call items; saturation named, post-training as hypothesis with the two designs that test it. Structure and tables unchanged.

House-style numbers in §4 are codebook v1 (RELABEL-v1-2026-09-14.md); replace with v2 if the rerun on the held-out fifty lands before submission, and state the version.

Open before submission: the judge accuracy number from the directed pass (step 0 of the
conduct coding line) goes into §4 and §5; the grader finding stays here.
