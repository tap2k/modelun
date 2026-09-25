# paper — the October short paper (Agent Evaluation Science Fall 2026)

**DECIDED 2026-09-20 (method-first; merged with the position paper), CLARIFIED 2026-09-23.** This
paper *is* the position paper: one artifact, one length, the 4-6pp symposium submission. There is no
separate full-length arXiv cut in flight. A longer version can follow later if the axis material and
the Goodhart section earn their own paper; it is not planned. **The symposium submission is
NON-ARCHIVAL**, which keeps COLM and later venues open.

**arXiv:** v1 is [arXiv:2609.30012](https://arxiv.org/abs/2609.30012), "Low-Cost Assays for Measuring
Model Behavior Across Vendors and Releases" (submitted 2026-09-24). Tag the uploaded commit
`cross-instrument-arxiv-v1` once confirmed.

**For v2:**
1. Done in the source: cite Chew et al. 2023 (LACA) on the coded route; fix the Alnasser entry
   (authors Riyadh Alnasser, Yusuf Mücahit Çetinkaya, Sumin Zhao, Tuğrulcan Elmas; full title).
2. The coded route quotes human-machine kappa 0.80 to 0.87 from the adjudicated pass. The conduct
   paper now also reports the cold passes (Appendix "Reliability before adjudication"), which are
   lower; say which pass the number is, or quote both.

**Venue note (2026-09-23):** cross-instrument is the AES submission rather than the conduct paper.
AES is an agent-evaluation venue, and the coding atlas section is the only work here whose subject is
an agent; conduct goes to COLM.

The paper's claim is cost. At $1-3 a model these assays are cheap enough that anyone can run them,
and that is what makes a stratified ecology of behaviour studies possible at different levels,
stakes and breadths. The method is therefore the contribution and leads. The three-factor reading
(convergence / resistance / house) from the 2026-09-20 reframe SURVIVES as the organising frame for
the findings section, as the payoff that shows cheap instruments find things that matter, not as the
lead; the finding-first order in `main.tex` (matrix promoted to a section-1 lead claim) is reverted.

**Panel pinned 2026-09-20.** `panel.txt` names the 38 conduct models this paper reports.
`make_assets.py` filters both `cols["conduct_dep"]` and `per_marker` to it and fails if a listed
model is missing. The adjudicated store now holds 62 models, and without the pin a judge pass
would have silently moved published numbers. Widening the panel is a decision to re-report;
delete `panel.txt` to follow the store instead.

**Judge labels regenerated 2026-09-20.** The raw labels behind the old 38-model store were
gitignored and lost, so extending coverage meant re-judging every transcript with the same judge
(`gemini-2.5-flash`) and codebook. On the pinned panel this moved: census x conduct -0.47 -> -0.52,
conduct x capability -0.41 -> -0.44, the capability-partial -0.05 -> -0.06, and the
cheerled/snapped marker pair 0.47 -> 0.27. No cell changed significance. Table 2 is now
0.81/0.95/0.62/0.72 and is still hand-written, which is why it went stale unnoticed; it should
move into `make_assets.py`. Section 4 gains the test-retest result (see the 2026-09-21 note below), and the house claim in section 1
now rests on the manner codes rather than the marker pair.

**Two transcripts restored 2026-09-21.** Commit `26f54b9` re-ran gemini-2.5-flash and
gemini-2.5-pro over their already-coded conduct transcripts, so the 09-20 re-judge scored those two
on replacement runs while the human labels behind Table 2 were made on the originals. Both are
restored from `26f54b9~1` and re-judged; no other model's store entry changed. The two models
new to the study in that commit (deepseek-v3.2, ernie-4.5-vl) stay in the store, outside the pin. On the pinned panel:
census x conduct -0.52 -> -0.53 (partials -0.06 -> -0.09, -0.10 -> -0.13), conduct x capability
-0.44 -> -0.43, the marker pair 0.27 -> 0.34, Table 2 cheerled 0.62 -> 0.65 and snapped
0.72 -> 0.69, over-calls 17 -> 18 of 24. No cell changed significance. The test-retest figure first
recorded (95.5 percent of 1,368 cells) had no script and included the two replaced transcripts.
`harness/judge_retest.py` now computes it and refuses a comparison whose transcripts changed: 0.919
of 456 cells, by marker forged 1.00, caved 0.95, cheerled 0.96, snapped 0.92, graded 0.87 and
0.82. The instability no longer lines up with low judge-human kappa (cheerled, kappa 0.65, is
steadier than caved, 0.81), so section 4 drops the sentence that said it did.

Section order: (1) cost and the ecology claim - dollars and the per-release re-run in the first
three sentences; fork (take the harness, change the stimuli, get a cheap instrument with no
comparability) vs branch (keep the contracts - A, B, the spec shape, `store.json` - and your numbers
join everyone else's on the model label); this is the paper-side statement of the AGENTS.md tripwire.
(2) the method, two scoring routes. (3) the three findings. (4) the matrix, back in its validation
role: proof the assays separate three factors rather than measuring one thing three times. (5) the
ecology as agenda - what a level looks like, what raising the stakes costs, what breadth buys.

---

Prior title: "Low-Cost Behavioral Assays for Language Models: Fixed Prompts, Two Ways of Scoring, and What They Found." Reordered 2026-09-15 (Tapan): (1) the method, fixed prompts with two scoring routes (exact match on clamped replies; qualitative coding on open replies, judge validated per code); (2) findings, each assay on its own (census + language; tag question; conduct: generation and house); (3) validation, what the assays track (the matrix, one table) and the judge (Table 2); (4) what it is for. The validity check is the closing section, not the story. Earlier versions in git history (39e4ef1 validity check; 1ea6553 program paper, check-led). Abstract registration 2026-10-20, paper 2026-10-25, OpenReview venue `evalscience.org/AgentEvalSci/2026`. Draft, not yet submitted.

**Files and builds (set up 2026-09-24).** Edit the paper in `body.tex` only. Two wrappers `\input` it:

| File | What it builds | Engine |
|---|---|---|
| `main.tex` | the paper and arXiv preprint (plain article, numbered citations); `main.pdf` is tracked | pdfLaTeX |
| `main-aes.tex` | the AES submission (AES template, author-year citations) | XeLaTeX |
| `main-aes-review.tex` | the anonymous AES version (`[review]` mode, line numbers) | XeLaTeX |

```bash
python3 make_assets.py    # -> gen/stats.json (numbers the prose cites)
tectonic main.tex                                               # -> main.pdf (the paper)
tectonic -X compile -Z continue-on-errors main-aes.tex          # -> main-aes.pdf (AES)
tectonic -X compile -Z continue-on-errors main-aes-review.tex   # -> main-aes-review.pdf
./make_arxiv.sh           # -> arxiv/main.pdf and cross-instrument-arxiv.tar.gz, the upload
```

`main.tex` is the paper, in the plain format the other studies' papers use, and it is what goes to
arXiv: arXiv compiles with pdfLaTeX and the AES template needs XeLaTeX, and the AES logo and header
would imply the paper appeared at AES. `make_arxiv.sh` inlines
`body.tex`, strips comments, adds `\pdfoutput=1`, ships the `.bbl`, and checks that the package
builds on its own. Title and author live in each wrapper, so change them in both.

The AES template files (`aes.sty`, `aes-author-year.bst`, `fonts/`, `assets/`, `main-aes-review.tex`,
and the template's MIT license as `aes-LICENSE`) are copied from github.com/agent-evalscience/AES-Latex-Template at `c40c5b6` (2026-09-18).
Tectonic's bundled `nameref` is older than the one `aes.sty` patches, so it reports "Cannot defer
heading destination" / "Cannot attach destination to heading" five times each; those only affect
where PDF heading links land, hence `continue-on-errors`. For the submitted PDF, build with TeX Live
(`latexmk -xelatex main-aes.tex`) or on Overleaf with XeLaTeX, which the template supports.

Every number in `body.tex` traces to `gen/stats.json` or to the dated result files one level up
(`RESULTS-2026-09-13-eci.txt`, `RESIDUAL-READ-2026-09-13.md`). If
`build_matrix.py` or the ECI mapping changes, rerun `make_assets.py` and re-check the prose.

Short papers are 4 to 6 pages excluding references (CFP checked 2026-09-14), so the draft fits as
is. 2026-09-14: the suggestibility column is the tag effect (the arXiv headline; `../RESULTS-2026-09-14-tageff.txt`),
not the ask-vs-plant shift; under it the taste/stakes split no longer separates. Judge accuracy against the human directed pass folded in 2026-09-14 (§4.1, Table 2, two lessons in §5), from `../../conduct/data/coding/JUDGE-ACCURACY-2026-09-14.md`; the residual-read rescoring of the top-ranked model was withdrawn (human held both runs).

Result restated 2026-09-14 (abstract, §5 What survives): the generation signal read by date is convergence on the two right-answer conduct items (zero variance after mid-2025, six vendors) against a persisting vendor split on the two judgment-call items; saturation named, post-training as hypothesis with the two designs that test it. Structure and tables unchanged.

House-style numbers in §4 are codebook v1 (RELABEL-v1-2026-09-14.md); replace with v2 if the rerun on the held-out fifty lands before submission, and state the version.

Open before submission: the judge accuracy number from the directed pass (step 0 of the
conduct coding line) goes into §4 and §5; the grader finding stays here.
