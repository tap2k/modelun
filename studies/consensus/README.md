# consensus — which models give answers the field doesn't?

Study #4 on the [modelun harness](../../README.md). Measures **answer-choice surprisal** (the blog
post calls it the **Mustard Quotient**): on prompts with a wide space of valid short answers
("Name a color."), does a model pick what everyone picks
(blue) or something the field doesn't (crimson)? The deliverable is a per-model **uniqueness scorecard**
on the *generative-defaults* axis — the open-world twin of CAIS's forced-choice
[values dashboard](https://values.safe.ai) (which measures what models *prefer*; we measure what they
*produce*; grok is an outlier there and a conformist here, so the constructs demonstrably differ).

Like [`gujarati`](../gujarati/), this is runner + analysis with the grading slot left open — no
codebook, no judge. The analysis is **fully mechanical**: exact-match on normalized one-word answers.
No embeddings, no LLM anywhere in the loop. A junk guard drops non-answers (chat-template artifacts,
reasoning-leak essays, bare acknowledgments like "Okay.") as failed cells rather than scoring them.

**Published pin:** the paper is [arXiv:2607.12796](https://arxiv.org/abs/2607.12796); the live v2
(revised 2026-07-25) derives from the repo at tag `consensus-arxiv-v2`, v1 (submitted 2026-07-14)
from `consensus-arxiv-v1`. The roster
and analysis on `main` may move past these; the tags do not.

## The metric

For each category, pool every *other* model's answers into a distribution, then score each of this
model's answers by **surprisal** `-log2 P(answer | field)`, leave-one-out, add-one smoothed. Companions:

- **modal-avoidance** — how often it dodges the field's #1 answer
- **novel-rate** — how often it says something *no* other model ever said (the strongest tell)
- **self-distinctness** — distinct answers / runs (within-model spread)

The surprisal × self-distinctness median split types every model: **true-contrarian** (stable
*different* defaults) / **explorer** (samples off-modal) / **consensus-fixed** / **consensus-sampler**.
Entropy is an *axis* here, not a confound.

## Why one-word answers (vs. the convergence study's no-clamp rule)

[`convergence`](../convergence/) measures *naked defaults*, so it forbids format instructions. Here the
datum is the **discrete choice** — phrasing is discarded — and the clamp is identical for every model,
so it cannot differentiate them. The clamp is what makes the metric **verbosity-immune by
construction**: the pilot's embedding metric ranked ernie-4.5 #1-unique on what turned out to be pure
word count; under one-word answers ernie fell to *dead last* (0% novel). That inversion is the metric's
validation (full history: [`../convergence/OBSERVATIONS.md`](../convergence/OBSERVATIONS.md)).

## Spec

- [`spec/stimulus.json`](spec/stimulus.json) — 31 categories, single-turn, no system prompt, frozen.
- [`spec/models.json`](spec/models.json) — 69 models (the paper's 44 + wave 2, below): US frontier (multi-generation), Chinese labs,
  enterprise, search-tuned, persona/roleplay, small open, plus an expansion wave of heirloom
  retro-tests and generation fillers (gpt-4o, gpt-4-turbo, wizardlm-2, sonnet-4.6, …). The
  **deepseek lineage**
  (v3-0324 → v3.2 → v4-flash, + r1) is a deliberate sub-experiment: v3.2 was the pilot's lone genuine
  outlier (25% novel) — is the explorer property lineage-stable or version-specific?

## Waves

- **Wave 1 (July 2026, 44 models)** — the arXiv panel; pinned at tag `consensus-arxiv-v2`.
- **Wave 2 (2026-09-03, +25 models)** — the current quorum roster (`~/Desktop/projects/LLM_REGISTRY.md`)
  appended: Fable 5.1, Opus 5, Gemini 3.8 Flash / 3.1 Flash Lite, Grok 4.6, Llama 4 Scout, GPT-OSS
  120B/20B, DeepSeek V4 Pro, Qwen 3.5/3.6/3.8, Kimi K3, GLM-5.3 (+Flash), MiniMax M3, Step 3.7 Flash,
  Gemma 4 (31B, 26B-A4B), Nemotron 3 Nano, Mistral Small 3.2 / Nemo, Hermes 3 405B. Same frozen
  stimulus, same 4 runs; leave-one-out scores are against the 69-model field, so wave-1 numbers here
  differ slightly from the paper's. Not served on OpenRouter, so not run: Mythos 5, Grok 4.1 Fast.
  Dropped after running: Hermes 3 70B (host returns essays, 1 valid answer in 124). Llama 4 Scout is
  pinned to DeepInfra (`--provider`) because Google's route truncates the first characters of replies.
  Residual failed cells (empty content after retries): Step 3.7 Flash 9/124, Qwen3.5 9B 4/124.
- **Fable 5 → 5.1 (2026-09-04)** — the headline wave-2 movement. Against the frozen wave-1 field
  Fable 5.1 scores 1.25–1.32 bits vs Fable 5's 1.71; a same-day n=8 re-snapshot of both
  (`probe_fable51.py` → `probes/resnapshot_fable.json`, scored by `analyze_fable51.py`) puts Fable 5
  at 1.78, so Fable 5 has not drifted — the drop is the release. In 9 of 31 categories 5.1 abandons
  Fable 5's off-modal default and lands exactly on the field modal (gouda→cheddar, mustard→ketchup,
  velvet→cotton, copper→iron, tokyo→paris, robin→sparrow, stegosaurus→tyrannosaurus,
  photography→gardening, curiosity→joy); the other off-modal defaults (mango, sapphire, butterfly,
  phoenix, tango, basketball) survive. Self-distinctness is at the floor for both, so this is a
  change of defaults, not of sampling. The paper read Fable 5's divergence as a possible first
  sighting of a turn toward diversity; 5.1 walks half of it back. This is the series to keep running.

## Run

```bash
source ../../.venv/bin/activate     # OPENROUTER_API_KEY in ../../.env

# generate: all models in parallel (per-model processes; ~120 one-word calls each)
# -P sets concurrency; tune to your CPU / provider rate limits
cat spec/models.txt | xargs -P 8 -I{} python ../../harness/run.py --study . --runs 4 {}

# analyze: transcripts -> analysis.json + ranked scorecard on stdout
python analyze.py
```

Known limits: temperature=1.0 is sent to every model but **not honored uniformly**, and providers don't
document this — so we record it as a *measured* property, not a spec field: **`self_distinct` doubles as
the effective-temperature proxy** (a model whose 4 runs are near-identical is ignoring or flattening the
param; cross-check `exact_dup_rate` in the convergence study's analysis). Don't read self-distinctness as
pure personality — it's entangled with provider sampling behavior. Reasoning models may burn the token
budget thinking;
top-rank CIs need many categories to separate (categories are the cheap axis — add more before adding
models). Characterization, not measurement.

The scores are leave-one-out against this panel, so "is this just measuring the roster?" is a fair
question — [`robustness.py`](robustness.py) tests it (leave-one-family-out, balanced one-per-family
fields, random subsets; zero new calls): rankings hold (ρ = 0.989 vs shipped; top tier and
bottom stable in every draw). Details in [`OBSERVATIONS.md`](OBSERVATIONS.md).
