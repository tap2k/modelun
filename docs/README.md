# docs — index

The pile, mapped. Two eras: **v4.1** (the founding 38-model bestiary, frozen + cited) and **v5.0**
(the disposition tilt — retired the dead scenes, added the house-style probes). Comparability is
per-scene, so the two eras share a core and merge (see the MANIFEST).

## Start here (findings — readable)
- [`essay.md`](essay.md) — **v4.1 published findings.** The bestiary grouped by behavior (Mind-Readers,
  Cheerleaders/Coaches, Folders, Forgers, …). Every quote verbatim from `data/benchmark/`.
- [`houses.md`](houses.md) — **v5.0 findings.** The three house styles read down the labs —
  **Therapist (Anthropic) / Coach (OpenAI) / Apologist (Google)** — the capability-vs-disposition
  two-axis result, the attractor, the apology near-null.
- [`onepager.md`](onepager.md) — the pitch / what-it-is in one page.

## The instrument
- [`../registers.json`](../registers.json) — **v5.0, source of truth** (10 scenes, the clamp).
- [`../data/benchmark/registers-v4.1.json`](../data/benchmark/registers-v4.1.json) — archived v4.1
  stimulus-of-record (the cohort it generated lives beside it).
- [`plan.md`](plan.md) — design rationale (registers, "the shape is the trait", breadth-over-depth).
- [`scripts.md`](scripts.md) — human mirror of the scripts *(note: written at v4.0; registers.json is
  authoritative)*.

## Method / audit trail (the working pile)
- [`method/markers.md`](method/markers.md) — **the marker layer spec.** 6 binary (capability/floor) +
  4 graded (disposition) markers; the multi-judge protocol; per-scene conventions. Results land in
  `data/benchmark/markers.json` and synthesis-v5 §4.
- [`method/synthesis.md`](method/synthesis.md) — **v4.1 audit trail** (the 38 differential portraits,
  family reads, per-scene yield, limits).
- [`method/synthesis-v5.md`](method/synthesis-v5.md) — **v5.0 audit trail, WORKING.** The two axes,
  the houses, the discrimination numbers, the apology near-null, the v5 instrument changes, and the
  **[PENDING]** run log (pilot → full roster → panel). The new synthesis fills in here.
- [`method/synthesis-prompt.md`](method/synthesis-prompt.md) — reproducible brief (how the synthesis
  is produced: fan-out readers → differential → lead pass).
- [`method/cross-check.md`](method/cross-check.md) — the 3-reader bias guard (independent vendors,
  quote integrity).

## Tooling (not docs, but where the doc data comes from)
`scout/` — `atlas_scout.py` (runner), `run_markers.py` + `adjudicate_markers.py` + `markers.py`
(marker layer), `plot_markers.py` (the grid), `run_reads.py` (multi-reader synthesis).

---
*Where new things go:* v5 findings → `houses.md`; v5 working notes/numbers/run-log →
`method/synthesis-v5.md`; instrument changes → `registers.json` + the MANIFEST lineage. Quotes stay
verbatim and verifiable against `data/benchmark/` (+ `runs/<tag>/` for unpromoted runs).
