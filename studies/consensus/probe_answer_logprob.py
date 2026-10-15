"""probe_answer_logprob.py — at each training stage, how likely is each candidate answer under "Name" and "Choose"?

Sampling shows which answer a stage gives; log-probabilities show how far it moved. For each census and expanded
category, the candidates are the API panel's top answers under "Name" (transcripts/ + transcripts-extra/ +
transcripts-expanded/) and under "Choose" (transcripts-choose/ + transcripts-expanded-choose/), five each, merged.
Each candidate's total log-probability as the reply to the stage's prompt is computed by a forward pass (the base stage
in raw framing, "<question>\\nAnswer: <candidate>"; tuned stages in the no-system-prompt chat turn), then normalised
over the candidates of that category.

It separates two readings of where favourites come from (LIT-CHECK-PREFERENCE-STAGES-2026-10-02):
  - preference tuning creates them: the Choose favourite (mango) gains probability at DPO or RL from a low base
  - preference tuning reinforces what the base already found likely (typicality bias): the gain goes to answers
    the base model already rated high

    ../../.venv/bin/python probe_answer_logprob.py olmo3-7b [--delete-cache]   # -> probes/answer_logprob_<pipeline>.json
    ../../.venv/bin/python probe_answer_logprob.py score    # -> probes/answer_logprob_steps.json

score: the census counterpart of probe_brand_logprob.py's verb shift. Over the categories where the panel's Choose
favourite differs from its Name favourite, per stage: log P(Choose fav) - log P(Name fav) under Choose minus the same
under Name (probabilities as stored, normalised over the candidates, floored at 1e-4), and its paired step between
stages. Does DPO move the judgment verb toward the panel's Choose answer outside brands too?
"""
import json, math, shutil, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "harness"))
import local
from analyze import answers, against, load
from probe_verb_ladder import stages, tuned_framing


def candidates():
    """category -> (name prompt, choose prompt, [candidate answers])."""
    core, exp = answers(HERE), answers(HERE, "expanded")
    extra = against(core, load(HERE, "census", paths=sorted((HERE / "transcripts-extra").glob("*.json"))), HERE)
    ch = {**{m: c for m, c in answers(HERE, "choose_census").items()}}
    for m, c in answers(HERE, "choose_expanded").items():
        ch.setdefault(m, {}).update(c)
    name_q = {s["id"]: s["turns"][0] for f in ("stimulus.json", "stimulus_expanded.json")
              for s in json.loads((HERE / "spec" / f).read_text())["scenes"]}
    choose_q = {s["id"]: s["turns"][0] for f in ("perturb/stimulus_choose.json", "perturb/stimulus_expanded_choose.json")
                for s in json.loads((HERE / "spec" / f).read_text())["scenes"]}
    out = {}
    for c in name_q:
        nm = Counter(x for src in (core, extra, exp) for m in src.values() for x in m.get(c, []))
        cm = Counter(x for m in ch.values() for x in m.get(c, []))
        cands = list(dict.fromkeys([a for a, _ in nm.most_common(5)] + [a for a, _ in cm.most_common(5)]))
        if c in choose_q and len(cands) >= 2:
            out[c] = (name_q[c], choose_q[c], cands)
    return out


def score(model, tok, prefix, answer, raw):
    """Log-probability of `answer` as the continuation of `prefix` token ids, summed over its lowercase and capitalised
    spellings (raw framing continues "Answer:" with a leading space; a chat reply starts without one)."""
    import mlx.core as mx
    lead = " " if raw else ""
    totals = []
    for form in dict.fromkeys([answer, answer[:1].upper() + answer[1:]]):
        ans = tok.encode(lead + form, add_special_tokens=False)
        ids = list(prefix) + ans
        logits = model(mx.array([ids]))[0]
        lp = logits - mx.logsumexp(logits, axis=-1, keepdims=True)
        totals.append(float(sum(lp[len(prefix) + i - 1, t].item() for i, t in enumerate(ans))))
    m = max(totals)
    return m + math.log(sum(math.exp(x - m) for x in totals))


def main(pipeline, delete_cache):
    cand = candidates()
    path = HERE / "probes" / f"answer_logprob_{pipeline}.json"
    res = json.loads(path.read_text()) if path.exists() else {"pipeline": pipeline, "categories": {}}
    done = {s for row in res["categories"].values() for s in row.get("name", {})}
    for st in stages(pipeline):
        if st["stage"] in done:                          # resume: a stage already scored is skipped
            print(f"skip {st['label']}: already scored", flush=True)
            continue
        base = st["stage"] == "base"
        f = "raw" if base else tuned_framing(st)
        model, tok = local.load(st)
        for c, (qn, qc, cands) in cand.items():
            row = res["categories"].setdefault(c, {"candidates": cands})
            for verb, q in (("name", qn), ("choose", qc)):
                pre = local.encode(tok, st, f, q)
                lps = [score(model, tok, pre, a, base) for a in cands]
                m = max(lps)
                z = sum(math.exp(x - m) for x in lps)
                row.setdefault(verb, {})[st["stage"]] = {a: round(math.exp(x - m) / z, 4) for a, x in zip(cands, lps)}
        print(f"logprob {st['label']}: {len(cand)} categories", flush=True)
        path.write_text(json.dumps(res, indent=1) + "\n")
        del model
        local.free()
        if delete_cache and not st["weights"].startswith(("/", "~")):
            shutil.rmtree(Path.home() / ".cache/huggingface/hub" / ("models--" + st["weights"].replace("/", "--")), ignore_errors=True)


def modes():
    """category -> (panel Name favourite, panel Choose favourite), counted as candidates() counts them."""
    core, exp = answers(HERE), answers(HERE, "expanded")
    extra = against(core, load(HERE, "census", paths=sorted((HERE / "transcripts-extra").glob("*.json"))), HERE)
    ch = dict(answers(HERE, "choose_census"))
    for m, c in answers(HERE, "choose_expanded").items():
        ch.setdefault(m, {}).update(c)
    out = {}
    for c in candidates():
        nm = Counter(x for src in (core, extra, exp) for m in src.values() for x in m.get(c, []))
        cm = Counter(x for m in ch.values() for x in m.get(c, []))
        if nm and cm:
            out[c] = (nm.most_common(1)[0][0], cm.most_common(1)[0][0])
    return out


def score():
    from probe_brand_logprob import boot
    md, out = modes(), {}
    lg = lambda x: math.log(max(x, 1e-4))
    for f in sorted((HERE / "probes").glob("answer_logprob_*.json")):
        if f.stem.endswith("steps"):
            continue
        d = json.loads(f.read_text())
        cats = {c: md[c] for c in d["categories"] if c in md and md[c][0] != md[c][1]}
        stages_ = list(next(iter(d["categories"].values()))["name"])
        shift = {st: {c: (lg(d["categories"][c]["choose"][st][ch]) - lg(d["categories"][c]["choose"][st][nm]))
                         - (lg(d["categories"][c]["name"][st][ch]) - lg(d["categories"][c]["name"][st][nm]))
                      for c, (nm, ch) in cats.items() if st in d["categories"][c].get("choose", {})}
                 for st in stages_}
        out[d["pipeline"]] = {"categories": len(cats), "stages": {st: boot(list(v.values())) for st, v in shift.items()},
                              "steps": {f"{a}->{b}": boot([shift[b][c] - shift[a][c] for c in shift[b] if c in shift[a]])
                                        for a, b in zip(stages_, stages_[1:])}}
        print(f"\n{d['pipeline']} ({len(cats)} categories where the panel's Choose favourite differs from Name)")
        for st, x in out[d["pipeline"]]["stages"].items():
            print(f"  {st:6} Choose shift {x['mean']:+.2f} {x['ci90']}")
        for k, x in out[d["pipeline"]]["steps"].items():
            print(f"  {k:12} {x['mean']:+.2f} {x['ci90']}")
    (HERE / "probes" / "answer_logprob_steps.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__" and sys.argv[1:2] == ["score"]:
    score()
elif __name__ == "__main__":
    main(sys.argv[1], "--delete-cache" in sys.argv)
