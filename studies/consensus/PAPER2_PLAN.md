# Paper 2 plan — the human-simulation paper

Split from paper 1 ("The Hidden Consensus", the *distributions* paper) on 2026-07-07.
Paper 1 measures the model field's own answer distribution (self-referential, no human).
Paper 2 asks whether that distribution can **simulate a human population** — and shows it
can't, in either direction.

## Working titles
- *You Can't Prompt Your Way to a Population: LLMs Under- and Over-Disperse Relative to Humans*
- *The Effective Population Size of a Language Model is Two*
- *Entropy Is Not Fidelity: Why LLMs Can't Simulate Answer Distributions*

## Thesis (the two-sided result)
There is no prompt that makes an LLM field reproduce a human population's answer distribution.
- **Unprompted, it undershoots**: the model field is far more concentrated than humans
  (modal answer 61% of the field vs 36% of human first responses; more concentrated in
  **19 of 20** matched categories; effective N ≈ 2.6 vs human ≈ 4.8).
- **Prompted for diversity, it overshoots**: a steelman anti-mode system prompt spreads the
  field past human entropy (effective N 2.6 → 7.8) — but into an **anti-modal** distribution
  (teal not blue, otter not dog, sapphire not diamond) that lands **further** from the human
  distribution (Jensen–Shannon 0.38 → 0.45; worse in 14/20).
- **Entropy is not fidelity.** Effective population size under a diversity prompt is a mirage:
  it measures spread, not match. The one dial (prompt strength) moves you from one wrong shape
  to another; neither is the population.

Stakes: this is a direct critique of the growing use of LLMs as **synthetic survey
respondents / silicon sampling / simulated populations**. The mode is recoverable; the
*distribution* is not.

## Data that already exists (committed, from paper-1 session)
- `probes/humannorms.json` — Van Overschelde et al. (2004) first-response norms vs model
  field, 20 overlapping categories (derived numbers only; raw norms not redistributed).
- `probes/exactword.json` — VO exact-wording rerun (removes the prompt-wording confound;
  collapses 3 of 4 apparent reversals; leaves `country` as the one real one).
- `probes/persona.json` — steelman persona/anti-mode system prompt, 20 cats × 39 models × 4.
- `analyze_humancompare.py` — modal share, effective-N, JS(field, human) for baseline vs
  persona. Reproduces every number above.
- Figure: `paper/figs/humannorms.pdf` (baseline human-vs-model dumbbell; regenerate for p2).

## What paper 2 still needs (the design pass that makes it robust)
1. **Prompt-strength sweep** (the headline experiment). Run a graded series of system prompts
   from neutral → mild "answer naturally" → strong "be one of many, avoid the obvious" →
   explicit "list as a diverse population would." Trace effective-N and JS(field, human) as a
   function of prompt strength. Prediction: a U-shaped JS (undershoot → best-but-still-off →
   overshoot), with **no** setting reaching the human distribution. This is the money figure.
2. **A second / fresher human baseline** to de-risk the 2004-undergrad comparator: either the
   2020 US cross-sectional norms (PMC7937767) or a small purpose-built single-response survey.
   Show the result holds under a modern baseline.
3. **More categories** — extend past the 20 VO-overlap to strengthen breadth (and to include
   opinion/preference categories closer to the silicon-sampling use case, not just concrete
   nouns).
4. **The `country` exception, examined** — the one real reversal (models avoid their home
   country; humans default to it) is a clean sub-story about embodied vs lexical prototypes;
   worth a short section, not a footnote.
5. **(Stretch) persona-conditioned distributions** — condition on demographic personas (the
   actual silicon-sampling setup) and test whether the distribution matches that subpopulation,
   not just the general one.

## Positioning (cite, sharpen, don't contradict)
- Silicon sampling / synthetic respondents: Argyle et al. *Out of One, Many*; Bisbee et al.
  (LLM survey flattening); Santurkar et al. *Whose Opinions* (already in paper 1's refs). Our
  delta: a cheap mechanical instrument, a human-norm comparator, and the **two-sided
  un-recoverability** (both under- and over-dispersion fail) — which the "personas reduce
  variance" literature hasn't framed as a prompt-strength impossibility.
- Diversity/mode-collapse: NoveltyBench, Wenger, Zhang *Forcing Diffuse Distributions*.
- Ground the instrument by citing paper 1.

## Key figures
- F1: prompt-strength sweep — effective-N and JS(field, human) vs prompt strength (the U).
- F2: baseline human-vs-model dumbbell (already built; 19/20 more concentrated).
- F3: per-category JS, baseline vs persona (shows overshoot lands further from human).

## Risks
- Salami concern: mitigated by the sweep + fresh baseline + opinion categories — genuinely a
  different question/method/literature from paper 1, not a spun-off table.
- Comparator age: mitigated by the second baseline.
- "You prompted it wrong": mitigated by the sweep spanning weak→strong, incl. an explicit
  diversity instruction as the steelman.
