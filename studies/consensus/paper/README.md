# paper — arXiv write-up of the consensus study

"The Hidden Consensus: Answer-Choice Conformity Across 39 Language Models" (Parikh, 2026).

## Build

```bash
# 1. regenerate figures, the scorecard table, and every quoted number from the frozen data
../../../.venv/bin/python make_assets.py     # -> figs/*.pdf, gen/scorecard_table.tex, gen/stats.json

# 2. compile (tectonic fetches packages on first run; brew install tectonic)
tectonic main.tex                            # -> main.pdf
```

Every number quoted in `main.tex` traces to `gen/stats.json`, `../analysis.json`, or the
robustness/pairwise suites (`../robustness.py`, `../pairwise.py`) — nothing is hand-entered
from working notes. If the transcripts or `analyze.py` change, rerun `make_assets.py` and
re-check the prose against the new `gen/stats.json` before rebuilding.

Cohort definitions for the peaked-vs-diffuse comparison (§4.3) are explicit in
`make_assets.py` (`NEWEST` / `OLDEST`).

Bibliography author lists were verified against the PDFs in the flowstore bibliography
folder (2026-07-07); `references.bib` corrects several entries relative to BIBLIOGRAPHY.md
shorthand (GX-Chen et al., Gueorguieva et al., Karouzos et al., Liu).
