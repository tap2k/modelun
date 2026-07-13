# modelun

A small, buildless harness for **labeling and viewing model transcripts**. Send an arbitrary
multi-turn script to arbitrary models, grade the transcripts with an LLM judge *and* a human judge
(voted together, every label grounded in a verbatim quote), and browse them in a no-deps local viewer.

The harness is domain-neutral. A **study** points it at a question by supplying a `{stimulus, codebook}`
and its own views. The first study is the **conduct atlas** — how language models behave under
multi-turn pressure — in [`studies/conduct/`](studies/conduct/).

## The two things this does that adjacent tools don't

- **A human and an LLM are the same labeler.** Judges are namespaced; a human grader and an LLM judge
  write the same label shape and are *voted together* in one tally. Collaboration is conflict-free with
  no backend — each labeler writes their own files, git is the merge.
- **Every verdict is mechanically grounded.** A label must cite a verbatim substring of the reply it
  judges; the adjudicator string-verifies it and drops what doesn't check out.

## Pipeline

```
spec.stimulus ─► run.py ────────► transcripts/<model>.json        a model's reply-arcs
+ spec.codebook ─► judge.py ────► labels/<labeler>/<model>.json   one judge's verdicts (LLM or human)
+ transcripts ─► adjudicate.py ─► store.json                      quote-verified, voted
+ store ─► viewer/core.js ──────► transcript view + compare
```

The runner is scripted (identical turns to every model, so columns compare); failures are written into
the file, not raised. The renderer is *dumb* — it draws transcripts and a side-by-side compare and
knows nothing about any study; a study layers its own views (grids, plots, synthesis) on top.

Full architecture and contracts: [`docs/harness.md`](docs/harness.md).

## Layout

| Path | What it is |
|---|---|
| [`harness/`](harness/) | The tool. `run.py`, `judge.py`, `adjudicate.py`, `render.py`, `study.py` (path resolution), `viewer/core.js` (the renderer). No study semantics. |
| [`studies/conduct/`](studies/conduct/) | The conduct atlas — study #1. See its [README](studies/conduct/README.md). |
| [`docs/harness.md`](docs/harness.md) | The core: contracts, the judging kernel, repo layout, interchange. |
| [`studies/conduct/bottom-up/`](studies/conduct/bottom-up/) | The conduct study's earlier bottom-up methodology layer (emergent bestiary, 3-reader cross-check basis, per-model cards) — still rendered by the conduct site. See its [README](studies/conduct/bottom-up/README.md). |

A study is a directory the harness resolves via `--study`:

```
studies/<name>/
  spec/stimulus.json     the frozen multi-turn script
  spec/codebook.py        the criteria (binary / graded / scale)
  spec/paths.json         optional: override transcripts/labels/store dir names
  transcripts/<model>.json    Contract A — runner output
  labels/<labeler>/<model>.json   Contract B — judge output
  store.json              adjudicator output
  views/                  bespoke views built on harness/viewer/core.js
```

## Run

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # OPENROUTER_API_KEY

# run a study's scenes against models, score them, adjudicate:
python harness/run.py        --study studies/conduct anthropic/claude-opus-4.8 openai/gpt-5.4 --runs 2
python harness/judge.py      --study studies/conduct --judge google/gemini-2.5-flash
python harness/adjudicate.py --study studies/conduct

# read a transcript by eye, or build + open the review site:
python harness/render.py     --study studies/conduct claude-opus-4.8
python studies/conduct/views/build.py && open studies/conduct/views/index.html
```

Every harness script takes `--study <dir>` (default: cwd) and resolves the study's files through
`harness/study.py`. `run.py` exits 0 even when cells fail (failures land in the file) — read the
output, not just the exit code.

## Starting a new study

**[`studies/conduct/`](studies/conduct/) is the worked example** — copy its shape. Make
`studies/<name>/`, write `spec/stimulus.json` (scenes × user turns) and `spec/codebook.py` (criteria),
then run the same four commands against `--study studies/<name>`. The viewer and the whole judging
kernel come for free; add `views/` only when you want more than transcript + compare. A study graduates
to its own repo (depending on a `harness/` checkout) when it needs different collaborators than the
harness.
