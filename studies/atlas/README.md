# atlas — the everyday battery

The atlas's admission interview: every model answers the same frozen set of everyday tasks,
single-turn, judge-free. Character at rest (plus one everyday-pressure verb). Stands alone —
no dependence on the other studies; the atlas site is built on this battery only.

## Verbs (battery v1 candidate set)

**EXPLAIN · ADVISE · DRAFT · CREATE · EDIT · INTERPRET · RESIST**

Each verb is a template with a variable slot (template × filler × version):

| Verb | Slot | Character axis | Measures |
|---|---|---|---|
| Explain | {topic \| how-to task} | analogy-reach, register | analogy extraction (span), structure, length |
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
  Create anchors span forms (one joke item, one story item); Resist anchors span pressure
  types (wrong assertion / bad-plan applause); Advise anchors span forms of neutrality
  (explicit binary "deciding between A and B" / open dilemma with no options — measures
  ask-before-advising vs presumption). Boundary rule: atlas Advise NEVER plants a stance or
  appends a tag — that is the suggestibility instrument, which lives in the papers.
- **Judge-free**: stylometrics, span extraction, exact/edit-distance measures. Any judge use
  follows the handcuffs rule (verbatim substring selection only).
- **Versioned**: template × filler × spec_version; new anchors may be ADDED in later waves,
  never changed. Every result cell carries model version + collection date.
- **Cheap by construction**: ~7 verbs × ~2–3 fillers × panel × few samples ≈ thousands of
  short calls — tens of dollars a wave.

## Measurement architecture: two layers

**Layer 1 — deterministic calculations** (always-on, judge-free, wave-comparable by
construction): verbosity (all cells); Edit = edit/word distance + rewrite fraction;
convergence counts (Create, Explain-analogy) by normalized match; Draft formula n-grams;
tics = distinctive n-grams vs field baseline.

**Layer 2 — derived codebooks** (per verb, per battery version): typologies that can't be
pre-specified — advising styles, interpretation postures, resistance manners — derived by
the BQC pass (open coding → embed-cluster-curate → categories bound to verbatim evidence,
reconciled to countable distributions), then applied mechanically. Derivation is the one
interpretive act; application inherits layer 1's reproducibility. This layer IS the labeling
service's methodology, demonstrated.

## Dimensions the atlas site derives from these cells

Verbosity (all cells) · uniqueness/convergence (Create, Explain-analogy) · stance (Advise) ·
interventionism (Edit) · closure (Interpret) · spine (Resist) · tics & phrases (all cells,
distinctive n-grams vs field baseline) · register (Draft/Explain).

Type layer: derive empirically — cluster models over the full profile; name clusters only if
real (no imposed global typology; no leaderboard, ever — characters, not ranks).

## Open design work before freeze

- Pick the anchor filler per verb (one each, frozen forever — choose deliberately).
- Resist anchor texts: pull and adapt from `studies/conduct/` — the scripted scenes already
  contain the pressure utterances (arithmetic hill, day-trader, self-flattering story);
  take the single-turn pressure line from each rather than authoring fresh.
- Edit stimulus (the flawed-but-fine paragraph — must be genuinely two-sided).
- Interpret stimulus (expert-attested ambiguity).
- Sampling: n per cell, temperature policy.

