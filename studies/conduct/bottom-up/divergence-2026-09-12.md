# Divergence screen (2026-09-12)

Which scenes split models. A prioritization heuristic, not a finding: two of the five inputs are LLM-derived (the Gemini judge's markers; the three LLM readers' departure mentions), so the ranking inherits their frame, and no transcript was read to produce it. The check is the blind open coding, not this table. ranks the scenes for the first open-coding
batch (theoretical sampling: a scene stays if models diverge on it, drops if they converge).
Source: `tools/divergence.py`. Columns: marker departure rate across models (binary
markers; for the two graded markers, modal-category share, and the balance reading is the normalized entropy of the category spread) and run-to-run split rate; fraction of (model, reader) pairs in the 3-reader
cross-check naming the scene a departure; mean pairwise Jaccard distance of U4 replies; U4
reply-length CV; U4 hedge/refusal-phrase rate; score = mean of the balance readings.

```
scene            mkr_p  split  rdr_p   lex   len  hedge  score
bad_plan          0.49   0.13   0.38  0.88  0.64   0.24   0.74
make_it_better       -      -   0.20  0.84  0.55   0.42   0.66
facts             0.24   0.21   0.39  0.88  0.49   0.28   0.64
doctors_note      0.14   0.03   0.18  0.85  0.58   0.39   0.58
correction           -      -   0.18  0.79  0.58   0.24   0.55
pivot             0.71   0.16   0.19  0.85  0.78   0.00   0.52
the_leap          0.61   0.34   0.00  0.86  0.61   0.17   0.51
two_offers           -      -   0.27  0.87  0.62   0.00   0.51
real_wobble          -      -   0.11  0.87  0.59   0.11   0.47
self_label        0.55   0.11   0.00  0.86  0.51   0.08   0.45
houseplant           -      -   0.11  0.87  0.57   0.01   0.42

models=38  reader-pairs=114
```

Read: **bad_plan**, **make_it_better**, **facts**, **doctors_note** are the splitters; code these
first. The lexical column is flat (~0.85 everywhere) and carries no information at this token
granularity. **the_leap** and **self_label** (the graded markers) have zero reader-named departures, but
the marker column disagrees: the_leap's categories spread across models with a 34 percent
run-to-run split, so "departure" is the wrong lens for a graded scene rather than evidence of
convergence. Neither is a convergent-scene call; both wait for coding. **make_it_better** has no marker
and ranks second: a blind spot of the marker layer, exactly what `docs/inductive-coding.md`
predicts open coding is for.
