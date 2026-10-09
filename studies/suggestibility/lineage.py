"""Single source of truth for model → (family, generation-index).

Used by the explorer (views/build.py) and the paper figures (paper/make_assets.py) to draw the
per-family generational walks. Generation LABELS and COLORS stay local to each consumer — the
explorer wants readable labels and dark-theme hues; the paper wants terse labels and the print
palette — but the family membership and ordering live here so they can't drift.
"""

# model label -> (family, generation index within the family; approx chronological)
FAM = {
    "gpt-3.5-turbo": ("GPT", 0), "gpt-4-turbo": ("GPT", 1), "gpt-4o": ("GPT", 2),
    "gpt-4o-mini-2024-07-18": ("GPT", 2), "gpt-4.1": ("GPT", 3), "gpt-5": ("GPT", 4),
    "gpt-5.4": ("GPT", 5), "gpt-5.5": ("GPT", 6), "gpt-5.6-luna": ("GPT", 7),
    "gpt-5.6-sol": ("GPT", 7), "gpt-5.6-terra": ("GPT", 7), "gpt-6-astra": ("GPT", 8),
    "claude-3-haiku": ("Claude", 0), "claude-haiku-4.5": ("Claude", 1),
    "claude-sonnet-4.6": ("Claude", 2), "claude-opus-4.8": ("Claude", 3),
    "claude-sonnet-5": ("Claude", 4), "claude-fable-5": ("Claude", 4),
    "claude-opus-5": ("Claude", 5), "claude-fable-5.1": ("Claude", 6),
    "gemini-2.5-flash": ("Gemini", 0), "gemini-3.1-pro-preview": ("Gemini", 1), "gemini-3.5-flash": ("Gemini", 2),
    "gemini-3.6-flash": ("Gemini", 3), "gemini-3.1-flash-lite": ("Gemini", 1), "gemini-3.8-flash": ("Gemini", 4),
    "grok-4.20": ("Grok", 0), "grok-4.3": ("Grok", 1), "grok-4.5": ("Grok", 2), "grok-4.6": ("Grok", 3),
    "qwen-2.5-72b-instruct": ("Qwen", 0), "qwen3-235b-a22b-2507": ("Qwen", 1),
    "qwen3.5-9b": ("Qwen", 2), "qwen3.5-27b": ("Qwen", 2), "qwen3.5-122b-a10b": ("Qwen", 2),
    "qwen3.6-35b-a3b": ("Qwen", 3), "qwen3.8-2.4t-a95b": ("Qwen", 4), "qwen3.8-27b": ("Qwen", 4),
    "deepseek-r1": ("DeepSeek", 0), "deepseek-chat-v3-0324": ("DeepSeek", 1),  # R1 2025-01, V3-0324 2025-03
    "deepseek-v3.2": ("DeepSeek", 2), "deepseek-v4-flash": ("DeepSeek", 3), "deepseek-v4-pro": ("DeepSeek", 3),
    # wave 3 (2026-09-25), placed between the existing generations by release date
    "claude-opus-4.1": ("Claude", 0.5), "claude-sonnet-4.5": ("Claude", 0.75),
    "claude-opus-4.5": ("Claude", 1.33), "claude-opus-4.6": ("Claude", 1.67),
    "claude-opus-4.7": ("Claude", 2.5), "claude-opus-5.5": ("Claude", 7),
    "gpt-5.4-mini": ("GPT", 5), "gpt-6-luna": ("GPT", 8), "gpt-6-sol": ("GPT", 8),
    "gemini-2.5-pro": ("Gemini", 0), "gemini-3-flash-preview": ("Gemini", 0.5),
    "grok-4.7": ("Grok", 4), "qwen3.7-plus": ("Qwen", 3.5),
    "claude-sonnet-5.5": ("Claude", 8),  # 2026-09-28, on its release
    "gpt-6.1-sol": ("GPT", 9),  # 2026-09-29, on its release
    "claude-haiku-5.5": ("Claude", 9),  # 2026-10-07, on its release
}

# Further multi-generation lineages in the panel, used only by the release test's robustness check
# (grid_stats.robustness): the six families above plus these.
EXTRA = {
    "llama-3.3-70b-instruct": ("Llama", 0), "llama-4-maverick": ("Llama", 1), "llama-4-scout": ("Llama", 1),
    "mixtral-8x22b-instruct": ("Mistral", 0), "mistral-nemo": ("Mistral", 1),
    "mistral-small-3.2-24b-instruct": ("Mistral", 2), "mistral-small-2603": ("Mistral", 3),
    "kimi-k2": ("Kimi", 0), "kimi-k2.5": ("Kimi", 1), "kimi-k3": ("Kimi", 2),
    "glm-4.7": ("GLM", 0), "glm-5.3": ("GLM", 1), "glm-5.3-flash": ("GLM", 1),
    "nemotron-3-nano-30b-a3b": ("Nemotron", 0), "nemotron-3-super-120b-a12b": ("Nemotron", 0),
    "nemotron-3-ultra-550b-a55b": ("Nemotron", 0), "nemotron-3.5-lightning": ("Nemotron", 1),
    "gemma-3-27b-it": ("Gemma", 0), "gemma-4-26b-a4b-it": ("Gemma", 1), "gemma-4-31b-it": ("Gemma", 1),
    "hermes-3-llama-3.1-405b": ("Hermes", 0), "hermes-3-llama-3.1-70b": ("Hermes", 0), "hermes-4-405b": ("Hermes", 1),
}
