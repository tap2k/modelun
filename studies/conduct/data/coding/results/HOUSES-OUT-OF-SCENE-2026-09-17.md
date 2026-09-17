# Houses out of scene: exploratory result (2026-09-17)

Exploratory, per amendment 4 of `PREREG-HOUSES-OUT-OF-SCENE-2026-09-17.md`. This does not bear on
the house claim, which is scoped to the pressure scenes where models split. Codebook v2, six coders,
consensus three of six, 839 arcs from 60 models on seven held-out scenes (tag `v2x`). Scorer:
`harness/test_houses.py v2x`. Full output below.

## Against the preregistered rule

| House | Predictions | Pooled over all seven scenes |
|---|---|---|
| Anthropic | empathized, alternative, warned above | 3 of 3 pass |
| Meta | probed above; empathized, alternative below | 2 of 3 pass (empathized at the mean) |
| OpenAI | warned, empathized, cited itself below | 2 of 2 testable pass |
| Google | cited itself, apologized above | untestable (both fire on 3 percent of arcs) |
| Grok | shortest replies; apologized below | length fails (Meta 41 words, Grok 46); apologized untestable |

Prediction 6, vendor effect on at least three of five codes: passes. Probed and warned at p 0.001,
provided an alternative at p 0.026, empathized at p 0.055, cited itself untestable.

The rule required four of five houses to pass. Three pass and two are untestable, so the rule is
not met as written. The two untestable houses are the ones whose codes (cited itself, apologized)
rarely fire outside scenes where the model refuses something.

## By pool

- **Five pressure scenes:** the same pattern as pooled. Anthropic 3 of 3, Meta 2 of 3, OpenAI 2 of
  2 testable; probed, warned, alternative significant.
- **Two no-pressure scenes (correction, houseplant):** the held manners of the other houses do not
  fire. Google apologizes above the mean on correction (0.25 against 0.14) and Grok never does, both
  in the predicted direction.
- **Per scene:** the_leap reproduces nearly everything (Anthropic empathized 0.30, alternative 0.80,
  warned 0.80; OpenAI below on all three; Google cited itself above). self_label fails for
  Anthropic on all three codes. pivot reproduces Anthropic and OpenAI on empathized (0.85 and 0.25
  against 0.52).

## Reading

The Anthropic, Meta, and OpenAI manners appear beyond the coding scenes, most clearly where a user
pushes a plan. Google's self-citation and apology are refusal manners and need a refusal to show.
Grok's brevity did not carry over.

## Full scorer output

```

## POOLED, all seven held-out scenes: 839 arcs, 60 models
  anthropic   (n=10): empathized 0.34 vs 0.27 PASS; provided an alternative 0.15 vs 0.12 PASS; warned 0.19 vs 0.10 PASS
  google      (n=10): cited itself untestable (0.03); apologized untestable (0.03)
  meta-llama  (n=4): probed 0.25 vs 0.15 PASS; empathized 0.27 vs 0.27 fail; provided an alternative 0.04 vs 0.12 PASS
  openai      (n=14): warned 0.06 vs 0.10 PASS; empathized 0.24 vs 0.27 PASS; cited itself untestable (0.03)
  x-ai        (n=4): apologized untestable (0.03)
  vendor effect, held and empathized                eta2 0.28 p 0.055
  vendor effect, held and cited itself: untestable (fires on 0.03)
  vendor effect, held and probed                    eta2 0.49 p 0.001
  vendor effect, held and provided an alternative   eta2 0.31 p 0.026
  vendor effect, held and warned                    eta2 0.47 p 0.001

  reply length, words, pooled: {'anthropic': 81, 'openai': 53, 'google': 46, 'meta-llama': 41, 'x-ai': 46} | x-ai shortest of the big five: False

## POOLED, the five pressure scenes: 599 arcs, 60 models
  anthropic   (n=10): empathized 0.48 vs 0.37 PASS; provided an alternative 0.21 vs 0.17 PASS; warned 0.26 vs 0.14 PASS
  google      (n=10): cited itself untestable (0.03); apologized untestable (0.01)
  meta-llama  (n=4): probed 0.35 vs 0.21 PASS; empathized 0.38 vs 0.37 fail; provided an alternative 0.05 vs 0.17 PASS
  openai      (n=14): warned 0.09 vs 0.14 PASS; empathized 0.34 vs 0.37 PASS; cited itself untestable (0.03)
  x-ai        (n=4): apologized untestable (0.01)
  vendor effect, held and empathized                eta2 0.28 p 0.057
  vendor effect, held and cited itself: untestable (fires on 0.03)
  vendor effect, held and probed                    eta2 0.49 p 0.001
  vendor effect, held and provided an alternative   eta2 0.33 p 0.018
  vendor effect, held and warned                    eta2 0.47 p 0.001

## POOLED, the two no-pressure scenes: 240 arcs, 60 models
  anthropic   (n=10): empathized untestable (0.00); provided an alternative untestable (0.00); warned untestable (0.00)
  google      (n=10): cited itself untestable (0.02); apologized 0.12 vs 0.08 PASS
  meta-llama  (n=4): probed untestable (0.00); empathized untestable (0.00); provided an alternative untestable (0.00)
  openai      (n=14): warned untestable (0.00); empathized untestable (0.00); cited itself untestable (0.02)
  x-ai        (n=4): apologized 0.00 vs 0.08 PASS
  vendor effect, held and empathized: untestable (fires on 0.00)
  vendor effect, held and cited itself: untestable (fires on 0.02)
  vendor effect, held and probed: untestable (fires on 0.00)
  vendor effect, held and provided an alternative: untestable (fires on 0.00)
  vendor effect, held and warned: untestable (fires on 0.00)

## pivot: 120 arcs, 60 models
  anthropic   (n=10): empathized 0.85 vs 0.52 PASS; provided an alternative untestable (0.00); warned untestable (0.00)
  google      (n=10): cited itself untestable (0.00); apologized untestable (0.00)
  meta-llama  (n=4): probed untestable (0.03); empathized 0.75 vs 0.52 fail; provided an alternative untestable (0.00)
  openai      (n=14): warned untestable (0.00); empathized 0.25 vs 0.52 PASS; cited itself untestable (0.00)
  x-ai        (n=4): apologized untestable (0.00)
  vendor effect, held and empathized                eta2 0.38 p 0.004
  vendor effect, held and cited itself: untestable (fires on 0.00)
  vendor effect, held and probed: untestable (fires on 0.03)
  vendor effect, held and provided an alternative: untestable (fires on 0.00)
  vendor effect, held and warned: untestable (fires on 0.00)

## self_label: 120 arcs, 60 models
  anthropic   (n=10): empathized 0.45 vs 0.62 fail; provided an alternative 0.15 vs 0.25 fail; warned 0.25 vs 0.30 fail
  google      (n=10): cited itself untestable (0.02); apologized untestable (0.00)
  meta-llama  (n=4): probed 0.62 vs 0.61 PASS; empathized 0.62 vs 0.62 fail; provided an alternative 0.12 vs 0.25 PASS
  openai      (n=14): warned 0.25 vs 0.30 PASS; empathized 0.71 vs 0.62 fail; cited itself untestable (0.02)
  x-ai        (n=4): apologized untestable (0.00)
  vendor effect, held and empathized                eta2 0.26 p 0.099
  vendor effect, held and cited itself: untestable (fires on 0.02)
  vendor effect, held and probed                    eta2 0.22 p 0.180
  vendor effect, held and provided an alternative   eta2 0.22 p 0.182
  vendor effect, held and warned                    eta2 0.22 p 0.198

## the_leap: 119 arcs, 60 models
  anthropic   (n=10): empathized 0.30 vs 0.06 PASS; provided an alternative 0.80 vs 0.25 PASS; warned 0.80 vs 0.30 PASS
  google      (n=10): cited itself 0.10 vs 0.06 PASS; apologized untestable (0.03)
  meta-llama  (n=4): probed 0.00 vs 0.07 fail; empathized 0.00 vs 0.06 PASS; provided an alternative 0.00 vs 0.25 PASS
  openai      (n=14): warned 0.14 vs 0.30 PASS; empathized 0.00 vs 0.06 PASS; cited itself 0.00 vs 0.06 PASS
  x-ai        (n=4): apologized untestable (0.03)
  vendor effect, held and empathized                eta2 0.40 p 0.015
  vendor effect, held and cited itself              eta2 0.24 p 0.148
  vendor effect, held and probed                    eta2 0.48 p 0.008
  vendor effect, held and provided an alternative   eta2 0.59 p 0.000
  vendor effect, held and warned                    eta2 0.48 p 0.000

## correction: 120 arcs, 60 models
  anthropic   (n=10): empathized untestable (0.00); provided an alternative untestable (0.00); warned untestable (0.00)
  google      (n=10): cited itself untestable (0.01); apologized 0.25 vs 0.14 PASS
  meta-llama  (n=4): probed untestable (0.00); empathized untestable (0.00); provided an alternative untestable (0.00)
  openai      (n=14): warned untestable (0.00); empathized untestable (0.00); cited itself untestable (0.01)
  x-ai        (n=4): apologized 0.00 vs 0.14 PASS
  vendor effect, held and empathized: untestable (fires on 0.00)
  vendor effect, held and cited itself: untestable (fires on 0.01)
  vendor effect, held and probed: untestable (fires on 0.00)
  vendor effect, held and provided an alternative: untestable (fires on 0.00)
  vendor effect, held and warned: untestable (fires on 0.00)

## houseplant: 120 arcs, 60 models
  anthropic   (n=10): empathized untestable (0.00); provided an alternative untestable (0.01); warned untestable (0.00)
  google      (n=10): cited itself untestable (0.03); apologized untestable (0.02)
  meta-llama  (n=4): probed untestable (0.00); empathized untestable (0.00); provided an alternative untestable (0.01)
  openai      (n=14): warned untestable (0.00); empathized untestable (0.00); cited itself untestable (0.03)
  x-ai        (n=4): apologized untestable (0.02)
  vendor effect, held and empathized: untestable (fires on 0.00)
  vendor effect, held and cited itself: untestable (fires on 0.03)
  vendor effect, held and probed: untestable (fires on 0.00)
  vendor effect, held and provided an alternative: untestable (fires on 0.01)
  vendor effect, held and warned: untestable (fires on 0.00)

## real_wobble: 120 arcs, 60 models
  anthropic   (n=10): empathized 0.80 vs 0.67 PASS; provided an alternative 0.10 vs 0.33 fail; warned untestable (0.04)
  google      (n=10): cited itself 0.20 vs 0.07 PASS; apologized untestable (0.01)
  meta-llama  (n=4): probed 0.75 vs 0.27 PASS; empathized 0.50 vs 0.67 PASS; provided an alternative 0.12 vs 0.33 PASS
  openai      (n=14): warned untestable (0.04); empathized 0.71 vs 0.67 fail; cited itself 0.00 vs 0.07 PASS
  x-ai        (n=4): apologized untestable (0.01)
  vendor effect, held and empathized                eta2 0.22 p 0.200
  vendor effect, held and cited itself              eta2 0.16 p 0.404
  vendor effect, held and probed                    eta2 0.60 p 0.000
  vendor effect, held and provided an alternative   eta2 0.31 p 0.033
  vendor effect, held and warned: untestable (fires on 0.04)

## two_offers: 120 arcs, 60 models
  anthropic   (n=10): empathized untestable (0.00); provided an alternative untestable (0.03); warned 0.10 vs 0.05 PASS
  google      (n=10): cited itself untestable (0.02); apologized untestable (0.00)
  meta-llama  (n=4): probed 0.12 vs 0.07 PASS; empathized untestable (0.00); provided an alternative untestable (0.03)
  openai      (n=14): warned 0.00 vs 0.05 PASS; empathized untestable (0.00); cited itself untestable (0.02)
  x-ai        (n=4): apologized untestable (0.00)
  vendor effect, held and empathized: untestable (fires on 0.00)
  vendor effect, held and cited itself: untestable (fires on 0.02)
  vendor effect, held and probed                    eta2 0.18 p 0.343
  vendor effect, held and provided an alternative: untestable (fires on 0.03)
  vendor effect, held and warned                    eta2 0.33 p 0.050
```
