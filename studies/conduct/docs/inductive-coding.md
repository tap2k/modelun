# Bottom-up inductive coding (the human layer)

A complement to the [marker layer](markers.md). Markers are a *deductive, a priori*
codebook — six pre-chosen tells on six pre-chosen scenes, defined up front and applied
top-down by an LLM judge. Inductive coding is the inverse: humans read transcripts cold,
attach open codes to whatever they actually notice, and let the categories *emerge*. The
codebook is the **output**, not the input.

## Motivation

The six markers can only ever measure what their designer already suspected. They are a
frame imposed on the data. Inductive coding is the only way to find out **what the marker
layer is blind to** — the phenomena that live outside the frame.

It audits the *design* of the codebook, not just the judge's *application* of it. Concretely,
once we have an emergent codebook we diff it against the imposed one and get three buckets:

- **Convergent** — emergent codes that reproduce a marker (validity for that marker).
- **Dead weight** — markers humans never independently coded (over-theorized).
- **Blind spots** — emergent codes with no marker (candidates for marker #7+, or new scenes).

This is **not** a scoring layer. It produces no model × marker grid. It sits *upstream* of
the markers — it tells us which markers deserve to exist, and gets refreshed when we reach
saturation.

## Decisions

**Unit of analysis: the scene-arc (conversation level), not the turn.** A "conversation" is
one scene's 4-turn arc, keyed `(model, scene, run)` — not the whole transcript (six unrelated
pressures would blend into mush). Turn-level capture is more citable but laborious, and most
of these phenomena are *trajectory* phenomena anyway (a "cave" is a U1→U4 delta). Coding the
arc as a unit keeps the trajectory in view for free at a fraction of the labor.

**Codebook-blind.** Coders do not see the six markers while coding. If the frame is visible,
inductive coding collapses into deductive coding wearing an inductive hat. Enforced
structurally: the coding UI never renders markers or judge output.

**One verbatim quote + one memo per code.** Each code = `{code label, verbatim quote, memo}`.
The quote keeps conversation-level codes grounded (the failure mode is global, unanchored
codes like "sycophantic" that can't become markers) and keeps them citable for the existing
quote-verification normalizer downstream.

**Independence over collaboration.** Collaborative open coding must be *independent* — coders
must not see each other's codes while working, or emergence is contaminated and the exercise
becomes consensus-seeking. The usual "collaborative backend" (a shared live document) is
therefore an anti-goal. Isolation is the design, not a limitation.

**No backend; git is the collaboration layer.** State belongs in repo files, reviewable in
git. Each coder writes their own namespaced file; merging coders is the union of files, with
zero merge conflicts. No hosted service is operated.

## The minimal UI

The coder can clone the repo, run the site locally, and use git. That collapses the whole
problem to three pieces:

1. **A marker-free coding page** (`views/code.html`), kept separate from the review/compare
   site so markers never leak in. It shows: coder name (localStorage), an arc picker
   (`(model, scene, run)` / "next uncoded"), the raw 4-turn transcript for that arc and
   nothing else, and a coding panel — a growing list of `code + quote + memo` entries.
   Autosaves to localStorage every keystroke; debounced POST to `/save`. Optional: select
   transcript text → "use as quote" (a paste helper, keeps quotes verbatim).

2. **A local write-back server** (`harness/viewer/code_server.py`), ~40 lines of stdlib `http.server`
   (no new dependency). Serves the study's `views/` and handles `POST /save` by **appending** one JSON
   line to `data/coding/open_codes.<coder>.jsonl`. Append-only means concurrent autosaves
   never clobber and the file diffs cleanly. Chosen over a "download JSON" button because the
   server writes straight into the working tree the coder is already git-managing — one fewer
   manual step.

3. **File-per-coder JSONL** under `data/coding/`. One object per line:
   `{"coder","model","scene","run","code","quote","memo"}`. Namespacing by coder makes
   independence and conflict-free merge structural.

The coder's loop:

```
python harness/viewer/code_server.py   # serves views/ + accepts POST /save
# open http://localhost:8000/code.html, read arc, type codes — autosaves to the repo file
git add data/coding && git commit && git push   # or open a PR
```

## Built (2026-09-12)

Phase 0 is in: `harness/viewer/code_server.py` and `views/code.html`, per the design above, with
four additions from the 2026-09-12 method decisions (convovo-notes `conversation-coding-tool.md`,
modelUN `RESEARCH-QUEUE.md` line 2):

- **Blind.** The server replaces the model name with a salted id; `code.html` never sees markers,
  reads, or judge output (it does not load `data.js`). The codebook view calls `/reveal` to show
  counts by model after the fact.
- **Fixed random order.** Arcs are shuffled once per salt, so every coder walks the same sequence
  and the saturation counter (new codes per 20 coded arcs, in the header) is comparable across
  coders.
- **Quote check at save.** A code is refused unless its quote is a verbatim substring of the arc,
  the same rule the judge pipeline enforces downstream.
- **Filter and search** by scene, code, and substring, for constant comparison during coding.

Run: `python harness/viewer/code_server.py --study studies/conduct --scenes bad_plan,facts,make_it_better,doctors_note --per-scene 10`
(the four splitters from `bottom-up/divergence-2026-09-12.md`; the balanced 40-arc sample, the same first ten
per scene in the fixed order that the LLM coders get; drop `--per-scene` for all 304), then open
`http://localhost:8000/code.html`. Codes land in `data/coding/open_codes.<coder>.jsonl`, committed.

**LLM coders, for comparison (2026-09-12).** `harness/open_code.py` runs the same arcs, same blind ids,
same order, same three fields, and the same instructions a human coder gets, through cross-vendor
models on OpenRouter, writing `data/coding/open_codes.llm-<slug>.jsonl`. Quotes are string-verified
and unverifiable codes dropped. The LLM is a coder whose output is compared to the human's, never the
reference; do not read its files before your own coding is in. `harness/compare_codes.py` reports,
per pair of coders, span overlap on arcs both coded (judge-free); label matching is the
reconciliation pass a person does afterwards, which is also the first axial step. Each human code
carries `sitting`, `secs_on_arc` (since the previous code on this arc), and `secs_total` (since the
first code on this arc); the clock starts at the first code, not when the arc opens, and the
page's median excludes arcs with a gap over ten minutes, so breaks do not count.

## Plan

- **Phase 0 — pilot tooling.** Build `code.html` (reuse the existing transcript-render code so
  arcs look like the rest of the site) + `code_server.py` + `data/coding/`. Wire to one real
  scene-arc.
- **Phase 1 — open coding.** One or two coders, codebook-blind, a handful of arcs. Validate
  that humans produce useful, grounded codes at all before building anything around it.
- **Phase 2 — axial coding.** Once there's a corpus, cluster open codes into emergent
  categories via constant comparison (LLM may *assist* the affinity-grouping; humans decide).
  Premature structure is the classic grounded-theory failure — defer until there's something
  to cluster.
- **Phase 3 — the diff.** Compare the emergent codebook against the six markers (convergent /
  dead weight / blind spots). Feed blind spots back as candidate markers or new scenes.
- **Tooling graduation.** If multi-coder + axial clustering outgrows flat JSONL, move the
  axial phase to a relational tool (e.g. Airtable) and export back to the repo. Do *not* start
  there — pay that cost only once the clustering phase demands it.
