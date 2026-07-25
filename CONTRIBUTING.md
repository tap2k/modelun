# Contributing a study

The harness is domain-neutral and studies are self-contained directories — you can add your
own. A study PR adds `studies/<name>/` and touches nothing outside it. Use
[`studies/consensus/`](studies/consensus/) as the template: it is the minimal shape (single-turn
stimulus, no judge, fully mechanical analysis), and it shipped as
[a paper](https://arxiv.org/abs/2607.12796) without needing anything the template lacks.

A study is three parts:

## 1. Config (`spec/`)

- `spec/stimulus.json` — the script sent to every model, **frozen before data collection**.
  Identical turns to every model is what makes columns comparable; if the stimulus changes,
  that's a new study (or a new versioned run), not an edit.
- `spec/models.json` — the panel, with per-model metadata (`family`, `origin`, `open`) so
  analyses can group without guessing.

## 2. Archive (`transcripts/`)

- Raw runner output, one `Contract A` JSON per model (see
  [`docs/harness.md`](docs/harness.md)), committed to the repo. The archive is the point:
  models get deprecated — several of the most interesting ones already can't be re-measured —
  and a committed transcript is the only version of your data that survives that. Failures are
  recorded in the files, not raised.

## 3. Analysis

- Prefer **mechanical** analysis (recomputable from the transcripts with stdlib + numpy, no
  model in the loop): `analyze.py` reads `transcripts/`, writes `analysis.json`, prints the
  scorecard. If your construct needs grading, use the harness's codebook / judge / adjudicate
  contracts instead of ad-hoc LLM calls, so labels stay quote-grounded and re-votable.
- Robustness probes are ordinary scripts (`probe_*.py` writing `probes/*.json`) — cheap,
  zero-new-calls checks that your finding isn't an artifact of the panel, the smoothing, the
  prompt wording, or the sampling temperature.

## Norms

- **README.md** states the question, the metric, and the known limits — including what the
  instrument does *not* measure.
- **OBSERVATIONS.md** is the dated working log: findings, dead ends, and reversals, kept
  honestly enough that a reader can reconstruct why the analysis looks the way it does.
- Every number in any write-up must trace to a committed script over the frozen transcripts —
  nothing hand-entered from working notes.
- New dependencies go in the root `requirements.txt`; keep them minimal.

Run your study the same way the existing ones run:

```bash
source .venv/bin/activate    # OPENROUTER_API_KEY in .env
cat studies/<name>/spec/models.txt | xargs -P 8 -I{} \
  python harness/run.py --study studies/<name> --runs 4 {}
python studies/<name>/analyze.py
```
