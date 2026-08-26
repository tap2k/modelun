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

Ecological grounding: the six usage verbs cover ~72–74% of consumer ChatGPT usage
(Chatterji et al. 2025, NBER 34255) and the majority of non-coding usage in every major
usage study (Clio; Anthropic Economic Index; WildChat; Microsoft's Working with AI). Full
crosswalk, per-source coverage estimates, and deliberate exclusions (coding, image
generation, translation, roleplay): `docs/usage-crosswalk.md`. Resist is the deliberate
exception — a character probe, not a usage category.

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

## Spec conventions (spec/stimulus.json)

The spec is the frozen instrument and carries no commentary; rationale lives here.

- Prompt sent = template with `{text}` replaced by the anchor text. Bare-slot templates
  (Explain, Advise, Create, Resist) send the anchor verbatim, so the anchor carries the
  question form and each anchor is in effect its own template. Advise uses this so the
  binary and open-dilemma anchors differ in form, not just topic.
- Each anchor has `id`, `text`, `frozen_at` (null until 1.0; set once, never changed).
  Each template has a `rotation` list, empty in v1.
- Sampling: `temperature: null` = as served (not set in the request); n=3 per cell.
  Convergence measures are therefore descriptive only in v1.
- `max_tokens` 8192; `finish_reason` recorded per cell so verbosity is not cap-relative.

## Anchor rationale (0.4 draft)

| Anchor | Why this one |
|---|---|
| explain-a1 mortgage | topic; audience unspecified on purpose; analogy reach |
| explain-a2 flat tire | how-to; structure (steps vs prose) |
| advise-a1 job offer | explicit binary, asks "what should I do?"; commit vs hedge |
| advise-a2 sister loan | open dilemma, no question asked; ask-before-advising vs presumption |
| draft-a1 decline wedding | decline; formula n-grams, politeness register |
| draft-a2 late rent | bad news; hedging formulas |
| create-a1 programmer joke | joke convergence |
| create-a2 lighthouse keeper | story; naming convergence (Elara effect) |
| edit-a1 follow-up email | correct, flat workplace prose; rewrite fraction |
| edit-a2 park paragraph | correct, deliberately plain personal prose; unrequested style rewrites |
| interpret-a1 "circle back" | social ambiguity with enough context that the model must read it rather than ask; readings count |
| interpret-a2 red wheelbarrow | literary ambiguity (Williams, US public domain); closure |
| resist-a1 day-trader | bad plan, announced not asked; applaud / question / warn |
| resist-a2 doctor's note | wrong ask (forgery) with a sympathy bid; refuse / coach toward a real note / write it |

Resist anchors span two pressure types, a bad plan and a wrong ask. A confident wrong fact
(5×9=54) was tried and dropped: every capable model holds it on turn one, so it does not
separate models single-turn. A self-flattering self-story was also dropped for v1: models
push back on it uniformly and gently. Both are rotation candidates if a harder single-turn
form is found. All Resist cells are collected fresh with the rest of the battery.

Edit anchors must contain no error, or interventionism collapses into correction.

## Open design work before freeze

- Review the 0.4 draft anchors (all 14 drafted, none frozen).
- Edit anchors: confirm no reader finds a real error.
- Interpret anchors: attest the ambiguity (one social, one literary).
- Resist: decide whether the fact/self-image types need single-turn forms hard enough to
  separate models, or stay as rotation candidates.
