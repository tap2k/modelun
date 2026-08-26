# atlas — the everyday battery

The atlas's admission interview: every model answers the same frozen set of everyday tasks,
single-turn, judge-free. Character at rest (plus one everyday-pressure verb). Stands alone —
no dependence on the other studies; the atlas site is built on this battery only.

## Verbs (battery v1 candidate set)

**EXPLAIN · ADVISE · DRAFT · CREATE · EDIT · INTERPRET · RESIST**

Each verb is a template with a variable slot (template × filler × version):

| Verb | Slot | Character axis | Measures |
|---|---|---|---|
| Explain | {topic \| how-to task} (± audience) | analogy-reach, register | analogy extraction (span), structure, length |
| Advise | {two-sided decision} | stance/hedging at rest | commitment vs hedge, stance extraction |
| Draft | {communication: decline / ask favor / bad news} | formula, politeness register | formulas (n-grams), length, structure |
| Create | {a name for X \| a joke about X \| a story about X} | generativity, convergence | naming/joke/story convergence (Elara effect), distinct-rate |
| Edit | {flawed-but-fine text} | interventionism | rewrite fraction, edit distance |
| Interpret | {ambiguous thing} | closure-compulsion | readings count, commitment vs multiplicity-held |
| Resist | {wrong assertion \| bad plan \| self-flattering story} | spine under everyday pressure | fold/hold/decline classification |

(Name folded into Create as a filler. Summarize dropped — benchmark-covered.)

## Design rules

- **Single-turn only** (v1). Multi-turn = the papers' territory, or a labeled v2 module.
- **Anchors first, rotation later**: per verb, 2 frozen anchor items to start (frozen from
  their first wave, forever; later anchors append-only). Rotating items join at a later wave;
  anchor-vs-rotation divergence then becomes the contamination meter for a published battery.
  Create anchors span forms (e.g. one joke item, one story item); Resist anchors span pressure
  types (wrong assertion / bad-plan applause).
- **Judge-free**: stylometrics, span extraction, exact/edit-distance measures. Any judge use
  follows the handcuffs rule (verbatim substring selection only).
- **Versioned**: template × filler × spec_version; new anchors may be ADDED in later waves,
  never changed. Every result cell carries model version + collection date.
- **Cheap by construction**: ~7 verbs × ~2–3 fillers × panel × few samples ≈ thousands of
  short calls — tens of dollars a wave.

## Dimensions the atlas site derives from these cells

Verbosity (all cells) · uniqueness/convergence (Create, Explain-analogy) · stance (Advise) ·
interventionism (Edit) · closure (Interpret) · spine (Resist) · tics & phrases (all cells,
distinctive n-grams vs field baseline) · register (Draft/Explain).

Type layer: derive empirically — cluster models over the full profile; name clusters only if
real (no imposed global typology; no leaderboard, ever — characters, not ranks).

## Open design work before freeze

- Pick the anchor filler per verb (one each, frozen forever — choose deliberately).
- Resist filler texts (single-turn versions of the pressure scenes).
- Edit stimulus (the flawed-but-fine paragraph — must be genuinely two-sided).
- Interpret stimulus (expert-attested ambiguity).
- Sampling: n per cell, temperature policy.

Design notes and public/commercial framing: `convovo-notes/atlas.md` (canonical).
