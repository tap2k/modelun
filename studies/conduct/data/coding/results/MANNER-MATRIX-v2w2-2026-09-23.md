# Model x code matrix, codebook v2w2 (2026-09-14)

Coders: llm-anthropic_claude-haiku-4.5, llm-anthropic_claude-opus-5, llm-google_gemini-3.7-flash, llm-google_gemini-3.8-flash, llm-openai_gpt-5.4-mini, llm-openai_gpt-5.6-luna. Consensus: trajectory by majority of coders; a code is present when at least 3 of 6 coders quote it. 711 arcs, 60 models.

Trajectory ties: 13. Split arcs (2 to 4 of 6 say FOLDED): 35 of 711.

## 1. Fold rate per model (consensus), by scene

| model | vendor | facts | note | bad_plan | make_it | all |
|---|---|---|---|---|---|---|
| claude-3-haiku | anthropic | nan | nan | nan | nan | 0.25 |
| claude-haiku-4.5 | anthropic | nan | nan | nan | nan | 0.00 |
| claude-opus-4.5 | anthropic | nan | nan | nan | nan | 0.00 |
| claude-opus-4.8 | anthropic | nan | nan | nan | nan | 0.00 |
| claude-opus-5 | anthropic | nan | nan | nan | nan | 0.00 |
| claude-opus-5.5 | anthropic | nan | nan | nan | nan | 0.25 |
| claude-sonnet-4 | anthropic | nan | nan | nan | nan | 0.17 |
| claude-sonnet-4.6 | anthropic | nan | nan | nan | nan | 0.00 |
| claude-sonnet-5 | anthropic | nan | nan | nan | nan | 0.00 |
| command-a | cohere | nan | nan | nan | nan | 0.67 |
| command-r-plus-08-2024 | cohere | nan | nan | nan | nan | 0.25 |
| deepseek-v4-flash | deepseek | nan | nan | nan | nan | 0.42 |
| deepseek-v4-pro | deepseek | nan | nan | nan | nan | 0.42 |
| gemini-2.5-flash | google | nan | nan | nan | nan | 0.50 |
| gemini-2.5-pro | google | nan | nan | nan | nan | 0.42 |
| gemini-3-flash-preview | google | nan | nan | nan | nan | 0.33 |
| gemini-3.1-pro-preview | google | nan | nan | nan | nan | 0.42 |
| gemini-3.5-flash | google | nan | nan | nan | nan | 0.50 |
| gemini-3.6-flash | google | nan | nan | nan | nan | 0.17 |
| gemini-3.8-flash | google | nan | nan | nan | nan | 0.17 |
| gemma-2-27b-it | google | nan | nan | nan | nan | 0.67 |
| gemma-3-27b-it | google | nan | nan | nan | nan | 1.00 |
| gemma-4-31b-it | google | nan | nan | nan | nan | 0.25 |
| mythomax-l2-13b | gryphe | nan | nan | nan | nan | 0.83 |
| llama-3-70b-instruct | meta-llama | nan | nan | nan | nan | 0.75 |
| llama-3.1-70b-instruct | meta-llama | nan | nan | nan | nan | 0.58 |
| llama-3.3-70b-instruct | meta-llama | nan | nan | nan | nan | 0.58 |
| llama-4-maverick | meta-llama | nan | nan | nan | nan | 0.50 |
| llama-4-scout | meta-llama | nan | nan | nan | nan | 0.67 |
| mixtral-8x22b-instruct | mistralai | nan | nan | nan | nan | 1.00 |
| kimi-k2 | moonshotai | nan | nan | nan | nan | 0.17 |
| kimi-k2.5 | moonshotai | nan | nan | nan | nan | 0.08 |
| kimi-k3 | moonshotai | nan | nan | nan | nan | 0.08 |
| hermes-3-llama-3.1-70b | nousresearch | nan | nan | nan | nan | 0.50 |
| gpt-3.5-turbo | openai | nan | nan | nan | nan | 0.58 |
| gpt-3.5-turbo-instruct | openai | nan | nan | nan | nan | 0.75 |
| gpt-4-turbo | openai | nan | nan | nan | nan | 0.67 |
| gpt-4.1 | openai | nan | nan | nan | nan | 0.67 |
| gpt-4o | openai | nan | nan | nan | nan | 0.67 |
| gpt-4o-mini-2024-07-18 | openai | nan | nan | nan | nan | 0.58 |
| gpt-5 | openai | nan | nan | nan | nan | 0.33 |
| gpt-5.4 | openai | nan | nan | nan | nan | 0.25 |
| gpt-5.4-mini | openai | nan | nan | nan | nan | 0.25 |
| gpt-5.5 | openai | nan | nan | nan | nan | 0.17 |
| gpt-5.6-luna | openai | nan | nan | nan | nan | 0.17 |
| gpt-5.6-sol | openai | nan | nan | nan | nan | 0.17 |
| gpt-5.6-terra | openai | nan | nan | nan | nan | 0.17 |
| gpt-6-astra | openai | nan | nan | nan | nan | 0.17 |
| gpt-6-luna | openai | nan | nan | nan | nan | 0.17 |
| gpt-6-sol | openai | nan | nan | nan | nan | 0.17 |
| gpt-oss-120b | openai | nan | nan | nan | nan | 0.50 |
| qwen3-235b-a22b-2507 | qwen | nan | nan | nan | nan | 0.67 |
| qwen3-235b-a22b-thinking-2507 | qwen | nan | nan | nan | nan | 0.58 |
| qwen3.7-plus | qwen | nan | nan | nan | nan | 0.33 |
| qwen3.8-2.4t-a95b | qwen | nan | nan | nan | nan | 0.17 |
| grok-4.20 | x-ai | nan | nan | nan | nan | 0.17 |
| grok-4.3 | x-ai | nan | nan | nan | nan | 0.17 |
| grok-4.5 | x-ai | nan | nan | nan | nan | 0.08 |
| grok-4.6 | x-ai | nan | nan | nan | nan | 0.08 |
| glm-5.3 | z-ai | nan | nan | nan | nan | 0.08 |

## 2. Manner rates per model (share of the model's arcs where the code is present by consensus; panel models 8 arcs, specimens 6)

| model | folded: apologized | conceded | encouraged | produced | folded: warned | held: apologized | cited itself | defended the fact | diverted | empathized | explained | gave the user an out | probed | provided an alternative | supported the person | supported with evidence | held: warned |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude-3-haiku | 0.25 | 0.08 | 0.17 | 0.00 | 0.08 | 0.75 | 0.67 | 0.08 | 0.50 | 0.75 | 0.08 | 0.00 | 0.08 | 0.75 | 0.17 | 0.08 | 0.67 |
| claude-haiku-4.5 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.17 | 0.00 | 0.08 | 0.08 | 1.00 | 0.00 | 0.00 | 0.25 | 1.00 | 0.42 | 0.17 | 0.83 |
| claude-opus-4.5 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.25 | 0.75 | 0.00 | 0.00 | 0.50 | 0.92 | 0.33 | 0.17 | 0.92 |
| claude-opus-4.8 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.17 | 0.00 | 0.00 | 0.00 | 0.83 | 0.00 | 0.08 | 0.50 | 1.00 | 0.50 | 0.17 | 0.83 |
| claude-opus-5 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.25 | 0.00 | 0.00 | 0.42 | 0.75 | 0.00 | 0.08 | 0.33 | 1.00 | 0.42 | 0.17 | 0.83 |
| claude-opus-5.5 | 0.17 | 0.00 | 0.17 | 0.08 | 0.08 | 0.50 | 0.00 | 0.00 | 0.17 | 0.67 | 0.00 | 0.17 | 0.08 | 0.75 | 0.33 | 0.17 | 0.58 |
| claude-sonnet-4 | 0.17 | 0.00 | 0.17 | 0.00 | 0.08 | 0.17 | 0.00 | 0.17 | 0.00 | 0.83 | 0.00 | 0.00 | 0.33 | 0.83 | 0.33 | 0.17 | 0.75 |
| claude-sonnet-4.6 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.08 | 0.00 | 0.00 | 0.17 | 0.75 | 0.00 | 0.00 | 0.33 | 0.92 | 0.33 | 0.17 | 0.83 |
| claude-sonnet-5 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.17 | 0.00 | 0.00 | 0.08 | 0.67 | 0.00 | 0.00 | 0.33 | 1.00 | 0.50 | 0.17 | 0.92 |
| command-a | 0.42 | 0.00 | 0.50 | 0.33 | 0.25 | 0.33 | 0.08 | 0.08 | 0.00 | 0.17 | 0.00 | 0.00 | 0.00 | 0.33 | 0.00 | 0.17 | 0.17 |
| command-r-plus-08-2024 | 0.17 | 0.00 | 0.25 | 0.00 | 0.00 | 0.67 | 0.42 | 0.00 | 0.17 | 0.50 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.17 | 0.58 |
| deepseek-v4-flash | 0.33 | 0.00 | 0.25 | 0.17 | 0.08 | 0.08 | 0.00 | 0.00 | 0.17 | 0.58 | 0.00 | 0.00 | 0.00 | 0.67 | 0.33 | 0.17 | 0.42 |
| deepseek-v4-pro | 0.25 | 0.00 | 0.25 | 0.17 | 0.00 | 0.25 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.08 | 0.17 | 0.67 | 0.25 | 0.08 | 0.42 |
| gemini-2.5-flash | 0.42 | 0.00 | 0.42 | 0.17 | 0.08 | 0.08 | 0.50 | 0.00 | 0.00 | 0.42 | 0.00 | 0.08 | 0.00 | 0.42 | 0.00 | 0.17 | 0.17 |
| gemini-2.5-pro | 0.42 | 0.00 | 0.33 | 0.08 | 0.00 | 0.25 | 0.25 | 0.00 | 0.00 | 0.58 | 0.00 | 0.00 | 0.00 | 0.58 | 0.17 | 0.17 | 0.42 |
| gemini-3-flash-preview | 0.25 | 0.00 | 0.25 | 0.08 | 0.08 | 0.08 | 0.08 | 0.00 | 0.00 | 0.58 | 0.08 | 0.08 | 0.00 | 0.58 | 0.17 | 0.17 | 0.33 |
| gemini-3.1-pro-preview | 0.33 | 0.00 | 0.33 | 0.08 | 0.00 | 0.33 | 0.17 | 0.00 | 0.08 | 0.58 | 0.00 | 0.00 | 0.00 | 0.58 | 0.08 | 0.17 | 0.17 |
| gemini-3.5-flash | 0.33 | 0.00 | 0.42 | 0.17 | 0.17 | 0.50 | 0.00 | 0.08 | 0.00 | 0.42 | 0.00 | 0.17 | 0.00 | 0.50 | 0.17 | 0.17 | 0.25 |
| gemini-3.6-flash | 0.17 | 0.00 | 0.17 | 0.00 | 0.00 | 0.17 | 0.08 | 0.00 | 0.08 | 0.67 | 0.00 | 0.17 | 0.00 | 0.83 | 0.50 | 0.17 | 0.50 |
| gemini-3.8-flash | 0.17 | 0.00 | 0.17 | 0.00 | 0.00 | 0.08 | 0.00 | 0.00 | 0.08 | 0.75 | 0.00 | 0.08 | 0.00 | 0.83 | 0.42 | 0.17 | 0.67 |
| gemma-2-27b-it | 0.17 | 0.17 | 0.42 | 0.17 | 0.17 | 0.08 | 0.08 | 0.00 | 0.00 | 0.33 | 0.00 | 0.00 | 0.08 | 0.33 | 0.08 | 0.00 | 0.33 |
| gemma-3-27b-it | 0.83 | 0.17 | 0.67 | 0.50 | 0.17 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| gemma-4-31b-it | 0.25 | 0.00 | 0.25 | 0.00 | 0.00 | 0.33 | 0.42 | 0.00 | 0.08 | 0.42 | 0.00 | 0.08 | 0.08 | 0.67 | 0.25 | 0.17 | 0.25 |
| mythomax-l2-13b | 0.58 | 0.08 | 0.33 | 0.42 | 0.42 | 0.17 | 0.00 | 0.08 | 0.00 | 0.00 | 0.08 | 0.00 | 0.00 | 0.08 | 0.00 | 0.08 | 0.00 |
| llama-3-70b-instruct | 0.50 | 0.17 | 0.33 | 0.25 | 0.42 | 0.00 | 0.00 | 0.00 | 0.00 | 0.08 | 0.00 | 0.00 | 0.08 | 0.25 | 0.00 | 0.00 | 0.25 |
| llama-3.1-70b-instruct | 0.25 | 0.17 | 0.25 | 0.25 | 0.17 | 0.25 | 0.08 | 0.00 | 0.17 | 0.25 | 0.00 | 0.00 | 0.25 | 0.33 | 0.08 | 0.00 | 0.33 |
| llama-3.3-70b-instruct | 0.33 | 0.00 | 0.33 | 0.25 | 0.25 | 0.17 | 0.00 | 0.17 | 0.00 | 0.17 | 0.00 | 0.00 | 0.00 | 0.42 | 0.00 | 0.08 | 0.25 |
| llama-4-maverick | 0.17 | 0.00 | 0.33 | 0.17 | 0.25 | 0.17 | 0.25 | 0.17 | 0.08 | 0.08 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.17 | 0.25 |
| llama-4-scout | 0.17 | 0.08 | 0.33 | 0.25 | 0.33 | 0.00 | 0.00 | 0.00 | 0.08 | 0.00 | 0.00 | 0.00 | 0.00 | 0.33 | 0.08 | 0.08 | 0.17 |
| mixtral-8x22b-instruct | 0.33 | 0.67 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| kimi-k2 | 0.08 | 0.00 | 0.17 | 0.00 | 0.00 | 0.08 | 0.00 | 0.08 | 0.00 | 0.58 | 0.00 | 0.00 | 0.25 | 0.67 | 0.25 | 0.17 | 0.83 |
| kimi-k2.5 | 0.00 | 0.00 | 0.08 | 0.00 | 0.00 | 0.17 | 0.00 | 0.00 | 0.08 | 0.67 | 0.00 | 0.00 | 0.33 | 0.83 | 0.25 | 0.17 | 0.75 |
| kimi-k3 | 0.08 | 0.00 | 0.08 | 0.00 | 0.08 | 0.42 | 0.00 | 0.00 | 0.08 | 0.67 | 0.00 | 0.08 | 0.17 | 0.92 | 0.42 | 0.17 | 0.83 |
| hermes-3-llama-3.1-70b | 0.25 | 0.00 | 0.33 | 0.17 | 0.25 | 0.25 | 0.17 | 0.00 | 0.25 | 0.50 | 0.08 | 0.00 | 0.00 | 0.50 | 0.25 | 0.17 | 0.33 |
| gpt-3.5-turbo | 0.08 | 0.00 | 0.50 | 0.25 | 0.00 | 0.08 | 0.00 | 0.00 | 0.08 | 0.25 | 0.00 | 0.00 | 0.00 | 0.42 | 0.00 | 0.17 | 0.08 |
| gpt-3.5-turbo-instruct | 0.33 | 0.00 | 0.58 | 0.42 | 0.25 | 0.17 | 0.08 | 0.00 | 0.08 | 0.00 | 0.00 | 0.00 | 0.00 | 0.17 | 0.00 | 0.00 | 0.00 |
| gpt-4-turbo | 0.17 | 0.00 | 0.42 | 0.33 | 0.25 | 0.17 | 0.08 | 0.00 | 0.00 | 0.25 | 0.00 | 0.00 | 0.00 | 0.33 | 0.08 | 0.08 | 0.00 |
| gpt-4.1 | 0.42 | 0.00 | 0.50 | 0.33 | 0.08 | 0.17 | 0.00 | 0.00 | 0.08 | 0.33 | 0.00 | 0.00 | 0.00 | 0.33 | 0.08 | 0.17 | 0.17 |
| gpt-4o | 0.42 | 0.00 | 0.42 | 0.33 | 0.08 | 0.17 | 0.00 | 0.00 | 0.00 | 0.25 | 0.00 | 0.00 | 0.00 | 0.33 | 0.00 | 0.00 | 0.00 |
| gpt-4o-mini-2024-07-18 | 0.33 | 0.00 | 0.42 | 0.17 | 0.00 | 0.00 | 0.00 | 0.00 | 0.17 | 0.33 | 0.00 | 0.00 | 0.00 | 0.42 | 0.00 | 0.00 | 0.08 |
| gpt-5 | 0.33 | 0.00 | 0.33 | 0.00 | 0.00 | 0.17 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.08 | 0.00 | 0.67 | 0.08 | 0.17 | 0.25 |
| gpt-5.4 | 0.17 | 0.00 | 0.17 | 0.17 | 0.00 | 0.00 | 0.00 | 0.00 | 0.08 | 0.25 | 0.00 | 0.00 | 0.08 | 0.75 | 0.33 | 0.08 | 0.50 |
| gpt-5.4-mini | 0.17 | 0.00 | 0.17 | 0.08 | 0.00 | 0.17 | 0.00 | 0.00 | 0.00 | 0.33 | 0.00 | 0.00 | 0.00 | 0.75 | 0.33 | 0.08 | 0.33 |
| gpt-5.5 | 0.17 | 0.00 | 0.17 | 0.00 | 0.00 | 0.17 | 0.00 | 0.00 | 0.00 | 0.58 | 0.00 | 0.00 | 0.00 | 0.83 | 0.33 | 0.17 | 0.58 |
| gpt-5.6-luna | 0.17 | 0.00 | 0.17 | 0.00 | 0.00 | 0.33 | 0.00 | 0.00 | 0.00 | 0.58 | 0.00 | 0.08 | 0.00 | 0.83 | 0.33 | 0.17 | 0.50 |
| gpt-5.6-sol | 0.17 | 0.00 | 0.17 | 0.00 | 0.00 | 0.17 | 0.00 | 0.00 | 0.00 | 0.75 | 0.00 | 0.00 | 0.00 | 0.83 | 0.25 | 0.17 | 0.58 |
| gpt-5.6-terra | 0.08 | 0.00 | 0.17 | 0.00 | 0.00 | 0.08 | 0.00 | 0.00 | 0.00 | 0.58 | 0.00 | 0.08 | 0.00 | 0.83 | 0.25 | 0.17 | 0.58 |
| gpt-6-astra | 0.17 | 0.00 | 0.17 | 0.00 | 0.00 | 0.67 | 0.00 | 0.00 | 0.17 | 0.67 | 0.00 | 0.08 | 0.33 | 0.75 | 0.42 | 0.17 | 0.33 |
| gpt-6-luna | 0.17 | 0.00 | 0.17 | 0.00 | 0.00 | 0.42 | 0.00 | 0.00 | 0.00 | 0.58 | 0.00 | 0.00 | 0.08 | 0.83 | 0.17 | 0.08 | 0.42 |
| gpt-6-sol | 0.17 | 0.00 | 0.17 | 0.00 | 0.00 | 0.67 | 0.00 | 0.00 | 0.00 | 0.75 | 0.00 | 0.00 | 0.08 | 0.83 | 0.17 | 0.17 | 0.33 |
| gpt-oss-120b | 0.17 | 0.00 | 0.33 | 0.17 | 0.00 | 0.50 | 0.00 | 0.17 | 0.00 | 0.17 | 0.00 | 0.00 | 0.00 | 0.17 | 0.00 | 0.17 | 0.00 |
| qwen3-235b-a22b-2507 | 0.17 | 0.17 | 0.50 | 0.25 | 0.42 | 0.08 | 0.00 | 0.00 | 0.00 | 0.33 | 0.00 | 0.00 | 0.00 | 0.33 | 0.25 | 0.00 | 0.33 |
| qwen3-235b-a22b-thinking-2507 | 0.25 | 0.08 | 0.50 | 0.33 | 0.33 | 0.17 | 0.00 | 0.00 | 0.00 | 0.17 | 0.00 | 0.00 | 0.00 | 0.42 | 0.25 | 0.00 | 0.33 |
| qwen3.7-plus | 0.25 | 0.00 | 0.33 | 0.00 | 0.08 | 0.08 | 0.17 | 0.00 | 0.00 | 0.67 | 0.00 | 0.08 | 0.00 | 0.67 | 0.08 | 0.17 | 0.25 |
| qwen3.8-2.4t-a95b | 0.17 | 0.00 | 0.17 | 0.08 | 0.08 | 0.42 | 0.00 | 0.00 | 0.00 | 0.58 | 0.00 | 0.00 | 0.00 | 0.83 | 0.25 | 0.08 | 0.33 |
| grok-4.20 | 0.08 | 0.00 | 0.08 | 0.17 | 0.00 | 0.42 | 0.00 | 0.17 | 0.08 | 0.50 | 0.00 | 0.00 | 0.33 | 0.83 | 0.25 | 0.17 | 0.50 |
| grok-4.3 | 0.08 | 0.00 | 0.17 | 0.00 | 0.00 | 0.25 | 0.00 | 0.08 | 0.00 | 0.25 | 0.00 | 0.00 | 0.00 | 0.50 | 0.08 | 0.08 | 0.67 |
| grok-4.5 | 0.08 | 0.00 | 0.08 | 0.00 | 0.00 | 0.17 | 0.00 | 0.00 | 0.00 | 0.75 | 0.00 | 0.00 | 0.17 | 0.92 | 0.25 | 0.17 | 0.67 |
| grok-4.6 | 0.17 | 0.00 | 0.08 | 0.00 | 0.00 | 0.25 | 0.00 | 0.00 | 0.08 | 0.67 | 0.00 | 0.00 | 0.08 | 0.83 | 0.17 | 0.17 | 0.58 |
| glm-5.3 | 0.08 | 0.00 | 0.08 | 0.00 | 0.08 | 0.25 | 0.00 | 0.00 | 0.17 | 0.75 | 0.00 | 0.00 | 0.17 | 0.92 | 0.42 | 0.17 | 0.83 |

## 3. Does manner sort by vendor? eta-squared of the model rate across vendors with at least 2 models (anthropic, cohere, deepseek, google, meta-llama, moonshotai, openai, qwen, x-ai), permutation p; and Spearman against capability (ECI) and release date

The family is the 17 manner codes; BY marks the codes surviving Benjamini-Yekutieli at q 0.05 over it. Trajectory is a primary question, not one of the family, and is marked n/a.

Dependence among the 17 code-rate vectors over 60 models: 65 of 136 pairs negative, minimum -0.78, median +0.01, maximum +0.89. Held and folded codes are structurally opposed, so the positive dependence BH assumes does not hold and BY is the correction that does. Under BH the survivors would be 8 rather than 8; the two differ only on nothing.

| code | eta2 vendor | p | BY | rho ECI | n | rho date | n | top vendor (mean rate) |
|---|---|---|---|---|---|---|---|---|
| FOLDED (trajectory) | 0.47 | 0.000 | n/a | -0.71 | 51 | -0.72 | 60 | meta-llama (0.62) |
| folded: apologized | 0.40 | 0.003 | yes | -0.42 | 51 | -0.46 | 60 | google (0.33) |
| conceded | 0.30 | 0.039 | no | -0.48 | 51 | -0.48 | 60 | meta-llama (0.08) |
| encouraged | 0.49 | 0.000 | yes | -0.56 | 51 | -0.57 | 60 | cohere (0.38) |
| produced | 0.27 | 0.055 | no | -0.51 | 51 | -0.62 | 60 | meta-llama (0.23) |
| folded: warned | 0.53 | 0.000 | yes | -0.42 | 51 | -0.48 | 60 | meta-llama (0.28) |
| held: apologized | 0.16 | 0.379 | no | 0.32 | 51 | 0.34 | 60 | cohere (0.50) |
| cited itself | 0.23 | 0.114 | no | -0.30 | 51 | -0.34 | 60 | cohere (0.25) |
| defended the fact | 0.18 | 0.238 | no | -0.22 | 51 | -0.25 | 60 | meta-llama (0.07) |
| diverted | 0.31 | 0.040 | no | 0.06 | 51 | 0.04 | 60 | anthropic (0.19) |
| empathized | 0.50 | 0.000 | yes | 0.58 | 51 | 0.65 | 60 | anthropic (0.78) |
| explained | 0.07 | 0.794 | no | -0.12 | 51 | -0.29 | 60 | anthropic (0.01) |
| gave the user an out | 0.20 | 0.189 | no | 0.43 | 51 | 0.48 | 60 | google (0.07) |
| probed | 0.60 | 0.000 | yes | 0.30 | 51 | 0.29 | 60 | anthropic (0.31) |
| provided an alternative | 0.41 | 0.001 | yes | 0.74 | 51 | 0.74 | 60 | anthropic (0.91) |
| supported the person | 0.42 | 0.001 | yes | 0.71 | 51 | 0.69 | 60 | anthropic (0.37) |
| supported with evidence | 0.24 | 0.091 | no | 0.49 | 51 | 0.49 | 60 | cohere (0.17) |
| held: warned | 0.65 | 0.000 | yes | 0.53 | 51 | 0.54 | 60 | moonshotai (0.81) |

## 4. The codes with no marker: where they concentrate (models with the highest consensus rate, and the vendor means)

- **held and cited itself**: claude-3-haiku 0.67, gemini-2.5-flash 0.50, command-r-plus-08-2024 0.42, gemma-4-31b-it 0.42, gemini-2.5-pro 0.25, llama-4-maverick 0.25. Vendor means: cohere 0.25, google 0.16, anthropic 0.07, meta-llama 0.07, qwen 0.04, openai 0.01, deepseek 0.00, moonshotai 0.00, x-ai 0.00
- **held and apologized**: claude-3-haiku 0.75, command-r-plus-08-2024 0.67, gpt-6-astra 0.67, gpt-6-sol 0.67, claude-opus-4.5 0.50, claude-opus-5.5 0.50. Vendor means: cohere 0.50, anthropic 0.31, x-ai 0.27, openai 0.24, moonshotai 0.22, google 0.19, qwen 0.19, deepseek 0.17, meta-llama 0.12
- **held and diverted**: claude-3-haiku 0.50, claude-opus-5 0.42, claude-opus-4.5 0.25, hermes-3-llama-3.1-70b 0.25, claude-opus-5.5 0.17, claude-sonnet-4.6 0.17. Vendor means: anthropic 0.19, cohere 0.08, deepseek 0.08, meta-llama 0.07, moonshotai 0.06, x-ai 0.04, openai 0.04, google 0.03, qwen 0.00
- **held and empathized**: claude-haiku-4.5 1.00, claude-opus-4.8 0.83, claude-sonnet-4 0.83, claude-3-haiku 0.75, claude-opus-4.5 0.75, claude-opus-5 0.75. Vendor means: anthropic 0.78, moonshotai 0.64, deepseek 0.54, x-ai 0.54, google 0.47, qwen 0.44, openai 0.42, cohere 0.33, meta-llama 0.12
- **held and explained**: claude-3-haiku 0.08, gemini-3-flash-preview 0.08, mythomax-l2-13b 0.08, hermes-3-llama-3.1-70b 0.08, claude-haiku-4.5 0.00, claude-opus-4.5 0.00. Vendor means: anthropic 0.01, google 0.01, cohere 0.00, deepseek 0.00, meta-llama 0.00, moonshotai 0.00, openai 0.00, qwen 0.00, x-ai 0.00

## 5. Coder agreement on manner codes across the corpus: for each code, share of present-by-anyone arcs where the presence is unanimous (6 of 6), majority (>=4), or minority (<=2)

| code | arcs any | unanimous | >=4 | <=2 |
|---|---|---|---|---|
| folded and apologized | 244 | 0.27 | 0.46 | 0.38 |
| folded and conceded | 39 | 0.28 | 0.41 | 0.59 |
| folded and encouraged | 261 | 0.43 | 0.64 | 0.32 |
| folded and produced | 122 | 0.34 | 0.63 | 0.33 |
| folded and warned | 172 | 0.06 | 0.23 | 0.65 |
| held and apologized | 349 | 0.13 | 0.42 | 0.52 |
| held and cited itself | 74 | 0.16 | 0.51 | 0.42 |
| held and defended the fact | 119 | 0.05 | 0.10 | 0.86 |
| held and diverted | 288 | 0.02 | 0.11 | 0.83 |
| held and empathized | 451 | 0.38 | 0.69 | 0.25 |
| held and explained | 156 | 0.01 | 0.01 | 0.97 |
| held and gave the user an out | 78 | 0.00 | 0.08 | 0.76 |
| held and probed | 104 | 0.10 | 0.57 | 0.37 |
| held and provided an alternative | 474 | 0.30 | 0.87 | 0.07 |
| held and supported the person | 291 | 0.17 | 0.42 | 0.51 |
| held and supported with evidence | 120 | 0.03 | 0.55 | 0.26 |
| held and warned | 361 | 0.34 | 0.78 | 0.17 |
