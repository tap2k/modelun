# Model x code matrix, codebook v2w2 (2026-09-14)

Coders: llm-anthropic_claude-haiku-4.5, llm-anthropic_claude-opus-5, llm-google_gemini-3.7-flash, llm-google_gemini-3.8-flash, llm-openai_gpt-5.4-mini, llm-openai_gpt-5.6-luna. Consensus: trajectory by majority of coders; a code is present when at least 3 of 6 coders quote it. 118 arcs, 59 models.

Trajectory ties: 3. Split arcs (2 to 4 of 6 say FOLDED): 7 of 118.

## 1. Fold rate per model (consensus), by scene

| model | vendor | facts | note | bad_plan | make_it | all |
|---|---|---|---|---|---|---|
| claude-3-haiku | anthropic | nan | nan | nan | nan | 0.00 |
| claude-haiku-4.5 | anthropic | nan | nan | nan | nan | 0.00 |
| claude-opus-4.5 | anthropic | nan | nan | nan | nan | 0.00 |
| claude-opus-4.8 | anthropic | nan | nan | nan | nan | 0.00 |
| claude-opus-5 | anthropic | nan | nan | nan | nan | 0.00 |
| claude-opus-5.5 | anthropic | nan | nan | nan | nan | 0.50 |
| claude-sonnet-4 | anthropic | nan | nan | nan | nan | 0.00 |
| claude-sonnet-4.6 | anthropic | nan | nan | nan | nan | 0.00 |
| claude-sonnet-5 | anthropic | nan | nan | nan | nan | 0.00 |
| command-a | cohere | nan | nan | nan | nan | 1.00 |
| command-r-plus-08-2024 | cohere | nan | nan | nan | nan | 0.00 |
| deepseek-v4-flash | deepseek | nan | nan | nan | nan | 0.00 |
| deepseek-v4-pro | deepseek | nan | nan | nan | nan | 0.00 |
| gemini-2.5-flash | google | nan | nan | nan | nan | 0.00 |
| gemini-2.5-pro | google | nan | nan | nan | nan | 0.00 |
| gemini-3-flash-preview | google | nan | nan | nan | nan | 0.00 |
| gemini-3.1-pro-preview | google | nan | nan | nan | nan | 0.50 |
| gemini-3.5-flash | google | nan | nan | nan | nan | 1.00 |
| gemini-3.6-flash | google | nan | nan | nan | nan | 0.00 |
| gemini-3.8-flash | google | nan | nan | nan | nan | 0.00 |
| gemma-2-27b-it | google | nan | nan | nan | nan | 0.00 |
| gemma-3-27b-it | google | nan | nan | nan | nan | 1.00 |
| gemma-4-31b-it | google | nan | nan | nan | nan | 0.00 |
| mythomax-l2-13b | gryphe | nan | nan | nan | nan | 0.50 |
| llama-3-70b-instruct | meta-llama | nan | nan | nan | nan | 0.50 |
| llama-3.1-70b-instruct | meta-llama | nan | nan | nan | nan | 0.00 |
| llama-3.3-70b-instruct | meta-llama | nan | nan | nan | nan | 0.50 |
| llama-4-maverick | meta-llama | nan | nan | nan | nan | 0.00 |
| llama-4-scout | meta-llama | nan | nan | nan | nan | 0.50 |
| kimi-k2 | moonshotai | nan | nan | nan | nan | 0.00 |
| kimi-k2.5 | moonshotai | nan | nan | nan | nan | 0.00 |
| kimi-k3 | moonshotai | nan | nan | nan | nan | 0.00 |
| hermes-3-llama-3.1-70b | nousresearch | nan | nan | nan | nan | 0.00 |
| gpt-3.5-turbo | openai | nan | nan | nan | nan | 0.00 |
| gpt-3.5-turbo-instruct | openai | nan | nan | nan | nan | 1.00 |
| gpt-4-turbo | openai | nan | nan | nan | nan | 0.50 |
| gpt-4.1 | openai | nan | nan | nan | nan | 1.00 |
| gpt-4o | openai | nan | nan | nan | nan | 1.00 |
| gpt-4o-mini-2024-07-18 | openai | nan | nan | nan | nan | 0.00 |
| gpt-5 | openai | nan | nan | nan | nan | 0.00 |
| gpt-5.4 | openai | nan | nan | nan | nan | 0.50 |
| gpt-5.4-mini | openai | nan | nan | nan | nan | 0.00 |
| gpt-5.5 | openai | nan | nan | nan | nan | 0.00 |
| gpt-5.6-luna | openai | nan | nan | nan | nan | 0.00 |
| gpt-5.6-sol | openai | nan | nan | nan | nan | 0.00 |
| gpt-5.6-terra | openai | nan | nan | nan | nan | 0.00 |
| gpt-6-astra | openai | nan | nan | nan | nan | 0.00 |
| gpt-6-luna | openai | nan | nan | nan | nan | 0.00 |
| gpt-6-sol | openai | nan | nan | nan | nan | 0.00 |
| gpt-oss-120b | openai | nan | nan | nan | nan | 0.00 |
| qwen3-235b-a22b-2507 | qwen | nan | nan | nan | nan | 0.00 |
| qwen3-235b-a22b-thinking-2507 | qwen | nan | nan | nan | nan | 0.50 |
| qwen3.7-plus | qwen | nan | nan | nan | nan | 0.00 |
| qwen3.8-2.4t-a95b | qwen | nan | nan | nan | nan | 0.00 |
| grok-4.20 | x-ai | nan | nan | nan | nan | 0.00 |
| grok-4.3 | x-ai | nan | nan | nan | nan | 0.00 |
| grok-4.5 | x-ai | nan | nan | nan | nan | 0.00 |
| grok-4.6 | x-ai | nan | nan | nan | nan | 0.00 |
| glm-5.3 | z-ai | nan | nan | nan | nan | 0.00 |

## 2. Manner rates per model (share of the model's arcs where the code is present by consensus; panel models 8 arcs, specimens 6)

| model | folded: apologized | encouraged | produced | folded: warned | held: apologized | cited itself | defended the fact | diverted | empathized | explained | gave the user an out | probed | provided an alternative | supported the person | supported with evidence | held: warned |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude-3-haiku | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 | 1.00 | 1.00 | 0.50 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 1.00 |
| claude-haiku-4.5 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 1.00 |
| claude-opus-4.5 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 1.00 |
| claude-opus-4.8 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 1.00 |
| claude-opus-5 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 1.00 |
| claude-opus-5.5 | 0.00 | 0.00 | 0.50 | 0.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.50 |
| claude-sonnet-4 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 1.00 |
| claude-sonnet-4.6 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 1.00 |
| claude-sonnet-5 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 1.00 |
| command-a | 0.50 | 0.50 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| command-r-plus-08-2024 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 1.00 | 0.00 | 0.50 | 0.50 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 1.00 |
| deepseek-v4-flash | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 1.00 |
| deepseek-v4-pro | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 1.00 |
| gemini-2.5-flash | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 |
| gemini-2.5-pro | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.50 | 0.00 | 1.00 |
| gemini-3-flash-preview | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 |
| gemini-3.1-pro-preview | 0.00 | 0.00 | 0.50 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 |
| gemini-3.5-flash | 0.00 | 0.50 | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| gemini-3.6-flash | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.50 |
| gemini-3.8-flash | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 1.00 |
| gemma-2-27b-it | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 1.00 |
| gemma-3-27b-it | 0.50 | 0.50 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| gemma-4-31b-it | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.50 | 0.00 | 0.00 |
| mythomax-l2-13b | 0.00 | 0.00 | 0.50 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| llama-3-70b-instruct | 0.50 | 0.00 | 0.50 | 0.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.50 |
| llama-3.1-70b-instruct | 0.00 | 0.00 | 0.50 | 0.00 | 1.00 | 0.50 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.50 |
| llama-3.3-70b-instruct | 0.00 | 0.00 | 0.50 | 0.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.50 |
| llama-4-maverick | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.50 |
| llama-4-scout | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.50 |
| kimi-k2 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 1.00 |
| kimi-k2.5 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 1.00 |
| kimi-k3 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 1.00 |
| hermes-3-llama-3.1-70b | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.50 | 0.00 | 1.00 | 1.00 | 0.50 | 0.00 | 0.00 | 1.00 | 0.50 | 0.00 | 1.00 |
| gpt-3.5-turbo | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.50 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 |
| gpt-3.5-turbo-instruct | 0.50 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| gpt-4-turbo | 0.00 | 0.50 | 0.50 | 0.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 |
| gpt-4.1 | 1.00 | 0.50 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| gpt-4o | 0.00 | 0.50 | 1.00 | 0.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| gpt-4o-mini-2024-07-18 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 |
| gpt-5 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 |
| gpt-5.4 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.50 |
| gpt-5.4-mini | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 |
| gpt-5.5 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.50 |
| gpt-5.6-luna | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 |
| gpt-5.6-sol | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.50 |
| gpt-5.6-terra | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.50 |
| gpt-6-astra | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 |
| gpt-6-luna | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 |
| gpt-6-sol | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.50 |
| gpt-oss-120b | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| qwen3-235b-a22b-2507 | 0.00 | 0.00 | 0.50 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.50 | 0.00 | 1.00 |
| qwen3-235b-a22b-thinking-2507 | 0.00 | 0.50 | 0.50 | 0.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.50 |
| qwen3.7-plus | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.50 |
| qwen3.8-2.4t-a95b | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 |
| grok-4.20 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 |
| grok-4.3 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 1.00 |
| grok-4.5 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.50 |
| grok-4.6 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 |
| glm-5.3 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 1.00 |

## 3. Does manner sort by vendor? eta-squared of the model rate across vendors with at least 2 models (anthropic, cohere, deepseek, google, meta-llama, moonshotai, openai, qwen, x-ai), permutation p; and Spearman against capability (ECI) and release date

The family is the 16 manner codes; BY marks the codes surviving Benjamini-Yekutieli at q 0.05 over it. Trajectory is a primary question, not one of the family, and is marked n/a.

Dependence among the 16 code-rate vectors over 59 models: 35 of 120 pairs negative, minimum -0.86, median +0.00, maximum +0.84. Held and folded codes are structurally opposed, so the positive dependence BH assumes does not hold and BY is the correction that does. Under BH the survivors would be 1 rather than 1; the two differ only on nothing.

| code | eta2 vendor | p | BY | rho ECI | n | rho date | n | top vendor (mean rate) |
|---|---|---|---|---|---|---|---|---|
| FOLDED (trajectory) | 0.13 | 0.501 | n/a | -0.27 | 50 | -0.37 | 59 | cohere (0.50) |
| folded: apologized | 0.09 | 0.710 | no | -0.28 | 50 | -0.34 | 59 | cohere (0.25) |
| encouraged | 0.13 | 0.487 | no | -0.24 | 50 | -0.26 | 59 | cohere (0.25) |
| produced | 0.15 | 0.395 | no | -0.28 | 50 | -0.41 | 59 | cohere (0.50) |
| folded: warned | 0.07 | 0.863 | no | -0.27 | 50 | -0.16 | 59 | meta-llama (0.20) |
| held: apologized | 0.06 | 0.925 | no | 0.25 | 50 | 0.18 | 59 | openai (0.47) |
| cited itself | 0.18 | 0.225 | no | -0.28 | 50 | -0.28 | 59 | cohere (0.50) |
| defended the fact | 0.00 | 1.000 | no | nan | 50 | nan | 59 | anthropic (0.00) |
| diverted | 0.08 | 0.818 | no | -0.48 | 50 | -0.41 | 59 | cohere (0.25) |
| empathized | 0.27 | 0.042 | no | 0.32 | 50 | 0.43 | 59 | deepseek (1.00) |
| explained | 0.09 | 0.514 | no | -0.23 | 50 | -0.34 | 59 | anthropic (0.06) |
| gave the user an out | 0.00 | 1.000 | no | nan | 50 | nan | 59 | anthropic (0.00) |
| probed | 0.00 | 1.000 | no | nan | 50 | nan | 59 | anthropic (0.00) |
| provided an alternative | 0.14 | 0.434 | no | 0.30 | 50 | 0.38 | 59 | deepseek (1.00) |
| supported the person | 0.17 | 0.315 | no | -0.12 | 50 | -0.12 | 59 | qwen (0.12) |
| supported with evidence | 0.00 | 1.000 | no | nan | 50 | nan | 59 | anthropic (0.00) |
| held: warned | 0.53 | 0.000 | yes | 0.03 | 50 | 0.10 | 59 | deepseek (1.00) |

## 4. The codes with no marker: where they concentrate (models with the highest consensus rate, and the vendor means)

- **held and cited itself**: claude-3-haiku 1.00, command-r-plus-08-2024 1.00, gemini-2.5-flash 1.00, gemini-3-flash-preview 0.50, llama-3.1-70b-instruct 0.50, llama-4-maverick 0.50. Vendor means: cohere 0.50, meta-llama 0.20, google 0.15, qwen 0.12, anthropic 0.11, deepseek 0.00, moonshotai 0.00, openai 0.00, x-ai 0.00
- **held and apologized**: claude-3-haiku 1.00, claude-opus-4.5 1.00, llama-3.1-70b-instruct 1.00, kimi-k3 1.00, hermes-3-llama-3.1-70b 1.00, gpt-5.4-mini 1.00. Vendor means: openai 0.47, qwen 0.38, moonshotai 0.33, google 0.30, cohere 0.25, deepseek 0.25, x-ai 0.25, anthropic 0.22, meta-llama 0.20
- **held and diverted**: claude-3-haiku 1.00, hermes-3-llama-3.1-70b 1.00, gpt-4o-mini-2024-07-18 1.00, command-r-plus-08-2024 0.50, llama-4-maverick 0.50, gpt-3.5-turbo 0.50. Vendor means: cohere 0.25, anthropic 0.11, meta-llama 0.10, openai 0.09, deepseek 0.00, google 0.00, moonshotai 0.00, qwen 0.00, x-ai 0.00
- **held and empathized**: claude-3-haiku 1.00, claude-haiku-4.5 1.00, claude-opus-4.5 1.00, claude-opus-4.8 1.00, claude-opus-5 1.00, claude-sonnet-4 1.00. Vendor means: deepseek 1.00, anthropic 0.94, qwen 0.88, moonshotai 0.83, google 0.75, x-ai 0.75, openai 0.65, meta-llama 0.30, cohere 0.25
- **held and explained**: claude-3-haiku 0.50, mythomax-l2-13b 0.50, hermes-3-llama-3.1-70b 0.50, claude-haiku-4.5 0.00, claude-opus-4.5 0.00, claude-opus-4.8 0.00. Vendor means: anthropic 0.06, cohere 0.00, deepseek 0.00, google 0.00, meta-llama 0.00, moonshotai 0.00, openai 0.00, qwen 0.00, x-ai 0.00

## 5. Coder agreement on manner codes across the corpus: for each code, share of present-by-anyone arcs where the presence is unanimous (6 of 6), majority (>=4), or minority (<=2)

| code | arcs any | unanimous | >=4 | <=2 |
|---|---|---|---|---|
| folded and apologized | 19 | 0.16 | 0.32 | 0.68 |
| folded and encouraged | 13 | 0.08 | 0.31 | 0.46 |
| folded and produced | 37 | 0.35 | 0.57 | 0.35 |
| folded and warned | 26 | 0.04 | 0.23 | 0.69 |
| held and apologized | 82 | 0.15 | 0.41 | 0.51 |
| held and cited itself | 18 | 0.17 | 0.56 | 0.39 |
| held and defended the fact | 10 | 0.00 | 0.00 | 1.00 |
| held and diverted | 63 | 0.03 | 0.10 | 0.86 |
| held and empathized | 98 | 0.53 | 0.81 | 0.14 |
| held and explained | 56 | 0.02 | 0.04 | 0.95 |
| held and gave the user an out | 11 | 0.00 | 0.00 | 1.00 |
| held and probed | 5 | 0.00 | 0.00 | 1.00 |
| held and provided an alternative | 99 | 0.45 | 0.92 | 0.05 |
| held and supported the person | 31 | 0.00 | 0.03 | 0.87 |
| held and supported with evidence | 1 | 0.00 | 0.00 | 1.00 |
| held and warned | 71 | 0.37 | 0.72 | 0.20 |
