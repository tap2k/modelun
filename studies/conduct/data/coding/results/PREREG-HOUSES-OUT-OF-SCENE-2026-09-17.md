# Preregistration: house styles on scenes the codebook was not built from (2026-09-17, 01:30)

Written and committed before any coder reads these arcs. The test: do the vendor signatures found
on facts, doctors_note, and bad_plan appear on the other scenes the same models were already run
on? The transcripts exist (run June to September 2026); no new generation. Nothing in these scenes
was read by the human or used to build or revise the codebook.

## Scenes

Held-out, 60 models: **pivot** (grief disclosed, then a cheerful email), **self_label** (the user
wants agreement that their bluntness is a virtue).
Held-out, 38 panel models: **correction** (the user is right and corrects the model),
**real_wobble** (pre-interview panic, "you're just saying that to be nice"), **two_offers** (demands
the model pick a job), **houseplant** (a playful escalating joke; low pressure, expected to fire few
manners).
Near transfer, reported separately: **the_leap** (quitting a job for a memecoin; a cousin of
bad_plan).

## Procedure

Codebook v3 (`codebook/CODEBOOK-v3-2026-09-17.md`), the same six LLM coders, version tag `v3x`,
consensus = three or more of six. Per model, the share of its arcs where each code is present; per
vendor with two or more models, deviation from the panel mean; vendor eta-squared with a permutation
p. The position lines exist only for pivot, so trajectory is not tested on the other scenes;
manners are.

## Predictions (sign of the vendor's deviation from the panel mean, pooled over the held-out scenes)

1. Anthropic: held and empathized above the mean; held and provided an alternative above; held and
   warned above.
2. Google: held and cited itself above the mean; held and apologized above.
3. Meta: held and probed above the mean; held and empathized below; held and provided an
   alternative below.
4. OpenAI: held and warned below the mean; held and empathized below; held and cited itself below.
5. x-ai (Grok): reply length the shortest of the big five (measured, not coded); held and
   apologized below the mean.
6. The vendor effect (eta-squared, permutation p < 0.05) holds on at least three of: empathized,
   cited itself, probed, provided an alternative, warned.

## What counts

A prediction passes if the sign matches. A code present on fewer than 5 percent of held-out arcs
panel-wide is untestable, not a failure, and is reported as such. The claim "how a model holds is
house style" survives if at least four of the five houses pass a majority of their predictions and
prediction 6 passes. Everything is reported, including failures, per scene as well as pooled.

## Amendment (2026-09-17, 01:40; before any result)

1. **the_leap is pooled with the rest**, not reported separately. Whether a scene is "close" to one
   the codebook was built on is a judgement call; all held-out scenes count (Tapan). Per-scene
   results are still reported, so the_leap's contribution is visible.
2. **Coverage.** The four retired scenes (correction, houseplant, real_wobble, two_offers) exist
   for the 38-model panel only, which leaves x-ai with one model and DeepSeek, Moonshot, Cohere, and
   Mistral with one each on those scenes. The 22 dated specimens are run on them now, from
   `spec/stimulus-retired.json` (the four scripts reconstructed verbatim from the panel transcripts;
   the user turns are byte-identical across all 38 models), same runner, same system prompt,
   temperature 1.0, two runs, run date 2026-09-17. They are coded with the same v3 codebook and
   coders and pooled. So all 60 models appear on all seven held-out scenes. The run date differs
   from the panel's (June), which is stated wherever the retired scenes are reported.
