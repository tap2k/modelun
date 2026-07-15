# language — the One-Word Census across languages

A cross-language extension of the [consensus](../consensus/) study. Same instrument — wide-answer-space
"Name a X" prompts, one-word clamp, exact-match on normalized tokens — but asked in **other languages**,
to ask two questions:

1. **Does the monoculture replicate?** Is the field as converged in Spanish and Hindi as in English?
2. **Is the prototype the same word, or culturally different?** English trees collapse on *oak*; does
   Hindi collapse on the (translated) *oak*, or on *banyan / neem / mango*? The paper's frictionless-
   prototype thesis predicts culturally-situated modes — this tests it directly.

## Pilot scope

- **8 culturally-portable categories** (of the census's 31): `color, animal, fruit, tree, flower, bird,
  country, any_word`. A mix of strong-mode (color, tree, bird), culturally-interesting prototypes
  (fruit, tree, flower), one diffuse (country), and the headline `any_word`.
- **Two languages:** Spanish (`es`, high-resource) and Hindi (`hi`, low-resource). English (`en`) is the
  baseline, reused from `../consensus/transcripts`.
- **Deferred:** culturally-Western categories (`condiment, cheese, board_game, dinosaur`) — they don't
  port cleanly to Hindi and need native review before inclusion.

Scene ids stay in English so answers align across languages; only the prompt text is translated
(`spec/stimulus_es.json`, `spec/stimulus_hi.json`), and the reply is elicited in-language by the prompt.

## Normalization (script-aware; see `analyze.py`)

- **en** — `a-z`.
- **es** — `a-z` + accents (`áéíóúñü`); accents are **preserved, never stripped** (*año* != *ano*).
- **hi** — Devanagari block `U+0900–U+097F`; the sentence-final *danda* (`।` / `॥`) is stripped as
  punctuation.

**Known limitation (Hindi):** the normalizer takes the last valid word, which works for English (SVO,
answer often sentence-final) but **not for verbose Hindi** (SOV, verb-final): `एक रंग नीला है।` → `है`
("is"), not `नीला` ("blue"). It is correct for **single-word** responses, which the one-word clamp is
meant to produce. **Validate the one-word compliance rate before trusting Hindi numbers**; if models
comply, last-word == the word == correct.

## English baseline (the 8 pilot categories)

`oak 94%` · `rose 91%` · `blue 78%` · `apple 76%` · `elephant 46%` · `sparrow 42%` · `canada 32%` ·
`serendipity 40%` — ≥80% modal in 2/8, mean modal share 62%.

## Run

```bash
# from studies/language/, with OPENROUTER_API_KEY set
python ../../harness/run.py --study . --spec spec/stimulus_es.json --out transcripts_es --runs 4 <slugs>
python ../../harness/run.py --study . --spec spec/stimulus_hi.json --out transcripts_hi --runs 4 <slugs>

../../.venv/bin/python analyze.py --lang es --transcripts transcripts_es
../../.venv/bin/python analyze.py --lang hi --transcripts transcripts_hi
../../.venv/bin/python analyze.py --lang en --transcripts ../consensus/transcripts   # baseline
```

Model roster is `spec/models.txt` (the 44-model consensus panel). Status: **pilot** — stimuli + analyzer
built and validated on the English baseline; `es`/`hi` not yet run.
