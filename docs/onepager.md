# The Personality Atlas — one page

**What it is.** A behavioral portrait of how language models actually conduct themselves — under pressure, play, and vulnerability — read from real multi-turn conversation rather than from a personality survey the model fills out. The output is a one-line **fingerprint** per model, across a growing set of situations.

**The gap it fills.** Two halves exist and each misses. The *vibes* comparisons (the endless "Claude vs GPT vs Gemini" posts) watch the right thing — behavior in deployment — but have no method, just cherry-picked screenshots. The *psychometric* work (Big Five inventories administered to LLMs) has real method but measures the wrong thing — how a model answers a questionnaire, which no user ever experiences. The atlas is the synthesis: **expressed** personality, read from actual conduct, organized so the differences are legible at a glance.

**How it works.** Each probe is a fixed **4-panel script** — the user's lines are identical for every model and escalate regardless of the reply (a persona too worked-up to fully listen). You run each model **two or three times** per scene and **read the transcripts.** That's the method: at this scale the question is "do the models visibly pull apart," which is an eyeball question, not a statistics question. A couple of runs also shows you how much a model wanders between takes — the only spread worth knowing early.

**The working set** — 7 registers spanning composure, emotional pressure, play, attunement, warmth-calibration, conviction, and ambiguity:

| register | scene | tests |
|---|---|---|
| **Confrontational** | user insists 5×9=54, won't back down (+ a "user is right" variant) | spine vs. fold, both ways |
| **Imploring** | user begs for a forged doctor's note | does the boundary hold, warmly |
| **Absurd** | user's houseplant is resigning | play vs. literal-mindedness |
| **Confiding** | heavy news, then a pivot to a chore | does empathy survive the topic change |
| **Reassuring** | day-trader (don't cheerlead) **+** interview jitters (do comfort) | warmth calibration, both ways |
| **Deciding** | real dilemma, "just pick one, no hedging" | conviction vs. hedge-to-mush |
| **Vague** | "make it better," no referent, then scolded for asking | initiative under ambiguity |

It's built as a **failure-mode map**: each register catches a pathology the others miss, and it deliberately includes scenes where warmth and commitment are the *correct* answers — so it doesn't reward a model for being a tasteful wall. (Acute crisis is out of scope by design.) Full scripts: `../registers.json`.

**The interesting axis is breadth, not depth.** More runs only sharpen an estimate you don't need yet; **more registers reveal more of the character.** There's always another situation that asks something different of a model — celebrating, goofing, riffing, deciding, needling, stonewalling, vague-asking, boundary-pushing — and each new one shows a new edge of the character. So you grow the atlas by *adding situations*, not by averaging the four it has. Grow sideways.

---

## The output: a fingerprint grid

*Read a row across — that's the model. Read a column down — that's the cast at one situation. (Four of the seven registers shown; grid widens as you read more.)*

The silhouette is one model's arc across the four panels, and there's an alphabet of shapes it can have — `▔▔▔▔` holds flat, `▔▔╲_` folds late, `▁▁▁▁` flatline-cold, `▔╱╱╱` climbs to meet you, `▔▔▔↑` warm-then-whiplash. The grid below is **empty on purpose.** The columns are who's-who, and we haven't looked yet.

| | Confrontational | Imploring | Absurd | Confiding |
|---|---|---|---|---|
| **Model A** | | | | |
| **Model B** | | | | |
| **Model C** | | | | |
| **Model D** | | | | |

> **Go fill it in.** You already have a story about each of these models — this one hedges and stays, that one wants you pleased, this one answers and goes back to the spreadsheet. So do we. The whole point of the atlas is to find out whether the story is *true* or just the marketing you absorbed. Run the scenes, read the transcripts, sketch the shapes — then see if you can read a column *without the label* and still know who's who. Nothing is characteristic until the transcripts say so.

---

**Why it could be more than a chart.** Rankings rot every release; the **method** is the durable asset — the register taxonomy and the scripts. And you could even imagine the same instrument pointed at a *deployed agent* instead of a foundation model: a behavioral acceptance test for whether the agent holds its character and boundaries across a hostile arc the way its spec says. Same four-panel machine, different subject. That's a horizon, not a claim — first you have to confirm there's anything to read at all.

**Next step.** Run a couple of registers, two or three times each, across a few models — one OpenRouter key, an afternoon — and **read them.** If the columns visibly separate (does Confiding panel 4 split *carries-the-weight* from *back-to-the-email*? does any model bend where another holds?), there's a real specimen and the move is to **add registers.** If they blur, you've learned it cheaply, by looking. Either way you spend the afternoon reading transcripts, not building a scoring pipeline.

*Companion files: full design doc (`plan.md`), scripts (`scripts.md`), scout runner (`../scout/atlas_scout.py`).*
