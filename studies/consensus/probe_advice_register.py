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
pool that the completion names. Read against the API panel as served: the share of completions naming the panel's
Name brand and the share naming its two-turn pick brand, over the categories where the two differ.

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
    import brand_ladder as B
    lv = B.levels()
    name = {c: B.top(n)[0] for c, n in B.agg(lv["name"]).items()}
    pick = {c: B.top(n)[0] for c, n in B.agg(lv["pick2"]).items()}
    pats = B.pools()[4]
    diff = sorted(c for c in name if pick.get(c) and pick[c] != name[c])
    res = {"categories_where_pick_differs": diff}
    for f in sorted(OUT.glob("*.json")):
        d = json.loads(f.read_text())
        row = {}
        for r in REGISTERS:
            hit_n = hit_p = named = total = 0
            for c in diff:
                for run in d["scenes"].get(f"{c}__{r}", {}).get("runs", []):
                    ms = B.mentions(run[0].get("reply") or "", pats[c]) if run else []
                    total += 1
                    if ms:
                        named += 1
                        hit_n += ms[0] == name[c]
                        hit_p += ms[0] == pick[c]
            row[r] = {"name_brand": hit_n / total if total else None, "pick_brand": hit_p / total if total else None,
                      "names_a_brand": named / total if total else None}
        res[d["model"]] = row
    (HERE / "probes" / "advice_register.json").write_text(json.dumps(res, indent=1) + "\n")
    print(f"{len(diff)} categories where the panel's two-turn pick differs from its Name brand; share of base completions")
    for m, row in res.items():
        if m == "categories_where_pick_differs":
            continue
        print(f"  {m:28} " + "  ".join(f"{r}: Name {v['name_brand']:.0%} / pick {v['pick_brand']:.0%}" for r, v in row.items()))


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "run":
        run(sys.argv[2])
    elif len(sys.argv) > 1 and sys.argv[1] == "score":
        score()
    else:
        print(__doc__)
