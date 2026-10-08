"""stage_pick.py — where in training the two-turn pick moves away from the Name brand.

For each open pipeline with stage checkpoints (Tulu 3 8B, OLMo 3 7B; Nemotron 3.5 Lightning has only its final
model) and each tuned stage, over the brand categories (the generic company/brand ones left out):
  * own move: share of categories where the stage's most common pick differs from its own most common one-word Name
    brand (probes/verb_ladder_<p>/stimulus_brands*), against a floor from two halves of the stage's own Name runs
  * panel brands: over the categories where the API panel's two-turn pick differs from its Name brand, the share of
    the stage's picks naming the panel's pick brand, and the share naming its Name brand
  * the same picks with the list held fixed (pick2_from_sft/: each later stage picks from the SFT stage's turn-1
    lists), the panel-pick share with a 90% bootstrap interval over categories, and head to head: of the runs whose
    turn-1 list names both panel brands and whose pick is one of them, the share picking the panel's pick brand
  * pooled: the held-fixed picks plus pick2_from_sft_k/ (K picks per head-to-head list, probe_verb_ladder.py
    --picks=K), head to head with a 90% bootstrap interval over categories. K picks from one list are not independent,
    so the interval resamples categories, not picks
Picks are read as brand_ladder reads them (the brand the reply commits to). Zero API calls. Writes
probes/stage_pick.json.

    python3 stage_pick.py
"""
import json
import random
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import brand_ladder as B                 # noqa: E402
from analyze import load                 # noqa: E402

PIPES = {"tulu3-8b": ("sft", "dpo", "rl"), "olmo3-7b": ("sft", "dpo", "rl"), "nemotron35-lightning": ("final",)}


def top(xs):
    xs = [x for x in xs if x and x != B.NO_PICK]
    return Counter(xs).most_common(1)[0][0] if xs else None


def stage_file(folder, label):
    hits = sorted(folder.glob(f"{label}*.json"))
    return hits[0] if hits else None


def read_picks(pf):
    """category -> [(the brand the pick commits to, the pool brands of its turn-1 list)]"""
    pats, out = B.pools()[4], {}
    for sid, sc in json.loads(pf.read_text())["scenes"].items():
        c = sid.removesuffix("__pick")
        if c in B.GENERIC:
            continue
        out[c] = [(B.committed(c, r[1]["reply"]), B.mentions(r[0].get("reply") or "", pats[c])) for r in sc["runs"]
                  if r and len(r) > 1 and (r[1].get("reply") or "").strip()]
    return out


def boot90(hit):
    """Pooled share of category -> [bool], and its 90% bootstrap interval over categories."""
    cats = [c for c in hit if hit[c]]
    share = lambda cs: sum(sum(hit[c]) for c in cs) / sum(len(hit[c]) for c in cs)
    boot = sorted(share(random.choices(cats, k=len(cats))) for _ in range(1000))
    return share(cats), [boot[50], boot[949]]


def head_to_head(picks, cats, panel_pick, panel_name):
    """category -> [picked the panel's pick brand], over runs whose list names both panel brands and whose pick is one."""
    return {c: [p == panel_pick[c] for p, ls in picks.get(c, [])
                if panel_pick[c] in ls and panel_name[c] in ls and p in (panel_pick[c], panel_name[c])] for c in cats}


def held_fixed(picks, differ, panel_pick, panel_name):
    """Panel-pick share over the differing categories with a 90% bootstrap interval, and the head-to-head share."""
    cats = [c for c in sorted(differ) if any(p != B.NO_PICK for p, _ in picks.get(c, []))]
    share, ci = boot90({c: [p == panel_pick[c] for p, _ in picks[c] if p != B.NO_PICK] for c in cats})
    h2h = [x for xs in head_to_head(picks, cats, panel_pick, panel_name).values() for x in xs]
    return {"panel_pick": share, "ci90": ci,
            "head_to_head": sum(h2h) / len(h2h) if h2h else None, "head_to_head_n": len(h2h)}


def pooled(picks, differ, panel_pick, panel_name):
    """Head to head over the differing categories, with a 90% bootstrap interval over categories."""
    hit = head_to_head(picks, sorted(differ), panel_pick, panel_name)
    share, ci = boot90(hit)
    return {"head_to_head": share, "ci90": ci, "head_to_head_n": sum(map(len, hit.values())),
            "categories": sum(1 for v in hit.values() if v)}


def main():
    random.seed(0)
    lv = B.levels()
    panel_name = {c: B.top(n)[0] for c, n in B.agg(lv["name"]).items()}
    panel_pick = {c: B.top(n)[0] for c, n in B.agg(lv["pick2"]).items()}
    differ = {c for c in panel_name if panel_pick.get(c) and panel_pick[c] != panel_name[c] and c not in B.GENERIC}
    out = {"categories_where_panel_pick_differs": sorted(differ),
           "panel_brands": {c: {"name": panel_name[c], "pick": panel_pick[c]} for c in sorted(differ)}, "pipelines": {}}
    print(f"{'stage':28} {'own pick != own Name':>22} {'floor':>6}   {'= panel pick':>12} {'= panel Name':>12}"
          f"   (over {len(differ)} categories where the panel's pick differs)")
    for p, stages in PIPES.items():
        base = HERE / "probes" / f"verb_ladder_{p}"
        rows = {}
        for s in stages:
            label = f"{p}-{s}"
            pf = stage_file(base / "pick2", label)
            names = [f for d in ("stimulus_brands", "stimulus_brands_ext") if (f := stage_file(base / d, label))]
            if not pf:
                continue
            pairs = read_picks(pf)
            picks = {c: [p for p, _ in v] for c, v in pairs.items()}
            own = {}
            for f in names:
                for m, cats in load(HERE, "brands", paths=[f]).items():
                    own.update(cats)
            cats = [c for c in picks if own.get(c) and top(picks[c]) and top(own[c])]
            moved = sum(top(picks[c]) != top(own[c]) for c in cats) / len(cats) if cats else None
            floor = []
            for _ in range(50):
                k = 0
                for c in cats:
                    xs = list(own[c]); random.shuffle(xs)
                    k += top(xs[:len(xs) // 2]) != top(xs[len(xs) // 2:])
                floor.append(k / len(cats))
            dp = [x for c in differ if c in picks for x in picks[c] if x != B.NO_PICK]
            dc = [c for c in differ if c in picks for x in picks[c] if x != B.NO_PICK]
            row = {"categories": len(cats), "own_moved": moved, "floor": sum(floor) / len(floor) if cats else None,
                   "panel_pick": sum(x == panel_pick[c] for x, c in zip(dp, dc)) / len(dp) if dp else None,
                   "panel_name": sum(x == panel_name[c] for x, c in zip(dp, dc)) / len(dp) if dp else None,
                   "picks": len(dp)}
            rows[s] = row
            f = lambda v: "   -" if v is None else f"{v:4.0%}"
            print(f"{label:28} {f(row['own_moved']):>22} {f(row['floor']):>6}   {f(row['panel_pick']):>12} {f(row['panel_name']):>12}")
        out["pipelines"][p] = rows
    print(f"\nlist held fixed{'':13} {'= panel pick':>12} {'90% interval':>14}   {'head to head':>12}")
    out["held_fixed"] = {}
    for p, stages in PIPES.items():
        base = HERE / "probes" / f"verb_ladder_{p}"
        for s, sub in [(s, "pick2" if s == "sft" else "pick2_from_sft") for s in stages if "sft" in stages]:
            pf = stage_file(base / sub, f"{p}-{s}")
            if not pf:
                continue
            r = held_fixed(read_picks(pf), differ, panel_pick, panel_name)
            out["held_fixed"][f"{p}-{s}"] = r
            print(f"{p + '-' + s:28} {r['panel_pick']:>12.0%} {r['ci90'][0]:>6.0%}-{r['ci90'][1]:<6.0%}"
                  f"   {r['head_to_head']:>8.0%} (n {r['head_to_head_n']})")
    print(f"\npooled with K picks{'':10} {'head to head':>12} {'90% interval':>14}")
    out["held_fixed_pooled"] = {}
    for p, stages in PIPES.items():
        base = HERE / "probes" / f"verb_ladder_{p}"
        for s in (s for s in stages if "sft" in stages):
            kf = stage_file(base / "pick2_from_sft_k", f"{p}-{s}")
            pf = stage_file(base / ("pick2" if s == "sft" else "pick2_from_sft"), f"{p}-{s}")
            if not (kf and pf):
                continue
            picks = read_picks(pf)
            for c, v in read_picks(kf).items():
                picks[c] = picks.get(c, []) + v
            r = pooled(picks, differ, panel_pick, panel_name)
            out["held_fixed_pooled"][f"{p}-{s}"] = r
            print(f"{p + '-' + s:28} {r['head_to_head']:>12.0%} {r['ci90'][0]:>6.0%}-{r['ci90'][1]:<6.0%}"
                  f"   (n {r['head_to_head_n']}, {r['categories']} categories)")
    (HERE / "probes" / "stage_pick.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
