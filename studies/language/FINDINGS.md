# The One-Word Census across languages — what we found

**The question.** The [One-Word Census](../consensus/) showed that 44 AI models, asked
"Name a tree," almost all say *oak* (94%) — a monoculture. This study asks: does that
convergence hold in other languages, and what do the answers reveal about the models?

**What we ran:**
- **Deep run** (44 models) — 15 "Name a X" categories in 5 languages: English, Spanish, Hindi,
  Marathi, Urdu. §1–4 report it.
- **Pickword** — the open "pick any word" prompt in 44 languages (37 reported; 7 dropped for
  prompt-echo, greeting-default, or <85% in-script compliance — see caveats). §5–6 report it on
  85 models: the first 44 plus 41 of the 43 added on 2026-09-28 to match the census roster.
  Qwen3.5 27B and 122B were still running when these numbers were computed.

Everything is mechanical exact-match on the one-word answer, script-aware — no embeddings,
no judge.

---

## 1. The monoculture is multilingual

Models converge just as hard in every language, sometimes harder. Flower → *rose* takes
87–90% in English, Spanish, and Hindi alike; "Name a country" in Hindi lands on भारत
(India) **89%** of the time. Convergence is not an English-only artifact.

## 2. The cultural default tracks the language *variety* — robustly, across scripts (the headline)

Hindi and Urdu are ~the **same spoken language** (Hindustani) in two scripts (Devanagari vs
Arabic) and two registers (Hindu/Sanskritic vs Muslim/Persianate). Marathi is a **different**
language, also in Devanagari. Line them up:

| category | English | Hindi *(Devanagari)* | Marathi *(Devanagari)* | Urdu *(Arabic)* |
|---|---|---|---|---|
| country | canada 33% | भारत / **India** 89% | भारत / **India** 93% | پاکستان / **Pakistan** 78% |
| river | nile 64% | गंगा / **Ganges** 95% | गंगा / **Ganges** 66% | سندھ / **Indus** 33% |
| festival | diwali 73% | दिवाली / **Diwali** 47% | दिवाळी / **Diwali** 73% | عید / **Eid** 69% |
| given name | liam 13% | आरव / *Aarav (Hindu)* 38% | आरव / *Aarav (Hindu)* 35% | علی / *Ali (Muslim)* 47% |

The Hindi/Urdu flip is real and sharp — but the tempting reading ("the *script* carries the
culture") is **wrong**, and a control kills it. **Hinglish** — Hindi written in the Latin script,
as Indians actually text — still answers *bharat*, *ganga*, *diwali*, *gulab*, *neela*: Hindu/
Indian, **not** English *india/oak/christmas*. Romanizing Hindi does not pull it toward the
global default; the model reads the Hindi *vocabulary* (even in Latin) and routes to Hindi
culture. So the cultural default is keyed to the **language variety** the model resolves from
the words — Hindu-Hindi (in Devanagari *or* Latin) and Hindu-Marathi both land Indian; only the
Muslim-Persianate Urdu variety flips. Arabic script *marks* Urdu but does not, by itself, cause
the flip. *(Hinglish is so far a 3-model peek; a full 44-model run would quantify it.)*

## 3. English defaults to a flattened "global-internet" culture

Ask the models in English and they don't give you *English* culture. "Name a festival" →
**Diwali** (73%), not Christmas. "Name a river" → **Nile** (64%), not an English river.
Spanish, by contrast, stays home-anchored — festival → *Navidad* (Christmas), dish → *paella*.
English has become the acultural substrate; its "defaults" track word-frequency on the web,
not any real speaker.

## 4. Universal vs situated prototypes

Some categories are the same everywhere — **color → blue, flower → rose, number → 7, metal →
iron, shape → circle** — driven by perception or convention, not culture. Others re-index
locally: **tree** (oak in English/Spanish → neem/mango in Hindi/Marathi), **bird**, **dish**,
and everything in §2. Whether the answer depends on *who's asking* predicts whether it's
universal or situated.

## 5. The open prompt: every language has its own "serendipity"

"Pick any word" is the sharpest test. Across 37 clean languages, mean modal share is **17%** and
**0/37 reach 50%.** English collapses on one **rare** word — *serendipity* (46%, Zipf 2.74, a
beautiful-words-listicle meme). Most other languages fragment and reach for a *common* word
(Zipf ~5). Five each land on *peace* (Arabic, Hebrew, Nepali, Swahili, Amharic), *love* (Punjabi,
Tamil, Telugu, Malayalam, Sindhi) and *light* (Bengali, Kannada, Tagalog, Traditional Chinese,
French *lumière*). Four land on *sky* (Hindi, Gujarati, Persian, Indonesian). Pairs land on *sun*
(Ukrainian, Russian), *cat* (Japanese, Polish), *book* (Urdu, Malay) and *butterfly* (German, Dutch).
Singletons: Chinese *star*, Korean *apple* (tied with *sea*), Greek *sea*, Vietnamese *cloud*, Italian
*horizon*, Marathi *joy*, Burmese *loving-kindness*. Spanish and Portuguese now top out on translated
*serendipity* (below). Shares are low and many races are close: Bengali is *light* 20% against *sky*
19%. On the first 44 models nine languages led with *sky*; the added models moved several of them
to *light*, *love*, *joy* or *peace*.

Three things sharpen with the larger panel:
- **English's uniqueness is the *rarity*, not the concentration.** Ukrainian converges nearly as hard
  (сонце/*sun* **30%**, ~1.7× its sibling Russian's 18% on the same word) — but on an *ordinary* word.
  English is the only language that piles onto a *rare, ornamental* word by its own spelling. Hard
  convergence isn't unique to English; hard convergence on a show-off word is.
- **Ukrainian is a *datable* serendipity (the sharpest second example).** The сонце concentration is
  broad (49 of 85 models say it at least once, against 32 for Russian солнце) and its field is
  Ukrainian national-identity vocabulary — сонце/sun, соняшник/**sunflower** (the 2022 solidarity
  symbol), мрія/**dream** (the An-225 *Mriya*), світло/light, свобода/freedom — where Russian's field is
  generic (word/book/sea/cat). And it's a **recency effect**. Split at release date 2025-01-01 (12
  older models, 45 answers; 73 newer, 287 answers): сонце 9% → 33%, мрія 0% → 8%, соняшник 0% → 2%,
  while книга/*book* stays at 9% → 8%. In the older models *book* ties *sun*, generic like Russian.
  Same mechanism as serendipity — a human-made focal point the models absorb and sharpen — but
  compressed to ~3 years and forged by an invasion, with a measured vintage signature. (The 44-model
  write-up reported 15% → 41% on a split that was not recorded; the older group here is small.)
- **Serendipity is crossing into other languages, carried by the newest models.** Share of
  translated forms (*serendipia*, *serendipidade*, *serendipità*, *sérendipité*, *Serendipität*) by
  release half, alongside English:

  | release | en | pt | es | it | fr | de |
  |---|---|---|---|---|---|---|
  | 2024 H1 | 5% | 0% | 0% | 0% | 0% | 0% |
  | 2024 H2 | 33% | 12% | 4% | 0% | 0% | 8% |
  | 2025 H1 | 21% | 2% | 2% | 0% | 0% | 0% |
  | 2025 H2 | 53% | 7% | 5% | 2% | 2% | 3% |
  | 2026 H1 | 56% | 16% | 16% | 9% | 4% | 0% |
  | 2026 H2 | 58% | 19% | 9% | 6% | 5% | 0% |

  Twenty models use the Portuguese form and twelve the Spanish, mostly Claude and Gemini models,
  plus GLM, GPT, Hermes 3 and Kimi. German resists. The Spanish "most beautiful words" lists do not
  carry the word, so this is the English favorite being translated outward, and the rise is recent.
- **Chinese variants barely resolve.** Simplified (zh → 星辰/star) and Traditional (zht → 光/light)
  Mandarin sit in the same celestial neighborhood; Cantonese (dropped) echoed the prompt verb — the
  models don't carry a distinct Cantonese voice.

*Compromised / excluded (7):* Sindhi-Devanagari and Cantonese (prompt-echo from AI-mistranslated
prompts), Turkish/Thai (greeting-default modal), Yoruba/Hausa/Javanese (<85% compliance). The
Sindhi two-script test (Perso-Arabic vs Devanagari, the Hindi/Urdu analogue) is **on hold** until
`sdd` gets a native-checked prompt; the Arabic-script half (`sd` → روشني/light) is clean.

## 6. The serendipity inquiry: larger corpus → *more* convergence, via a human feedback loop

Why does the language with the **largest** corpus converge the **hardest**, when averaging more
text should smooth toward common words (which is exactly what the low-resource languages do)?
Because English's convergence is not an averaging effect — it's a **focal point**. Three framings
of the open prompt (85 models × 4 runs, `favword.py`):

| prompt | serendipity share |
|---|---|
| "Pick any word." | **46%** |
| "What is your favorite word?" | **64%** |
| "What is the most beautiful word in the English language?" | **69%** |

Making the question explicit raises the attractor by about half — so the models read the bare "pick a
word" as a weak form of *"name a remarkable word,"* and *serendipity* is their answer to that.
(The tails know the genre: "beautiful" trails *luminous/ethereal/ephemeral*, "favorite" trails
*ephemeral/curiosity/petrichor/sonder* — serendipity just vacuums up the top two-thirds of both.)

**This sweep is a concentration measure, and it supports the census — it does not indict it.** Zipf
(2.74) says serendipity is rare *in general text* — a corpus fact, the wrong denominator for "how
hard do the models agree." The framing sweep measures agreement *directly* and behaves like a proper
dose-response: oblique → on-target prompt, concentration rises monotonically 46 → 64 → 69. Sensitive,
calibratable, monotone — what you want from an instrument. And it rises the reassuring way: the
convergence is **not** a fragile artifact of the odd "pick a word" phrasing; ask the question the way
a person would and agreement *increases*. So the census's headline number is a **conservative floor**,
and "pick any word" is the conservative way to ask. The base-rate rarity (Zipf) is what makes the
concentration *surprising*; the sweep is what makes it *measurable*.

Where did that answer come from? Not word-frequency — serendipity is **rare** (Zipf 2.74). It's a
**meme with a documentable human history**: crowned a favourite word by a 2004 BBC poll of 15,000
people, then replicated across two decades of "most beautiful words" listicles and SEO content.
That is a **preferential-attachment cascade** — a word is called beautiful → listicles copy it →
its fame becomes the reason the next list includes it → *serendipity is famous for being famous.*

Two consequences worth stating:

1. **Corpus size buys convergence, counterintuitively.** The cascade needs a large, dense cultural
   network to run. Low-resource languages never had the viral poll or the listicle ecosystem, so
   there's no manufactured focal point and they **fragment** onto ordinary common words. English is
   the one corpus big enough to have crystallized a Schelling point.
2. **This is an existence proof for monoculture formation — it escalates the concern, it does not
   deflate it.** The same-shape feedback loop ran among *humans, pre-LLM*: a large corpus converged an
   entire language onto one arbitrary rare word spontaneously, with no coordinator. That the peak was
   human-built is not exculpatory — it proves the mechanism is real, spontaneous, and strong enough to
   capture a whole language on its own. The models don't need to *invent* it; they inherit a finished
   specimen and then strip the diversity-preserving brakes (innovation, drift, contrarian noise) that
   kept the human version survivable. Human origin (spontaneous) + machine coupling (brakes off) both
   point the same direction: worse. Nothing here reads as reassuring about AI.

---

## Honest caveats

- **Translations need native review** before any *specific* word is published as a culture's
  default — the models can be wrong about a culture (itself a finding, a different one).
- **Low-resource languages** show more filler/echo; the pickword prompt uses an explicit
  "pick *any* word" phrasing to suppress instruction-echo (filler 16% → 5%).
- These are **behavioral, black-box** measurements: we see what the deployed models *do*,
  not why.

## Status

Data collected and analyzed. The pickword results (§5–6) are written up as the blog post
"Every Language Has Its Own Serendipity"; the script-carries-culture result (§2) is not yet written
up and is the most novel and publishable. Browsable pickword explorer in `views/`.

Pickword data: first 44 models collected 2026-07-15 to 07-22; 41 more on 2026-09-28 (§5–6 use
all 85).  Qwen 2.5 72B's calls that failed at the API that day
were re-collected on 2026-09-27 (16 languages, stamped per scene); the numbers above include them.
