# Taste paper (draft)

"How Language Models Learn Taste: Brand Preference in LLMs". One text, `main.tex`, for arXiv. Claims and decisions: the private
`PLAN.md` §1.

Every table reads from `gen/`, written by `../brands_paper.py` from the committed probe outputs (`../probes/`:
`brand_ladder.json`, `factors.json`, `brand_confounds.json`, `brand_logprob*.json`, `stage_pick.json`,
`answer_logprob_steps.json`, `stage_dolci.json`, `stage_tulu.json`). Text-only numbers cite their probe in a `%`
comment below the paragraph (`obvious.json`, `self_preference.json`, `brand_teacher.json`, `search_spotcheck.json`).

    python3 ../brands_paper.py     # rewrite gen/
    tectonic main.tex

Tag the panel `consensus-brands-arxiv-v1` when the paper is posted.
