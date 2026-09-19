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

No `make_assets.py` yet. **Every number in `main.tex` is currently hand-carried from the dated
result files below**, which is not the convention the other studies follow (consensus,
suggestibility and cross-instrument each trace every quoted number to `gen/stats.json`). Writing
`make_assets.py` to emit `gen/vendor_table.tex`, `gen/profiles_table.tex` and `gen/stats.json` from
`data/coding/results/` is the open item before submission.

## Decisions already made

- One paper, not two. The reliability work is the validation section, not a separate methods paper.
  The contributions are (1) the behavior result and (2) the role of humans in labeling behavior,
  stated as this study's finding with its limits, not as a claim about qualitative methodology.
- Codebook v2 is the instrument. v3 was tested and is not reported (`CODEBOOK-v3-2026-09-17.md`
  is kept only for the audit trail). §3 says so, and §6 says the exploratory test was moved from
  v3 to v2 by amendment 3 before any result.
- The house claim is scoped to the scenes where models split. The out-of-scene test is exploratory
  and its preregistered rule was not met. It is §6 in the current draft; the standing decision is
  that it belongs in an appendix, which the port did not do.
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

Two objections a reviewer raised, both answered from data already here, and both checks had
precedent in the v1 record (`RELABEL-v1-2026-09-14.md`) before being dropped from the v2 draft.

- **Coders share vendors with the panel.** Two of six coders come from each of Anthropic, Google
  and OpenAI. Rebuilding the consensus three times with one vendor's coders out leaves every
  corrected effect standing: empathizing 0.59 to 0.57 without Anthropic's coders, self-citation
  0.52 to 0.47 without Google's. In the paper as a Validation paragraph; the table is
  `CODER-VENDOR-2026-09-19.md`; `harness/manner_matrix.py --drop-coder-vendor` reruns it.
- **Multiplicity.** The draft showed 7 rows with uncorrected permutation p and no denominator.
  Table 1 now carries all 17 manner codes with a Benjamini-Yekutieli column at q 0.05. Six
  survive; probing is seventh at p 0.007 and is reported as suggestive. Trajectory is out of the
  table: it is a primary question reported either way, not one of the family, and folding it in
  made the manner codes pay a penalty for it.

  **On BY rather than BH**, which took two wrong turns before it was settled. The first pass used
  BY without saying why. The second switched to BH on the claim that the codes are positively
  correlated, BH's condition, which restored probing. A reviewer asked for that claim to be shown
  rather than asserted, and it is false: of the 136 code pairs across the 60 models, 65 correlate
  negatively, from -0.75 to +0.73 with a median of +0.03, because a model that holds on an arc
  cannot fold on it and the held and folded codes are structurally opposed. BH's assumption fails,
  BY holds under any dependence, so BY is the correction. `manner_matrix.py` now measures the
  dependence and prints it above the table, and states what BH would have given, so the choice is
  auditable rather than a matter of which test was kinder.

## Open before submission

- `make_assets.py` and `gen/`, so no number is hand-carried (above).
- `references.bib` author lists are not yet verified against the source PDFs: `moore2026coding`,
  `marston2026fortysix`, `liu2026agreement`, `norman2026reliability`, `dunivin2024scalable`, and
  `anthropic2025values` whose arXiv id is unconfirmed. The consensus paper verified its lists
  against the PDFs before posting; do the same here.
- arXiv metadata not yet chosen: primary category (cs.CL or cs.HC, with cs.CY cross-list),
  license, and the abstract as plain text for the submission form.
- Whether §6 moves to an appendix, per the standing decision above.
- No figures. The held-or-folded grid (`harness/plot_hold_fold.py`) is the obvious candidate.
- House names in the paper and post are drafts, not Tapan's words.
- Authorship and whether the labeling contribution leads or follows.
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
