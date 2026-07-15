# language — the One-Word Census across languages

A cross-language extension of the [consensus](../consensus/) census: the same instrument
(wide-answer-space "Name a X" prompts, one-word clamp, exact-match on script-aware normalized
tokens) asked in **other languages**, to test whether the monoculture replicates and whether
the prototypes are culturally situated. **Results: [FINDINGS.md](FINDINGS.md).** The headline
is that *script*, not language, carries the cultural default (Hindi→India/Diwali vs Urdu→
Pakistan/Eid, same spoken language).

## Instruments (44-model panel, `spec/models.txt`)

- **Deep run** — 15 categories along a contextuality spectrum, in 5 languages:
  `spec/deep_{en,es,hi,ur,mr}.json` → `transcripts_deep_*`. Universal controls (color, shape,
  number, metal, body_part), biological kinds (flower, tree, fruit, bird, animal), and
  cultural gravity wells (country, river, dish, festival, given_name).
- **Pickword** — the open "Pick a word" prompt across **21 languages**, one spec keyed by
  language code: `spec/pickword.json` (v1) and `spec/pickword_v2.json` (the "any word"
  cleanup — cut filler 16%→5%, fixed the Russian echo). v1 kept for the a-vs-any comparison.
- **Hinglish** — `spec/deep_hinglish.json`: Hindi language in Latin script, the sharp H2
  control (holds language fixed, changes only the script). Normalize at the concept level.
- **Bake-off** — `spec/bakeoff_{en,hi,ur}.json`: festival vs holiday vs celebration wording;
  locked `festival` (cleanest Diwali/Eid split, least vacation-drift).

## Analysis

- `analyze.py` — per-category modal / share / distinct, script-aware (`--lang en|es|hi|ur|mr`).
- `pickword.py` — the 21-language pickword panel (modal, base-rate Zipf, compliance).
- `gloss.py` — concept-clusters answers to English concepts via an LLM (synonym collapse +
  filler tagging); writes `spec/gloss_map.json`.
- `views/` — a browsable pickword explorer (`build_pickword.py` → `data.js` → `index.html`;
  currently built on the v1 pickword data).

```bash
# from studies/language/, OPENROUTER_API_KEY in repo-root .env
python ../../harness/run.py --study . --spec spec/deep_hi.json --out transcripts_deep_hi --runs 4 <slugs>
../../.venv/bin/python analyze.py  --lang hi --transcripts transcripts_deep_hi
../../.venv/bin/python pickword.py --transcripts transcripts_pickword_v2
```

## Normalization

Script-aware exact match: Latin(+accents), Devanagari (hi/mr), Arabic (ur), plus the 12
scripts in `pickword.py` (Bengali, Tamil, Telugu, Gujarati, Kannada, Malayalam, Gurmukhi,
Cyrillic, Han+kana, Hangul). **Caveat:** the last-word rule assumes one-word compliance;
verbose SOV replies need first-mentioned extraction. Any *specific* word claimed as a
culture's default needs native review before publication.

Status: **data collected and analyzed, not yet written up** as a paper or post. Planning notes
on the research desk (`convengineering/modelUN/language-census/`).
