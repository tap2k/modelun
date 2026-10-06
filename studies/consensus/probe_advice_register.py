"""probe_advice_register.py — does a base model already hold the brand the tuned models recommend?

The brand ladder shows tuned models moving off their one-word Name brand when asked to recommend or pick (Nike to
Brooks), and dolci_brands.py finds almost no brand recommendations in OLMo's post-training data. The remaining
explanation is that pretraining text already pairs advice phrasing with the other brand and post-training routes a
request to it. This probe asks the base models directly, as plain completion (cloze framing), in three registers for
each of the 44 brand categories:

  typical    "A well-known running shoe brand is"
  advice     "The best running shoe brand is"
  recommend  "If you want a good running shoe brand, I recommend"

20 completions each, 16 tokens, temperature 1, through harness/local.py; scored by the first brand from the panel's
pool that the completion names. Read against the API panel as served: of the completions that name a brand, the share
naming the panel's Name brand and the share naming its clamped Recommend brand (the matched target for "I recommend"),
over the categories where the two differ; the two-turn pick brand is reported beside it.

    caffeinate -ims ../../.venv/bin/python probe_advice_register.py run olmo3-7b "base=/Volumes/My Passport/models/Olmo-3-1025-7B"
    ../../.venv/bin/python probe_advice_register.py score
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "harness"))
sys.path.insert(0, str(HERE))
OUT = HERE / "probes" / "advice_register"
PIPES = ("olmo3-7b", "tulu3-8b", "olmo31-32b", "nemotron35-lightning")
REGISTERS = {"typical": "A well-known {n} is", "advice": "The best {n} is",
             "recommend": "If you want a good {n}, I recommend"}


def nouns():
    out = {}
    for f in ("spec/stimulus_brands.json", "spec/stimulus_brands_ext.json", "spec/stimulus_brands_ext2.json"):
        for s in json.loads((HERE / f).read_text())["scenes"]:
            out[s["id"]] = re.match(r"Name an? (.+?)\. Reply", s["turns"][0]).group(1)
    return out


def spec():
    return {"spec_version": "advice-register-cloze-1", "system_prompt": None,
            "scenes": [{"id": f"{c}__{r}", "turns": [t.format(n=n)]} for c, n in nouns().items() for r, t in REGISTERS.items()]}


def run(pipe):
    import local
    over = dict(a.split("=", 1) for a in sys.argv[3:] if "=" in a)
    st = next(s for s in local.stages(pipe) if s["stage"] == "base")
    st = {**st, "weights": over.get("base", st["weights"])}
    model = local.load(st)
    local.run(spec(), st, "cloze", 20, local.path(OUT, st, "cloze"), max_tokens=16, batch=16, model=model)
    del model
    local.free()


def score():
    """Per base model and register: of the completions that name a pool brand, the share naming the panel's Name brand
    and the share naming a target brand, over the categories where the target differs from Name (the generic
    company/brand categories left out); and in how many categories the target's share rises, and falls, from the
    typical to the recommend register. The matched target for "I recommend" is the panel's clamped Recommend brand
    (one brand per answer); the two-turn pick brand is reported beside it."""
    import brand_ladder as B
    lv = B.levels()
    name = {c: B.top(n)[0] for c, n in B.agg(lv["name"]).items()}
    pats = B.pools()[4]
    res = {}
    for tname, level in (("recommend_clamp", "recommend_clamp"), ("pick2", "pick2")):
        tgt = {c: B.top(n)[0] for c, n in B.agg(lv[level]).items()}
        diff = sorted(c for c in name if tgt.get(c) and tgt[c] != name[c] and c not in B.GENERIC)
        block = {"categories": diff}
        for f in sorted(OUT.glob("*.json")):
            d = json.loads(f.read_text())
            row, per = {}, {}
            for r in REGISTERS:
                hit_n = hit_t = named = 0
                for c in diff:
                    k = per.setdefault(c, {}).setdefault(r, [0, 0])
                    for run in d["scenes"].get(f"{c}__{r}", {}).get("runs", []):
                        ms = B.mentions(run[0].get("reply") or "", pats[c]) if run else []
                        if ms:
                            named += 1
                            hit_n += ms[0] == name[c]
                            hit_t += ms[0] == tgt[c]
                            k[0] += ms[0] == tgt[c]
                            k[1] += 1
                row[r] = {"named": named, "name_brand": hit_n / named if named else None,
                          "target_brand": hit_t / named if named else None}
            share = lambda c, r: per[c][r][0] / per[c][r][1]
            both = [c for c in diff if per[c]["typical"][1] and per[c]["recommend"][1]]
            row["target_rises"] = sum(share(c, "recommend") > share(c, "typical") for c in both)
            row["target_falls"] = sum(share(c, "recommend") < share(c, "typical") for c in both)
            block[d["model"]] = row
        res[tname] = block
        print(f"\ntarget: the panel's {tname} brand; {len(diff)} categories where it differs from Name. Of the base"
              " completions that name a brand, Name brand / target brand")
        for m, row in block.items():
            if m == "categories":
                continue
            print(f"  {m:28} " + "  ".join(f"{r}: {row[r]['name_brand']:.0%} / {row[r]['target_brand']:.0%} (n {row[r]['named']})"
                                           for r in REGISTERS)
                  + f"   target rises in {row['target_rises']}, falls in {row['target_falls']}")
    (HERE / "probes" / "advice_register.json").write_text(json.dumps(res, indent=1) + "\n")


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "run":
        run(sys.argv[2])
    elif len(sys.argv) > 1 and sys.argv[1] == "score":
        score()
    else:
        print(__doc__)
