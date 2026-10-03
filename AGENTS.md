# AGENTS.md — notes for coding agents

Rules and tripwires that aren't obvious from the code. For what the project is and how to run it, see
[README.md](README.md).

**Private planning material** (study plans, the research queue, paper notes and PDFs, the bibliography) lives outside this public repo at `~/Desktop/projects/modelUN/`. Look there for anything planning-shaped before assuming it does not exist.

## Layout: harness vs. study
The repo splits into a domain-neutral **`harness/`** (the tool — runner, judge, adjudicator, the
`viewer/core.js` renderer) and **`studies/<name>/`** (the conduct atlas is `studies/conduct/`). The
harness holds no conduct semantics; a study supplies `spec/` (`stimulus.json` + `codebook.py`),
`data/`, `views/`, `docs/`. Architecture and contracts: [`docs/harness.md`](docs/harness.md). Harness
scripts take `--study <dir>` and resolve paths via `harness/study.py` (+ the study's
`spec/paths.json`, which lets conduct keep its historical `data/benchmark` and `markers/` names).

## The frozen stimulus is sacred
`studies/conduct/spec/stimulus.json` is byte-identical input sent to every model — that's what makes
columns comparable.
- Do **not** edit scene turns or the `system_prompt` clamp between runs you intend to compare.
- Any change to the stimulus (including the clamp) **must bump `script_version`**, and the old and
  new versions are not comparable — keep them in separate run dirs.
- The clamp is content added to the stimulus, not a config knob: version it; it's stamped into every
  transcript header.

## Markers annotate, they don't replace
- Every marker value cites a **verbatim** trigger quote that must be a real substring of the
  transcript. After scoring, string-check it; an unverifiable claim is dropped (it has happened).
- The judge is `google/gemini-2.5-flash`, which is **itself a subject**. Its calls on the google
  family (gemini / gemma) are self-judged — flag those cells, don't silently trust or drop them.

## Forking is the adoption path — do not build a framework
The intended way someone else uses this is to **fork it, or vendor `harness/` plus one study's
`spec/`, and go do their own thing**. Contributions back are welcome but are not the model. Two
consequences for anyone working in here:

- **Do not extract a shared library across studies, and do not add a plugin or extension API to
  `harness/`.** Duplication between studies is correct, not debt. A shared abstraction converts
  vendoring into depending, and then this repo owns every downstream upgrade. If two studies have
  similar analysis code, leave them similar.
- **The contracts are the interchange, and they are what to keep stable.** Contract A
  (transcripts), Contract B (labels), the spec shape and `store.json` are why two independently
  forked studies are comparable to each other and to ours. That comparability is the thing a shared
  framework would have bought, obtained without the dependency. Changing a contract is expensive in
  a way that changing a study's code is not.

## Panels grow by appending, and a published panel is pinned by tag

A study's roster is **append-only**. New models go on the end of
`spec/models.txt`; existing entries are never reordered or removed, because a
paper refers to its panel by position ("the first 44 entries") and reordering
silently changes what a published number was computed over. A model that had to
be dropped is recorded as dropped in `spec/models.json`, with the reason, rather
than deleted (see `hermes-3-llama-3.1-70b`, whose only host returned prose to a
one-word prompt).

**Every panel a paper reports is pinned with a git tag** named
`<study>-arxiv-v<n>` — `consensus-arxiv-v1`, `consensus-arxiv-v2`,
`suggestibility-arxiv-v1`, `structured-arxiv-v1`, `conduct-arxiv-v1`, `conduct-arxiv-v2`. Adding models after a paper
ships is expected and does not invalidate it: the tag is what the paper's
numbers reproduce from, and `main` carries the growing panel. When a new wave is
added, note the wave and its date in `spec/models.json`, and tag the panel again
if it is published again.

So the sequence for adding a model is: append to `spec/models.txt`, run it,
commit the transcripts, and leave every earlier tag alone.

A model added to the census also gets pickword on the same day: append it to
`studies/language/spec/models.txt` and run `spec/pickword.json` into
`transcripts_pickword/`. Pickword is the cheapest longitudinal record the repo
keeps (one word, 44 languages), and gaps in it cannot be filled after a model
is retired.

## What has been run is the transcripts, not the roster

`spec/models.txt` is intent; `transcripts/` (or a study's `paths.json`
equivalent) is fact. They drift — a model can be listed and not yet run, or run
and not yet listed. Anything asking "what have we covered?" reads the transcript
directory. `harness/panel_gap.py` diffs both against the live OpenRouter
catalog, and flags models with an `expiration_date`, which are the only ones
where waiting loses the data permanently.

## Pending decisions: resolve at the next merge of `claude/brand-panel-languages`

Raised 2026-10-03 and not settled. Whoever merges that branch into `main` settles each item with
Tapan before or at the merge, records the outcome in the section it belongs to, and deletes the
item here.

1. **Reasoning default: as served or off.**
   - **History.**
     - The census, expanded, pickword and language batteries ran as served (no `--reasoning` flag).
     - The brand batteries ran `--reasoning off` where the endpoint allowed it.
     - The 24 hybrids (accept off, reason by default; the models in
       `studies/consensus/transcripts-brands-ext-default/`) also have default-reasoning reruns in
       the `-default` directories.
     - So the brand panel can be read either way: as served is the off run with the hybrids'
       `-default` files swapped in.
     - For every other model off and as served are the same, except GPT-6 Luna (about 13
       reasoning tokens per answer as served) and Kimi K2, which ignores off.
   - **The check.** On the 24 hybrids the brand consensus differs between the two settings in
     4 of 41 categories, and a model's own top brand is the same in 80% of model x category pairs.
   - **The case for as served:** it is what users get.
   - **The case for off:** a reasoning trace can pull an answer (in other languages, possibly
     toward English), and off is the cleaner reflex.
   - **Either way:** about 19 reasoning-only models cannot be switched off, so the panel stays mixed.
   - **Robustness check:** reasoning-off reruns of the hybrids for census, expanded and pickword
     are in `transcripts-reasoning-off/`, `transcripts-expanded-reasoning-off/` and
     `studies/language/transcripts_pickword_reasoning_off/`.
   - **Until decided:** run hybrids both ways (`studies/consensus/run_brands_panel.py` does).
2. **The full census in every language.**
   - **Scope.** The full panel through all three Name batteries in every language: the census (31
     categories), the expanded battery (65) and the brand battery (44). It would replace the
     language study's deep run (15 categories, 5 languages) as the cross-language census.
   - **Template.** The brand battery's five-model pilot in 21 languages:
     `studies/consensus/transcripts-brands-lang-pilot/`, `build_brands_lang.py`, `brands_lang.py`
     and `probes/brands_lang_pilot.json`. That is one prompt table per battery, one directory per
     language, and a per-category alias table mapping every answer to one name across scripts.
   - **Still to settle.**
     - The language set: the brand pilot's 21, or pickword's 37 reported.
     - How to ask for one word where words are not space-separated (zh, ja) or are
       agglutinative (tr, ko, sw).
     - A census scorer for non-Latin scripts. `analyze.norm()` keeps the last Latin token.
     - The reasoning setting (item 1).
   - **Before running.**
     - Translations of the 96 census and expanded questions.
     - Native review of those translations and of the brand prompts.
     - A pilot on a few models.
   - **Rough cost** for 20 languages beyond English on 105 models: census at 4 runs about $45,
     expanded at 8 runs about $670, brands at 8 runs about $300, so about $1,000. These are the
     English per-call costs times 1.5 for non-Latin tokenisation. Expanded is most of it,
     because reasoning models answer it at length.
3. **The brand gradient's clamped/free grid.**
   - **What is new.** Clamped Recommend and clamped one-turn pick were added on this branch
     (`spec/perturb/stimulus_brands_{recommend,pick}_clamp.json`). With them, every step from
     Name to pick has a clamped form, and all but two-turn pick also has a free form.
   - **Reconcile them** with the other session's free Choose, one-turn pick, two-turn pick and
     Recommend-paraphrase runs, which were uncommitted on Tapan's Mac on 2026-10-03.
   - **Rescore its headline counts as served** (Choose 6/41, Recommend 15/41, pick 28/41).
4. **Review the cross-language brand material.**
   - **The alias table** `studies/consensus/spec/brands_lang_aliases.json` was drafted by Claude
     agents. The flagged calls are in the 2026-10-03 session (Asahi Super Dry into Asahi, BBC
     language services kept apart, the Persian "پی" left unresolved).
   - **The translated prompts** need a native check before the full panel. The notes are in
     `studies/consensus/spec/brands_lang_notes.md`.
5. **The hybrid list.** Whether GPT-6 Luna joins the 24, and the rule for adding a model: it
   accepts off and uses reasoning tokens as served.
6. **Look for an earlier census pilot in another language.**
   - **The question.** Tapan recalls a pilot of the full census or expanded battery in another
     language. It is not in git (all 814 commits checked).
   - **Searched on 2026-10-03:** remote sessions from 2026-07-04 to 10-03. There was no run of the
     31 or 65 categories in another language.
   - **Closest finds:**
     - The committed deep run (15 categories, 5 languages, commit 5f0f326, 2026-07-15).
     - The 2026-09-30 decision to "hold the languages" until prompts are native-checked.
     - The language coverage probe (2026-09-29), whose files are in the private folder
       `consensus/language-census/`. The research queue there has the language census "PARKED
       2026-09-13".
   - **Where else to look.** An all-category pilot would date from about 2026-07-10 to 07-15, when
       `studies/language` was created. No remote session covers that window, so check the local
       Claude Code history on the Mac for that week before re-running one.

## History & the bottom-up layer
- The conduct study has two methodology layers. The current **top-down** layer (6 scenes, predeclared
  TONGUE/HANDS/HEART markers, single judge) is `studies/conduct/` itself. Its earlier **bottom-up**
  layer (9 open scenes, emergent bestiary, its 3-reader cross-check basis, the per-model cards, the
  catchphrase report) is preserved and still rendered under
  [`studies/conduct/bottom-up/`](studies/conduct/bottom-up/) — see its
  [README](studies/conduct/bottom-up/README.md) for the map and how to recreate any thread. No tags or
  side branches: everything (analyses, basis, tooling, and the scene-run library in
  `studies/conduct/data/benchmark/`) is on `main` and pushed. The pre-prune repo remains reachable in
  history at commit `a36cf84` (`git show a36cf84:<path>`).
- **Picking up the markers thread**: the live top-down marker layer is single-judge; the pipeline
  already supports a multi-judge panel (`harness/adjudicate.py` does majority + self-family exclusion).
  The exact recipe to harden it — importing the bottom-up layer's 3-reader cross-check as the template —
  is in `studies/conduct/bottom-up/README.md` § *Picking up the markers thread*.
- Principle for what to commit: **keep anything that served as the basis of an analysis/synthesis;
  intermediates (raw runs, scratch labels, regenerable figures) stay gitignored**.

## Provenance & secrets
- **Published papers are pinned by git tag**, not by `main`: `consensus-arxiv-v1`/`-v2`,
  `structured-arxiv-v1`, `suggestibility-arxiv-v1`, `conduct-arxiv-v1`/`-v2`. Rosters and analyses on `main`
  may grow past them (new models join the live panel); never move or delete a tag. A paper revision
  gets a new tag.
- Every run is a dated specimen: model version + date + script_version + clamp, all stamped.
- `runs/`, `cards/` (root) and per-study `reads/`, `markers/`, `views/data.js` are generated working output and **gitignored** (the
  curated basis is committed under `studies/conduct/bottom-up/`). The published data lives in `studies/conduct/data/benchmark/`. Never
  commit transcripts-in-progress, scratch marker runs, or `.env`.
- Before any push, confirm `.env` is not staged. A leaked `OPENROUTER_API_KEY` is the one
  unrecoverable mistake.

## Honest limits to respect
- Small N, dated specimens. The conduct study's *live* marker layer is single-judge (the harness
  supports a multi-judge panel; conduct just hasn't run one). Characterizations, not measurements —
  don't write reads into docs as established. The frontier-lab "house styles" are a working lens, not a
  universal law.

## Gotchas
- `harness/run.py` exits 0 even if cells fail (failures are written into the file). Check the output,
  not just the exit code.
- Local checkpoints (`harness/local.py`, listed in `harness/ladders.json`) write Contract A into a
  probe's own directory (`probes/<name>/`) or `transcripts-local/`, never into a study's API transcript
  directory: a file there joins the panel, the views and `analysis.json` on the next build.
- One local model in memory at a time on this 64 GB machine. Two large checkpoints resident together
  (a second process, or a dropped model mlx still caches) gave `<unk>` replies, not an error. Between
  stages call `del model` then `local.free()`; before starting a GPU job, check that no other `local.py`
  or mlx process is running (`pgrep -fl mlx`), including another session's.
- Commit messages: use `git commit -F <file>`. Heredocs with apostrophes (`model's`, `don't`) break
  the shell.
