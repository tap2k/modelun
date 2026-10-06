# paper — arXiv write-up of the consensus study

"The One-Word Census: Answer-Choice Conformity Across 44 Language Models" (Parikh, 2026; v2). The v3 draft covers 105 models.

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

## v3 (draft, 2026-10-06)

`main.tex` is the v3 draft: 105 models x 96 prompts x 8 runs. It reads `figs-v3/` and `gen-v3/`
(`make_assets.py --v3`) and the `*_v3.json` probes (`robustness.py`, `pairwise.py`, `probe_smoothing.py`,
`probe_corpusfreq.py`, `probe_permutation.py`, `probe_temp0.py`, `family_signal.py`, each with `--v3`;
`lineage_trend.py`; `probe_serendipity.py`; `stage_ladder.py census|verbs`). v2's `figs/` and `gen/` stay as
published; v2 is reproducible from tag `consensus-arxiv-v2`. Tag `consensus-arxiv-v3` at submission.

Open before submission: the Nemotron training-data counts (TODO in §6) need a committed probe; native-speaker
checks of the pickword translations; `make_assets.py --v3` NEWEST/OLDEST review.
