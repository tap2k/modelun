# surprisal — working observations

## FINAL scorecard (refill complete, 32/33 full-data; reka-flash-3 still failing its route)

Refill (2026-07-04) rewrote the 13 clipped models with clean 120/120 runs. Changes vs run-1 preview:

- **NEW #1: hermes-4-70b — 3.05 [2.60,3.56], 20% novel, 60% modal-avoid, explorer.** The lightly-RLHF'd
  Nous persona model is the most off-consensus model of all 32 — clearly above mixtral 2.59 and
  deepseek-v3.2 2.45. With mythomax also solidly explorer at 2.13 (8% novel on DISCRETE choices — its
  earlier "mostly noise" dismissal was about embedding-space wandering; on answer CHOICE it's genuinely
  off-modal), the **low-RLHF/persona arm is real on this metric**. RLHF-lightness ↔ off-consensus answers
  is now the leading explanatory candidate — fits Finding 2 (newest most-RLHF'd flagships at the bottom).
- **claude-fable-5 jumped to 1.90 true-contrarian** (49% avoid, LOW self-distinct — stable different
  defaults). This BREAKS the clean Claude generational decline: 3-haiku 2.04 → haiku-4.5 1.65 →
  opus-4.8 1.26 → **fable-5 1.90** → sonnet-5 1.04. The creative-writing-branded gen-5 Claude deviates
  from the mainline assistant slide. Richer story: the decline holds for MAINLINE assistants; a
  deliberately creative-tuned sibling escapes it (a little).
- **sonar (search-tuned) with full data: 2.12 explorer** — retrieval-grounding apparently pulls answers
  off the parametric consensus. The "different objective = different answers" hypothesis has one clean
  supporting case.
- deepseek-r1 full: 1.46 consensus-sampler → lineage final: v3-0324 1.34, **v3.2 2.45**, v4-flash 1.71,
  r1 1.46. v3.2 stays the version-specific anomaly (Finding 1 unchanged).
- grok-4.3 full: 1.41, 0% novel — generation-conformist, third independent confirmation.
- Bottom stable: **claude-sonnet-5 1.04 (last)**, qwen3 1.13, gpt-5.5 1.25, opus-4.8 1.26 — the newest
  mainline flagships are the most consensus-bound, all ~0% novel.
- Substrate: tree→oak 96%, tool→hammer 95%, flower→rose 90%, cheese/herb/fruit/vegetable 88%.

(Below: run-1 notes, kept for provenance.)

Run 1: 2026-07-03/04, 33 models × 30 categories × 4 runs. **13 models were clipped by OpenRouter credit
exhaustion (402s)** mid-run — hermes/mythomax/reka got ~nothing; palmyra, sonar, kimi-k2.5, deepseek-r1,
glm-4.7, claude-fable-5, grok-4.3, command-a, hunyuan, granite lost 10–85% of cells. Those rows are
thin-data (wide CIs). Refill re-run launched 2026-07-04 after top-up. The ~20 clean models carry the
findings below; treat clipped-model numbers as provisional.

## Finding 1 — deepseek's explorer property is VERSION-SPECIFIC, not lineage-wide

The lineage sub-experiment (all four deepseeks, three of them clean):

  chat-v3-0324   surprisal 1.31   novel  0%   consensus-fixed
  v3.2           surprisal 2.47   novel 15%   explorer        <- the anomaly
  v4-flash       surprisal 1.69   novel  5%   explorer-ish
  r1             surprisal 1.85   novel  6%   (thin data — 84/120 cells failed)

v3.2's predecessor is a bottom-tier conformist; its successor regressed halfway back. Whatever made v3.2
unique was a choice in THAT release (data mix / RL recipe / sampling), not "deepseek DNA". Uniqueness is
a property of a MODEL VERSION, not a lab or a country — consistent with (and sharpening) the earlier
refutation of "Chinese-primary = divergent".

## Finding 2 — newer generations ARE more conformist (the discrete metric finds what embeddings missed)

Within-family surprisal declines with generation:

  Claude: 3-haiku 2.06 -> haiku-4.5 1.58 -> opus-4.8 1.22 -> sonnet-5 1.00 (LAST of all 30; fable-5 1.41 thin)
  GPT:    4o-mini 2.11 -> 5.4 1.46 -> 5.5 1.24        (gpt-3.5-turbo 1.57)
  Gemini: 2.5-flash 1.51 -> 3.1-pro 1.47 -> 3.5-flash 1.65   (flat — no decline)

The newest flagships (sonnet-5, gpt-5.5, opus-4.8, qwen3-235b) occupy the BOTTOM of the scorecard with
~0% novel answers. The user's original hypothesis — later generations converge more — was NULL on the
embedding metric (convergence study Axis B) but SHOWS on answer-choice surprisal, at least for the
Claude and GPT lineages. Caveats: size × generation not fully separated in this roster (the size-matched
claude 3-haiku -> haiku-4.5 pair does decline, which is the cleanest cell); gemini is flat; one day, one
run each. Suggestive, not established — but now worth a designed test (size-matched generational walks,
the convergence study's B1 grid, on THIS metric).

## Finding 3 — the substrate convergence at 33-model scale

High-convergence categories (modal share across ~15 labs' models):
  tree->oak 98%, cheese->cheddar 94%, tool->hammer 93%, flower->rose 91%, vegetable->carrot 90%,
  condiment->ketchup 89%, fruit->apple 88%, herb->basil 84%, mythical_creature->dragon 84%,
  fabric->cotton 84%, fish->salmon 81%, color->blue 80%.
Twelve of 30 categories have a single answer taken by >=80% of the entire field.

## Scorecard top/bottom (clean models only)

  top:    mixtral-8x22b 2.59, deepseek-v3.2 2.47 (overlapping CIs — a top TIER, not an order),
          gpt-4o-mini 2.11, llama-4-maverick 2.06, claude-3-haiku 2.06
  bottom: claude-sonnet-5 1.00, qwen3-235b 1.11, claude-opus-4.8 1.22, gpt-5.5 1.24,
          ernie-4.5 1.31 (verbosity king = discrete-choice conformist, inversion still holds),
          deepseek-chat-v3-0324 1.31

## Method notes

- 3 models (hermes, mythomax, reka) had 100% failure in run 1 — absent from analysis.json until refill.
- analyze.py joins metadata on run.py's slug-tail labels (fixed 2026-07-04 — labels in spec/models.json
  must equal slug.split('/')[-1]).
- Console table prints n_answers-blind; thin-data rows are only visible via CI width. Consider printing
  n_answers.
- Categories are the power axis; 30 got the top tier's CIs to ~overlapping-but-tight. More categories
  (cheap) before more models.

## The original convergence-study axes, rerun on surprisal data (2026-07-04, zero new calls)

- **open vs closed:** 1.78 vs 1.60 — direction matches (open more divergent) but small, and driven by the
  persona models being open. Weak on its own.
- **origin:** persona 2.20 > us-frontier 1.69 > chinese 1.55 ≈ enterprise 1.52. Alignment-lightness beats
  country of origin as the divergence predictor (and within persona, grok 1.41 vs hermes 3.05 — persona
  branding ≠ generation divergence; RLHF-lightness is the live variable).
- **generation walks (B1 analog), honest version:** claude declines (2.04→1.65→1.26→1.04, fable-5 bump
  1.90); gpt declines after 4o-mini (2.19→1.47→1.25); **gemini flat** (1.52→1.43→1.62); **llama RISES**
  (1.80→2.01); deepseek non-monotonic (v3.2 anomaly). So "newer = more conformist" is a **2-of-5-lineage
  pattern** (the two biggest mainline assistant lines), NOT a universal law. Earlier claim softened.
- **Axis A analog (category concentration × tier):** newest models on peaked categories = **0.86 bits** —
  near the theoretical floor (they give the field's modal answer essentially always); oldest = 1.37.
  On diffuse categories the gap persists (2.04 vs 2.62) but proportionally smaller. The newest flagships
  snap to the mode hardest exactly where a strong mode exists — the original prior-strength hypothesis,
  now measured instead of assumed.

## REGISTERED PREDICTIONS (2026-07-04) — surprisal as a leading indicator of "heirloom" attachment

Hypothesis (user): attachment to a model's VOICE — the folklore that makes people demand a deprecated
model back — is predicted by answer-choice surprisal, measurable at launch for ~$1, months before the
folklore settles. Mechanism: a model that gives the consensus answer is interchangeable; one with
off-consensus defaults feels like a SOMEONE, and its loss registers as a loss.

Retro-validation (settled folklore, scored blind by our metric first): 4o-mini 2.19 = the mourned model
(user revolt at deprecation, restored as legacy); mythomax 2.13 = roleplay-community heirloom used years
past obsolescence; hermes 3.05 = Nous cult; mixtral 2.59 = local-community classic; vs gpt-3.5 1.63
(deprecated without grief) and grok 1.41 (persona branding, no voice-keeping). 5/5 directionally right.

Forward predictions, to grade in ~6–12 months (criteria: deprecation backlash / bring-it-back demands /
sustained use past obsolescence in writing+RP communities; all conditional on the model having real
adoption — an unused distinctive model can't be mourned):

1. **claude-fable-5 (1.90, true-contrarian): WILL develop an heirloom following.** Early signal already
   (subscriber fury during the June-2026 export-control removal — attachment, though about availability).
2. **claude-sonnet-5 (1.04) and gpt-5.5 (1.25): will NOT be mourned at deprecation.** Consensus-floor
   models are interchangeable with their successors by construction.
3. **deepseek-v3.2 (2.45) vs v4-flash (1.71): if deepseek retires v3.2, expect pushback + "v4 is tamer"
   grumbling.** The regression is in our numbers before it's in the folklore.
4. **kimi-k2.5 (1.61), glm-4.7 (1.36), command-a (1.86): no voice-folklore forms.** (command-a is the
   riskiest of these — 1.86 is borderline.)

If these hold, the study's deliverable upgrades from scorecard to LEADING INDICATOR: run the battery on
launch day, know whether users will fight for the model years later.

## Expansion run (2026-07-04): +7 models (heirloom retro-tests + generation fillers), junk guard added

Data quality first (eyeball caught both):
- **reka-flash-3 EXCLUDED as junk** — its resurrected transcript scored 4.85/53%-novel on whitespace and
  truncated reasoning-prose, not answers. analyze.py now has a JUNK guard (chat-template artifacts,
  >15-word reasoning leaks → failed cell, not answer). Verbose-but-real answers still count.
- **wizardlm-2-8x22b had template leakage** ([/INST], <thinking>) inflating it 2.95 → cleaned **2.76, #2,
  10% novel** — still a top explorer. Real spread (Dog/Lion/Elephant/Cat; Sad/Curiosity/Cheerful).

Heirloom retro-tests — one hit, one honest miss:
- **wizardlm CONFIRMS** (2.76): the yanked-and-community-mirrored legend is a top explorer. ✓
- **gpt-4o MISSES (1.73, mid-pack, 0% novel; clean data — Azure/Blue, Elephant, Joy).** The most-mourned
  model in history scores MIDDLING on snap answers. Refines the frame: surprisal captures CONTENT-CHOICE
  character; 4o's heirloom-ness lived in TONE (warmth, effusiveness, long-form style), which this metric
  does not reach. So: high surprisal at launch predicts voice-attachment via distinctive CHOICES
  (wizardlm, mythomax, hermes); tone-based attachment (4o) needs a different instrument. The registered
  predictions stand but are scoped to choice-character. (4o-mini 2.04 > 4o 1.73 also cautions against
  reading lineage proximity as folklore proximity.)

Generation walks, enriched:
- **gpt (7 points): 3.5 1.67 → 4-turbo 1.97 → 4o 1.73 / 4o-mini 2.04 → 4.1 1.64 → 5 1.35 → 5.4 1.44 →
  5.5 1.24.** NOT a monotonic slide — a PEAK AT THE 4-ERA then a steep 5-era descent. Matches the "4o era
  was peak ChatGPT personality" folklore remarkably well.
- claude: 3-haiku 2.08 → haiku-4.5 1.64 → sonnet-4.6 1.50 → opus-4.8 1.26 → fable-5 1.76 → sonnet-5 1.06
  (sonnet-4.6 slots cleanly into the slide; fable-5 stays the creative-tuned exception).
- **qwen: 2.5-72b 1.78 → qwen3 1.15 — another lineage slide.** Sliding lineages now: claude, gpt(5-era),
  qwen = 3; flat/other: gemini, llama, deepseek. The pattern is real but family-specific.
- Delisting note: claude-3-opus, 3.5-sonnet, mixtral-8x7b, gpt-4.5 are GONE from OpenRouter — the most
  heirloomed models are already unmeasurable. Argument for running this battery AT LAUNCH.

## The "frictionless mode" — warped prototype, from reading the full column distributions (2026-07-04)

The default answer is not the most COMMON thing, nor the most-DISCUSSED thing — it's the blandest
unambiguous exemplar, the answer with no edges. Two clean cases:
- **fruit: apple 124, mango 24, banana 7, orange 1.** Orange — one of the two most common fruits — is a
  singleton (said only by mythomax). Beaten 24-to-1 by mango. Prototype != real-world frequency.
- **vegetable: carrot 138, broccoli 15, potato/cucumber/spinach 1 each, TOMATO 0.** Tomato — the single
  most-cited "well actually it's a fruit" example in English, everywhere in text — never appears. So
  prototype != salience/discussion either.
=> the mode selects for LACK OF FRICTION. Orange has a color collision; tomato has a fruit/veg argument;
both dropped. Carrot, cheddar, oak, hammer survive because they're vegetables/cheeses/trees in exactly
one uncontested sense. "Generic" and "robotic," from the user's side, is friction sanded off.

Full column survey (modal share, sorted): tool 95% hammer, tree 94% oak, flower 89% rose, vegetable 88%
carrot, herb 87% basil, cheese 85% cheddar, condiment 82% ketchup (mustard 26 > mayo 2!), fish 80% salmon,
fruit 79% apple, color 77% blue ... down to the genuinely-diverse tail (no single cultural default):
gemstone 25% (diamond/ruby/sapphire ~tied), country 27%, hobby 28%, occupation 32%, dance 34%. Also:
emotion → joy/happiness dominate, primary emotions (anger/fear/sadness) nearly absent; language → 10
models said "python" (the coders leak through). The diverse categories are exactly the ones with no
prototypical text-example.

## Prompting reaches conditional modes, not the tail (tested, 2026-07-04)

"Name an UNUSUAL fruit" across 10 models, 2x each: rambutan (sonnet-5, fable, gpt-5.5, gemini-3.5 — twice
each), durian (hermes, grok, 4o-mini), kiwano==horned-melon (deepseek, one fruit two names), pitaya,
jackfruit. ~3 distinct fruits from 20 samples. The "unusual" column has its own cheddar (rambutan). So
prompting for divergence samples the MODE of P(answer | unusual), not the tail of P(answer). It's modes
all the way down — every frame opens a new column, every column has an archetype. You navigate between
conditional modes; you never draw from variance. (Validates the "dormant not reachable-by-prompting" read.)

## Implications synthesis (from the 3am thread — for the essay, not established results)

The through-line the data sets up, beyond "models are homogeneous":
- **Variance is a POPULATION property, not an individual one.** All the divergence we measured is BETWEEN
  models (fable/hermes/wizardlm/mythomax), never a model exploring its own tail — gouda IS Fable's mode.
  Human creativity likewise comes from population variance (cranks/outliers at the tail), not from the
  median human being creative. A monoculture is not one uncreative model; it is a POPULATION losing its
  variance. The heirlooms people fight for are the remaining gene pool.
- **Dormant, not destroyed — but not prompt-reachable.** The weights contain orange/tomato; the default
  never says them, and prompting only moves you to another mode. So it's a decoding+tuning problem
  (Fable proves the shape is a dial: same lab/month as Sonnet-5, opposite instinct — cause NOT localized:
  could be pretrain mix, RLHF, or serving-layer prompt; our instrument sees the deployed artifact only).
- **Two roots, often conflated:** mode-seeking (generic advice, samey answers — measured directly here)
  vs RLHF-reward (sycophancy, suggestibility — inferred via the generational slide, NOT measured). Shared
  cause: "give the answer that gets approved" collapses toward both the expected answer AND the wanted
  answer. Newest most-tuned flagships hug consensus hardest (sonnet-5 last) — RLHF amplifies mode-seeking.
- **Correlated error, not wisdom of crowds:** consult three models, get one answer, don't know it. At
  population scale, everyone's first thought becomes the same thought; the loss lands hardest on the
  heaviest users (smart people who use these tools all day), and never flags because the mode is never
  WRONG, just frictionless.
- **"Forgetting Gouda"** (candidate essay): nothing is deleted; RETRIEVAL atrophies — what comes to mind.
  Models' tail went dormant; human expression homogenizes through use (per others' work); the cycle runs
  human→model→web→model. The connecting claim (default-transfer + retrieval-atrophy + heaviest-user
  incidence) is what this night's data uniquely sets up.

## Candidate follow-up studies (surfaced in the thread, not run)

1. **Synthetic-user critique** — run persona-prompted panels through the battery, report EFFECTIVE
   POPULATION SIZE ("a 50-persona panel has effective N ~3"). Prediction: personas are conditional modes
   (the rambutan effect), so a simulated "population" is one user in N costumes — tail-free by
   construction, which is exactly where products break. Note: a "silicon sampling" lit already shows
   LLM survey respondents under-vary; the cheap instrument + effective-N framing would be the contribution.
2. **Base vs instruct** — run the battery on a base model and its RLHF'd version (same weights). If base
   names 40 fruits and instruct names 4, the tail is dormant-suppressed-by-tuning; if base is narrow too,
   the monoculture is deeper than RLHF. ~$1 each. Blocker found: OpenRouter serves ZERO base models —
   the market doesn't sell the haystack, only the modes (a finding in itself). Would need HF/local.
3. **Sycophancy bridge** — same roster, prompts with a planted user stance ("I think X, right?"), measure
   agreement-vs-correctness. Tests whether mode-collapsers are also the sycophants (connects the two roots
   with data instead of inference).

## Prior-art status (2 web searches, NOT a lit review)

Phenomenon (LLM homogeneity) established: "We're Different We're the Same" (2025), "Artificial Hivemind"
(2025), PNAS Nexus "homogeneously creative", + human-side "Homogenizing Effect" (2025). NOT found:
leave-one-out answer-CHOICE surprisal as a per-model scorecard; the generational conformity slide within
lineages; the heirloom framing + registered predictions; the frictionless-prototype catalog. Do a real
lit review before claiming "novel" in public. Distinct from CAIS values.safe.ai (that measures VALUES via
forced-choice/Bradley-Terry; grok is their outlier and our conformist — construct dissociation).

## any_word ("Pick a word") — RUN and folded in (now 31 categories, 2026-07-04)

The purest prior probe: no domain constraint, the whole ~1M-word lexicon available. Prediction confirmed.
**serendipity 60/156 (38% modal share)**, then ephemeral 7, sunshine 6, cloud 6, sunflower 4, sunset 4,
luminous 3 — the entire head is the "pretty word" cluster; apple 11 is the thing-prototype leaking in.
50 distinct of 156. Given the ENTIRE dictionary to disagree with, 39 models still collapse onto the single
most self-consciously delightful word in English — serendipity is the text-prototype of word-worth-naming,
so the model picks the word people pick when asked to pick a word (one meta-layer up, same machine).
Note: 38% at N=39 vs the ~50% pilot at N=12 — the frontier labs ARE the serendipity monoculture (all
Claudes 3/3, gemini 3/3), the enterprise/persona/Chinese oddballs spread it out. It sits just below the
>=80% extreme tier, but is the conceptually sharpest category: every other high-converger had a constraint
("a tool" -> hammer is reasonable); this one had NONE and still collapsed. Strong candidate essay opener:
*ask 39 AIs to pick any word in the language, and the frontier labs all say "serendipity."*
