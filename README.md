# modelun — the Personality Atlas (scout stage)

A cheap way to *look* at how different language models actually conduct themselves
in multi-turn conversation — under pressure, play, and vulnerability — by reading
real transcripts rather than personality surveys.

**Where this is right now:** step zero. We have an instrument and a hunch, no
specimen yet. The whole current job is to generate a handful of transcripts, read
them side by side, and find out whether anything pulls apart. Everything in
`docs/` past the motivation is *where this could go if it works* — not a result.

## Layout

- `registers.json` — the frozen scripts (the instrument; source of truth)
- `scout/atlas_scout.py` — the runner: plays each scene a few times per model, dumps readable markdown
- `docs/` — the writeup: [onepager](docs/onepager.md), [plan](docs/plan.md), [scripts](docs/scripts.md)
- `runs/` — generated transcripts land here (gitignored — they're dated output, not source)

## Run a scout

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then put your real OpenRouter key in it — the script loads it automatically

# start tiny — two scenes, a few models, read them
python scout/atlas_scout.py registers.json \
  anthropic/claude-sonnet-4.6 openai/gpt-5.4-mini google/gemini-3.5-flash \
  --runs 2 --out runs
```

Then open the `runs/scout_*.md` files and read them. The only question that
matters yet: **side by side, does anything pull apart?**
