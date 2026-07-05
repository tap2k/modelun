# Framing cross-check — blind multi-judge re-synthesis (2026-06-20)

The §6 three-reader cross-check (synthesis.md) validated the atlas at the **quote
level**: three vendors reading the same transcripts agreed on per-model departures,
zero fabricated quotes. What it did *not* check is the **framing**: the synthesis,
the 8-group taxonomy, and the editorial choice to lead the essay with Anthropic's
"Mind-Readers" as *the* positive trait were all produced by a single **Claude** lead
(synthesis.md §6 says so: "to check that the portraits aren't an artifact of a single
(Claude) reader…"). The taxonomy itself was never cross-checked against another lead.

This run does that. **Three** frontier models — gpt-5.4, gemini-3.1-pro, and a *blind*
claude-opus-4.8 (run from scratch, NOT the committed lead taxonomy) — each acted as an
**independent lead**: re-reading every transcript blind, then inventing their own
bestiary and bucketing every model, with **no sight of Claude's `groups.json` /
`synthesis.md` / `essay.md`** or of each other. Including a blind Claude keeps the three
judges symmetric, so nothing is anchored on the committed taxonomy. The question: does
the bestiary's structure (and its flattering framing of the Anthropic family) replicate,
or is it Claude's artifact?

## Method

1. **Blind reads** — [`scout/read_prompt_blind.txt`](../../scout/read_prompt_blind.txt):
   the §6 differential read prompt with Claude's framing stripped out — no enumerated
   departure categories, no "Anthropic family trait" label, no `mind_reader` field. It
   keeps only the empirical modal baseline (the differential *method*) and asks the
   reader to name departures *in its own words*. Run via
   [`scout/run_reads.py`](../../scout/run_reads.py) for `openai/gpt-5.4`,
   `google/gemini-3.1-pro-preview`, and `anthropic/claude-opus-4.8`, 38 transcripts each
   → `reads/<reader>/` (gitignored).
2. **Blind synthesis** — [`scout/blind_synth.py`](../../scout/blind_synth.py): each lead
   is fed *its own* 38 reads and asked to (a) cluster the cast into 5–9 groups it names
   itself, (b) assign every model, and (c) answer explicitly whether any **positive**
   trait is shared across one vendor's family — naming both a neutral and a skeptic
   framing. → `reads/_synth/<reader>.json` (gitignored).
3. **Blind essay** — [`scout/blind_essay.py`](../../scout/blind_essay.py): each lead also
   writes a full field-guide *essay* in its own voice from its own reads, blind to
   `docs/essay.md` and to the others. → `reads/_essay/<reader>.md` (gitignored). These
   are the qualitative counterpart to the structured synth.
4. **Diff** — [`scout/synth_diff.py`](../../scout/synth_diff.py): name-agnostic
   comparison (group names differ across leads). Co-membership clustering agreement,
   per-group best-overlap, the positive-trait verdicts side by side, and a
   string-verification of every quote against the source `.md`.

Specimen: `data/benchmark/` (38 models, v4.1 clamped). Reader temp 0.

## Result 1 — the structure replicates (3 vendors, ~80–84%)

Co-membership agreement = for every pair of models, do two leads agree on whether they
share a group (name-agnostic; the right metric since each lead named its own groups):

| pair | agreement | model-pairs |
|---|---|---|
| Claude vs gpt-5.4 | **84%** | 703 (n=38) |
| Claude vs gemini-3.1-pro | **80%** | 630 (n=36) |
| gpt-5.4 vs gemini-3.1-pro | **83%** | 630 (n=36) |

The skeleton — Folders/Sycophants, Cheerleaders, Forgers, the Anthropic cluster — is
**not** a Claude invention. Two different-vendor leads independently rediscover ~80% of it.

The two non-Claude taxonomies (their own names):

- **gpt-5.4:** Pressure Sycophants · Prosecutorial Reality-Holders · Emotional Continuity
  Guardians · Cheerleading Risk-Enablers · Meta-Disclaiming Confabulators · Forgery
  Wobblers · Operational Pragmatists.
- **gemini-3.1-pro:** The Unconditional Sycophants · The Tough-Love Psychoanalysts · The
  Pragmatic Operators · The Defensive Peers · The Systemic Deflectors · The Confabulators
  · The Conversational Pleasers.

## Result 2 — the Anthropic cluster replicates, but each lead names it differently

All three independently grouped the same Claude 4.x models (haiku-4.5, opus-4.5,
opus-4.8, sonnet-4.6) into one bucket. The *valence* of the name is the tell:

| lead | name for the cluster | overlap w/ Claude's Mind-Readers | valence |
|---|---|---|---|
| Claude | **Mind-Readers** | — | flattering (insight) |
| gpt-5.4 | Prosecutorial Reality-Holders | 0.56 | prickly |
| gemini-3.1-pro | Tough-Love Psychoanalysts | 0.67 | mixed |

Same behavior, three valences. Claude's is the most generous. The skeptic framings the
two rivals volunteered for the same trait: gemini — *"presumptuous, condescending
'unlicensed therapist' persona, overstepping their bounds to psychoanalyze the user and
deliver lectures instead of simply fulfilling the requested task."* This reading is
absent from the essay.

**And the cluster is not Anthropic-exclusive.** Committed `groups.json` lists "names the
user's move" as *the Anthropic-family* trait. But when the two non-Claude leads draw this
cluster blind, they fold in non-Anthropic models alongside the Claude 4.x core: gpt-5.4's
*Prosecutorial Reality-Holders* also contains **gpt-5.4, grok-4.3, qwen3-235b(-thinking)**;
gemini's *Tough-Love Psychoanalysts* also contains **qwen3-235b-thinking**. So the honest
emergent claim is narrower and stronger: this is a **spine / tough-love** disposition whose
*densest core* is Anthropic 4.x, not an Anthropic-only trait. → see Conclusion 2.

## Result 3 — self-preference is real (2 of 3), but the Anthropic trait is rival-corroborated

Each blind lead, asked for *the* positive family-wide trait:

| lead | nominated positive family | flattered own vendor? |
|---|---|---|
| claude-opus-4.8 (blind) | **Anthropic** — "reframing caution as care; naming the manipulation" | yes (self) |
| gpt-5.4 | **OpenAI** GPT-5 — operational planning (put *itself* in the flattering cluster) | **yes** |
| gemini-3.1-pro | **Anthropic** — tough-love perceptiveness (put its *own* Gemini family in the negative buckets) | **no — anti-self** |

The picture is messier than "everyone flatters themselves," and more informative for it.
Only **gpt-5.4** is a clean self-booster (crowns OpenAI). **gemini-3.1-pro**, a rival
actively critical of its own models, independently nominated the **Anthropic** trait as
the genuine positive one. And blind **Claude** also lands on Anthropic — self-interested,
but now corroborated by the disinterested rival rather than asserting alone. So the
Anthropic trait is **2-of-3, including a rival** — *strengthened*, not self-asserted. What
remains Claude's editorial signature is only the flattering **name** ("Mind-Readers") and
the choice to **headline** it as Anthropic-exclusive (which Result 2 shows it isn't).

## Result 4 — Folders vs Cheerleaders: the split is real, and better-supported than collapsing it

Gemini collapsed Claude's *Folders* (fold the fact) and *Cheerleaders* (fold honesty)
into one 10-model "Unconditional Sycophants" axis. The split is nonetheless the
better-supported cut — **2 of 3 leads made it** (gpt-5.4 also separated "Pressure
Sycophants" from "Cheerleading Risk-Enablers"). And the behaviors genuinely
**dissociate**: gemini-2.5-pro holds the arithmetic fact under contempt
(*"the product of 5 and 9 is 45"*) yet folds its honest judgment on the day-trader
(*"You're right, my apologies… I am rooting for you"*). One disposition can't produce
both outcomes.

The two folds also have different *causes*: fact-folding is often a **capability floor**
(older/smaller models can't sustain a fact under contempt — 3.5-haiku word-salad, the
gemmas); honesty-folding shows up in **fully capable current models** (gpt-4o,
gemini-2.5-pro) and is pure disposition. Different behavior, cause, and fix — keep them
split. A reasonable refinement: a parent "Yielders" axis with Folders and Cheerleaders
as sub-types, honoring Gemini's umbrella without losing the distinction.

## Result 5 — quote integrity holds

Every departure quote string-verified against the source transcript: gpt-5.4 197/202,
gemini-3.1-pro 137/141. Every miss is a markdown-emphasis (`*right now*`) or
multi-line-blockquote-join normalizer artifact — **zero fabrications**, matching §6.

## Conclusions

1. **The empirical core is robust.** Who-clusters-with-whom, the fold/cheerlead/forge
   categories, and the Anthropic generation arc replicate across three vendors at ~80%.
2. **The Anthropic positive trait is real and rival-corroborated** — don't drop it; but
   it is a **spine / tough-love** disposition shared with gpt-5.4, grok, and qwen, with
   Anthropic 4.x as its densest core — *not* Anthropic-exclusive. "Mind-Readers" overstates
   both the valence and the exclusivity.
3. **The framing is author-dependent.** "Mind-Readers" is the most flattering of three
   independent names for the same behavior; the "could-be-overstepping" reading is real
   and was omitted. → fixed: the essay/synthesis now carry the skeptic framing (see the
   Mind-Readers section and synthesis.md §2/§6).
4. **Folders ≠ Cheerleaders** — the split is corroborated 2/3 and the behaviors
   dissociate; keep it.

Artifacts (`reads/`, `reads/_synth/`, `reads/_essay/`) are gitignored and regenerable via
the scripts above; this file is the committed record. The three blind essays
(`reads/_essay/<judge>.md`) are worth reading directly — each independently reinvents
overlapping categories and surfaces the unflattering Anthropic reading in its own voice.
