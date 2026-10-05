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
- [`spec/models.json`](spec/models.json) — 105 models (the paper's 44 + waves 2-4, below): US frontier (multi-generation), Chinese labs,
  enterprise, search-tuned, persona/roleplay, small open, plus an expansion wave of heirloom
  retro-tests and generation fillers (gpt-4o, gpt-4-turbo, wizardlm-2, sonnet-4.6, …). The
  **deepseek lineage**
  (v3-0324 → v3.2 → v4-flash, + r1) is a deliberate sub-experiment: v3.2 was the pilot's lone genuine
  outlier (25% novel) — is the explorer property lineage-stable or version-specific?

Other batteries, each with its own spec, transcripts and scoring (`analyze.BATTERIES`):

- **Expanded** ([`spec/stimulus_expanded.json`](spec/stimulus_expanded.json), `transcripts-expanded/`): 65
  more categories, 8 runs, scored like the census.
- **Brands** ([`spec/stimulus_brands.json`](spec/stimulus_brands.json), `transcripts-brands/`): 37 brand
  categories ("Name a soda brand. Reply with the name only."), 8 runs, as served. Scored by whole name with variant merging ([`brands.py`](brands.py)), not by last word.
  [`spec/stimulus_brands_ext.json`](spec/stimulus_brands_ext.json) (`transcripts-brands-ext/`, 2026-10-02) adds
  four: coffee brand, skincare, project-management tool, mobile carrier. `--battery brands_all` scores the 41
  together. The 25 hybrid models' reasoning-off runs are in
  `transcripts-brands-off/` and `transcripts-brands-ext-off/`.
- **Choose** ([`spec/perturb/`](spec/perturb/), `transcripts-choose/`, `transcripts-expanded-choose/`): the census
  and expanded questions with "Choose" for "Name" ("Choose a fruit"), a pick rather than an example. 8 runs, 102
  models, scored as the census; `probe_choose.py` compares the two verbs. The 41 brand questions were asked the
  same way (`transcripts-brands-choose-clamp/`, `transcripts-brands-ext-choose-clamp/`, `--battery choose_brands_all`); the
  consensus brand changes in 6 of 41 (Facebook to Instagram, Chrome to Firefox, Siri to Claude, Trello to Asana,
  Heineken to Guinness, Venmo to PayPal). `spec/perturb/` also holds the
  14-model prompt-perturbation check (`probe_perturb.py`: a generic system prompt, a named identity, the verb).
- **The census at other settings**: `transcripts-off/` (8 runs, reasoning off) and
  `transcripts-extra/` (4 more runs at default) use the frozen 31-category spec.

## Runs

[`spec/runs.json`](spec/runs.json) lists every transcript directory: its battery, the form of the question, whether
the answer was clamped to one word, the reasoning arm, the models, the runs and the tier. `check_runs.py` checks each
entry against the files and writes the table below (`--index`). Refer to a run by its id; directory names may change,
except for the three a published paper reports. Arms: `served` is as the endpoint serves it; `off` is reasoning off
where the endpoint allows it, with reasoning-only models as served.

<!-- runs:start -->
**core**

| id | directory | battery | form | wording | arm | models | runs |
|---|---|---|---|---|---|---|---|
| census | `transcripts/` (published) | census (31) | name | clamped | served | panel (105) | 4 |
| census-extra | `transcripts-extra/` | census (31) | name | clamped | served | panel (102) | 4 |
| census-off | `transcripts-off/` | census (31) | name | clamped | off | panel (74) | 8 |
| expanded | `transcripts-expanded/` | expanded (65) | name | clamped | served | panel (102) | 8 |
| expanded-off | `transcripts-expanded-off/` | expanded (65) | name | clamped | off | hybrids (25) | 8 |
| brands | `transcripts-brands/` | brands (37) | name | clamped | served | panel (102) | 8 |
| brands-off | `transcripts-brands-off/` | brands (37) | name | clamped | off | hybrids (25) | 8 |
| brands-ext | `transcripts-brands-ext/` | brands (4) | name | clamped | served | panel (101) | 8 |
| brands-ext-off | `transcripts-brands-ext-off/` | brands (4) | name | clamped | off | hybrids (25) | 8 |
| brands-ext2 | `transcripts-brands-ext2/` | brands (3) | name | clamped | served | panel (101) | 8 |
| brands-ext2-off | `transcripts-brands-ext2-off/` | brands (3) | name | clamped | off | hybrids (25) | 8 |

**extended**

| id | directory | battery | form | wording | arm | models | runs |
|---|---|---|---|---|---|---|---|
| census-choose | `transcripts-choose/` | census (31) | choose | clamped | served | panel (102) | 8 |
| expanded-choose | `transcripts-expanded-choose/` | expanded (65) | choose | clamped | served | panel (102) | 8 |
| brands-choose | `transcripts-brands-choose-clamp/` | brands (37) | choose | clamped | served | panel (101) | 8 |
| brands-choose-off | `transcripts-brands-choose-clamp-off/` | brands (37) | choose | clamped | off | hybrids (25) | 8 |
| brands-ext-choose | `transcripts-brands-ext-choose-clamp/` | brands (4) | choose | clamped | served | panel (101) | 8 |
| brands-ext-choose-off | `transcripts-brands-ext-choose-clamp-off/` | brands (4) | choose | clamped | off | hybrids (25) | 8 |
| brands-ext2-choose | `transcripts-brands-ext2-choose-clamp/` | brands (3) | choose | clamped | served | panel (99) | 8 |
| brands-ext2-choose-off | `transcripts-brands-ext2-choose-clamp-off/` | brands (3) | choose | clamped | off | hybrids (25) | 8 |
| brands-choose-free | `transcripts-brands-choose-free/` | brands (41) | choose | free | served | panel (101) | 4 |
| brands-choose-free-off | `transcripts-brands-choose-free-off/` | brands (41) | choose | free | off | hybrids (25) | 4 |
| brands-recommend-clamp | `transcripts-brands-recommend-clamp/` | brands (41) | recommend | clamped | served | panel (101) | 8 |
| brands-recommend-clamp-off | `transcripts-brands-recommend-clamp-off/` | brands (41) | recommend | clamped | off | hybrids (25) | 8 |
| brands-recommend-free | `transcripts-brands-recommend-free/` | brands (41) | recommend | free | served | panel (101) | 4 |
| brands-recommend-free-off | `transcripts-brands-recommend-free-off/` | brands (41) | recommend | free | off | hybrids (25) | 4 |
| brands-pick1-clamp | `transcripts-brands-pick1-clamp/` | brands (41) | pick1 | clamped | served | panel (101) | 8 |
| brands-pick1-clamp-off | `transcripts-brands-pick1-clamp-off/` | brands (41) | pick1 | clamped | off | hybrids (25) | 8 |
| brands-pick1-free | `transcripts-brands-pick1-free/` | brands (41) | pick1 | free | served | panel (101) | 4 |
| brands-pick1-free-off | `transcripts-brands-pick1-free-off/` | brands (41) | pick1 | free | off | hybrids (25) | 4 |
| brands-pick2-free | `transcripts-brands-pick2-free/` | brands (41) | pick2 | free | served | panel (101) | 4 |
| brands-pick2-free-off | `transcripts-brands-pick2-free-off/` | brands (41) | pick2 | free | off | hybrids (25) | 4 |
| brands-ext2-choose-free | `transcripts-brands-ext2-choose-free/` | brands (3) | choose | free | served | panel (99) | 4 |
| brands-ext2-choose-free-off | `transcripts-brands-ext2-choose-free-off/` | brands (3) | choose | free | off | hybrids (25) | 4 |
| brands-ext2-recommend-free | `transcripts-brands-ext2-recommend-free/` | brands (3) | recommend | free | served | panel (99) | 4 |
| brands-ext2-recommend-free-off | `transcripts-brands-ext2-recommend-free-off/` | brands (3) | recommend | free | off | hybrids (25) | 4 |
| brands-ext2-recommend-clamp | `transcripts-brands-ext2-recommend-clamp/` | brands (3) | recommend | clamped | served | panel (99) | 8 |
| brands-ext2-recommend-clamp-off | `transcripts-brands-ext2-recommend-clamp-off/` | brands (3) | recommend | clamped | off | hybrids (25) | 8 |
| brands-ext2-pick1-free | `transcripts-brands-ext2-pick1-free/` | brands (3) | pick1 | free | served | panel (99) | 4 |
| brands-ext2-pick1-free-off | `transcripts-brands-ext2-pick1-free-off/` | brands (3) | pick1 | free | off | hybrids (25) | 4 |
| brands-ext2-pick1-clamp | `transcripts-brands-ext2-pick1-clamp/` | brands (3) | pick1 | clamped | served | panel (99) | 8 |
| brands-ext2-pick1-clamp-off | `transcripts-brands-ext2-pick1-clamp-off/` | brands (3) | pick1 | clamped | off | hybrids (25) | 8 |
| brands-ext2-pick2-free | `transcripts-brands-ext2-pick2-free/` | brands (3) | pick2 | free | served | panel (99) | 4 |
| brands-ext2-pick2-free-off | `transcripts-brands-ext2-pick2-free-off/` | brands (3) | pick2 | free | off | hybrids (25) | 4 |

**check**

| id | directory | battery | form | wording | arm | models | runs |
|---|---|---|---|---|---|---|---|
| census-temp0 | `transcripts-temp0/` (published) | census (31) | name | clamped | temp0 | panel (95) | 4 |
| clamp | `transcripts-clamp/` (published) | census (10) | name | both | served | panel (105) | 4 |
| clamp-ext | `transcripts-clamp-ext/` | mixed (25) | name | both | served | panel (101) | 4 |
| free-all | `transcripts-clamp-free/` | mixed (98) | name | free | served | panel (101) | 4 |
| free-brands-ext | `transcripts-clamp-free-brands-ext/` | brands (4) | name | free | served | panel (101) | 4 |
| free-brands-ext2 | `transcripts-clamp-free-brands-ext2/` | brands (3) | name | free | served | panel (99) | 4 |

**probe**

| id | directory | battery | form | wording | arm | models | runs |
|---|---|---|---|---|---|---|---|
| perturb-base | `transcripts-perturb/base/` | census (31) | name | clamped | served | subset (14) | 8 |
| perturb-choose | `transcripts-perturb/choose/` | census (31) | choose | clamped | served | subset (14) | 8 |
| perturb-ava | `transcripts-perturb/ava/` | census (31) | name+persona | clamped | served | subset (14) | 8 |
| perturb-sysgen | `transcripts-perturb/sysgen/` | census (31) | name+system | clamped | served | subset (14) | 8 |
| perturb-recommend2 | `transcripts-perturb/recommend2/` | brands (41) | recommend | free | off | subset (14) | 4 |
| perturb-recommend3 | `transcripts-perturb/recommend3/` | brands (41) | recommend | free | off | subset (14) | 4 |
| realism | `transcripts-realism/` | brands (10) | name+recommend | both | served | subset (14) | 8 |
| brands-lang-pilot | `transcripts-brands-lang-pilot/` | brands-lang (44) | name | clamped | off | subset (105) | 8 |

**local**

| id | directory | battery | form | wording | arm | models | runs |
|---|---|---|---|---|---|---|---|
| local-census | `transcripts-local/census/` | census (31) | name | clamped | served | subset (3) | 8 |
| local-expanded | `transcripts-local/expanded/` | expanded (65) | name | clamped | served | subset (1) | 8 |
| local-brands | `transcripts-local/brands/` | brands (37) | name | clamped | served | subset (1) | 8 |
| local-choose | `transcripts-local/choose/` | census (31) | choose | clamped | served | subset (1) | 8 |
| local-expanded-choose | `transcripts-local/expanded-choose/` | expanded (65) | choose | clamped | served | subset (1) | 8 |
<!-- runs:end -->

Scoring is v3 (2026-10-01): `analyze.clean()` strips reasoning and chat-template wrappers and takes the first line that is an answer, accents fold, compound names in a few categories stay whole, and `answer_variants.json` merges spelling and naming variants in the census and expanded batteries, after a category-by-category review. v2's numbers reproduce from the `consensus-arxiv-v2` tag. Every battery's headline is as served (settled 2026-10-04): each route's default reasoning, which is what users get. The 25 hybrids (models that accept reasoning off and reason by default, listed in `spec/runs.json`) also have a reasoning-off arm in each battery, in the `-off` directories; reasoning measurably moves their answers on the expanded, pickword and brand batteries. The newer batteries cover 102 of the 105 census models; three (Claude 3 Haiku, Granite 4.1 8B, Hermes 4 70B) have no endpoint any more. Sonar was retired from the panel on 2026-10-02 (`not_run_after` in `spec/models.json`) and is absent from batteries run after that date.

## Waves

- **Wave 1 (July 2026, 44 models)** — the arXiv panel; pinned at tag `consensus-arxiv-v2`.
- **Wave 2 (2026-09-03, +25 models)** — the current cross-study roster
  appended: Fable 5.1, Opus 5, Gemini 3.8 Flash / 3.1 Flash Lite, Grok 4.6, Llama 4 Scout, GPT-OSS
  120B/20B, DeepSeek V4 Pro, Qwen 3.5/3.6/3.8, Kimi K3, GLM-5.3 (+Flash), MiniMax M3, Step 3.7 Flash,
  Gemma 4 (31B, 26B-A4B), Nemotron 3 Nano, Mistral Small 3.2 / Nemo, Hermes 3 405B. Same frozen
  stimulus, same 4 runs; leave-one-out scores are against the 69-model field, so wave-1 numbers here
  differ slightly from the paper's. Not served on OpenRouter, so not run: Mythos 5, Grok 4.1 Fast.
  Dropped after running: Hermes 3 70B (host returns essays, 1 valid answer in 124). Llama 4 Scout is
  pinned to DeepInfra (`--provider`) because Google's route truncates the first characters of replies.
  Residual failed cells (empty content after retries): Step 3.7 Flash 9/124, Qwen3.5 9B 4/124.
  **+1 (2026-09-04): GPT-6 Astra**, released that day, run as part of the wave (`openai/gpt-6-astra`;
  the Pro variant is not run, matching the base-only 5.6 rows). 1.40 bits, consensus-fixed, 1%
  novel — the GPT 5.4/5.5/luna profile, not the sol/terra one. Its off-modal defaults are the
  lineage's house answers (mango, canada, tennis, tea, triceratops, gardening, mustard); none of
  sol/terra's odd picks (prague, octopus, penguin, swahili, phoenix) survive. Same-day n=8
  re-snapshot of the three 5.6 variants (`recheck.py` → `probes/recheck_2026-09-04.json`, scored
  against the frozen wave-1 field): sol 2.02 → 2.01 and luna 1.52 → 1.57 hold; terra 1.86 → 1.66,
  with 4 of its 8 moved categories landing on the field modal (elephant, ketchup, gardening,
  dragon). Against that same field Astra reads 1.37, luna 1.52 (July) / 1.57 (today), 5.5 1.39,
  5.4 1.40. So Astra is not a Fable-5.1-style snap to the mode; it is the lineage's pre-sol/terra
  baseline, and the 5.6 → Astra drop is within the luna CI. The one drift is terra's.
- **Wave 3 (2026-09-25, +16 models)** — the atlas gap fill, completing the frontier-lab families:
  Opus 4.1, 4.5, 4.6, 4.7, 5.5, Sonnet 4.5, GPT-5.4 mini, GPT-6 Sol and Luna, Grok 4.7, Gemini 2.5
  Pro, 3 Flash Preview, 3.6 Flash, Kimi K2, Qwen3.7 Plus, Muse Spark 1.3. Same frozen stimulus, 4
  runs, no failed cells; 86 models in `analysis.json`. Per-call usage with USD cost is stored in the
  transcripts from this wave on (the wave cost $1.29). Muse Spark needs an 18+ attestation on the
  OpenRouter account. Placement: every Opus from 4.5 through 4.8 sits in the bottom eight (Opus 4.5
  last of 86), where Opus 4.1 sits at the median, and Opus 5.5 (1.43) is fixed on answers of its own
  (lantern, Japan) rather than the field's. Gemini 2.5 Pro and 3 Flash Preview rank 10th and 8th;
  the later 3.6 Flash ranks 76th. Muse Spark ranks 83rd.
- **Sonnet 5.5 (2026-09-28, +1 model)** — appended on its release day. Same frozen stimulus, 4 runs,
  no failed cells; 87 models in `analysis.json`. It ranks 13th of 87 (surprisal 2.13, CI
  [1.54, 2.72]), where Sonnet 5 ranks 85th (0.99). It holds the modal answer on every peaked category
  (oak, hammer, rose) and leaves it on the diffuse ones: lantern for any_word on all four runs (the
  word Opus 5.5 also fixes on), otter, griffin, dragonfly, Lisbon, lemonade or tea.
- **GPT-6.1 Sol (2026-09-29, +1 model)** — appended on its release day. Same frozen stimulus, 4
  runs, no failed cells; 88 models in `analysis.json`. It ranks 85th of 88 (surprisal 1.04), below
  GPT-6 Sol and Astra (both 1.31). The temperature-0 and unclamped runs were collected the same day.
  The route ignores temperature (`probes/temp0.json`: self-distinctness 0.32 at temperature 1 and
  0.35 at 0), and in free prose it avoids the field's modal word on 35% of replies.
- **Open-weight lineages (2026-09-29, +5 models)** — Nemotron 3.5 Lightning, Nemotron 3 Super
  120B and Ultra 550B, Hermes 4 405B and Qwen3.8 27B, appended to extend the NVIDIA, Hermes and
  Qwen lines. Same frozen stimulus, 4 runs, no failed cells after re-collecting the empty replies
  at `--max-tokens 8192`; 93 models in `analysis.json`. The temperature-0 and unclamped runs were
  collected the same day. Within one open pipeline, concentration rises with size: Nemotron 3 Nano
  30B 1.74 bits (30th), Lightning 1.65 (34th), Super 1.35 (59th), Ultra 1.27 (71st). Hermes 4 405B
  ranks 13th (2.15) where the departed 70B ranked 1st (3.43), so the line stays in the divergent
  third without the 70B's scatter, and at temperature 0 it collapses to 1.59. Qwen3.8 27B (1.55,
  41st) sits well above its 2.4T sibling (1.07, 88th). Hermes 4 70B and Granite 4.1 8B no longer
  have OpenRouter endpoints.
- **Mistral Small 2603 (2026-09-29/30, +1 model)** — appended with the open-weight wave; Mistral's
  upstream rate limit on OpenRouter's shared key returned 429s through the night, and the missing
  cells were collected on 2026-09-30 through the study author's own Mistral key (BYOK). No failed
  cells; 94 models. It ranks 6th (2.69 bits), above Small 3.2 (2.08, 18th) and beside Nemo (3.01)
  and Mixtral 8x22B (2.86): the newest Mistral stays divergent. At temperature 0 it collapses to
  1.65, the persona-tail pattern.
- **Wave 4 (2026-10-02, +11 models)** — Hermes 3 Llama 3.1 70B rejoins (DeepInfra now answers one-word
  prompts cleanly), Granite 4.2 8B and 30B, Inkling and Inkling-Small (Thinking Machines), Seed 2.0 Pro,
  MiMo V2.6 Pro, Ling 3.0 Flash, Phi-4, Muse Glimmer 30B and Hy4 Preview. Three are served by DeepInfra
  directly (`run.py --host deepinfra`): Hermes 3 70B, Granite 4.2 30B and Seed 2.0 Pro. All batteries plus
  pickword ran the same day; 105 models in `analysis.json`. Phi-4 ranks 1st (4.63 bits, 30% novel answers:
  "Lacrosse", "Olympics", "N/A"), above Hermes 4 70B. The new labs sit in the concentrated half: Seed 2.0
  Pro 1.13 (95th), Inkling 1.27, MiMo 1.27, Ling 1.32. Existing models' scores move negligibly with the
  larger field (r=0.9995).
- **Unclamped check (`probe_clamp.py`, data 2026-07, rank check added 2026-09-10)** — the study's own
  free-prose control: 10 categories asked bare, no clamp, all 44 wave-1 models. Field level: the
  clamped modal word appears in free replies at about the clamped share (oak 92% vs 93%, rose
  90/85, blue 76/76; bird and country lower), so the clamp extracts the mode rather than creating
  it. Model level: a model's share of free replies that avoid the modal word rank-correlates with
  its clamped census surprisal at Spearman 0.61 (n=44, p<0.001) — the divergent tail (hermes,
  wizardlm, mixtral) avoids the mode in prose 60–68% of the time, the conformist tail 15–30%. The
  effect exists without the clamp and the ranking mostly survives it. This is the census's
  validation; the convergence cross-check below is corroboration.
  **At full scale (2026-10-02):** every census, expanded and brand category (137) asked free on the live
  panel (`transcripts-clamp-free/`, `transcripts-clamp-ext/`, `transcripts-clamp-free-brands-ext/`). Free
  replies are scored by first mention among the category's answers (whole-word regex, plurals, brand
  aliases). Per model, Spearman 0.58 (n=105, p<0.0001), so the ranking survives. Per category, clamped and
  free modal shares correlate at 0.80; 53 categories hold within 5 points, 26 strengthen by more than 5,
  and 58 weaken by more than 5, 30 of them by 15 or more. The weakening is concentrated in name categories, where the one-word instruction favours the
  most famous one-word name: painter is Picasso 59% clamped and 3% free, where Vincent van Gogh leads.
  Brand answers hold without the clamp.
- **Construct check vs open-ended convergence (`probe_convergence_xval.py`, 2026-09-07)** — census
  surprisal against the convergence study's embedding `uniqueness` (free-prose replies, 9 prompts)
  over the 18 shared models: Spearman 0.41 (p=0.09); 0.64 (p=0.007) without ernie, convergence's
  verbosity outlier. The sampling-spread proxies agree far better (self_distinct vs
  1−self_consistency: 0.71). Read: the census's *ranking* carries over to open text, moderately;
  the convergence study is a weak criterion (9 prompts, verbosity-sensitive embeddings), so this
  is not a validation, it is the absence of a contradiction. A human-labeled open-ended
  companion remains the real test (`../suggestibility/README.md` § Waves for the same gap there).
- **Drift check (`recheck.py <label>...`)** — generic form of the Fable re-snapshot: n=8 today,
  scored next to the model's transcript against the wave-1 field, per-category DRIFT flags.
  Run it before reading any wave-1-vs-today comparison as a release effect; the Opus 5
  suggestibility swing (`../suggestibility/README.md` § Waves) shows an unchanged id can move.
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
- **Serendipity across a post-training ladder (`probe_olmo_ladder.py`, `probe_olmo_data.py`,
  2026-09-28)**. The test is whether SFT, preference tuning and RL put serendipity into any_word.
  OLMo 3 7B publishes every stage of one pipeline, so each stage was sampled locally 50 times at
  temperature 1 (`probes/olmo_ladder/`, summary in `probes/olmo_ladder.json`). No stage picks it. Under the model's own chat template
  the counts are SFT 2/50, DPO 1/50 and RL 0/50. Without the template's default system prompt all
  three are 0/50, and the base model in completion framing is 0/46. The upper 95% bounds are 7–13%,
  against 61% for 2026 H2 releases. Post-training does narrow the answers. The base model scatters
  (5.3 bits over 50 samples), and SFT, DPO and RL settle on a small set of pleasant nature words:
  sky, ocean, star, sunshine. Most of the narrowing happens at DPO (4.9 → 4.4 bits), and RL adds
  none. The training data carries a weak lean toward the word (`probes/olmo_data.json`). In the DPO
  set it appears 0.44 times per million words in chosen responses and 0.13 in rejected ones (29
  pairs chosen-only against 6 rejected-only, sign test p = 1e-4). None of the 329 short
  pick-a-word DPO pairs has it on either side. In the SFT set's synthetic tool-use conversations,
  serendipity is the word a "random word" tool returns most often (21 times, next ephemeral and
  apple at 7). Read: in this pipeline the stages produce the class of charming words but not the
  word itself, and RL does not collapse onto it. This fits serendipity arriving through data
  distilled from frontier models, as with Hermes 3, more than through the stages themselves. One
  7B pipeline at n=50 is a characterization. The raw-completion control is uninformative for the
  instruct stages, which mostly end the turn at once (26–35 valid of 50).
- **The full census across the same ladder (`probe_olmo_census.py`, 2026-09-28)**. Each OLMo 3 7B
  stage answered all 31 categories 20 times at temperature 1 (`probes/olmo_census/`, Contract A),
  scored as the panel is scored (`analyze.answers()`, v3) against the 94-model field
  (`probes/olmo_census.json`). Surprisal falls 4.92 (base) → 2.67 (SFT) → 2.34 (DPO) → 2.11 (RL).
  Modal share rises 0.28 → 0.49 → 0.54 → 0.56, and the stage's own entropy falls 2.92 → 1.59 →
  1.29 → 1.05. Conformity and diversity loss move together at every stage, so this model gives no
  sign that they are separate processes. The base → SFT step is inflated by the base model's
  completion framing (truncations such as "new" for New York). The final model's 2.11 sits with
  the lightly tuned open models (Llama 3.3 2.06, Qwen 2.5 72B 2.00, MythoMax 2.34), not with
  the frontier (Claude Sonnet 5 0.98, GPT-5 1.26); the field median is 1.49.

## Run

New batteries start the hybrids and these long-reasoning models at `--max-tokens 8192` rather than retrying
after a cut-off at 1024: Step 3.7 Flash, Muse Glimmer 30B, GLM 5.3 Flash, Muse Spark 1.3 (reasoning-only), and the
hybrids that run long as served (the Qwen 3.5 and 3.6 models, Qwen 3.7 Plus, Nemotron 3.5 Lightning, GLM 4.7,
Hy4 Preview, Granite 4.2 8B). They stay as served, like every model (decided 2026-10-04). Models marked
`not_run_after` in `spec/models.json` are skipped.

```bash
source ../../.venv/bin/activate     # OPENROUTER_API_KEY in ../../.env

# generate: all models in parallel (per-model processes; ~120 one-word calls each)
# -P sets concurrency; tune to your CPU / provider rate limits
cat spec/models.txt | xargs -P 8 -I{} python ../../harness/run.py --study . --runs 4 {}

# analyze: transcripts -> analysis.json + ranked scorecard on stdout
python analyze.py
python analyze.py --battery brands    # -> analysis_brands.json (also: expanded)

# review site: index.html (the 96 census and expanded questions, 8 runs), ?set=choose (the 96 with "Choose");
# ?set=brands and ?set=brands-choose only after --battery brands / brands-choose (not deployed)
python views/build.py
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
