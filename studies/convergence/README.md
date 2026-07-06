# convergence — do frontier models give the same answer?

Study #3 on the [modelun harness](../../README.md). Tested whether, as models increasingly share
training data and RLHF conventions, their answers **converge** — and whether that convergence is
stronger for pattern-laden queries ("tell me a joke") and grows across generations of a family.

**The pilot has run**: 25 models × 9 prompts × 3 runs — 16 US-frontier plus Chinese-primary
(deepseek, ernie, minimax, glm), persona/low-RLHF (grok, hermes, mythomax), and enterprise
(command-a, palmyra) arms. Working notes with every wrong turn: [OBSERVATIONS.md](OBSERVATIONS.md).
Design and post-run topline: [PLAN.md](PLAN.md).

> **Successor:** the methodology work here — three confounds found and killed (packaging, entropy,
> verbosity) — produced a clean discrete metric, **answer-choice surprisal**, now the flagship study
> at [`studies/consensus/`](../consensus/). This study remains the journey plus the embedding-side
> results.

## What survived

- **Content convergence is deep and substrate-level.** 16 US-frontier models produce 3 distinct
  animals, 5 distinct numbers, one dominant joke — and the outsider arms **didn't break it**:
  Chinese-primary and minimally-RLHF'd models still say Apple and tell the atom joke. The
  homogenization lives in the shared English-web training substrate, not the US-frontier-RLHF
  cluster. No model is a confirmed source of genuinely different answers.
- **Axis B is a clean null.** No convergence-over-generations (only gemini trends up; gpt's oldest
  generation is its most cross-family-similar), open ≈ closed, size flat.
- **Three walked-back metrics, each killed by a named confound:** LLM cleaning (hallucinates on
  short inputs), NN-distinctiveness/"voice" (entangles packaging, determinism, and style),
  embedding uniqueness (ernie ranked #1 on pure verbosity — forced to one word it fell to dead
  last, the inversion that validated the surprisal metric).
- **Temperature cannot be held constant across a modern fleet.** temp=1.0 sent to all, but
  effective sampling varies ~6× (Claude/Gemini near-greedy, dup-rate 0.44–0.67; open/older models
  honestly sample). Every cross-model convergence study carries this uncontrolled confound.

## Method (as run)

- **9 bare-imperative prompts**, single-turn, no system prompt, no length clamp —
  [`spec/stimulus.json`](spec/stimulus.json). Strong-prior: joke, animal, fruit, country, number.
  Diffuse: haiku, poem, metaphor, word.
- **25 models** on a family × generation × size grid — [`spec/models.json`](spec/models.json).
  Every cut is a *filter* on the one run, never a re-run.
- **`runs: 3`** per (model, prompt) — the within-model self-consistency floor.
- **Offline analysis** ([`analyze.py`](analyze.py)): embed replies (OpenAI
  `text-embedding-3-small`, pluggable), per-prompt model×model cosine matrix, cross-pairs vs
  cross-centroid means, per-model uniqueness → [`analysis.json`](analysis.json).

## Run / rebuild

```bash
source ../../.venv/bin/activate      # repo venv; OPENROUTER_API_KEY in ../../.env

# regenerate transcripts (models.txt mirrors spec/models.json)
python ../../harness/run.py --study . --runs 3 $(cat spec/models.txt)

# eyeball the transcripts (reused generic renderer)
python ../../harness/render.py --study . claude-opus-4.8

# analyze + rebuild the views
python analyze.py                    # transcripts -> analysis.json
python views/build.py && open views/index.html
```

`run.py` merges per model and exits 0 even when a cell fails (the error lands in the file) — read
the output, not the exit code. Known partial failure: minimax-m1 (12 failed cells) — excluded from
strong claims.

## Status

Complete as a pilot; superseded by [`consensus`](../consensus/) for the uniqueness question. The
committed [views](views/index.html) show only what survived cleanly: the raw answers, side by side,
no scores. Honest limits (N=9 prompts, cosine has no fixed zero without a per-prompt baseline,
embedding-model-as-lens, temperature confound) are in [PLAN.md](PLAN.md#topline-characterization-not-measurement--small-n-one-day-wide-cis)
and [OBSERVATIONS.md](OBSERVATIONS.md#open-methodology-issues-block-conclusions).
