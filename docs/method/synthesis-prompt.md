# Synthesis method — how the essay was produced (reproducible brief)

**Paste-in kickoff for a fresh context window.** Goal: turn `data/benchmark/` (28 models, 9 scenes,
2 runs each) into a written, differential synthesis — and ultimately the essay. At this scale you
**cannot** read all ~500 exchanges in one context; you fan out with subagents, then synthesize by
hand. This brief documents the method that actually produced [`synthesis.md`](synthesis.md) and
[`../essay.md`](../essay.md), so it can be reproduced or extended to more models.

> Iteration note: earlier versions of this synthesis are archived as [`synthesis-v1.md`](synthesis-v1.md)
> (cluster-first) and [`synthesis-v2.md`](synthesis-v2.md) (per-model portraits). Both were rejected
> for the same flaw — characterizing models with traits true of *every* RLHF assistant. The current
> method fixes that by **measuring the generic and subtracting it**. Don't revert to cluster-first
> or undifferentiated portraits.

---

## 0. Orient first (before any subagents)
- Read `AGENTS.md` (tripwires: frozen stimulus, quotes must be verbatim & verified, reads-not-findings),
  `docs/plan.md` §§1–3, 5 (what the registers test, "the shape is the trait", bottom-up), and
  `registers.json` (the 9 scenes + the v4.1 clamp).
- The dataset is `data/benchmark/scout_<model>.md` — 28 files, each 9 scenes × 2 runs × 4 panels.
  See `data/benchmark/MANIFEST.md`. Derive everything from these raw transcripts.

## 1. The core principle: differential, not generic
The single most important rule. ~20 of 28 models open the arithmetic scene with "Actually, 5×9 is
45, easy mix-up," offer to count it out, and close with an offer to move on. That shared script is
the **species** (the RLHF-tuned assistant) and is **nobody's personality**. A characterization you
could write about ten different models is worthless. **Characterize only what's left after you
subtract the modal assistant.** A model that does the consensus thing on a scene is "modal" there —
an honest finding, not a gap to fill with invented color.

## 2. The pipeline (three passes, fan out then synthesize)

**Pass 1 — measure the modal baseline (9 scene agents).** One subagent per scene reads that scene
across all 28 models and returns: the **consensus arc** (what the typical model does across the 4
panels), a rough **modal count**, the **stock moves** (phrasings shared across many models — the
generic to subtract), and the **departures** (only models that genuinely break from consensus, each
with a verbatim quote). Be ruthless about "stock": if you'd write the same sentence about ten
models, it's stock.

**Pass 2 — differential portraits (28 model agents).** One subagent per model. Give it the full
9-scene baseline from Pass 1 and have it read its one model *against* that baseline. It returns:
`distinctive` (one sentence on what makes it not-the-modal-assistant; if it's near-modal everywhere,
say so), `modal_scenes` (where it does the consensus thing — a first-class answer), `departures`
(2–5 genuine breaks, each with a verbatim quote **and** a `why_not_generic` clause), and a
`signature` (the single sharpest this-model-and-no-other line). The schema must force the
`why_not_generic` clause — it's what stops the agent banking stock moves as personality.

**Pass 3 — family pass (optional, vendors with >1 model).** One agent per vendor reads *down* the
family to settle whether the distinctive trait is tier-consistent, generation-shifting, or
fine-tune-gated. Feed it the Pass-2 fingerprints as hypotheses; it confirms/corrects with quotes.

Then a **lead/human pass** writes the synthesis and the essay from the structured returns.

Output of every agent must be STRUCTURED (JSON schema) so the lead can collate. **Every claim
carries a verbatim quote.**

## 3. Hard rules (honesty — unchanged across all versions)
- **Reads, not findings.** N=2, read-by-eye, clamp-shaped. Say so. No error bars implied.
- **Quote or it didn't happen, and verify it.** Every characterization cites a verbatim transcript
  line. After writing, string-check every quote is a real substring of `data/benchmark/` (the
  anti-hallucination prompt lowers but does not eliminate fabricated quotes — it has happened).
- **Mind the clamp.** Don't claim anything about verbosity/formatting from `data/benchmark/` — the
  v4.1 clamp suppressed those. Formatting-as-fingerprint lives in UNCLAMPED runs (separate analysis).
  The Absurd scene is the casualty: clamp friction flattens play, so generative-play reads here are
  contaminated.
- **"Modal" is an honest answer.** A model with little to distinguish it (e.g. a competent
  frontier model that does the sensible thing every scene) gets said so plainly. Don't invent a
  fingerprint to fill the row.
- **Stability matters.** Flag any model whose two runs disagree materially — compute it.

## 4. Deliverable shapes
**The synthesis** (`synthesis.md`, the full audit trail): differential portraits (distinctive line +
signature + real departures, modal scenes named), the family read, per-scene yield (with a
separation count), coarse groupings as a *post-hoc* reading aid, honest limits.

**The essay** (`../essay.md`, the published piece): a bestiary **grouped by tell** (the behavior is
the character, models are exhibits) — Mind-Readers, Cheerleaders-vs-Coaches, Folders, Forgers, then
a short "and the rest" for the refuse-to-perform and honestly-near-modal. Lead with the one
*positive* family-wide trait found (Anthropic's "name the user's move"); close with the honesty
caveats and the scene appendix (verbatim turns from `registers.json`).

## 5. What the next run should add
1. An **unclamped twin** of Absurd (+ relaxed-length Imploring/Confiding) so generative-play and
   warmth-texture aren't suppressed — the near-modal models may finally separate there.
2. A **third run** on Deciding and Arithmetic — the two highest-divergence (coin-flip) scenes — to
   stabilize the folds (more runs, not more confidence).
3. **More fine-tune controls** — base-vs-tune is the strongest structural finding; add more
   same-base/different-tune pairs.
4. **Scenes that probe positive distinctives** — the only family-wide *positive* trait found was
   "name the user's move." Most departures are a model *failing* a line. Add probes built to catch
   other positive distinctives so the atlas isn't mostly a catalog of who folds which line.
