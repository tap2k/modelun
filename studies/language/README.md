# language — comparing model generation in a language

Study #2 on the [modelun harness](../../README.md). Where [conduct](../conduct/README.md) exercises the
full pipeline (codebook, LLM judge, voted store, bespoke marker grid), this study is deliberately the
**other half**: the runner and the renderer, with the judging kernel left out. It asks a fixed
conversation to several models, in a target language, and renders the transcripts side by side. No
codebook, no labels, no store — just *generate and view*.

This is the harness's smallest honest study, and a useful counterweight to conduct: proof that a study
can use the runner + renderer alone, with the grading slot left open for later.

## The question

**How do different models generate in a given language — and how do they differ?** Same turns, same
system prompt, many models, read the columns. The first (and currently only) language is **Gujarati**.

There is no rubric and no verdict. The output is a transcript view and a side-by-side compare; the
reader judges quality, fluency, register, and faithfulness by eye. A codebook can be added later (see
[Leaving the grading slot open](#leaving-the-grading-slot-open)) without reworking anything above it.

## Scope: one language, deliberately

This study is **one language compared across models** — nothing more. That is the whole design, and the
restraint is the point.

The obvious next question — *how do we hold many languages?* — is **deferred on purpose.** There is one
language today. Every mechanism for multiple (a `lang` field on scenes, a per-language folder split, a
view that filters by language) is infrastructure for a second language that does not yet exist, and
each such mechanism invents a concept the harness does not natively model. The harness knows *scene*,
*model*, *transcript* — it does not know *language*. Adding that vocabulary now, before a second
language exists to justify a particular shape, is guessing.

So the shape here is the plain one the harness already documents: **a study, exactly like conduct, minus
the grading half.** When a second language is real, its actual requirements — shared turns or
native-authored ones? its own collaborators? a fluency codebook? — will pick the multi-language shape
with evidence instead of speculation. That decision belongs *after* Gujarati transcripts exist and have
been looked at, not before. (KISS, YAGNI: build the one correct thing for today.)

## Method

A fixed multi-turn script, identical for every model. The **user turns are written in the target
language** — a natural same-language conversation, which tests the *quality and fluency* of replies
rather than the instruction-following pull of "stay in language X while I write English." The top-level
system prompt names the language and sets register. The runner plays the script multi-turn against each
model via one OpenRouter endpoint; the renderer shows each model's arc and a side-by-side compare.

- **Temperature / runs.** Default `runs: 1` unless you want to observe nondeterminism — fluency is
  usually stable enough that N=1 is informative and cheap. Bump `--runs` if a model looks borderline.
- **No escalation semantics.** Unlike conduct, the turns need not escalate or pressure; they are just a
  representative conversation in the target language. (They *may* — nothing forbids a hard scene — but
  the default is an ordinary exchange.)

## Spec shape — flat `scenes[]`, the documented target

This study uses the **target Contract** from [harness.md](../../docs/harness.md) — flat `scenes[]` with
a top-level `system_prompt` — not conduct's grandfathered `registers[]` / `script_version` wrapper.
Conduct predates the flat schema and is kept as-is; a new study should use the names the docs promise:

```jsonc
// spec/stimulus.json
{
  "spec_version": "1.0",
  "system_prompt": "તમે ગુજરાતીમાં જવાબ આપો છો. સ્વાભાવિક, વાતચીતની ભાષામાં લખો.",
  "scenes": [
    {
      "id": "greeting",
      "turns": [
        "<gujarati user turn 1>",
        "<gujarati user turn 2>"
      ]
    }
    // more scenes — each a representative Gujarati exchange
  ]
}
```

No `lang` field, no per-scene system prompt: the language is a property of *this whole study*, carried
once at the top, exactly as the harness documents. If a second language ever lands, that is the moment
to decide whether it becomes a field, a folder, or a sibling study — not now.

### Runner change this required (done — one small, additive patch)

`harness/run.py` originally read only `spec["registers"]` and `spec["script_version"]` — conduct's
legacy shape. It now also accepts the flat `spec["scenes"]` / `spec_version`, via an `iter_scenes(spec)`
helper that yields `(register_name, scene)` for either shape (register is `None` for flat specs). The
version key is written through as found (`spec_version` here, `script_version` for conduct), and
`play()` honors a per-scene `system_prompt` override falling back to the spec-level one. The change is
purely additive — conduct runs byte-identically — and pays down the doc/runner drift
[harness.md](../../docs/harness.md) flags.

## Leaving the grading slot open

There is no `spec/codebook.py`, no `labels/`, no `store.json` now. The folder shape leaves the slot
open: if a comparison signal is wanted later — e.g. a graded *fluency* category per scene — drop in
`spec/codebook.py` and run `harness/judge.py` + `harness/adjudicate.py`. Everything above (runner,
transcripts, view) is unchanged; the study simply gains a graded layer. This is the start-simple path:
generate-and-view first, grow into a graded study only if the eye-read proves insufficient.

## Layout

```
studies/language/
├── spec/
│   └── stimulus.json          # flat scenes[], top-level system_prompt
├── transcripts/<model>.json   # Contract A — runner output, one per model  [created on first run]
├── views/
│   ├── index.html             # thin page: Transcripts + Compare tabs on the core renderer
│   ├── build.py               # bakes transcripts → data.js (+ copies core.js)
│   ├── data.js                # generated blob          [gitignored]
│   └── core.js                # copied harness renderer [gitignored]
└── README.md
```

No `spec/paths.json` — this study keeps the harness's default directory names (unlike conduct, which
overrides them for historical reasons). `data.js` / `core.js` are generated and already gitignored
study-wide.

## Build it

```sh
# 1. run the frozen Gujarati scenes against models (writes transcripts/<model>.json)
python harness/run.py --study studies/language <slug> <slug> ...

# 2. bake the transcripts into the site, then open it (buildless, no server)
python studies/language/views/build.py
open studies/language/views/index.html
```

The site has two tabs: **Transcripts** (each model's arc per scene) and **Compare** (all models side by
side on the same turns, with a run selector if `--runs > 1`). A scene a model hasn't been run on shows
`[no reply]` cells, so partial runs render cleanly.

## Status

Built; awaiting content + a run.

1. ~~Runner patch~~ — **done** (flat `scenes[]` via `iter_scenes`; conduct unaffected).
2. ~~The view~~ — **done** (`views/index.html` + `build.py`, verified end-to-end on a synthetic
   transcript).
3. **The Gujarati turns** — `spec/stimulus.json` ships **starter** scenes (recipe / advice / explain);
   replace with the conversation you actually want to probe. This is the real content work.
4. **The model set** — pick which OpenRouter slugs to compare, then run the two commands above.
