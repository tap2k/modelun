"""probe_fingerprint_robust.py — does the fingerprint survive a system prompt, a changed verb and the passage of weeks?

The fourteen models of the perturbation check (probe_perturb.py, transcripts-perturb/<variant>/, 31 census questions,
8 runs, collected 2026-10-01) are identified among the full panel (probe_fingerprint.panel(), profiles from all 8
panel answers per question, no system prompt) with the likelihood of probe_fingerprint.py. For each variant and each
budget (k questions x n answers), 20 random draws of questions and answers per model.

  base    a later-day rerun of the original stimulus
  sysgen  system prompt "You are a helpful assistant."
  ava     system prompt "You are Ava, a friendly assistant."
  choose  "Choose a" in place of "Name a" (a different question, reported as such)

Also reported:
  stability   share of (model, category) whose favourite answer on 2026-10-01 (base) matches the panel's favourite,
              against two halves of the same day's base samples (runs 0-3 vs 4-7)
  lineage     nearest panel model to Palmyra X5 and to Qwen3 235B 2507 (mean log-likelihood per question of all 8
              answers under each other model's profile)

    ../../.venv/bin/python probe_fingerprint_robust.py      # -> probes/fingerprint_robust.json
"""
import json, math, random, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import probe_fingerprint as pf
import probe_perturb as pp
from analyze import answers

BUDGETS = ((10, 2), (20, 2), (31, 2), (31, 4))
DRAWS = 20


def main():
    A = pf.panel()
    models = sorted(A)
    cats = sorted({c for m in A for c in A[m]})
    vocab = {c: len({a for m in models for a in A[m].get(c, [])}) + 1 for c in cats}
    prof = {m: {c: Counter(A[m].get(c, [])[:8]) for c in cats} for m in models}

    def ll(m, c, a):
        return math.log((prof[m][c][a] + 0.1) / (sum(prof[m][c].values()) + 0.1 * vocab[c]))

    def ident(obs):
        return max(models, key=lambda m: sum(ll(m, c, a) for c, a in obs))

    field = answers(HERE)
    rng = random.Random(0)
    res = {"models_in_panel": len(models), "draws": DRAWS, "identification": {}}
    for v in pp.VARIANTS:
        V = pp.variant(v, field)
        tm = sorted(m for m in V if m in A)
        row = {"models": len(tm)}
        for k, n in BUDGETS:
            hit = tot = 0
            for _ in range(DRAWS):
                for m in tm:
                    pool = [c for c in V[m] if c in vocab]
                    cs = rng.sample(pool, min(k, len(pool)))
                    obs = [(c, a) for c in cs for a in rng.sample(V[m][c], min(n, len(V[m][c])))]
                    hit += ident(obs) == m
                    tot += 1
            row[f"{k}x{n}"] = round(hit / tot, 3)
        res["identification"][v] = row
        print(v, row, flush=True)

    base = pp.variant("base", field)
    kept = total = halves = half_total = 0
    for m in base:
        if m not in A:
            continue
        for c, ans in base[m].items():
            if c in A[m] and A[m][c]:
                total += 1
                kept += Counter(ans).most_common(1)[0][0] == Counter(A[m][c][:8]).most_common(1)[0][0]
                if len(ans) >= 8:
                    half_total += 1
                    halves += Counter(ans[:4]).most_common(1)[0][0] == Counter(ans[4:8]).most_common(1)[0][0]
    res["stability"] = {"favourite_kept": kept, "of": total, "share": round(kept / total, 3),
                        "same_day_halves": halves, "halves_of": half_total, "halves_share": round(halves / half_total, 3)}
    print(res["stability"])

    def nearest(x):
        cs = [c for c in cats if len(A[x].get(c, [])) >= 8]
        sc = {m: sum(ll(m, c, a) for c in cs for a in A[x][c][:8]) / len(cs) for m in models if m != x}
        return [[m, round(sc[m], 2)] for m in sorted(sc, key=sc.get, reverse=True)[:3]]

    res["lineage"] = {x: nearest(x) for x in ("palmyra-x5", "qwen3-235b-a22b-2507")}
    print(res["lineage"])
    (HERE / "probes" / "fingerprint_robust.json").write_text(json.dumps(res, indent=1) + "\n")


if __name__ == "__main__":
    main()
