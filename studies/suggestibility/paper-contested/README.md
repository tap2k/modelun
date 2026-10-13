# Contested questions paper (draft)

Companion to `../paper/` (the decision items). One text, `main.tex`, for arXiv.

Numbers in the text are written out in `main.tex`; `gen/numbers.tex` lists the same values for
checking them after a rerun. Every table reads from `gen/`. Both come from `../contested_stats.py`, which reads `../probes/contested/` and the four
`../probes/contested_ladder_*.json` files.

    python studies/suggestibility/contested_stats.py             # recompute everything (~30 min)
    python studies/suggestibility/contested_stats.py --numbers   # rewrite numbers.tex and the row files only
    tectonic main.tex                                            # build
