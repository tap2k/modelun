# convergence — do frontier models give the same answer?

Study #3 on the [modelun harness](../../README.md). **Pilot has run** (22 models × 9 prompts × 3 runs:
16 US-frontier + 3 Chinese-primary + 3 persona/low-RLHF). Detailed working notes: [OBSERVATIONS.md](OBSERVATIONS.md).

> **Successor:** this pilot's methodology work (three confounds found and killed: packaging, entropy,
> verbosity) produced a clean discrete metric — answer-choice surprisal — now the flagship study at
> [`studies/surprisal/`](../surprisal/). This study remains the journey + the embedding-side results.

## TOPLINE (characterization, not measurement — small N, one day, wide CIs)

**Claim.** On open-ended prompts, models draw from a **shared, narrow answer-space that transcends lab,
alignment recipe, and country of origin.** 16 US-frontier models produce 3 distinct animals, 5 distinct
numbers, one dominant joke. Stress-tested with genuine outsiders — Chinese-primary (deepseek, ernie,
minimax) and a minimally-RLHF'd roleplay model (mythomax) — the convergence **held**: outsiders still gave
Apple, the atom joke, stock metaphors. So the homogenization is not a US-frontier-cluster artifact; it
lives in the **shared English-web training substrate** everyone draws on. **No available model is a
reliable source of genuinely different answers.** (An earlier "ernie-4.5 is the one clean content-outlier"
claim was WALKED BACK on eyeballing: ernie's distance is mostly VERBOSITY/hedging/format, not different
content — it says apple/blue/Einstein/the atom joke, just in full sentences. Text embeddings encode length/
register, so a verbose model reads as "divergent" without being original. deepseek shows more genuine
answer-choice divergence [Crimson not blue, Serendipity], but that too needs a length-controlled check.
Bottom line: no model is a CONFIRMED content outlier once verbosity is controlled — the search continues.)

**Method (the tool that got us there).** A per-model **content-uniqueness** score = distance of a model's
per-prompt centroid from the consensus centroid, embedding-based, roster-relative, **decomposed to strip
the entropy confound** (a model that merely wanders scores far from consensus without being more
original — mythomax was exactly this false positive; separating CONTENT from SPREAD killed it). No LLM in
the loop (an LLM cleaning pass was tried and dropped — it hallucinated on short inputs). Validated by
ablation (drop-a-family → Spearman 0.80–0.97), permutation (13/16 above chance), and bootstrap (only
COARSE tiers survive at N=9).

**Honest nulls / limits (equally part of the result).**
- **No convergence-over-generations** (Axis B): newer ≠ more homogenized here; open≈closed; size flat.
- **Stylistic "voice" is not cleanly measurable** with text embeddings (they entangle style/topic/
  packaging) — we can measure *content* uniqueness, not *voice*.
- **Temperature is an uncontrolled confound**: temp=1.0 sent to all, but effective sampling varies ~6x
  (Claude/Gemini near-greedy, dup-rate 0.44–0.67; open/older honestly sample, 0.11–0.22). "Self-
  consistency" is largely effective-temperature, not personality.
- N=9 prompts, ~3 runs, one day, minimax-m1 partial-fail (12 cells). Bootstrap CIs are wide; only the
  coarse pattern (deep convergence, ~no escape hatch, ernie the lone content-outlier) is firm. To sharpen,
  **add prompts, not models** (power is prompt-bound).

**Related work.** CAIS [values.safe.ai](https://values.safe.ai) (Phan/Mazeika/Blair/Hendrycks 2026)
measures the same convergence rigorously on VALUES (forced-choice → Bradley-Terry → Elo) and finds the
same divergence structure (DeepSeek→Taiwan/China, Grok→persona). We are the **generative twin** of that
values work: open-ended generation, per-model uniqueness, the temperature confound they never hit.
(Their "coherence rises with scale" = within-model coherence, NOT our null Axis-B cross-family claim.)

## The hypothesis (as stated)

As frontier models increasingly share training data and RLHF process, their answers converge and become
homogeneous — and the same shared-data story predicts foundation-vs-open-source models *diverge*.
Convergence should be **strongest for generic queries** ("tell me a joke") and weakest for queries with a
large, contested answer space.

A second prediction from the same mechanism: **later generations of a given model family converge more**
than earlier ones did — as each family trains on more of the same web + shared RLHF conventions, the
lineages should drift *toward each other over generational time*. Same cause (shared data/RLHF), read as
a time trend within lineages instead of a snapshot across them.

## The one design decision everything hangs on

**Convergence is not an absolute number — it is a slope.** "Claude and GPT agree 0.82 on *tell me a joke*"
means nothing on its own: maybe the prompt just has few good answers. `capital of France` gets identical
answers from every model, and that is a *fact*, not convergence.

So the study is a **contrast**, not a leaderboard:

> Do frontier models get *more* similar to each other *as prompts get more open-ended*, more than
> open-source models do?

Prior-strength (below) is the independent variable; model-tier is the grouping. The result is read as a
*relationship* — convergence vs. prior-strength — the same (noisy) way for every model, so the noise floor
of "cosine on open-ended text" cancels out of the comparison. Absolute cosine is uninterpretable; the
*difference* across the prior-strength span, and *between* frontier and open, is the signal.

We do **not pre-rank** prompts by an assumed prior strength and fit a slope to that ranking — that would
bake our guesses into the axis. We pick unhedgeable prompts spanning obviously-strong to obviously-diffuse
priors, measure convergence per prompt, and **let the data draw the curve** (correlate observed
convergence with observed answer-concentration). The finding is the correlation, not an asserted slope.

This framing is the whole point. It is the only version of the claim that a shared-answer-space confound
cannot explain away.

### What "generic" actually means: prior-strength, not answer-length

The independent variable is **how sharply the training data concentrates on a few expected answers** —
the *prior strength* of the query. This is the real content of the seed intuition: *"tell me a joke"
converges because the corpus is saturated with the same jokes* — the pattern is in the training data, and
all models learned the same distribution. Strong-prior imperatives (name an animal → lion, name a number →
7) should converge if the homogenization story holds; diffuse-prior ones (write a haiku) should not.

This replaces an earlier, worse gradient (generic↔specific by answer *length*), which confounded
genericness with verbosity. Prior-strength is the right axis; it also keeps answers naturally short and
self-contained, so **cosine embeds the whole answer, not a fragment of a long essay** — a requirement for
the metric to bite.

**No waffle — the hard constraint on prompt wording.** A prompt that invites hedging ("what's the *best*
X?", "what's *your favorite* X?", "*any advice*?") is disqualified, for two compounding reasons:
1. A hedged reply ("it depends, but popular options include…") embeds to a *deliberation* vector, not an
   answer vector — the metric stops measuring answer convergence.
2. Hedging is itself an **RLHF-trained register**, so frontier models hedge *more* and *more similarly* —
   a directional confound that would manufacture fake convergence on the exact arm we're testing.
Every prompt must be a **bare imperative that forces a committed short answer with zero coaxing** — the
"tell me a joke" template. No "best", no "your favorite", no "one word" clamp (the clamp is its own
confound). `analyze.py` stays pure similarity: we *prevent* waffle by design, we don't measure it.

### Two axes off one matrix

There are two contrasts, and they read off the **same per-prompt model×model similarity matrix** — no
second mechanism, just a second way to slice and plot the pairwise cosines:

- **Axis A — prior-strength × tier.** Do frontier models converge *more on strong-prior prompts* than open
  models do? Convergence measured per prompt, correlated with observed answer-concentration (not a
  pre-ranked slope). Snapshot across models.
- **Axis B — generation-time × family.** Do model *families drift toward each other over generational
  time*? x = release generation of each model; y = its mean cross-**family** similarity to the rest of the
  field. Rising = homogenization over time.

Axis B is tighter than a naive cross-family snapshot because it holds lab, house style, and product
constant and varies only training-maturity. **Precise claim to test = "later generations are more similar
to *other families*"** (homogenization), *not* the weaker "later generations are more self-consistent"
(just stability). The y-axis is cross-family similarity, plotted against generational time.

**Size and generation are separate axes — do not walk them diagonally.** Within a family you have a
(size × generation) grid. Stepping `3-haiku → sonnet-4 → opus-4.8` moves *both* at once, so a convergence
trend there is unattributable: it could be "later generation" (homogenization) or "bigger model" (bigger
models are better and better models agree more). Axis B therefore splits into two single-variable walks:

- **B1 — generation, size held ~constant.** Step generations along one size tier:
  - Claude *haiku* line: `claude-3-haiku → claude-3.5-haiku → claude-haiku-4.5`
  - Gemini *flash* line: `gemini-2.5-flash → gemini-3-flash-preview → gemini-3.5-flash`
  - GPT *small/mid* line: `gpt-3.5-turbo → gpt-4o-mini → gpt-5.4-mini`
- **B2 — size, generation held constant (the control).** Step sizes within one generation:
  - Claude gen-4: `claude-haiku-4.5` vs `claude-sonnet-4` vs `claude-opus-4.8`
  - Gemini gen-3: `gemini-3-flash-preview` vs `gemini-3.1-pro-preview`

B2 is not a side quest — it is the control that makes B1 interpretable. If cross-family similarity rises
with **size** within a fixed generation, that increment is a size effect, and B1's generational slope only
counts as homogenization to the extent it exceeds it. Report B1 net of the B2 size gradient.

## What we measure (and the free summary)

The primitive is **pairwise answer similarity**: for each prompt, a model×model matrix of how similar
each pair's answers are. Diversity/entropy is not separate work — it is the **row-mean of that matrix**.
Compute the matrix once; the per-prompt convergence number falls out.

Two numbers per prompt:

- **cross-model similarity** — mean off-diagonal of the matrix. High = models converge.
- **within-model similarity** — mean similarity across a model's *own* `runs: N` samples. This is the
  **self-consistency floor**: if a model can't reproduce itself, cross-model agreement is meaningless.
  Convergence is interesting only as cross-model similarity *rises toward* this floor.

## Similarity method — pluggable, cosine-on-embeddings first

- **Embeddings, mechanical, for the spine.** OpenAI embeddings (user is providing a key). Cosine on a
  fixed model → a matrix anyone can regenerate. No LLM-judge self-family problem (the gemini-judging-gemini
  issue `AGENTS.md` flags), no methodology argument before we've seen data.
- **Pluggable by construction.** `analyze.py` separates *embed(texts) → vectors* from *similarity(a,b) →
  score*. Both are named strategies behind a tiny interface so a later run can swap the embedding model or
  the metric (Jaccard on n-grams, LLM-judge semantic score) without touching the pipeline. Config, not fork.
- **LLM judge deferred, not rejected.** It is the right tool for "same meaning, different words," but it
  is expensive and argument-prone. Add it as a *semantic cross-check on a sample* once the embedding slope
  is worth defending. The harness judging kernel is left in the open grading slot, exactly like the
  `language` study documents.

## The pilot (one afternoon, cheap, proves or kills the signal)

Small on purpose. A pilot's job is to show the pipeline yields a *readable slope*, not to be significant.

- **~17 models — every slug verified against the conduct benchmark.** Each model carries three metadata
  fields so all cuts are *filters on one run*, never re-runs: `family`, `generation` (ordinal), `size_tier`
  (small/mid/large), plus an `open` flag. The set is built to give **B1 a size-matched generational walk,
  B2 a same-generation size walk, and Axis A an open-family breadth arm** — the same models reused across
  all three cuts.

  **B1 — generation walks (size held ~constant):**
  - Claude haiku line: `anthropic/claude-3-haiku`, `anthropic/claude-3.5-haiku`, `anthropic/claude-haiku-4.5`
  - Gemini flash line: `google/gemini-2.5-flash`, `google/gemini-3-flash-preview`, `google/gemini-3.5-flash`
  - GPT small/mid line: `openai/gpt-3.5-turbo`, `openai/gpt-4o-mini-2024-07-18`, `openai/gpt-5.4-mini`

  **B2 — size walks (generation held constant), reusing the above + adding the large tier:**
  - Claude gen-4: `claude-haiku-4.5` (from B1) + `anthropic/claude-sonnet-4` + `anthropic/claude-opus-4.8`
  - Gemini gen-3: `gemini-3-flash-preview` (from B1) + `google/gemini-3.1-pro-preview`
  - GPT gen-5: `gpt-5.4-mini` (from B1) + `openai/gpt-5.4`

  **Axis A — open-source breadth arm** (independent lineages, for frontier-vs-open):
  - `meta-llama/llama-3-70b-instruct`, `meta-llama/llama-4-maverick` (a small open depth walk too),
    `qwen/qwen3-235b-a22b-2507`, `mistralai/mixtral-8x22b-instruct`, `deepseek/deepseek-r1`,
    `moonshotai/kimi-k2`

  ~17 models × 9 prompts × 3 runs ≈ 400 generations — an afternoon, cheap on OpenRouter. The metadata
  grid (family × generation × size_tier × open) is what lets one run answer A, B1, and B2 without a re-run.
- **9 single-turn bare-imperative prompts spanning strong→diffuse prior** (table below, seeded on the joke
  example): unhedgeable and pattern-laden, each forcing a naturally short committed answer. No system
  prompt, no length clamp — each model's naked default.
- **`runs: 3` per (model, prompt)** — a single sample can't separate "models agree" from "this model said
  X once." The 3 samples give the within-model floor.
- **Offline:** embed every reply, build the per-prompt matrix, emit cross- and within-model means, plot
  both per prompt (ordered by measured convergence), split by tier.
- **Read for:** frontier cross-model similarity climbing toward its floor as prompts get generic, faster
  than open. Slope present in ~15×8 → scale N. Slope flat → hypothesis cheaply falsified.

### Prompts — bare imperatives spanning strong → diffuse prior (for your review)

Single-turn scenes in `spec/stimulus.json`. **No system prompt, no length clamp.** Every prompt is a bare,
unhedgeable imperative — the "tell me a joke" template — chosen so the model *commits* to a short answer
with no room to deliberate. The set spans obviously-strong priors ("name an X" with a sharp corpus mode)
to obviously-diffuse ones (creative imperatives). We do **not** pre-rank; convergence is measured per
prompt and the ordering emerges from the data.

**Strong-prior end** — "name an X"; the corpus has a sharp mode, so convergence is predicted:

| id | prompt | folklore mode |
|----|--------|---------------|
| `joke` | "Tell me a joke." | the seed — corpus saturated with the *same* jokes |
| `animal` | "Name an animal." | lion / dog |
| `fruit` | "Name a fruit." | apple |
| `country` | "Name a country." | France / USA |
| `number` | "Name a number." | 7 / 42 — the classic homogenization tell |

**Diffuse-prior end** — creative imperatives; committed but a vast answer space, so divergence is predicted:

| id | prompt | why diffuse |
|----|--------|-------------|
| `haiku` | "Write a haiku." | huge space; the 5-7-5 form holds length ~constant → clean embeddings, no clamp |
| `poem` | "Write a short poem." | vast space, mild length variance |
| `metaphor` | "Give me a metaphor." | open, creative, single committed line |
| `word` | "Make up a word." | invented token — near-maximal divergence anchor |

Convergence should be high on the top block and low on the bottom block **for every model**; the
*hypothesis* is that the frontier arm's top-block convergence sits higher / its top-vs-bottom gap is
wider than the open arm's. If open models converge as hard as frontier on the strong-prior block, the
homogenization story is wrong. The `word`/`haiku` end is the divergence sanity check — if *everything*
converges there, the metric isn't discriminating and the pilot has failed cleanly.

Selection rule (final): a rung is **a bare imperative · unhedgeable · pattern-laden · naturally short**.
"Tell me a joke" is the template; "what's the *best* X?" (waffle), "your *favorite* X" (premise refusal),
and long derivations (unembeddable) are all disqualified.

## What gets built (reuse-first — almost nothing is new)

| Piece | Status |
|---|---|
| `harness/run.py` | **reused as-is** — single-turn scenes are `turns: ["..."]`; `--runs 3` already supported |
| `harness/viewer/core.js` | **reused as-is** — renders the transcripts for eyeballing |
| `spec/stimulus.json` | **new, small** — flat `scenes[]`, the 9 bare-imperative prompts, no system_prompt |
| `models.json` | **new, small** — per-model `{family, generation, size_tier, open}` metadata map |
| `analyze.py` | **new — the only real code** — transcripts → embeddings → matrix → per-prompt means (JSON) |
| `views/` | **new, thin** — copy the `language` build; add the Axis-A and Axis-B plots |

`analyze.py` is the study's spine and the only file with real logic. Sketch:

```
load transcripts/*.json  →  for each prompt, collect {model: [reply per run]}
embed(all replies)        # strategy: openai-text-embedding-3-small (swappable)
for each prompt:
    within[model]  = mean pairwise cosine over that model's own runs
    cross          = mean cosine over one-sample-per-model pairs (all model pairs)
emit analysis.json:
    per-prompt {cross, within_by_model, tier_means}          # Axis A: convergence per prompt, data-ranked
    per-model  {generation, family, mean_cross_family_sim}   # Axis B: × generation time
```

`family` + `generation` are two small fields on each model in the spec (or a sidecar map) — the only
metadata Axis B needs. Cross-**family** similarity for Axis B excludes same-lineage pairs so we measure
drift *toward other families*, not within-lineage stability.

Embedding source and metric are named strategies behind one interface; the pilot wires
`openai/text-embedding-3-small` + cosine and leaves the seam for the rest.

## Honest limits (respect the AGENTS.md ethos)

- **N is small.** ~17 models × 9 prompts × 3 runs is a *pilot* — it detects a signal or its absence, not an
  effect size. Two–three generations per lineage is enough to see a trend's *direction*, not to fit a curve.
  Characterization, not measurement.
- **Prior-strength is observed, not controlled.** We span strong→diffuse by judgment and let the data rank;
  we don't independently measure each prompt's true corpus prior. The correlation is suggestive, not causal.
- **Cosine on open-ended text is noisy.** Mitigated by reading the *contrast*, not the level; stated, not
  hidden.
- **Embedding model is a lens.** text-embedding-3 has its own biases; the pluggable seam exists so a second
  embedder can check the first.
- **No LLM judge yet** — semantic "same meaning, different words" is deferred to a cross-check pass.

## Known confound: packaging vs payload (→ an LLM cleaning pass)

Real fan-out data (a 17-model "tell me a joke" export) exposed this: models that gave the **same joke**
wrapped it in different **scaffolding** — "Here's one:", "Sure! Here's a lighthearted one 😄", "Want to
hear another one?". Cosine sees the scaffolding and scores identical jokes *lower*, while the shared
helpful-register preamble (itself an RLHF-homogenized pattern — the waffle confound via packaging) can
*inflate* similarity between different answers. So raw-text cosine both **under**counts real answer
convergence and **manufactures** fake convergence from shared chrome.

Two responses, both slotting into the pluggable design as a `normalize(text) → text` stage *before*
`embed`:

1. **Modal-agreement metric** (cheap, immediate): for short pattern-laden prompts, report "fraction giving
   the plurality answer" and "# distinct answers / N" alongside cosine. On the joke export, cosine read
   0.50 but 10/17 gave the *identical* joke (59%, 5 distinct total) — the modal number is the honest one.
   Limitation: needs hand-keyed categories, doesn't scale past a hand-labeled prompt.
2. **LLM cleaning pass** (the general fix — BUILT, validated): a **purely extractive** cleaner unwraps each
   reply to its payload (strip preamble, sign-off, emoji, markdown; preserve the whole answer verbatim),
   then embed. Generic across queries — it strips *packaging*, never names the answer.

   **This step gates every downstream number, and getting it right was non-trivial:**
   - A terse instruction ("return only the direct answer") **silently corrupted data** — models read the
     "answer" to a joke as the *punchline* and dropped the setup, and mangled already-clean inputs. Only
     reading before/after caught it; no aggregate number would have.
   - `gpt-5.4-mini` (cheap) **failed** — over-edited, dropped setups. It is kept only as a negative control.
   - Fix = **stronger model + stronger prompt.** `google/gemini-3.5-flash` with a forceful, example-driven
     instruction (preserve the ENTIRE answer; be idempotent — clean input returns byte-identical; strip
     only packaging). This is the validated default.

   **Acceptance test (re-run if the cleaner model or prompt changes):** the *skeleton-joke trio* —
   gpt-5.4 (bare), mixtral (`**markdown**` + "Sure! …😄"), qwen3 ("Sure! Here's a lighthearted one 🦴😄") —
   must collapse to near-identical text, AND already-clean replies (gpt-5.4, gpt-3.5) must return
   UNCHANGED. Both now pass. Command sketch: clean those five joke replies, assert the trio matches and
   the clean ones are byte-identical.

   Caveat (AGENTS.md self-family): the cleaner **gemini-3.5-flash is itself a subject** in this study, so it
   self-cleans the gemini/gemma answers. Extractive-only + idempotence limits the damage (it isn't
   rewriting toward its own style), but flag those cells; a non-subject cleaner (or a second cleaner as a
   cross-check) is the harder-line fix. Keep raw text alongside cleaned so every strip is auditable.

## Sequence

1. Scaffold `studies/convergence/` (README + `spec/stimulus.json` with the 9 prompts + `models.json`) — **after prompt review**.
2. Run the ~17 models, `--runs 3`, temp default. Eyeball transcripts in the reused viewer.
3. Write `analyze.py`; wire OpenAI embeddings + cosine; emit `analysis.json`.
4. Two plots off the one matrix:
   - **Axis A** — cross- & within-model similarity per prompt (ordered by measured convergence), split by tier.
   - **Axis B** — per-model cross-family similarity vs. generation time, one line per family; B2 size-control overlaid.
5. Decide from the results: scale N / add the LLM-judge cross-check, or record the falsification.
