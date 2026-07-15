# perturbation — is the monoculture shallow or deep?

A robustness sibling to the [consensus](../consensus/) census and the [language](../language/)
study. Same instrument (wide-answer-space "Name a X" prompts, one-word clamp, exact-match),
but instead of varying the *language*, we vary the *prompt* by tiny, meaning-preserving
amounts and ask: **does the field's convergent answer survive?**

If a typo or a synonym swap flips the modal answer, the "default" is a **shallow
surface-triggered lookup**, not knowledge — the strongest form of the frequency-prototype
thesis ([language](../language/) H1/H2). If the strongest attractors (oak, serendipity)
survive every perturbation, they are **deep**, and the monoculture is robust.

## Anchors

Chosen for contrast:
- **`word`** → *serendipity* (43%) — an open, meme-driven attractor; expected fragile.
- **`tree`** → *oak* (94%) — the single strongest attractor in the whole census; if oak
  cracks, nothing is safe.

## Perturbation kinds

1. **Misspelling** — `wrod`, `treee`, `naem` (surface typo)
2. **Wording / synonym swap** — pick / choose / give / think-of (meaning-preserving)
3. **Article / quantifier** — a / any / one / the
4. **Register / format** — lowercase, politeness, no one-word clamp, terse (`A word:`)
5. **Persona / context injection** — "You are a poet. Name a tree." (`spec/persona.json`, run)
6. **Cross-lingual** — the ladder rerun in Hindi/Urdu (`spec/crosslingual_{hi,ur}.json`, planned)

`spec/perturb.json` covers 1–4 over both anchors (20 conditions).

## Findings so far

- **Kinds 1–4 (`transcripts_ladder`):** the strongest attractors are *deep* — oak survives
  typos and rewordings almost untouched (flip 2–9%); serendipity (weaker) scatters ~50% under
  any nudge but clings to modal. The biggest single lever is **format** — dropping the one-word
  clamp or going terse breaks both (flip 39–100%).
- **Kind 5, persona (`transcripts_persona`):** the interesting one. "Be wildly original" raises
  effective diversity **5–11×** — you *can* instruct diversity — but leaves a category-dependent
  **residual mode** (tree → baobab 47%): a shared prototype-of-originality. A `child` persona can
  *reduce* diversity (blue 81%). So the monoculture is a steerable default, not a hard ceiling.

## Metric

Per condition, vs its control: **flip%** (fraction of models whose own modal answer changed
from control — the direct brittleness measure), field modal + share, and **Δshare**
(convergence change; negative = the perturbation scattered the field).

## Run

```bash
python ../../harness/run.py --study . --spec spec/perturb.json --out transcripts --runs 4 <slugs>
../../.venv/bin/python analyze.py --transcripts transcripts
```

Roster is the 44-model consensus panel (`../language/spec/models.txt`). Status: **kinds 1–5 run
(44 models each); cross-lingual (6) specs built, not run.**
