# data/coding

The conduct study's coding record. Flat files are the coders' labels, written by the coding
page (`views/code.html` via `harness/viewer/code_server.py`) or by the LLM coder scripts; they
stay here because the scripts read and append them by name. Method: `docs/inductive-coding.md`.

## Human labels
`CODER-LOG.md` — dated events that touch a human pass (sittings, mid-pass messages), for the order splits.

### Tapan
- `directed.Tap.jsonl` — held/departed on the four binary markers, 304 arcs (2026-09-14); three soft-cave rows recoded under the v2 rule with the v1 verdict kept.
- `open_codes.Tap.jsonl` — open coding of the forty-arc sample, 97 codes; `open_codes.Tap-anchor.jsonl` — the anchor recode of the first five.
- `manner_v2.Tap.jsonl` — directed manner pass on the held-out fifty under codebook v2; rows flagged `adjudicated` were added in the 2026-09-15 adjudication with the coders' quote and the reason.
- `trace.Tap.jsonl` — the trace pilot (other session).

## LLM coders
- `open_codes.llm-*.jsonl` — three open coders on the forty (`harness/open_code.py`).
- `relabel_v0.llm-*.jsonl` — the marker rules per arc, six coders (the confound check).
- `relabel_v1.llm-*.jsonl`, `relabel_v2.llm-*.jsonl` — six coders applying codebook v1 / v2 to every arc incl. specimens (`harness/relabel.py`). v2 rows carry the current code names after the 2026-09-15 renames, split, retirement, and fold.
- `second-judges-2026-09-14/` — raw marker-judge labels from gpt-5.4-mini and claude-haiku-4.5 (the working `markers/` dir is gitignored).
- `COVERAGE-v1.jsonl`, `COVERAGE-v2-draft.jsonl` — every LLM open code mapped to a codebook code or NONE (`harness/coverage_check.py`).

## codebook/
- `CODEBOOK-v0-markers-2026-09-14.md` — the a-priori marker rules restated per arc (confound check).
- `CODEBOOK-v1-2026-09-14.md` — version one, decided code by code 2026-09-14.
- `CODEBOOK-v2-2026-09-14.md` — version two, the author's file with evidence and history; the coders read a rendering of sections A to D with evidence stripped (`relabel.codebook_text`).
- `CODER-BRIEF-2026-09-15.md` — what the second coder is told; `CODER-SHEET-v2-2026-09-15.md` — the second human's sheet; `CODES-v2-SIMPLE-2026-09-15.md` — the one-page list (code, phrase, quote).
- `CODEBOOK-v3-2026-09-17.md` — not reported: a tie-break pass that raised machine consistency without moving agreement with any cold human reading; v2 is the instrument. Kept only because the out-of-scene preregistration's amendment 3 refers to it.
- `HELDOUT-50.txt` — the fifty directed arcs (seed 2026) for judge accuracy and the second human.

## results/
Dated, never edited after the day: `JUDGE-ACCURACY-2026-09-14.md` (judges vs the human, three judges), `COMPARE-2026-09-14.txt` and `RECONCILIATION-2026-09-14.md` (open coders vs the human), `RELABEL-v1-2026-09-14.md` (the relabel cycle, sections 1 to 12), `MANNER-MATRIX-*.md` and `HOUSE-PROFILES-*.md` (v1 at 43 models; v2 at 60 on the three common scenes), `MANNER-ACCURACY-2026-09-15.txt` and `ADJUDICATION-v2-2026-09-15.*` (the human manner pass vs the coders, and the adjudication).
- `HOUSES-OUT-OF-SCENE-2026-09-17.md` — the exploratory out-of-scene house test on v2: three houses reproduce, Google and Grok untestable or not carried over; relabel files tagged `v2x`.
