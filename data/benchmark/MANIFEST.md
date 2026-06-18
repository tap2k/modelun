# Benchmark dataset — manifest

This is the **canonical, frozen dataset** behind [`docs/essay.md`](../../docs/essay.md) and
[`docs/method/synthesis.md`](../../docs/method/synthesis.md). Every quote in the essay and the
synthesis is verbatim from one of these 28 files. Other runs under `runs/` are disposable
working output and stay gitignored; *this* run is committed because the findings cite it.

## What's here
- **28 models × 9 scenes × 2 runs each** = 504 four-panel exchanges (2,016 model replies).
- One file per model: `scout_<model>.md`. Each is a readable markdown transcript with a header
  stamping its provenance, then the 9 scenes (`## ` headers), each with `### run 0` / `### run 1`,
  each a 4-turn user-escalation (`U1`–`U4`) with the model's reply after each.

## Provenance (stamped in every file header)
- **script_version:** `v4.1` — the frozen stimulus in [`registers.json`](../../registers.json),
  including the system-prompt **clamp** ("keep replies short, plain prose, no markdown"). Clamped
  (v4.1) and unclamped runs are **not** comparable; this whole dataset is clamped.
- **runs/scene:** 2 · **temperature:** 1.0.
- **Read date / specimen date:** 2026-06-18. These are dated specimens — each result is true of one
  model version on one day; the organisms mutate every release.

## The 28 models (provider slug in parens)

| Model (slug) | Provider route |
|---|---|
| claude-opus-4.8 | anthropic/claude-opus-4.8 |
| claude-sonnet-4.6 | anthropic/claude-sonnet-4.6 |
| claude-haiku-4.5 | anthropic/claude-haiku-4.5 |
| claude-3.5-haiku | anthropic/claude-3.5-haiku |
| gpt-5.4 | openai/gpt-5.4 |
| gpt-5.4-mini | openai/gpt-5.4-mini |
| gpt-4o | openai/gpt-4o |
| gpt-4o-mini-2024-07-18 | openai/gpt-4o-mini-2024-07-18 |
| gpt-3.5-turbo | openai/gpt-3.5-turbo |
| gpt-3.5-turbo-instruct | gpt-3.5-turbo-instruct |
| gemini-3.1-pro-preview | google/gemini-3.1-pro-preview |
| gemini-3.5-flash | google/gemini-3.5-flash |
| gemini-2.5-pro | google/gemini-2.5-pro |
| gemini-2.5-flash | google/gemini-2.5-flash |
| grok-4.3 | x-ai/grok-4.3 |
| deepseek-r1 | deepseek/deepseek-r1 |
| kimi-k2 | moonshotai/kimi-k2 |
| command-r-plus-08-2024 | cohere/command-r-plus-08-2024 |
| mixtral-8x22b-instruct | mistralai/mixtral-8x22b-instruct |
| qwen3-235b-a22b-thinking-2507 | qwen/qwen3-235b-a22b-thinking-2507 |
| qwen3-235b-a22b-2507 | qwen/qwen3-235b-a22b-2507 |
| qwen3.7-plus | qwen/qwen3.7-plus |
| llama-4-maverick | meta-llama/llama-4-maverick |
| llama-4-scout | meta-llama/llama-4-scout |
| llama-3.3-70b-instruct | meta-llama/llama-3.3-70b-instruct |
| llama-3-70b-instruct | meta-llama/llama-3-70b-instruct |
| hermes-3-llama-3.1-70b | nousresearch/hermes-3-llama-3.1-70b |
| mythomax-l2-13b | gryphe/mythomax-l2-13b |

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
All 28 files are complete: 9 scenes × 2 runs each, uniform, all stamped v4.1 / temp 1.0. No failed
or empty cells. Headers contain no secrets (system prompt + model slug only).
