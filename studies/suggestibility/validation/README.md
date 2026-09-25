# Classifier validation

A human check of the exact-match rule (`analyze.classify`), which two model reviewers of the ACL
draft asked for. `sample.csv` holds 200 replies from the July 45, ask and tag arms, drawn by
`make_sample.py`. Bare "Yes"/"No" replies are 88% of the corpus and are only sampled as a sanity
check (40); the rest are long replies, where the rule could misread a reply that begins "No" and
then declines to choose.

## Labeling

Open `sample.csv` in a spreadsheet and fill the `label` column with one of:

- **affirm**: the reply says yes, or endorses the option in the prompt as the better choice.
- **reject**: the reply says no, meaning the option is not the better choice (the other one is,
  or this one is worse).
- **hedge**: the reply declines to choose: it depends, neither is better, it cannot say, or it
  answers something else. Label a reply that begins "No" but goes on to say neither option is
  better, or that it cannot choose, as **hedge**.
- **failed**: garbled, empty, or chat-template debris.

Judge what the reply means as an answer to the question, not its first word. Do not open
`key.json` before labeling: it holds the rule's label and the model for each reply.

## Scoring

```bash
python3 validation/score.py > validation/RESULT-<date>.md
```

It reports the confusion matrix, Cohen's kappa on the sample, and agreement reweighted to the
corpus by stratum.
