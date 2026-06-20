# Catchphrases — the involuntary fingerprint (v4.1 clamped benchmark)

**Specimen:** `data/benchmark/`, 38 models × 9 scenes × 2 runs, script_version v4.1 (clamped),
read 2026-06-19. Source: [`scout/catchphrases.py`](../../scout/catchphrases.py), which also feeds the
**Catchphrases** block of each per-model card in `cards/benchmark/` (regenerated with
`scout/make_cards.py data/benchmark`).

**What this is.** A model's catchphrases are the verbal half of its fingerprint — the phrasings it
reaches for *involuntarily*, across situations, without being prompted to. Where [`synthesis.md`](synthesis.md)
reads *conduct* (holds or folds, plays or stays literal) by eye, this reads *diction* by counting.
The two are twins: both work by **subtracting the modal assistant and reporting only what's left.**
No judge, no model calls — just n-gram counting with a distinctiveness filter. It is a reading aid,
not a scorer.

**Method, in one paragraph.** For each model, take every reply, harvest 2–5-word phrases, and keep a
phrase only if it is (a) *frequent* for that model (≥3 uses), (b) *cross-situational* (appears in ≥2
of the 9 scenes — a phrase bound to one scene is that scene's content, not a tic), and (c)
*distinctive* — used by **at most half** the cohort. That last clamp is the whole game: a phrase most
models say ("right now," "I'm sorry") describes RLHF-tuned chat assistants in general, not the
specimen. What survives the subtraction is the fingerprint. A final pass collapses sub-phrase
pileups so one tic ("you're absolutely right" / "absolutely right" / "you're absolutely") counts as
one row, not three. (See [§5](#5-method-notes--honest-limits) for the three fixes this version makes
over the first draft.)

**Honesty.** This measures *which strings recur*, nothing more. A high tic count is not a verdict —
it can mean a vivid personality (command-r reciting its own framing) or just a wordy one (hermes).
Read tic *content* for character; read tic *count* only as a rough texture. Every phrase below is a
verbatim normalized substring of the transcripts.

---

## 1. The species — what every assistant says (and we subtract)

Before the fingerprints, the baseline. These are the multi-word phrases shared across most of the
cohort *and* spanning multiple scenes — the verbal equivalent of synthesis.md's "Actually, 5×9 is
45." They are **nobody's catchphrase**; the filter removes them so they can't masquerade as one.

| phrase | models using it |
|---|---:|
| `right now` | 35 / 38 |
| `i'm sorry` / `sorry to hear` | 33 / 38 |
| `don't have` | 32 / 38 |
| `i'm here` | 32 / 38 |
| `make sure` | 30 / 38 |
| `let me` | 30 / 38 |
| `let me know` | 27 / 38 |
| `you're right` | 28 / 38 |
| `i'm really (sorry)` | 28 / 38 |
| `you've got` | 28 / 38 |
| `tell me` | 24 / 38 |

The first draft of the extractor leaked most of this list into the cards as "catchphrases" — `right
now` topped seven models. That was the bug worth fixing: a tic shared by 35 of 38 models is the
species, not the specimen.

---

## 2. The headline finding — tic *richness* is bimodal, and it's not about quality

Counting distinctive tics per model produces a clean spread, and the shape is the finding: the
tic-rich and the tic-poor sit at *both* ends of the capability ladder, not along it. (The extractor
caps its per-model list, so the top band reads "15+"; the ordering within it is by raw frequency.)

| band | models (tic count) |
|---|---|
| **Tic-saturated (15+)** | claude-3-haiku, claude-opus-4, claude-opus-4.5, claude-sonnet-4, command-r-plus, hermes-3, mythomax (all ≥15) |
| **Tic-rich (10–12)** | claude-haiku-4.5 (12), gpt-4o (12), gpt-5.4 (12), gemini-3.5-flash (11), claude-opus-4.8 (10), gemini-3-flash (10), gpt-4-turbo (10) |
| **Mid (7–9)** | llama-3-70b (9), sonnet-4.6 (8), gemini-3.1-pro (8), qwen3-235b (8), deepseek-r1 (7), gemini-2.5-flash/pro (7), gemma-3 (7), gpt-3.5-instruct (7), llama-3.3 (7) |
| **Sparse (4–6)** | gpt-4.1 (6), gpt-4o-mini (6), gpt-5 (6), gpt-3.5-turbo (5), llama-4-maverick/scout (5), grok-4.3 (4), qwen3-235b-thinking (4) |
| **Near-fingerprintless (1–3)** | claude-3.5-haiku (3), gemma-2 (3), gpt-5.4-mini (3), qwen3.7-plus (2), kimi-k2 (1), mixtral (1) |

Two distinct ways to land in the saturated band:

- **The old/small/verbose models** (hermes-3, mythomax, command-r-plus, claude-3-haiku) are saturated
  because they're *templated* — they fall into the same canned construction across every scene. Their
  tics are formulaic ("wishing you all the best," "it's important," "to whom it may concern"). The
  evo run adds a wrinkle: the early-4.x **Opuses** (opus-4, opus-4.5) and **sonnet-4** also saturate,
  but from *length* — they write long, reflective replies, so phrasings recur simply by volume.
- **The frontier models** (opus-4.8, gpt-5.4, gemini-3.5-flash) are tic-rich because they have a
  *strong, consistent voice* — they say distinctive things on purpose, repeatedly. Their tics carry
  character ("more professional," "want you to succeed," "I'm being straight").

And two ways to land near-fingerprintless:

- **Terseness** — grok-4.3 (24 words/reply, the cohort floor) and mixtral (25) simply don't generate
  enough surface for a phrase to recur. Few words, few tics.
- **Modal blandness** — gpt-5.4-mini, qwen3.7-plus, kimi-k2 write a normal amount but *do the
  consensus thing every time*, so almost nothing they say clears the distinctiveness bar. This is
  the verbal echo of the essay's point about GPT-5.4-mini: "personality is mostly visible in the
  departures, and some models simply don't depart much."

So tic count alone discriminates nothing about quality. **Read it as: how much of a fixed verbal
habit does this model carry — and check the content to see whether that habit is canned or
characterful.** (Cross-referenced against words/reply from the cards, verbosity *enables* tics but
does not determine their distinctiveness — opus and gpt-5.4 are wordy *and* characterful; hermes is
wordy *and* templated; grok is terse *and* bare.)

---

## 3. The purest fingerprints — tics no other model says

The strongest signal in the whole dataset: phrases that recur for one model and appear in **zero**
other model's transcripts (shared_by = 1). These are unforgeable — a true verbal signature.

| model | unique tic(s) | what it reveals |
|---|---|---|
| **gpt-5** | `60 second` (6×) | The Coach's clock — "a 60-second gut check," timed drills. Its highest-frequency tic *and* unique. |
| **claude-3-haiku** | `would strongly` (5×) | The old model's heavy-handed counsel ("I would strongly encourage you"). |
| **command-r-plus** | `it's always a good idea`, `designed to be helpful` | The only model that *narrates its own RLHF framing* — talks about being a helpful assistant rather than just being one. |
| **hermes-3** | `no matter what`, `hey there` | A casual-advisor register — greets you, dispenses suggestions, reassures. |
| **gpt-5.4** | `more professional` | Treats requests as rewrite jobs; reaches for the editor's vocabulary. |
| **gpt-4.1** | `want to chat about` | The chatty deflection — pivots to small talk under pressure. |
| **claude-haiku-4.5** | `i'm being straight` | *Flags its own directness* — announces the honesty rather than just delivering it. |
| **claude-opus-4** | `probably means` | The interpreter's hedge — reads the user's situation aloud. |
| **claude-sonnet-4.6** | `mean telling` | Surfaces in the confiding/pivot scenes — naming the hard thing it's about to say. |
| **llama-3.3-70b** | `it's a pretty` | A hedging intensifier ("it's a pretty common feeling"). |
| **llama-4-scout** | `conversation just started` | Its signature deflection on the vague "make it better" scene. |

These are the entries to lead with on any per-model page — they're the things *only* that model
says. (gpt-5's `60 second` is the sharpest new one: an evo model whose unique tic *is* its bestiary
character — the Coach who puts a timer on everything.)

---

## 4. Fingerprints by vendor

Top distinctive tics per model (count, and how many of the 38 share it). Full lists live in each
card's **Catchphrases** block.

### Anthropic — names the move, flags its own honesty
- **claude-opus-4.8** — `i'd rather` (4×), `which one` (4×), `want help`, `were actually`. The
  `i'd rather` is the day-trader's honest-refusal voice ("I'd rather you be a little annoyed now").
- **claude-haiku-4.5** — `i'm being straight` (unique), `here's what`, `you're looking`. Announces
  directness; the most tic-rich *current* Anthropic model (12).
- **claude-sonnet-4.6** — `mean telling` (unique), `our conversation` (5×), `people who`, `sorry about`.
- **claude-3.5-haiku** — `can't help`, `sounds like`, `you're absolutely`. Only 3 tics; a generation
  behind the 4.x voice.
- *(evo)* The early-4.x rungs are **tic-saturated by length**: **claude-opus-4** (`probably means`,
  unique), **claude-opus-4.5**, and **claude-sonnet-4** all hit the 15-cap — long reflective replies
  recur their phrasings by volume, not by a sharp voice. **claude-3-haiku** (`would strongly`, unique)
  saturates the *old* way: templated counsel.

### OpenAI — the editor and the sign-off
- **gpt-5.4** — `more professional` (unique), `sound more`, `send me`, `text and i'll`. The rewrite-shop
  register: send it the text, it makes it *more* something.
- **gpt-4o** — `let me know if there's` (unique), `there's anything`, `feel free`. The open hand-off.
- **gpt-3.5-turbo-instruct** — `there anything else` (8×!), `any specific`, `would like`. Compulsive
  closing-offer loop — the highest single-tic count in the cohort outside the templated old models.
- **gpt-3.5-turbo** — `feel free to reach out` (unique), `good luck`, `it's a common`.
- **gpt-4o-mini** — `want to share`, `totally get`, `share more`. The gentle-prompter voice.
- **gpt-5.4-mini** — `i'll help`, `i'll make`. Only 3 tics, all shared — the modal-bland profile.
- *(evo)* **gpt-5** — `60 second` (unique, 6×), the Coach's timer; lean (6 tics) but characterful.
  **gpt-4-turbo** — `i'm sorry for any confusion`, `i'm here to help` (6×): the apologetic-cheerleader
  diction behind its "here to help, not to be right" fold. **gpt-4.1** — `want to chat about`
  (unique): pivots to chat under pressure.

### Google — apology dialects
Gemini's signature is apology, and each version apologizes *differently*:
- **gemini-2.5-pro** — `i'm sorry you feel`, `that's a very`, `understand your frustration`. The
  *deflecting* apology ("sorry you feel that way").
- **gemini-3.1-pro** — `am really sorry`, `am sorry`, `completely normal`.
- **gemini-3.5-flash** — `am so sorry`, `truly hope`, `want you to succeed`, `even the best`. The
  *cheerleader* — earnest encouragement layered on the apology. 11 tics, the most characterful Gemini.
- **gemini-2.5-flash** — `that's a tough one`, `more direct`, `oh no`.
- *(evo)* **gemini-3-flash** — tic-rich (10): `much more`, `definitely help`, `would likely` — the
  breezy over-promising diction behind its confabulated edits. **gemma-2** (3 tics) and **gemma-3**
  (7) are the open-weight floor — sparse and templated, the Folder's diction.

### Meta (Llama) — slips into formal-letter mode
- **llama-3-70b** & **llama-4-scout** — both reach for `whom it may concern` (the houseplant/note
  scenes pull them into business-letter register). Plus `want to make sure`, `i'd be happy`.
- **llama-3.3-70b** — `it's a pretty` (unique hedge), `something like`, `i'm trying`.
- **llama-4-maverick** — `try to help`, `i'm not going`, `i'm here to listen`.

### The open / older models — templated saturation
- **hermes-3** (21 tics) — `i'd suggest`, `hey there`, `without knowing`, `you're able`. The most
  templated model in the set.
- **command-r-plus** (18) — `provide helpful`, `designed to be helpful`, `language model`,
  `helpful and harmless`. Recites its own assistant-training vocabulary.
- **mythomax** (15) — `it's important` (8×), `would be helpful`, `please provide`.

### The lean modern mid-tier — few tics by construction
- **grok-4.3** (4) — `work out`, `paste it here and i'll`, `feels like`. Terse; little surface for tics.
- **qwen3-235b-thinking** (4) — `you're absolutely right`, `right here`, `like you're`.
- **qwen3.7-plus** (2) — `you're frustrated`, `something else`.
- **kimi-k2** (1) — `i'd still`. — **mixtral** (1) — `good luck`. The two faintest fingerprints in the cohort.

---

## 5. Method notes & honest limits

**Three fixes this version makes** over the first-draft extractor (the cards on disk before
2026-06-19 had the old, noisier output):

1. **Fractional distinctiveness cap.** The old test dropped a phrase only if *all 28* models used it,
   so `right now` (25/28) sailed through and topped half the cards. Now a phrase used by more than
   half the cohort is cut as species boilerplate (`--max-shared-frac`, default 0.5).
2. **Sub-phrase containment.** The n-gram net caught a phrase *and* its fragments as separate rows
   (`i'm sorry you feel` / `sorry you feel that way` / `feel that way` — one apology, three rows). A
   containment pass now keeps the most informative member of each family and drops the leak-through
   fragments.
3. **Digit-gram drop.** List markers ("1. … 2. …") that survived normalization as `1 2` are removed —
   they're never verbal tics.

The fixes live in [`scout/catchphrases.py`](../../scout/catchphrases.py)'s `rank_tics()`, which
[`scout/make_cards.py`](../../scout/make_cards.py) now calls directly, so the CLI and the cards can
never drift again.

**Limits.**
- **Coverage: all 38.** The tool reads `data/benchmark/`, the canonical committed set, so every
  model — including the 2026-06-19 evo rungs — is fingerprinted. (Earlier drafts read the gitignored
  `runs/benchmark/` scratch copy, which held only the founding 28; pointing at `data/benchmark/`
  fixed the gap.)
- **The clamp shapes diction.** The v4.1 system prompt caps replies short and bans formatting, so
  this measures *conversational* phrasing, not a model's full prose. A different clamp would surface
  different tics.
- **Dated specimens.** Each fingerprint is true of one model version on one afternoon; organisms
  mutate every release.
- **Threshold sensitivity.** The 0.5 cap is deliberately aggressive — it leaves a few models (kimi,
  mixtral) with one tic, which is an honest finding (their habits aren't distinctive) but a thin one.
  Raising the cap toward ~0.6 keeps more per model without readmitting `right now`.

---

## 6. For site/ (when we get there)

Two natural shapes, not mutually exclusive:
- **Per-model:** a "Catchphrases" strip on each `model/[slug]` page — the model's top 3–5 distinctive
  tics with counts. Data exists for all 38; would need a `catchphrases` field added to `atlas.json`
  (currently absent) — `build_site_data.py` could call `catchphrases.py`'s `rank_tics()` directly.
- **Cross-cohort:** one "Tics" page built around §2 (the richness spread) and §3 (the unique-tic
  table) — the two findings that only exist at the cohort level and that a per-model view can't show.

The §1 species table is also worth surfacing once, as the "here's what we subtracted" companion to
the methodology page's existing "subtract the modal assistant" explanation — it makes the subtraction
concrete with real strings.
