# Responsible NLP checklist: answers for the ARR submission

Drafted 2026-09-25 against `main-acl-review.tex`, checked against the submitted build the same day. Section numbers are the anonymous build's:
§1 Introduction, §2 Related work, §3 Method, §4 The tag effect, §5 The reversal is generational
(§5.1 Held-out models), §6 The resistance is keyed to the construction, §7 The tentative tag,
§8 Discussion, then Limitations, Ethical considerations, Data and code availability, Note on AI
usage, and Appendices A (stimulus), B (per-model results), C (naming both options), D
(baseline), E (reasoning), F (classifier). Paste into the OpenReview form; recheck the section numbers if the text moves.

## A. For every submission

- **A1. Limitations:** Yes, the Limitations section.
- **A2. Potential risks:** Yes, Ethical considerations. The stimulus is everyday decisions with no
  harmful content, the study involves no human subjects or user data, and the results are a dated
  description of served behavior, not a vendor ranking. The Discussion notes one risk to
  evaluation practice: a fixed construction can read as cured on models tuned against it.

## B. Scientific artifacts

- **B1. Cite the creators of artifacts used:** Yes. The models are named throughout and listed in
  Appendices B and E; the serving channel (OpenRouter) is named in §3; prior instruments are cited in §2.
- **B2. License or terms:** Yes. The repository's code is MIT and its data and text CC BY 4.0
  (repository `LICENSE` and `LICENSE-DATA`). Model outputs were collected through OpenRouter under
  each provider's API terms.
- **B3. Intended use:** Yes. The models are used as served chat assistants, their intended use.
  The released stimulus, replies and scripts are for research; §8 and Limitations scope the claims.
- **B4. Personally identifying or offensive content:** Yes, none. The items are fictional everyday
  decisions written by the author; no real user data was collected.
- **B5. Documentation of artifacts:** Yes. Appendix A gives the full stimulus and every arm
  template verbatim; Appendix F the classifier rule; Data and code availability maps each script.
- **B6. Statistics of the data:** Yes. §3: 20 items, both options, four samples per cell, 45
  models in July and 25 more in September; Appendix B per-model rates. No train/test split
  applies; nothing is trained.

## C. Computational experiments

- **C1. Model size and compute budget:** Partly. No model is trained. Parameter counts are
  unpublished for the closed models (§5, Tier). Cost is about a dollar per model (§1);
  all calls go through a hosted API, so no local GPU budget applies.
- **C2. Experimental setup and hyperparameters:** Yes, §3: no system prompt, temperature 1.0, the
  yes/no clamp, four samples per cell, output budget 512 tokens in July and 8,192 in September.
- **C3. Descriptive statistics:** Yes. 90% bootstrap intervals over items (2,000 resamples),
  Benjamini-Hochberg FDR at q = .10 over two-sided bootstrap p (§3); per-model intervals in
  Appendix B; failed-cell rates (§3).
- **C4. Existing packages:** Yes. The analysis is custom Python in the released scripts, with
  NumPy for the bootstrap and matplotlib for figures; model calls go through the OpenRouter API.

## D. Human annotators or research with human participants

- **D1. Instructions given to annotators:** Yes. The only human annotation is the author's hand
  check of the classifier on 100 replies (Limitations). The labeling instructions are
  `validation/README.md` in the released repository.
- **D2. Recruitment and payment:** N/A. The author labeled the sample; no one was recruited.
- **D3. Consent:** N/A, for the same reason.
- **D4. Ethics review:** N/A. The study sends scripted prompts to model APIs and involves no human
  subjects.
- **D5. Annotator demographics:** N/A, one annotator who is the author.

## E. AI assistants

- **E1. Use of AI assistants:** Yes, Note on AI usage: Claude helped run the probes, build the
  analysis and draft the text, and several Claude models are subjects of the study.
