"""probe_olmo_census.py — where in post-training does a model join the field's consensus?

The full census (31 categories) asked of each OLMo 3 stage, to separate two things the literature
runs together: diversity collapse (a model's own answers narrow) and conformity (its answers move
onto the field's modal answer). Karouzos et al. (arXiv:2604.16027) put the Instruct line's diversity
collapse at DPO. If conformity is installed at a different stage, the two are distinct processes.

Stages and framings as in probe_olmo_ladder.py: base as a raw completion (first word kept), the
instruct stages through their own chat template. N samples per category at temperature 1.
Per stage, against the frozen 87-model field (transcripts/, same norm and plural merge as analyze.py):
  surprisal     mean -log2 P(answer | field), add-one smoothed        (conformity, lower = more)
  modal_share   share of answers equal to the field's modal answer   (conformity)
  entropy       mean per-category entropy of the stage's own answers (diversity)
    ../../.venv/bin/python probe_olmo_census.py [N=20]
    ../../.venv/bin/python probe_olmo_census.py --score
    ../../.venv/bin/python probe_olmo_census.py --32b       # OLMo 3.1 32B, 8-bit -> probes/olmo_census_32b.json
"""
import json, math, sys, time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from analyze import load, norm                              # same normalization as the paper
from probe_olmo_ladder import first_word, SIZE, QUANT, LADDERS

OUT = HERE / "probes" / ("olmo_census.json" if SIZE == "7b" else "olmo_census_32b.json")
SCENES = json.loads((HERE / "spec" / "stimulus.json").read_text())["scenes"]
STAGES = [(stage, repo, weights) for stage, repo, weights, _ in LADDERS[SIZE]]  # same checkpoints as the ladder


def sample(n):
    from mlx_lm import load as mlx_load, generate
    from mlx_lm.sample_utils import make_sampler
    from huggingface_hub import model_info

    sampler = make_sampler(temp=1.0)
    runs = json.loads(OUT.read_text())["runs"] if OUT.exists() else {}
    for stage, repo, weights in STAGES:
        if stage in runs and len(runs[stage]["replies"]) == len(SCENES):
            continue
        model, tok = mlx_load(weights)
        rec = runs.setdefault(stage, {"repo": repo, "revision": model_info(repo).sha, "weights": weights,
                                      "quantization": QUANT, "temperature": 1.0,
                                      "framing": "raw" if stage == "base" else "chat",
                                      "run_date": time.strftime("%Y-%m-%d"), "replies": {}})
        t0 = time.time()
        for sc in SCENES:
            if sc["id"] in rec["replies"]:
                continue
            q = sc["turns"][0]
            if stage == "base":
                prompt, mt = tok.encode(q + "\nAnswer:"), 8
            else:
                prompt, mt = tok.apply_chat_template([{"role": "user", "content": q}], add_generation_prompt=True), 24
            rec["replies"][sc["id"]] = [generate(model, tok, prompt=prompt, max_tokens=mt, sampler=sampler)
                                        for _ in range(n)]
            OUT.write_text(json.dumps({"runs": runs}, indent=1, ensure_ascii=False))
        print(f"{stage}: {time.time() - t0:.0f}s", flush=True)
        del model, tok
    return runs


def score(runs):
    field = load(HERE)
    summary = {}
    for stage, _, _ in STAGES:
        if stage not in runs:
            continue
        rec = runs[stage]
        score_fn = first_word if rec["framing"] == "raw" else norm
        surp, modal_hits, ents, per_cat = [], [], [], {}
        for c, replies in rec["replies"].items():
            mine = [a for a in (score_fn(r) for r in replies) if a]
            others = [a for m in field for a in field[m].get(c, [])]
            if not mine or not others:
                continue
            pool = Counter(others)
            stems = {w: w[:-1] for w in set(pool) | set(mine) if w.endswith("s") and w[:-1] in pool}
            mine = [stems.get(a, a) for a in mine]
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
        print(f"{stage:5s} surprisal {v['surprisal']:.2f}  modal_share {v['modal_share']:.2f}  "
              f"entropy {v['entropy']:.2f}  ({v['valid']} answers, {v['categories']} categories)")
    return summary


if __name__ == "__main__":
    if "--score" in sys.argv:
        runs = json.loads(OUT.read_text())["runs"]
    else:
        nums = [a for a in sys.argv[1:] if a.isdigit()]
        runs = sample(int(nums[0]) if nums else 20)
    OUT.write_text(json.dumps({"summary": score(runs), "runs": runs}, indent=1, ensure_ascii=False))
