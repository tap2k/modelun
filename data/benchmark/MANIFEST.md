# Dataset

**38 models × 6 scenes × 2 runs.** One JSON file per model: `<model>.json` —
`{model, slug, script_version, temperature, scenes}`, where each scene is
`{register, subtitle, run_date, runs: [[{u, reply} × 4 panels] × 2 runs]}`. Plus `markers.json` — the
scored marker layer. Read a transcript with `python scout/render.py <model>` (or the site).

## Provenance
- **script_version** `5.0` — the frozen stimulus in [`../../registers.json`](../../registers.json),
  including the system-prompt clamp ("keep replies short, plain prose, no markdown").
- **runs/scene** 2 · **temperature** 1.0.
- Dated specimens: each result is true of one model version on the day it was run.

## The six scenes
TONGUE: `facts` (arithmetic hill), `bad_plan` (day-trader), `self_label` (flattering self-story).
HANDS: `doctors_note` (backdated note), `the_leap` (the all-in).
HEART: `pivot` (disclosure & pivot). Full scripts: [`../../docs/scenes.md`](../../docs/scenes.md).

## The markers
`markers.json` — per (model, scene, run): the marker value + a verbatim, string-verified trigger
quote. Judge: `google/gemini-2.5-flash`. See [`../../docs/markers.md`](../../docs/markers.md).

## The models

| Vendor | Models (slug) |
|---|---|
| Anthropic | claude-3-haiku, claude-3.5-haiku, claude-sonnet-4, claude-opus-4, claude-opus-4.5, claude-haiku-4.5, claude-sonnet-4.6, claude-opus-4.8 |
| OpenAI | gpt-3.5-turbo-instruct, gpt-3.5-turbo, gpt-4-turbo, gpt-4o, gpt-4o-mini-2024-07-18, gpt-4.1, gpt-5, gpt-5.4-mini, gpt-5.4 |
| Google | gemini-2.5-flash, gemini-2.5-pro, gemini-3-flash-preview, gemini-3.1-pro-preview, gemini-3.5-flash, gemma-2-27b-it, gemma-3-27b-it |
| Meta-Llama | llama-3-70b-instruct, llama-3.3-70b-instruct, llama-4-scout, llama-4-maverick |
| Qwen | qwen3-235b-a22b-2507, qwen3-235b-a22b-thinking-2507, qwen3.7-plus |
| Other | grok-4.3 (x-ai), deepseek-r1, kimi-k2 (moonshotai), command-r-plus-08-2024 (cohere), mixtral-8x22b-instruct (mistralai), hermes-3-llama-3.1-70b (nousresearch), mythomax-l2-13b (gryphe) |

## How to read it
Across a scene (same beat, whole cast): who folds. Down a model (its arc over four panels): its
character. Small N — characterizations, not measurements. To regenerate or extend, see
[`../../README.md`](../../README.md) and `scout/`.
