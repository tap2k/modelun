# Open-ended replies — handoff, 2026-10-30

A first pass over every free-wording (unclamped) reply in the consensus study: a transcript viewer and a
judge-free shape analysis. Nothing here is published or established; these are characterizations from string
matching, spot-read against the replies. What to follow up is Tapan's call.

## What is covered

All as served (the reasoning-off arms are left out), 4 runs each, every run a fresh conversation.

| group | prompt | prompts | models | dirs |
|---|---|---|---|---|
| name | "Name a X." (non-brand) | 93 | ~105 | `transcripts-clamp` and `-clamp-ext` (free halves), `-clamp-free` |
| name-brand | "Name a soda brand." etc. | 44 | ~101 | same, plus `-clamp-free-brands-ext`, `-ext2` |
| choose | "Choose a soda brand." | 44 | ~121 | `transcripts-brands-choose-free`, `-ext2-` |
| recommend | "Can you recommend a soda brand?" | 44 | ~121 | `transcripts-brands-recommend-free`, `-ext2-` |
| pick1 | "Which soda brand would you pick?" | 44 | ~121 | `transcripts-brands-pick1-free`, `-ext2-` |
| pick2 | recommend, then "Which one would you pick?" (one conversation) | 44 | ~121 | `transcripts-brands-pick2-free`, `-ext2-` |

"Name a car brand." is asked twice (in `clamp-ext` and in `clamp-free`); both are kept.

## Files

- `probe_open.py` — the analysis. `python probe_open.py` prints the tables and writes `probes/open.json` (~1 min).
- `views/build_open.py` + `views/open.html` — the viewer. `python views/build_open.py` writes `views/data-open/`
  (179 MB, one file per prompt, loaded on demand; gitignored), then open `views/open.html`. Pages: overview
  (group, vendor, brand-noun-by-form grid, cross-form agreement), one page per group (sortable prompt table), one
  per prompt (first-answer bars that filter, vendor/shape/text filters, all runs with mentions highlighted;
  pick2 shows both turns), and per model.

## Measures (per reply, no judge)

- **first**: the first pool answer named, the prose analogue of the one-word pick. Pool: the field's clamped
  answers named twice or more, minus words of the question (`probe_clamp` for Name; the Name+Choose brand
  batteries for brand nouns, as `probe_recommend`). Matching reuses `probe_clamp.patterns`/`mentions`.
- **bare** ≤ 4 words; **list** 3+ answers or 3+ bullet lines; **asks** a `?`; **disclaims** "as an AI",
  "I don't have personal preferences", "I don't drink" and similar; **consistent** all of a model's runs open on
  the same answer.

## First readings (to check, not findings)

1. **Without the clamp most Name replies are still one word** (median 2 words, 65% bare). It splits by vendor:
   OpenAI, Qwen, Meta, xAI ~86–93% bare; Anthropic 44% bare, median 11 words, asks back 21% ("Would you like to
   know something about it?"); Mistral asks 39%; Cohere and Nous run to ~30–40 words.
2. **"Pick a word." → "serendipity"** in 171 of ~400 replies.
3. **Asking for the model's own pick triggers disclaimers**: Name 0%, recommend 1%, pick1 26%, pick2 18%.
   pick1 by vendor: Meta 50%, Cohere 49%, Qwen 45%, NVIDIA 43%, OpenAI and xAI 6%.
4. **Name → recommend → pick moves from the famous brand to the "good choice" brand.** The field's top first
   mention changes with the form for 31 of 44 nouns: WhatsApp → Signal (94% in pick2), Chrome → Firefox,
   Google → DuckDuckGo (pick2), McDonald's → Chick-fil-A, Heineken → Sierra Nevada, Canon → Sony, Nike →
   Uniqlo/Patagonia, Tesla → Hyundai (Ioniq 5), Siri → Claude or "me" (AI assistant). Spot-read: real
   (e.g. Culver's, Brave Search, Chick-fil-A in pick2).
5. **The same model's brand changes across forms**: top first mention agrees Name~pick2 36%, recommend~pick1 68%.
   In pick2 the turn-2 pick is in the model's own turn-1 list 98% of the time, but is the first brand listed
   only 60%.

## Known limits

- **Pool misses.** A brand the clamped batteries never named twice is invisible; the first mention then falls to
  the next pool answer (EV: Kia is not in the pool, so "Ioniq 5 or Kia EV6" scores Hyundai, and a Kia-first
  reply scores whatever comes next). "no answer found" is 13% in pick1, partly disclaim-only replies.
- **Multi-word names.** "Lake Superior", "Eiffel Tower" score oddly (pool built from last-word extraction).
  `probe_clamp`'s table shows the same (lake first 0%, landmark single 0%).
- **Shape regexes are crude.** `asks` counts any `?`, including rhetorical ones; `disclaims` is a phrase list.
- Vendor rows mix very different models (DeepSeek's median 19 words comes from some models; V4 Pro answers bare).

## Possible next steps (proposals)

- Grow the brand pool from the free replies themselves (bolded names) so Kia, Lucid, etc. are scored.
- Score the reasoning-off arms (`*-off` dirs) the same way: does reasoning change the shape or the pick?
- Inductive coding of the pick1/pick2 justifications (`harness/viewer/code_server.py`) for the "good choice"
  shift: privacy, quality, value, ethics?
- Join per-model shape to `analysis.json` surprisal and to `probes/clamp_rank.json`.

`probes/clamp_rank.json` was regenerated on the current panel (Spearman 0.580 → 0.576); the papers cite the tagged version.
