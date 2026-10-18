"""pickword_ladder.py — pickword (spec/pickword.json, 46 scenes) on each stage of the local stage ladders.

Every stage of the named harness/ladders.json pipelines, in its default framings (raw for a base, chat and nosys
or systrain for the instruct stages), 8 samples per scene at temperature 1, as the panel's pickword plus
pickword-extra. Replies are capped at 32 tokens, enough for one word in any script. Batch 8: at 32 and 64 the
OLMo 3 7B base ran out of GPU memory (2026-10-16). One Contract-A file per stage/framing in
probes/pickword_ladder_<pipeline>/.

Scoring is per file (pickword.py pools a directory as one panel), over the 37 reported languages (views/build.py
EXCLUDE). A reply is cut at its first line before pickword.norm, since a base checkpoint keeps writing after its
answer. Per stage/framing: compliance (share of replies with a word in the language's script), mean modal share,
languages with a modal share of 50% or more, and the English modal word; written to probes/pickword_ladder.json.

    ../../.venv/bin/python pickword_ladder.py olmo3-7b [olmo31-32b ...]   # sample, then score every ladder
    ../../.venv/bin/python pickword_ladder.py --score                     # score only
"""
import json, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "views"))
sys.path.insert(0, str(HERE.parents[1] / "harness"))
import local
from pickword import LANGS, norm
from build import EXCLUDE

SPEC = json.loads((HERE / "spec" / "pickword.json").read_text())
RUNS = 8
REPORTED = [l for l in LANGS if l not in EXCLUDE]


def sample(pipeline):
    out_dir = HERE / "probes" / f"pickword_ladder_{pipeline}"
    for st in local.stages(pipeline):
        todo = [f for f in st["framings"] if not local.path(out_dir, st, f).exists()]
        if not todo:
            continue
        model = local.load(st)
        for framing in todo:
            local.run(SPEC, st, framing, RUNS, local.path(out_dir, st, framing), 32, batch=8, model=model)
        del model
        local.free()


def score_file(data):
    per = {}
    for l in REPORTED:
        replies = [r[0]["reply"] for r in data["scenes"][l]["runs"]]
        toks = [t for t in (norm((r or "").strip().split("\n")[0], l) for r in replies) if t]
        top = Counter(toks).most_common(1)
        per[l] = (len(toks) / len(replies), top[0][1] / len(replies) if top else 0.0, top[0][0] if top else None)
    shares = [s for _, s, _ in per.values()]
    return {"compliance": round(sum(c for c, _, _ in per.values()) / len(per), 3),
            "mean_modal_share": round(sum(shares) / len(shares), 3),
            "langs_modal_ge50": sum(s >= 0.5 for s in shares),
            "en_modal": [per["en"][2], per["en"][1]],
            "modal": {l: [w, round(s, 3)] for l, (_, s, w) in per.items()}}


def score():
    out = {}
    for d in sorted((HERE / "probes").glob("pickword_ladder_*/")):
        pipeline = d.name.removeprefix("pickword_ladder_")
        order = [st["stage"] for st in local.stages(pipeline)]
        files = sorted((json.loads(p.read_text()) for p in d.glob("*.json")),
                       key=lambda f: (order.index(f["stage"]), f["framing"]))
        rows = out[pipeline] = {f"{f['stage']}/{f['framing']}": score_file(f) for f in files}
        print(f"== {pipeline}")
        for k, r in rows.items():
            print(f"  {k:18s} compliance {r['compliance']:4.0%}  modal share {r['mean_modal_share']:4.0%}  "
                  f">=50% in {r['langs_modal_ge50']:2d}/{len(REPORTED)}  en {r['en_modal'][0]} {r['en_modal'][1]:.0%}")
    (HERE / "probes" / "pickword_ladder.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    for pipeline in (a for a in sys.argv[1:] if a != "--score"):
        sample(pipeline)
    score()
