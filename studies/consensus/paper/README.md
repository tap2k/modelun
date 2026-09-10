# paper — arXiv write-up of the consensus study

"The One-Word Census: Answer-Choice Conformity Across 44 Language Models" (Parikh, 2026).

## Build

```bash
# 1. regenerate figures, the scorecard table, and every quoted number from the frozen data
../../../.venv/bin/python make_assets.py     # -> figs/*.pdf, gen/scorecard_table.tex, gen/stats.json

# 2. compile (tectonic fetches packages on first run; brew install tectonic)
tectonic main.tex                            # -> main.pdf
```

Every number quoted in `main.tex` traces to `gen/stats.json`, `../analysis.json`, or the
robustness/pairwise/probe suites (`../robustness.py`, `../pairwise.py`, `../probe_*.py`,
e.g. `probes/corpusfreq.json` for the §4.1 frequency-null numbers) — nothing is hand-entered
from working notes. If the transcripts or `analyze.py` change, rerun `make_assets.py` and
re-check the prose against the new `gen/stats.json` before rebuilding.

Cohort definitions for the peaked-vs-diffuse comparison (§4.3) are explicit in
`make_assets.py` (`NEWEST` / `OLDEST`).

Bibliography author lists were verified against the source PDFs (2026-07-07);
`references.bib` corrects several entries relative to BIBLIOGRAPHY.md
shorthand (GX-Chen et al., Gueorguieva et al., Karouzos et al., Liu).

## Pending for the next revision (v3)

Neither warrants a revision on its own; include both when one happens.

1. **Data-availability link → tag.** The paragraph points at `tree/main`, which now carries the
   wave-2 roster (70 models) and September re-snapshots. Point it at `tree/consensus-arxiv-v2`,
   the frozen 44-model panel the paper describes.
2. **Per-model unclamped sentence** after the oak/rose list in §3.4 ("Why one-word answers"):
   the ranking survives without the clamp, not just the mode — a model's share of bare-prompt
   replies avoiding the field's modal word rank-correlates with its census surprisal at Spearman
   0.61 (n=44, permutation p<0.001; `probe_clamp.py`, `probes/clamp_rank.json`). Optional
   corroboration: Spearman 0.64 against the convergence study's embedding uniqueness over the 17
   shared models excluding ernie (`probe_convergence_xval.py`).

