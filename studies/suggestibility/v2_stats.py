"""v2_stats.py — the reviewer-requested statistics for v2, computed from the existing data.

v1 reported TAGeff with a 90% bootstrap over items only and Benjamini-Hochberg at q = .10, and stated
the taste/consequential difference without a test. This script leaves those outputs untouched and
writes the v2 versions to probes/v2_stats.json:

  1. Nested bootstrap (items, then replies within each item x arm x side cell), 95% intervals, two-sided
     bootstrap p, BH at q = .05 (and at .10 for comparison with v1). Raw and answered-only TAGeff.
  2. Taste vs consequential: per panel, the mean over models of TAGeff(consequential) - TAGeff(taste),
     with items resampled within tier (shared across models, items being the random factor) and
     replies within cells; 95% interval and two-sided p. Also the count of models with the difference
     below zero.
  3. Both panels: v1's 45 models (the probes/righteffect files at tag suggestibility-arxiv-v1, read
     with git) and every model with both arms on main.

The ask arm is the main stimulus (transcripts/, item__askx / item__asky); the tag arm is
probes/righteffect/. Scoring is analyze.classify.

    python studies/suggestibility/v2_stats.py
"""
import json
from pathlib import Path
import numpy as np
from analyze import classify, CONSEQUENTIAL
from probe_righteffect import ITEMS

STUDY = Path(__file__).resolve().parent
B = 2000
rng = np.random.default_rng(7)


def v1_panel():
    """The 45 models with a tag-arm file at the v1 tag."""
    import subprocess
    out = subprocess.run(["git", "ls-tree", "--name-only", "suggestibility-arxiv-v1",
                          "studies/suggestibility/probes/righteffect/"], cwd=STUDY.parent.parent,
                         capture_output=True, text=True, check=True).stdout.split()
    return sorted(Path(p).stem for p in out)


CODE = {"affirm": 1, "reject": 0, "hedge": -1}


def codes(replies):
    return np.array([CODE[c] for c in (classify(r) for r in replies if r) if c is not None], dtype=int)


def load():
    data = {}
    for rp in sorted((STUDY / "probes" / "righteffect").glob("*.json")):
        m = rp.stem
        tp = STUDY / "transcripts" / f"{m}.json"
        if not tp.exists():
            continue
        sc = json.loads(tp.read_text())["scenes"]; tg = json.loads(rp.read_text())["tag"]
        cells = {}
        for item, *_ in ITEMS:
            c = {}
            for s in "xy":
                c[("ask", s)] = codes([r[0].get("reply") for r in sc.get(f"{item}__ask{s}", {}).get("runs", []) if r])
                c[("tag", s)] = codes(tg.get(item, {}).get(s, []))
            if all(len(v) for v in c.values()):
                cells[item] = c
        if len(cells) >= 15:
            data[m] = cells
    return data


def item_effects(cells, idx_draw=None, answered=False):
    """Per-item TAGeff for one draw. idx_draw maps (item, arm, side) -> resampled reply indices."""
    out = {}
    for item, c in cells.items():
        e = []
        for s in "xy":
            rates = []
            for arm in ("ask", "tag"):
                v = c[(arm, s)]
                if idx_draw is not None:
                    v = v[idx_draw[(item, arm, s)]]
                if answered:
                    v = v[v >= 0]
                    rates.append(v.mean() if len(v) else np.nan)
                else:
                    rates.append((v == 1).mean())
            e.append(rates[1] - rates[0])
        out[item] = np.nanmean(e) if not all(np.isnan(e)) else np.nan
    return out


def draw_indices(cells):
    return {(item, arm, s): rng.integers(0, len(c[(arm, s)]), len(c[(arm, s)]))
            for item, c in cells.items() for arm in ("ask", "tag") for s in "xy"}


def per_model(cells, answered=False):
    items = list(cells)
    point = np.nanmean(list(item_effects(cells, answered=answered).values()))
    boots = []
    for _ in range(B):
        pick = rng.choice(items, len(items))
        eff = item_effects(cells, draw_indices(cells), answered=answered)
        boots.append(np.nanmean([eff[i] for i in pick]))
    boots = np.array(boots)
    lo, hi = np.nanpercentile(boots, [2.5, 97.5])
    p = 2 * min(np.mean(boots <= 0), np.mean(boots >= 0))
    return {"tageff": float(point), "ci95": [float(lo), float(hi)], "p": float(min(1.0, max(p, 1 / B)))}


def bh(ps, q):
    ms = sorted(ps, key=ps.get); n = len(ms); k = 0
    for i, m in enumerate(ms, 1):
        if ps[m] <= q * i / n:
            k = i
    return set(ms[:k])


def tier_test(data, models):
    cons = [i for i, *_ in ITEMS if i in CONSEQUENTIAL]; taste = [i for i, *_ in ITEMS if i not in CONSEQUENTIAL]
    def stat(pick_c, pick_t, draws):
        diffs = []
        for m in models:
            eff = item_effects(data[m], draws.get(m))
            c = [eff[i] for i in pick_c if i in eff]; t = [eff[i] for i in pick_t if i in eff]
            if c and t:
                diffs.append(np.nanmean(c) - np.nanmean(t))
        return np.mean(diffs), diffs
    point, diffs = stat(cons, taste, {})
    boots = []
    for _ in range(B // 4):  # 500 joint draws: each re-scores every model
        draws = {m: draw_indices(data[m]) for m in models}
        boots.append(stat(list(rng.choice(cons, len(cons))), list(rng.choice(taste, len(taste))), draws)[0])
    boots = np.array(boots)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    p = 2 * min(np.mean(boots <= 0), np.mean(boots >= 0))
    tag_c = float(np.mean([np.nanmean([v for i, v in item_effects(data[m]).items() if i in CONSEQUENTIAL]) for m in models]))
    tag_t = float(np.mean([np.nanmean([v for i, v in item_effects(data[m]).items() if i not in CONSEQUENTIAL]) for m in models]))
    return {"mean_tageff_consequential": tag_c, "mean_tageff_taste": tag_t, "diff": float(point),
            "ci95": [float(lo), float(hi)], "p": float(min(1.0, max(p, 1 / len(boots)))),
            "models_with_cons_below_taste": int(sum(d < 0 for d in diffs)), "n_models": len(diffs)}


def main():
    data = load()
    panels = {"v1_45": [m for m in v1_panel() if m in data], "current": sorted(data)}
    res = {"method": "nested bootstrap (items, then replies within cells), 2000 draws, 95% CI, BH q=.05",
           "per_model": {}, "panels": {}}
    for m in panels["current"]:
        res["per_model"][m] = {"raw": per_model(data[m]), "answered": per_model(data[m], answered=True)}
        print(f"  {m:<30} {res['per_model'][m]['raw']['tageff']:+.1%} "
              f"[{res['per_model'][m]['raw']['ci95'][0]:+.1%}, {res['per_model'][m]['raw']['ci95'][1]:+.1%}]", flush=True)
    for name, ms in panels.items():
        out = {"n": len(ms)}
        for kind in ("raw", "answered"):
            ps = {m: res["per_model"][m][kind]["p"] for m in ms}
            sig = {q: bh(ps, q) for q in (0.05, 0.10)}
            eff = {m: res["per_model"][m][kind]["tageff"] for m in ms}
            out[kind] = {f"q{q}": {"resist": sum(1 for m in sig[q] if eff[m] < 0),
                                   "sycophantic": sum(1 for m in sig[q] if eff[m] > 0)} for q in (0.05, 0.10)}
            out[kind]["ci95_excludes_zero"] = {
                "resist": sum(1 for m in ms if res["per_model"][m][kind]["ci95"][1] < 0),
                "sycophantic": sum(1 for m in ms if res["per_model"][m][kind]["ci95"][0] > 0)}
            out[kind]["mean_tageff"] = float(np.mean(list(eff.values())))
        out["tier_test"] = tier_test(data, ms)
        res["panels"][name] = out
        t = out["tier_test"]
        print(f"\n== {name} (n={len(ms)}): mean TAGeff {out['raw']['mean_tageff']:+.1%}, answered {out['answered']['mean_tageff']:+.1%}")
        for kind in ("raw", "answered"):
            print(f"   {kind}: BH q=.05 resist {out[kind]['q0.05']['resist']} / syco {out[kind]['q0.05']['sycophantic']};"
                  f" q=.10 resist {out[kind]['q0.1']['resist']} / syco {out[kind]['q0.1']['sycophantic']};"
                  f" 95% CI excludes 0: resist {out[kind]['ci95_excludes_zero']['resist']} / syco {out[kind]['ci95_excludes_zero']['sycophantic']}")
        print(f"   taste vs consequential: cons {t['mean_tageff_consequential']:+.1%}, taste {t['mean_tageff_taste']:+.1%},"
              f" diff {t['diff']:+.1%} [{t['ci95'][0]:+.1%}, {t['ci95'][1]:+.1%}], p={t['p']:.3f};"
              f" {t['models_with_cons_below_taste']} of {t['n_models']} models have cons < taste")
    (STUDY / "probes" / "v2_stats.json").write_text(json.dumps(res, indent=1))
    print("\n-> probes/v2_stats.json")


if __name__ == "__main__":
    main()
