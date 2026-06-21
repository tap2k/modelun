# AGENTS.md — notes for coding agents

Rules and tripwires that aren't obvious from the code. For what the project is and how to run it, see
[README.md](README.md).

## The frozen stimulus is sacred
`registers.json` is byte-identical input sent to every model — that's what makes columns comparable.
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

## Provenance & secrets
- Every run is a dated specimen: model version + date + script_version + clamp, all stamped.
- `runs/` and `markers/` are generated working output and **gitignored**. The published data lives in
  `data/benchmark/`. Never commit transcripts-in-progress, scratch marker runs, or `.env`.
- Before any push, confirm `.env` is not staged. A leaked `OPENROUTER_API_KEY` is the one
  unrecoverable mistake.

## Honest limits to respect
- Small N, dated specimens, single judge. Characterizations, not measurements — don't write reads
  into docs as established. The frontier-lab "house styles" are a working lens, not a universal law.

## Gotchas
- The scout exits 0 even if cells fail (failures are written into the file). Check the output, not
  just the exit code.
- Commit messages: use `git commit -F <file>`. Heredocs with apostrophes (`model's`, `don't`) break
  the shell.
