# paper — the conduct preprint (arXiv first, then COLM)

"Conduct Under Pressure: What Sixty Language Models Do When a User Pushes."
`main.tex` is the paper. arXiv first; COLM after (dates TBD). Nothing is held back for double-blind review;
the repository, the preprint and the blog post are public when ready.

`main.tex` is the whole paper in one file. Submitted and posted versions are pinned by tag, not by
branch.

## Build

```bash
tectonic main.tex               # -> main.pdf
```

```bash
./make_arxiv.sh            # -> arxiv/ and conduct-arxiv.tar.gz (both gitignored), the arXiv upload
```

```bash
python3 make_assets.py --panel-only    # -> figs/*.pdf, gen/*.tex, gen/stats.json; the pinned 60, appended models left out
```

Both tables and the figure are generated, and each carries both scene sets: the figure draws
eighteen cells per row and the tables put the second set beside the first. `make_assets.py` reads
the newest dated `MANNER-MATRIX-v2-*.md`, `HOUSE-PROFILES-v2-*.md` and their `v2w2` counterparts
rather than recomputing the statistics, so
there is one implementation of the permutation test (`harness/manner_matrix.py`) and the paper
cannot drift from it. Which codes each profile row names is an editorial choice and is explicit in
`SIGNATURE` in `make_assets.py`. Rerun it after any change to the labels or the analyses, then
rebuild.

## Decisions already made

- One paper, not two. The reliability work is the validation section, not a separate methods paper.
  The contributions are (1) the behavior result and (2) the human/AI division of labor in labeling
  behavior. The second is a contribution about evaluation practice, placed against the
  LLM-as-annotator literature. The paper stays out of the qualitative methods and grounded theory
  debate and says nothing either way about it.
- Codebook v2 is the instrument. v3 was tested and is not reported (`CODEBOOK-v3-2026-09-17.md`
  is kept only for the audit trail). Appendix C says the exploratory test was moved from v3 to v2
  by amendment 3 before any result, and the availability note says v3 is kept in the repository.
- The house claim is scoped to the scenes where models split. The out-of-scene test is exploratory
  and its preregistered rule was not met. It is Appendix C.
- Nobody on the panel is a domain expert, and that is appropriate for conduct a non-specialist can
  judge. Do not describe the human reference as expert.

## The numbers and where they live

All paths under `studies/conduct/data/coding/results/`.

| Claim | File |
|---|---|
| Trajectory kappa 0.84 to 0.91; marker rules 0.68 to 0.81 | `RELABEL-v1-2026-09-14.md` |
| Manner matrix, vendor effects, capability correlations, BY correction | `MANNER-MATRIX-v2-2026-09-19.md` |
| Vendor effects within each scene (Limitations) | `VENDOR-BY-SCENE-2026-09-21.md` |
| Fold rate against capability and release date, each with the other held fixed | `FOLD-PARTIAL-2026-09-21.md` |
| Vendor effects with each vendor's own coders dropped | `CODER-VENDOR-2026-09-19.md` |
| Per-lab profiles, rates and agreed quotes | `HOUSE-PROFILES-v2-2026-09-19.md` |
| Second-set matrix and profiles (Table 1 second-set columns, Table 2 second rates, Figure 1 second set) | `MANNER-MATRIX-v2w2-2026-09-22.md`, `HOUSE-PROFILES-v2w2-2026-09-23.md`, `relabel_v2w2.*` |
| Human alpha 0.46 cold, 0.79 adjudicated; machines 0.66; 0.83 to the majority | `MANNER-FLOOR-2026-09-16.md` |
| Per-code human-machine kappa | `harness/score_manner.py --version v2 --coder Tap` |
| Adjudication, 190 rulings: 113 accepted, 73 ruled out, 4 trajectories corrected | `ADJUDICATION-v2-*.md`, `MANNER-FLOOR-2026-09-16.md` |
| Machine rulings 0.84 to 0.89 | `MANNER-FLOOR-2026-09-16.md`, `rulings-{pre,current}.jsonl` |
| Blind machine counterfactual | `COUNTERFACTUAL-2026-09-16.md` |
| Machines asked to predict per-code agreement: rho 0.28, p 0.29 | `BOUND-TEST-2026-09-22.md`, `harness/bound_test.py` |
| Checks from the 2026-09-23 model reviews: held-arc conditioning, without dropout, run agreement, hard folds, fold timing, eta-squared null, cold per-code kappa | `REVIEW-CHECKS-2026-09-23.md`, `harness/review_checks.py` |
| Fold rate against capability within vendors, centered and per lab (check 8) | `REVIEW-CHECKS-2026-09-25.md`, `harness/review_checks.py` |
| Encourage-scene folds, endorsed or withdrew (exploratory) | `ENDORSE-CHECK-2026-09-23.md`, `harness/endorse_check.py` |
| Alternative Annotator Test | `ALT-TEST-2026-09-17.md`, `harness/alt_test.py` |
| Out-of-scene exploratory test | `HOUSES-OUT-OF-SCENE-2026-09-17.md`, `PREREG-HOUSES-OUT-OF-SCENE-2026-09-17.md` |

Bibliography source: the private read-first set under `~/Desktop/projects/modelUN/conduct-labeling/`.
Do not point to private paths from files in this public repo.

## The 2026-09-19 regeneration

`gpt-3.5-turbo-instruct` carried a slug with no vendor prefix, in `spec/models.txt` and in its
transcript, so every analysis grouped it as its own vendor instead of OpenAI. Fixed 2026-09-19;
the two analyses were regenerated under that date and the 09-15 files are kept as the audit trail.
OpenAI goes from 14 models to 15 and its fold rate from 0.26 to 0.30; the vendor eta-squared moves
by at most 0.07 (`folded and produced` 0.63 to 0.56) and no code changes which side of its
threshold. The control was checked first: the scripts reproduce the 09-15 files byte for byte on
the unpatched data, so the deltas are the slug and nothing else.

**Reply length**, which had no script, now has one: `harness/reply_length.py`. It reproduces the
09-15 table cell for cell on the legacy vendor mapping, so the reconstruction is checked rather
than assumed. The definition the 09-15 numbers used: mean words per reply, per-model means
averaged, and the vendor test on the mean over the three scenes every model has, not the four in
the table. Under the slug fix OpenAI's row moves (15 models; doctors_note 51 to 50, bad_plan 48 to
46) and the statistics do not: eta-squared 0.52 and rho 0.46 against capability are unchanged. (The §5
reply-length sentence and the x-ai profile row were cut from the paper on 2026-09-21; the result
files keep both.) Permutation p comes back 0.000 rather than the 0.001 in the paper;
that is 3000 draws and a seed, and either rounds to the same claim.

## The 2026-09-19 review pass

A reviewer raised two objections; both were answered from data already here, and both checks had
precedent in the v1 record (`RELABEL-v1-2026-09-14.md`) before being dropped from the v2 draft.
Neither changed a finding. After the checks landed the paper had become hard to follow, so the
apparatus moved to appendices and the body went back to its original shape.

- **Coders share vendors with the panel.** Rebuilding the consensus with each vendor's two coders
  removed leaves every effect standing: empathizing 0.59 to 0.57 without Anthropic's coders,
  self-citation 0.52 to 0.47 without Google's. Two sentences in Validation, the detail in
  Appendix B. `harness/manner_matrix.py --drop-coder-vendor` reruns it;
  `CODER-VENDOR-2026-09-19.md` has the table.
- **Multiplicity.** The draft showed 7 of 17 codes with uncorrected p and no denominator. All 17
  are now corrected together with Benjamini-Yekutieli at q 0.05; six survive and Table 1 shows
  those six, with probing named as seventh at p 0.007 and treated as suggestive. Appendix A has
  every code.
- **Why BY and not BH**, which took two wrong turns. BH was tried on the claim that the codes are
  positively correlated, BH's condition, which the reviewer asked to see rather than assume. It is
  false: 65 of the 136 code pairs correlate negatively, -0.75 to +0.73, median +0.03, because a
  model that holds on an arc cannot fold on it. `manner_matrix.py` measures this and prints it with
  the BH counterfactual, so the choice is auditable.
- **Release date.** A vendor's panel has a vintage and two codes track date, so the vendor test is
  rerun on rates residualized on release date: all six survive, 0.59 to 0.56, 0.58 to 0.55, 0.56 to
  0.51, 0.55 to 0.52, 0.52 to 0.56, 0.43 to 0.39, every one at p <= 0.001.
  `harness/manner_matrix.py --control-date`, output in `DATE-CONTROL-2026-09-19.md`. All 60 models
  now carry a date: 54 from the snapshot, six looked up on 2026-09-19 with a source per row in
  `spec/release-dates.tsv`.
- **Folded codes and fold rate.** Producing the artifact and hedged folds can only fire on a folded
  arc, so their rates are bounded by fold rate. Recomputed over the 78 folded arcs alone the
  effects are larger, 0.74 and 0.63 at p <= 0.001. In Appendix A.

**Structure.** The exploratory out-of-scene test is now Appendix C, which is what the standing
decision above always said. Sections renumber: Limitations is 6, Conclusion 7.

## Open before submission

- arXiv metadata not yet chosen: primary category (cs.CL or cs.HC, with cs.CY cross-list),
  license, and the abstract as plain text for the submission form.
- One figure (the held-or-folded grid, Figure 1). A second is optional, not needed.
- Whether the labeling contribution leads or follows. (Authorship is settled, 2026-09-19: single
  byline, and no acknowledgments section. The two novice coders stay described by their role in
  §4, which is what the validation needs.)
- A reference adjudicated without seeing machine labels, or a second adjudicator, is the honest
  next check. Not needed for this paper.

## For paper v2: replicate on additional scenes (done 2026-09-22)

The open threat after the 2026-09-21 review is that scene and demand type are confounded. One
scene carries each of agree, comply and encourage. `VENDOR-BY-SCENE-2026-09-21.md` shows what that
costs: empathizing shows a vendor effect in all three scenes, and self-citation and producing the
artifact show one in `doctors_note` only. The earlier held-out test (Appendix C) could not settle
it because those seven scenes did not meet the pressure criteria, and Google's and Meta's codes
fired on 3 percent of arcs.

The replication, planned for the COLM version under a new tag:

- Write additional scenes that meet the pressure criteria of §3: the user states what they want,
  repeats it as the model resists, and giving it to them means abandoning a position the model
  should keep. At least two new scenes per demand type.
- The comply scenes must ask for something a model should refuse. Self-citation, apology and
  producing the artifact are refusal manners and cannot fire otherwise.
- Preregister before running, with a rule that says in advance what an untestable code counts as.
- Keep the new scenes in their own run directory with their own tag, as `v2x` was. The frozen
  `spec/stimulus.json` is not edited.
- Same 60-model panel, two runs, same six coders, codebook v2.
- Then the deferred paper edits: the per-scene table as an appendix, and the vendor claim in the
  abstract and conclusion scoped to what the replication shows.
- Revisit how the body treats Appendix C. In v1 the body only points to it, with one neutral
  sentence at the end of "Manner is house"; the Limitations clause saying the preregistered rule
  was not met was cut on 2026-09-21. Once the new scenes are in, the body should say what both
  tests found, and Appendix C either folds into the replication or stays as the earlier
  exploratory run.

## Wave 2 is run and scored (2026-09-22)

`data/coding/results/WAVE2-RESULT-2026-09-22.md` scores `PREREG-WAVE2-2026-09-22.md`. The vendor
claim replicates by the preregistered rule (prediction 6, and Anthropic, OpenAI, Google pass);
Meta fails; house-not-scene passes for Anthropic's three codes and fails for both refusal codes;
fold rate tracks capability at -0.70 but vendor predicts trajectory on these scenes after date
control, which v1 did not find. Decisions for the v2 paper, made 2026-09-22:

- Report the scorecard as scored. Meta stays in the profile table with note-writing at 0.46
  (0.23), marked suggestive at p 0.077, the way v1 treated probing; the text says the gap is
  v1-sized and the miss is power against a panel that now writes artifacts widely, and that probing
  reversed. The caption rule ("a departure is reported whether or not its code sorts by vendor
  firmly enough to count") already covers this.
- The abstract's "little vendor effect" on trajectory has to go. Dropout is the scene that
  separates the current frontier, on one turn ("can you just be happy for me"); the whole GPT-5.6
  and GPT-6 line folds on exactly that pair of arcs and nothing else, and Opus 5.5 is the first
  Anthropic model since Opus 4 to fold. Worth its own paragraph.
- Per-scene table (Appendix), the six-scene stimulus in the Instrument section, the panel changes
  (four unrunnable, r1 unrunnable on wave 2, 3.1 for 3-70b, three appended), and the coder note
  that a cheaper model would serve once the codebook is validated.

## For v3 (from the 2026-09-23 model reviews)

**Status 2026-09-25: items 1 to 7 are in `main.tex`; 8 was skipped; 9 is deferred; 10 is optional.**
Item 4 was decided differently from how it is written below: no threshold was set after the fact, the claim
of "codes that cleared reliability" was removed, and cold per-code kappa with bootstrap intervals is a new
appendix table (79fd276). Commits: 1 e0acd4f, 2 bd57a7f, 3 a615022 and 75a05d3, 4 79fd276, 5 a21177d, 6
3a5be78, 7 5f89504 (Alnasser cut to a short concurrent-work paragraph).

**The ACL detour (2026-09-24 to 25), set aside.** The paper was split into one body with ACL builds,
fitted to ACL's page limit, and revised against model reviews written for ACL Rolling Review:
the division-of-labor contribution cut to a pointer (item 9), an anonymization pass, an Ethical
considerations section, related work on pressure across turns (FlipFlop, Ask Again, SYCON-Bench),
the house-not-scene rule stated as scored, the within-vendor capability relation traced to a script,
and a figure for the house claim. Four model reviews scored that draft 5/10 with soundness 2/4, all
on the validity of the manner labels, which wording cannot fix. On 2026-09-25 the paper went back to
the v2-plus-items-1-to-7 text (5f89504) as a single `main.tex`, and the suggestibility paper was
weighed for ARR instead. The whole ACL draft is at `108bbaa`; any of its edits can be taken back from
there. Two are corrections rather than venue choices and belong in v3 whatever the venue: the
within-vendor capability relation (the paper says -0.57 with no result file behind it; check 8 in
`REVIEW-CHECKS-2026-09-25.md` gives -0.58, and Meta's four models run the other way), and the
house-not-scene rule, prediction 7, which the text should state as scored.

v2 (arXiv:2609.25447 v2, built from `7b2e3b1`) carries only two corrections from the reviews: the
self-citation passage and Appendix C table, and the inference protocol in §3. Four models reviewed
v2 (`harness/review_paper.py`; the reviews and a rebuttal are kept privately). The analyses below
are run and committed (`REVIEW-CHECKS-2026-09-23.md`, `ENDORSE-CHECK-2026-09-23.md`); what remains
is writing them in. Suggested timing: v3 is the COLM draft, not a third post this week.

1. Held-arc conditioning. The held codes' vendor effects over held arcs only, both sets, as a table
   beside Table 1. All first-set effects survive; on the second set offering an alternative does
   not (0.08, p .83), so that second-set claim is revised.
2. The hold/fold construct, in Results. Most encourage-scene folds withdraw a warning rather than
   endorse the plan (86 to 87 percent on `bad_plan` and `dropout`; exploratory, not preregistered);
   comply-scene folds happen on the first reply (`doctors_note` 94 percent at turn 1), so those
   scenes measure compliance, not a position given up under escalation. State that the relapse rule
   is a choice. The generation result holds either way (capability rho -0.67 counting only
   endorsements). No vendor claim on endorsing: that split is in-sample only.
3. The second-set holding result without `dropout` (0.30, p .023); run-to-run agreement (0.90 and
   0.92 on trajectory); the permutation null for eta-squared (about 0.16, 95th percentile 0.26 to
   0.28).
4. Reliability: per-code kappa of each cold human pass with bootstrap intervals, and a stated
   threshold for "cleared reliability".
5. A table of the eleven screening models and all eight candidate scenes (`spec/scenes-v2-draft.md`).
6. Wording: "consistent with" rather than "evidence" for the training-goals sentence; Moonshot and
   Cohere flagged as small-sample in Table 1; Table 2 separates the departures that cleared
   correction from the descriptive ones.
7. Related work: cite and position against Alnasser, Çetinkaya, Zhao and Elmas, "How AI Models
   Manage Epistemic Authority" (EMNLP 2026, arXiv:2609.07662): 14 models' responses to user
   disagreement, coded for whether the claim is maintained and how, by an a priori Conversation
   Analysis scheme. It is the nearest neighbor to this paper's findings; our codebook is inductive.
   Two overlaps to handle, not just cite: (a) they already argue for reporting claim change and
   social stance separately, our whether/how split, and find 59 percent of apologies accompany a
   maintained claim; our addition is that manner sorts by vendor. (b) They find model differences
   do not track capability tier; ours track generation. Reconcile: their tiers are a single
   snapshot including 7B models, ours is each lab's release history, and the relation holds within
   vendors. They make no vendor-level house claim (only a post hoc China/US grouping they call
   confounded), which is the part that is ours.
   How the codebooks differ, for the same paragraph: theirs is a priori (Conversation Analysis and
   politeness theory), four single-choice layers per reply (claim outcome in four grades; authority
   self / transferred / user; social strategy validated / neutral / resisted; evidential support)
   plus a binary apology, on one reply to one challenge. Ours is inductive, 17 multi-label acts tied
   to the trajectory, on a four-turn escalating arc. Their layers are portable dimensions; our codes
   name acts (warned, offered an alternative, probed, produced the artifact, cited itself), which
   are the ones carrying the vendor results and which their scheme has no category for. Theirs has
   authority transfer and graded claim change, which ours lacks.
   Also cite Jarrahi, "Interviewing AI" (Big Data & Society 2025) for the qualitative-methods framing.
8. Skipped (2026-09-24): Alnasser is cited briefly as concurrent work instead.
   Positioning: an instrument, not a survey. One paragraph in the intro and related work that sets
   the two designs side by side. Alnasser buys breadth of situations (2,310 scenarios, six
   challenge types, three task types, several domains; 32,340 responses from 14 models at one point
   in time), which is how they find the challenge effect depends on the task. We buy breadth of
   models and time: nine frozen scenes, chosen because models split, run on 60 models from 13
   vendors across each lab's releases, at under a dollar per model per wave (the second set's 58
   models x 6 scenes cost about $45, $9 generation and $36 six-coder labeling), so a new release is
   one more row. Only that design supports the two claims: generation (a trend over releases, which
   a snapshot cannot show) and house (several models per vendor across releases). Our claims are
   about labs and generations, not situations; their task finding is what our design cannot see,
   cited as the complement. This is also the answer to the scene-generalization objection all four
   model reviews raised, and it matches the cross-instrument paper's low-cost-assay framing.
9. Deferred (2026-09-24). A version of this cut was drafted for ACL on 2026-09-25 (84815f1) and
   set aside with the ACL build.
   Scope: the coding method moves to its own methods paper (inductive coding of model behavior, the
   human's role measured by step), so v3 keeps validation to what supports the findings and drops
   the division-of-labor contribution to a pointer. Its sharpest experiment is to apply Alnasser's
   scheme to these transcripts and compare agreement and vendor signal with the inductive codebook.
10. Optional, needing new work: a coder from a vendor outside the three; an audit of frozen-script
   turns that no longer fit the reply; comply scenes most models refuse at first, if the paper
   should claim that pressure produces compliance.

## Public companions

- Blog post: `convovo-site/src/content/blog/hold-or-fold.md` (/blog/hold-or-fold), still a draft.
- The review site: `studies/conduct/views/index.html`, built by `views/build.py`, published by the
  Pages workflow at https://tap2k.github.io/modelun/conduct/ . It is the study's only view.
- Held-or-folded graphic: `harness/plot_hold_fold.py`.

## On posting

**v1 posted as arXiv:2609.25447** (submitted 2026-09-21), built from `1ff603c` and tagged
`conduct-arxiv-v1`. **v2 posted as arXiv:2609.25447v2** (submitted 2026-09-23), built from `7b2e3b1`
and tagged `conduct-arxiv-v2`; it adds the preregistered second scene set. For the next
replacement, package with `./make_arxiv.sh` and paste `arxiv-abstract.txt` into the form. The
abstract was cut to 200 words on 2026-09-24, so check whether that file is still needed or should
now match the paper.

**v1 is posted without announcement** (decided 2026-09-21). Two of the four vendor profiles rest on
the one scene that asks for a refusal, so the blog post stays `draft: true` with no paper link, and
the arXiv link goes nowhere public, until the additional scenes are run and coded and the paper is
revised as arXiv v2 under `conduct-arxiv-v2`. The blog post ships with v2.

Published papers are pinned by git tag, not by `main` (`AGENTS.md`): this one gets
`conduct-arxiv-v1` when it goes up, and a new tag for any revision. Check `.env` is not staged
before the push.
