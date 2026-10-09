# Responsible NLP checklist: answers for the ARR submission

Updated 2026-10-09 for v2, against `main-acl-review.tex`. Section numbers are the anonymous build's:
§1 Introduction, §2 Related work, §3 Method, §4 Agreement falls as the user sounds surer, §5 The
generational reversal, §6 The boundary, §7 The resistance is keyed to the construction, §8 Training
stages, §9 Discussion, then Limitations, Ethical considerations, Data and code availability, Note on
AI usage, and Appendices A (stimulus), B (per-model results), C (validation), D (training stages),
E (family orderings), F (robustness of the release test), G (reasoning configuration), H
(classifier). Recheck the section numbers if the text moves.

## A. For every submission

- **A1. Limitations:** Yes, the Limitations section.
- **A2. Potential risks:** Yes, Ethical considerations. The stimulus is everyday decisions with no
  harmful content, the study involves no human subjects or user data, and the results are a dated
  description of served behavior, not a vendor ranking. §9 notes one risk to evaluation practice:
  a fixed construction can read as cured on models tuned against it.

## B. Scientific artifacts

- **B1. Cite the creators of artifacts used:** Yes. The models are named throughout and listed in
  Appendices B and G; the serving channels (OpenRouter, DeepInfra) are named in §3; the open
  training pipelines in §8 and Appendix D are cited; prior instruments are cited in §2.
- **B2. License or terms:** Yes. The released code is MIT and the data and text CC BY 4.0
  (`LICENSE` and `LICENSE-DATA` in the supplement). Model outputs were collected under each
  provider's API terms; the open checkpoints in §8 were used under their published licenses.
- **B3. Intended use:** Yes. The served models are used as chat assistants, their intended use, and
  the open checkpoints for research. The released stimulus, replies and scripts are for research;
  §9 and Limitations scope the claims.
- **B4. Personally identifying or offensive content:** Yes, none. The items are fictional everyday
  decisions written by the author; no real user data was collected.
- **B5. Documentation of artifacts:** Yes. Appendix A gives every wording and cue template
  verbatim; Appendix H the classifier rule; Data and code availability maps each script.
- **B6. Statistics of the data:** Yes. §3: 106 models, 20 items, both options, three wordings by
  three cues, four samples per cell, collection dates and failed-cell rates; Appendix B per-model
  rates. Nothing is trained, so no split applies.

## C. Computational experiments

- **C1. Model size and compute budget:** Partly. No model is trained. Parameter counts are
  unpublished for the closed models. Served models were called through hosted APIs at about a
  dollar per model (§1). The training-stage checkpoints (§8, Appendix D) were sampled locally on one
  64 GB Apple-silicon machine, quantized as Appendix D states.
- **C2. Experimental setup and hyperparameters:** Yes. §3 and Appendix A: no system prompt,
  temperature 1.0, the yes/no clamp, four samples per cell, output budget 512 or 8,192 tokens;
  Appendix D: 16 samples per cell for the local checkpoints; Appendix G: reasoning settings.
- **C3. Descriptive statistics:** Yes. Nested bootstrap over items and replies (2,000 draws), 95%
  intervals, two-sided bootstrap p with Benjamini-Hochberg at q = .05 per measure within a wording;
  the release test is a permutation test (§3, §5, Appendix F); per-model intervals in Appendix B.
- **C4. Existing packages:** Yes. The analysis is custom Python in the released scripts, with NumPy
  for the bootstrap and matplotlib for figures; served models are called through the OpenRouter API
  and local checkpoints through MLX.

## D. Human annotators or research with human participants

- **D1. Instructions given to annotators:** Yes. The only human annotation is the author's blind
  audit of the classifier on 150 replies (Limitations, Appendix H). The labeling instructions are
  `validation/README.md` in the supplement.
- **D2. Recruitment and payment:** N/A. The author labeled the sample; no one was recruited.
- **D3. Consent:** N/A, for the same reason.
- **D4. Ethics review:** N/A. The study sends scripted prompts to models and involves no human
  subjects.
- **D5. Annotator demographics:** N/A, one annotator who is the author.

## E. AI assistants

- **E1. Use of AI assistants:** Yes, Note on AI usage: Claude helped run the probes, build the
  analysis and draft the text, and several Claude models are subjects of the study.
