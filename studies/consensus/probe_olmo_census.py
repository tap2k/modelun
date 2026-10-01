"""probe_olmo_census.py — where in post-training does a model join the field's consensus?

The full census (31 categories) asked of each OLMo 3 stage, to separate two things the literature
runs together: diversity collapse (a model's own answers narrow) and conformity (its answers move
onto the field's modal answer). Karouzos et al. (arXiv:2604.16027) put the Instruct line's diversity
collapse at DPO. If conformity is installed at a different stage, the two are distinct processes.

Pipelines as in probe_olmo_ladder.py (harness/ladders.json, sampled by harness/local.py): base as a raw
completion (first word kept), the other stages in their first default framing: the chat template, or
for a reasoning model (RL-Zero) the think framing, where only the answer after </think> is scored and
an unclosed trace is no answer. N samples per category at temperature 1. Each stage is one Contract-A transcript in
probes/<name>/; probes/<name>.json holds the summary.

Per stage, against the frozen field (transcripts/, scored by analyze.answers(); the stage's answers get
the same variant merge and the plural merge onto the field's pool, analyze.against()):
  surprisal     mean -log2 P(answer | field), add-one smoothed        (conformity, lower = more)
  modal_share   share of answers equal to the field's modal answer   (conformity)
  entropy       mean per-category entropy of the stage's own answers (diversity)
    ../../.venv/bin/python probe_olmo_census.py --7b [N=20]   # -> probes/olmo_census/
    ../../.venv/bin/python probe_olmo_census.py --7b --score
    --32b, --nemotron, --tulu, --rlzero pick the pipeline; add --expanded for the 65-category battery
    (spec/stimulus_expanded.json), scored against transcripts-expanded/ -> probes/<name>_expanded/
"""
import json, math, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "harness"))
from analyze import answers, against, load
from probe_olmo_ladder import first_word, SIZE, PIPELINE
import local

EXPANDED = "--expanded" in sys.argv                         # the 65-category battery instead of the 31
BATTERY = "expanded" if EXPANDED else "census"
NAME = ({"7b": "olmo_census", "32b": "olmo_census_32b", "nemotron": "nemotron_census", "tulu": "tulu_census",
         "rlzero": "rlzero_census"}[SIZE] + ("_expanded" if EXPANDED else ""))
DIR, OUT = HERE / "probes" / NAME, HERE / "probes" / f"{NAME}.json"
SPEC = json.loads((HERE / "spec" / ("stimulus_expanded.json" if EXPANDED else "stimulus.json")).read_text())


def framing(st):
    return "raw" if st["stage"] == "base" else st["framings"][0]


def sample(n):
    for st in local.stages(PIPELINE):
        f = framing(st)
        local.run(SPEC, st, f, n, local.path(DIR, st, f), local.MAX_TOKENS.get(f, 24))


def stage_answers(path, field):
    """One stage's transcript -> {category: [answer]}: first word for raw, the panel's scoring otherwise."""
    d = json.loads(path.read_text())
    if d["framing"] == "raw":
        ans = {d["model"]: {c: [a for a in (first_word(r[0]["reply"]) for r in sc["runs"]) if a]
                            for c, sc in d["scenes"].items()}}
    else:
        ans = load(HERE, BATTERY, paths=[path])
    return d["stage"], against(field, ans, HERE, BATTERY)[d["model"]]


def score():
    field = answers(HERE, BATTERY)
    summary = {}
    for st in local.stages(PIPELINE):
        path = local.path(DIR, st, framing(st))
        if not path.exists():
            continue
        stage, mine_by_cat = stage_answers(path, field)
        surp, modal_hits, ents, per_cat = [], [], [], {}
        for c, mine in mine_by_cat.items():
            others = [a for m in field for a in field[m].get(c, [])]
            if not mine or not others:
                continue
            pool = Counter(others)
            total, vocab = sum(pool.values()), len(set(others) | set(mine))
            modal = pool.most_common(1)[0][0]
            s = [-math.log2((pool.get(a, 0) + 1) / (total + vocab)) for a in mine]
            own = Counter(mine)
            h = -sum(v / len(mine) * math.log2(v / len(mine)) for v in own.values())
            surp += s
            modal_hits += [a == modal for a in mine]
            ents.append(h)
            per_cat[c] = {"valid": len(mine), "surprisal": round(sum(s) / len(s), 2),
                          "modal": modal, "modal_share": round(sum(a == modal for a in mine) / len(mine), 2),
                          "entropy": round(h, 2), "top": own.most_common(3)}
        summary[stage] = {"surprisal": round(sum(surp) / len(surp), 3),
                          "modal_share": round(sum(modal_hits) / len(modal_hits), 3),
                          "entropy": round(sum(ents) / len(ents), 3),
                          "valid": len(surp), "categories": len(per_cat), "per_category": per_cat}
        v = summary[stage]
        print(f"{stage:7s} surprisal {v['surprisal']:.2f}  modal_share {v['modal_share']:.2f}  "
              f"entropy {v['entropy']:.2f}  ({v['valid']} answers, {v['categories']} categories)")
    return summary


if __name__ == "__main__":
    if "--score" not in sys.argv:
        nums = [a for a in sys.argv[1:] if a.isdigit()]
        sample(int(nums[0]) if nums else 20)
    OUT.write_text(json.dumps({"summary": score()}, indent=1, ensure_ascii=False) + "\n")
