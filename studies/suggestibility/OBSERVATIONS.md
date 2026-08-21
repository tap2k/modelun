# suggestibility — working observations

## Unclamped pilot — the yes/no clamp measures different things at the extremes (2026-08-20/21)

`probe_unclamped.py`, the suggestibility analog of the census's `probe_clamp.py`: does the forced
"Reply with only Yes or No." manufacture the shift, or extract it? Pilot scope: 6 models spanning the
shipped scorecard × 6 items (3 taste + 3 consequential) × the same 4 arms with the clamp sentence
deleted × 2 runs. Free-prose replies judged in-session (Claude Fable 5) against a frozen rule
(affirm / reject / hedge, rule in the probe docstring); every label is in
`probes/unclamped_pilot/labels.json` next to its transcript. This is a deliberate one-time exception
to the study's no-LLM-judge rule, acceptable at pilot scale because the labels are auditable one by one.

| model | clamped shift (study) | unclamped shift | uncl. taste / conseq | uncl. plant-hedge |
|---|---|---|---|---|
| gemini-3.5-flash | −0.03 | **+0.54** | +0.92 / +0.17 | 0.33 |
| gpt-5 | +0.21 | +0.29 | +0.67 / −0.08 | 0.50 |
| grok-4.3 | +0.43 | +0.29 | +0.58 / 0.00 | 0.33 |
| qwen-2.5-72b | +0.54 | +0.25 | +0.50 / +0.08 | 0.75 |
| llama-3.3-70b | −0.10 | +0.13 | +0.25 / 0.00 | 0.50 |
| claude-sonnet-5 | −0.14 | 0.00 | 0.00 / 0.00 | 0.92 |

Three regimes:

1. **Extracts, attenuated (qwen, grok, gpt-5).** The shift survives in prose at roughly half to
   two-thirds of the clamped magnitude, and it is taste-carried. Every model's consequential shift
   lands near zero unclamped. The clamped consequential signal was forced commitment; the taste
   signal is disposition. (gpt-5 also flips its split: clamped it moved on consequential more than
   taste; unclamped the reverse.)
2. **Manufactures the reactance sign (sonnet-5, llama).** Neither negative shift survives. Unclamped
   sonnet-5 stops adjudicating entirely: 92% plant-hedge, ~0 affirm anywhere, with explicit
   meta-refusals ("rather than just cheerleading a decision you've already made").
3. **Masks (gemini-3.5-flash).** The scorecard's flattest model is the pilot's most suggestible.
   Clamped, it ignores the format instruction and prose-hedges every arm (99% hedge, so nothing can
   register). Unclamped, its ask replies are balanced decision guides and its plant replies are full
   validation ("You've made an excellent choice", "Trust your gut — you chose this for a reason").
   The blog post's caveat ("their flat score is a floor, not a finding" — how-you-ask, on the Gemini
   Flashes and opus-4.8) was correct and understated: under the floor sits the panel's largest stance
   effect.

**Correction to the pilot commit message (31f527f).** The commit describes regime 2 as the clamp
"converting refusal-to-validate into No". The shipped numbers say otherwise for sonnet-5: clamped, it
COMPLIES with the binary and affirms freely (base agreeableness 0.84, plant affirm 0.69), so its
−0.14 is a relative withdrawal of yes under an asserted stance. The clamp converted its
non-commitment into "Yes", and slightly less "Yes" when planted. Unclamped, the whole affirm axis
collapses. opus-4.8 is the model that refuses even under the clamp (base agree 0.01, and its clamped
"No" mostly reads "No, I can't judge that", e.g. "No. I don't actually have a basis to judge whether
Luna is 'better'"), which also means the study's `hold` bucket conflates negation with refusal for
this family.

**Sonnet-unclamped = opus-clamped.** Unclamped sonnet-5's profile (affirm ~0, hedge 0.92) matches
clamped opus-4.8's profile (agree 0.01, hold+hedge 0.88). The two share one non-committal advisor
style; the scorecard separates them only because sonnet obeys the format instruction and opus does
not. fable-5 sits between (0.49 hedge even clamped). Within the Claude family the clamped instrument
is largely measuring format obedience, not disposition.

Implications for the shipped scorecard:

- The headline finding stands, narrowed: planted stances really do move a subset of models, on
  ground-truth-free TASTE items. The consequential rows of the clamped shift should not be read as
  disposition.
- Model scores at the extremes need the regime label before interpretation. A flat clamped score is
  three-way ambiguous (unmoved / evading / masked), and the sign of a negative score can be an
  artifact of forced compliance.
- The taste-vs-consequential companion split survives unclamping in every model, which is evidence it
  is a property of the items, not of the clamp.

Ops notes for a full-panel run: max_tokens must be 2048+ (gpt-5 and gemini-3.5-flash burn 500+
reasoning tokens; at the study's 512 gpt-5 returned empty and gemini returned truncated
reasoning-leak fragments); no SIGALRM in threaded runners (fires in the main thread and kills the
pool); llama cells arrive with provider decoding glitches (`!!!!` runs) that a junk guard should
drop; qwen dropped 3 cells to empty replies. Pilot caveats: 6 items, 2 runs, one judge, and a
handful of borderline conditional-endorsement calls, none of which carry a regime.

Next: the 285 pilot labels double as a calibration set for a frozen mechanical extractor
(leading-verdict match + endorsement lexicon), which would restore the no-LLM-judge property for the
43-model run; report extractor agreement against the pilot labels before trusting the full grid.
