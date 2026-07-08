# Paper 2 plan — the human-comparison / diversity-metrics paper

Split from paper 1 ("The Hidden Consensus", the inter-model convergence paper) on 2026-07-07.
Paper 1 measures the model field's answer distribution *relative to itself*; paper 2 compares
it to a *human* answer distribution.

## Scope correction (2026-07-07)
An earlier draft of this plan framed paper 2 as a critique of **silicon sampling / synthetic
survey respondents**. It is not, and should not claim to be. Silicon sampling conditions *one*
model on a *distribution of demographic personas* and checks whether the answer spread matches
a real subpopulation (Argyle et al., *Out of One, Many*; Santurkar, OpinionQA). Our experiments
do something different: fixed open-ended prompts, a panel of *different* models, and *generic*
diversity instructions — no persona-conditioning, no demographic baseline, no opinion questions.
The one-word proxy is a clean instrument for **answer-distribution shape on open-ended
generation**; it is the wrong instrument for persona-conditioned population simulation. Paper 2
makes the honest, narrower claim and **explicitly disclaims silicon sampling** as a related but
untested use case (see "Future, separate" below).

## Working titles (honest, narrow)
- *Diversity Is Not Fidelity: LLM Answer Distributions Against Human Norms*
- *You Can't Prompt an LLM Field to a Human Answer Distribution*

## Thesis
On open-ended generation, the LLM field's answer distribution does not match a human
population's, this is not recoverable by prompting, and the diversity metric you would use to
check points the wrong way.

Evidence (all collected; `probes/humannorms.json`, `probes/sweep_curve.json`):
1. **Under-concentration by default.** Matched wording, the model field is more concentrated
   than the human first-response distribution in **19 of 20** categories (modal 61% vs 36%;
   effective N ≈ 2.6 vs ≈ 6). One principled exception: `country` (models avoid their home
   country; humans default to it).
2. **Un-promptable.** A 5-rung prompt-strength ladder (none → extreme anti-mode) never
   recovers the human distribution: JS-to-human floor ≈ 0.365, and that rung is the *most*
   concentrated. Persona/"be a random person" prompts backfire (72% modal, *more* stereotyped);
   only explicit anti-mode prompts spread the field, and they overshoot.
3. **Diversity is anti-fidelity (the novel hook).** Effective population size and
   JS-distance-from-human rise in lockstep. The extreme prompt hits effective N = 21 (3.5×
   human) at JS = 0.92 (near-maximal distance). The "coverage/diversity" check people would use
   to validate a synthetic panel is the *same line* as "we have left the target distribution."

## Honest calibration of contribution
- Findings 1–2 partly **replicate** known results (NoveltyBench, Wenger: models < human
  diversity; Zhang *Forcing Diffuse Distributions*: prompting doesn't fix it, the fix is
  training-side). Our value-add there is a cheap mechanical instrument + a direct human-norm
  comparison.
- Finding 3 (**diversity metrics anti-correlate with distributional fidelity, demonstrated
  across a controlled prompt ladder**) is the genuinely novel, quotable part — a cautionary
  result about using coverage/diversity as a validity check.
- Realistic size: this is a **short / workshop paper or a technical note** built around
  Finding 3, with 1–2 as support. It is *not* a flagship. Do not pour flagship effort into it.

## What paper 2 needs
1. Honest write-up around Finding 3; positioning in the **generation-diversity / mode-collapse**
   literature (NoveltyBench, Wenger, Zhang, Tevet & Berant), explicitly disclaiming silicon
   sampling. Cite paper 1 for the instrument.
2. (Optional, strengthens) A fresher/broader human baseline than the 2004 undergrad norms
   (e.g. the 2020 US cross-sectional norms) to show Findings 1–3 hold under a modern comparator.
3. The one figure is already built (`probes/sweep_curve.pdf`); F2 = the human-vs-model dumbbell.

## Future, separate (NOT paper 2)
The real silicon-sampling study is a different endeavor and a possible later project:
persona-condition a model on demographic marginals, ask **opinion** questions, and compare the
synthetic population to matched human subpopulations (OpinionQA-style). Different task, method,
and baseline; does not reuse the one-word instrument. Our diversity-is-anti-fidelity result
would be a relevant secondary finding there.

## Data already collected (committed)
- `probes/humannorms.json`, `probes/exactword.json` — human comparison, exact-wording rerun.
- `probes/persona.json`, `probes/sweep_{L1,L2,L4}.json`, `probes/sweep_curve.{json,pdf}` — the
  5-rung prompt-strength sweep and the anti-fidelity curve.
- `analyze_humancompare.py`, `analyze_sweep.py` — reproduce every number (need local VO PDF;
  derived numbers only, raw norms not redistributed).
