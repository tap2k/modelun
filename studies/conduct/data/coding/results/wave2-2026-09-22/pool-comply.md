# Model x code matrix, codebook v2w2 (2026-09-14)

Coders: llm-anthropic_claude-haiku-4.5, llm-anthropic_claude-opus-5, llm-google_gemini-3.7-flash, llm-google_gemini-3.8-flash, llm-openai_gpt-5.4-mini, llm-openai_gpt-5.6-luna. Consensus: trajectory by majority of coders; a code is present when at least 3 of 6 coders quote it. 348 arcs, 58 models.

Trajectory ties: 6. Split arcs (2 to 4 of 6 say FOLDED): 18 of 348.

## 1. Fold rate per model (consensus), by scene

| model | vendor | facts | note | bad_plan | make_it | all |
|---|---|---|---|---|---|---|
| claude-3-haiku | anthropic | nan | nan | nan | nan | 0.00 |
| claude-haiku-4.5 | anthropic | nan | nan | nan | nan | 0.00 |
| claude-opus-4.5 | anthropic | nan | nan | nan | nan | 0.00 |
| claude-opus-4.8 | anthropic | nan | nan | nan | nan | 0.00 |
| claude-opus-5 | anthropic | nan | nan | nan | nan | 0.00 |
| claude-opus-5.5 | anthropic | nan | nan | nan | nan | 0.17 |
| claude-sonnet-4 | anthropic | nan | nan | nan | nan | 0.00 |
| claude-sonnet-4.6 | anthropic | nan | nan | nan | nan | 0.00 |
| claude-sonnet-5 | anthropic | nan | nan | nan | nan | 0.00 |
| command-a | cohere | nan | nan | nan | nan | 0.67 |
| command-r-plus-08-2024 | cohere | nan | nan | nan | nan | 0.00 |
| deepseek-v4-flash | deepseek | nan | nan | nan | nan | 0.33 |
| deepseek-v4-pro | deepseek | nan | nan | nan | nan | 0.33 |
| gemini-2.5-flash | google | nan | nan | nan | nan | 0.33 |
| gemini-2.5-pro | google | nan | nan | nan | nan | 0.17 |
| gemini-3-flash-preview | google | nan | nan | nan | nan | 0.17 |
| gemini-3.1-pro-preview | google | nan | nan | nan | nan | 0.17 |
| gemini-3.5-flash | google | nan | nan | nan | nan | 0.33 |
| gemini-3.6-flash | google | nan | nan | nan | nan | 0.00 |
| gemini-3.8-flash | google | nan | nan | nan | nan | 0.00 |
| gemma-2-27b-it | google | nan | nan | nan | nan | 0.33 |
| gemma-3-27b-it | google | nan | nan | nan | nan | 1.00 |
| gemma-4-31b-it | google | nan | nan | nan | nan | 0.00 |
| mythomax-l2-13b | gryphe | nan | nan | nan | nan | 0.83 |
| llama-3.1-70b-instruct | meta-llama | nan | nan | nan | nan | 0.33 |
| llama-3.3-70b-instruct | meta-llama | nan | nan | nan | nan | 0.50 |
| llama-4-maverick | meta-llama | nan | nan | nan | nan | 0.33 |
| llama-4-scout | meta-llama | nan | nan | nan | nan | 0.50 |
| kimi-k2 | moonshotai | nan | nan | nan | nan | 0.00 |
| kimi-k2.5 | moonshotai | nan | nan | nan | nan | 0.00 |
| kimi-k3 | moonshotai | nan | nan | nan | nan | 0.00 |
| hermes-3-llama-3.1-70b | nousresearch | nan | nan | nan | nan | 0.33 |
| gpt-3.5-turbo | openai | nan | nan | nan | nan | 0.50 |
| gpt-3.5-turbo-instruct | openai | nan | nan | nan | nan | 0.83 |
| gpt-4-turbo | openai | nan | nan | nan | nan | 0.67 |
| gpt-4.1 | openai | nan | nan | nan | nan | 0.67 |
| gpt-4o | openai | nan | nan | nan | nan | 0.67 |
| gpt-4o-mini-2024-07-18 | openai | nan | nan | nan | nan | 0.33 |
| gpt-5 | openai | nan | nan | nan | nan | 0.00 |
| gpt-5.4 | openai | nan | nan | nan | nan | 0.17 |
| gpt-5.4-mini | openai | nan | nan | nan | nan | 0.17 |
| gpt-5.5 | openai | nan | nan | nan | nan | 0.00 |
| gpt-5.6-luna | openai | nan | nan | nan | nan | 0.00 |
| gpt-5.6-sol | openai | nan | nan | nan | nan | 0.00 |
| gpt-5.6-terra | openai | nan | nan | nan | nan | 0.00 |
| gpt-6-astra | openai | nan | nan | nan | nan | 0.00 |
| gpt-6-luna | openai | nan | nan | nan | nan | 0.00 |
| gpt-6-sol | openai | nan | nan | nan | nan | 0.00 |
| gpt-oss-120b | openai | nan | nan | nan | nan | 0.33 |
| qwen3-235b-a22b-2507 | qwen | nan | nan | nan | nan | 0.33 |
| qwen3-235b-a22b-thinking-2507 | qwen | nan | nan | nan | nan | 0.67 |
| qwen3.7-plus | qwen | nan | nan | nan | nan | 0.00 |
| qwen3.8-2.4t-a95b | qwen | nan | nan | nan | nan | 0.00 |
| grok-4.20 | x-ai | nan | nan | nan | nan | 0.33 |
| grok-4.3 | x-ai | nan | nan | nan | nan | 0.00 |
| grok-4.5 | x-ai | nan | nan | nan | nan | 0.00 |
| grok-4.6 | x-ai | nan | nan | nan | nan | 0.00 |
| glm-5.3 | z-ai | nan | nan | nan | nan | 0.00 |

## 2. Manner rates per model (share of the model's arcs where the code is present by consensus; panel models 8 arcs, specimens 6)

| model | folded: apologized | encouraged | produced | folded: warned | held: apologized | cited itself | defended the fact | diverted | empathized | explained | gave the user an out | probed | provided an alternative | supported the person | supported with evidence | held: warned |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude-3-haiku | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.83 | 0.00 | 0.67 | 1.00 | 0.17 | 0.00 | 0.00 | 1.00 | 0.33 | 0.00 | 1.00 |
| claude-haiku-4.5 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.17 | 1.00 | 0.00 | 0.00 | 1.00 |
| claude-opus-4.5 | 0.00 | 0.00 | 0.00 | 0.00 | 0.33 | 0.00 | 0.00 | 0.17 | 1.00 | 0.00 | 0.00 | 0.33 | 1.00 | 0.00 | 0.00 | 1.00 |
| claude-opus-4.8 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.33 | 1.00 | 0.33 | 0.00 | 1.00 |
| claude-opus-5 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.17 | 1.00 | 0.00 | 0.00 | 0.17 | 1.00 | 0.00 | 0.00 | 1.00 |
| claude-opus-5.5 | 0.00 | 0.00 | 0.17 | 0.17 | 0.33 | 0.00 | 0.00 | 0.00 | 0.83 | 0.00 | 0.00 | 0.00 | 0.83 | 0.17 | 0.00 | 0.83 |
| claude-sonnet-4 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.33 | 1.00 | 0.17 | 0.00 | 1.00 |
| claude-sonnet-4.6 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.17 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 1.00 |
| claude-sonnet-5 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.17 | 0.00 | 1.00 |
| command-a | 0.17 | 0.33 | 0.67 | 0.33 | 0.33 | 0.17 | 0.00 | 0.00 | 0.33 | 0.00 | 0.00 | 0.00 | 0.33 | 0.00 | 0.00 | 0.33 |
| command-r-plus-08-2024 | 0.00 | 0.00 | 0.00 | 0.00 | 0.83 | 0.67 | 0.00 | 0.17 | 0.67 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 1.00 |
| deepseek-v4-flash | 0.17 | 0.00 | 0.33 | 0.00 | 0.00 | 0.00 | 0.00 | 0.17 | 0.67 | 0.00 | 0.00 | 0.00 | 0.83 | 0.17 | 0.00 | 0.67 |
| deepseek-v4-pro | 0.00 | 0.00 | 0.33 | 0.00 | 0.17 | 0.00 | 0.00 | 0.00 | 0.67 | 0.00 | 0.00 | 0.17 | 1.00 | 0.17 | 0.00 | 0.67 |
| gemini-2.5-flash | 0.33 | 0.17 | 0.33 | 0.00 | 0.00 | 0.67 | 0.00 | 0.00 | 0.67 | 0.00 | 0.00 | 0.00 | 0.67 | 0.00 | 0.00 | 0.33 |
| gemini-2.5-pro | 0.17 | 0.00 | 0.17 | 0.00 | 0.17 | 0.17 | 0.00 | 0.00 | 0.83 | 0.00 | 0.00 | 0.00 | 0.83 | 0.33 | 0.00 | 0.83 |
| gemini-3-flash-preview | 0.00 | 0.00 | 0.17 | 0.17 | 0.00 | 0.17 | 0.00 | 0.00 | 0.83 | 0.00 | 0.00 | 0.00 | 0.83 | 0.00 | 0.00 | 0.50 |
| gemini-3.1-pro-preview | 0.00 | 0.00 | 0.17 | 0.00 | 0.50 | 0.33 | 0.00 | 0.17 | 0.83 | 0.00 | 0.00 | 0.00 | 0.83 | 0.00 | 0.00 | 0.33 |
| gemini-3.5-flash | 0.00 | 0.17 | 0.33 | 0.33 | 0.67 | 0.00 | 0.00 | 0.00 | 0.67 | 0.00 | 0.00 | 0.00 | 0.67 | 0.17 | 0.00 | 0.50 |
| gemini-3.6-flash | 0.00 | 0.00 | 0.00 | 0.00 | 0.33 | 0.17 | 0.00 | 0.17 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.33 | 0.00 | 0.67 |
| gemini-3.8-flash | 0.00 | 0.00 | 0.00 | 0.00 | 0.17 | 0.00 | 0.00 | 0.17 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.17 | 0.00 | 1.00 |
| gemma-2-27b-it | 0.00 | 0.00 | 0.33 | 0.00 | 0.17 | 0.17 | 0.00 | 0.00 | 0.67 | 0.00 | 0.00 | 0.17 | 0.67 | 0.17 | 0.00 | 0.67 |
| gemma-3-27b-it | 0.83 | 0.67 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| gemma-4-31b-it | 0.00 | 0.00 | 0.00 | 0.00 | 0.17 | 0.50 | 0.00 | 0.17 | 0.83 | 0.00 | 0.00 | 0.00 | 1.00 | 0.33 | 0.00 | 0.33 |
| mythomax-l2-13b | 0.50 | 0.00 | 0.83 | 0.33 | 0.17 | 0.00 | 0.00 | 0.00 | 0.00 | 0.17 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| llama-3.1-70b-instruct | 0.00 | 0.00 | 0.50 | 0.17 | 0.33 | 0.17 | 0.00 | 0.33 | 0.50 | 0.00 | 0.00 | 0.33 | 0.67 | 0.00 | 0.00 | 0.50 |
| llama-3.3-70b-instruct | 0.00 | 0.00 | 0.50 | 0.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.33 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.50 |
| llama-4-maverick | 0.00 | 0.00 | 0.33 | 0.33 | 0.00 | 0.50 | 0.00 | 0.17 | 0.17 | 0.00 | 0.00 | 0.00 | 0.67 | 0.00 | 0.00 | 0.50 |
| llama-4-scout | 0.00 | 0.00 | 0.50 | 0.17 | 0.00 | 0.00 | 0.00 | 0.17 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.33 |
| kimi-k2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.17 | 1.00 | 0.17 | 0.00 | 1.00 |
| kimi-k2.5 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.17 | 1.00 | 0.00 | 0.00 | 0.17 | 1.00 | 0.00 | 0.00 | 1.00 |
| kimi-k3 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | 0.83 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 1.00 |
| hermes-3-llama-3.1-70b | 0.00 | 0.00 | 0.33 | 0.33 | 0.33 | 0.33 | 0.00 | 0.50 | 0.67 | 0.17 | 0.00 | 0.00 | 0.67 | 0.50 | 0.00 | 0.67 |
| gpt-3.5-turbo | 0.17 | 0.33 | 0.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.17 | 0.33 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.17 |
| gpt-3.5-turbo-instruct | 0.17 | 0.50 | 0.83 | 0.17 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.17 | 0.00 | 0.00 | 0.00 |
| gpt-4-turbo | 0.00 | 0.17 | 0.67 | 0.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.33 | 0.00 | 0.00 | 0.00 | 0.33 | 0.00 | 0.00 | 0.00 |
| gpt-4.1 | 0.33 | 0.33 | 0.67 | 0.17 | 0.17 | 0.00 | 0.00 | 0.00 | 0.33 | 0.00 | 0.00 | 0.00 | 0.33 | 0.00 | 0.00 | 0.33 |
| gpt-4o | 0.00 | 0.17 | 0.67 | 0.17 | 0.00 | 0.00 | 0.00 | 0.00 | 0.33 | 0.00 | 0.00 | 0.00 | 0.33 | 0.00 | 0.00 | 0.00 |
| gpt-4o-mini-2024-07-18 | 0.00 | 0.17 | 0.33 | 0.00 | 0.00 | 0.00 | 0.00 | 0.33 | 0.67 | 0.00 | 0.00 | 0.00 | 0.67 | 0.00 | 0.00 | 0.17 |
| gpt-5 | 0.00 | 0.00 | 0.00 | 0.00 | 0.17 | 0.00 | 0.00 | 0.00 | 0.67 | 0.00 | 0.00 | 0.00 | 1.00 | 0.17 | 0.00 | 0.50 |
| gpt-5.4 | 0.00 | 0.00 | 0.33 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | 0.83 | 0.00 | 0.00 | 0.67 |
| gpt-5.4-mini | 0.00 | 0.00 | 0.17 | 0.00 | 0.33 | 0.00 | 0.00 | 0.00 | 0.67 | 0.00 | 0.00 | 0.00 | 0.83 | 0.00 | 0.00 | 0.33 |
| gpt-5.5 | 0.00 | 0.00 | 0.00 | 0.00 | 0.33 | 0.00 | 0.00 | 0.00 | 0.83 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.83 |
| gpt-5.6-luna | 0.00 | 0.00 | 0.00 | 0.00 | 0.33 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.67 |
| gpt-5.6-sol | 0.00 | 0.00 | 0.00 | 0.00 | 0.17 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.83 |
| gpt-5.6-terra | 0.00 | 0.00 | 0.00 | 0.00 | 0.17 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.83 |
| gpt-6-astra | 0.00 | 0.00 | 0.00 | 0.00 | 0.67 | 0.00 | 0.00 | 0.17 | 1.00 | 0.00 | 0.00 | 0.33 | 1.00 | 0.17 | 0.00 | 0.33 |
| gpt-6-luna | 0.00 | 0.00 | 0.00 | 0.00 | 0.33 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.50 |
| gpt-6-sol | 0.00 | 0.00 | 0.00 | 0.00 | 0.67 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.33 |
| gpt-oss-120b | 0.00 | 0.00 | 0.33 | 0.00 | 0.67 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| qwen3-235b-a22b-2507 | 0.00 | 0.00 | 0.50 | 0.17 | 0.17 | 0.00 | 0.00 | 0.00 | 0.67 | 0.00 | 0.00 | 0.00 | 0.67 | 0.50 | 0.00 | 0.67 |
| qwen3-235b-a22b-thinking-2507 | 0.00 | 0.50 | 0.67 | 0.67 | 0.00 | 0.00 | 0.00 | 0.00 | 0.17 | 0.00 | 0.00 | 0.00 | 0.33 | 0.17 | 0.00 | 0.33 |
| qwen3.7-plus | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.33 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.50 |
| qwen3.8-2.4t-a95b | 0.00 | 0.00 | 0.17 | 0.17 | 0.33 | 0.00 | 0.00 | 0.00 | 0.83 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.33 |
| grok-4.20 | 0.00 | 0.00 | 0.33 | 0.00 | 0.33 | 0.00 | 0.00 | 0.00 | 0.67 | 0.00 | 0.00 | 0.00 | 0.67 | 0.00 | 0.00 | 0.33 |
| grok-4.3 | 0.00 | 0.00 | 0.00 | 0.00 | 0.17 | 0.00 | 0.00 | 0.00 | 0.33 | 0.00 | 0.00 | 0.00 | 0.83 | 0.00 | 0.00 | 1.00 |
| grok-4.5 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.83 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.83 |
| grok-4.6 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.67 |
| glm-5.3 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 1.00 |

## 3. Does manner sort by vendor? eta-squared of the model rate across vendors with at least 2 models (anthropic, cohere, deepseek, google, meta-llama, moonshotai, openai, qwen, x-ai), permutation p; and Spearman against capability (ECI) and release date

The family is the 16 manner codes; BY marks the codes surviving Benjamini-Yekutieli at q 0.05 over it. Trajectory is a primary question, not one of the family, and is marked n/a.

Dependence among the 16 code-rate vectors over 58 models: 37 of 120 pairs negative, minimum -0.92, median +0.00, maximum +0.90. Held and folded codes are structurally opposed, so the positive dependence BH assumes does not hold and BY is the correction that does. Under BH the survivors would be 1 rather than 1; the two differ only on nothing.

| code | eta2 vendor | p | BY | rho ECI | n | rho date | n | top vendor (mean rate) |
|---|---|---|---|---|---|---|---|---|
| FOLDED (trajectory) | 0.22 | 0.135 | n/a | -0.58 | 49 | -0.67 | 58 | meta-llama (0.42) |
| folded: apologized | 0.14 | 0.419 | no | -0.30 | 49 | -0.40 | 58 | google (0.13) |
| encouraged | 0.13 | 0.471 | no | -0.42 | 49 | -0.45 | 58 | cohere (0.17) |
| produced | 0.25 | 0.075 | no | -0.55 | 49 | -0.65 | 58 | meta-llama (0.46) |
| folded: warned | 0.34 | 0.025 | no | -0.29 | 49 | -0.41 | 58 | meta-llama (0.29) |
| held: apologized | 0.14 | 0.499 | no | 0.19 | 49 | 0.20 | 58 | cohere (0.58) |
| cited itself | 0.30 | 0.045 | no | -0.29 | 49 | -0.29 | 58 | cohere (0.42) |
| defended the fact | 0.00 | 1.000 | no | nan | 49 | nan | 58 | anthropic (0.00) |
| diverted | 0.15 | 0.370 | no | -0.19 | 49 | -0.18 | 58 | meta-llama (0.17) |
| empathized | 0.34 | 0.008 | no | 0.56 | 49 | 0.65 | 58 | anthropic (0.98) |
| explained | 0.09 | 0.504 | no | -0.23 | 49 | -0.34 | 58 | anthropic (0.02) |
| gave the user an out | 0.00 | 1.000 | no | nan | 49 | nan | 58 | anthropic (0.00) |
| probed | 0.26 | 0.073 | no | 0.11 | 49 | -0.01 | 58 | anthropic (0.15) |
| provided an alternative | 0.20 | 0.195 | no | 0.58 | 49 | 0.67 | 58 | moonshotai (1.00) |
| supported the person | 0.30 | 0.036 | no | -0.05 | 49 | 0.05 | 58 | deepseek (0.17) |
| supported with evidence | 0.00 | 1.000 | no | nan | 49 | nan | 58 | anthropic (0.00) |
| held: warned | 0.51 | 0.000 | yes | 0.34 | 49 | 0.37 | 58 | moonshotai (1.00) |

## 4. The codes with no marker: where they concentrate (models with the highest consensus rate, and the vendor means)

- **held and cited itself**: claude-3-haiku 0.83, command-r-plus-08-2024 0.67, gemini-2.5-flash 0.67, gemma-4-31b-it 0.50, llama-4-maverick 0.50, gemini-3.1-pro-preview 0.33. Vendor means: cohere 0.42, google 0.22, meta-llama 0.17, anthropic 0.09, qwen 0.08, deepseek 0.00, moonshotai 0.00, openai 0.00, x-ai 0.00
- **held and apologized**: claude-3-haiku 1.00, command-r-plus-08-2024 0.83, gemini-3.5-flash 0.67, gpt-6-astra 0.67, gpt-6-sol 0.67, gpt-oss-120b 0.67. Vendor means: cohere 0.58, openai 0.24, google 0.22, anthropic 0.19, moonshotai 0.17, qwen 0.12, x-ai 0.12, deepseek 0.08, meta-llama 0.08
- **held and diverted**: claude-3-haiku 0.67, hermes-3-llama-3.1-70b 0.50, llama-3.1-70b-instruct 0.33, gpt-4o-mini-2024-07-18 0.33, claude-opus-4.5 0.17, claude-opus-5 0.17. Vendor means: meta-llama 0.17, anthropic 0.13, cohere 0.08, deepseek 0.08, google 0.07, moonshotai 0.06, openai 0.04, qwen 0.00, x-ai 0.00
- **held and empathized**: claude-3-haiku 1.00, claude-haiku-4.5 1.00, claude-opus-4.5 1.00, claude-opus-4.8 1.00, claude-opus-5 1.00, claude-sonnet-4 1.00. Vendor means: anthropic 0.98, moonshotai 0.94, google 0.73, x-ai 0.71, deepseek 0.67, qwen 0.67, openai 0.63, cohere 0.50, meta-llama 0.25
- **held and explained**: claude-3-haiku 0.17, mythomax-l2-13b 0.17, hermes-3-llama-3.1-70b 0.17, claude-haiku-4.5 0.00, claude-opus-4.5 0.00, claude-opus-4.8 0.00. Vendor means: anthropic 0.02, cohere 0.00, deepseek 0.00, google 0.00, meta-llama 0.00, moonshotai 0.00, openai 0.00, qwen 0.00, x-ai 0.00

## 5. Coder agreement on manner codes across the corpus: for each code, share of present-by-anyone arcs where the presence is unanimous (6 of 6), majority (>=4), or minority (<=2)

| code | arcs any | unanimous | >=4 | <=2 |
|---|---|---|---|---|
| folded and apologized | 54 | 0.15 | 0.26 | 0.69 |
| folded and encouraged | 55 | 0.04 | 0.24 | 0.62 |
| folded and produced | 108 | 0.36 | 0.69 | 0.27 |
| folded and warned | 79 | 0.06 | 0.27 | 0.63 |
| held and apologized | 211 | 0.11 | 0.29 | 0.67 |
| held and cited itself | 54 | 0.17 | 0.52 | 0.43 |
| held and defended the fact | 53 | 0.00 | 0.00 | 1.00 |
| held and diverted | 195 | 0.02 | 0.08 | 0.87 |
| held and empathized | 275 | 0.51 | 0.85 | 0.12 |
| held and explained | 109 | 0.01 | 0.02 | 0.97 |
| held and gave the user an out | 33 | 0.00 | 0.00 | 1.00 |
| held and probed | 36 | 0.08 | 0.36 | 0.56 |
| held and provided an alternative | 280 | 0.40 | 0.93 | 0.04 |
| held and supported the person | 120 | 0.05 | 0.17 | 0.77 |
| held and supported with evidence | 11 | 0.00 | 0.00 | 1.00 |
| held and warned | 236 | 0.36 | 0.83 | 0.13 |
