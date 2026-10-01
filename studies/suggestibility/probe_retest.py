"""probe_retest.py — test-retest of the two arms the headline rests on.

Re-collects, on a later date, the neutral ask arm (the main stimulus's item__askx / item__asky
prompts, verbatim) and the "right?" tag arm (probe_righteffect's tag_prompt), 20 items x both
options x 4 samples, temperature 1, no system prompt, the roster's provider pins. Budget is 8192
for every model: the reasoning models needed it in wave 2, and a Yes/No reply does not reach it
otherwise. The file records the date and budget.

  analyze: per model, TAGeff on the retest against TAGeff from the original collection
  (transcripts/ ask arm + probes/righteffect/ tag arm), and the same for the ask-arm affirm rate.
  Reports Spearman across models, the mean absolute per-model change, and how many models change
  the sign or the significance of their TAGeff.

    python studies/suggestibility/probe_retest.py run <slug>...
    python studies/suggestibility/probe_retest.py analyze
"""
import json, sys, time
from pathlib import Path
import numpy as np
import probe_righteffect as pr
from probe_righteffect import ITEMS, tag_prompt, arate

STUDY = Path(__file__).resolve().parent
OUT = STUDY / "probes" / "retest"
RUNS = 4
ASK = {sc["id"]: sc["turns"][0] for sc in json.loads((STUDY / "spec" / "stimulus.json").read_text())["scenes"]}


def run(slug):
    pr.MAX_TOKENS = 8192
    pr.PROVIDER = pr.META.get(slug, {}).get("provider")
    pr.TRACES.clear()
    label = slug.split("/")[-1]
    OUT.mkdir(parents=True, exist_ok=True)
    rec = {"model": label, "slug": slug, "date": time.strftime("%Y-%m-%d"), "max_tokens": 8192, "ask": {}, "tag": {}}
    if pr.PROVIDER:
        rec["provider"] = pr.PROVIDER
    for item, d, x, y in ITEMS:
        rec["ask"][item] = {"x": [pr.chat(slug, ASK[f"{item}__askx"]) for _ in range(RUNS)],
                            "y": [pr.chat(slug, ASK[f"{item}__asky"]) for _ in range(RUNS)]}
        rec["tag"][item] = {"x": [pr.chat(slug, tag_prompt(d, x)) for _ in range(RUNS)],
                            "y": [pr.chat(slug, tag_prompt(d, y)) for _ in range(RUNS)]}
        if pr.TRACES:
            rec["reasoning"] = list(pr.TRACES)
        (OUT / f"{label}.json").write_text(json.dumps(rec, indent=1))
        n = sum(1 for arm in ("ask", "tag") for s in "xy" for r in rec[arm][item][s] if r)
        print(f"  [{label}] {item}: {n}/{4 * RUNS}", flush=True)
    print(f"-> retest/{label}.json", flush=True)


def effect(ask_by_item, tag_by_item):
    per = []
    for item, *_ in ITEMS:
        a, t = arate(ask_by_item.get(item, [])), arate(tag_by_item.get(item, []))
        if a is not None and t is not None:
            per.append((t - a, a))
    return per


def ci(effs, rng):
    boots = [float(np.mean(rng.choice(effs, len(effs)))) for _ in range(2000)]
    return float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))


def rank(a):
    a = np.asarray(a, float); r = np.empty(len(a)); r[a.argsort()] = np.arange(len(a))
    for v in np.unique(a):
        r[a == v] = r[a == v].mean()
    return r


def analyze():
    rng = np.random.default_rng(7)
    res = {}
    for p in sorted(OUT.glob("*.json")):
        d = json.loads(p.read_text()); m = d["model"]
        tp, rp = STUDY / "transcripts" / f"{m}.json", STUDY / "probes" / "righteffect" / f"{m}.json"
        if not (tp.exists() and rp.exists()):
            continue
        sc = json.loads(tp.read_text())["scenes"]; tg = json.loads(rp.read_text())["tag"]
        orig = effect({i: [r[0].get("reply") for s in "xy" for r in sc.get(f"{i}__ask{s}", {}).get("runs", []) if r]
                       for i, *_ in ITEMS},
                      {i: tg.get(i, {}).get("x", []) + tg.get(i, {}).get("y", []) for i, *_ in ITEMS})
        new = effect({i: d["ask"][i]["x"] + d["ask"][i]["y"] for i in d["ask"]},
                     {i: d["tag"][i]["x"] + d["tag"][i]["y"] for i in d["tag"]})
        if len(orig) < 15 or len(new) < 15:
            continue
        o, n = [e for e, _ in orig], [e for e, _ in new]
        res[m] = {"tageff_orig": float(np.mean(o)), "tageff_retest": float(np.mean(n)),
                  "ci95_orig": ci(o, rng), "ci95_retest": ci(n, rng),
                  "ask_orig": float(np.mean([a for _, a in orig])), "ask_retest": float(np.mean([a for _, a in new])),
                  "retest_date": d["date"], "n_items": min(len(o), len(n))}
    if not res:
        print("no models with both collections"); return
    ms = sorted(res)
    def rho(k1, k2):
        return float(np.corrcoef(rank([res[m][k1] for m in ms]), rank([res[m][k2] for m in ms]))[0, 1])
    sig = lambda c: -1 if c[1] < 0 else (1 if c[0] > 0 else 0)
    summary = {"n_models": len(ms),
               "spearman_tageff": rho("tageff_orig", "tageff_retest"),
               "spearman_ask": rho("ask_orig", "ask_retest"),
               "mean_abs_change_tageff": float(np.mean([abs(res[m]["tageff_retest"] - res[m]["tageff_orig"]) for m in ms])),
               "sign_flips": sum(1 for m in ms if res[m]["tageff_orig"] * res[m]["tageff_retest"] < 0),
               "significance_changes": sum(1 for m in ms if sig(res[m]["ci95_orig"]) != sig(res[m]["ci95_retest"])),
               "panel_mean_orig": float(np.mean([res[m]["tageff_orig"] for m in ms])),
               "panel_mean_retest": float(np.mean([res[m]["tageff_retest"] for m in ms]))}
    (STUDY / "probes" / "retest_analysis.json").write_text(json.dumps({"summary": summary, "per_model": res}, indent=1))
    print(f"\n{'model':<28}{'orig':>7}{'retest':>8}{'change':>8}")
    for m in sorted(ms, key=lambda m: res[m]["tageff_orig"]):
        r = res[m]
        print(f"{m:<28}{r['tageff_orig']:>+7.0%}{r['tageff_retest']:>+8.0%}{r['tageff_retest'] - r['tageff_orig']:>+8.0%}")
    print("\n" + json.dumps(summary, indent=1))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "analyze":
        analyze()
    elif len(sys.argv) > 2 and sys.argv[1] == "run":
        for s in sys.argv[2:]:
            run(s)
    else:
        print(__doc__)
