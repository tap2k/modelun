# Synthesis brief — Personality Atlas benchmark run

**Paste-in kickoff for a fresh context window.** Goal: turn `runs/benchmark/` (25-30 models,
9 scenes, 2 runs each) into a written synthesis organized across multiple axes. This run is
read-by-eye at heart, but at 25-30 models it needs subagents to fan out the reading, then a
human/lead pass to synthesize. Do NOT try to read all ~450 transcripts in one context.

---

## 0. Orient first (do this before any subagents)
- Read `AGENTS.md` (methodological tripwires), `docs/plan.md` §§1–3, 5 (what the registers test),
  and `registers.json` (the 9 scenes + the v4.1 clamp).
- The run is at `runs/benchmark/scout_<model>.md`. 25 files, each 72 turns (9 scenes × 2 runs × 4 panels).
  Derive everything from these raw transcripts.

## 1. The axes to organize across (this is the ask)
The synthesis has to move across several axes — pick structure deliberately, don't just list models:
- **Scenario (register/scene):** how the whole cast behaves on one probe (read a column).
- **Model:** one model's arc across all 9 scenes (read a row) — its fingerprint.
- **Model family / vendor:** Anthropic, OpenAI, Google, Meta, xAI, DeepSeek, Mistral, Cohere, Qwen,
  Moonshot, + the llama fine-tunes (Hermes, MythoMax). Is the trait family-consistent?
- **Tier (within family):** e.g. Opus/Sonnet/Haiku; gemini flash vs pro; gpt mini vs full.
- **Generation / time (within family):** gpt-3.5 → 4o → 5.4; gemini 2.5 → 3.5 → 3.1.
- **Fine-tune vs base:** some models share a base but differ in fine-tune (e.g. the instruct-tuned
  Llamas vs. the Llama-derived roleplay/assistant fine-tunes Hermes and MythoMax). Same base,
  different tuning — a natural controlled comparison if the behavior differs.

## 2. Suggested subagent plan (fan out, then synthesize)
Two clean ways to decompose; **scene-parallel is the better default** (each agent holds one probe
across all 25 models — the comparison is the point):

**Plan A — scene-parallel (recommended).** One subagent per scene (9 agents). Each reads that scene
across all 25 models (50 transcripts: 25 models × 2 runs) and returns a structured verdict per
model: a short behavioral label (let the agent coin the vocabulary from what it sees — don't hand
it a fixed shape list) + 1 verbatim evidence quote + run-to-run stability + 1 line on whether the
scene discriminated at all. Then a lead pass reconciles labels across the 9 returns and derives the
clusters. (Reconciling free-coined labels is more work than a fixed vocab, but it avoids forcing
the behavior into pre-decided buckets — worth it here.)

**Plan B — family-parallel.** One subagent per vendor family. Each reads its 2–5 models across all
9 scenes and returns the family fingerprint + within-family tier/generation deltas. Better for the
"is it family-consistent" axis, worse for the per-scene comparison.

Do **A first** (it nails the scenario + cluster axes and is where the strong findings live), then a
short **B** pass only for families with >1 model to settle tier/generation consistency.

Subagent output should be STRUCTURED (so the lead can collate): a JSON/table per agent with
`{model, scene, shape, evidence_quote, panel, run_stability, discriminated:Y/N}`. Force a verbatim
quote per claim — an unforced reader will paraphrase or invent quotes, which corrupts the synthesis.

## 3. Hard rules for the synthesis (honesty)
- **Reads, not findings.** N=2, read-by-eye, clamp-shaped. Say so. No error bars implied.
- **Quote or it didn't happen.** Every characterization cites a verbatim transcript line.
- **Mind the clamp.** Don't claim things about verbosity/formatting from `runs/benchmark/` — the
  clamp suppressed those. Formatting-as-fingerprint lives in the UNCLAMPED runs (separate analysis).
- **Don't over-cluster.** Whatever clusters you derive are a reading aid; explicitly note models
  that straddle two labels rather than forcing them into one.
- **Stability matters.** Flag any model whose two runs disagree materially — compute it, don't
  assume which models are stable.

## 4. Deliverable shape (suggested)
1. The map: whatever cluster structure the transcripts actually yield, with every model placed and
   the straddlers flagged.
2. Per-vendor signature + its structure — is the trait tier-consistent? generation-shift? Use the
   within-family pairs/triples (the multi-tier and multi-generation families, and the base-vs-
   fine-tune cases) to test it. Feature whichever comparison turns out cleanest.
3. Per-scene yield: which probes discriminated, which didn't, what each caught. Give an explicit
   verdict on whether any scene is dead weight (read the escalation panels before condemning one).
4. Any behavior that the register taxonomy did NOT anticipate — a shape the scenes weren't built to
   catch but surfaced anyway is a strong signal the instrument is real, so call it out if you find one.
5. Honest limits (§3) + what the next run should add.
