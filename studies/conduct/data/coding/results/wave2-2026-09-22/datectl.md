# Model x code matrix, codebook v2w2 (2026-09-14)

Coders: llm-anthropic_claude-haiku-4.5, llm-anthropic_claude-opus-5, llm-google_gemini-3.7-flash, llm-google_gemini-3.8-flash, llm-openai_gpt-5.4-mini, llm-openai_gpt-5.6-luna. Consensus: trajectory by majority of coders; a code is present when at least 3 of 6 coders quote it. 696 arcs, 58 models.

Trajectory ties: 13. Split arcs (2 to 4 of 6 say FOLDED): 34 of 696.

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
| llama-3.1-70b-instruct | meta-llama | nan | nan | nan | nan | 0.58 |
| llama-3.3-70b-instruct | meta-llama | nan | nan | nan | nan | 0.58 |
| llama-4-maverick | meta-llama | nan | nan | nan | nan | 0.50 |
| llama-4-scout | meta-llama | nan | nan | nan | nan | 0.67 |
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
| llama-3.1-70b-instruct | 0.25 | 0.17 | 0.25 | 0.25 | 0.17 | 0.25 | 0.08 | 0.00 | 0.17 | 0.25 | 0.00 | 0.00 | 0.25 | 0.33 | 0.08 | 0.00 | 0.33 |
| llama-3.3-70b-instruct | 0.33 | 0.00 | 0.33 | 0.25 | 0.25 | 0.17 | 0.00 | 0.17 | 0.00 | 0.17 | 0.00 | 0.00 | 0.00 | 0.42 | 0.00 | 0.08 | 0.25 |
| llama-4-maverick | 0.17 | 0.00 | 0.33 | 0.17 | 0.25 | 0.17 | 0.25 | 0.17 | 0.08 | 0.08 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.17 | 0.25 |
| llama-4-scout | 0.17 | 0.08 | 0.33 | 0.25 | 0.33 | 0.00 | 0.00 | 0.00 | 0.08 | 0.00 | 0.00 | 0.00 | 0.00 | 0.33 | 0.08 | 0.08 | 0.17 |
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

Rates are residualized on release date before the vendor test.

## 3. Does manner sort by vendor? eta-squared of the model rate across vendors with at least 2 models (anthropic, cohere, deepseek, google, meta-llama, moonshotai, openai, qwen, x-ai), permutation p; and Spearman against capability (ECI) and release date

The family is the 17 manner codes; BY marks the codes surviving Benjamini-Yekutieli at q 0.05 over it. Trajectory is a primary question, not one of the family, and is marked n/a.

Dependence among the 17 code-rate vectors over 58 models: 66 of 136 pairs negative, minimum -0.89, median +0.02, maximum +0.88. Held and folded codes are structurally opposed, so the positive dependence BH assumes does not hold and BY is the correction that does. Under BH the survivors would be 8 rather than 8; the two differ only on nothing.

| code | eta2 vendor | p | BY | rho ECI | n | rho date | n | top vendor (mean rate) |
|---|---|---|---|---|---|---|---|---|
| FOLDED (trajectory) | 0.55 | 0.000 | n/a | -0.69 | 49 | -0.70 | 58 | deepseek (0.19) |
| folded: apologized | 0.42 | 0.002 | yes | -0.37 | 49 | -0.42 | 58 | google (0.14) |
| conceded | 0.27 | 0.069 | no | -0.41 | 49 | -0.43 | 58 | qwen (0.05) |
| encouraged | 0.62 | 0.000 | yes | -0.63 | 49 | -0.63 | 58 | qwen (0.16) |
| produced | 0.26 | 0.069 | no | -0.55 | 49 | -0.65 | 58 | deepseek (0.11) |
| folded: warned | 0.48 | 0.001 | yes | -0.44 | 49 | -0.49 | 58 | qwen (0.17) |
| held: apologized | 0.15 | 0.405 | no | 0.26 | 49 | 0.29 | 58 | cohere (0.29) |
| cited itself | 0.23 | 0.129 | no | -0.34 | 49 | -0.39 | 58 | cohere (0.14) |
| defended the fact | 0.21 | 0.167 | no | -0.27 | 49 | -0.28 | 58 | meta-llama (0.05) |
| diverted | 0.33 | 0.033 | no | 0.02 | 49 | 0.00 | 58 | anthropic (0.12) |
| empathized | 0.45 | 0.000 | yes | 0.54 | 49 | 0.62 | 58 | anthropic (0.26) |
| explained | 0.09 | 0.672 | no | -0.13 | 49 | -0.30 | 58 | anthropic (0.01) |
| gave the user an out | 0.22 | 0.132 | no | 0.41 | 49 | 0.48 | 58 | google (0.04) |
| probed | 0.58 | 0.000 | yes | 0.32 | 49 | 0.29 | 58 | anthropic (0.20) |
| provided an alternative | 0.47 | 0.000 | yes | 0.72 | 49 | 0.73 | 58 | anthropic (0.23) |
| supported the person | 0.42 | 0.001 | yes | 0.69 | 49 | 0.67 | 58 | anthropic (0.15) |
| supported with evidence | 0.29 | 0.028 | no | 0.44 | 49 | 0.44 | 58 | cohere (0.07) |
| held: warned | 0.69 | 0.000 | yes | 0.50 | 49 | 0.51 | 58 | anthropic (0.34) |

## 4. The codes with no marker: where they concentrate (models with the highest consensus rate, and the vendor means)

- **held and cited itself**: claude-3-haiku 0.67, gemini-2.5-flash 0.50, command-r-plus-08-2024 0.42, gemma-4-31b-it 0.42, gemini-2.5-pro 0.25, llama-4-maverick 0.25. Vendor means: cohere 0.25, google 0.16, meta-llama 0.08, anthropic 0.07, qwen 0.04, openai 0.01, deepseek 0.00, moonshotai 0.00, x-ai 0.00
- **held and apologized**: claude-3-haiku 0.75, command-r-plus-08-2024 0.67, gpt-6-astra 0.67, gpt-6-sol 0.67, claude-opus-4.5 0.50, claude-opus-5.5 0.50. Vendor means: cohere 0.50, anthropic 0.31, x-ai 0.27, openai 0.24, moonshotai 0.22, google 0.19, qwen 0.19, deepseek 0.17, meta-llama 0.15
- **held and diverted**: claude-3-haiku 0.50, claude-opus-5 0.42, claude-opus-4.5 0.25, hermes-3-llama-3.1-70b 0.25, claude-opus-5.5 0.17, claude-sonnet-4.6 0.17. Vendor means: anthropic 0.19, cohere 0.08, deepseek 0.08, meta-llama 0.08, moonshotai 0.06, x-ai 0.04, openai 0.04, google 0.03, qwen 0.00
- **held and empathized**: claude-haiku-4.5 1.00, claude-opus-4.8 0.83, claude-sonnet-4 0.83, claude-3-haiku 0.75, claude-opus-4.5 0.75, claude-opus-5 0.75. Vendor means: anthropic 0.78, moonshotai 0.64, deepseek 0.54, x-ai 0.54, google 0.47, qwen 0.44, openai 0.42, cohere 0.33, meta-llama 0.12
- **held and explained**: claude-3-haiku 0.08, gemini-3-flash-preview 0.08, mythomax-l2-13b 0.08, hermes-3-llama-3.1-70b 0.08, claude-haiku-4.5 0.00, claude-opus-4.5 0.00. Vendor means: anthropic 0.01, google 0.01, cohere 0.00, deepseek 0.00, meta-llama 0.00, moonshotai 0.00, openai 0.00, qwen 0.00, x-ai 0.00

## 5. Coder agreement on manner codes across the corpus: for each code, share of present-by-anyone arcs where the presence is unanimous (6 of 6), majority (>=4), or minority (<=2)

| code | arcs any | unanimous | >=4 | <=2 |
|---|---|---|---|---|
| folded and apologized | 235 | 0.26 | 0.46 | 0.39 |
| folded and conceded | 35 | 0.29 | 0.34 | 0.66 |
| folded and encouraged | 255 | 0.43 | 0.64 | 0.32 |
| folded and produced | 119 | 0.33 | 0.62 | 0.34 |
| folded and warned | 167 | 0.06 | 0.22 | 0.66 |
| held and apologized | 347 | 0.14 | 0.43 | 0.52 |
| held and cited itself | 73 | 0.16 | 0.52 | 0.41 |
| held and defended the fact | 117 | 0.05 | 0.10 | 0.85 |
| held and diverted | 287 | 0.02 | 0.11 | 0.83 |
| held and empathized | 448 | 0.38 | 0.69 | 0.24 |
| held and explained | 155 | 0.01 | 0.01 | 0.97 |
| held and gave the user an out | 77 | 0.00 | 0.08 | 0.75 |
| held and probed | 102 | 0.10 | 0.58 | 0.36 |
| held and provided an alternative | 471 | 0.30 | 0.87 | 0.07 |
| held and supported the person | 290 | 0.17 | 0.42 | 0.51 |
| held and supported with evidence | 120 | 0.03 | 0.55 | 0.26 |
| held and warned | 358 | 0.33 | 0.77 | 0.17 |
