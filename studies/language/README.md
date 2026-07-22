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
- **Pickword** — the open "pick any word" prompt in **44 languages** (scene id = language code),
  one spec: `spec/pickword.json`. Phrased "pick *any* word" to suppress instruction-echo filler
  (16%→5%; e.g. Russian no longer echoes слово / "word"). **37 reported; 7 dropped** for
  prompt-echo, greeting-default modal, or <85% in-script compliance (`sdd`, `yue`, `tr`, `th`,
  `yo`, `ha`, `jv` — the exclusion set lives in `views/build_pickword.py`; `sdd`/`yue` are
  AI-mistranslated prompts awaiting native review).
- **Framing sweep** — three English framings of the open prompt, folded into the same file as
  scenes `en` ("pick any word", the census baseline), `en_fav` ("your favorite word?"), and
  `en_beautiful` ("most beautiful word?"). The serendipity attractor climbs 42% → 70% → 70% as
  the prompt gets explicit — see `favword.py` and FINDINGS §6.
- **Hinglish** — `spec/deep_hinglish.json`: Hindi language in Latin script, the sharp H2
  control (holds language fixed, changes only the script). Normalize at the concept level.
- **Bake-off** — `spec/bakeoff_{en,hi,ur}.json`: festival vs holiday vs celebration wording;
  locked `festival` (cleanest Diwali/Eid split, least vacation-drift).

## Analysis

- `analyze.py` — per-category modal / share / distinct, script-aware (`--lang en|es|hi|ur|mr`).
- `pickword.py` — the 44-language pickword panel (modal, base-rate Zipf, compliance).
- `favword.py` — the English framing sweep (pick / favorite / most-beautiful → 42/70/70%).
- `gloss.py` — concept-clusters answers to English concepts via an LLM (synonym collapse +
  filler tagging); writes `spec/gloss_map.json`.
- `views/` — a browsable pickword explorer (`build_pickword.py` → `data.js` → `index.html`).

```bash
# from studies/language/, OPENROUTER_API_KEY in repo-root .env
python ../../harness/run.py --study . --spec spec/deep_hi.json --out transcripts_deep_hi --runs 4 <slugs>
../../.venv/bin/python analyze.py  --lang hi --transcripts transcripts_deep_hi
../../.venv/bin/python pickword.py --transcripts transcripts_pickword
```

## Normalization

Script-aware exact match: Latin(+accents), Devanagari (hi/mr), Arabic (ur), plus the 12
scripts in `pickword.py` (Bengali, Tamil, Telugu, Gujarati, Kannada, Malayalam, Gurmukhi,
Cyrillic, Han+kana, Hangul). **Caveat:** the last-word rule assumes one-word compliance;
verbose SOV replies need first-mentioned extraction. Any *specific* word claimed as a
culture's default needs native review before publication.

Status: data collected and analyzed. The pickword/framing/Ukraine strand is drafted as a blog post
(*The One-Word Census, Redux* — convovo-site, `draft`); the deep-run script-carries-culture strand
is unwritten. Blog-only, not paper material. Planning notes on the research desk
(`convengineering/modelUN/language-census/`).
