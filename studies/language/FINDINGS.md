# The One-Word Census across languages — what we found

**The question.** The [One-Word Census](../consensus/) showed that 44 AI models, asked
"Name a tree," almost all say *oak* (94%) — a monoculture. This study asks: does that
convergence hold in other languages, and what do the answers reveal about the models?

**What we ran** (44 models each):
- **Deep run** — 15 "Name a X" categories in 5 languages: English, Spanish, Hindi, Marathi,
  Urdu.
- **Pickword** — the open "Pick a word" prompt in 21 languages.

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

"Pick a word" is the sharpest test. English collapses on one **rare** word — *serendipity*
(43%, a beautiful-words-listicle meme). **No other language does.** Each fragments and reaches
for its own *common* word — love, peace, light, freedom (सुख/prem, שלום… love/peace/light) —
(Hindi प्रेम/love, शांति/peace; Arabic سلام/peace; French/Italian *liberté*/*libertà*/freedom)
— and it's a different concept per language, not a translation of serendipity. English's
convergence here is a training-data artifact unique to English.

---

## Honest caveats

- **Translations need native review** before any *specific* word is published as a culture's
  default — the models can be wrong about a culture (itself a finding, a different one).
- **Low-resource languages** show more filler/echo; the pickword prompt was cleaned to an
  "any word" phrasing (v2) that cut filler from 16% → 5%.
- These are **behavioral, black-box** measurements: we see what the deployed models *do*,
  not why.

## Status

Data collected and analyzed; **not yet written up as a paper or post.** The script-carries-
culture result (§2) is the most novel and publishable. Browsable pickword explorer in
`views/`; hypotheses and priorities on the research desk (`convengineering/modelUN/
language-census/`).
