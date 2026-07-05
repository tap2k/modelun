# The bottom-up layer — the conduct study's first methodology

The conduct study has two methodology layers over the same 38-model transcript library. This directory
is the **earlier bottom-up layer**; the current **top-down** layer is the rest of `studies/conduct/`.
It is not dead history — the conduct site still renders this layer's cards, cross-check reads, and
catchphrase report ([`../views/build.py`](../views/build.py)) alongside the top-down markers.

**Kept here: anything that served as the basis of an analysis or synthesis. Discarded: pure
intermediates** (raw run transcripts, scratch judge labels, regenerable figures) — those are distilled
into committed artifacts or recoverable from history.

## The two layers

**Bottom-up — this layer** *(the earlier methodology, still rendered)*
Inductive. Read 38 models on a 9-scene open instrument, let character emerge, three independent
vendor-models read every transcript blind, and findings counted only when ≥2 readers agreed (≈660
quotes string-verified, zero fabrications). Produced a 38-model differential synthesis, a bestiary
essay, per-model cards, and a catchphrase cohort report. Its strength is **panel validation** (the
cross-check); it was noisy, so it was reframed top-down — but its *basis* (the cross-reader findings)
and its outputs are kept here.

**Top-down — the live layer** *(the rest of `studies/conduct/`)*
Deductive. 6 discriminating scenes, three predeclared dimensions of conduct (TONGUE / HANDS / HEART),
three vendor house styles (Therapist / Coach / Apologist). JSON data model, a binary+graded marker
layer scored by a single judge. See [`../docs/houses.md`](../docs/houses.md),
[`../data/benchmark/`](../data/benchmark/), and [`../spec/stimulus.json`](../spec/stimulus.json).

## What's in here (bottom-up basis + outputs)

| Path | What | Why kept |
|---|---|---|
| `synthesis.md` | The 38-model differential synthesis (the portraits) | The analysis |
| `essay.md` | The bestiary essay | The analysis |
| `cross-check-method.md` | The 3-reader bias-guard method writeup | Documents *how* findings were validated |
| `catchphrases.md` | Catchphrase cohort report (verbal-tic signatures) | A finished analysis |
| `cross-check/<reader>/<model>.json` | Each of 3 readers' structured findings, ×38 models | **The basis of `synthesis.md`** — the raw the synthesis was distilled from |
| `cross-check/essay-drafts/`, `synth-drafts/` | Per-reader prose/structured drafts | The independent reads that got merged |
| `cards/<model>.md` | 38 per-model cards (measured tics + read) | Analysis output |
| `tools/` | The bottom-up methodology scripts: 3-reader `run_reads.py` + prompts, `make_cards.py`, `catchphrases.py`, blind variants | **Re-run any bottom-up analysis straight from `main`** — no tag checkout needed |

So everything you need to read the analyses, see what they were built on, and re-run the methodology
lives on `main`. The top-down marker tooling is the generic [`../../../harness/`](../../../harness/);
the bottom-up reading tooling is in `tools/` above.

## One branch, no tags

Deliberately no tags or side branches — the analyses, their basis, the tooling, and the scene-run
library all live on `main` (and are pushed to the remote). What used to sit only in tags is handled:
- The bottom-up reading tooling was folded onto `main` → `tools/`.
- The **pre-prune repo** (the old `plan.md`/`onepager.md`/`scripts.md`/method docs + `build_site`
  scripts) is still reachable through `main`'s history at commit **`a36cf84`** — recover any file with
  `git show a36cf84:<path>`.
- The only thing dropped entirely is the obsolete bestiary **website** (`site/`, built from the
  old 9-scene data with pre-houses framing) — not data, not analysis.

## Picking up the markers thread

The top-down marker layer is the live frontier. **Current state:** single judge
`google/gemini-2.5-flash`, adjudicated to
[`../data/benchmark/markers.json`](../data/benchmark/markers.json) (raw labels under the gitignored
`labels/`). The single judge is the main stated limit in
[`../docs/houses.md`](../docs/houses.md) § *Honest limits*.

**This layer's 3-reader cross-check is the template for hardening it — and the top-down pipeline already
supports it.** [`../../../harness/adjudicate.py`](../../../harness/adjudicate.py) takes the **majority
vote across every labeler dir** and flags self-family cells; it was built for a panel, just run with one
judge so far. To harden to a panel:

```bash
python harness/judge.py --study studies/conduct --judge openai/gpt-5.4          # add a 2nd judge (~38 calls)
python harness/judge.py --study studies/conduct --judge anthropic/claude-opus-4.8  # add a 3rd (~38 calls)
python harness/adjudicate.py --study studies/conduct   # majority across all judges + self-family exclusion -> markers.json
python studies/conduct/views/plot.py                   # regenerate reads/markers_grid.png
# then update ../docs/houses.md "Honest limits": single judge -> multi-judge panel
```

Marker definitions live in [`../spec/codebook.py`](../spec/codebook.py); the instrument (active scenes)
in [`../spec/stimulus.json`](../spec/stimulus.json). The benchmark retains all 11 scenes ever collected;
to revive a not-scored scene, add its marker to `codebook.py` and the scene to `stimulus.json`.

## Discarded (intermediate — not committed)

Raw `runs/` transcripts (their content is preserved distilled — the active+not-scored scenes in
`../data/benchmark/*.json`, and the published 9-scene `.md` at commit `a36cf84` in history), the
clamp/p4fix run+card *experiment variants*, scratch label dirs, and regenerable grid PNGs. These were
intermediate; they've been cleaned from both machines. None is the basis of a finding not already
preserved above.
