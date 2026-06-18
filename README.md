# modelun — the Personality Atlas (scout stage)

A cheap way to *look* at how different language models actually conduct themselves
in multi-turn conversation — under pressure, play, and vulnerability — by reading
real transcripts rather than personality surveys.

The method: a fixed 4-panel script per register, identical for every model and
escalating regardless of the reply; run each a few times; read the transcripts
side by side. No judge, no scoring — the read is by eye.

`registers.json` is at `v4.1`, which includes an optional system-prompt **clamp**
(plain prose, no markdown, keep it short) to strip formatting/verbosity from the
read. The clamp is recorded in the JSON and stamped into every transcript header,
so clamped and unclamped runs stay distinguishable.

## Layout

- `registers.json` — the frozen scripts + the clamp (the instrument; source of truth)
- `scout/atlas_scout.py` — the runner: plays each scene a few times per model, dumps readable markdown
- `scout/catchphrases.py` — reading aid: surfaces each model's recurring phrases from a run
- `docs/` — the writeup: [onepager](docs/onepager.md), [plan](docs/plan.md), [scripts](docs/scripts.md)
- `runs/<tag>/` — transcripts land in a per-run subdir (gitignored — dated output, not source)

## Run a scout

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then put your real OpenRouter key in it — the script loads it automatically

python scout/atlas_scout.py registers.json \
  anthropic/claude-sonnet-4.6 openai/gpt-5.4-mini google/gemini-3.5-flash \
  --runs 2 --tag my-run
```

Each run writes `runs/<tag>/scout_<model>.md` (omit `--tag` to auto-stamp with a
timestamp; runs never overwrite each other). To read a model's tics afterward:

```bash
python scout/catchphrases.py runs/my-run
```

To run **without the clamp**, point the scout at a copy of `registers.json` with
the `system_prompt` field removed.

Then open the `runs/<tag>/scout_*.md` files and read them.
