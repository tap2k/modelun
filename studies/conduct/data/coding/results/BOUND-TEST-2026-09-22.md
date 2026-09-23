# Can a machine predict which codes a second reader will apply the same way? (2026-09-22)

Written before any model was asked. The paper's second contribution rests on a division: machines
recovered the codebook's categories, and a human settled which of them hold up under a second
reader. A reviewer's point: the machine arms were never asked to predict that, so "could not" is an
inference from an omission. This is the test.

## Procedure

- Input: the coder-facing codebook v2 (the same text the six coders receive, definitions with
  examples), and five transcripts drawn from outside the held-out fifty, so the model sees what
  the codes look like applied but none of the arcs the ground truth was scored on.
- Task: rank the 17 manner codes from the one two independent readers would most often apply the
  same way to the one they would least often, and give each a predicted agreement from 0 to 1.
  Output JSON.
- Models: three that were not coders and are not on the coder vendors' coder list:
  `anthropic/claude-sonnet-5`, `openai/gpt-5.6-sol`, `google/gemini-3.6-flash`. Three samples each
  at temperature 1.0, so nine rankings; each model's mean rank per code is its prediction, and the
  mean over models is the pooled prediction.
- Ground truth (`bound-test-ground-truth.json`, computed before this file): per code, the mean
  over the six coders of kappa against the author's pass on the held-out fifty, cold (before
  adjudication) and adjudicated. Cold is primary, since it is the "second reader" reading.
- Score: Spearman between predicted rank and observed kappa over the 17 codes, per model and
  pooled, with a permutation p (5000 draws). Secondary: does the prediction separate the four
  codes below kappa 0.45 cold (explained, folded and warned, cited itself, apologized while
  holding) from the rest, as area under the curve.

## What counts

- rho >= 0.5 with p < 0.05 pooled: machines can bound, and contribution 2 is restated as authoring
  and reference, with bounding shared.
- rho < 0.3 or p >= 0.05: machines did not bound when asked, and the claim stands with evidence.
- Between: reported as partial.

Script: `harness/bound_test.py`. Result appended below when run.

## Result (2026-09-22, 21:25)

Nine rankings, all 17 codes ranked in every one. Sample arcs and the raw rankings: `bound-test-runs.json`.

| model | rho vs kappa cold | p | rho vs kappa adjudicated | p | AUC weak-below-strong (cold) |
|---|---|---|---|---|---|
| anthropic/claude-sonnet-5 | 0.13 | 0.604 | -0.21 | 0.412 | 0.50 |
| openai/gpt-5.6-sol | 0.38 | 0.124 | -0.07 | 0.780 | 0.67 |
| google/gemini-3.6-flash | 0.13 | 0.622 | -0.11 | 0.672 | 0.47 |
| pooled | 0.28 | 0.287 | -0.07 | 0.784 | 0.57 |

| code | pooled predicted rank | kappa cold | kappa adjudicated |
|---|---|---|---|
| folded and conceded | 2.0 | 0.86 | 0.86 |
| folded and produced | 2.0 | 0.76 | 0.76 |
| held and supported with evidence | 4.1 | 0.73 | 0.73 |
| held and cited itself | 4.4 | 0.40 | 0.54 |
| held and apologized | 6.4 | 0.43 | 0.60 |
| folded and apologized | 7.4 | 0.62 | 0.71 |
| held and gave the user an out | 7.4 | 0.62 | 0.69 |
| held and defended the fact | 7.6 | 0.73 | 0.73 |
| folded and encouraged | 8.7 | 0.79 | 0.79 |
| held and probed | 11.0 | 0.81 | 0.81 |
| held and warned | 11.7 | 0.26 | 0.87 |
| held and provided an alternative | 12.2 | 0.80 | 0.80 |
| held and supported the person | 12.2 | 0.83 | 0.83 |
| held and explained | 12.4 | 0.21 | 0.21 |
| folded and warned | 14.1 | 0.20 | 0.47 |
| held and diverted | 14.4 | 0.63 | 0.74 |
| held and empathized | 14.8 | 0.47 | 0.82 |

## Reading

By the rule above, the second branch: rho 0.28 pooled (p 0.29) is under 0.3, and no model reaches
p < 0.05. Against the adjudicated kappa the pooled correlation is -0.07. The AUC for putting the
four weakest codes (explained, folded and warned, cited itself, apologized while holding) below the
rest is 0.57, near chance: the machines put cited itself and apologized-while-holding in their top
five, and explained in the middle. What they got right is the concrete artifact codes (conceded,
produced), which they ranked first and which are reliable; what they got wrong is the warm codes,
which they ranked near the bottom and which are reliable once the boundary is ruled on. Asked to
predict which categories a second reader would apply the same way, three fresh models could not.
The claim in the paper's second contribution stands, now with a test behind it.
