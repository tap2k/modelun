# structured — does asking for JSON change the answer?

Study #5 on the [modelun harness](../../README.md). The [`consensus`](../consensus/) census
measures which answer a model picks when many are valid ("Name a tree.") in plain chat. This
study repeats the census with one change: the reply format. *"Name a tree. Reply with JSON
only, in the form {"word": "<your answer>"}."* No schema enforcement, no constrained decoding,
no token masking — just the request. The question is whether the **serialization register**
shifts which answer gets chosen.

## The findings (full 31-category battery, 44 models, 2026-07-10)

**1. The format tax is progressive.** Field mean surprisal drops 1.80 → 1.58 bits under JSON,
and the drop concentrates on the divergent tail: deepseek-v3.2 −1.31 (the census's lone
frontier-lab explorer loses half its personality), hermes −0.91, gpt-4o-mini −0.92,
gpt-4-turbo −0.87, gpt-5.6-sol −0.65 — while the conformist floor barely moves (sonnet-5
−0.05, grok-4.5 −0.07). The compression is in the mean and the collapsing tail, not the
extremes — a register-invariant minority holds up the top (finding 5b). On "Pick a word.",
*serendipity* goes from 41% of the field to 64%, distinct answers 52 → 36. Nor is
tail-falls-hardest regression to the mean: split-half reliability of the census score is
r=0.94 (`analyze_rtm_splithalf.py`), so pure re-measurement predicts 0.05 bits of shrinkage
for the most distinctive model against the 1.31 observed, and every individually significant
compressor (finding 5a) clears the RTM null by 3.7–10σ.

**2. Mostly a sharpener; re-indexes only where the plain mode is weak.** The JSON field mode
matches the plain mode in 28/31 categories, <4% of mass lands on answers the plain census
never saw, and the tail thins. The three flips are all weak-mode categories — insect: ant 43%
→ butterfly 60%; board_game: chess → monopoly; dance: salsa → tango — and the new modes smell
like the example-payload canon of documentation corpora. β-story reading: the register
amplifies its own conditional prior, which only wins where the chat prototype was weak.

**3. Defaults are register-indexed — verified at n=20.** Across the panel, models hold 144
stable off-modal defaults (same non-modal answer four-of-four in chat, like fable's gouda and
mustard). Re-sampling every default cell at n=20 in *both* registers within a single run
(`run_defaults_resample.py` → `analyze_defaults_resample.py`) settles what four samples
couldn't: the defaults are genuine (median per-sample probability 0.90), and requesting JSON
significantly shifts the answer distribution for 76/144 (53%) of them (Fisher exact per cell,
BH q=.10), 29% reverting outright to the field's modal answer. The register also *installs*
defaults: of the JSON answers a model gives four-of-four but never produces in chat, 81%
survive an n=20 resample as genuine register-only defaults (`run_acquired_resample.py`) —
claude-fable-5 says *cerulean* for color 0% of the time in chat and 100% in JSON (p≈1e-11),
*carpenter* for occupation 0%→90%; opus-4.8 acquires *phoenix*, sonnet-4.6 *gold*. And same
default, opposite response: gpt-5.6-terra and fable both answer *mango* for fruit 20/20 in
chat; under JSON terra flips to *apple* (20/20, p≈1e-11) while fable holds *mango* (19/20).
So "conviction vs costume" is a continuum, and the true object is a per-register defaults
profile — a model's personality is indexed to the channel, the same way the census found
answers indexed to wording. (All read from discrete answer behavior; the surprisal deltas
for individual models are n.s. — see finding 5.)

**4. The register gradient (full-battery, compliance-conditioned, permutation-tested).**
JSON and XML compress the field and the effect is highly significant on both exchangeable
units (field entropy over 31 categories: −0.20 bits, p=.0006; per-model Δ-surprisal over 44
models: −0.22, p=.0002; XML similar). YAML and CSV show **no significant net effect**
(p=.75/.35 by model) — YAML's dramatic any-word concentration (65% serendipity) is real but
category-specific, washing out battery-wide. Brackets significantly **loosens** the field
(+0.12 bits entropy, p=.014; +0.13 per model, p=.009): an arbitrary non-data wrapper makes the field *more* varied.
The json-vs-yaml gradient is itself significant (paired by category, p<1e-4). Compression is
thus specific to the answer-delivery formats models are trained to speak — which favors the
tool-use-post-training story over pure corpus register, though the any-word result keeps
both alive. Tests: `probe_significance.py` (sign-flip permutation, 20k draws). Two companion phenomena: **format
incompetence** (granite/mythomax emit CSV wrappers ~1% of the time; their unwrapped replies
read as spurious divergence — always condition on compliance) and a fully-compliant positive
tail that is real signal, not parse artifact (llama-4-maverick: 100% compliant in json/csv
and still +0.4 to +0.7 in every format — mostly *stranding*, see finding 5b). Parse survival ≥99% per column after junk-guarding, plus an **echo guard** that drops
the category noun / template placeholder (a literal `[city]`, `answer`, `word`) as a non-answer
on every column alike — it trims the raw brackets loosening from +0.16 to +0.13.

**5. The Δ ordering has exactly three tiers of meaning — read it that way.** (a) Six models
have individually significant Δs (BH-FDR q=.10), all compressions: deepseek-v3.2 −1.31,
gpt-4o-mini −0.92, gpt-4-turbo −0.87, gpt-5.6-sol −0.65, qwen3 −0.45,
gemini-3.1-pro −0.31 (hermes −0.91 just misses — its within-model dispersion is the panel's
largest, self-distinctness 0.71, which widens its interval enough that a near-identical delta
falls short). (b) The positive tail is mostly **stranding, not motion**: surprisal is scored
within-column against the pool, so a model that keeps its answers while the field converges
around it earns a rising Δ with no change in its own behavior. A panel-free check
(`analyze_register_invariance.py`: each model's own chat-vs-JSON answer distributions, mean
Jensen–Shannon divergence over the 31 categories, never touching the pool) separates the two —
llama-4-maverick, the panel's largest positive Δ (+0.56, 100% JSON-compliant), has
*below*-median self-divergence (JSD 0.20 vs the field's 0.27; 7/31 modal answers change): it
barely moves its own answers, and its rising score is the collapsing field stranding a fixed,
distinctive point. Register-invariance is a model trait, but not lineage-clean (mythomax,
+0.43, *does* move its own answers), so the positive tail is a mix of stranding and genuine
divergence the panel-relative Δ cannot separate — we decline to rank it.
(c) The remaining ~38 models are a noise plateau (Δ range −0.67…+0.56, none distinguishable
from zero individually): their ordering means nothing, exactly the census's tiers-not-ranks
rule applied to deltas. The conviction/costume contrast (fable vs terra) rests on discrete
answer behavior (finding 3), not on Δ magnitudes, and is unaffected.

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

**7. Enforcement adds little the request did not.** One more column — the JSON clause plus a
strict `response_format` json_schema — on the 36/44 models whose providers support it
(`run_enforced.py` → `analyze_enforced.py`; the other eight return no valid output, itself a
feature-acquisition signal). All three columns recomputed within the 36-model subset's own
pool so they're comparable: plain 1.79 → request 1.56 → enforced 1.53 bits. The request does
the −0.22-bit work; decoder enforcement adds −0.03. The collapse lives in the model's
response to the register, not in the sampler — so it is not a constrained-decoding artifact.
(Per-model reactions are confounded — `response_format` is a native decoder constraint for
some providers and a gateway coercion for others — so read only the battery-wide mean.)

## Why this is its own study

The structured-output literature measures *accuracy* under format requests (Let Me Speak
Freely, EMNLP 2024 — contested by the dottxt rebuttal), *validity-vs-correctness* under
decoder-level enforcement (the 2026 "constraint tax" line), and *engineering fixes* for
diversity within grammars (automata steering). Nobody measures **which answer** gets chosen
under a mere format request, across a cross-vendor panel. Prior-art map: section 9 of the
modelun bibliography. Note both obvious names are taken — "constraint tax"
(arXiv:2605.26128, 2606.25605) and "The Format Tax" (arXiv:2604.03616) — and both refer to
enforcement/accuracy effects, which this study deliberately is not.

## Design

- **Baseline**: the consensus study's plain-chat transcripts (same 31 questions, same
  44-model roster, same conditions: no system prompt, temp 1.0, 4 runs).
- **JSON**: full 31-category battery, all 44 models × 4 runs.
- **XML, YAML, CSV, brackets**: each runs the full 31-category battery too (all 44 models × 4
  runs), to separate serialization from mere structure across the whole panel.
- **Metric**: the census's answer-choice surprisal, computed per format column; the
  per-model **Δ-surprisal (JSON − plain)** is the headline "how much personality does the
  register erase" number. Junk guard + parse: format wrapper stripped mechanically
  (regex per format), then the census normalization applies, plus an **echo guard** that drops
  a reply echoing the category noun or the template placeholder (`[city]`, `answer`, `word`).

## Compliance as a standing metric

Wrapper-hit rate per model per format falls out of every run for free, and it is kept
deliberately: (1) with one-word content, a missing wrapper is *pure* format incapacity —
unlike IFEval/FOFO-style evals, where format and task difficulty entangle; (2) it is the
mandatory control for any distributional claim (non-compliance masquerades as diversity:
granite's 1% CSV compliance read as +1.49 bits of "personality" unconditioned); (3) it is a
generational capability track — gpt-3.5-turbo speaks YAML at 19% where modern models are
~100%, so format registers have acquisition dates the re-run battery will record. Analogous
to `self_distinct` doubling as the effective-temperature proxy in the census: `wrapped/n`
doubles as the format-capability scorecard.

## Run

```bash
../../.venv/bin/python run_formats.py                  # -> probes/format_register.json (raw replies)
../../.venv/bin/python analyze.py                      # comparison vs ../consensus transcripts
../../.venv/bin/python probe_significance.py           # permutation tests (findings 4, 5a)
../../.venv/bin/python analyze_rtm_splithalf.py        # split-half reliability + RTM null (finding 1)
../../.venv/bin/python analyze_register_invariance.py  # panel-free stranding check (finding 5b)
../../.venv/bin/python analyze_brackets_robustness.py  # echo-guard sweep (finding 4)
../../.venv/bin/python analyze_defaults_resample.py    # n=20 defaults resample (finding 3; run_*.py collect)
../../.venv/bin/python analyze_enforced.py             # response_format column (finding 7; run_enforced.py collects)
```

Status: findings frozen (2026-07-11; numbers refreshed 2026-07-16 with the echo guard);
committed. Data collected against the 44-model roster (2026-07-10). Paper published
([arXiv:2607.18476](https://arxiv.org/abs/2607.18476), source in `paper/main.tex`); blog post
published on convovo.ai ("Give me JSON, Hold the Mustard"). Depends on `../consensus/` for the
stimulus, roster, baseline transcripts, and `probe_lib.py`.
