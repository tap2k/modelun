# Cross-instrument matrix

Do the published instruments measure one thing, measure capability in disguise, or measure
nothing in common? Per-model scores from each instrument, joined on the model label, Spearman
correlations with bootstrap 90 percent intervals, and partial correlations controlling for a
capability index. The construct-validity check the validity literature (Wallach et al.;
Salaudeen et al., "Measurement to Meaning") asks of any instrument, run on our own record.

    python build_matrix.py > RESULTS-<date>.txt

Columns (higher = more of the named behavior):
- `census_conc`: negative mean answer surprisal from the One-Word Census (`consensus/analysis.json`).
- `suggestib`: suggestibility rate from How You Ask (`suggestibility/analysis.json`).
- `format_tax`: plain minus JSON surprisal from the format study (`structured/views/data.js`).
- `conduct_dep`: departure rate over the six binary conduct markers (`conduct/data/benchmark/markers.json`).
- `capability`: LMArena text score, snapshot 2026-09-11 (`arena_2026-09-11.txt`, hand-mapped labels); recent models only, restricted range.
- `capability_eci` and `release_date` (`eci_matrix.py`): the Epoch Capabilities Index, `eci_scores_2026-09-13.csv` (CC-BY, epoch.ai), mapped in `eci_map_2026-09-13.tsv`; covers the older half of the panel. Use this one.

Read `ECI-MATRIX-2026-09-13.txt` first; the earlier files record the morning's reading and are marked superseded. Capability and release date are collinear (0.91) on this panel, so "capability" and "generation" cannot be separated here.
