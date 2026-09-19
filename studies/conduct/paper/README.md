# paper — the conduct preprint (arXiv first, then FAccT 2027)

"Conduct Under Pressure: What Sixty Language Models Do When a User Pushes."
`main.tex` is the paper. arXiv first; FAccT 2027 after (abstract 2026-10-27, paper 2026-11-03,
reviews 12-22, rebuttal 2027-01-28, decision 03-23). Nothing is held back for double-blind review;
the repository, the preprint and the blog post are public when ready.

`main.tex` is the only source. The markdown draft it was ported from on 2026-09-19 was removed the
same day; it is in git at `875a010` if a passage needs recovering.

## Build

```bash
tectonic main.tex         # -> main.pdf
```

```bash
python3 make_assets.py    # -> figs/hold_fold.pdf, gen/*.tex, gen/stats.json
```

Both tables and the figure are generated. `make_assets.py` reads the newest dated
`MANNER-MATRIX-v2-*.md` and `HOUSE-PROFILES-v2-*.md` rather than recomputing the statistics, so
there is one implementation of the permutation test (`harness/manner_matrix.py`) and the paper
cannot drift from it. Which codes each profile row names is an editorial choice and is explicit in
`SIGNATURE` in `make_assets.py`. Rerun it after any change to the labels or the analyses, then
rebuild.

## Decisions already made

- One paper, not two. The reliability work is the validation section, not a separate methods paper.
  The contributions are (1) the behavior result and (2) the role of humans in labeling behavior,
  stated as this study's finding with its limits, not as a claim about qualitative methodology.
- Codebook v2 is the instrument. v3 was tested and is not reported (`CODEBOOK-v3-2026-09-17.md`
  is kept only for the audit trail). §3 says so, and §6 says the exploratory test was moved from
  v3 to v2 by amendment 3 before any result.
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
| Vendor effects with each vendor's own coders dropped | `CODER-VENDOR-2026-09-19.md` |
| Per-lab profiles, rates and agreed quotes | `HOUSE-PROFILES-v2-2026-09-19.md` |
| Human alpha 0.46 cold, 0.79 adjudicated; machines 0.66; 0.83 to the majority | `MANNER-FLOOR-2026-09-16.md` |
| Per-code human-machine kappa | `harness/score_manner.py --version v2 --coder Tap` |
| Adjudication, 113 accepted and 79 rejected | `ADJUDICATION-v2-*.md` |
| Machine rulings 0.84 to 0.89 | `MANNER-FLOOR-2026-09-16.md`, `rulings-{pre,current}.jsonl` |
| Blind machine counterfactual | `COUNTERFACTUAL-2026-09-16.md` |
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
46) and the statistics do not: eta-squared 0.52 and rho 0.46 against capability are unchanged, so
the §5 sentence stands. Permutation p comes back 0.000 rather than the 0.001 in the paper;
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
- House names in the paper and post are drafts, not Tapan's words.
- Whether the labeling contribution leads or follows. (Authorship is settled, 2026-09-19: single
  byline, and no acknowledgments section. The two novice coders stay described by their role in
  §4, which is what the validation needs.)
- A reference adjudicated without seeing machine labels, or a second adjudicator, is the honest
  next check. Not needed for this paper.

## Public companions

- Blog post: `convovo-site/src/content/blog/hold-or-fold.md` (/blog/hold-or-fold), still a draft.
- The review site: `studies/conduct/views/index.html`, built by `views/build.py`, published by the
  Pages workflow at https://tap2k.github.io/modelun/conduct/ . It is the study's only view.
- Held-or-folded graphic: `harness/plot_hold_fold.py`.

## On posting

Published papers are pinned by git tag, not by `main` (`AGENTS.md`): this one gets
`conduct-arxiv-v1` when it goes up, and a new tag for any revision. Check `.env` is not staged
before the push.
