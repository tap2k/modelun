# Archive — the analysis history

This folder preserves the work the current study was built on, so the full history of analyses is
recoverable and any thread can be picked up later. **Kept here: anything that served as the basis of
an analysis or synthesis. Discarded: pure intermediates** (raw run transcripts, scratch judge labels,
regenerable figures) — those are distilled into committed artifacts or recoverable from a tag.

## Two studies

**v4.1 — the bottom-up study** *(superseded, preserved here)*
Read 38 models on a 9-scene instrument, let character emerge, three independent vendor-models read
every transcript blind, and findings counted only when ≥2 readers agreed (≈660 quotes string-verified,
zero fabrications). Produced a 38-model differential synthesis, a bestiary essay, per-model cards, and
a catchphrase cohort report. It was noisy bottom-up, so it was reframed top-down into v5 — but its
*basis* (the cross-reader findings) and its outputs are kept here.

**v5 — the current study** *(live, on `main`)*
6 discriminating scenes, three dimensions of conduct (TONGUE / HANDS / HEART), three vendor house
styles (Therapist / Coach / Apologist). JSON data model, a binary+graded marker layer scored by a
single judge. See [`../docs/houses.md`](../docs/houses.md), [`../data/benchmark/`](../data/benchmark/),
and [`../registers.json`](../registers.json).

## What's in here (v4.1 basis + outputs)

| Path | What | Why kept |
|---|---|---|
| `v4.1/synthesis.md` | The 38-model differential synthesis (the portraits) | The analysis |
| `v4.1/essay.md` | The bestiary essay | The analysis |
| `v4.1/cross-check-method.md` | The 3-reader bias-guard method writeup | Documents *how* findings were validated |
| `v4.1/catchphrases.md` | Catchphrase cohort report (verbal-tic signatures) | A finished analysis |
| `v4.1/cross-check/<reader>/<model>.json` | Each of 3 readers' structured findings, ×38 models | **The basis of `synthesis.md`** — the raw the synthesis was distilled from |
| `v4.1/cross-check/essay-drafts/`, `synth-drafts/` | Per-reader prose/structured drafts | The independent reads that got merged |
| `v4.1/cards/<model>.md` | 38 per-model cards (measured tics + read) | Analysis output |

## Git tags — full snapshots

- **`v4.1-archive`** — the whole repo just before the v5 prune: all v4.1 docs (plan, onepager,
  scripts) **and tooling** (`run_reads.py`, `make_cards.py`, `catchphrases.py`, `blind_*.py`,
  read prompts). To re-run any v4.1 analysis: `git checkout v4.1-archive`.
- **`satya-catchphrases`** — the divergent v4.1 line from `satya.local`: the two catchphrase commits
  (the cohort report + the improved extractor) **and the bestiary `site/`** (14 files). These commits
  exist on no other machine; this tag is their only backup. `git checkout satya-catchphrases`.

## Picking up the markers thread

The v5 marker layer is the live frontier. **Current state:** single judge `google/gemini-2.5-flash`,
adjudicated to [`../data/benchmark/markers.json`](../data/benchmark/markers.json) (raw labels under the
gitignored `markers/`). The single judge is the main stated limit in `houses.md`.

**The v4.1 3-reader cross-check is the template for hardening it — and the v5 pipeline already
supports it.** `adjudicate_markers.py` takes the **majority vote across every judge dir** and flags
self-family cells; it was built for a panel, just run with one judge so far. To harden to a panel:

```bash
python scout/run_markers.py --judge openai/gpt-5.4          # add a 2nd judge (~38 calls)
python scout/run_markers.py --judge anthropic/claude-opus-4.8  # add a 3rd (~38 calls)
python scout/adjudicate_markers.py    # majority across all 3 judges + self-family exclusion -> markers.json
python scout/plot_markers.py          # regenerate reads/markers_grid.png
# then update docs/houses.md "Honest limits": single judge -> 3-judge panel
```

Marker definitions live in [`../scout/markers.py`](../scout/markers.py); the instrument (active scenes)
in [`../registers.json`](../registers.json). The benchmark retains all 11 scenes ever collected; to
revive an archived scene, add its marker to `markers.py` and the scene to `registers.json`.

## Discarded (intermediate — not committed)

Raw `runs/` transcripts (distilled into `data/benchmark/*.json` and the `v4.1-archive` tag's `.md`),
the clamp/p4fix run+card variants, scratch `markers/` labels, and regenerable grid PNGs. They remain
on disk on `satya.local` and locally (gitignored) if ever needed, but they are not the basis of any
finding that isn't already preserved above.
