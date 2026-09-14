# paper — the October short paper (Agent Evaluation Science Fall 2026)

"Four Frozen Instruments, One Panel: A Construct-Validity Check on Behavioral Measures of
Language Models." Draft 2026-09-13. Abstract registration 2026-10-20, paper 2026-10-25,
OpenReview venue `evalscience.org/AgentEvalSci/2026`. Draft, not yet submitted.

```bash
python3 make_assets.py    # -> gen/matrix_table.tex, gen/marker_table.tex, gen/stats.json
tectonic main.tex         # -> main.pdf
```

Every number in `main.tex` traces to `gen/stats.json` or to the dated result files one level up
(`RESULTS-2026-09-13-eci.txt`, `RESIDUAL-READ-2026-09-13.md`). If
`build_matrix.py` or the ECI mapping changes, rerun `make_assets.py` and re-check the prose.

Short papers are 4 to 6 pages excluding references (CFP checked 2026-09-14), so the draft fits as
is. 2026-09-14: the suggestibility column is the tag effect (the arXiv headline; `../RESULTS-2026-09-14-tageff.txt`),
not the ask-vs-plant shift; under it the taste/stakes split no longer separates. Open before submission: the judge accuracy number from the directed pass (step 0 of the
conduct coding line) goes into §4 and §5; the grader finding stays here.
