# The core harness

A small, domain-neutral tool for **labeling and viewing** model transcripts. Ask an arbitrary
multi-turn script to arbitrary models; grade the transcripts with an LLM judge *and* a human judge,
voted together; render for review. Transcripts may come from this harness's runner or any raw log.

The conduct atlas is *one study* on this core — and the **worked example** a new study is cloned from
([`studies/conduct/`](../studies/conduct/README.md)). It supplies a `{stimulus, codebook}` spec and its
own view code; the core holds no study semantics. For the study itself see its
[markers](../studies/conduct/docs/markers.md), [scenes](../studies/conduct/docs/scenes.md), and
[houses](../studies/conduct/docs/houses.md) docs.

## Ontology

| Concept | Is | Keyed by |
|---|---|---|
| **scene** | one multi-turn stimulus (a script of escalating user turns) | `scene_id` |
| **run** | one sampling of a scene against a model (temperature > 0 → a distribution) | `(model, scene, run)` |
| **transcript** | a model's reply-arcs across scenes | one file per model |
| **labeler** | a grader — an LLM judge *or* a human; the same primitive | `provider/model` \| `human/name` |
| **criterion** | one question in a codebook, bound to one scene; binary, graded (scale *planned*) | `criterion_id` |
| **codebook** | a bundle of criteria (= a rubric) | per study |
| **label** | one labeler's verdict on one criterion for one run, with a verbatim quote | `(labeler, model, scene, run, criterion)` |
| **store** | the adjudicated result: labels quote-verified and voted across labelers | one file per study |
| **study** | a `{stimulus, codebook}` spec + its own views | a folder under `studies/` |

Two concepts carry the harness's intelligence: **`labeler`** — graders compose, independent and
voteable, with a human and an LLM treated identically — and **`quote`** — every verdict is a
mechanically checkable substring of the text it judges.

## The pipeline

```
spec.stimulus ─► RUNNER ──────────► transcripts/<model>.json          (Contract A)
A + spec.codebook ─► JUDGE ───────► labels/<labeler>/<model>.json     (Contract B)
B + A ─► ADJUDICATOR ─────────────► store.json   (quote-verified, voted, self-family tagged)
A + store ─► RENDERER ────────────► transcript view + side-by-side compare
```

Two contracts (transcript, label) are the spine; the components are transforms between them.

> **Target vs. the legacy exemplar.** The shapes below are the *target* contracts. The conduct study
> predates them and is **grandfathered**: it uses `script_version` (not `spec_version`), wraps scenes
> in a `registers[]` array (not flat `scenes[]`), names the label quote `trigger_quote` (not `quote`),
> and its store carries `verdict`/`evidence`/`self_judged` rather than raw `runs:[{value,quote}]`. The
> harness reads both because it resolves names through `harness/study.py`. A **new** study should use
> the names here; conduct stays as-is rather than churn 2 MB of published, cited data. Where a field is
> marked *(planned)*, the code does not implement it yet.

## Contract A — the transcript

One file per model, authored by the model. Merge by `scene_id`: re-running a scene replaces one key,
never rewrites the file.

```jsonc
{
  "model": "<label>",                 // short display name
  "slug": "<provider/model>",         // OpenRouter slug; vendor = slug.split('/')[0]
  "spec_version": "<frozen stimulus version>",   // bumping it invalidates comparability
  "temperature": 1.0,
  "max_tokens": 1200,
  "scenes": {
    "<scene_id>": {
      "run_date": "YYYY-MM-DD",
      "runs": [                       // 1..N samples of THE SAME stimulus; default length 1
        [                             // one arc = the multi-turn conversation
          { "u": "<user turn>", "reply": "<model reply>" },
          { "u": "<user turn>", "reply": "<model reply>" }
          // a failed scene: { "u": "...", "reply": null, "error": "..." }
        ]
      ]
    }
  }
}
```

- `runs` is a list because a scene is one stimulus and a run is one sampling of it — sampling the same
  input N times to observe nondeterminism is fundamental to evaluating a stochastic model. Length 1
  when a study doesn't repeat; a label's `run` indexes into it.
- Failures live inside the file (`reply: null, error`); the runner exits 0 so a flaky route doesn't
  sink the batch.

## Contract B — the label

Labeler-namespaced files; the union of files is the merge; many labelers per scene, no clobber.

```jsonc
{
  "labeler": "<provider/model | human/name>",
  "target": { "model": "...", "scene": "...", "run": 0, "criterion": "..." },
  "kind": "binary | graded",          // scale planned
  "value": true,                      // type follows kind:
                                      //   binary → true|false
                                      //   graded → "<category id>"
                                      //   scale  → <int in range>  (planned)
  "quote": "<verbatim substring>",    // omitted iff requires_quote: false  (planned)
  "note": ""                          // optional
}
```

- `target` is arc-grain: one criterion judging one sampling of one scene. (Turn-grain adds `turn_idx`;
  subject-grain — "this model is a Therapist" across all scenes — is not modeled, it stays prose
  synthesis.)
- `quote` is substring-verified by the adjudicator (smart-quote / markdown / line-join normalized),
  required unless the criterion declares `requires_quote: false` for a holistic judgment with no single
  trigger line.

## The spec

A study is the `{stimulus, codebook}` data the runner and judge consume. Views are not in the spec — a
view is code, and lives in the study's own script on the core renderer.

```jsonc
{
  "spec_version": "...",
  "stimulus": {                       // → RUNNER
    "system_prompt": "<optional>",
    "scenes": [
      { "id": "<scene_id>", "turns": ["<u1>", "<u2>", "..."] }
    ]
  },
  "codebook": [                       // → JUDGE + ADJUDICATOR
    { "id": "<criterion>", "scene": "<scene_id>", "kind": "binary", "question": "...",
      "requires_quote": false,        // present only when opting out; absent = required  (planned)
      "categories": { "<id>": "<desc>" },   // graded only
      "range": [1, 5] }                     // scale only  (planned)
  ]
}
```

A criterion binds to one scene — it judges that scene's transcript, and the adjudicator needs the scene
to locate the reply to verify the quote against. A codebook is a bundle of criteria; there is no
separate "rubric" type. Stimulus is frozen and versioned — changing it bumps `spec_version`, and
old/new are not comparable.

## The components

1. **RUNNER** — *stimulus → transcripts.* Plays each scene's escalating turns multi-turn against each
   model via one OpenRouter endpoint; writes Contract A, merging by scene-key. Escalation is scripted,
   not adaptive — identical turns regardless of reply, which is what makes columns comparable.
   *(= `harness/run.py`.)*

2. **JUDGE** — *transcript + codebook → labels.* Two backends behind one contract: an LLM judge
   (builds a prompt from the codebook, forces grounded JSON) and a human judge (the codebook as a side
   panel on the renderer; picks `value`, selects `quote`). They differ only in `labeler`.
   *(= `harness/judge.py`; the human path is a thin UI on the renderer.)*

3. **ADJUDICATOR** — *labels → verified, voted store.* For each `(target, criterion)`: substring-verify
   every `quote` and drop the unverified; aggregate across labelers by `kind` — binary → majority,
   graded → majority (tie → contested); tag `self_family` (labeler vendor == subject vendor) as a
   neutral fact the study may use or ignore. *(Planned: `scale` → mean/median + spread, and a per-
   criterion `requires_quote: false` to skip verification for holistic judgments.)*
   *(= `harness/adjudicate.py`.)*

4. **RENDERER** — *transcripts (+ optional store) → view.* Ships the transcript view and side-by-side
   compare, nothing more. It renders scenes but knows no markers, colors by no verdict, imports no house
   style. Buildless (no deps, open the HTML); exposes `renderArc()` / `renderCompare()` for studies to
   call and decorate. Bespoke views (a marker grid, a synthesis, a plot) are study code on top.
   *(= `harness/viewer/core.js`, with the conduct grid/compare layered on in `studies/conduct/views/`.)*

## The store

What the renderer reads.

```jsonc
{
  "models": {
    "<model>": {
      "<criterion>": {
        "runs": [ {"value": ..., "quote": "..."}, {"value": ..., "quote": "..."} ],
        "self_family": false
      }
    }
  }
}
```

Run-to-run agreement is derivable from `runs`, so the study computes and names it (`stable-hold` /
`split`) rather than the store carrying it.

## Two invariants

1. **Quote-grounding is mechanical and universal.** Every label verifies the same way regardless of
   labeler or kind, unless a criterion opts out. The adjudicator is the only place trust is decided.
2. **The renderer knows no study.** It draws transcripts and a compare view; all study vocabulary,
   special views, and synthesis live above it as study code.

## Repository layout

The primary cut is tool vs. study — code that stabilizes vs. data that grows. The harness holds no
study semantics (markers, house styles, TONGUE/HANDS/HEART); generic data nouns like "scene" are fine.
A study holds all of it, which makes it extractable to its own repo as a `git mv`.

A study may rename the data dirs via `spec/paths.json` (conduct keeps its historical
`data/benchmark` + `markers/`); the generic names below are the defaults.

```
modelun/
├── harness/                 # the tool — code only, no study semantics
│   ├── run.py               #   stimulus → transcripts
│   ├── judge.py             #   transcript + codebook → labels
│   ├── adjudicate.py        #   verify + vote + self-family tag
│   ├── render.py            #   transcript → readable markdown
│   ├── study.py             #   resolves a study's paths (--study)
│   └── viewer/core.js       #   transcript + compare renderer
│
├── studies/
│   └── conduct/             # study #1 (the worked example)
│       ├── spec/
│       │   ├── stimulus.json   #   the frozen multi-turn script
│       │   ├── codebook.py     #   criteria × kind
│       │   └── paths.json      #   optional dir-name overrides
│       ├── transcripts/<model>.json          # Contract A  [commit basis, gitignore scratch]
│       ├── labels/<labeler>/<model>.json     # Contract B  ← collaboration primitive
│       ├── coding/<coder>.jsonl              # inductive open codes [deferred]
│       ├── store.json
│       ├── views/index.html                  # bespoke views on viewer/core.js
│       ├── docs/                             # study docs (markers, scenes, houses)
│       └── README.md
│
├── docs/harness.md
└── README.md
```

- **`studies/<name>/`** — a study is a folder; `conduct` is not privileged. A second study (another
  codebook, a prompting A/B) is a sibling folder. `studies/` is in-repo multiplicity; separate repos
  are cross-team multiplicity.
- **`labels/<labeler>/`** — the collaboration primitive. Each grader (human or LLM, the same `labeler`)
  writes only their own subtree; the merge is the union; git is the merge engine. No backend.
- **`views/`** lives in the study, never in `harness/viewer/` — a conduct view cannot sit in the
  harness folder.
- A study's `docs/` move into the study; `docs/harness.md` (about the tool) stays at top level.

**Who does what.** A grader clones the *study* repo, runs `judge.py` or opens the human-labeling page,
and writes into `labels/<their-name>/` — never cloning the harness, which the study resolves as a
dependency. A reader clones nothing: the study publishes `store.json` + `transcripts/` +
`views/index.html` to GitHub Pages — buildless, no key. "Local data" is just unpushed
`labels/<name>/`; git's commit boundary is the public/private line.

A study graduates from a folder to its own repo (`modelun-study-<name>`, pointing at a `harness/`
checkout) when it needs different collaborators or access than the harness — not before.

## Human labeling: build, don't adopt

Mature tools exist across three categories — and each solves the cheap part (a labeling/compare
surface) while missing the **load-bearing** part this core is built around: *a human and an LLM as the
same voted `labeler`, one mechanical quote-verification gate over both, and self-family flagging.* The
survey below is current as of 2026-06; the gap is structural, not a missing feature.

| Tool | Category | Has | Missing (vs. this kernel) |
|---|---|---|---|
| **promptfoo** | prompt/model eval | runner, side-by-side compare grid, **a human rating surface** (👍/👎, 0–1 score, comment, exportable) | single-rater only — no multi-annotator, no human+LLM **voted as one** primitive, no quote-grounding gate |
| **Argilla** | data annotation | multi-annotator (`Response`), span highlight, LLM `Suggestion` | LLM is a **non-voting suggestion**, not a peer labeler; no documented vote/aggregation; spans stored, not substring-verified |
| **Label Studio** | data annotation | multi-annotator, span, LLM-as-judge integration | same human/LLM split; server + DB; no quote-verification invariant |
| **Taguette / QualCoder** | qualitative coding | human open coding, quote-anchored excerpts | no LLM labeler at all; no voting across human+machine |

Two specifics worth stating, because they're the exact dividing line:

- **promptfoo does do human eval** — its web UI persists per-cell pass/fail, a custom score, comments,
  and exports a "Human Eval YAML" / DPO JSON. But it is *one* rater building a dataset, with the LLM
  graders living on a separate `assert` track. It never **votes a human and an LLM together as coequal
  `labeler`s**, which is this core's defining primitive — and it has no substring-verification gate.
- **Argilla is the closest miss** — it has real multi-annotator support — yet it draws the line this
  core deliberately erases: a human is a `Response` (the real labeler), an LLM is a `Suggestion` (a
  non-voting aid shown to humans). Here they are the *same* voteable primitive, distinguished only by
  the `labeler` string.

All four are also **servers with their own DB and data model**, breaking the two properties this core
rests on — buildless / no-deps, and git as the collaboration layer. Since the transcript renderer
already exists, the human panel is just the LLM judge's Contract B filled by a human; that thin UI plus
the small adjudicator is the smaller and better-fitting build. (Academic qualitative-analysis pipelines
— e.g. QualAnalyzer, multi-stage LLM coding with auditable quote trails — share the quote-grounding
instinct, but are research artifacts, not adoptable tools, and still lack the human-and-LLM-as-one vote.)

## Inductive open coding (deferred)

Inductive coding — humans read arcs codebook-blind and *invent* codes, see
[inductive-coding.md](../studies/conduct/docs/inductive-coding.md) — is a sibling activity, not a fourth `kind`. The closed
kinds (binary/graded/scale) consume a codebook and select from a declared value space, so they vote.
An open code produces a codebook: no pre-declared criterion, nothing to vote on.

The schema is deferred until the coding UI is built (the schema is that UI's output). The contract is
fixed: open codes reuse `labeler`, arc-grain `target`, and the same `quote` verifier; drop `criterion`
and `kind` (the invented code is both question and answer); carry a `memo`; live in their own
labeler-namespaced file (`coding/<coder>.jsonl`); don't vote. When an emergent code graduates into a
fixed category, it becomes a declared `graded` criterion and crosses into the closed model.
