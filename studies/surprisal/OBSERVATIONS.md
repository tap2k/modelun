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
