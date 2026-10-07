"""probe_split.py — does the field's convergence hold in the major labs alone, or is it carried by small models?
(census v3, the "it's only the small models" objection)

Groups from spec/models.json `origin`: major = us-frontier, chinese, enterprise; small = small-open, persona, search.
On the v3 battery (analyze.py "combined": 96 categories x 8 runs), per group and for the whole field:
  1. substrate: mean / median modal share over the 96 categories, categories with one answer >= 80%, the
     serendipity share of the unconstrained prompt, and how often the two groups share a modal answer;
  2. scorecard: mean / median surprisal against the whole field (the paper's score), and the major group re-scored
     against the major-only field;
  3. human norms (Van Overschelde 2004, analyze_humannorms.py's reading): models more concentrated than people, and
     mean modal share, on the 20 shared categories, per group;
  4. bootstrap 90% CIs, resampling models within each group (2000 draws), for mean modal share and mean surprisal,
     and the major - small difference;
  5. size sensitivity: the major group without its small members (SMALL_MAJOR), items 1-2 again;
  6. sampling noise: each model's surprisal re-estimated by resampling its own answers within each category (500
     draws); the mean of that SD per group against the between-model SD of surprisal in the group;
  7. leave one origin out: field mean / median modal share with each origin dropped.
Zero API calls.

    ../../.venv/bin/python probe_split.py [--pdf ~/Desktop/projects/modelUN/papers/vanoverschelde-2004-category-norms.pdf]
        -> probes/split_v3.json
"""
import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from analyze import analyze, answers  # noqa: E402

MAJOR = {"us-frontier", "chinese", "enterprise"}
SMALL = {"small-open", "persona", "search"}
# Major-lab models that are small or a small tier by name: haiku / mini / lite / small tiers, flash tiers outside
# Gemini, and open weights at or under ~35B total.
SMALL_MAJOR = ["claude-3-haiku", "claude-haiku-4.5", "gpt-4o-mini-2024-07-18", "gpt-5.4-mini", "gemini-3.1-flash-lite",
               "inkling-small", "muse-glimmer-30b", "qwen3.6-35b-a3b", "qwen3.5-27b", "qwen3.8-27b",
               "hunyuan-a13b-instruct", "glm-5.3-flash", "step-3.7-flash", "ling-3.0-flash", "granite-4.1-8b",
               "granite-4.2-8b", "granite-4.2-30b"]
UNCONSTRAINED = "any_word"
B = 2000
rng = np.random.default_rng(0)

ORIGIN = {e["label"]: e["origin"] for e in json.loads((HERE / "spec/models.json").read_text())["models"]}
ans = answers(HERE, "combined")
models = sorted(m for m in ans if ans[m])
cats = sorted({c for m in models for c in ans[m]})
pm = analyze(HERE, "combined", ans=ans)["per_model"]


def substrate(g):
    """Modal share per category over the pooled answers of g (a list; a repeated model counts again)."""
    sh, modes = {}, {}
    for c in cats:
        f = Counter()
        for m in g:
            f.update(ans[m].get(c, []))
        if f:
            modes[c], n = f.most_common(1)[0]
            sh[c] = n / sum(f.values())
    v = np.array(list(sh.values()))
    f = Counter(a for m in g for a in ans[m].get(UNCONSTRAINED, []))
    return {"models": len(set(g)), "mean_modal_share": float(v.mean()), "median_modal_share": float(np.median(v)),
            "categories_modal_ge_80": int((v >= 0.8).sum()),
            "serendipity_share": f["serendipity"] / sum(f.values()) if f else None,
            "top_unconstrained": f.most_common(5)}, modes


def per_answer(m, field):
    """category -> m's per-answer surprisals against the pooled answers of field (m excluded), add-one smoothed."""
    out = {}
    for c, mine in ans[m].items():
        pool = Counter()
        for o in field:
            if o != m:
                pool.update(ans[o].get(c, []))
        if pool and mine:
            tot, vocab = sum(pool.values()), len(set(pool) | set(mine))
            out[c] = np.array([-math.log2((pool.get(a, 0) + 1) / (tot + vocab)) for a in mine])
    return out


def score(pa):
    return float(np.concatenate(list(pa.values())).mean())


def boot_ci(x):
    return [float(np.percentile(x, 5)), float(np.percentile(x, 95))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", default="~/Desktop/projects/modelUN/papers/vanoverschelde-2004-category-norms.pdf")
    args = ap.parse_args()
    groups = {"all": models, "major": [m for m in models if ORIGIN.get(m) in MAJOR],
              "small": [m for m in models if ORIGIN.get(m) in SMALL]}
    groups["major_large"] = [m for m in groups["major"] if m not in SMALL_MAJOR]
    assert len(groups["major"]) + len(groups["small"]) == len(models), "a model has no origin"
    assert all(m in groups["major"] for m in SMALL_MAJOR), "SMALL_MAJOR names a model outside the major group"
    surp = {m: pm[m]["surprisal"] for m in models}

    res = {"battery": "census + expanded, 8 runs", "categories": len(cats), "groups": {}}
    modes = {}
    for k, g in groups.items():
        s, modes[k] = substrate(g)
        v = np.array([surp[m] for m in g])
        s.update({"surprisal_mean": float(v.mean()), "surprisal_median": float(np.median(v)),
                  "surprisal_sd": float(v.std(ddof=1)),
                  "self_distinct_mean": float(np.mean([pm[m]["self_distinct"] for m in g]))})
        res["groups"][k] = s
    # 1. shared modes
    res["same_mode_major_small"] = sum(modes["major"][c] == modes["small"].get(c) for c in cats)
    res["same_mode_majorlarge_small"] = sum(modes["major_large"][c] == modes["small"].get(c) for c in cats)
    res["modes_differ"] = {c: [modes["major"][c], modes["small"].get(c)] for c in cats if modes["major"][c] != modes["small"].get(c)}
    # 2. the major group re-scored against the major-only field
    for k in ("major", "major_large"):
        own = {m: score(per_answer(m, groups[k])) for m in groups[k]}
        res["groups"][k]["surprisal_own_field_mean"] = float(np.mean(list(own.values())))
        res["groups"][k]["surprisal_own_field_median"] = float(np.median(list(own.values())))
        res["groups"][k]["spearman_own_vs_whole_field"] = float(np.corrcoef(
            np.argsort(np.argsort([own[m] for m in groups[k]])), np.argsort(np.argsort([surp[m] for m in groups[k]])))[0, 1])
    # 3. human norms, per group
    try:
        from analyze_humannorms import parse_vo, merged, WORDING_MISMATCH
        from analyze import norm
        human = parse_vo(Path(args.pdf).expanduser())
        exact = json.loads((HERE / "probes/exactword.json").read_text())["replies"]
        hn = {}
        for k, g in groups.items():
            rows = []
            for c in sorted(human):
                h = max(f for _, f in human[c])
                if c in WORDING_MISMATCH:
                    f = merged([t for lab in exact if lab in g for r in exact[lab].get(c, []) if r for t in [norm(r)] if t])
                else:
                    f = Counter(a for m in g for a in ans[m].get(c, []))
                if f:
                    rows.append((h, f.most_common(1)[0][1] / sum(f.values())))
            hh, mm = np.array([r[0] for r in rows]), np.array([r[1] for r in rows])
            hn[k] = {"categories": len(rows), "model_more_concentrated": int((mm > hh).sum()),
                     "mean_model_modal_share": float(mm.mean()), "mean_human_modal_first": float(hh.mean())}
        res["human_norms"] = hn
    except FileNotFoundError:
        res["human_norms"] = None
    # 4. bootstrap over models within group
    bt = {}
    for k in ("major", "small", "major_large"):
        g = groups[k]
        ms, ss = [], []
        for _ in range(B):
            d = list(rng.choice(g, len(g)))
            ms.append(substrate(d)[0]["mean_modal_share"])
            ss.append(float(np.mean([surp[m] for m in d])))
        bt[k] = {"mean_modal_share": np.array(ms), "surprisal": np.array(ss)}
    res["bootstrap"] = {k: {q: boot_ci(v) for q, v in d.items()} for k, d in bt.items()}
    res["bootstrap"]["major_minus_small"] = {q: boot_ci(bt["major"][q] - bt["small"][q]) for q in ("mean_modal_share", "surprisal")}
    res["bootstrap"]["majorlarge_minus_small"] = {q: boot_ci(bt["major_large"][q] - bt["small"][q]) for q in ("mean_modal_share", "surprisal")}
    # 6. sampling noise in each model's score against the between-model spread
    noise = {}
    for m in models:
        pa = per_answer(m, models)
        draws = [float(np.concatenate([rng.choice(v, len(v)) for v in pa.values()]).mean()) for _ in range(500)]
        noise[m] = float(np.std(draws, ddof=1))
    res["sampling_noise"] = {k: {"mean_within_model_sd": float(np.mean([noise[m] for m in g])),
                                 "between_model_sd": res["groups"][k]["surprisal_sd"],
                                 "share_of_variance_from_noise": float(np.mean([noise[m] ** 2 for m in g]) / res["groups"][k]["surprisal_sd"] ** 2)}
                             for k, g in groups.items()}
    # 7. leave one origin out
    res["leave_one_origin_out"] = {}
    for o in sorted(set(ORIGIN[m] for m in models)):
        s, _ = substrate([m for m in models if ORIGIN[m] != o])
        res["leave_one_origin_out"][o] = {"dropped": sum(ORIGIN[m] == o for m in models),
                                          "mean_modal_share": s["mean_modal_share"], "median_modal_share": s["median_modal_share"],
                                          "categories_modal_ge_80": s["categories_modal_ge_80"]}
    res["small_major_dropped"] = SMALL_MAJOR

    print(f"{len(models)} models x {len(cats)} categories")
    print(f"{'group':12} {'n':>3} {'modal mean':>10} {'median':>7} {'>=80%':>5} {'serend.':>7} {'surp mean':>9} {'median':>7} {'own field':>9} {'noise sd':>8} {'between sd':>10}")
    for k, s in res["groups"].items():
        print(f"{k:12} {s['models']:3d} {s['mean_modal_share']:10.3f} {s['median_modal_share']:7.3f} {s['categories_modal_ge_80']:5d} "
              f"{s['serendipity_share']:7.2f} {s['surprisal_mean']:9.2f} {s['surprisal_median']:7.2f} "
              f"{s.get('surprisal_own_field_mean', float('nan')):9.2f} {res['sampling_noise'][k]['mean_within_model_sd']:8.3f} {s['surprisal_sd']:10.2f}")
    print(f"same mode, major vs small: {res['same_mode_major_small']} of {len(cats)}; major_large vs small: {res['same_mode_majorlarge_small']}")
    for k, d in res["bootstrap"].items():
        print(f"bootstrap {k:22} " + "  ".join(f"{q} [{a:+.3f}, {b:+.3f}]" for q, (a, b) in d.items()))
    if res["human_norms"]:
        for k, d in res["human_norms"].items():
            print(f"human norms {k:12} more concentrated {d['model_more_concentrated']}/{d['categories']}; modal {d['mean_model_modal_share']:.2f} vs people {d['mean_human_modal_first']:.2f}")
    for o, d in res["leave_one_origin_out"].items():
        print(f"without {o:12} (-{d['dropped']:2d}) modal mean {d['mean_modal_share']:.3f} median {d['median_modal_share']:.3f} >=80% {d['categories_modal_ge_80']}")
    (HERE / "probes/split_v3.json").write_text(json.dumps(res, indent=1, default=float) + "\n")
    print("-> probes/split_v3.json")


if __name__ == "__main__":
    main()
