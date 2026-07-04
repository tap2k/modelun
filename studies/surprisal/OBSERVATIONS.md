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
