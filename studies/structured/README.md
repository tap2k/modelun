# structured — does asking for JSON change the answer?

Study #5 on the [modelun harness](../../README.md). The [`consensus`](../consensus/) census
measures which answer a model picks when many are valid ("Name a tree.") in plain chat. This
study repeats the census with one change: the reply format. *"Name a tree. Reply with JSON
only, in the form {"word": "<your answer>"}."* No schema enforcement, no constrained decoding,
no token masking — just the request. The question is whether the **serialization register**
shifts which answer gets chosen.

## The findings (full 31-category battery, 44 models, 2026-07-10)

**1. The format tax is progressive.** Field mean surprisal drops 1.80 → 1.58 bits under JSON,
and the drop concentrates on the divergent tail: deepseek-v3.2 −1.32 (the census's lone
frontier-lab explorer loses half its personality), hermes −0.98, gpt-4o-mini −0.92,
gpt-4-turbo −0.87, gpt-5.6-sol −0.66 — while the conformist floor barely moves (sonnet-5
−0.05, grok-4.5 −0.07). The scorecard's spread compresses from ~2.2 to ~1.5 bits. On "Pick a
word.", *serendipity* goes from 40% of the field to 63%, distinct answers 53 → 28.

**2. Mostly a sharpener; re-indexes only where the plain mode is weak.** The JSON field mode
matches the plain mode in 28/31 categories, <4% of mass lands on answers the plain census
never saw, and the tail thins. The three flips are all weak-mode categories — insect: ant 43%
→ butterfly 60%; board_game: chess → monopoly; dance: salsa → tango — and the new modes smell
like the example-payload canon of documentation corpora. β-story reading: the register
amplifies its own conditional prior, which only wins where the chat prototype was weak.

**3. Defaults are register-indexed — the register erases about half of them.** Across the
panel, models hold 144 stable off-modal defaults (same non-modal answer four-of-four in
chat); only 47% survive into JSON. Retention is a per-model trait: gpt-5.6-terra loses its
signature defaults (mustard→ketchup, mango→apple, four-of-four flips) keeping 1/4;
claude-fable-5 keeps 5/7 (mustard, mango survive; gouda→cheddar does not) — and *acquires
five new JSON-only stable defaults* (cerulean for color, carpenter for occupation, 4-of-4 in
the register, never in chat). llama-4-maverick holds the panel's largest defaults set (10)
and keeps 6, which is what its positive Δ is made of. So "conviction vs costume" is a
continuum, and the true object is a per-register defaults profile — a model's personality is
indexed to the channel, the same way the census found answers indexed to wording. (All read
from deterministic 4-of-4 answer behavior; the surprisal deltas for individual models are
n.s. — see finding 5.)

**4. The register gradient (full-battery, compliance-conditioned, permutation-tested).**
JSON and XML compress the field and the effect is highly significant on both exchangeable
units (field entropy over 31 categories: −0.20 bits, p=.0006; per-model Δ-surprisal over 44
models: −0.22, p=.0001; XML similar). YAML and CSV show **no significant net effect**
(p=.76/.15) — YAML's dramatic any-word concentration (65% serendipity) is real but
category-specific, washing out battery-wide. Brackets significantly **loosens** the field
(+0.14 bits entropy, p=.005): an arbitrary non-data wrapper makes the field *more* varied.
The json-vs-yaml gradient is itself significant (paired by category, p<1e-4). Compression is
thus specific to the answer-delivery formats models are trained to speak — which favors the
tool-use-post-training story over pure corpus register, though the any-word result keeps
both alive. Tests: `probe_significance.py` (sign-flip permutation, 20k draws). Two companion phenomena: **format
incompetence** (granite/mythomax emit CSV wrappers ~1% of the time; their unwrapped replies
read as spurious divergence — always condition on compliance) and a genuine **register-
diverger** (llama-4-maverick: 100% compliant in json/csv and still +0.4 to +0.7 in every
format). Parse survival ≥99% per column after junk-guarding.

**5. The Δ ordering has exactly three tiers of meaning — read it that way.** (a) Seven models
have individually significant Δs (BH-FDR q=.10), all compressions: deepseek-v3.2 −1.31,
hermes −0.96, gpt-4o-mini −0.92, gpt-4-turbo −0.87, gpt-5.6-sol −0.65, qwen3 −0.45,
gemini-3.1-pro −0.31. (b) One family-level effect: the Llama-derived group (maverick,
llama-3.3, mythomax [a community Llama-2 merge]) *diverges* under JSON — no member
significant alone, but pooled Δ +0.44 (p=.009) and +0.70 vs the rest of the field
(two-sample permutation, p<.0001, surviving a ×19 family-selection penalty). Interpretation
is open: hermes-4 (also Llama-based, heavily Nous-retuned) compresses hardest of anyone, so
base weights alone don't explain it — but with community derivatives splitting both ways
(mythomax up, hermes down), a clean "follows the tuner" story doesn't hold either.
Pre-registered for the clean re-run; mechanistically unresolved.
(c) The remaining ~37 models are a noise plateau (Δ range −0.67…+0.56, none distinguishable
from zero individually): their ordering means nothing, exactly the census's tiers-not-ranks
rule applied to deltas. The conviction/costume contrast (fable vs terra) rests on discrete
4-of-4 answer behavior, not on Δ magnitudes, and is unaffected.

**6. The register moves the mode, not the temperature.** Field-mean self-distinctness is
nearly flat across columns (plain 0.42 → json 0.39) while surprisal drops 0.22 bits — the
collapse is positional, not a sampling change (and so not a serving-layer artifact). The
within-model narrowing that does exist is progressive like everything else: hermes 0.71 →
0.52, deepseek-v3.2 0.56 → 0.42, while the conformist floor and fable (0.32, conviction ≠
noise) don't move.

Contrast with the census's "unusual fruit" probe: a **semantic reframe re-indexes** (new
column, new mode — durian), while a **channel reframe sharpens** (same column, higher peak).
The question picks the distribution; the register sets its peakedness — mostly by moving
mass onto the mode, not by cooling the sampler.

## Why this is its own study

The structured-output literature measures *accuracy* under format requests (Let Me Speak
Freely, EMNLP 2024 — contested by the dottxt rebuttal), *validity-vs-correctness* under
decoder-level enforcement (the 2026 "constraint tax" line), and *engineering fixes* for
diversity within grammars (automata steering). Nobody measures **which answer** gets chosen
under a mere format request, across a cross-vendor panel. Prior-art map: section 9 of the
modelun bibliography (flowstore). Note both obvious names are taken — "constraint tax"
(arXiv:2605.26128, 2606.25605) and "The Format Tax" (arXiv:2604.03616) — and both refer to
enforcement/accuracy effects, which this study deliberately is not.

## Design

- **Baseline**: the consensus study's plain-chat transcripts (same 31 questions, same
  44-model roster, same conditions: no system prompt, temp 1.0, 4 runs).
- **JSON**: full 31-category battery, all 44 models × 4 runs.
- **XML + brackets**: 6-category controls (color, fruit, condiment, cheese, tree, any_word)
  to separate serialization from mere structure.
- **Metric**: the census's answer-choice surprisal, computed per format column; the
  per-model **Δ-surprisal (JSON − plain)** is the headline "how much personality does the
  register erase" number. Junk guard + parse: format wrapper stripped mechanically
  (regex per format), then the census normalization applies.

## Compliance as a standing metric

Wrapper-hit rate per model per format falls out of every run for free, and it is kept
deliberately: (1) with one-word content, a missing wrapper is *pure* format incapacity —
unlike IFEval/FOFO-style evals, where format and task difficulty entangle; (2) it is the
mandatory control for any distributional claim (non-compliance masquerades as diversity:
granite's 1% CSV compliance read as +1.69 bits of "personality" unconditioned); (3) it is a
generational capability track — gpt-3.5-turbo speaks YAML at 19% where modern models are
~100%, so format registers have acquisition dates the re-run battery will record. Analogous
to `self_distinct` doubling as the effective-temperature proxy in the census: `wrapped/n`
doubles as the format-capability scorecard.

## Run

```bash
../../.venv/bin/python run_formats.py     # -> probes/format_register.json (raw replies)
../../.venv/bin/python analyze.py         # comparison vs ../consensus transcripts
```

Status: findings frozen (2026-07-11, after the finding-5 correction); committed. Data collected
against the 44-model roster but not yet re-run clean (current file is the interrupted+refilled
run). Paper draft in `paper/main.tex` (finished abstract, skeleton body); blog draft in
convovo-site. Depends on `../consensus/` for the stimulus, roster, baseline transcripts,
and `probe_lib.py`.
