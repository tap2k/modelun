# convergence — do frontier models give the same answer?

Study #3 on the [modelun harness](../../README.md). Tests whether, as frontier models increasingly share
training data and RLHF conventions, their answers **converge** — and whether that convergence is stronger
for pattern-laden queries ("tell me a joke") and grows across generations of a family.

Like [`language`](../language/), this study is **runner + renderer with the grading slot left open** — but
it adds one offline analysis step (`analyze.py`) that embeds every reply and measures cross-model answer
similarity. No LLM judge in the pilot; that's the deferred cross-check.

**The design, the confounds, and the reasoning are all in [`PLAN.md`](PLAN.md).** This README is the
operational summary. Read the plan before changing the prompt set or model grid — several non-obvious
decisions (no waffle, prior-strength not length, size ⊥ generation) are load-bearing.

## The claim, precisely

Convergence is not an absolute number — it's a **contrast**. Two contrasts, both read off one per-prompt
model×model cosine-similarity matrix:

- **Axis A — prior-strength × tier.** Do models converge *more* on strong-prior prompts (name an animal →
  lion) than diffuse ones (write a haiku)? And do *frontier* models converge harder than *open* ones?
- **Axis B — generation-time × family.** Do families drift *toward each other* over generational time?
  Split into **B1** (step generations, hold size) and **B2** (step size, hold generation — the control
  that subtracts the size effect, since size and generation are separate axes).

## Method

- **9 bare-imperative prompts**, single-turn, **no system prompt, no length clamp** —
  [`spec/stimulus.json`](spec/stimulus.json). Every prompt is unhedgeable and pattern-laden so the model
  commits to a short answer; hedging breaks embedding similarity *and* is an RLHF-converged register (a
  directional confound). Strong-prior: joke, animal, fruit, country, number. Diffuse: haiku, poem,
  metaphor, word.
- **17 models** on a family × generation × size grid — [`spec/models.json`](spec/models.json). Three
  closed lineages (GPT, Claude, Gemini) carry generational + size depth; an open arm (Llama×2, Qwen,
  Mixtral) carries breadth. Every cut is a *filter* on the one run, never a re-run.
- **`runs: 3`** per (model, prompt) — gives the within-model self-consistency floor; cross-model
  convergence is only interesting as it rises toward that floor.
- **Offline** (`analyze.py`, to be written): embed replies (OpenAI `text-embedding-3-small`, pluggable),
  build the per-prompt matrix, emit cross-/within-model means → `analysis.json` → two plots in `views/`.

## Run

```bash
source ../../.venv/bin/activate      # repo venv; OPENROUTER_API_KEY in ../../.env

# generate: all 17 models, 3 runs each, all 9 prompts
python ../../harness/run.py --study . --runs 3 $(cat spec/models.txt)

# eyeball the transcripts (reused generic renderer)
python ../../harness/render.py --study . claude-opus-4.8

# analyze + view (once analyze.py + views/ exist)
python analyze.py            # transcripts -> analysis.json
python views/build.py && open views/index.html
```

`run.py` merges per model and exits 0 even when a cell fails (the error lands in the file) — read the
output, not the exit code. Transcripts are working output; per the harness ethos they stay gitignored
until a run is promoted to the committed basis.

## Status

Pilot, not yet run. `spec/` is frozen; `analyze.py` and `views/` are the remaining new code. Honest
limits (small N, cosine noise, embedding-model-as-lens, prior-strength observed-not-controlled, no LLM
judge yet) are enumerated in [`PLAN.md`](PLAN.md#honest-limits-respect-the-agentsmd-ethos).
