"""stage_pick.py — where in training the two-turn pick moves away from the Name brand.

For each open pipeline with stage checkpoints (Tulu 3 8B, OLMo 3 7B; Nemotron 3.5 Lightning has only its final
model) and each tuned stage, over the brand categories (the generic company/brand ones left out):
  * own move: share of categories where the stage's most common pick differs from its own most common one-word Name
    brand (probes/verb_ladder_<p>/stimulus_brands*), against a floor from two halves of the stage's own Name runs
  * panel brands: over the categories where the API panel's two-turn pick differs from its Name brand, the share of
    the stage's picks naming the panel's pick brand, and the share naming its Name brand
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


def main():
    random.seed(0)
    lv = B.levels()
    panel_name = {c: B.top(n)[0] for c, n in B.agg(lv["name"]).items()}
    panel_pick = {c: B.top(n)[0] for c, n in B.agg(lv["pick2"]).items()}
    differ = {c for c in panel_name if panel_pick.get(c) and panel_pick[c] != panel_name[c] and c not in B.GENERIC}
    out = {"categories_where_panel_pick_differs": sorted(differ), "pipelines": {}}
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
            picks = {}
            for sid, sc in json.loads(pf.read_text())["scenes"].items():
                c = sid.removesuffix("__pick")
                if c in B.GENERIC:
                    continue
                picks[c] = [B.committed(c, r[1]["reply"]) for r in sc["runs"]
                            if r and len(r) > 1 and (r[1].get("reply") or "").strip()]
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
    (HERE / "probes" / "stage_pick.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
