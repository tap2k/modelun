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
- `capability`: LMArena text score, snapshot 2026-09-11 (`arena_2026-09-11.txt`, hand-mapped labels).

Caveats in the results file. The capability column is the weak link: Arena carries only the
recent half of the panel, so the joint panel with capability is small.
