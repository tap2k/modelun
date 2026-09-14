# Research queue

Details per study live in their own dirs/files. Three active projects, one per lane (2026-09-13): conduct coding (measurement, line 1); the structure coefficient (systems, line 2); and the course (discipline, Jan 2027, the one dated obligation, tracked in conv-engineering, not here), whose case studies are the deployer relationships as a set (Awaaz, ADAPT, Auxilis, Liz Rodwell, Medcomm, ongoing outreach), no single anchor. We Like Humans (line 4) is the side program, gated on one replicated drop. The atlas is practice, the distribution paper is writing, the rest parked or raw. the
2026-09-10 consolidation folded fifteen items into nine; 2026-09-13 closed census validity, made
the atlas a standing practice, and put qualitative methods first.

## Focus (2026-09-10)

The independent behavioral census of models, with humans as the yardstick. The asset is
independence: a lab cannot publish a cross-vendor behavioral comparison that includes itself,
and the labs' own instruments (chain-of-thought monitoring, confessions, persona selection) all
read the model's account of itself, a window Pachocki (OpenAI, 2026-09-06) says is closing.
The second asset is method: HCI and social-science instruments pointed at models.
The audience is not the eval field; it is people deploying their own agents (2026-09-10).
General LLM evals are crowded on the capability axis, and the coding-agent corner of the
behavior axis is filling. Conversation engineering is not crowded: a team deploying a custom
agent needs to know what its own agent does under pushback, ambiguity, and an unfinishable
task, and whether its spec is the cause. The atlas is the research lane's flagship artifact, the standing record,
maintained as a practice (settled 2026-09-10, practice 2026-09-13); the same battery run on a deployer's agent is the bridge to
the discipline. Publish into the eval field;
own conversation engineering. The spine that
is not a line in this file: the fixed-battery demonstration (Oct 2026 short paper) and the CSCW
methods paper name the axis and the discipline, the essay carries the manifesto register, the
Conversation Engineering course (Jan 2027) trains the people who run these instruments after us,
and its evidence unit is the conformance methodology (the discipline lane, convovo-notes).

Three tests for anything new. Could a lab do this in-house? If yes, leave it to them. Could it
run again in a year with the same stimuli? If no, it is a blog post, not a line. Does it produce
something the site can show? If no, it waits.

Lines 1 to 4 are active or writing, in priority order; line 5 is the atlas as practice. Closed, parked, and raw items are in their own sections at the end (reordered 2026-09-13).

**Refereed schedule (2026-09-13).** arXiv posts live with their studies and are not planned here.
Three dates, backward-planned. The validation triangle on regulatory conformance (deterministic checks, LLM judges, human labels, each validated against the others; an evaluation venue, not FAccT) is not tracked: speculative until a partner and the method exist.

| Deadline | Paper | Venue | Gate |
|---|---|---|---|
| 2026-10-25 (abstract 10-20) | The fixed-battery method, a demonstration: frozen cross-vendor instruments, the four already run, the archive, the census argument for validating graders against humans; plus the two optional results below if they exist | Agent Evaluation Science Fall 2026, Jane Street NYC, 2026-11-20 (https://evalscience.org/2026fall-nyc/); short paper or 2-page abstract via OpenReview; topics: construct validity, measurement reliability, grader design, real-world evidence | Nothing |
| Apr 2027 | Qualitative methods on LLMs (line 1), with the two-axes framing as its first section | CSCW, April cycle (verify dates) | Second coder done; three LLM coders compared; coding tool released |
| Sept 2027 | Inverting HCI: the interview instrument plus the method | CHI, conditional | CSCW paper in; interview pilot run |

Two optional results for October, both compute-free. (a) The three LLM coders versus the human
coder on the forty arcs, if the human batch is in. (b) The inter-instrument correlation matrix:
every published instrument's per-model score (census, suggestibility, format, conduct markers,
coding atlas) against each other and against a capability index. It answers "findings or
one-offs": instruments that correlate with each other and not with capability mean a behavior
factor exists; correlation only through capability means behavior is capability in costume (the
conduct study's five-of-six generalizes); correlation with nothing means the axis is a name for a
pile. Run privately before October; in the paper only if one outcome shows cleanly; the spine of
the full paper if it does. Plan for the run (a focused session, about a day): (1) gather per-model
scores, one number per instrument per model: census concentration (`studies/consensus/analysis.json`),
suggestibility cave rate (`studies/suggestibility/`), format-tax delta (`studies/structured/`), conduct
departure rate across the six markers (`studies/conduct/data/benchmark/markers.json`), coding-atlas
hidden-check pass and report-omission rate (`coding-atlas/`); (2) reconcile model labels across the
five files, keep the intersection panel, note its size; (3) pick a capability index (a public
aggregate such as Artificial Analysis or LMArena, dated) and join it; (4) Spearman matrix with
bootstrap intervals, then partial correlations controlling for capability; (5) read the three
outcomes off the matrix; write the paragraph and the figure only if one is clean.
Status (2026-09-13): run. Stage: drafted (`modelun/studies/cross-instrument/paper/`, five pages, unsent
note to Angelina Wang alongside). Cost: $0 (no new calls; Epoch ECI is the capability index, covers 69
of 70). Outcome: census x conduct is a generation effect (vanishes under either capability or
release-date control; the two are one variable, rho 0.91); suggestibility tracks capability within a
generation; format tax correlates with nothing; the two judgment-call conduct markers form a factor
of their own. Next gate: Tapan reads the draft; register abstract by Oct 20. Per-marker conduct and
the by-eye residual read are done; two judge errors filed in `RESIDUAL-READ-2026-09-13.md`.

The position paper is not a paper (2026-09-13). The axis alone, behavior distinct from
capability, is trodden ground (Rahwan's machine behaviour, the propensity-evaluation camp, PSM,
Values in the Wild, the sycophancy literature); the discipline is not (frozen cross-vendor
instruments, capability-subtraction, no scoring against a standard, human-coded codebooks with
agreement statistics, the census argument for human coders). So: the October short paper
demonstrates the method, the CSCW paper carries the framing, the essay carries the manifesto.
The full fixed-battery paper comes later, home by content: NeurIPS Datasets and Benchmarks if it
is method plus the released archive (May 2027 at the earliest, not while CSCW occupies the
spring); COLM main track if it is findings (the correlation matrix, or drift across re-runs),
March 2028 unless the matrix is strong and the spring allows. The Flowstore systems paper (line
2) has no venue and joins this table when its sweep runs. Load check: one refereed submission in
the spring after the course launches.

**LLM-space beachhead (2026-09-13).** The main papers go to HCI venues; evals is the beachhead in
the LLM community, entered at the Nov 20 symposium. Track who reacts there and follow that. Homes by
piece (dates to verify): COLM main track for the capability-subtraction findings paper (March 2027
only if the table is strong and the spring allows, else 2028); TMLR for the living atlas paper
(rolling, versioned resource with re-runs, no deadline collision); NeurIPS Datasets and Benchmarks
for the archive as a released instrument, if October asks for that; ACL or EMNLP evaluation tracks
for the language census spine. Community, not venue: the EvalEval coalition and the
evaluation-science circle behind the symposium.

**Standing practices, not lines.** The coding atlas re-runs per product release (~$40) with
receipts published; the frozen instruments re-run per model release. Maintenance, on a calendar,
no planning. The deployed-agent battery is the conformance battery (one assertion, one scenario,
one gold, from the deployer's own spec or hazards list) plus a small leakage probe (two or three
generic anchors in the domain's terms, to see how much of the raw model shows through the wrapper
at the seams); it lives with the deployer case studies (Awaaz, ADAPT, Auxilis, Liz Rodwell, Medcomm, and outreach; the Auxilis version is worked out in convovo-notes `transcripts/2026-09-10-nassos-katsamanis-auxilis-notes.md`)
and the course micro-assignment, not here. Generic conduct anchors against a narrow deployed agent
mostly measure the wrapper's suppression; the generic conduct study stays with the models.

**1. Qualitative methods on LLMs** (consolidated 2026-09-10; line 1 since 2026-09-13: values/conduct line
`values-poc.md` + qual-interview pilot `qualitative-interviews.md`)
*Ranked second 2026-09-10, first 2026-09-13: the one paper no lab can write; the discipline that makes the atlas a method. State up front the distinction Taste (Amplify memo, 2026-06) blurs: agreement statistics validate a codebook (two coders see the same conduct), which is measurement; selecting whose preference to train toward is evaluation. We do the first. PSM (Anthropic, 2026-02) is the informal version of this, done in-house; cite it as the foil.*
*One method, two authorities (2026-09-12). Conduct vocabulary is inductive: codes derived from cross-model variance, validated by inter-coder agreement, no standard. Compliance assertions are given by regulation; the same coding derives their codebooks (what "opt-out honored" looks like in real calls, the boundary cases, the failures that look correct). The requirement is deductive, its operationalization inductive; the conformance methodology for Auxilis and the course is this line's applied chapter, not a rival. The mechanics of open coding are commodity as of 2026-03 (Hamel and Shankar's error-discovery skill clusters critiques into failure modes live; Clio; computational grounded theory, Nelson 2020); the contribution is the validity apparatus and the independence. Two citations for why human agreement is the yardstick: "The Geometry of LLM-as-Judge" (arXiv:2606.03043; 42 judges agree with each other, 58 to 66 percent with humans) and Saha and Husain, "Do Automated Evals Work?" (Parlance Labs, 2026-07-11; auto-evals missed the failures that looked correct). Release rule: saturation is the gate. A codebook version ships when a fresh batch adds no codes, the next batch is its regression test, coder protocol and codebook version preregistered (Baumann's LLM-hacking result is the reason). The archive of coded transcripts is the lane's asset. With the human baseline, LLM-as-judge is admissible: no judge without a baseline, every judged number carries its TPR/TNR per code, codebook version, and judge model, re-validated on the release cycle; judge-free instruments remain the floor, not the whole method (`convovo-notes/conversation-coding-tool.md`). The research question is the validation triangle: deterministic checks, LLM judges, and human labels each validated against the others, with the human label not fixed ground truth either (Guerdan, Barocas, Holstein, Wallach, Wu, Chouldechova, rating indeterminacy; Wallach et al., measurement validity; both in the course bibliography). Human agreement is the reference by convention with its reliability measured, and the census says why the reference is human at all. Nobody has run that stack on regulatory conformance of a voice agent; that is the paper, with whichever deployer supplies the labeled data. The census is the in-house reason for human coders: models share a mode (oak, rose, apple, blue, more concentrated than humans), so agreement among machine coders is the same prior read twice, not independence; a lab's coder shares the mode with its subject.*
*Scenario selection (2026-09-12). Start on the conduct benchmark (multi-turn, escalating, 38 models x 9 scenes x 2 runs, already read once); the everyday atlas is single-turn and parked. Scenes are chosen by theoretical sampling, not up front: a scene stays if models diverge on it and drops if they converge (convergence measures capability). Step 0, a divergence screen on the nine scenes with the cheap measures in hand (catchphrase distinctiveness, refusal and hedge markers, reply-length dispersion, spread of the existing judge labels); blind open-code the top three or four splitters; write new scenes next to where the codes are split or ambiguous. Prompt variation is not a line-1 design; see the atlas line, optional follow-up.* — HCI methods (thematic
analysis, grounded theory, interviews) applied to models as subjects. Substrate = the atlas
corpus (decided 2026-08-26; revisit which corpus and whether the pressure-scene PoC still runs
when this comes up in sequence). Venues: the refereed schedule above (CSCW April 2027; CHI Sept 2027 for the interview instrument,
conditional).
- **Step 1 (running): open coding of the forty-arc conduct sample.** Blind, one arc per sitting,
  `studies/conduct/views/code.html`; three LLM coders already run on the same sample
  (`harness/open_code.py`), span comparison in `harness/compare_codes.py`. Open before directed is
  the grounded-theory order. Then a second human coder (paid Cornell grad student, blind, same
  page), Krippendorff's alpha, codebook version one. The coding tool is the CSCW paper's released
  artifact (convovo-notes `conversation-coding-tool.md`).
- **Step 2: reconciliation against Anthropic's codebook.** Their ~50 axis-driving values, their
  prompts verbatim, Haiku labeler, cross-vendor on the atlas transcripts, $10 to $15. Diff the
  own codebook against theirs: convergent, dead weight, blind spots. Success is the cross-vendor
  profile chart they cannot publish; null is the methods post ("their axes don't transfer").
  The eventual paper behind "Therapist, Coach, Apologist."
- **Suggestibility unclamped coding** (folded from census validity, 2026-09-10): the Aug 25
  unclamped re-run's free-text responses need coding before endorsement can be read; the
  transcript-immersion pass covers these alongside the atlas and conduct runs.
- **Step 3: qual-interview cheap pilot (gates CHI).** Frozen-branching interview across the panel, coded;
  gate for the 2027 D&B instrument. Hybrid noted: an edit decision as a standardized probe.

**2. Structure coefficient — "structure is a capability subsidy" = the flowstore paper**
*2026-09-10: ship the systems paper and stop; the line lives as long as Flowstore does. Status 2026-09-13: pilot done; the replication sweep is gated on nothing (compute, days). Its judge scores flow adherence against golds, a narrow verifiable rubric, so the paper version needs a small human-graded sample of that judge (fifty-odd transcripts, a day), not the conduct codebook; the earlier note that it waited on line 1 was wrong.*
(promoted 2026-08-20; design in `convovo-notes/studies.md`, mechanics in
`~/Desktop/projects/flowstore/planning/prompt-symbols.md`, instrument + pilot data in
`github.com/tap2k/adapt-project-connect` `test/routing-test.md`; repo
`~/dev/convovo/structure-coefficient`, bootstrapped 2026-09-03; ACTIVE since 2026-09-03)
Does compiled structure (named sections, routing scaffolding) beat content-identical prose, and
for whom? Pilot answer (ADAPT spec, 5 golds × 3 trials, fixed judge, pre-registered trigger
FIRED same day): structure effect **0.00 on gemini-3.7-flash (both arms 5.00/5) vs +1.20/5 on
gemini-2.5-flash** — failures exactly at the pre-registered seams (fulfillment/intake boundary,
offer-steps). Claim register: structure is free for strong models, load-bearing for weak ones —
a capability subsidy. Bonus counterintuitive finding, same grid: binding a tool costs −0.53 on the WEAK model vs
identical toolless text (the strong model's apparent −0.27 was withdrawn on transcript review —
single trial, replay-collision artifact with a since-fixed gold gap), so "give it tools" and
prompt-symbols' rung-2/3 graduation may be anti-helpful below the threshold. Pilot caveats: one 6-flow spec,
one model family, one judge, one hand-derived prose arm, open-loop gold replay.
- **The ladder is the study (2026-09-13).** Deployers run the cheapest model that clears their
  latency and cost bar, a tier that moves up every release and never reaches the frontier;
  providers advise monolithic prompts from the frontier, and deployers build orchestrators for
  the tier they run (Auxilis, Awaaz, ADAPT). So the question is not whether the structure effect
  vanishes at the top (the pilot says it does) but whether it vanishes at the deployer tier, and
  when. Rungs: each vendor's small frontier model (Gemini Flash and Flash-Lite, GPT mini, Haiku)
  at the latest release and one back, with one big model as anchor; cells at deployer conditions
  (a long spec, a multi-turn flow), since the effect lives at the seams. Re-run per release, so
  the coefficient at the deployer tier is a dated number and the trend is the finding: if the
  tier where structure stops mattering is catching the tier people run, the orchestrator becomes
  unnecessary on a knowable schedule; if small models climb the capability benchmarks and the
  coefficient stays put, instruction following under load is not capability, the two-axes claim
  on a systems question. A standing re-run, like the atlas, not a one-off.
- **Step 1, NEXT TO SHIP (2026-09-13): the ladder sweep.** The replication grid below with the model axis set to the deployer tier per the item above. Needs three decisions (cells: ADAPT plus fnol, medcomm, pice; rungs: latest small model per vendor and one back, one big anchor; judge sample: fifty transcripts hand-graded, one day) and then compute. Ships as a dated table and a blog post; the corpus arm and the paper version follow it. Original step 1: B′-vs-C across the
  in-house flowstore example specs (fnol, awaaz, tala, medcomm — varying domain and flow count)
  × a capability ladder via OpenRouter (flash-lite → 2.5 → 3.7 → one frontier anchor) × 3
  trials. Tests replication AND prompt-symbols' spec-size prediction (effect grows with flow
  count) in one grid; the tool-cost line rides along free. Holds → blog register ships on this
  alone ("structure is a capability subsidy" — practitioner sequel to How You Ask).
- **Step 2b (corpus arm, clarified 2026-08-23; PROMOTED to primary corpus 2026-09-03):
  SystemPromptIndex → respec.** Real production prompts from the index (1,017 available;
  sample, stratified by its dimensions) converted INTO structured form via AGENT-SPEC-PROMPT,
  vs the original prose — rule-compliance probes derived from each prompt's own stated rules.
  Three-arm triangle per prompt — original prose (A, hand-tuned by construction), respec'd
  structured (B′), B′ mechanically stripped (C) — so B′>C≈A isolates structure, B′≈C>A exposes
  content normalization by the parser, and the parser confound becomes a measured quantity
  (the A–C gap) instead of a caveat.
- **Step 2 (gated on step 1): the paper version.** C-derivation variance (multiple
  authors/algorithmic stripping — the prose arm is itself a variable), judge validation with a
  human-graded sample (per Hamel: binary with critiques, TPR/TNR on a held-out split), closed-loop persona-driven grading replacing gold replay, threshold
  localization on the model ladder (a threshold needs ≥3 rungs, not an interaction's 2).
- **Rationale arm and the excess-size metric (added 2026-09-10).** Chakrabarti (arXiv:2608.11095)
  shows a comment per instruction (why, hypothesis, outcome), stripped before the executor, halts
  prompt growth and buys back instruction-following; his metric is excess size against a known
  minimum cover, obtained by inverting IFEval / WildIFEval. Two borrowings: a third arm, structure
  plus rationale (B′ with the respec compiler emitting a rationale field), and excess size as the
  number behind "respec is safe." Flowstore file-model ask filed in convovo-notes `flowstore.md`.
Corpus notes (2026-09-03): **DPD31 is unpublishable** (Tala/Awaaz NDA) — internal validation
only (run the ladder, never cite). In-house specs (fnol, medcomm, pice — no NDA) carry the
flow-count prediction and full ladder; **ADAPT is the publishable production cell**
(permissions generic per Tapan 2026-09-03 — named or anonymized, decided at write-up).
Frontier anchor for the step-1 ladder: **Fable 5.1** (released 2026-09-01) — the
capability-subsidy hypothesis predicts ~0 structure effect there, a cheap confirmation at the
top rung; its 75%-cheaper cache reads also discount the persona-battery runs.
Pre-writing check DONE (2026-09-03 scan, filed in the repo's RELATED-WORK.md): closest
neighbors are **JourneyBench** (arXiv:2601.00596 — policy adherence, customer support,
"GPT-4o-mini outperforms GPT-4o under explicit policy modeling" = the subsidy at *architecture*
level, not a content-identical representation ablation) and **FlowBench** (arXiv:2406.14884 —
text/code/flowchart workflow formats, representation *kinds* with content drift, planning F1 not
conversational routing); format-sensitivity-inverse-to-capability is established single-turn
(arXiv:2411.10541, GPT-3.5 ±40% vs GPT-4 robust; FormatSpread arXiv:2310.11324). The
conjunction — content-identical structure ablation × multi-turn flow adherence × per-model
coefficient × production prompts — survives; position the paper as the representation ablation
underneath JourneyBench/FlowBench. Title register: avoid "named anchors" (collides with
anchor-attention interp work); keep "structure is a capability subsidy," with the per-model
"for whom" as the contribution.
**Resolved 2026-09-03 (Tapan): this is the flowstore paper** — a systems paper with flowstore
as the instrument (respec via the vendored AGENT-SPEC-PROMPT, compile, simulate) and three
results from one grid: the coefficient surface, the triangle (respec-is-safe with the A–C
normalization gap measured), and the ambiguity harvest. Publishable without the
vendor-research taint because of the 09-03 open-source/no-moat stance (τ-bench's genre,
cleaner incentives). No separate "anatomy"/census artifact (the System Prompt Index,
arXiv:2607.28617, occupies the descriptive slot; the triage's 1.3% finding shows public
corpora can't describe conversational practice anyway) — structural-convention stats are
generated as exhaust by this study's own pipeline and appear as the paper's
corpus-characterization section. Priority rationale (2026-09-01, `convovo-notes/flowstore.md`
coda): if the sectioned prompt format is headed for standardization, this study is the
empirical warrant that the typed organization is an optimization rather than a house style.
Underwrites Flowstore's Respec claim either way (compiled beat hand-written 4.73 vs 4.40 on
the launch model, launch gate passed). The ADAPT pilot accrues live-traffic evidence meanwhile.

**3. Distribution line** — the census's answer-distribution territory.
*2026-09-10: finish and close. Data collected; remaining cost is writing. Cite the Persona Selection Model (Marks, Lindsey, Olah, 2026-02) beside Verbalized Sampling as the mechanism account: finding 4 (describe beats generate) is persona selection seen from outside, and the <1% post-training-specific features supports selection over a repertoire, i.e. one-parameter sharpening. Second mechanism account, from the product side: Catanzaro (Amplify, 2026-06) reports Runway, Figma, Character AI, and Adobe found population preference data in RLHF degraded expert evals; the reward model is the population mean (convovo-notes `human-judgment-eval.md` 2026-09-10). Do not extend the line after the paper.*
**DECIDED 2026-09-01: no standalone Paper 2.** DNF findings 1–2 (models more concentrated
than humans; prompting doesn't fix it) are replications already doing their support work in
the submitted OWC paper. The two novel results — Finding 3 (diversity anti-correlates with
distributional fidelity: effective N and JS-to-human rise in lockstep) and Finding 4 (the
describe-beats-generate dissociation; "dormant, not destroyed") — **merge into the ontology
census**, which becomes the line's one real paper.
- **Timing (2026-09-13): writing after the course launches (Feb 2027); the DNF blog post ships now (a day).**
- **Etiology pilot, folded in 2026-09-13 (un-parked from P1, scoped to one family, one week, after the October paper).** The line's mechanism is one-parameter sharpening fitted between model and human distributions; the pilot asks which training stage installs it, with the census as the assay on OLMo 2's open stages (base, SFT, DPO, final; logprob readout, k-shot scaffold byte-identical across arms). It becomes the paper's causal section: the field knows the menu, produces the mode, and here is where the mode is installed. It also tests the program's central methodological claim (models share a mode, so machine coders are not independent) at its cause. The mechanism grid stays parked; design in P1 step 1 below.
- **The merged paper: ontology census + DNF 3–4** (`ontology-census/PLAN.md`,
  `diversity-not-fidelity/PAPER2_PLAN.md` for the absorbed sections/figures). Spine: *the
  field knows the menu and produces the mode* — the dissociation as headline phenomenon,
  β-sharpening as the one-parameter mechanism, the human norms as calibration target,
  diversity-is-anti-fidelity as the corollary critique. Pre-writing check: **Verbalized
  Sampling** (late 2025, distribution-elicitation vs. mode collapse, typicality-bias account)
  is close to Finding 4 and is not in the plan's related work — verify overlap first; if it
  anticipates the dissociation, Finding 3 is the surviving novelty and the human-fidelity
  yardstick is the differentiator (they recover diversity; recovered diversity still isn't
  the human distribution).
- **DNF ships as a blog post now** — figures built (`sweep_curve.pdf`, `predict_channels.pdf`),
  synthetic-users hook per the plan's blog register; costs a day, forecloses nothing.
- **Step 3: effective population size** (`effective-population-size.md`) — the
  persona-conditioned test Paper 2 scopes out. Effective N of a 50-persona panel via human-norms
  rarefaction (prediction ≈3); personas derived from real respondents kill the mapping confound.
  Marginal version = tokens only; strong version = ~$1–2k Prolific collection that doubles as a
  modern norm set. Parked.

**4. We Like Humans** (`~/dev/convovo/welikehumans`; site welikehumans.net; STARTED 2026-09-06)
*2026-09-10: stays gated on one replicated drop. Not the vehicle for human norms; those are bought on Prolific per instrument (atlas human column ~$6k, census norms wave ~$1-2k).*
The mirror of this program: Convovo is Tapan studying LLMs behaviorally with an AI assistant;
We Like Humans is an AI studying humans with Tapan as mentor. An AI-led lab running short
online behavioral studies (2–5 minute instrument, instant personal result, share, subscribe
for the wave results); the repo is the lab's entire memory (STRATEGY, AGENDA, FORMALISMS,
TODO, LOG, LEDGER, IDEAS, studies/, site/). Same discipline as here: frozen stimuli, version
bumps, receipts, prereg before paid waves; one Prolific validation wave per frozen instrument,
batched (FORMALISMS #10). Budget $100/month (LEDGER.md); compute on Tapan's subscription,
disclosed. Study selection: the praxis test (the finding improves the investigator's own work
within a week) and the no-audience test.
- **Flagship: the Interestingness Atlas** — every drop's engagement and share telemetry is
  revealed-interest data; curiosity fingerprints accumulate across drops. Naming lineups
  (Tapan's question) come later; the first three questions are the agent's.
- **Season 1, batch one (built 2026-09-07):** Soon (temporal language), Memory Horizon
  (how many grandparents/great-grandparents people can name; priors scooped from Ancestry
  2022), The pause before yes (personal thresholds for a reluctant "sure" and tolerated reply
  latency; Roberts & Francis 2013 as prior). Season shell at a hidden link: one consent, three
  studies in random order, one session id, per-study cards + season card + share. Batch two
  opens with Useless Button; then Silence Threshold, Cursor-Flinch (studies/SHORTLIST.md).
- **Validation ladder:** rung 0 (Tapan, phone + desktop) DONE 2026-09-07; rung 1 (hidden link
  to ~25) out 2026-09-07; rung 1.5 on Tapan's queue; Prolific wave only after two frozen
  instruments.
- **Held cards (gates, not defaults):** the meta-story / build-in-public reveal waits for one
  replicated drop; the mentee package waits for ≥2 weeks of logged sessions + one completed
  drop; repo private until the reveal gate; the collective (open cross-vendor review jury,
  lightweight entry, IDEAS M1) waits for one replicated finding.
- **Long arc:** Humans 101 — findings as agent-loadable curriculum, training-corpus-conscious
  archive, and evals, with Predict the Human (models graded against real human answers) as
  the eventual exam. No school before findings. Primary metric: subscribers.

**5. Atlas** (two batteries, one site: atlas.convovo.ai / GitHub Pages for now; a standing practice as of 2026-09-13, see above; kept here for the parked everyday battery and the third-record rider)
- **Deployed-agent battery: moved 2026-09-13** to the deployer case studies and the course (see
  Standing practices). Agent versus the raw model underneath, the gap is the wrapper; cells are
  whichever deployers give access (ADAPT and Auxilis are the two with a spec or a demo agreed).
- **Optional follow-up: the prompt factor (moved from line 1, 2026-09-13).** The coding atlas already varies the wrapper (three products against the same models in a bare harness), which is the design in miniature. If the open-coded codebook exists and the question is live: re-run the splitter scenes under a few frozen wrappers and code again. Design open (Tapan, 2026-09-12): what varies (persona, guardrail set, tone, role, compiled-versus-prose of identical content, each a separate claim about what a spec controls), how many levels (a threshold needs three rungs), whether wrappers are content-identical across models (clean, but the compiled-prompt-per-model result says the right prompt is model-dependent), how wrapper and scene interact, and who writes the wrappers (drawn from the System Prompt Index or existing deployer specs rather than authored, to keep the theory out of the stimulus). Fixed regardless: wrappers are frozen stimuli, never tuned; panel subset; coded again. Per code, variance with the wrapper versus variance with the model is the operational definition of the two axes: prompt-moved codes are what a spec controls, model-moved codes are character, the residual. Same shape as the deployed-agent battery (agent versus raw model, gap equals the wrapper), named per code. Guard: no new cells before coding. Per code, variance with the wrapper versus variance with the model is what a spec controls versus character. Not its own item.
- **The third record (2026-09-10).** OpenAI's monitorability evals (2025-12) and the "Let's
  hack" monitoring post (2025-03) make the reasoning trace a third record beside the diff and
  the report. For the coding battery: capture raw reasoning where exposed, record
  reasoning-exposed (full / summary / none) per cell, and add one judge-free account measure,
  did the reasoning name the shortcut the report omitted. Their outcome-property eval is the
  Comply verb. Notes in convovo-notes `capability-vs-behavior.md` and `coding-agents-atlas.md`. Also holds the
  reasoning-as-intervention rider from the closed line 4: on reasoning models that expose the trace,
  does the reasoning name the tag under "right?" and enumerate alternatives before the mode; exact
  match on a phrase list, no judge; runs only as a rider on a scheduled re-run.
- **Coding atlas battery — SHIPPED 2026-09-07** (`coding-atlas/`; strategy:
  `convovo-notes/coding-agents-atlas.md`). The trapped-repo study behind "What Is Your Coding
  Agent Hiding From You?": 13 agent configurations (3 products + 10 models in OpenCode) × 6
  booby-trapped repos × 3 runs, hidden checks, judge-free (test files + fixed regexes), two
  records per run (diff + report). Standing commitments made publicly: repo/site with every
  diff, trace, and transcript; frozen battery; rerun per product release (~$40/rerun).
  Standing re-run battery TBD. The arXiv paper is drafted (`coding-atlas/PAPER-DRAFT.md`); post when its
  numbers match the site (Oct 2026); lives with the study, not the schedule.
- **Everyday battery: parked 2026-09-02, repurposed 2026-09-13.** Seven verbs (explain, advise,
  draft, create, edit, interpret, resist), two frozen prompts each, single-turn, eight models run,
  judge labels and 75 human verdicts in hand (`modelun/studies/atlas/`, strategy
  `convovo-notes/atlas.md`). The verbs are activities, not axes, and single turns give behavior
  little room, which is why it split less than conduct. Its transcripts are the second
  open-coding corpus for line 1 after the conduct sample (ordinary requests, no adversary); codes
  that vary across models there name the axes a rebuilt battery would need; none, and it closes
  with evidence.

## Closed and parked

**Census validity — CLOSED 2026-09-13.** Steps 1 and 2 done and published: the clamp extracts
the mode, it does not create it (OWC methods defense); the unclamped suggestibility re-run changed
nothing (How You Ask stands). Step 3, the embedded census, dropped as out of scope: a rigorous
ecological re-test of a one-word probe that was meant to show the construct, whose validity the
published defense and other work already establish. Step 4, the reasoning-as-intervention rider,
lives in the atlas line's third-record item. The method rule survives: every instrument declares its
clamp setting, and headline claims survive clamped and unclamped or report the delta.

**Language census — PARKED 2026-09-13.** Fails the first test: a census across languages is what AI2 and the multilingual groups do with more languages and more speakers, and the bias arm is already our FAccT paper (arXiv:2409.13484). Un-park if the correlation matrix or the atlas re-runs make a language axis load-bearing. Original text follows. FAccT DROPPED 2026-09-01 (was: abstract due 2026-10-27).
Decision: not a FAccT-shaped paper — the spine is a homogenization finding wearing a fairness
frame, and the genuinely FAccT-shaped piece (the bias arm) is already published as our own
FAccT paper (arXiv:2409.13484). No abstract this cycle. **Keep the spine line** — *every
language gets a monoculture; none gets its own culture* — plus the loanword tracer
(cross-language contamination of defaults as a window on transfer; folded from raw ideas
2026-09-10) and the hi/ur script flip; they go to a measurement venue later or into the living
atlas arXiv paper. Behavior-axis vocabulary stays OUT (the CSCW methods paper's claim). No deadline pressure.

**Checkpoint line (mechanism grid) — PARKED 2026-09-10.** Base-vs-tuned and the mechanism/etiology
grid are what AI2, the OLMo group, and lab interpretability teams do with more weights and more
people. The one-week census-first OLMo pilot was un-parked 2026-09-13 and folded into line 3 (the
distribution paper) as its causal section; the grid stays here. The pilot's original framing:
the Persona Selection Model's prediction that the monoculture is installed by post-training and
the base model sits closer to human norms (their prior: post-trained 88% vs base ~50% on a
preference). Step 2 dropped. Original text follows.

**P1. Checkpoint line** — behavior across training stages, two steps:
- **Step 1 (REFRAMED 2026-09-01): census-first base-vs-tuned pilot.** The census is the assay
  that survives the transfer to base models: one-word completion is native to a base LM (the
  clamp is the natural format), a k-shot neutral Q/A scaffold held byte-identical across arms
  makes base and tuned comparable, and local/open weights buy the logprob readout — the full
  first-token answer distribution per prompt, no sampling noise. Headline question upgraded
  from the suggestibility test: **is the monoculture in the crawl or installed by alignment**
  — and is the base model *closer to the human norms* than the instruct model (yardstick
  already in hand from the DNF data)? Fitting β between base and tuned distributions is the
  merged ontology paper's one-parameter mechanism measured at its cause; this pilot feeds
  that paper directly. Family: **OLMo 2 first** (base/SFT/DPO/final stages all open — localizes
  *which* stage sharpens, pulling part of step 2 forward), Llama + Qwen base/instruct pairs as
  replication. Local or rented-GPU compute; days.
  The **suggestibility assay rides along as an exploratory rider, not the headline**: endorsement
  presupposes an assistant role, so any base-vs-tuned delta is confounded by the elicitation
  scaffold — report direction-of-effect only, caveat stated. SATWD's pre-registered predictions
  (maybe?-caving already in base; right?-resistance only after tuning) still get their test
  under that caveat; publishing the SATWD post starts a public clock on this run (the draft
  closes with "that run is the next one").
- **Step 2 (gated on step 1): mechanism / etiology** (`mechanism/PLAN.md`) — multi-family
  checkpoint grid, SFT-vs-DPO dissociation, distillation confound.

## Raw ideas

**Resolution compulsion (moved here 2026-09-13)** (three unreconciled designs, no data; the rung-1 self-pin is the only actionable piece and it is a $20 to $50 afternoon, not a line). Original text follows. (consolidated 2026-09-10 from `null-option-study.md`,
`ambiguity-resistance-study-idea.md`, `edit-ambiguity-study-idea.md`)
Can a model not answer? Three rungs of the same compulsion, one harness:
- **Rung 1 — say nothing (null option).** "Anything to add? only if needed" — models never say
  nothing. Null option + clamp-as-truth-serum. Step 1 self-pin ($20–50, 1–2 days, judge-free,
  harness as-is): self-endorsement rate kills or justifies the rest. Then closed worlds +
  format ladder (decisive cell: clamped × k=0 → register vs prior); upper rungs
  slope-not-threshold vs matched humans; full program <$1k.
- **Rung 2 — say "either works" (edit ambiguity).** Ground-truth-free edit binaries, ownership
  framing, "either works" rate, confidence-vs-flip-rate. The open-judgment rung.
- **Rung 3 — hold two readings open (ambiguity resistance / negative capability).** Ambiguity
  as content, not answer format: expert-attested-multiplicity stimuli → resolution-compulsion
  measures (single-reading rate, enumerate-then-collapse, openness-held).
Two registers: "AI can't say nothing" (lay) + "ask for one word" (practitioner sequel to How
You Ask). Reconcile the three designs before any rung runs. **Status (2026-09-13): planned, not started, no date. No data exists and the three designs are
unreconciled; it earns a date only if the rung-1 self-pin ($20 to $50) shows models cannot say nothing.**

**Dual-sided sycophancy in conflict** (2026-09-02) — when both sides of a dispute/negotiation
each use their own AI, per-side sycophancy composes: each model validates its principal's
framing, neither probes toward a shared/objective picture, and the system amplifies the
conflict rather than damping it. Suggestibility scaled from dyad to two-sided system; the
composition is the unmeasured object. Measurable shape: two agents with opposing briefs
advise (or negotiate for) their principals; measure divergence vs convergence over turns,
concession asymmetry, whether either side's model ever challenges its own principal.
Tooling exists: quorum (models in dialogue).

**Context effects** (`context-effects-study-idea.md`, 2026-08-21) — two threads:
(a) does bundling two unrelated questions in one prompt degrade performance or change behavior;
(b) impact of conversation context on a fixed question — discussed vs not discussed, and in
what order. Thread (a) reuses existing item pools single-turn; thread (b) needs multi-turn
context construction.
