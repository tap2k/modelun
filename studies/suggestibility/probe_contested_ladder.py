"""probe_contested_ladder.py — the contested battery on the local stage ladders.

On the API panel, "I think P." raises agreement and "P, right?" lowers it, with bare "P." near zero;
the tag effect is largest on history and absent on partisan ("hot") items, where hedging is highest.
This runs the same 18 items x 2 mirror sides x 4 arms (ask, tag, bare, belief; items, arms and exact
prompts imported read-only from probe_contested) on OLMo 3.1 32B base/SFT/DPO/RL and Nemotron 3.5
Lightning base/final, with the stages and framings of probe_suggest_ladder, to see which stage installs
the deference to a stated belief and which installs the resistance to the tag.

Reported per stage/framing, overall and per stratum (history / policy / hot): answered and hedge rates,
affirm by arm, TAG/BARE/BELIEF effects (affirm(arm) - affirm(ask), mean over the two mirror sides, then
items; nested bootstrap 95% CI), the same effects answered-only, the both-Yes / both-No rate on mirror
pairs (sample i of side x against sample i of side y), and on the 9 LEFT-coded items the affirm rate of
the left- vs right-coded claim.

    ../../.venv/bin/python probe_contested_ladder.py --32b [N=16]   # -> probes/contested_ladder_32b/ (Contract A) + .json
    ../../.venv/bin/python probe_contested_ladder.py --nemotron --score
"""
import json, sys
import numpy as np
from probe_suggest_ladder import HERE, SIZE, sample, labelled, boot_effect
from probe_contested import ITEMS, ARMS, STRATA, LEFT, prompt

DIR, OUT = HERE / "probes" / f"contested_ladder_{SIZE}", HERE / "probes" / f"contested_ladder_{SIZE}.json"
STRATUM = {sid: st for sid, st, _, _ in ITEMS}
EFFECTS = [a for a in ARMS if a != "ask"]


def cells():
    """(item, side, arm, text): 18 items x 2 mirror sides x 4 arms."""
    return [(sid, side, arm, prompt(arm, q, s)) for sid, _, qx, qy in ITEMS
            for side, (q, s) in (("x", qx), ("y", qy)) for arm in ARMS]


def block(M):
    """Rates and effects over a subset M[item][side][arm] = labels."""
    labels = {a: [l for it in M.values() for sd in it.values() for l in sd[a]] for a in ARMS}
    arms = {a: {k: round(sum(l == k for l in ls) / len(ls), 3) for k in ("affirm", "reject", "hedge", None)}
            for a, ls in labels.items()}
    both = {}
    for a in ARMS:
        pairs = [(x, y) for it in M.values() for x, y in zip(it["x"][a], it["y"][a])]
        both[a] = {"both_yes": round(sum(x == y == "affirm" for x, y in pairs) / len(pairs), 3),
                   "both_no": round(sum(x == y == "reject" for x, y in pairs) / len(pairs), 3)}
    return {"answered": round(float(np.mean([s["affirm"] + s["reject"] for s in arms.values()])), 3),
            "arms": {a: {str(k): v for k, v in s.items()} for a, s in arms.items()},
            "effects": {f"{a.upper()}eff": boot_effect(M, a) for a in EFFECTS},
            "effects_answered_only": {f"{a.upper()}eff": boot_effect(M, a, answered=True) for a in EFFECTS},
            "mirror_pairs": both}


def lean(M):
    """Left- vs right-coded claim affirm rate per arm, over the LEFT items."""
    out = {}
    for a in ARMS:
        l = [x for it, s in LEFT.items() for x in M[it][s][a]]
        r = [x for it, s in LEFT.items() for x in M[it]["y" if s == "x" else "x"][a]]
        out[a] = {"left": round(l.count("affirm") / len(l), 3), "right": round(r.count("affirm") / len(r), 3)}
    return out


def score():
    summary = {}
    f = lambda e: f"{100 * e[0]:+4.0f} [{100 * e[1]:+.0f},{100 * e[2]:+.0f}]"
    for key, M in labelled(DIR).items():
        summary[key] = {"all": block(M), **{st: block({k: v for k, v in M.items() if STRATUM[k] == st}) for st in STRATA},
                        "left_right": lean(M)}
        print(f"\n{key}")
        print(f"  {'stratum':8s}{'answ':>6}{'hedge@ask':>10}  affirm ask/tag/bare/belief  "
              f"{'TAGeff':22s}{'BAREeff':22s}{'BELIEFeff':22s}TAG/BELIEF answered-only   both-No@ask")
        for st in ("all",) + STRATA:
            b = summary[key][st]
            e, ea = b["effects"], b["effects_answered_only"]
            print(f"  {st:8s}{100 * b['answered']:5.0f}%{100 * b['arms']['ask']['hedge']:9.0f}%  "
                  + "/".join(f"{100 * b['arms'][a]['affirm']:.0f}" for a in ARMS).ljust(26)
                  + f"{f(e['TAGeff']):22s}{f(e['BAREeff']):22s}{f(e['BELIEFeff']):22s}"
                  + f"{100 * ea['TAGeff'][0]:+4.0f} / {100 * ea['BELIEFeff'][0]:+4.0f}".ljust(27)
                  + f"{100 * b['mirror_pairs']['ask']['both_no']:4.0f}%")
        lr = summary[key]["left_right"]
        print("  left/right affirm: " + "  ".join(f"{a} {100 * v['left']:.0f}/{100 * v['right']:.0f}" for a, v in lr.items()))
    return summary


if __name__ == "__main__":
    if "--score" not in sys.argv:
        nums = [a for a in sys.argv[1:] if a.isdigit()]
        sample(int(nums[0]) if nums else 16, cells(), DIR, "probe_contested_ladder")
    OUT.write_text(json.dumps({"summary": score()}, indent=1, ensure_ascii=False) + "\n")
