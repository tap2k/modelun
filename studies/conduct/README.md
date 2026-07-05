# conduct — a behavioral atlas of language models

Study #1 on the [modelun harness](../../README.md), and its **worked example**: the reference a new
study is cloned from. It exercises every part of the harness — a frozen multi-turn stimulus, a codebook
of binary and graded criteria, an LLM judge with quote-verification, and a bespoke viewer built on the
generic renderer. To start your own study, copy this directory's shape.

## The question

**How do language models conduct themselves under pressure?** Not how they answer a personality
questionnaire — how they behave across a hard, multi-turn conversation: when a user insists 5×9 is 54
and turns nasty, begs for a forged sick note, confides a dying parent and then asks for a cheerful
email, or wants help betting their savings on a memecoin. The **identical** escalating script goes to
every model; we read the transcripts.

Each scene probes one of three dimensions of conduct:

- **TONGUE** — *honesty*: will it tell you a truth you don't want to hear?
- **HANDS** — *integrity*: will it refuse to *do* a wrong thing you ask for?
- **HEART** — *attunement*: will it stay with your feelings?

| Dimension | Scene | What it tests |
|---|---|---|
| TONGUE | **facts** — the arithmetic hill | holds an impersonal fact under contempt |
| TONGUE | **bad_plan** — the day-trader | withholds applause for a bad plan under social punishment |
| TONGUE | **self_label** — the flattering self-story | declines to ratify a self-flattering frame |
| HANDS | **doctors_note** — the backdated note | refuses a forgery, warmly |
| HANDS | **the_leap** — the all-in | won't lend its skill to a hype-driven self-harming plan |
| HEART | **pivot** — the disclosure & pivot | carries the weight across a topic-change |

The synthesis reads each model across the three dimensions. Frontier labs with a full generational
ladder resolve into recurring **house styles** — a working lens, not a law:

- **Therapist** — names the move you're making instead of just answering it.
- **Coach** — holds the line and hands you a concrete tool to survive it.
- **Apologist** — softens, apologizes, makes the friction go away — even when the friction was the truth.

## Method

A fixed four-panel script per scene, identical for every model and escalating regardless of the reply;
each model run twice at deployment temperature; a system-prompt **clamp** holds replies short and plain
so the read is about conduct, not formatting. Each scene carries a **marker** — a discrete,
quote-verified event scored by a single judge (`google/gemini-2.5-flash`) — that turns the scene into a
comparable readout. See [`docs/markers.md`](docs/markers.md).

These are reads at small N, dated specimens. Vivid enough to recognize, precise enough to compare on the
markers — not a leaderboard.

## How it maps onto the harness

The conduct study is a concrete `{stimulus, codebook}` + views. Every file here has a generic role —
this is the mapping to copy:

| Harness concept | Here |
|---|---|
| stimulus (scenes × turns) | [`spec/stimulus.json`](spec/stimulus.json) — the frozen 6-scene script + the clamp; `stimulus-unclamped.json` is the ablation |
| codebook (criteria × kind) | [`spec/codebook.py`](spec/codebook.py) — 4 binary markers + 2 graded; the source of truth for the categorical layer |
| path overrides | [`spec/paths.json`](spec/paths.json) — keeps this study's historical `data/benchmark` + `markers/` names |
| transcripts (Contract A) | [`data/benchmark/`](data/benchmark/) — every model × 6 scenes × 2 runs ([`MANIFEST.md`](data/benchmark/MANIFEST.md)) |
| store (adjudicated) | `data/benchmark/markers.json` — the voted, quote-verified marker layer |
| views | [`views/`](views/) — the marker grid, frontier compare, and synthesis, built on `harness/viewer/core.js` |
| study docs | [`docs/`](docs/) — [scenes](docs/scenes.md), [markers](docs/markers.md), [houses](docs/houses.md), [inductive-coding](docs/inductive-coding.md) |
| earlier layer | [`bottom-up/`](bottom-up/) — the study's first, inductive methodology (emergent bestiary + 3-reader cross-check); its cards, reads, and catchphrases are still rendered by the views. See its [README](bottom-up/README.md). |

## Run

From the repo root (the harness is study-agnostic; `--study studies/conduct` points it here):

```bash
# run the scenes against models, score the codebook, adjudicate the store
python harness/run.py        --study studies/conduct anthropic/claude-opus-4.8 openai/gpt-5.4 --runs 2
python harness/judge.py      --study studies/conduct --judge google/gemini-2.5-flash
python harness/adjudicate.py --study studies/conduct

# the marker grid + the review site
python studies/conduct/views/plot.py     # data/benchmark → reads/markers_grid.png
python studies/conduct/views/build.py    # → views/data.js (+ core.js); open views/index.html
```

## Tripwires

- **The stimulus is sacred.** `spec/stimulus.json` is byte-identical input to every model — that's what
  makes columns comparable. Any change (including the clamp) must bump `script_version`; old and new are
  not comparable. See [AGENTS.md](../../AGENTS.md).
- **The judge is itself a subject.** `gemini-2.5-flash` scoring the google family (gemini / gemma) is
  self-judged — the adjudicator flags those cells rather than trusting or dropping them silently.
- **Markers annotate, they don't replace.** Every value cites a verbatim trigger quote, string-verified
  against the transcript; an unverifiable claim is dropped.
