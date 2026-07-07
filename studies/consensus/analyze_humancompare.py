"""analyze_humancompare.py — pull the human-norms comparison and the persona experiment
together, and update probes/humannorms.json (used by the figure).

  * Experiment A (exactword.json): override the model-field numbers for the 6 wording-mismatch
    categories with the VO-exact-wording rerun, so the figure is apples-to-apples.
  * Experiment B (persona.json): baseline vs persona vs human -- modal share, distinct>=5%,
    and effective population size (inverse Simpson, 1/sum p_i^2). Does the anti-mode prompt
    move the field toward the human spread, or just to a new mode?

    ../../.venv/bin/python analyze_humancompare.py
"""
import json, sys
from pathlib import Path
from collections import Counter
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from analyze import norm, load

def merged_pool(answers):
    """Counter of normalized answers with the study's singular/plural merge."""
    pool = Counter(a for a in answers if a)
    stems = {w: w[:-1] for w in pool if w.endswith("s") and w[:-1] in pool}
    return Counter(stems.get(a, a) for a in answers if a)

def field_from_replies(replies, cat):
    """replies: {label:{cat:[reply,...]}} -> merged Counter of normalized answers for cat."""
    toks = [norm(r) for lab in replies for r in replies[lab].get(cat, []) if r]
    return merged_pool([t for t in toks if t])

def stats(pool):
    n = sum(pool.values())
    ps = np.array([v / n for v in pool.values()])
    modal, mc = pool.most_common(1)[0]
    return {"modal": modal, "modal_share": round(mc / n, 3),
            "n_ge5": int(sum(1 for p in ps if p >= 0.05)),
            "eff_n": round(float(1.0 / np.sum(ps ** 2)), 2), "n": n}

# baseline model field (our prompts)
ans = load(HERE)
models = sorted(m for m in ans if ans[m])
cats = sorted({c for m in models for c in ans[m]})
for c in cats:
    ans_c = [a for m in models for a in ans[m].get(c, [])]
    stems = {w: w[:-1] for w in Counter(ans_c) if w.endswith("s") and w[:-1] in Counter(ans_c)}
    for m in models:
        if c in ans[m]:
            ans[m][c] = [stems.get(a, a) for a in ans[m][c]]
def baseline_pool(cat):
    return merged_pool([a for m in models for a in ans[m].get(cat, [])])

exact = json.loads((HERE / "probes/exactword.json").read_text())["replies"]
persona = json.loads((HERE / "probes/persona.json").read_text())["replies"]
hn = json.loads((HERE / "probes/humannorms.json").read_text())

OVERLAP = [r["category"] for r in hn["per_category"]]

print(f"{'cat':11} | {'MODEL modal (base/exact)':>24} | {'PERSONA modal':>14} | eff-N base/persona")
print("-" * 78)
rows = []
for cat in OVERLAP:
    base = stats(baseline_pool(cat))
    exact_s = stats(field_from_replies(exact, cat)) if cat in next(iter(exact.values())) else None
    pers = stats(field_from_replies(persona, cat))
    model_modal = exact_s["modal_share"] if exact_s else base["modal_share"]
    rows.append({"category": cat, "base": base, "exact": exact_s, "persona": pers,
                 "model_modal_used": model_modal})
    ex = f'{exact_s["modal_share"]:.0%}' if exact_s else "  -"
    print(f"{cat:11} | base {base['modal_share']:4.0%}  exact {ex:>4} | "
          f"{pers['modal']:>8} {pers['modal_share']:4.0%} | {base['eff_n']:.1f} / {pers['eff_n']:.1f}")

# aggregate: does persona move the field toward the human spread?
base_mod = np.mean([r["base"]["modal_share"] for r in rows])
pers_mod = np.mean([r["persona"]["modal_share"] for r in rows])
base_eff = np.mean([r["base"]["eff_n"] for r in rows])
pers_eff = np.mean([r["persona"]["eff_n"] for r in rows])
hum_mod = hn["mean_human_modal_first"]
print("-" * 78)
print(f"mean modal share:  human {hum_mod:.0%}   model-baseline {base_mod:.0%}   persona {pers_mod:.0%}")
print(f"mean effective-N:  model-baseline {base_eff:.1f}   persona {pers_eff:.1f}   (human ref ~{hn['mean_human_n_ge5']} at >=5%)")

# update humannorms.json: use exact-wording model modal shares for the mismatch cats
for r in hn["per_category"]:
    match = next(x for x in rows if x["category"] == r["category"])
    if match["exact"]:
        r["model_modal"] = match["exact"]["modal"]
        r["model_modal_share"] = match["exact"]["modal_share"]
        r["model_n_ge5"] = match["exact"]["n_ge5"]
        r["exact_wording"] = True
m = np.array([r["model_modal_share"] for r in hn["per_category"]])
h = np.array([r["human_modal_first"] for r in hn["per_category"]])
hn["mean_model_modal_share"] = round(float(m.mean()), 3)
hn["model_more_concentrated_n"] = int((m > h).sum())
hn["reversals"] = [r["category"] for r in hn["per_category"] if r["human_modal_first"] > r["model_modal_share"]]
hn["persona"] = {"mean_modal_share": round(float(pers_mod), 3),
                 "mean_eff_n": round(float(pers_eff), 2),
                 "baseline_mean_eff_n": round(float(base_eff), 2),
                 "system": json.loads((HERE / "probes/persona.json").read_text())["system"]}
(HERE / "probes/humannorms.json").write_text(json.dumps(hn, indent=1) + "\n")
print(f"\nupdated humannorms.json: model more concentrated {hn['model_more_concentrated_n']}/20, "
      f"reversals now {hn['reversals']}")
