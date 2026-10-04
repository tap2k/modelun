# Handoff: pending decisions from `claude/brand-panel-languages`

Raised 2026-10-03 and not settled. Resolve at the next merge of that branch into `main`.
Whoever merges settles each item with Tapan, records the outcome where it belongs (AGENTS.md,
a study README, the code), and deletes the item here. Delete this file when the list is empty.

1. **Reasoning default: as served or off.** *Settled 2026-10-04 with Tapan: as served is the headline, and the
   hybrids' off arm is reported beside it. Still to do: the brand swap and the missing served arms (see Task 1
   below), then record the rule in the README and delete this item.*
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
     - **Battery tiers** (agreed in discussion 2026-10-03; confirm at the merge).
       - **Core.** Every model on release day, judge-free, about $1 a model:
         - census (31), expanded (65) and brands Name (44), each at 8 runs;
         - pickword (44 languages) at 8 runs;
         - suggestibility;
         - both reasoning arms for the hybrids in each (item 1);
         - later, the census, expanded and brand batteries in every language, once piloted,
           native-checked and frozen (item 2).
       - **Extended.** Every model, may lag: conduct (judged, multi-turn), structured (the census
         asked in JSON), the brand verb grid (Choose, Recommend, one-turn pick, two-turn pick,
         clamped and free), and the atlas once out of its pilot.
       - **Probes.** Subsets, question-driven, never standing: perturbation, realism, the
         Recommend paraphrase check, fingerprinting, the provider audit, channel control, the SDK
         thinking check, temperature 0, the brand-language pilot.
       - **Instrument checks.** Run once on the full panel to validate an instrument, then again
         only when its version changes: the clamped/free checks (`transcripts-clamp*`),
         temperature 0, prompt perturbation.
       - **Re-snapshots.** The census each quarter, in dated directories (see below).
       - **Local and open-weight.** Training-stage ladders (OLMo, Tulu, Nemotron), the local census,
         and local stand-ins for retired models (`transcripts-local/`). Beside the panel, never in
         it.
       - **Concluded, meta or pilot.**
         - Concluded: convergence, gujarati, and the language deep run (superseded by item 2).
         - Meta, no runs: cross-instrument, which is why the core has to be uniform across models.
         - Pilot: interview.
       - **Still open:** suggestibility in the core only if it is truly judge-free; structured as
         core or extended; retired models stay frozen, with local stand-ins where weights exist.
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
9. **Proposals, not decisions: which models to leave out of new batteries, or run with reasoning
   off.** Drafted 2026-10-04 from the brand, pickword and suggestibility runs of 2026-10-03. The
   existing batteries are complete, so nothing is retired or rerun. Consider these when a new
   battery or instrument is added to the panel.
   - **Measures used:**
     - Failed cells after one retry at `--max-tokens 8192`.
     - The share of scenes that needed the 8192 retry because the reply was cut off at 1024.
       DeepInfra models that always run at 4096 are excluded from this measure.
     - Median reasoning tokens per answer, as served.
   - **Candidates to leave out of new batteries.** If adopted, mark them in `spec/models.json` with
     the reason. The roster stays append-only and existing transcripts stay.
     - **Claude 3 Haiku, Granite 4.1 8B, Hermes 4 70B.** Retired from OpenRouter (404). Granite
       and Hermes keep their local stand-ins (item 8).
     - **WizardLM-2 8x22B.** 7.8% of cells still fail after the retry, from empty replies plus rate
       limits. A 2024 model, with little added value.
     - **DeepSeek R1.** 11% of cells fail even at 8192, from empty replies with `stop`, and 43% of
       scenes needed the 8192 retry. Superseded by V3.2 and V4 in the same lineage. One option is
       to freeze it: keep what exists, run nothing new, and accept that its time series ends.
     - Sonar is already stopped.
   - **Candidates for reasoning off as their default arm in new batteries** (heavy or unstable
     hybrids). Their as-served answers are long, slow and often cut off. The proposal is reasoning
     off in new batteries, and as served only for the core census (a cheap check of the reasoning
     effect). This would be an exception to item 1 if item 1 settles on as served.

     | model | median reasoning tokens | scenes needing 8192 | note |
     |---|---|---|---|
     | Qwen 3.5 9B | 444 | 63% | runaway to 38,778 tokens; failures persist at 8192 |
     | Qwen 3.5 122B | 405 | 5% | hours per battery |
     | Qwen 3.5 27B | 368 | 9% | hours per battery |
     | Qwen 3.7 Plus | 347 | 27% | 67% of free Recommend calls cut off at 1024 |
     | Nemotron 3.5 Lightning | 383 | 23% | |
     | Qwen 3.6 35B | 300 | 21% | |
     | GLM 4.7 | 259 | 33% | |
     | Hy4 Preview | 241 | 19% | |
     | Granite 4.2 8B | 194 | 27% | |

   - **Reasoning-only models that run long.** Off is not available. The proposal is to start new
     batteries at `--max-tokens 8192` rather than retrying: Step 3.7 Flash (42% of scenes needed 8192), Muse
     Glimmer 30B (37%), GLM 5.3 Flash (33%), Muse Spark 1.3 (26%).
   - **No action:** Kimi K2 ignores off, so its off runs are its as-served runs.

## Session state (2026-10-04, head before this note `fdefc79`)

For the next session: what the branch holds, what is open, and how to run. The numbered items above
are the decisions to settle.

**On the branch, all committed:**
- **Core panel complete for 101 served models:**
  - census at 8 runs (`transcripts` + `transcripts-extra`);
  - expanded at 8;
  - brands Name in 44 categories (41 + `spec/stimulus_brands_ext2.json`);
  - pickword at 8 (`transcripts_pickword` + `transcripts_pickword_extra`);
  - suggestibility (11 models appended to its `spec/models.txt`).
- **Both reasoning arms for the 25 hybrids** (the 24 in `transcripts-brands-ext-default/` plus GPT-6
  Luna):
  - off: `transcripts-reasoning-off`, `transcripts-expanded-reasoning-off`,
    `studies/language/transcripts_pickword_reasoning_off`;
  - as served: the brand `-default` directories.
- **Brand verb grid.** Clamped Recommend and clamped one-turn pick
  (`spec/perturb/stimulus_brands_{recommend,pick}_clamp.json`), each with `-default` directories for
  the hybrids. Free Recommend's as-served arm is `transcripts-brands-recommend-default`.
- **Language pilot.** 5 models x 21 languages x 44 categories in
  `transcripts-brands-lang-pilot/<lang>/`. Specs from `build_brands_lang.py`; scoring in
  `brands_lang.py` with `spec/brands_lang_aliases.json` (agent-drafted, review it); the summary is
  `probes/brands_lang_pilot.json`.
- **Scorer.** `brands.brand_name` keeps Indic and Arabic marks, the katakana middle dot and the
  Persian zero-width non-joiner. `latin_only=False` is for the cross-language battery. All 124,820
  English cells score unchanged.
- **Harness.** `run.py` saves after every scene (atomically) and has `--resume`.
- **Runners.** `run_brands_panel.py` (each model with its `transcripts-brands-ext` settings; has
  `--skip-existing`), `run_reasoning_off.py`, `run_extra.py` (skips the retired models),
  `run_brands_lang_pilot.sh`.

**Failures recorded in the files** (the models' own replies, persisting at `--max-tokens 8192`):

| model | clamped pick | clamped Recommend | pickword extra |
|---|---|---|---|
| DeepSeek R1 | 51/328 | 58/328 | 20/184 |
| WizardLM-2 | 49/328 | 34/328 | 12/184 |

Qwen 3.5 9B has 3-4 runaway-reasoning failures per file. Claude 3 Haiku, Granite 4.1 8B and Hermes 4
70B are retired from OpenRouter.

**Preliminary readings (not written up; discuss with Tapan first):**
1. **Reasoning makes the hybrids more conventional.** As served they move 3-8 points toward the
   panel consensus. The effect is real on expanded and pickword, and within noise on the census.
2. **The clamped verb series, as served** (99 models, 38 categories). The consensus brand differs
   from Name in Choose 5, Pick 12 and Recommend 14. The other session's two-turn pick is 28/41,
   so the conversation, not the verb, drives the shift.
3. **The language pilot.** Where a home market exists, the home-market brand wins (Alipay, Jio,
   Coupang). Global brands hold (Google, Tesla, Netflix).

**Next:**
1. **The other session's work is now committed** (`a18ecd8` on `main`, merged here in `fd53785`):
   - `transcripts-brands-pick/` (two-turn recommend then pick, 41 brands, 101 models),
     `transcripts-brands-choose-free/`, `transcripts-brands-you-pick/` (one-turn "Which X would you pick?", free),
     `transcripts-brands-recommend/` (free one-turn recommend, committed earlier in `f0e5e8d`), and
     `transcripts-perturb/recommend2`, `recommend3` (two recommend paraphrases on the 14-model perturbation subset).
   - Empty cells still in the files: pick 51, free Choose 138, one-turn pick 296 (mostly GLM 5.3, GLM 5.3 Flash,
     GPT-5, DeepSeek R1). Refill with `run.py --resume --max-tokens 8192`.
   - Scoring is not final. The scratch scorers (open-vocabulary pick extraction, brand collapsing, the gradient
     table, the stage-ladder and log-probability readers) are in the planning folder,
     `consensus/converging-on-serendipity/scoring-2026-10-03/`. `probe_recommend.py` (first mention over the
     Name and Choose pools) is committed.
   - Preliminary, free forms on the full panel (not yet rescored as served): the consensus brand differs from Name in
     Choose 6, Recommend 15 and two-turn pick 28 of 41; free Choose about 8 and one-turn pick about 12 (79 models).
     The clamped series above agrees (one-turn pick 12). Read: the conversation, not the verb, drives the shift.
     Confounds to separate before claiming it (agreed with Tapan 2026-10-03, discuss before writing anything up):
     where the pick sits in the model's own turn-1 list; the paraphrase floor (recommend2/3, unscored); by lab;
     by category; reasoning arm; first-mention versus opening-brand scoring.
   - **Stage ladders** (`probes/verb_ladder_<pipeline>/`, `probes/answer_logprob_<pipeline>.json`):
     - OLMo 3 7B complete. Preliminary: Name fixes at SFT; Choose separates from Name at DPO and clearly at RL
       against a split-half noise floor; DPO raises the Choose favourite's probability under the Choose prompt only.
       Notes in the planning folder's `converging-on-serendipity/PLAN.md`.
     - Tulu 3 8B complete, not yet scored. It is the same ladder as Samanta, Holtzman and West (arXiv:2606.29933),
       who state SFT "nucleation" then "settling"; the 7B DPO gain for low-ranked favourites is the test of it.
     - OLMo 3.1 32B: base only. Nemotron: final-stage recommend only. The first queue's conversions failed on a
       dropped download. A fixed rerun (`scoring-2026-10-03/weekend2.sh`, log in the old session's scratch) was
       started 2026-10-04 17:22 on the Mac: full `hf download`, convert from the local copy, check before use. The
       probes skip completed stages. Expected: 32B overnight, Nemotron Monday.
   - **Literature pass (2026-10-03).** Combined gap report `~/Desktop/projects/modelUN/GAP-REPORT-2026-10-03.md`
     (about 160 papers added across the bibliographies). Claims that changed: the stage ladder must cite Samanta and
     Fortier; IRIS (arXiv:2607.20860) pre-empts closed-set fingerprinting and a cross-provider audit; AgentProv
     (arXiv:2609.00052) means each provider-audit mismatch needs the billed-token check before it counts (added to
     `fingerprinting/PROVIDER-AUDIT-PLAN.md`); Jack et al. make a paraphrase floor necessary for the brand gradient.
   - **Blind ranking of the program's results (2026-10-03,** four rankers: ML reviewer, journalist, practitioner,
     strategist). Consistent top: the brand gradient, fingerprinting from meaning, the census; "APIs are not bare" top
     for the journalist and practitioner. Agreed wording fixes and cuts are in that session; the brands page is
     unchanged on purpose (Tapan: not shared yet, discuss later).
2. **Local pickword** for Granite 4.1 8B and Hermes 4 70B (item 8).
3. **The merge.** Open a PR to `main`, settle the items above, then delete this file. The only
   existing files the branch changes are `brands.py`, `harness/run.py` and
   `studies/suggestibility/spec/models.txt`.
4. **Running.**
   - Launch long batches detached (`setsid nohup`) with `--resume`, never tied to a tool's time limit.
   - Start hybrids and long-reasoning models at `--max-tokens 8192`.
   - Commit a transcript only with zero failed cells, or state its failures in the commit message.
   - OpenRouter credit was about $111 on 2026-10-04.
5. **Keys.** The OpenRouter and DeepInfra keys used on 2026-10-03 were pasted into chat; rotate
   them. No copy is in the repo.

## Next session (set 2026-10-04 by Tapan)

**Still running on the Mac** (in `~/dev/convovo/modelun`, branch `main`; do not switch branches in that folder until both finish):
- GPU: OLMo 3.1 32B SFT/DPO/RL then Nemotron base/final, copied from the external drive with checksums
  (`~/Desktop/projects/modelUN/consensus/converging-on-serendipity/scoring-2026-10-03/weekend3.sh` is the same queue;
  the live copy and its log are in the old session's job scratch). Outputs land uncommitted in
  `studies/consensus/probes/verb_ladder_{olmo31-32b,nemotron35-lightning}/` and `probes/answer_logprob_*.json`.
- API: refill of the empty cells in `transcripts-brands-{you-pick,choose-free,pick}/` (about 20 model files).
- Commit both from that folder when done.

**The brand verb grid, scored** (scorer `scoring-2026-10-03/grid.py` in the planning folder; results discussed with Tapan
2026-10-04, not yet written up). Consensus differs from one-word Name in 4/41 free Name, 6 Choose, 13 free Choose,
15 one-turn pick, 15 recommend, 28 two-turn pick. Models keep their own one-word default 87, 76, 72, 43, 24, 46, 21%.
Own default is in the turn-1 list 75% of the time and is the pick 25%. Cold one-turn pick scatters (top share 38%,
29% no pick); after a list the field converges on a new winner (49%). Paraphrase floor small (rewordings agree with
recommend's consensus in 39/41 and 34/41). Toyota holds at every level.

**Task 1: housekeeping and organisation.** *Step 1 done 2026-10-04:* `studies/consensus/spec/runs.json` lists every
transcript directory (battery, form, clamped or free, arm, models, runs, tier, published tag), `check_runs.py` checks it
against the files and writes the README "Runs" table, and `analyze.BATTERIES` reads from it. Agreed with Tapan, still to
do once the Mac refill is committed and merged:
- **Renames** (unpublished directories only; `transcripts/`, `transcripts-temp0/`, `transcripts-clamp/` stay, because
  the paper links to `main`): `-reasoning-off` to `-off`; `brands-recommend` to `brands-recommend-free`;
  `brands-you-pick` to `brands-pick1-free`; `brands-pick-clamp` to `brands-pick1-clamp`; `brands-pick` to
  `brands-pick2-free`; `brands-choose` to `brands-choose-clamp`. Update `spec/runs.json` (ids stay), the scripts that
  name them, and the planning folder's `grid.py`.
- **Brand swap** (item 1): the 25 hybrids' `-default` files move into the main brand directories, and their off files
  move out to `-off`, so every main directory is as served.
- **Missing served arms:** free Choose, free one-turn pick and two-turn pick have no as-served run for the hybrids.
- **Empty files:** 23 reasoning-only models in `transcripts-reasoning-off/` have every cell failed (400, off rejected).
  They hold no answers; remove them in the rename commit.
- The cost.py/panel_gap.py manifest (item 6) is deferred until a second study keeps a `spec/runs.json`.

**Task 2: visualise the brand ladder.** Name, free Name, Choose, free Choose, one-turn pick, recommend, two-turn pick:
per category (the running-shoe walk Nike to Brooks is the clearest example) and possibly per model. Likely home: the
consensus viewer (`views/`) as a new page, and later the convovo.ai/brands page (unshared on purpose; discuss first).
