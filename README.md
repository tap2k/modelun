# modelun — the Personality Atlas

**How do language models actually behave under pressure?** Not how they answer a personality
questionnaire — how they *conduct themselves* across a hard multi-turn conversation: when a user
insists 5×9 is 54 and turns nasty, begs for a forged sick note, or confides a dying parent and then
asks for a cheerful email. We sent the **identical** escalating script to 28 models, read the
transcripts with the names off, and kept only what distinguishes each one from the generic
assistant.

### → Read the findings: [**docs/essay.md**](docs/essay.md)

A short field guide — a bestiary grouped by behavior. A few models read your mind (name the move
you're making instead of answering it). Several tell you what you want to hear. A handful fold on a
fact a child knows the moment you raise your voice. Every characterization quotes a verbatim
transcript line.

---

## What's in here

| Path | What it is |
|---|---|
| [`docs/essay.md`](docs/essay.md) | **The published findings** — the bestiary + the scene appendix. Start here. |
| [`data/benchmark/`](data/benchmark/) | **The canonical dataset** — 28 models × 9 scenes × 2 runs, the transcripts the essay cites. Every quote is verifiable here. See [`MANIFEST.md`](data/benchmark/MANIFEST.md). |
| [`registers.json`](registers.json) | **The instrument** — the frozen 4-panel scripts + the v4.1 clamp. Source of truth; byte-identical input to every model. |
| [`docs/method/`](docs/method/) | **The audit trail** — the full [differential synthesis](docs/method/synthesis.md) behind the essay and the [reproducible method](docs/method/synthesis-prompt.md). |
| [`docs/plan.md`](docs/plan.md) | The design rationale — what each register tests and why. |
| [`scout/`](scout/) | The runner (`atlas_scout.py`) + reading aids. |
| `runs/`, `cards/` | Disposable working output (gitignored). The one published run lives in `data/`. |

## The method, in one paragraph

A fixed 4-panel script per scene, identical for every model and escalating regardless of the reply;
run each twice; read the transcripts side by side. **No judge, no scoring — the read is by eye.**
Then the differential step: *measure* what the majority of models do on each scene (the generic
RLHF-assistant script), and characterize each model only by where it **departs**. The v4.1 **clamp**
(plain prose, no markdown, keep it short) strips the formatting/verbosity confound so the read is
about conduct, not layout; it's recorded in `registers.json` and stamped into every transcript
header, so clamped and unclamped runs stay distinguishable.

These are **reads, not measurements**: N=2, by eye, dated specimens. Vivid enough to recognize, not
precise enough to rank.

## Reproduce or extend

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then put your real OpenRouter key in it — the script loads it automatically

python scout/atlas_scout.py registers.json \
  anthropic/claude-sonnet-4.6 openai/gpt-5.4-mini google/gemini-3.5-flash \
  --runs 2 --tag my-run
```

Each run writes `runs/<tag>/scout_<model>.md` (omit `--tag` to auto-stamp with a timestamp; runs
never overwrite each other). To read a model's tics afterward:

```bash
python scout/catchphrases.py runs/my-run
```

To run **without the clamp**, point the scout at a copy of `registers.json` with the `system_prompt`
field removed. To turn a run into a written synthesis, follow
[`docs/method/synthesis-prompt.md`](docs/method/synthesis-prompt.md).

> The 28-model run in `data/benchmark/` is the canonical specimen; new runs you generate land in
> `runs/` and stay out of git unless you promote one.
