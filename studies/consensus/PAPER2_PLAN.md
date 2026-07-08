# Paper 2 plan — the human-simulation paper

Split from paper 1 ("The Hidden Consensus", the *distributions* paper) on 2026-07-07.
Paper 1 measures the model field's own answer distribution (self-referential, no human).
Paper 2 asks whether that distribution can **simulate a human population** — and shows it
can't, in either direction.

## Working titles
- *You Can't Prompt Your Way to a Population: LLMs Under- and Over-Disperse Relative to Humans*
- *The Effective Population Size of a Language Model is Two*
- *Entropy Is Not Fidelity: Why LLMs Can't Simulate Answer Distributions*

## Thesis (sharpened by the completed prompt-strength sweep)
There is no prompt that makes an LLM field reproduce a human population's answer distribution,
and **the standard diversity/coverage metric points the wrong way.**

Prompt-strength sweep (5 rungs × 20 categories × 39 models; `probes/sweep_curve.json`):

| rung | prompt | eff-N | JS→human | modal |
|---|---|---|---|---|
| L0 | none (baseline) | 2.62 | 0.377 | 61% |
| L1 | "answer naturally" | 2.49 | 0.380 | 63% |
| L2 | "be a random person, first thing to mind" | **1.97** | 0.365 | **72%** |
| L3 | steelman anti-mode | 7.80 | 0.448 | 30% |
| L4 | extreme "give an unusual answer" | **21.16** | **0.922** | 19% |
| human | — | 6.01 | 0 | 36% |

Three findings:
1. **Diversity is anti-fidelity.** Effective population size and JS-distance-from-human rise
   in *lockstep*. L4 hits effective N = 21 (3.5× human) at JS = 0.92 (near-maximal distance).
   The metric you'd use to claim "our synthetic panel covers the population" is the same line
   as "we have left the population." A coverage/diversity check is worse than uninformative.
2. **Humanizing prompts backfire.** "Be a random member of the public" (L2) makes the field
   *more* stereotyped than no prompt at all (72% modal, eff-N 1.97) — it reaches harder for
   the prototype. Mild "answer naturally" (L1) does nothing.
3. **No rung recovers the distribution.** The JS floor across all prompt strengths is ~0.365
   (L2), barely below baseline and achieved by *increasing* concentration. Persona prompts
   collapse harder; diversity prompts explode into noise; neither is the population.

Stakes: a direct critique of LLMs as **synthetic survey respondents / silicon sampling /
simulated populations** — and specifically of validating them with diversity/coverage metrics.
The mode is recoverable; the *distribution* is not, at any prompt strength.

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
0. ~~**Prompt-strength sweep** (the headline experiment)~~ — **DONE** (2026-07-07). The money
   figure exists (`probes/sweep_curve.pdf`): eff-N and JS-to-human rise in lockstep; no rung
   recovers the distribution. The result came out *stronger* than the predicted U (it's a
   diversity-is-anti-fidelity lockstep, not a U with a sweet spot). Remaining items below.
1. **A second / fresher human baseline** to de-risk the 2004-undergrad comparator: either the
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
