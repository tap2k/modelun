"""probe_brand_teacher.py — does preference training move a model toward its teacher's brand, or toward its own?

DPO data carries almost no brand comparisons (stage_dolci.json, stage_tulu.json), yet DPO moves brand picks. Two
readings: the student copies its teacher's answers, or it learns a way of choosing and applies it to the options its
own pretraining supplied. Where the teacher's brand and the student's own differ, the two predict opposite moves.

  teacher  The modal one-name answer to clamped Recommend of the model that supplied the pipeline's preferred
           answers: Qwen 3 32B, reasoning off, for OLMo 3 (chosen side of Dolci's delta-learning pairs;
           probes/teacher_brands/, not a panel transcript) and GPT-4o for Tulu 3 (its preference judge; panel file).
  own      The brand the pipeline's base model rates likeliest under the three clamped Recommend wordings (mean
           log-probability), over the probe_brand_logprob candidates plus the teacher's brand.

Per stage, over the categories where the two differ: the fixed three-item list (own, teacher, a third brand) in both
orders, scored from "I'd pick " as in probe_brand_logprob.py, P(own) / (P(own) + P(teacher)) averaged over the orders;
and the paired step between stages.

    ../../.venv/bin/python probe_brand_teacher.py run olmo3-7b       # -> probes/brand_teacher/<pipeline>.json
    ../../.venv/bin/python probe_brand_teacher.py score              # -> probes/brand_teacher.json
"""
import json, math, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "harness"))
from probe_brand_logprob import questions, free_recommend, panel, logprob, turn1, pick_prefix, boot  # noqa: E402

OUT = HERE / "probes" / "brand_teacher"
TEACHER = {"olmo3-7b": ("qwen3-32b", "probes/teacher_brands/recommend-clamp/qwen3-32b.json"),
           "olmo31-32b": ("qwen3-32b", "probes/teacher_brands/recommend-clamp/qwen3-32b.json"),
           "tulu3-8b": ("gpt-4o", "transcripts-brands-recommend-clamp/gpt-4o.json")}
RECS = ("recommend", "recommend2", "recommend3")


def teacher_brands(pipe):
    """category -> the teacher's modal one-name clamped Recommend answer, scored as brand_ladder scores clamped levels."""
    import brand_ladder as B
    from analyze import load as load_clamped
    model, f = TEACHER[pipe]
    paths = [HERE / f] + ([HERE / "transcripts-brands-ext2-recommend-clamp" / "gpt-4o.json"] if model == "gpt-4o" else [])
    ans = load_clamped(HERE, "brands", paths=[p for p in paths if p.exists()])
    cats = next(iter(ans.values()))
    out = {}
    for c, xs in cats.items():
        xs = [x for x in xs if B.one_name(x) and x != B.NO_PICK]
        if xs:
            out[c] = Counter(xs).most_common(1)[0][0]
    return out


def run(pipe):
    import local
    from probe_verb_ladder import stages, tuned_framing
    qs, rec, pn, tb = questions(), free_recommend(), panel(), teacher_brands(pipe)
    path = OUT / f"{pipe}.json"
    res = json.loads(path.read_text()) if path.exists() else {"pipeline": pipe, "teacher": TEACHER[pipe][0], "teacher_brands": tb,
                                                              "stages": {}}
    for st in stages(pipe):
        if st["stage"] in res["stages"]:
            continue
        base = st["stage"] == "base"
        f = "raw" if base else tuned_framing(st)
        model, tok = local.load(st)
        if base:                                       # the student's own favourite, from its base model
            own = {}
            for c, p in pn.items():
                if c not in tb or c not in rec:
                    continue
                cands = list(dict.fromkeys(p["candidates"] + [tb[c]]))
                lp = {a: 0.0 for a in cands}
                for v in RECS:
                    if c in qs[v]:
                        pre = local.encode(tok, st, f, qs[v][c])
                        for a in cands:
                            lp[a] += logprob(model, tok, pre, a, " ")
                own[c] = max(lp, key=lp.get)
            res["own"] = own
            res["third"] = {c: next((a for a in [pn[c]["name"]] + pn[c]["candidates"] if a not in (own[c], tb[c])), None)
                            for c in own}
        row = {"framing": f, "revision": local.revision(st["repo"], st["weights"]), "pick": {}}
        for c, o in res["own"].items():
            t, x = tb[c], res["third"][c]
            if o == t or o in t or t in o or not x:      # one brand under two spellings ("kind", "kind snacks")
                continue
            for key, order in (("own_first", (o, t, x)), ("teacher_first", (t, o, x))):
                pre = pick_prefix(tok, st, f, rec[c], turn1(order))
                row["pick"].setdefault(c, {})[key] = {a: logprob(model, tok, pre, a, " ") for a in (o, t)}
        res["stages"][st["stage"]] = row
        OUT.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
        print(f"teacher {st['label']}: {len(row['pick'])} categories where own and teacher differ", flush=True)
        del model
        local.free()


def score():
    out = {}
    for f in sorted(OUT.glob("*.json")):
        d = json.loads(f.read_text())
        own, tb = d["own"], d["teacher_brands"]
        share = {}
        for st, r in d["stages"].items():
            share[st] = {c: sum(1 / (1 + math.exp(o[tb[c]] - o[own[c]])) for o in lists.values()) / 2
                         for c, lists in r["pick"].items()}
        names = list(share)
        out[d["pipeline"]] = {"teacher": d["teacher"], "categories": {c: [own[c], tb[c]] for c in share[names[0]]},
                              "stages": {s: boot(list(v.values())) for s, v in share.items()},
                              "steps": {f"{a}->{b}": boot([share[b][c] - share[a][c] for c in share[b] if c in share[a]])
                                        for a, b in zip(names, names[1:])}}
        o = out[d["pipeline"]]
        print(f"\n{d['pipeline']} (teacher {d['teacher']}): own brand over teacher's, {len(o['categories'])} categories")
        for s, x in o["stages"].items():
            print(f"  {s:6} {x['mean']:.0%} {x['ci90']}")
        for s, x in o["steps"].items():
            print(f"  {s:10} {x['mean']:+.2f} {x['ci90']}")
    (HERE / "probes" / "brand_teacher.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "run":
        run(sys.argv[2])
    elif len(sys.argv) > 1 and sys.argv[1] == "score":
        score()
    else:
        print(__doc__)
