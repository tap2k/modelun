# AGENTS.md — notes for coding agents

Rules and tripwires that aren't obvious from the code. Read before changing anything.
For *what the project is* and *how to run it*, see [README.md](README.md) and [docs/plan.md](docs/plan.md).

## Stage discipline (the big one)
This is a **read-by-eye scout**, not a measurement pipeline. The method is breadth
(more registers, more models) read from transcripts — not depth, scoring, or aggregation.
- The next move is almost always **add registers or add models**, NOT build more analysis tooling.
- Resist standing up rubrics, markers, or scoring layers. `docs/plan.md` defers all of that on
  purpose. If you think the project needs it, say so and ask — don't just build it.

## The frozen stimulus is sacred
`registers.json` is byte-identical input sent to every model — that's what makes columns comparable.
- Do **not** edit scene turns, seeds, or the `system_prompt` between runs you intend to compare.
- Any change to the stimulus (including the clamp text) **must bump `script_version`**. Clamped and
  unclamped, v4.0 and v4.1, are NOT comparable — keep them in separate run dirs.
- The `system_prompt` "clamp" is content added to the stimulus, not a config knob. Treat it as part
  of the frozen input: version it, and it's stamped into every transcript header.

## The judge must not be a subject (self-preference leak)
`make_cards.py --judge <slug>` must NOT be a model family under test. With Claude/GPT/Gemini as
subjects, the judge can't be any of them. The tool warns on vendor collision but won't block — heed it.
- Judge reads are **drafts**, cited and marked UNVERIFIED. The human read overrides them.
- The anti-hallucination prompt lowers fabricated quotes but does NOT guarantee against them
  (it happened once). If quotes need to be airtight, add a string-check verification pass.

## Provenance & secrets
- Every run is a **dated specimen**: model version + date + script_version + clamp, all stamped.
- `runs/` and `cards/` are generated output and **gitignored**. Never commit transcripts, cards, or `.env`.
- Before any push, confirm `.env` is not staged. A leaked `OPENROUTER_API_KEY` is the one unrecoverable mistake.

## Honest limits to respect
- Current data is small-N, read-by-eye, and mostly on **mini/flash tiers** — characterizations, not findings.
  Don't write results into the README or docs as established. Reads stay labeled as reads.
- Between-run wander matters: a model with low run-to-run overlap (see the card's wander line) has a
  shakier card. More runs, not more confidence.

## Gotchas
- Commit messages: use `git commit -F <file>`. Heredocs with apostrophes (`model's`, `don't`) break the shell.
- The scout exits 0 even if every cell failed (failures are written into the file). Check the output, not just the exit code.
- `--judge` is required and has no default, on purpose. Don't add one.
