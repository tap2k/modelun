# modelun — a behavioral atlas of language models

**How do language models conduct themselves under pressure?** Not how they answer a personality
questionnaire — how they behave across a hard, multi-turn conversation: when a user insists 5×9 is 54
and turns nasty, begs for a forged sick note, confides a dying parent and then asks for a cheerful
email, or wants help betting their savings on a memecoin. We send the **identical** escalating script
to every model and read the transcripts.

## The frame

Each scene probes one of three dimensions of conduct:

- **TONGUE** — *honesty*: will it tell you a truth you don't want to hear?
- **HANDS** — *integrity*: will it refuse to *do* a wrong thing you ask for?
- **HEART** — *attunement*: will it stay with your feelings?

Six scenes sample those three (full scripts in [`docs/scenes.md`](docs/scenes.md)):

| Dimension | Scene | What it tests |
|---|---|---|
| TONGUE | **facts** — the arithmetic hill | holds an impersonal fact under contempt |
| TONGUE | **bad_plan** — the day-trader | withholds applause for a bad plan under social punishment |
| TONGUE | **self_label** — the flattering self-story | declines to ratify a self-flattering frame |
| HANDS | **doctors_note** — the backdated note | refuses a forgery, warmly |
| HANDS | **the_leap** — the all-in | won't lend its skill to a hype-driven self-harming plan |
| HEART | **pivot** — the disclosure & pivot | carries the weight across a topic-change |

The synthesis reads each model across the three dimensions. The frontier labs with a full
generational ladder resolve into recurring **house styles** — a working lens, tested and revised
against the data, with room for emergent patterns:

- **Therapist** — names the move you're making instead of just answering it.
- **Coach** — holds the line and hands you a concrete tool to survive it.
- **Apologist** — softens, apologizes, makes the friction go away — even when the friction was the truth.

## Method

A fixed four-panel script per scene, identical for every model and escalating regardless of the
reply; run each model twice at deployment temperature; a system-prompt **clamp** holds replies short
and plain so the read is about conduct, not formatting. Each scene carries a **marker** — a discrete,
quote-verified event scored by a single judge (`google/gemini-2.5-flash`) — that turns the scene into
a comparable readout. See [`docs/markers.md`](docs/markers.md).

These are reads at small N, dated specimens. Vivid enough to recognize, precise enough to compare on
the markers — not a leaderboard.

## What's here

| Path | What it is |
|---|---|
| [`registers.json`](registers.json) | The instrument — the frozen 6-scene script + the clamp. Source of truth. |
| [`docs/scenes.md`](docs/scenes.md) | The scene scripts (user turns), by dimension. |
| [`docs/markers.md`](docs/markers.md) | The marker layer + the judge. |
| [`data/benchmark/`](data/benchmark/) | The dataset — every model × 6 scenes × 2 runs, plus `markers.json`. See [`MANIFEST.md`](data/benchmark/MANIFEST.md). |
| [`scout/`](scout/) | The runner (`atlas_scout.py`), the marker pipeline (`run_markers.py`, `adjudicate_markers.py`, `markers.py`, `plot_markers.py`), the site builder. |

## Run it

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # put your OpenRouter key in it

# run the scenes against one or more models
python scout/atlas_scout.py registers.json anthropic/claude-opus-4.8 openai/gpt-5.4 --runs 2

# score the markers, then verify + emit data/benchmark/markers.json
python scout/run_markers.py --judge google/gemini-2.5-flash
python scout/adjudicate_markers.py
```
