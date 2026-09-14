# Cross-instrument matrix

Do the published instruments measure one thing, measure capability in disguise, or measure
nothing in common? Per-model scores from each instrument, joined on the model label, Spearman
correlations with bootstrap 90 percent intervals, and partial correlations controlling for a
capability index and for release date. The construct-validity check the validity literature
(Wallach et al.; Salaudeen et al., "Measurement to Meaning") asks of any instrument, run on our
own record.

    python build_matrix.py > RESULTS-<date>.txt

Columns (higher = more of the named behavior):
- `census_conc`: negative mean answer surprisal from the One-Word Census (`consensus/analysis.json`).
- `suggestib`: the tag effect from How You Ask, affirm under "..., right?" minus affirm under the
  neutral ask (`suggestibility/probes/righteffect_analysis.json`, written by
  `probe_righteffect.py analyze`); `sugg_taste` and `sugg_conseq` are its halves, matters of taste
  and decisions with stakes (no item has a right answer). `sugg_shift` is the study's ask-vs-plant
  shift (`suggestibility/analysis.json`), kept as a check: rho 0.68 with the tag effect, same
  capability reading.
- `format_tax`: plain minus JSON surprisal from the format study (`structured/views/data.js`).
- `conduct_dep`: departure rate over the four binary conduct markers (`conduct/data/benchmark/markers.json`);
  the per-marker block breaks it into `caved_on_fact`, `forged_document`, `cheerled_bad_plan`, `snapped_to_task`.
- `capability`: the Epoch Capabilities Index, `eci_scores_2026-09-13.csv` (epoch.ai, CC-BY,
  retrieved 2026-09-13), mapped to panel labels in `eci_map_2026-09-13.tsv`; dated variants are
  the latest released before each study's run. Covers 69 of 70 census and 35 of 38 conduct models.
- `release_date`: from the same ECI file. Collinear with capability on this panel (rho 0.91), so
  "capability" and "generation" cannot be separated here; the script partials on each in turn.
- `cap_arena`: LMArena text, snapshot 2026-09-11 (`arena_2026-09-11.txt`); recent models only,
  restricted range, kept as a check on ECI.

Partials are rank-based sequential residualization, pairwise on the models that carry both
instruments and the control. Companion probes: `temperature_check.py` (stability vs direction),
`residual.py` (who is off the census-conduct diagonal), `atlas_check.py` (report honesty vs census).

Files. Read `RESULTS-2026-09-14-tageff.txt` first: the matrix on the full panel with the tag
effect as the suggestibility column, and the reading that stands. `RESULTS-2026-09-13-eci.txt` is
the same matrix with the ask-vs-plant shift in that column (the switch changes no headline; the
taste/consequential split separates under the shift and not under the tag effect). `RESIDUAL-READ-2026-09-13.md` is the by-eye read of the residual rows, with two
judge issues. The earlier dated files (`RESULTS-2026-09-13.txt`, `TEMPERATURE-CHECK`, `RESIDUAL`,
`TASTE-SPLIT`, all 2026-09-13) record the morning's reading against Arena and are stamped
superseded; kept as the record of how the reading moved in one day. `paper/` is the October
short paper.
