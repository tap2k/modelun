# Held-out test of the generational reversal on the wave-2 models (2026-09-25)

July panel 45 models (the arXiv tag); wave 2 adds 25. TAGeff in points, 90% bootstrap interval; 'resists' means the interval is below zero.

| family | July endpoint | wave-2 model (generation) | TAGeff [90% CI] | resists |
|---|---|---|---|---|
| GPT | gpt-5.6-terra -8 [-18, +1] | gpt-6-astra (g8) | -19 [-31, -10] | yes |
| Claude | claude-opus-5 -15 [-23, -7] | claude-fable-5.1 (g6) | -30 [-41, -20] | yes |
| Gemini | gemini-3.6-flash -21 [-29, -13] | gemini-3.1-flash-lite (g1) | +1 [-6, +8] | no |
| Gemini | gemini-3.6-flash -21 [-29, -13] | gemini-3.8-flash (g4) | -9 [-17, -2] | yes |
| Grok | grok-4.5 -11 [-19, -1] | grok-4.6 (g3) | -2 [-13, +8] | no |
| Qwen | qwen3-235b-a22b-2507 -11 [-20, -2] | qwen3.5-122b-a10b (g2) | +6 [-2, +14] | no |
| Qwen | qwen3-235b-a22b-2507 -11 [-20, -2] | qwen3.5-27b (g2) | -16 [-24, -9] | yes |
| Qwen | qwen3-235b-a22b-2507 -11 [-20, -2] | qwen3.5-9b (g2) | +4 [-1, +10] | no |
| Qwen | qwen3-235b-a22b-2507 -11 [-20, -2] | qwen3.6-35b-a3b (g3) | -12 [-20, -6] | yes |
| Qwen | qwen3-235b-a22b-2507 -11 [-20, -2] | qwen3.8-2.4t-a95b (g4) | -5 [-12, +2] | no |
| DeepSeek | deepseek-v4-flash +11 [+2, +20] | deepseek-v4-pro (g3) | +4 [-6, +13] | no |

Wave-2 models outside the tracked families:

- gemma-4-26b-a4b-it: +3 [-4, +11], resists no
- gemma-4-31b-it: -3 [-10, +4], resists no
- glm-5.3: -18 [-24, -11], resists yes
- glm-5.3-flash: -29 [-41, -19], resists yes
- gpt-oss-120b: +1 [-2, +4], resists no
- gpt-oss-20b: +8 [-1, +15], resists no
- hermes-3-llama-3.1-405b: -1 [-7, +4], resists no
- kimi-k3: -31 [-41, -21], resists yes
- llama-4-scout: -4 [-9, +0], resists no
- minimax-m3: -4 [-12, +4], resists no
- mistral-nemo: +14 [+5, +23], resists positive
- mistral-small-3.2-24b-instruct: -2 [-8, +4], resists no
- nemotron-3-nano-30b-a3b: +24 [+16, +31], resists positive
- step-3.7-flash: -3 [-9, +2], resists no

Significant resisters: July 19 of 45, wave 2 8 of 25. Significantly sycophantic: July 8, wave 2 2. (The paper's counts use BH over bootstrap p and a floor guard, so they differ from these interval counts.)
