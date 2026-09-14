# paper — the October short paper (Agent Evaluation Science Fall 2026)

"Four Frozen Instruments, One Panel: A Construct-Validity Check on Behavioral Measures of
Language Models." Draft 2026-09-13. Abstract registration 2026-10-20, paper 2026-10-25,
OpenReview venue `evalscience.org/AgentEvalSci/2026`. Private until submitted.

```bash
python3 make_assets.py    # -> gen/matrix_table.tex, gen/marker_table.tex, gen/stats.json
tectonic main.tex         # -> main.pdf
```

Every number in `main.tex` traces to `gen/stats.json` or to the dated result files one level up
(`RESULTS-2026-09-13b.txt`, `DATE-CHECK-2026-09-13.txt`, `RESIDUAL-READ-2026-09-13.md`). If
`build_matrix.py` or the ECI mapping changes, rerun `make_assets.py` and re-check the prose.

`NOTE-ANGELINA.md` is the unsent cover note asking Angelina Wang for a read before Oct 20.

Open before submission: the CFP's page limit for short papers (the page says only "2-page
extended abstracts"; the draft is five pages); whether the grader finding (§5) stays here or
moves to the CSCW methods paper; a second reader on a sample of conduct labels.
