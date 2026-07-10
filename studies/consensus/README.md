# consensus — which models give answers the field doesn't?

Study #4 on the [modelun harness](../../README.md). Measures **answer-choice surprisal** (the blog
post calls it the **Mustard Quotient**): on prompts with a wide space of valid short answers
("Name a color."), does a model pick what everyone picks
(blue) or something the field doesn't (crimson)? The deliverable is a per-model **uniqueness scorecard**
on the *generative-defaults* axis — the open-world twin of CAIS's forced-choice
[values dashboard](https://values.safe.ai) (which measures what models *prefer*; we measure what they
*produce*; grok is an outlier there and a conformist here, so the constructs demonstrably differ).

Like [`language`](../language/), this is runner + analysis with the grading slot left open — no
codebook, no judge. The analysis is **fully mechanical**: exact-match on normalized one-word answers.
No embeddings, no LLM anywhere in the loop. A junk guard drops non-answers (chat-template artifacts,
reasoning-leak essays, bare acknowledgments like "Okay.") as failed cells rather than scoring them.

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
- [`spec/models.json`](spec/models.json) — 44 models: US frontier (multi-generation), Chinese labs,
  enterprise, search-tuned, persona/roleplay, small open, plus an expansion wave of heirloom
  retro-tests and generation fillers (gpt-4o, gpt-4-turbo, wizardlm-2, sonnet-4.6, …). The
  **deepseek lineage**
  (v3-0324 → v3.2 → v4-flash, + r1) is a deliberate sub-experiment: v3.2 was the pilot's lone genuine
  outlier (25% novel) — is the explorer property lineage-stable or version-specific?

## Run

```bash
source ../../.venv/bin/activate     # OPENROUTER_API_KEY in ../../.env

# generate: all models in parallel (per-model processes; ~120 one-word calls each)
cat spec/models.txt | xargs -P 11 -I{} python ../../harness/run.py --study . --runs 4 {}

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
