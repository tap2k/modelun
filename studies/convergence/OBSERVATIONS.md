# convergence — raw observations (NOT conclusions)

Working notes from reading transcripts by eye during the pilot. **These are observations to be
checked, not findings.** Nothing here is settled; several depend on methodology fixes still open
(see bottom). Do not promote any of this to a claim without the cleaned run + a fixed cross-model
metric + more than run-0.

## Per-prompt, from reading run-0 (and 3-run stability where noted)

- **fruit** — near-total convergence: 15/16 said *Apple* (llama-3.3: Orange). Strongest single
  convergence in the study. Even here, cleaning matters (mixtral "An apple! 🍎" → "Apple").
- **number** — two attractors, {**7/Seven**, **42**}, covering almost the whole fleet; 13/27 appear
  once or twice. Individual models WOBBLE between 7 and 42 across their 3 runs (claude-3-haiku:
  42,42,7). Population answer-space is narrow + stable; per-model attractor is noisy.
- **animal** — *Elephant* is the runaway mode, then Lion/Tiger/Dog. Also wobbles within-model
  (gpt-5.4-mini: Tiger,Octopus,Elephant). Same shape as number: narrow shared menu, noisy per model.
- **country** — *Japan* plurality (~6), then France/Canada. Faint FAMILY split: the Claudes that
  answered leaned France/US; GPT+Gemini leaned Japan. (Faint, run-0 only — do not overweight.)
- **joke** — 11/16 collapse onto TWO jokes: *atom* (Claude+Gemini) vs *skeleton* (GPT+open). Clear
  family fingerprint in which attractor. This is the case that proved cleaning is needed (same joke,
  different wrappers).
- **haiku** — lexically all distinct (16 unique), but THEMATICALLY collapsed: nearly all
  nature/seasons (breeze, leaves, dew, snowflakes, cherry blossoms). Not one about a city/machine/
  person/argument. llama-3.3 & llama-4 nearly identical ("snowflakes gently fall … peaceful hush").
- **word** — lexically all distinct (16 unique invented words), but convergent one level up: shared
  whimsical-European phonology (-le/-une/-ax), shared FORMAT (bold word → part-of-speech →
  pronunciation → definition), and several landed in the same semantic space ("soft luminous feeling
  at dusk" appeared 2+ times independently).
- **metaphor** — behaves like a MEMORIZED-ITEM prompt, not a creative one. ~5 models on two stock
  clichés: "Life is a river" (sonnet-4, qwen3) and "Life is a tapestry … woven with threads of joy
  and sorrow" (claude-3-haiku, gpt-4o-mini, llama-3.3 — near-verbatim). Separately "Time is a
  thief/river" recurs (opus-4.8, gemini-3.5, gemini-3-flash). A small canon of stock metaphors that
  models draw from. (mixtral misread the task — defined "metaphor" instead of giving one.)
- **poem** — pure theme/register convergence, exactly like haiku. 16 distinct poems, but nearly all
  are rhyming-couplet nature-at-dusk: twilight, stars, wind, moon, whispers ("whispers of the wind"
  verbatim 2+). None about a city/breakup/hunger/code.

## The pattern that keeps recurring (tentative)

Convergence appears to live at DIFFERENT LEVELS, and the split is NOT "factual vs creative" — it's
whether a **memorized canon of answers** exists:
- **Canon prompts** (fruit/number/animal/country/joke/**metaphor**): converge on the same small set
  of DISCRETE answers/clichés. Even "give me a metaphor" has a stock canon (life-is-a-river,
  time-is-a-thief). Visible to exact/near-match; muddy under raw cosine on short tokens.
- **Generative-from-aesthetic prompts** (haiku/poem/word): lexically divergent but converge on
  THEME / REGISTER / FORMAT (nature-at-dusk poems; whimsical-European invented words). This IS partly
  captured by cosine (see correction below) — earlier claim that it was "invisible to cosine" was
  WRONG. Cluster-count (# distinct exact strings) does miss it; cosine against a baseline catches it.
- So metaphor MOVED from the creative bucket to the canon bucket once read. The lesson: don't assign
  a prompt to a regime a priori — read it.

If this holds, the study isn't measuring one thing on a gradient — it's measuring (at least) two
different homogenization phenomena. Do not collapse them into a single "convergence score."

## CORRECTION: theme convergence IS in the embeddings (tested, not assumed)

Earlier I claimed cosine was "blind" to the theme/register convergence on creative prompts. TESTED —
it's false. Probe on the 16 poems (run 0):

  actual poems (all nature-at-dusk):              mean cross cosine = 0.597
  baseline: 16 poems FORCED onto varied topics:   mean cross cosine = 0.403
  noise floor (unrelated prose):                  mean cross cosine = 0.10

The +0.20 (0.60 vs 0.40) IS the theme convergence, sitting in the embedding. So embeddings DO reflect
it; what I lacked was a BASELINE to read the number against.

Bigger lesson (fixes my whole reading): **absolute cosine has no fixed zero** — two unrelated texts
score ~0.1–0.64 ("blue" vs "red" = 0.64). Cosine 0.5–0.6 is NOT "moderate/muddy"; against a matched
off-distribution baseline it can be strong convergence. Every convergence number needs a per-prompt
baseline ("what would genuinely-varied answers to THIS prompt score?") to mean anything. This is the
original plan's "only the contrast is interpretable" point — I just hadn't applied it to my own reads.
Implication: the fix is likely NOT "swap in regime-specific metrics" but "give every prompt a baseline."

## VERDICT: LLM cleaning is NOT worth it as built (raw-vs-clean, full run)

Tested the validated cleaner (gemini-3.5-flash + strong prompt) across all 9 prompts, raw vs clean
cross-model cosine:

  joke   +0.010   animal -0.037   fruit  +0.005
  number +0.026   country -0.121  haiku  -0.001
  poem   -0.009   metaphor -0.005  word   -0.077

**Not one prompt shows meaningful positive lift; short-answer prompts are actively CORRUPTED.** Root
cause found by reading country: the cleaner HALLUCINATES on short inputs — told to strip-and-preserve,
it instead INVENTED prose: "Japan" → "Japan is an island country in…", "Senegal" → "Senegal is a country
located in…", "Brazil" → "Brazil is the largest country…". That's fabrication, not extraction, and it's
worse than the earlier setup-dropping bug. It fires precisely when there's nothing to strip (the model
can't resist "being helpful"). Result: 16 crisp country names became verbose descriptions that diverge on
the description → cosine 0.472 → 0.351.

Why the intended win is small anyway: the wrapper problem (skeleton-joke trio) is REAL but RARE in
aggregate — most replies aren't heavily wrapped, so stripping them barely moves the mean (joke +0.01).
The cure (a generative model in the loop) introduces a bigger disease (hallucination on short inputs).

**So: high-risk, low-reward. Do NOT use LLM cleaning as a blanket normalizer.** Options if the wrapper
problem still needs addressing:
- deterministic rule-based strip (preamble/signoff/emoji/markdown) — can't hallucinate, but English-biased
- apply cleaning ONLY to long replies (len > threshold), never to short ones — but that's ad hoc
- skip cleaning; rely on BASELINE-relative cosine, which already handles most of what cleaning aimed at
  (a wrapped and unwrapped joke both sit above the varied-joke baseline)
The baseline approach looks like it dominates cleaning: cheaper, no fabrication risk, and it made joke's
"low" 0.40 legible as strong convergence without touching the text. Leaning toward: DROP cleaning, ADD
baselines.

## REBUILT metric (run-0 bug fixed, cleaning dropped) — the pairs-vs-centroid gap is signal

analyze.py rebuilt: raw-only (no cleaning), uses ALL 3 runs per model, reports two cross-model measures.
- **cross_pairs** = every run of X vs every run of Y (honest about run noise)
- **cross_centroid** = per-model averaged vector vs the same (smooths run noise)
The GAP between them = within-model run-to-run wobble.

  prompt     pairs  centroid  gap   within | closed_c open_c |  #distinct
  joke       0.406  0.507   +0.10  0.716  |  0.560  0.501  |  9
  animal     0.571  0.727   +0.16  0.691  |  0.704  0.804  |  3   <- 75% plurality
  fruit      0.757  0.823   +0.07  0.873  |  0.851  0.732  |  5
  country    0.489  0.639   +0.15  0.666  |  0.694  0.461  |  8
  number     0.554  0.623   +0.07  0.845  |  0.609  0.602  |  5
  haiku      0.560  0.680   +0.12  0.745  |  0.668  0.757  |  12
  poem       0.607  0.717   +0.11  0.774  |  0.703  0.771  |  10
  metaphor   0.393  0.541   +0.15  0.595  |  0.533  0.534  |  14
  word       0.409  0.575   +0.17  0.569  |  0.560  0.664  |  15

Reads (tentative):
- **#distinct (centroid-clustered) is the cleanest discrete signal.** Canon prompts cluster hard
  (animal 3, fruit 5, number 5); aesthetic prompts don't (haiku 12, metaphor 14, word 15). Matches the
  two-regimes reading from eyeballing — now quantified.
- **animal: 3 distinct / 75% plurality** — much higher convergence than run-0 suggested, because averaging
  out the Tiger/Octopus/Elephant wobble reveals Elephant as a strong shared mode.
- **closed>open holds on CANON prompts** (country +0.23, fruit +0.12) but **inverts on aesthetic**
  (animal, haiku, word: open >= closed). Consistent with two regimes. Per-prompt, small-N — do not lean.
- All still need BASELINES to be interpretable (absolute cosine has no zero).

## Axis B (size / open / generation) — WEAK signal, do not lean on it (provisional, run-0)

Cross-family similarity per model (excl. same-lineage), from raw analysis.json (run-0 metric — see bug #1):

- **open vs closed:** closed 0.514 (n=12) vs open 0.495 (n=4). Direction matches hypothesis but the
  0.019 gap is noise-level at this N. Cannot support the frontier-vs-open claim from this.
- **size (closed only):** small 0.523, mid 0.506, large 0.512 — NO monotonic size effect. (Upside: the
  B2 size-control isn't a big confound to subtract. Downside: no signal.)
- **generation within family (B1):**
    gemini: 0.482 → 0.477 → 0.521 → 0.549   — clean upward trend (SUPPORTS homogenization-over-time)
    gpt:    0.491 → 0.543 → 0.496 / 0.532    — no trend, bounces
    claude: 0.518 → 0.492 → 0.527 → 0.545    — weak-up at best, starts by dropping
  => ONE family trends up, two don't. Not a result to lean on.

**Why Axis B is the LEAST trustworthy part right now:** it's a PER-MODEL quantity built from ONE sample
per model (run-0 bug), then differenced at the 0.02 level — below the run-to-run wobble we observed. It
also lacks a baseline and averages over both prompt regimes (which may cancel).

**UPDATE — rebuilt metric (centroid, all-runs) makes Axis B WEAKER, and that is the finding:**

  open vs closed:  0.642 vs 0.639   (gap 0.003 — the earlier 0.019 was run-noise; now essentially ZERO)
  size (closed):   small 0.647 | mid 0.632 | large 0.649   (flat)
  generation:  gpt    0.658 → 0.622 → 0.640     (starts HIGH, no upward trend, arguably down)
               claude 0.655 → 0.608 → 0.644 → 0.666  (dips then recovers to ~start; no net trend)
               gemini 0.623 → 0.638 → 0.641 → 0.673  (only clean upward trend)

=> **Axis B shows NO robust signal in this pilot.** Only 1 of 3 families (gemini) trends the predicted
way; gpt's OLDEST gen (3.5) is its MOST cross-family-similar, which cuts directly against "convergence
increases over generations." open-vs-closed is null. size is null. This is a real NULL result on Axis B
(homogenization-over-generations / frontier-vs-open / size) — state it plainly, don't fish. The Axis-A
per-prompt convergence (canon prompts) is where the actual signal lives.

## Per-model layer — convergence as a MODEL property, not a prompt property (new axis)

Same embedding tensor, collapsed over prompts per model. Three metrics (computed in analyze.py):

- **conformity_field** (mainstream-ness vs OTHER families): range 0.608–0.673, spread 0.065. Discriminates,
  but modestly. Most consensus: gemini-3.5-flash (0.673), claude-opus-4.8 (0.666). Most outlier:
  claude-sonnet-4 (0.608), llama-3.3 (0.616). (An earlier scratch script showed 0.62–0.79 — that was
  BUGGY, inflated by including same-family; ignore it. This is the fixed number.)
- **sibling_lift** (pool minus field = how much conformity comes from a model's OWN family): ≈0 for
  everyone (±0.017). SURPRISING and important: a model's mainstream-ness is NOT driven by its siblings.
  Excluding same-family barely moves the number → the convergence is CROSS-family, not lineage cliques.
  "Everyone sounds like everyone," not "Claudes sound like Claudes." This STRENGTHENS the homogenization
  reading and weakens the house-style/family-fingerprint hypothesis (which the joke split had hinted at —
  that fingerprint may be prompt-specific, not a global trait).
- **self_consistency** (a model vs its own 3 runs): range 0.55–0.83, spread 0.28 — 4x the conformity
  spread, the MOST discriminating per-model axis. claude-opus-4.8 0.834 (commits) → mixtral 0.551,
  gpt-3.5 0.587 (wander). A real determinism/commitment trait at temp 1.0, orthogonal to conformity.

Tentative: **self-consistency is a cleaner "metric about the model" than conformity** (separates models
4x more). Conformity is real but tight. Both are per-model characterizations the same data yields for free.
Caveat: conformity-to-consensus is still somewhat circular (consensus built from these models); baselines
would help here too. Small N, one day, temp 1.0 — characterization not measurement.

## THE PIVOT: model UNIQUENESS (distinctiveness) — the metric worth keeping

Reframe (user): convergence itself is uninteresting (everyone assumes it); a per-model UNIQUENESS score
is. Built + validated:

**distinctiveness = does a model have a RECOGNIZABLE VOICE.** Leave-one-out nearest-neighbor: for each of
a model's answers, is its nearest neighbor (within the same prompt, across all models' runs) another
answer from the SAME model? Report lift over chance. This is genuinely a metric ABOUT THE MODEL, and it's
the RIGHT notion of uniqueness because:
- It is NOT "unusualness vs the crowd" (roster-dependent, circular — user correctly flagged that with weak
  inter-family effects, panel-relative metrics just measure roster size). Distinctiveness ≠ unusualness: a
  model giving random different answers is unusual but NOT recognizable.
- ROSTER-ROBUST (the key test): removing all 5 Claude models left the other models' distinctiveness
  ranking at **Spearman 0.95**, most deltas exactly 0. A model's signature is its own property, not an
  artifact of who else is in the panel. (Conformity/unusualness fail this.)

Ranking (lift over chance, integrated analyze.py — within-scene, all runs):
  claude-3-haiku 0.66, claude-opus-4.8 0.62, gpt-4o-mini 0.55  (strong signature)
  ... middle ...
  gpt-3.5-turbo 0.11, gemini-3.1-pro 0.11, mixtral 0.07        (generic, dissolve into crowd)

Cross-metric reading (distinctiveness vs conformity vs self-consistency — three DIFFERENT things):
- claude-opus-4.8: high on all three — recognizable, mainstream, consistent. Strong stable identity.
- gpt-3.5-turbo / mixtral: LOW distinctiveness + LOW self-consistency — generic BECAUSE they wander
  (different answer each run → no stable signature). Genericness here is a symptom of inconsistency.
=> tentative: **a voice requires consistency to be recognizable.** The distinctive models are self-
consistent; the generic ones wander. (Small N, temp 1.0 — characterization, not measurement.)

This is the study's actual deliverable: a **model-uniqueness scorecard**, not a convergence claim.

### Scorecard split by prompt regime — TWO KINDS of signature (the sharpest result)

Distinctiveness broken into CANON prompts (joke/animal/fruit/country/number/metaphor — distinctive by
CHOICE) vs AESTHETIC (haiku/poem/word — distinctive by STYLE). nn-hit rate:

  model                 overall  canon  aesth   | reading
  qwen3-235b              0.67    0.72   0.56    | Type A — recognizable CHOICES (idiosyncratic picks)
  llama-3.3-70b           0.59    0.67   0.44    | Type A
  gpt-4o-mini             0.59    0.44   0.89    | Type B — recognizable STYLE (generic facts, huge poetic voice)
  claude-opus-4.8         0.48    0.33   0.78    | Type B
  gpt-5.4-mini            0.37    0.11   0.89    | Type B (extreme: canon 0.11, aesth 0.89)
  gpt-5.4                 0.37    0.17   0.78    | Type B
  ...
  gemini-3.1-pro          0.15    0.00   0.44    | pure CONFORMIST on facts (canon 0.00 — never identifiable)
  gpt-3.5-turbo           0.15    0.17   0.11    | generic on BOTH (+ low self-cons 0.59 → wanders)
  mixtral                 0.22    0.28   0.11    | generic on BOTH (+ lowest self-cons 0.55)

The finding: **a "recognizable voice" is not one thing.** Some models are identifiable by WHAT they pick
(qwen3, llama — distinctive on canon), others by HOW they write (the GPT/Claude cluster — distinctive on
aesthetic, often generic on facts). "Does your uniqueness come from your choices or your style?" is a real
per-model axis. gpt-5.4-mini is the clean case: canon 0.11 (blends in on facts) vs aesth 0.89 (unmistakable
poetic style).

Caveats: conformity_field is FLAT (0.61–0.67 all models) — does not discriminate; distinctiveness is the
metric that does. canon=6 prompts, aesth=3 prompts × 3 runs — splits are directional, not measured
(gpt-5.4-mini 0.11→0.89 is thin data). Small N, temp 1.0, one day.

## VALIDATION BATTERY (ablation + permutation + bootstrap) — all zero LLM cost, on cached embeddings

Three tests, three different questions. All run on already-computed embeddings — no new generations/API.

1. **Permutation (significance):** shuffle which model produced which answer 1000x → null ~0.06 (chance).
   - 13/16 models are SIGNIFICANTLY distinctive (p<0.05, most p<0.001).
   - 3 are NOT: mixtral (p=0.25), gemini-3.1-pro (p=0.13), gpt-3.5-turbo (p=0.06) — statistically GENERIC,
     indistinguishable from random attribution. A real finding, not merely "low score."
2. **Leave-one-family-out ablation (robustness):** drop each family, recompute, Spearman vs full ranking.
   - 0.80 (drop gpt) to 0.97 (drop llama/qwen). Ranking survives removing ANY lineage → not a roster
     artifact. Generalizes the earlier Claude-only drop across all families.
3. **Bootstrap over prompts (the N=9 reality check):** resample 9 prompts w/ replacement 2000x → 90% CIs.
   - CIs are WIDE and overlapping (opus 0.44–0.85, qwen3 0.07–0.56). At 9 prompts, fine-grained ranking
     is NOT supported. Only TIERS separate: claude-3-haiku (0.56–0.85) vs mixtral (0.04–0.19) don't overlap.

**DEFENSIBLE CONCLUSION (not a 16-deep ranking):** distinctiveness is real (permutation) and roster-robust
(ablation), but at N=9 only COARSE TIERS are trustworthy (bootstrap):
  - TOP (genuine signature): claude-3-haiku, claude-opus-4.8, gpt-4o-mini
  - BOTTOM (statistically generic): mixtral, gemini-3.1-pro, gpt-3.5-turbo
  - MIDDLE: unresolved — CIs overlap.
The bootstrap's message is actionable: **to sharpen the middle, add PROMPTS, not models.** (Power is limited
by 9 prompts, not by 16 models.)

Terminology (user asked): the removal technique is **ablation** (leave-group-out). "Validate the scorecard"
= ablation (robustness) + permutation (above-chance significance) + bootstrap (rank confidence/CIs).

## RESOLVED FRAMING: "which models give unique answers" (the buyer's question)

Popped up a level (user): don't chase authorial VOICE (stylometry — text embeddings entangle
style/topic/packaging, and 3 different distinctiveness definitions gave 3 different rankings + needed a
brittle regex packaging-strip; that whole line is abandoned). The actual use case is simpler: *some people
want a model that gives genuinely UNIQUE answers, not the consensus.* So the metric is just:

  **uniqueness = distance from consensus** = 1 - cos(model's per-prompt centroid, mean of OTHER models'
  centroids), averaged over prompts. No packaging strip needed (tics wash out — they move an answer only
  slightly off consensus, equally for all models). Content-dominated, which is exactly what "a different
  answer" means. Roster-relative, and that's CORRECT here ("unique vs the current field" is what a buyer
  means — there is no Platonic uniqueness).

Result (bootstrap 90% CI over prompts):
  llama-3.3 0.247, claude-sonnet-4 0.242, gpt-4o-mini 0.239 ... gemini-3.5-flash 0.161 (most consensus)
  Range 0.16–0.25 — NARROW. CIs overlap almost entirely. Only gemini-3.5-flash clearly separates (bottom).

**THE FINDING (defensible, matches the homogenization thesis from the buyer's angle):** on simple
open-ended prompts, NO model meaningfully escapes the consensus — they all sit ~equally far (~0.2) from
center. There is no standout "original" model among these 16. The only clear signal is that
gemini-3.5-flash is the most consensus-hugging. So: convergence is real AND no model is a notable escape
hatch from it.

This supersedes the distinctiveness/voice scorecard above (kept as a record of what DIDN'T work: NN-
attribution conflated packaging tics [claude-3-haiku "Here's one for you:"], determinism [opus verbatim
repeats], and style [gpt-4o-mini], and flipped ranking with each definition — not robust, don't ship it).

## TEMPERATURE CONFOUND — self-consistency is largely EFFECTIVE-TEMP, not "voice" (reframe)

We send temperature=1.0 to every model, but they DON'T all honor it. Exact-duplicate rate (how often 2+ of
a model's 3 runs are byte-identical — a near-greedy tell):

  Claude/Gemini families: 0.44–0.67 (gemini-3.5-flash 0.67)   <- effectively LOW temp, ignore the 1.0
  open + older GPT:        0.11–0.22 (llama-3.3/mixtral 0.11)  <- actually sampling at temp 1.0

A ~6x spread in effective determinism under a NOMINALLY IDENTICAL temperature. Consequence:
- **self_consistency is contaminated.** "claude-opus-4.8 self_cons 0.83 = committed voice" was WRONG — it
  has a 56% byte-identical-repeat rate; it's running near-greedy and literally returning the same string.
  Reframe: self_consistency ≈ "does this model honor temp / run near-greedy", NOT a personality trait.
  Report exact-duplicate rate as the effective-temperature proxy.
- The models earlier dismissed as "generic because they wander" (mixtral, gpt-3.5) are the ones HONESTLY
  sampling at temp 1.0 — their spread is real stochasticity, not a defect.
- **uniqueness (consensus-distance) is ROBUST to this** — it's centroid-based (averages a model's 3 runs),
  so effective-temp differences partly wash out. Keep uniqueness as the headline; reframe self-consistency.

Follow-up (deferred): a TEMPERATURE SWEEP on the SUBSET of models that honor temp (temp 0/0.7/1.0/1.5) to
test whether convergence is partly a sampling artifact. Cannot include fixed-temp newer models — partial
fleet only. Not run yet.

Methods caveat (not a headline): newer/reasoning models increasingly ignore or fix temperature, so it
cannot be held constant across a modern fleet — every cross-model convergence study now carries an
uncontrolled sampling confound. Note in limitations.

## OUTSIDER TEST (6 added: Chinese-primary + persona) — mixed, honestly

Added deepseek-v3.2, ernie-4.5, minimax-m1 (Chinese-primary) + grok-4.3, hermes-4-70b, mythomax (persona/
lightly-RLHF'd). Q: do genuine outsiders break the flat 0.16–0.25 uniqueness band? Answer: PARTIALLY.

Recomputed uniqueness (22 models), NEW top of ranking:
  ernie-4.5      0.335   (Chinese; well above old ceiling 0.247)
  mythomax       0.306   (roleplay-tuned, least RLHF)
  deepseek-v3.2  0.258   (Chinese)
  ... monoculture pack 0.19–0.24 ...
  grok-4.3       0.175   (LOWEST — total conformist on generic prompts!)
  gemini-3.5     0.168

Reads (still provisional):
- **Some outsiders DO break the ceiling** — ernie 0.335 vs old max 0.247 is real. Chinese-origin +
  minimal-RLHF models are the most distinctive. User's "expect other-country models to differ" = supported.
- **BUT the effect is selective and partly confounded:**
  - CONTENT convergence is DEEP: even outsiders give Apple (all) and the ATOM JOKE (deepseek, ernie, grok,
    hermes). Divergence shows on `animal` (grok→capybara, hermes→pangolin — genuinely novel) and jokes for
    mythomax only. The strong-prior attractors capture even non-US, non-RLHF models → homogenization is in
    the shared ENGLISH-WEB SUBSTRATE, not just the US-frontier-RLHF cluster.
  - grok is a VALUES-outlier (per CAIS) but a GENERATION-CONFORMIST (lowest uniqueness here). DOMAIN
    MATTERS: distinctiveness on opinions ≠ distinctiveness on open-ended generation. Don't conflate.
  - The uniqueness gain for ernie/mythomax/deepseek is PARTLY effective-temperature: they have low dup_rate
    (0.00–0.11) + low self_cons (0.44–0.50) — they WANDER more, which inflates consensus-distance. The temp
    confound bites again. Genuine-content-divergence vs higher-entropy is NOT cleanly separated here.
- **minimax-m1: 12 failed cells** (partial-failure model) — flag/exclude from strong claims.

Net (provisional): outsiders raise the ceiling modestly; content homogenization (apple, atom joke) is
robust across origin AND alignment; the "unique" outsiders are partly just higher-entropy samplers.

## CONFOUND SEPARATED: content-divergence vs entropy (decisive for the outsider claim)

Decomposed uniqueness into CONTENT (centroid distance from consensus — entropy CAN'T inflate) vs SPREAD
(within-model wander — pure entropy). Verdict per outsider:
  ernie-4.5    CONTENT 0.335, spread 0.213 (LOW) -> GENUINELY different content, cleanly. The real finding.
  deepseek     CONTENT 0.258, spread 0.499 (high) -> partly real, half rides on entropy.
  mythomax     CONTENT 0.306, spread 0.559 (highest) -> ILLUSION. Not original, INCOHERENT (wanders). Its
               "distinctiveness" was entropy, not content. Least-RLHF ≠ most-original; = most-unstable.
  grok         CONTENT 0.175 (LOWEST), spread 0.426 -> conformist AND noisy. Confirmed generation-conformist.
So the confound was REAL and material: only ERNIE is a clean genuine-content outlier. mythomax was a false
positive (entropy). The honest CONTENT column compresses ALL 22 models to 0.17–0.34 — even ernie is only
~0.10 above the pack. Outsiders barely move the real needle; one model (ernie) clearly does.

## ERNIE EYEBALL + SPOT-CHECK — the "content outlier" is mostly VERBOSITY (deflates topline)

Read ernie's actual answers vs the pack (current prompts + 5 fresh short-answer prompts). Finding:
ernie's high content-distance is ~80% VERBOSITY/FORMAT, not different content:
- animal→"One fascinating animal is the octopus. Known for..." (octopus is NOT unique — 4o-mini/deepseek
  said it too; the PARAGRAPH is what's far from the one-word consensus)
- number→REFUSES/hedges ("very open-ended, countless numbers...") — maximally far, but a DODGE not originality
- color→"A common color is blue", scientist→Einstein(+bio), fruit→apple, joke→atom joke. SAME content,
  sentence-wrapped + hedged + follow-up questions.
- Genuine content divergence is small: city Paris-vs-pack-Tokyo is about the only real one.

=> **A THIRD confound, still live: VERBOSITY/FORMAT.** Text embeddings encode length/register, so a verbose
model reads as "far from consensus" without saying anything different. The centroid-decomposition killed the
ENTROPY confound but NOT this one. **ernie is not more original — it's more verbose.** The topline's "ernie
= one clean content-outlier" is WEAKENED; treat it as unproven.

Secondary: in the spot-check, **deepseek** showed REAL content divergence (color→Crimson not blue,
word→Serendipity) — divergence in ANSWER CHOICE, not word count. If any model is a genuine content outlier,
deepseek is a better candidate than ernie. Needs the same verbosity-controlled check.

Implication for method: to measure genuine content uniqueness we must CONTROL FOR LENGTH — e.g. force
one-word answers, or normalize/truncate before embedding, or measure divergence on the DISCRETE answer
(exact-match clustering) not the embedded sentence. Open methodology item.

## ANSWER-CHOICE SURPRISAL — the metric that finally works (probe validated, all 4 predictions hit)

Reverse-engineered deepseek's behavior into: force ONE-WORD answers on wide-answer-space categories
("Name a color."), then score each model's DISCRETE choice against the field: surprisal =
-log2 P(answer | all other models' answers), leave-one-out, add-one smoothed. Companions: modal-avoidance,
novel-rate (answers NOBODY else gave), self-distinctness. Exact-match on normalized tokens — no embeddings,
no judge, no cleaner. Verbosity-immune BY CONSTRUCTION; entropy becomes an AXIS (surprisal × self-distinct
2x2: true-contrarian / explorer / consensus-fixed / consensus-sampler) instead of a confound.

Probe: 15 models × 16 categories × 4 runs (960 calls, ~$1). Results:

  deepseek-v3.2    2.88 [2.24,3.56]  avoid 62%  NOVEL 25%  -> EXPLORER, #1, validated
  mixtral          2.36 [1.79,2.90]  (honest sampler, picks off-modal)
  claude-haiku-4.5 2.27              (surprise: small Claude explores)
  ... pack ~1.5–2.1 ...
  qwen3            1.42, glm-4.7 1.55, gpt-5.4 1.51 (0% novel), grok 1.64 (0% novel)
  ernie-4.5        1.33 [0.96,1.68]  avoid 38%  novel 0%   -> DEAD LAST

All four predictions confirmed:
1. **deepseek is genuinely unique — now verified.** #1 surprisal, and the only model with a large NOVEL
   rate (25%: sanskrit, marigold, cardinal, tailor — answers no other model ever gave). CI vs ernie
   non-overlapping.
2. **ernie INVERTED: embedding-metric #1 -> surprisal DEAD LAST.** The smoking gun for the verbosity
   confound: forced to one word, ernie is the most CONFORMIST model in the roster (0% novel). Its entire
   embedding "uniqueness" was word count. This inversion is the strongest validation of both the confound
   diagnosis and the new metric.
3. claude-opus-4.8: consensus-fixed (0% novel), as predicted.
4. mythomax: mid-pack (2.07) — its earlier "distinctiveness" was entropy, as suspected.

New findings from the probe:
- **"Chinese-primary = divergent" is REFUTED.** qwen (1.42), glm (1.55), ernie (1.33) are all bottom-tier
  consensus. Divergence is a DEEPSEEK-specific property (its training/sampling choices), not a country
  property. Sharper and more honest than the origin story.
- grok: 0% novel — generation-conformist CONFIRMED on the discrete metric too (CAIS dissociation stands).
- **tree -> "oak": 58/58.** Every model, every run. A perfect 100% convergence anchor — the substrate
  homogenization at maximum. Also flower->rose 52/57, color->blue 47/60, fruit->apple 46/59.
- Caveat: top ranks (deepseek vs mixtral vs haiku-4.5) have overlapping CIs at 16 categories — coarse
  tiers again; more categories to sharpen (cheap: one-word answers).

Raw + analysis: scratchpad/surprisal_probe.py, surprisal_analyze.py, surprisal_raw.json (promote to a
study spec if adopted).

## Comparison to CAIS values.safe.ai (Phan/Mazeika/Blair/Hendrycks 2026) — related work

CAIS measures cross-model convergence on VALUES (forced-choice pairwise over people/companies/countries/
sports → Bradley-Terry → Elo per model). Findings: 4 models "agree on almost the entire ranking" (broad
convergence), with the SAME divergence structure we see: DeepSeek alone ranks Taiwan low / badminton high
(Chinese prior); Grok alone favors defense/US/Israel (persona). Their method (forced-choice, one token) is
CLEANER than our free-text+embedding (no temp confound, no packaging, no cosine ambiguity) — it's the
rigorous template if we ever want values.

Positioning (user: pivot to unexplored): CAIS OWNS values-convergence. Our lane is the UNEXPLORED TWIN —
open-ended GENERATION (not forced-choice values): per-model UNIQUENESS as a consumer score, the
effective-temperature confound (they never hit it — one-token answers), and the outsider-divergence
structure on generative prompts. Their board CONFIRMS our early pattern (Chinese model → own-country/
own-culture; persona model → values-outlier) externally. Note: their "coherence increases with scale"
(Mazeika 2025) is WITHIN-model coherence, NOT our Axis-B cross-family-over-generations (which was null) —
different claims, keep separate.

## Open methodology issues (block conclusions)

1. **run-0 representative bug.** `analyze.py` uses only run-0 per model for the cross-model metric,
   discarding 2/3 of the data. Given the within-model wobble above, cross-model numbers are partly a
   coin-flip. Two fixes to compare, not silently pick one:
   - **all-pairs across all runs** (honest about noise; lower convergence)
   - **per-model centroid** (smooths noise; higher convergence)
   The GAP between them is itself the within-model-noise signal. Report both.
2. **Short-token cosine is near-useless.** "7" vs "42" are tiny strings; cosine ~0.5 is noise. These
   prompts need exact/normalized-string clustering, not embedding cosine. Regime-appropriate metrics.
3. **Creative-prompt convergence is topical, not lexical** — current metrics miss it entirely. Needs
   a judge or a theme-embedding, else we'll falsely report "haiku = divergent."
4. **Cleaner self-family.** gemini-3.5-flash is a subject and self-cleans gemini/gemma. Flag those.
5. **N and dating.** 16 models, 3 runs, one day. Pilot. Characterization, not measurement.
