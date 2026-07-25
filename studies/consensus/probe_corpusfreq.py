"""probe_corpusfreq.py — does the field's mode just echo corpus frequency?

The deflationary null for the frictionless-prototype reading (paper §4.1): models pick the
modal answer because it is the most corpus-frequent member of the category. Test it against
the field's own support — for each category, every distinct answer any model gave, with its
pooled count — scored by wordfreq's Zipf frequency (Speer 2022; multi-corpus English). No
category-membership oracle is needed: the field itself certified every support word as a
valid answer, and if frequency set the mode, the mode would be the support's frequency-top.

Per category: is the modal answer the frequency-top of the support? what is its frequency
rank? tie-aware Spearman rho between pooled answer count and Zipf across the support
(categories with >=5 distinct answers). Aggregates + the named head-to-heads the paper
quotes (carrot/potato, serendipity). No new API calls.

    ../../.venv/bin/python probe_corpusfreq.py   -> probes/corpusfreq.json
"""

import json
import sys
from pathlib import Path
from collections import Counter

import numpy as np
from wordfreq import zipf_frequency

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from analyze import load

ans = load(HERE)
models = sorted(m for m in ans if ans[m])
cats = sorted({c for m in models for c in ans[m]})
for c in cats:  # plural merge, identical to analyze.py
    pool = Counter(a for m in models for a in ans[m].get(c, []))
    stems = {w: w[:-1] for w in pool if w.endswith("s") and w[:-1] in pool}
    for m in models:
        if c in ans[m]:
            ans[m][c] = [stems.get(a, a) for a in ans[m][c]]


def avg_ranks(x):
    """Average ranks with ties (needed: support counts are mostly ties at 1)."""
    x = np.asarray(x, dtype=float)
    order = np.argsort(x, kind="stable")
    r = np.empty(len(x))
    i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and x[order[j + 1]] == x[order[i]]:
            j += 1
        r[order[i:j + 1]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(x, y):
    rx, ry = avg_ranks(x), avg_ranks(y)
    if rx.std() == 0 or ry.std() == 0:
        return float("nan")
    return float(np.corrcoef(rx, ry)[0, 1])


per_cat = []
for c in cats:
    pool = Counter(a for m in models for a in ans[m].get(c, []))
    if not pool:
        continue
    words = sorted(pool, key=lambda w: -pool[w])
    zipf = {w: zipf_frequency(w, "en") for w in words}
    modal, modal_n = pool.most_common(1)[0]
    by_freq = sorted(words, key=lambda w: -zipf[w])
    total = sum(pool.values())
    # share ∝ corpus frequency over the same support (Zipf is log10 of per-billion rate)
    lin = {w: 10.0 ** zipf[w] for w in words}
    freqprop = {w: lin[w] / sum(lin.values()) for w in words}
    rec = {
        "category": c,
        "n_distinct": len(words),
        "modal": modal,
        "modal_share": round(modal_n / total, 3),
        "modal_zipf": round(zipf[modal], 2),
        "freq_top": by_freq[0],
        "freq_top_zipf": round(zipf[by_freq[0]], 2),
        "freq_top_share": round(pool[by_freq[0]] / total, 3),
        "modal_is_freq_top": by_freq[0] == modal,
        "modal_freq_rank": by_freq.index(modal) + 1,
        "freqprop_modal_share": round(freqprop[modal], 3),
        "freqprop_top_share": round(max(freqprop.values()), 3),
        "rho_count_zipf": (round(spearman([pool[w] for w in words],
                                          [zipf[w] for w in words]), 3)
                           if len(words) >= 5 else None),
    }
    per_cat.append(rec)

n = len(per_cat)
hits = [r for r in per_cat if r["modal_is_freq_top"]]
rhos = [r["rho_count_zipf"] for r in per_cat if r["rho_count_zipf"] is not None]
ranks = [r["modal_freq_rank"] for r in per_cat]
# cross-category: do stronger modes sit on more frequent words? (frictionless reading: no)
rho_share_zipf = spearman([r["modal_share"] for r in per_cat],
                          [r["modal_zipf"] for r in per_cat])

veg = next(r for r in per_cat if r["category"] == "vegetable")
anyw = next(r for r in per_cat if r["category"] == "any_word")
veg_pool = Counter(a for m in models for a in ans[m].get("vegetable", []))

result = {
    "source": "wordfreq (Speer), Zipf scale, English; candidates = field support per category",
    "n_categories": n,
    "modal_is_freq_top_n": len(hits),
    "modal_is_freq_top_cats": sorted(r["category"] for r in hits),
    "median_modal_freq_rank": float(np.median(ranks)),
    "rho_count_zipf_mean": round(float(np.mean(rhos)), 3),
    "rho_count_zipf_median": round(float(np.median(rhos)), 3),
    "rho_count_zipf_n": len(rhos),
    "rho_count_zipf_positive_n": sum(r > 0 for r in rhos),
    "rho_modalshare_modalzipf": round(rho_share_zipf, 3),
    "mean_observed_modal_share": round(float(np.mean([r["modal_share"] for r in per_cat])), 3),
    "mean_freqprop_top_share": round(float(np.mean([r["freqprop_top_share"] for r in per_cat])), 3),
    "mean_freqprop_modal_share": round(float(np.mean([r["freqprop_modal_share"] for r in per_cat])), 3),
    "headliners": {
        "vegetable": {"carrot": {"zipf": veg["modal_zipf"], "share": veg["modal_share"]},
                      "potato": {"zipf": round(zipf_frequency("potato", "en"), 2),
                                 "count": veg_pool.get("potato", 0),
                                 "of": sum(veg_pool.values())},
                      "tomato": {"zipf": round(zipf_frequency("tomato", "en"), 2),
                                 "count": veg_pool.get("tomato", 0)}},
        "any_word": {"modal": anyw["modal"], "modal_zipf": anyw["modal_zipf"],
                     "modal_share": anyw["modal_share"],
                     "modal_freq_rank": anyw["modal_freq_rank"],
                     "n_distinct": anyw["n_distinct"],
                     "freq_top": anyw["freq_top"], "freq_top_zipf": anyw["freq_top_zipf"],
                     "freq_top_share": anyw["freq_top_share"]},
    },
    "per_category": per_cat,
}

(HERE / "probes").mkdir(exist_ok=True)
(HERE / "probes" / "corpusfreq.json").write_text(json.dumps(result, indent=1) + "\n")

print(f"modal == frequency-top of support: {len(hits)}/{n} categories "
      f"({', '.join(r['category'] for r in hits)})")
print(f"median frequency rank of modal within support: {np.median(ranks):.0f}")
print(f"rho(count, zipf) over support: mean {np.mean(rhos):+.2f}, median {np.median(rhos):+.2f} "
      f"({sum(r > 0 for r in rhos)}/{len(rhos)} positive)")
print(f"rho(modal share, modal zipf) across categories: {rho_share_zipf:+.2f}")
print(f"mean modal share: observed {np.mean([r['modal_share'] for r in per_cat]):.0%} vs "
      f"frequency-proportional sampler {np.mean([r['freqprop_top_share'] for r in per_cat]):.0%} "
      f"(its modal would give ours {np.mean([r['freqprop_modal_share'] for r in per_cat]):.0%})")
print(f"{'category':<12}{'modal':<14}{'zipf':>5}{'rank':>5}  {'freq_top':<14}{'zipf':>5}{'share':>7}{'rho':>7}")
for r in sorted(per_cat, key=lambda r: -r["modal_share"]):
    rho = f"{r['rho_count_zipf']:+.2f}" if r["rho_count_zipf"] is not None else "  --"
    print(f"{r['category']:<12}{r['modal']:<14}{r['modal_zipf']:>5.2f}{r['modal_freq_rank']:>5}  "
          f"{r['freq_top']:<14}{r['freq_top_zipf']:>5.2f}{r['freq_top_share']:>7.1%}{rho:>7}")
print("-> probes/corpusfreq.json")
