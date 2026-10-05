"""brand_confounds.py — the checks the brand gradient needs before it is read as a verb or conversation effect.

  1. list position: in the two-turn pick, where the picked brand sits in the model's own turn-1 list (first, second,
     third or later, not listed), and how often the model's one-word Name brand was listed at all
  2. by lab: per vendor with at least three models, how often its models keep their own Name brand under clamped
     Recommend and in the two-turn pick, and in how many categories the vendor's own consensus moves from Name
  3. by category: which categories move from Name, at which level, and which hold at every level
  4. paraphrase floor: free Recommend against two rewordings on the 14-model perturbation subset (as served)

Everything as served, 44 categories, scored as brand_ladder.py scores it. Zero API calls. Writes
probes/brand_confounds.json.

    ../../.venv/bin/python brand_confounds.py
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import brand_ladder as B  # noqa: E402

NONE = B.NO_PICK
DIRS = {e["id"]: e["dir"] for e in json.loads((HERE / "spec/runs.json").read_text())["runs"]}
VENDOR = {e["label"]: e["slug"].split("/")[0] for e in json.loads((HERE / "spec/models.json").read_text())["models"]}


def top(cnt):
    return B.top(cnt)[0]


def list_position():
    pats, dflt = B.pools()[4], B.defaults()
    pos, in_list, n = Counter(), 0, 0
    for rid in ("brands-pick2-free", "brands-ext2-pick2-free"):
        for f in sorted((HERE / DIRS[rid]).glob("*.json")):
            x = json.loads(f.read_text())
            for sid, s in x["scenes"].items():
                c = sid.removesuffix("__pick")
                if c not in pats:
                    continue
                for r in s["runs"]:
                    if not r or len(r) < 2 or any(t.get("error") or not (t.get("reply") or "").strip() for t in r[:2]):
                        continue
                    pick = B.committed(c, r[1]["reply"])
                    if pick == NONE:
                        continue
                    listed = B.mentions(r[0]["reply"], pats[c])
                    n += 1
                    in_list += dflt.get(x["model"], {}).get(c) in listed
                    i = listed.index(pick) if pick in listed else None
                    pos["first" if i == 0 else "second" if i == 1 else "third or later" if i is not None else "not listed"] += 1
    return {"picks": n, "position": {k: v / n for k, v in pos.items()}, "own_name_brand_listed": in_list / n}


def by_lab(lv):
    dflt = B.defaults()
    fams = defaultdict(list)
    for m in lv["name"]:
        fams[VENDOR.get(m, "?")].append(m)
    out = {}
    for v, ms in sorted(fams.items()):
        if len(ms) < 3:
            continue
        row = {"models": len(ms)}
        for lab, level in (("recommend_clamp", "recommend_clamp"), ("pick2", "pick2")):
            kept = []
            for m in ms:
                for c, xs in lv[level].get(m, {}).items():
                    d = dflt.get(m, {}).get(c)
                    ys = [y for y in xs if y != NONE]
                    if d and ys:
                        kept.append(sum(y == d for y in ys) / len(ys))
            row[f"own_kept_{lab}"] = sum(kept) / len(kept) if kept else None
            name = B.agg({m: lv["name"][m] for m in ms if m in lv["name"]})
            other = B.agg({m: lv[level][m] for m in ms if m in lv[level]})
            cats = [c for c in name if c in other and top(other[c])]
            row[f"consensus_moved_{lab}"] = sum(top(name[c]) != top(other[c]) for c in cats) / len(cats) if cats else None
        out[v] = row
    return out


def by_category(lv):
    levels = ["choose", "recommend_clamp", "free_choose", "recommend", "pick2"]
    name = {c: top(n) for c, n in B.agg(lv["name"]).items()}
    tops = {k: {c: top(n) for c, n in B.agg(lv[k]).items()} for k in levels}
    rows = {c: {"name": name[c], **{k: tops[k].get(c) for k in levels}} for c in sorted(name)}
    for r in rows.values():
        r["levels_moved"] = sum(r[k] not in (None, r["name"]) for k in levels)
    return rows


def paraphrase(lv):
    sub = {"recommend": lv["recommend"],
           "recommend2": B.load("perturb-recommend2", "__recommend2", 0, "first"),
           "recommend3": B.load("perturb-recommend3", "__recommend3", 0, "first")}
    ms = set(sub["recommend2"])
    tops = {k: {c: top(n) for c, n in B.agg({m: d[m] for m in ms if m in d}).items()} for k, d in sub.items()}
    name = {c: top(n) for c, n in B.agg({m: lv["name"][m] for m in ms if m in lv["name"]}).items()}
    out = {"models": len(ms)}
    for a, b in (("recommend", "recommend2"), ("recommend", "recommend3"), ("recommend2", "recommend3")):
        cats = [c for c in tops[a] if c in tops[b]]
        out[f"{a}_vs_{b}_same"] = f"{sum(tops[a][c] == tops[b][c] for c in cats)}/{len(cats)}"
    for k in sub:
        cats = [c for c in tops[k] if c in name]
        out[f"{k}_differs_from_name"] = f"{sum(tops[k][c] != name[c] for c in cats)}/{len(cats)}"
    return out


def main():
    lv = B.levels()
    out = {"list_position": list_position(), "by_lab": by_lab(lv), "by_category": by_category(lv),
           "paraphrase": paraphrase(lv)}
    (HERE / "probes" / "brand_confounds.json").write_text(json.dumps(out, indent=1) + "\n")
    lp = out["list_position"]
    print(f"1. two-turn pick, {lp['picks']} picks: " + ", ".join(f"{k} {v:.0%}" for k, v in sorted(lp["position"].items(), key=lambda kv: -kv[1]))
          + f"; the model's own Name brand was in its turn-1 list {lp['own_name_brand_listed']:.0%}")
    print("\n2. by lab (vendors with >= 3 models): own Name brand kept, and consensus moved from Name")
    print(f"   {'vendor':14} {'models':>6}  {'Recommend kept':>14} {'moved':>6}   {'two-turn kept':>13} {'moved':>6}")
    for v, r in sorted(out["by_lab"].items(), key=lambda kv: -kv[1]["models"]):
        f = lambda x: "  -" if x is None else f"{x:.0%}"
        print(f"   {v:14} {r['models']:6}  {f(r['own_kept_recommend_clamp']):>14} {f(r['consensus_moved_recommend_clamp']):>6}   "
              f"{f(r['own_kept_pick2']):>13} {f(r['consensus_moved_pick2']):>6}")
    rows = out["by_category"]
    moved = Counter(r["levels_moved"] for r in rows.values())
    print(f"\n3. by category, levels (of 5) where the consensus differs from Name: "
          + ", ".join(f"{k} levels: {moved[k]} categories" for k in sorted(moved)))
    print("   hold at every level: " + ", ".join(f"{c} ({r['name']})" for c, r in rows.items() if r["levels_moved"] == 0))
    print("   move at every level: " + ", ".join(f"{c} ({r['name']} -> {r['pick2']})" for c, r in rows.items() if r["levels_moved"] == 5))
    print(f"\n4. paraphrase floor: {out['paraphrase']}")


if __name__ == "__main__":
    main()
