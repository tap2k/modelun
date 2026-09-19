# Are the vendor effects the coders reading their own family? (2026-09-19)

Two of the six coders come from each of Anthropic, Google and OpenAI, and those three labs are
among the vendors the paper profiles. The test: rebuild the consensus with one vendor's two
coders left out (four coders, a code present when two or more mark it, the analogue of three of
six) and rerun the vendor effect. Script: harness/manner_matrix.py --drop-coder-vendor.

| code | all six | Anthropic's coders out | Google's coders out | OpenAI's coders out |
|---|---|---|---|---|
| produced | 0.56 (p 0.000) | 0.62 (p 0.000) | 0.58 (p 0.000) | 0.56 (p 0.000) |
| empathized | 0.59 (p 0.000) | 0.57 (p 0.000) | 0.58 (p 0.000) | 0.64 (p 0.000) |
| folded: warned | 0.58 (p 0.000) | 0.54 (p 0.000) | 0.43 (p 0.003) | 0.67 (p 0.000) |
| held: warned | 0.55 (p 0.000) | 0.56 (p 0.000) | 0.51 (p 0.000) | 0.57 (p 0.000) |
| cited itself | 0.52 (p 0.000) | 0.46 (p 0.000) | 0.47 (p 0.001) | 0.46 (p 0.001) |
| provided an alternative | 0.43 (p 0.001) | 0.41 (p 0.002) | 0.35 (p 0.010) | 0.43 (p 0.001) |
| probed | 0.36 (p 0.007) | 0.41 (p 0.002) | 0.40 (p 0.002) | 0.36 (p 0.006) |

Every effect survives every drop. Held and empathized, Anthropic's signature at 0.77, stays at 0.57
with Anthropic's own two coders out of the consensus; held and cited itself, Google's at 0.37, stays
at 0.47 with Google's coders out. No code loses significance at 0.05 in any arm. Codebook v2, the
three coded scenes, sixty models.
