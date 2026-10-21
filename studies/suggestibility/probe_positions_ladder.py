"""probe_positions_ladder.py — the positions instrument (probe_contested_assert.py) on the local stage ladders.

At which post-training stage does a model take a side when told to, answer claim and mirror as one position, and
keep the side its plain-clamp answer gives? The 18 contested items x 2 mirror sides (probe_contested.ITEMS), with
the assertive sentence (probe_contested_unclamped.ASSERT) from one of two places:

  sys    the sentence as the system message, the clamp's user turn verbatim (the panel instrument). Framing "assert",
         instruct stages only.
  user   "<sentence> <question> Reply with only Yes or No." as the user turn, in each stage's default framings
         (raw for a base, which has no roles). Who gives the instruction is a dimension of the positions paper.

16 samples per cell, temperature 1, 8 tokens, scored by first word (analyze.classify). One Contract-A file per
stage/framing in probes/positions_ladder_<size>/<arm>/, scene <item>__<side>. The plain clamp is the ask arm of
probe_contested_ladder (probes/contested_ladder_<size>/), same stage: the user arm is compared with the clamp in the
same framing, the sys arm with the clamp under chat.

Per stage/framing, overall and by stratum (history / policy / hot): answered, hedge and none rates; side taken
(probe_contested_unclamped.side_of: x, y or neither) and coherent rate per item; agreement with the clamp's side where
both take one; and on the 9 LEFT-coded items the affirm rate of the left- vs right-coded claim.

    ../../.venv/bin/python probe_positions_ladder.py --32b [N=16]   # sample both arms, then score
    ../../.venv/bin/python probe_positions_ladder.py --32b --score
    --7b, --tulu, --nemotron pick the other pipelines (probe_suggest_ladder's flags).
"""
import json, sys
import numpy as np
from probe_suggest_ladder import HERE, SIZE, PIPELINE
from probe_contested import ITEMS, LEFT, CLAMP
from probe_contested_unclamped import ASSERT, side_of, coherent
from analyze import classify
import local

DIR, OUT = HERE / "probes" / f"positions_ladder_{SIZE}", HERE / "probes" / f"positions_ladder_{SIZE}.json"
CLAMP_DIR = HERE / "probes" / f"contested_ladder_{SIZE}"
STRATUM = {sid: st for sid, st, _, _ in ITEMS}
ARMS = {"sys": lambda q: f"{q} {CLAMP}", "user": lambda q: f"{ASSERT} {q} {CLAMP}"}
local.LADDERS[PIPELINE].setdefault("system_prompts", {})["assert"] = ASSERT   # the sys arm's framing


def sample(n):
    for st in local.stages(PIPELINE):
        jobs = [("user", f) for f in st["framings"]] + ([("sys", "assert")] if st["stage"] != "base" and
                                                         st["framings"] != ["raw"] else [])
        jobs = [(a, f) for a, f in jobs if not local.path(DIR / a, st, f).exists()]
        if not jobs:
            continue
        model = local.load(st)
        for arm, framing in jobs:
            spec = {"spec_version": f"probe_positions_ladder/{arm}",
                    "scenes": [{"id": f"{sid}__{side}", "turns": [ARMS[arm](q)]}
                               for sid, _, (qx, _), (qy, _) in ITEMS for side, q in (("x", qx), ("y", qy))]}
            local.run(spec, st, framing, n, local.path(DIR / arm, st, framing), 8, batch=64, model=model)
        del model
        local.free()


def labels(path, arm_of_scene=lambda sid: sid):
    """{item: {side: [labels]}} from a Contract-A file; arm_of_scene maps a scene id to <item>__<side> or None."""
    out = {}
    for sid, sc in json.loads(path.read_text())["scenes"].items():
        key = arm_of_scene(sid)
        if key:
            item, side = key.rsplit("__", 1)
            out.setdefault(item, {})[side] = [classify(r[0]["reply"] or "") for r in sc["runs"]]
    return out


def clamp(st, framing):
    """The stage's plain-clamp ask arm (probe_contested_ladder's scene <item>__ask<side>)."""
    p = local.path(CLAMP_DIR, st, framing)
    return labels(p, lambda sid: sid.replace("__ask", "__") if "__ask" in sid else None) if p.exists() else None


def block(M, C):
    ls = [l for it in M.values() for sd in it.values() for l in sd]
    sides = {it: side_of(M[it]["x"], M[it]["y"]) for it in M}
    took = [it for it, s in sides.items() if s in ("x", "y")]
    out = {"answered": round(sum(l in ("affirm", "reject") for l in ls) / len(ls), 3),
           "hedge": round(ls.count("hedge") / len(ls), 3), "none": round(ls.count(None) / len(ls), 3),
           "side_taken": round(len(took) / len(M), 3),
           "coherent": round(sum(coherent(M[it]["x"], M[it]["y"]) for it in M) / len(M), 3),
           "sides": sides}
    if C:
        both = [it for it in took if side_of(C[it]["x"], C[it]["y"]) in ("x", "y")]
        out["clamp_side_taken"] = round(sum(side_of(C[it]["x"], C[it]["y"]) in ("x", "y") for it in M) / len(M), 3)
        out["same_side_as_clamp"] = [sum(sides[it] == side_of(C[it]["x"], C[it]["y"]) for it in both), len(both)]
    return out


def score():
    summary = {}
    stages = {st["stage"]: st for st in local.stages(PIPELINE)}
    for arm in ARMS:
        for p in sorted((DIR / arm).glob("*.json"), key=lambda p: (list(stages).index(json.loads(p.read_text())["stage"]), p.name)):
            d = json.loads(p.read_text())
            st, M = stages[d["stage"]], labels(p)
            C = clamp(st, "chat" if arm == "sys" else d["framing"])
            row = block(M, C)
            row["by_stratum"] = {s: {k: v for k, v in block({i: M[i] for i in M if STRATUM[i] == s},
                                                            C and {i: C[i] for i in C if STRATUM[i] == s}).items()
                                     if k != "sides"} for s in ("history", "policy", "hot")}
            row["lean"] = {"left": round(float(np.mean([l == "affirm" for it, s in LEFT.items() for l in M[it][s]])), 3),
                           "right": round(float(np.mean([l == "affirm" for it, s in LEFT.items()
                                                         for l in M[it]["y" if s == "x" else "x"]])), 3)}
            key = f"{arm}:{d['stage']}/{d['framing']}"
            summary[key] = row
            same = row.get("same_side_as_clamp")
            print(f"{key:24s} answered {100 * row['answered']:3.0f}%  hedge {100 * row['hedge']:3.0f}%  side "
                  f"{100 * row['side_taken']:3.0f}% (clamp {100 * row.get('clamp_side_taken', float('nan')):3.0f}%)  "
                  f"coherent {100 * row['coherent']:3.0f}%  same side {same[0] if same else '-'}/{same[1] if same else '-'}"
                  f"  hot side {100 * row['by_stratum']['hot']['side_taken']:3.0f}%  left/right "
                  f"{100 * row['lean']['left']:.0f}/{100 * row['lean']['right']:.0f}")
    return summary


if __name__ == "__main__":
    if "--score" not in sys.argv:
        nums = [a for a in sys.argv[1:] if a.isdigit()]
        sample(int(nums[0]) if nums else 16)
    OUT.write_text(json.dumps({"summary": score()}, indent=1, ensure_ascii=False) + "\n")
