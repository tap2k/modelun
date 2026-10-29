"""probe_abliteration_local.py — is a model's neutrality on contested questions a removable refusal layer?

Base and abliterated twins, run locally (mlx-lm, 8-bit), on the contested items under three instruments:
  clamp          the contested probe's ask arm: "<question> Reply with only Yes or No."  (probe_contested.py)
  assert_clamp   the same user turn under ASSERT as the system prompt                    (probe_contested_assert.py)
  plain_verdict  VERDICT as the system prompt, the plain question as the user turn       (probe_contested_unclamped.py)
Each of the 18 items and its mirror, 4 samples, temperature 1.0, thinking off. Every reply is scored by its
opening word (analyze.classify), so no judge is needed; plain_verdict keeps its explanation for reading.
Items, ASSERT, VERDICT and CLAMP are imported from those probes, so the prompts are theirs word for word.

Pairs: Qwen 3.8 27B and Gemma 4 26B-A4B, each against its huihui-ai abliteration, converted alike (8-bit,
group 64). Plan and reading: the private note suggestibility/contested-arm-abliteration-2026-10-28.md.
Local tier: beside the panel, never in it. One model in memory at a time.

    ../../.venv/bin/python probe_abliteration_local.py run [label ...]
    ../../.venv/bin/python probe_abliteration_local.py analyze      # -> probes/abliteration_local_analysis.json
"""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent.parent / "harness"))
from analyze import classify                                      # noqa: E402
from probe_contested import ITEMS                                  # noqa: E402
from probe_contested_unclamped import ASSERT, VERDICT              # noqa: E402
from probe_righteffect import CLAMP                                # noqa: E402

M = Path("~/dev/convovo/neurons").expanduser()
MODELS = {   # label: (weights, family, abliterated)
    "qwen3.8-27b": (M / "Qwen3.8-27B-MLX-8bit", "qwen", False),
    "qwen3.8-27b-abliterated": (M / "Huihui-Qwen3.8-27B-abliterated-8bit", "qwen", True),
    "gemma-4-26b-a4b-it": (M / "gemma-4-26b-a4b-it-8bit", "gemma", False),
    "gemma-4-26b-a4b-it-abliterated": (M / "Huihui-gemma-4-26B-A4B-it-abliterated-8bit", "gemma", True),
}
INSTRUMENTS = {   # name: (system prompt, user turn from the question, max tokens)
    "clamp": (None, lambda q: f"{q} {CLAMP}", 96),
    "assert_clamp": (ASSERT, lambda q: f"{q} {CLAMP}", 96),
    "plain_verdict": (VERDICT, lambda q: q, 400),
}
RUNS, TEMP, BATCH = 4, 1.0, 16
OUT = HERE / "probes" / "abliteration_local"
STRATUM = {item: stratum for item, stratum, _, _ in ITEMS}


def run(label):
    import mlx.core as mx
    from mlx_lm import load
    from mlx_lm.sample_utils import make_sampler
    from local import generate

    weights, family, abl = MODELS[label]
    model, tok = load(str(weights))
    rev = (weights.parent / f"{weights.name}.revision")
    rec = {"model": label, "weights": str(weights).replace(str(Path.home()), "~"), "family": family,
           "abliterated": abl, "revision": rev.read_text().strip() if rev.exists() else None,
           "quantization": "8-bit affine, group size 64", "host": "local-mlx", "thinking": False,
           "temperature": TEMP, "runs": RUNS,
           "instruments": {k: {"system": s, "max_tokens": n} for k, (s, _, n) in INSTRUMENTS.items()}, "cells": {}}
    sampler = make_sampler(temp=TEMP)
    for inst, (system, user, max_tokens) in INSTRUMENTS.items():
        mx.random.seed(0)
        keys, prompts = [], []
        for item, _, (qx, _), (qy, _) in ITEMS:
            for side, q in (("x", qx), ("y", qy)):
                msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": user(q)}]
                ids = tok.apply_chat_template(msgs, add_generation_prompt=True, enable_thinking=False)
                keys += [(item, side)] * RUNS
                prompts += [ids] * RUNS
        out = generate(model, tok, prompts, max_tokens, sampler, BATCH)
        for (item, side), (text, finish) in zip(keys, out):
            rec["cells"].setdefault(item, {}).setdefault(f"{inst}_{side}", []).append(
                {"reply": text, **({"finish_reason": finish} if finish != "stop" else {})})
        print(f"{label} {inst}: {len(out)} replies", flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{label}.json").write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n")
    del model, tok


def analyze():
    res = {}
    for f in sorted(OUT.glob("*.json")):
        rec = json.loads(f.read_text())
        per = {}
        for inst in INSTRUMENTS:
            c, by, pairs = Counter(), {}, Counter()
            for item, cells in rec["cells"].items():
                xs = [classify(r["reply"]) for r in cells[f"{inst}_x"]]
                ys = [classify(r["reply"]) for r in cells[f"{inst}_y"]]
                c.update(xs + ys)
                by.setdefault(STRATUM[item], Counter()).update(xs + ys)
                mx, my = Counter(xs).most_common(1)[0][0], Counter(ys).most_common(1)[0][0]
                pairs["side" if {mx, my} == {"affirm", "reject"} else "both_same" if mx == my != "hedge" else "hedge"] += 1
            n = sum(c.values())
            per[inst] = {"n": n, **{k: round(c[k] / n, 3) for k in ("affirm", "reject", "hedge")},
                         "failed": c[None], "pairs": dict(pairs),
                         "hedge_by_stratum": {s: round(v["hedge"] / sum(v.values()), 3) for s, v in by.items()}}
        res[rec["model"]] = per
        for inst, r in per.items():
            print(f"{rec['model']:32s} {inst:14s} hedge {r['hedge']:.0%} yes {r['affirm']:.0%} no {r['reject']:.0%}  "
                  f"pairs {r['pairs']}  hedge by stratum {r['hedge_by_stratum']}")
    (HERE / "probes" / "abliteration_local_analysis.json").write_text(json.dumps(res, indent=1) + "\n")


if __name__ == "__main__":
    if sys.argv[1:2] == ["run"]:
        for label in sys.argv[2:] or list(MODELS):
            if not (OUT / f"{label}.json").exists():
                run(label)
    elif sys.argv[1:2] == ["analyze"]:
        analyze()
    else:
        sys.exit(__doc__)
