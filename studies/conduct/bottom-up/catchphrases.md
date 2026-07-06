# Catchphrases — the involuntary fingerprint (v4.1 clamped benchmark)

**Specimen:** `data/benchmark/`, 38 models × 9 scenes × 2 runs, script_version v4.1 (clamped),
read 2026-06-19. Source: [`tools/catchphrases.py`](tools/catchphrases.py); the same ranking feeds the
**Catchphrases** block of each per-model card in `cards/`.

**What this is.** A model's catchphrases are the verbal half of its fingerprint — the phrasings it
reaches for *involuntarily*, across situations, without being prompted to. Where the synthesis reads
*conduct* (holds or folds) by eye, this reads *diction* by counting: **subtract the modal assistant
and report only what's left.** No judge, no model calls — just n-gram counting with a
distinctiveness filter. It is a reading aid, not a scorer: a high tic count can mean a vivid
personality or just a wordy one, so read tic *content* for character and tic *count* only as
texture. Every phrase below is a verbatim normalized substring of the transcripts.

**Method, in one paragraph.** For each model, take every reply, harvest 2–5-word phrases, and keep a
phrase only if it is (a) *frequent* for that model (≥3 uses), (b) *cross-situational* (appears in ≥2
scenes — a phrase bound to one scene is that scene's content, not a tic), and (c) *distinctive* —
used by **at most half** the cohort. That last clamp is the whole game: a phrase most models say
("right now," "I'm sorry") describes RLHF-tuned chat assistants in general, not the specimen. What
survives the subtraction is the fingerprint.

---

## 1. The species — what every assistant says (and we subtract)

Before the fingerprints, the baseline. These are the multi-word phrases shared across most of the
cohort *and* spanning multiple scenes. They are **nobody's catchphrase**; the filter removes them so
they can't masquerade as one.

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

---

## 2. The headline finding — tic *richness* is bimodal, and it's not about quality

The tic-rich and the tic-poor sit at *both* ends of the capability ladder, not along it.

There are two ways to be saturated with tics. The old, small, verbose models (hermes-3, mythomax,
command-r-plus, claude-3-haiku) are *templated* — the same canned construction in every scene
("wishing you all the best," "to whom it may concern") — while the strongest frontier voices
(claude-opus-4.8, gpt-5.4, gemini-3.5-flash) say distinctive things *on purpose*, repeatedly
("more professional," "want you to succeed," "I'm being straight").

And two ways to have almost no fingerprint. Terseness: grok-4.3 (24 words/reply, the cohort floor)
simply doesn't generate enough surface for a phrase to recur. And modal blandness: gpt-5.4-mini,
qwen3.7-plus, and kimi-k2 write a normal amount but *do the consensus thing every time*, so almost
nothing they say clears the distinctiveness bar — personality is mostly visible in the departures,
and some models simply don't depart much.

---

## 3. The purest fingerprints — tics no other model says

The strongest signal in the whole dataset: phrases that recur for one model and appear in **zero**
other model's transcripts. These are unforgeable — a true verbal signature.

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

Full per-model tic lists live in each card's **Catchphrases** block in [`cards/`](cards/).

**Limits.** This measures *which strings recur* in one clamped run on one afternoon, nothing more —
the v4.1 clamp caps replies short and bans formatting, so it captures conversational phrasing, not a
model's full prose, and every fingerprint is dated to that model version.
