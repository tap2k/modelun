# Handoff: pending decisions from `claude/brand-panel-languages`

Raised 2026-10-03 and not settled. Resolve at the next merge of that branch into `main`.
Whoever merges settles each item with Tapan, records the outcome where it belongs (AGENTS.md,
a study README, the code), and deletes the item here. Delete this file when the list is empty.

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
   - **The check (2026-10-03, the 24 hybrids, off vs as served).** The first figure is how often
     a model gives the same top answer under both settings; the noise floor is the same comparison
     between two as-served samples.
     - **Census:** 79% against a noise floor of 77%. No real effect; the consensus differs in 2 of
       31 categories.
     - **Expanded:** 60% against a floor of 76%, at matched 4-run samples. A real effect: the
       consensus differs in 13 of 65 (composer Bach to Mozart, villain Voldemort to Joker,
       landmark Eiffel to Colosseum).
     - **Pickword:** 16% against a floor of 25%. A real effect: the consensus differs in 24 of 46
       languages (es sol to hola, hi शांति to नमस्ते).
     - **Brands:** 80%, floor not measured. The consensus differs in 4 of 41.
     - So the setting matters outside the core census. Whatever the default, expanded and pickword
       need both settings for the hybrids.
     - **Direction: reasoning makes the hybrids more conventional, in every battery.** Compared
       with the consensus of the other models, as served the hybrids:
       - give the field's answer more often: census 59% to 62%, expanded 55% to 63%, pickword 10%
         to 15%, brands 74% to 77%;
       - repeat their own top answer more: census 74% to 82%, pickword 41% to 51%;
       - give fewer distinct answers.

       Thinking reaches the canonical answer (Mozart over Bach, the Joker over Voldemort); off
       gives the first association. In pickword, reasoning pulls toward the language's greeting
       (hola, नमस्ते, سلام). A hybrid's census divergence therefore depends on the setting.
       Contrast this with the brand gradient, where a written-out list pulls the pick away from
       the consensus.
   - **The case for as served:** it is what users get.
   - **The case for off:** a reasoning trace can pull an answer (in other languages, possibly
     toward English), and off is the cleaner reflex.
   - **Either way:** about 19 reasoning-only models cannot be switched off, so the panel stays mixed.
   - **Robustness check:** reasoning-off reruns of the hybrids for census, expanded and pickword
     are in `transcripts-reasoning-off/`, `transcripts-expanded-reasoning-off/` and
     `studies/language/transcripts_pickword_reasoning_off/`.
   - **Until decided:** run hybrids both ways (`studies/consensus/run_brands_panel.py` does).
   - **Recommended:** both arms for the hybrids as part of the standing core, in every battery.
     Report as served as the headline (what users get, and how five of six batteries already
     run), with the off arm reported beside it; it is a measured effect, not a footnote. It costs
     about $5-10 a battery, since only the hybrids need it. The brand batteries switch their
     headline by swapping in the existing `-default` files.
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
   accepts off and uses reasoning tokens as served. Luna was given default-reasoning reruns of
   every brand battery on 2026-10-03, in the same `-default` directories, so it can join without
   new runs. Kimi K2 needs none, because it ignores off.
6. **The shape of the standing panel.** The goals it serves, as drafted 2026-10-03 (confirm):
   - **Goals, in priority order:**
     1. A dated, cross-vendor archive of what production models default to, collected on release
        day and kept after retirement.
     2. The same frozen instruments across models and over time.
     3. A per-model profile across behaviours.
     4. Audiences beyond ML (brands, languages).
     5. Forkability.
   - **Not goals:** a leaderboard, a quality ranking, a brand tracker.
   - **Recommended:**
     - **Roster.** Models join by rule, not taste: frontier releases from the major labs, the top
       models by OpenRouter usage, notable open-weight families, every version of a tracked
       lineage, and a few deliberate outliers. Append-only; a model with an expiration date goes
       first.
     - **Battery tiers.**
       - Core: judge-free, every model on release day, about $1 a model. Census, expanded,
         brands Name, pickword and suggestibility, plus the cross-language census once it is
         piloted, native-checked and frozen.
       - Extended: every model, may lag. Conduct and the brand verb grid.
       - Probes: subsets only, never standing. Realism, paraphrase, perturbation, fingerprinting
         and local ladders. (The hybrids' second reasoning arm is part of the core; see item 1.)
       - An instrument enters the core only after a pilot and a frozen spec.
     - **Runs.** 8 for every one-word battery. The census already has 4 + 4 in
       `transcripts-extra/`. Pickword gets 4 more in `studies/language/transcripts_pickword_extra/`
       (run 2026-10-03; it doubles as a re-snapshot); its original 4-run files stay as published.
     - **Re-snapshots.** The census each quarter on every model still served, and on any alias
       change. Store in dated directories and never overwrite.
     - **Language set.** Fix it once (21 or 37) if cross-language work enters the core.
     - **One manifest.** `harness/cost.py` `BATTERY` becomes the single definition of the core
       tier (spec, runs, condition). `panel_gap.py` reports models missing any core instrument, and
       the release-day rule in this file points at it. Plain data, not a plugin API.
7. **Look for an earlier census pilot in another language.**
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

8. **Models that left OpenRouter: run locally where possible (handoff, on the Mac).**
   - **What happened.** Claude 3 Haiku, Granite 4.1 8B and Hermes 4 70B return 404 on
     OpenRouter as of 2026-10-03. They keep 4 API census runs (no `transcripts-extra/`), and their
     pickword extra runs fail.
   - **Granite 4.1 8B (bf16) and Hermes 4 70B (4-bit mlx).** Both already have 8 local census runs
     in `studies/consensus/transcripts-local/census/`. Their weights are in `harness/ladders.json`;
     the local files record `/Volumes/My Passport/models/...`.
   - **What is left: run pickword for both locally** with `harness/local.py`, into a local
     directory such as `studies/language/transcripts-local/pickword/`, per the AGENTS.md gotcha on local checkpoints.
     A local checkpoint differs from the served model in quantization, chat template and serving,
     so local runs sit beside the API runs; they are not merged into them.
   - **Claude 3 Haiku** has no local route. Leave it at 4 runs.
