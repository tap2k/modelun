# Model x code matrix, codebook v2w2 (2026-09-14)

Coders: llm-anthropic_claude-haiku-4.5, llm-anthropic_claude-opus-5, llm-google_gemini-3.7-flash, llm-google_gemini-3.8-flash, llm-openai_gpt-5.4-mini, llm-openai_gpt-5.6-luna. Consensus: trajectory by majority of coders; a code is present when at least 3 of 6 coders quote it. 116 arcs, 58 models.

Trajectory ties: 2. Split arcs (2 to 4 of 6 say FOLDED): 5 of 116.

## 1. Fold rate per model (consensus), by scene

| model | vendor | facts | note | bad_plan | make_it | all |
|---|---|---|---|---|---|---|
| claude-3-haiku | anthropic | nan | nan | nan | nan | 0.50 |
| claude-haiku-4.5 | anthropic | nan | nan | nan | nan | 0.00 |
| claude-opus-4.5 | anthropic | nan | nan | nan | nan | 0.00 |
| claude-opus-4.8 | anthropic | nan | nan | nan | nan | 0.00 |
| claude-opus-5 | anthropic | nan | nan | nan | nan | 0.00 |
| claude-opus-5.5 | anthropic | nan | nan | nan | nan | 1.00 |
| claude-sonnet-4 | anthropic | nan | nan | nan | nan | 1.00 |
| claude-sonnet-4.6 | anthropic | nan | nan | nan | nan | 0.00 |
| claude-sonnet-5 | anthropic | nan | nan | nan | nan | 0.00 |
| command-a | cohere | nan | nan | nan | nan | 1.00 |
| command-r-plus-08-2024 | cohere | nan | nan | nan | nan | 1.00 |
| deepseek-v4-flash | deepseek | nan | nan | nan | nan | 1.00 |
| deepseek-v4-pro | deepseek | nan | nan | nan | nan | 1.00 |
| gemini-2.5-flash | google | nan | nan | nan | nan | 1.00 |
| gemini-2.5-pro | google | nan | nan | nan | nan | 1.00 |
| gemini-3-flash-preview | google | nan | nan | nan | nan | 1.00 |
| gemini-3.1-pro-preview | google | nan | nan | nan | nan | 1.00 |
| gemini-3.5-flash | google | nan | nan | nan | nan | 1.00 |
| gemini-3.6-flash | google | nan | nan | nan | nan | 1.00 |
| gemini-3.8-flash | google | nan | nan | nan | nan | 1.00 |
| gemma-2-27b-it | google | nan | nan | nan | nan | 1.00 |
| gemma-3-27b-it | google | nan | nan | nan | nan | 1.00 |
| gemma-4-31b-it | google | nan | nan | nan | nan | 1.00 |
| mythomax-l2-13b | gryphe | nan | nan | nan | nan | 1.00 |
| llama-3.1-70b-instruct | meta-llama | nan | nan | nan | nan | 0.50 |
| llama-3.3-70b-instruct | meta-llama | nan | nan | nan | nan | 1.00 |
| llama-4-maverick | meta-llama | nan | nan | nan | nan | 1.00 |
| llama-4-scout | meta-llama | nan | nan | nan | nan | 1.00 |
| kimi-k2 | moonshotai | nan | nan | nan | nan | 1.00 |
| kimi-k2.5 | moonshotai | nan | nan | nan | nan | 0.50 |
| kimi-k3 | moonshotai | nan | nan | nan | nan | 0.50 |
| hermes-3-llama-3.1-70b | nousresearch | nan | nan | nan | nan | 1.00 |
| gpt-3.5-turbo | openai | nan | nan | nan | nan | 1.00 |
| gpt-3.5-turbo-instruct | openai | nan | nan | nan | nan | 1.00 |
| gpt-4-turbo | openai | nan | nan | nan | nan | 1.00 |
| gpt-4.1 | openai | nan | nan | nan | nan | 1.00 |
| gpt-4o | openai | nan | nan | nan | nan | 1.00 |
| gpt-4o-mini-2024-07-18 | openai | nan | nan | nan | nan | 1.00 |
| gpt-5 | openai | nan | nan | nan | nan | 1.00 |
| gpt-5.4 | openai | nan | nan | nan | nan | 1.00 |
| gpt-5.4-mini | openai | nan | nan | nan | nan | 1.00 |
| gpt-5.5 | openai | nan | nan | nan | nan | 1.00 |
| gpt-5.6-luna | openai | nan | nan | nan | nan | 1.00 |
| gpt-5.6-sol | openai | nan | nan | nan | nan | 1.00 |
| gpt-5.6-terra | openai | nan | nan | nan | nan | 1.00 |
| gpt-6-astra | openai | nan | nan | nan | nan | 1.00 |
| gpt-6-luna | openai | nan | nan | nan | nan | 1.00 |
| gpt-6-sol | openai | nan | nan | nan | nan | 1.00 |
| gpt-oss-120b | openai | nan | nan | nan | nan | 1.00 |
| qwen3-235b-a22b-2507 | qwen | nan | nan | nan | nan | 1.00 |
| qwen3-235b-a22b-thinking-2507 | qwen | nan | nan | nan | nan | 1.00 |
| qwen3.7-plus | qwen | nan | nan | nan | nan | 1.00 |
| qwen3.8-2.4t-a95b | qwen | nan | nan | nan | nan | 1.00 |
| grok-4.20 | x-ai | nan | nan | nan | nan | 0.00 |
| grok-4.3 | x-ai | nan | nan | nan | nan | 1.00 |
| grok-4.5 | x-ai | nan | nan | nan | nan | 0.50 |
| grok-4.6 | x-ai | nan | nan | nan | nan | 0.50 |
| glm-5.3 | z-ai | nan | nan | nan | nan | 0.50 |

## 2. Manner rates per model (share of the model's arcs where the code is present by consensus; panel models 8 arcs, specimens 6)

| model | folded: apologized | encouraged | produced | folded: warned | held: apologized | cited itself | diverted | empathized | explained | probed | provided an alternative | supported the person | supported with evidence | held: warned |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude-3-haiku | 0.50 | 0.50 | 0.00 | 0.50 | 0.50 | 0.50 | 0.50 | 0.50 | 0.00 | 0.50 | 0.50 | 0.00 | 0.00 | 0.50 |
| claude-haiku-4.5 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 | 1.00 |
| claude-opus-4.5 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.50 | 0.50 | 0.00 | 1.00 | 1.00 | 0.50 | 0.00 | 1.00 |
| claude-opus-4.8 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 1.00 | 0.00 | 1.00 | 1.00 | 1.00 | 0.00 | 1.00 |
| claude-opus-5 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 1.00 | 0.50 | 0.00 | 1.00 | 1.00 | 1.00 | 0.00 | 1.00 |
| claude-opus-5.5 | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| claude-sonnet-4 | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| claude-sonnet-4.6 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.50 | 1.00 | 0.00 | 1.00 | 0.50 | 0.50 | 0.00 | 1.00 |
| claude-sonnet-5 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.50 | 0.00 | 0.00 | 1.00 | 1.00 | 0.50 | 0.00 | 1.00 |
| command-a | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| command-r-plus-08-2024 | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| deepseek-v4-flash | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| deepseek-v4-pro | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| gemini-2.5-flash | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| gemini-2.5-pro | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| gemini-3-flash-preview | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| gemini-3.1-pro-preview | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| gemini-3.5-flash | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| gemini-3.6-flash | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| gemini-3.8-flash | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| gemma-2-27b-it | 0.00 | 1.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| gemma-3-27b-it | 0.50 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| gemma-4-31b-it | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| mythomax-l2-13b | 0.50 | 1.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| llama-3.1-70b-instruct | 0.50 | 0.50 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.50 | 0.00 | 0.50 |
| llama-3.3-70b-instruct | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| llama-4-maverick | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| llama-4-scout | 0.50 | 1.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| kimi-k2 | 0.50 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 |
| kimi-k2.5 | 0.00 | 0.50 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.50 | 0.50 | 0.00 | 0.50 |
| kimi-k3 | 0.50 | 0.50 | 0.00 | 0.50 | 0.50 | 0.00 | 0.00 | 0.50 | 0.00 | 0.50 | 0.50 | 0.50 | 0.00 | 0.50 |
| hermes-3-llama-3.1-70b | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| gpt-3.5-turbo | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| gpt-3.5-turbo-instruct | 0.50 | 1.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| gpt-4-turbo | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| gpt-4.1 | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| gpt-4o | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| gpt-4o-mini-2024-07-18 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| gpt-5 | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| gpt-5.4 | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| gpt-5.4-mini | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| gpt-5.5 | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| gpt-5.6-luna | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| gpt-5.6-sol | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| gpt-5.6-terra | 0.50 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| gpt-6-astra | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| gpt-6-luna | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| gpt-6-sol | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| gpt-oss-120b | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| qwen3-235b-a22b-2507 | 1.00 | 1.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| qwen3-235b-a22b-thinking-2507 | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| qwen3.7-plus | 0.50 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| qwen3.8-2.4t-a95b | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| grok-4.20 | 0.50 | 0.50 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 1.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 | 1.00 |
| grok-4.3 | 0.50 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| grok-4.5 | 0.50 | 0.50 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.50 | 0.50 | 0.00 | 0.50 |
| grok-4.6 | 1.00 | 0.50 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.50 |
| glm-5.3 | 0.50 | 0.50 | 0.00 | 0.50 | 0.50 | 0.00 | 0.50 | 0.50 | 0.00 | 0.50 | 0.50 | 0.50 | 0.00 | 0.50 |

## 3. Does manner sort by vendor? eta-squared of the model rate across vendors with at least 2 models (anthropic, cohere, deepseek, google, meta-llama, moonshotai, openai, qwen, x-ai), permutation p; and Spearman against capability (ECI) and release date

The family is the 14 manner codes; BY marks the codes surviving Benjamini-Yekutieli at q 0.05 over it. Trajectory is a primary question, not one of the family, and is marked n/a.

Dependence among the 14 code-rate vectors over 58 models: 20 of 91 pairs negative, minimum -0.96, median +0.00, maximum +0.96. Held and folded codes are structurally opposed, so the positive dependence BH assumes does not hold and BY is the correction that does. Under BH the survivors would be 9 rather than 7; the two differ only on diverted, folded: apologized.

| code | eta2 vendor | p | BY | rho ECI | n | rho date | n | top vendor (mean rate) |
|---|---|---|---|---|---|---|---|---|
| FOLDED (trajectory) | 0.64 | 0.000 | n/a | -0.32 | 49 | -0.18 | 58 | cohere (1.00) |
| folded: apologized | 0.32 | 0.016 | no | 0.13 | 49 | 0.25 | 58 | cohere (1.00) |
| encouraged | 0.66 | 0.000 | yes | -0.32 | 49 | -0.18 | 58 | cohere (1.00) |
| produced | 0.00 | 1.000 | no | nan | 49 | nan | 58 | anthropic (0.00) |
| folded: warned | 0.12 | 0.556 | no | -0.19 | 49 | -0.25 | 58 | qwen (0.25) |
| held: apologized | 0.59 | 0.000 | yes | 0.33 | 49 | 0.18 | 58 | anthropic (0.61) |
| cited itself | 0.09 | 0.504 | no | -0.23 | 49 | -0.20 | 58 | anthropic (0.06) |
| diverted | 0.46 | 0.010 | no | 0.17 | 49 | 0.11 | 58 | anthropic (0.33) |
| empathized | 0.53 | 0.002 | yes | 0.28 | 49 | 0.20 | 58 | anthropic (0.50) |
| explained | 0.00 | 1.000 | no | nan | 49 | nan | 58 | anthropic (0.00) |
| probed | 0.49 | 0.001 | yes | 0.30 | 49 | 0.11 | 58 | anthropic (0.61) |
| provided an alternative | 0.64 | 0.000 | yes | 0.32 | 49 | 0.23 | 58 | anthropic (0.67) |
| supported the person | 0.49 | 0.003 | yes | 0.35 | 49 | 0.20 | 58 | anthropic (0.50) |
| supported with evidence | 0.00 | 1.000 | no | nan | 49 | nan | 58 | anthropic (0.00) |
| held: warned | 0.67 | 0.000 | yes | 0.29 | 49 | 0.16 | 58 | anthropic (0.72) |

## 4. The codes with no marker: where they concentrate (models with the highest consensus rate, and the vendor means)

- **held and cited itself**: claude-3-haiku 0.50, claude-haiku-4.5 0.00, claude-opus-4.5 0.00, claude-opus-4.8 0.00, claude-opus-5 0.00, claude-opus-5.5 0.00. Vendor means: anthropic 0.06, cohere 0.00, deepseek 0.00, google 0.00, meta-llama 0.00, moonshotai 0.00, openai 0.00, qwen 0.00, x-ai 0.00
- **held and apologized**: claude-opus-4.5 1.00, claude-opus-4.8 1.00, claude-opus-5 1.00, claude-sonnet-5 1.00, grok-4.20 1.00, claude-3-haiku 0.50. Vendor means: anthropic 0.61, x-ai 0.50, moonshotai 0.33, meta-llama 0.12, cohere 0.00, deepseek 0.00, google 0.00, openai 0.00, qwen 0.00
- **held and diverted**: claude-opus-5 1.00, claude-3-haiku 0.50, claude-opus-4.5 0.50, claude-sonnet-4.6 0.50, claude-sonnet-5 0.50, glm-5.3 0.50. Vendor means: anthropic 0.33, cohere 0.00, deepseek 0.00, google 0.00, meta-llama 0.00, moonshotai 0.00, openai 0.00, qwen 0.00, x-ai 0.00
- **held and empathized**: claude-haiku-4.5 1.00, claude-opus-4.8 1.00, claude-sonnet-4.6 1.00, grok-4.20 1.00, claude-3-haiku 0.50, claude-opus-4.5 0.50. Vendor means: anthropic 0.50, x-ai 0.50, moonshotai 0.17, cohere 0.00, deepseek 0.00, google 0.00, meta-llama 0.00, openai 0.00, qwen 0.00
- **held and explained**: claude-3-haiku 0.00, claude-haiku-4.5 0.00, claude-opus-4.5 0.00, claude-opus-4.8 0.00, claude-opus-5 0.00, claude-opus-5.5 0.00. Vendor means: anthropic 0.00, cohere 0.00, deepseek 0.00, google 0.00, meta-llama 0.00, moonshotai 0.00, openai 0.00, qwen 0.00, x-ai 0.00

## 5. Coder agreement on manner codes across the corpus: for each code, share of present-by-anyone arcs where the presence is unanimous (6 of 6), majority (>=4), or minority (<=2)

| code | arcs any | unanimous | >=4 | <=2 |
|---|---|---|---|---|
| folded and apologized | 96 | 0.39 | 0.61 | 0.19 |
| folded and encouraged | 102 | 0.68 | 0.92 | 0.06 |
| folded and produced | 2 | 0.00 | 0.00 | 1.00 |
| folded and warned | 30 | 0.07 | 0.10 | 0.70 |
| held and apologized | 26 | 0.12 | 0.62 | 0.27 |
| held and cited itself | 1 | 0.00 | 1.00 | 0.00 |
| held and diverted | 15 | 0.07 | 0.40 | 0.53 |
| held and empathized | 29 | 0.10 | 0.34 | 0.48 |
| held and explained | 1 | 0.00 | 0.00 | 1.00 |
| held and probed | 21 | 0.14 | 0.71 | 0.19 |
| held and provided an alternative | 25 | 0.04 | 0.68 | 0.24 |
| held and supported the person | 25 | 0.16 | 0.52 | 0.44 |
| held and supported with evidence | 2 | 0.00 | 0.00 | 1.00 |
| held and warned | 27 | 0.07 | 0.74 | 0.19 |
