"""probe_olmo_ladder.py — does post-training put "serendipity" into any_word? The OLMo 3 7B stage ladder.

The census any_word item ("Pick a word. Reply with one word only.") has serendipity as its modal
answer, rising with release date, near 0% on lightly tuned models and 100% on Hermes 3 405B. The
hypothesis under test: pretraining links the prompt to charming words, preference tuning rewards
serendipity, RL collapses onto it. OLMo 3 publishes every stage of one pipeline, so each stage is
sampled locally (mlx-lm, bf16, temperature 1, no system prompt of our own):

  base  allenai/Olmo-3-1025-7B            raw only
  sft   allenai/Olmo-3-7B-Instruct-SFT    chat, nosys, raw
  dpo   allenai/Olmo-3-7B-Instruct-DPO    chat, nosys, raw
  rl    allenai/Olmo-3-7B-Instruct        chat, nosys, raw

  chat   the stage's own chat template. With no system message it inserts a default one
         ("You are a helpful function-calling AI assistant. ..."), which any host using the
         template would send too.
  nosys  the same ChatML turn with that default system message removed.
  raw    completion text 'Pick a word. Reply with one word only.\\nAnswer:', first word kept.

chat/nosys replies are scored with the census norm(); raw keeps the first word, since a base model
has no stop convention. Share = serendipity / valid answers, Wilson 95% CI.
    ../../.venv/bin/python probe_olmo_ladder.py [N=50]      # needs mlx-lm and ~60 GB of weights
    ../../.venv/bin/python probe_olmo_ladder.py --score     # re-score probes/olmo_ladder.json only
    ../../.venv/bin/python probe_olmo_ladder.py --32b       # OLMo 3.1 32B ladder, 8-bit -> olmo_ladder_32b.json
"""
import json, math, re, sys, time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent                      # studies/consensus
sys.path.insert(0, str(HERE))
from analyze import norm                                    # same normalization as the paper

SIZE = "32b" if "--32b" in sys.argv else "7b"
OUT = HERE / "probes" / ("olmo_ladder.json" if SIZE == "7b" else "olmo_ladder_32b.json")
PROMPT = "Pick a word. Reply with one word only."
RAW = PROMPT + "\nAnswer:"
NOSYS = f"<|im_start|>user\n{PROMPT}<|im_end|>\n<|im_start|>assistant\n"
# (stage, source repo, weights loaded, framings). 7B loads the source in bf16. 32B loads 8-bit MLX
# weights (group size 64): mlx-community's conversions for base and final, local conversions with the
# same settings for SFT and DPO (mlx_lm.convert -q --q-bits 8 --q-group-size 64). The 32B instruct
# stages are OLMo 3.1, built on the Olmo-3-1125-32B base.
M32 = Path.home() / "models" / "olmo32"
LADDERS = {
    "7b": [
        ("base", "allenai/Olmo-3-1025-7B", "allenai/Olmo-3-1025-7B", ["raw"]),
        ("sft", "allenai/Olmo-3-7B-Instruct-SFT", "allenai/Olmo-3-7B-Instruct-SFT", ["chat", "nosys", "raw"]),
        ("dpo", "allenai/Olmo-3-7B-Instruct-DPO", "allenai/Olmo-3-7B-Instruct-DPO", ["chat", "nosys", "raw"]),
        ("rl", "allenai/Olmo-3-7B-Instruct", "allenai/Olmo-3-7B-Instruct", ["chat", "nosys", "raw"]),
    ],
    "32b": [
        ("base", "allenai/Olmo-3-1125-32B", "mlx-community/Olmo-3-1125-32B-8bit", ["raw"]),
        ("sft", "allenai/Olmo-3.1-32B-Instruct-SFT", str(M32 / "Olmo-3.1-32B-Instruct-SFT-8bit"), ["chat", "nosys", "raw"]),
        ("dpo", "allenai/Olmo-3.1-32B-Instruct-DPO", str(M32 / "Olmo-3.1-32B-Instruct-DPO-8bit"), ["chat", "nosys", "raw"]),
        ("rl", "allenai/Olmo-3.1-32B-Instruct", "mlx-community/Olmo-3.1-32B-Instruct-8bit", ["chat", "nosys", "raw"]),
    ],
}
STAGES = LADDERS[SIZE]
QUANT = None if SIZE == "7b" else "8-bit affine, group size 64"


def first_word(text):
    m = re.search(r"[A-Za-z][A-Za-z'-]*", text)
    return m.group(0).lower().strip("'-") if m else None


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(c - h, 0.0), min(c + h, 1.0))


def sample(n):
    from mlx_lm import load, generate
    from mlx_lm.sample_utils import make_sampler
    from huggingface_hub import model_info

    sampler = make_sampler(temp=1.0)
    runs = json.loads(OUT.read_text())["runs"] if OUT.exists() else {}
    for stage, repo, weights, framings in STAGES:
        todo = [f for f in framings if f"{stage}/{f}" not in runs]
        if not todo:
            continue
        model, tok = load(weights)
        rev = model_info(repo).sha
        for framing in todo:
            if framing == "chat":
                prompt = tok.apply_chat_template([{"role": "user", "content": PROMPT}], add_generation_prompt=True)
            else:
                prompt = tok.encode(NOSYS if framing == "nosys" else RAW)
            max_tokens = 8 if framing == "raw" else 24
            t0 = time.time()
            replies = [generate(model, tok, prompt=prompt, max_tokens=max_tokens, sampler=sampler) for _ in range(n)]
            runs[f"{stage}/{framing}"] = {"repo": repo, "revision": rev, "weights": weights, "quantization": QUANT,
                                          "prompt": tok.decode(prompt),
                                          "temperature": 1.0, "max_tokens": max_tokens,
                                          "run_date": time.strftime("%Y-%m-%d"), "replies": replies}
            OUT.write_text(json.dumps({"runs": runs}, indent=1, ensure_ascii=False))
            print(f"{stage}/{framing}: {time.time() - t0:.0f}s", flush=True)
        del model, tok
    return runs


def score(runs):
    summary = {}
    for stage, _, _, framings in STAGES:
        for framing in framings:
            key = f"{stage}/{framing}"
            if key not in runs:
                continue
            answers = [(first_word if framing == "raw" else norm)(r) for r in runs[key]["replies"]]
            valid = [a for a in answers if a]
            k = sum(a == "serendipity" for a in valid)
            c = Counter(valid)
            lo, hi = wilson(k, len(valid))
            h = -sum(v / len(valid) * math.log2(v / len(valid)) for v in c.values()) if valid else 0.0
            summary[key] = {"n": len(answers), "valid": len(valid), "serendipity": k,
                            "share": round(k / len(valid), 3) if valid else None,
                            "ci95": [round(lo, 3), round(hi, 3)], "distinct": len(c),
                            "entropy_bits": round(h, 2), "top": c.most_common(8)}
            print(f"{key:10s} valid={len(valid):2d}/{len(answers)} serendipity={k:2d} "
                  f"({100 * k / max(len(valid), 1):3.0f}%, CI {100 * lo:.0f}-{100 * hi:.0f})  "
                  f"H={h:.2f}  " + ", ".join(f"{w}×{n}" for w, n in c.most_common(6)))
    return summary


if __name__ == "__main__":
    if "--score" in sys.argv:
        runs = json.loads(OUT.read_text())["runs"]
    else:
        nums = [a for a in sys.argv[1:] if a.isdigit()]
        runs = sample(int(nums[0]) if nums else 50)
    OUT.write_text(json.dumps({"summary": score(runs), "runs": runs}, indent=1, ensure_ascii=False))
