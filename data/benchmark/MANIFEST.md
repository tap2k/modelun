# Benchmark dataset — manifest

This is the **canonical, committed dataset** behind [`docs/essay.md`](../../docs/essay.md) and
[`docs/method/synthesis.md`](../../docs/method/synthesis.md). Every quote in the essay and the
synthesis is verbatim from one of these files. Other runs under `runs/` are disposable working
output and stay gitignored; *this* set is committed because the findings cite it.

## The roster is additive — not a closed set
The benchmark **grows**. Models are specimens added over time, not a fixed cohort. New rungs get
pulled with the **same instrument** (`registers.json` v4.1, clamped, 2 runs/scene) and dropped in
here as `scout_<model>.md` — that's what keeps every column comparable no matter when it was added.
"How many models" is therefore a running count, not a property of the dataset. Each file's header
stamps its own read-date, and the table below records which cohort each specimen came in with.

## What's here
- **38 models × 9 scenes × 2 runs each** (and counting). One file per model: `scout_<model>.md` — a
  readable markdown transcript with a provenance header, then the 9 scenes (`## ` headers), each
  with `### run 0` / `### run 1`, each a 4-turn user-escalation (`U1`–`U4`) with the reply after each.

## Provenance (stamped in every file header)
- **script_version:** `v4.1` — the frozen stimulus in [`registers.json`](../../registers.json),
  including the system-prompt **clamp** ("keep replies short, plain prose, no markdown"). Clamped
  (v4.1) and unclamped runs are **not** comparable; this whole dataset is clamped.
- **runs/scene:** 2 · **temperature:** 1.0.
- **Dated specimens.** Each result is true of one model version on one day; the organisms mutate
  every release. Read-dates are per-cohort (see the table) — adding specimens later is expected.

## Cohorts
- **2026-06-18 — the founding 28.** The first committed roster across all major families.
- **2026-06-19 — the evo rungs (+10).** Older/intermediate generations added to fill the
  generational ladders the founding set left thin (e.g. claude-3-haiku below 3.5-haiku; gpt-4-turbo
  below gpt-4o and gpt-4.1/gpt-5 above it; gemma-2/3 and gemini-3-flash on the Google side). Same
  v4.1 instrument. These were cross-read by three independent vendors (gpt-5.4, claude-opus-4.8,
  gemini-3.1-pro) and every cited quote was string-verified against the source — **zero fabricated
  quotes across ~660 reader quotes** (see [`docs/method/synthesis.md`](../../docs/method/synthesis.md) §2).

## Instrument versions & per-scene comparability
- **v4.1** is this dataset's stimulus-of-record, archived here as
  [`registers-v4.1.json`](registers-v4.1.json) — next to the transcripts it generated — so the
  cohort stays reproducible after the root [`registers.json`](../../registers.json) advanced to v5.0.
- **v5.0** tilts the battery toward DISPOSITION (where the house-style differences live; see
  [`docs/houses.md`](../../docs/houses.md)). It **retires** two scenes that stopped discriminating —
  `confrontational/correction` (≈everyone climbs down) and `absurd/houseplant` (off-axis +
  clamp-contaminated) — and **adds** three: `complicity/the_leap`, `confiding/guilt`,
  `reassuring/self_label`. The clamp is byte-identical to v4.1.
- **Comparability is per-scene, not per-version.** The six scenes carried into v5.0 unchanged
  (arithmetic, doctor's note, confiding-pivot, day-trader, interview, vague) plus `deciding/two_offers`
  (turns unchanged; only the marker was reframed `flipped_or_hedged` → `held_a_pick`) are the **same
  experiment** as their v4.1 runs and pool directly with this dataset — they are **not** re-run on the
  existing roster. Only the three new scenes get run on the existing roster
  ([`registers_v5_new.json`](../../registers_v5_new.json)); net-new models get the full
  `registers.json`. The retired scenes' v4.1 transcripts **stay committed here** (still cited by the
  essay/synthesis). The binary/graded marker layer is specified in
  [`docs/method/markers.md`](../../docs/method/markers.md).

## The models (provider slug · cohort)

| Model (slug) | Provider route | Cohort |
|---|---|---|
| claude-3-haiku | anthropic/claude-3-haiku | 2026-06-19 (evo) |
| claude-3.5-haiku | anthropic/claude-3.5-haiku | 2026-06-18 |
| claude-haiku-4.5 | anthropic/claude-haiku-4.5 | 2026-06-18 |
| claude-opus-4 | anthropic/claude-opus-4 | 2026-06-19 (evo) |
| claude-opus-4.5 | anthropic/claude-opus-4.5 | 2026-06-19 (evo) |
| claude-opus-4.8 | anthropic/claude-opus-4.8 | 2026-06-18 |
| claude-sonnet-4 | anthropic/claude-sonnet-4 | 2026-06-19 (evo) |
| claude-sonnet-4.6 | anthropic/claude-sonnet-4.6 | 2026-06-18 |
| gpt-3.5-turbo-instruct | gpt-3.5-turbo-instruct | 2026-06-18 |
| gpt-3.5-turbo | openai/gpt-3.5-turbo | 2026-06-18 |
| gpt-4-turbo | openai/gpt-4-turbo | 2026-06-19 (evo) |
| gpt-4.1 | openai/gpt-4.1 | 2026-06-19 (evo) |
| gpt-4o | openai/gpt-4o | 2026-06-18 |
| gpt-4o-mini-2024-07-18 | openai/gpt-4o-mini-2024-07-18 | 2026-06-18 |
| gpt-5 | openai/gpt-5 | 2026-06-19 (evo) |
| gpt-5.4 | openai/gpt-5.4 | 2026-06-18 |
| gpt-5.4-mini | openai/gpt-5.4-mini | 2026-06-18 |
| gemini-2.5-flash | google/gemini-2.5-flash | 2026-06-18 |
| gemini-2.5-pro | google/gemini-2.5-pro | 2026-06-18 |
| gemini-3-flash-preview | google/gemini-3-flash-preview | 2026-06-19 (evo) |
| gemini-3.1-pro-preview | google/gemini-3.1-pro-preview | 2026-06-18 |
| gemini-3.5-flash | google/gemini-3.5-flash | 2026-06-18 |
| gemma-2-27b-it | google/gemma-2-27b-it | 2026-06-19 (evo) |
| gemma-3-27b-it | google/gemma-3-27b-it | 2026-06-19 (evo) |
| grok-4.3 | x-ai/grok-4.3 | 2026-06-18 |
| deepseek-r1 | deepseek/deepseek-r1 | 2026-06-18 |
| kimi-k2 | moonshotai/kimi-k2 | 2026-06-18 |
| command-r-plus-08-2024 | cohere/command-r-plus-08-2024 | 2026-06-18 |
| mixtral-8x22b-instruct | mistralai/mixtral-8x22b-instruct | 2026-06-18 |
| qwen3-235b-a22b-thinking-2507 | qwen/qwen3-235b-a22b-thinking-2507 | 2026-06-18 |
| qwen3-235b-a22b-2507 | qwen/qwen3-235b-a22b-2507 | 2026-06-18 |
| qwen3.7-plus | qwen/qwen3.7-plus | 2026-06-18 |
| llama-4-maverick | meta-llama/llama-4-maverick | 2026-06-18 |
| llama-4-scout | meta-llama/llama-4-scout | 2026-06-18 |
| llama-3.3-70b-instruct | meta-llama/llama-3.3-70b-instruct | 2026-06-18 |
| llama-3-70b-instruct | meta-llama/llama-3-70b-instruct | 2026-06-18 |
| hermes-3-llama-3.1-70b | nousresearch/hermes-3-llama-3.1-70b | 2026-06-18 |
| mythomax-l2-13b | gryphe/mythomax-l2-13b | 2026-06-18 |

## The 9 scenes
See [`registers.json`](../../registers.json) for the exact turns, or the appendix of
[`docs/essay.md`](../../docs/essay.md). In order: Confrontational/arithmetic-hill,
Confrontational/right-correction, Imploring/doctor's-note, Absurd/houseplant, Confiding/pivot,
Reassuring/day-trader, Reassuring/interview-jitters, Deciding/two-offers, Vague/make-it-better.

## How to read it
Read by eye, across and down. *Across* a scene (same beat, whole cast): who folds. *Down* a model
(its arc over four panels): its character. This is a read-by-eye scout, N=2 — characterizations,
not measurements. To regenerate or extend, see [`README.md`](../../README.md) and `scout/`.

## Integrity
All files are complete: 9 scenes × 2 runs each, uniform, all stamped v4.1 / temp 1.0. No failed or
empty cells. Headers contain no secrets (system prompt + model slug only). When you add a specimen,
append its row above with its cohort date and keep this line honest.
