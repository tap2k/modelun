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
    "gpt-5.6-sol": ("GPT", 7), "gpt-5.6-terra": ("GPT", 7),
    "claude-3-haiku": ("Claude", 0), "claude-haiku-4.5": ("Claude", 1),
    "claude-sonnet-4.6": ("Claude", 2), "claude-opus-4.8": ("Claude", 3),
    "claude-sonnet-5": ("Claude", 4), "claude-fable-5": ("Claude", 4),
    "gemini-2.5-flash": ("Gemini", 0), "gemini-3.1-pro-preview": ("Gemini", 1), "gemini-3.5-flash": ("Gemini", 2),
    "grok-4.20": ("Grok", 0), "grok-4.3": ("Grok", 1), "grok-4.5": ("Grok", 2),
    "qwen-2.5-72b-instruct": ("Qwen", 0), "qwen3-235b-a22b-2507": ("Qwen", 1),
    "deepseek-chat-v3-0324": ("DeepSeek", 0), "deepseek-r1": ("DeepSeek", 1),
    "deepseek-v3.2": ("DeepSeek", 2), "deepseek-v4-flash": ("DeepSeek", 3),
}
