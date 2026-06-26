# AGENTS.md — notes for coding agents

Rules and tripwires that aren't obvious from the code. For what the project is and how to run it, see
[README.md](README.md).

## Layout: harness vs. study
The repo splits into a domain-neutral **`harness/`** (the tool — runner, judge, adjudicator, the
`viewer/core.js` renderer) and **`studies/<name>/`** (the conduct atlas is `studies/conduct/`). The
harness holds no conduct semantics; a study supplies `spec/` (`stimulus.json` + `codebook.py`),
`data/`, `views/`, `docs/`. Architecture and contracts: [`docs/harness.md`](docs/harness.md). Harness
scripts take `--study <dir>` and resolve paths via `harness/study.py` (+ the study's
`spec/paths.json`, which lets conduct keep its historical `data/benchmark` and `markers/` names).

## The frozen stimulus is sacred
`studies/conduct/spec/stimulus.json` is byte-identical input sent to every model — that's what makes
columns comparable.
- Do **not** edit scene turns or the `system_prompt` clamp between runs you intend to compare.
- Any change to the stimulus (including the clamp) **must bump `script_version`**, and the old and
  new versions are not comparable — keep them in separate run dirs.
- The clamp is content added to the stimulus, not a config knob: version it; it's stamped into every
  transcript header.

## Markers annotate, they don't replace
- Every marker value cites a **verbatim** trigger quote that must be a real substring of the
  transcript. After scoring, string-check it; an unverifiable claim is dropped (it has happened).
- The judge is `google/gemini-2.5-flash`, which is **itself a subject**. Its calls on the google
  family (gemini / gemma) are self-judged — flag those cells, don't silently trust or drop them.

## History & archive
- The full analysis history (the bottom-up v4.1 study, its 3-reader cross-check basis, the bestiary
  essay, the per-model cards, the catchphrase report) is preserved under
  [`archive/`](archive/) — see [`archive/README.md`](archive/README.md) for the map and how to
  recreate any thread. No tags or side branches: everything (analyses, basis, tooling, and the
  scene-run library in `studies/conduct/data/benchmark/`) is on `main` and pushed. The pre-prune v4.1 repo remains
  reachable in history at commit `a36cf84` (`git show a36cf84:<path>`).
- **Picking up the markers thread**: the live marker layer is single-judge; the v5 pipeline already
  supports a multi-judge panel (`harness/adjudicate.py` does majority + self-family exclusion). The
  exact recipe to harden it is in `archive/README.md` § *Picking up the markers thread*.
- Principle for what to commit: **keep anything that served as the basis of an analysis/synthesis;
  intermediates (raw runs, scratch labels, regenerable figures) stay gitignored**.

## Provenance & secrets
- Every run is a dated specimen: model version + date + script_version + clamp, all stamped.
- `runs/`, `cards/` (root) and per-study `reads/`, `markers/`, `views/data.js` are generated working output and **gitignored** (the
  curated basis is committed under `archive/`). The published data lives in `studies/conduct/data/benchmark/`. Never
  commit transcripts-in-progress, scratch marker runs, or `.env`.
- Before any push, confirm `.env` is not staged. A leaked `OPENROUTER_API_KEY` is the one
  unrecoverable mistake.

## Honest limits to respect
- Small N, dated specimens. The conduct study's *live* marker layer is single-judge (the harness
  supports a multi-judge panel; conduct just hasn't run one). Characterizations, not measurements —
  don't write reads into docs as established. The frontier-lab "house styles" are a working lens, not a
  universal law.

## Gotchas
- `harness/run.py` exits 0 even if cells fail (failures are written into the file). Check the output,
  not just the exit code.
- Commit messages: use `git commit -F <file>`. Heredocs with apostrophes (`model's`, `don't`) break
  the shell.
