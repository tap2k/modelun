"""probe_local_census.py: run a census battery on a model served locally (mlx-lm), for panel models whose
OpenRouter endpoint is gone but whose weights are open (Hermes 4 70B, Granite 4.1 8B).

Writes Contract A transcripts, the same shape the harness writes, to transcripts-local/<battery>/<label>.json,
stamped with host "local-mlx", the weights path, the quantization and the Hub revision. Prompts, temperature
(1.0) and the absence of a system prompt follow the battery's spec; replies are capped at --max-tokens (default
256; the spec's 1024 is a ceiling for reasoning models, and these answer in a few tokens). Nothing here is
merged into the API transcripts: calibrate first, by comparing the local 31-category census with the model's API
census (--compare), against the panel's resampling baseline (modal agreement ~0.81, main vs extra runs).

    ../../.venv/bin/python probe_local_census.py run --battery census --label hermes-4-70b \\
        --repo NousResearch/Hermes-4-70B --weights "/Volumes/My Passport/models/Hermes-4-70B-4bit" --quant "4-bit (mlx-community)"
    ../../.venv/bin/python probe_local_census.py compare --label hermes-4-70b
"""
import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from analyze import BATTERIES, norm  # noqa: E402


def run(a):
    from mlx_lm import load, batch_generate
    from mlx_lm.sample_utils import make_sampler
    from huggingface_hub import model_info

    sub, spec_file = BATTERIES[a.battery]
    spec = json.loads((HERE / "spec" / spec_file).read_text())
    out = HERE / "transcripts-local" / a.battery / f"{a.label}{a.suffix}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    cfg = json.loads(a.model_config) if a.model_config else None
    model, tok = load(a.weights, model_config=cfg) if cfg else load(a.weights)
    stops = {t for t in tok.eos_token_ids}            # end of turn as well as end of text (Hermes: <|eot_id|>)
    for name in ("<|eot_id|>", "<|im_end|>", "<|end_of_text|>", "<|endoftext|>"):
        tid = tok.convert_tokens_to_ids(name)
        if isinstance(tid, int) and tid >= 0 and tid != getattr(tok, "unk_token_id", None):
            stops.add(tid)
    tok.eos_token_ids = stops
    scenes = spec["scenes"]
    if a.prompt_format:     # a literal chat format, e.g. one without the template's default system prompt
        prompts = [tok.encode(a.prompt_format.replace("{q}", s["turns"][0]), add_special_tokens=False) for s in scenes]
    else:
        prompts = [tok.apply_chat_template([{"role": "user", "content": s["turns"][0]}], add_generation_prompt=True)
                   for s in scenes]
    t0 = time.time()
    flat = [p for p in prompts for _ in range(a.runs)]
    texts = batch_generate(model, tok, flat, max_tokens=a.max_tokens, sampler=make_sampler(temp=1.0),
                           completion_batch_size=a.batch).texts
    date = time.strftime("%Y-%m-%d")
    data = {"model": a.label, "slug": a.repo, "model_config_override": cfg, "prompt_format": a.prompt_format, "spec_version": spec.get("spec_version") or spec.get("script_version"),
            "temperature": 1.0, "max_tokens": a.max_tokens, "host": "local-mlx", "weights": a.weights,
            "quantization": a.quant, "revision": model_info(a.repo).sha, "scenes": {}}
    for i, s in enumerate(scenes):
        data["scenes"][s["id"]] = {"subtitle": s.get("subtitle", s["id"]), "run_date": date,
                                   "runs": [[{"u": s["turns"][0], "reply": r}] for r in texts[i * a.runs:(i + 1) * a.runs]]}
    out.write_text(json.dumps(data, indent=1, ensure_ascii=False))
    print(f"wrote {out}  ({len(scenes)} categories x {a.runs} runs, {time.time() - t0:.0f}s)")


def modal(path):
    d = json.loads(Path(path).read_text())
    out = {}
    for sid, sc in d["scenes"].items():
        ans = [norm(r[0].get("reply")) for r in sc["runs"] if r]
        ans = [x for x in ans if x]
        if ans:
            out[sid] = Counter(ans).most_common(1)[0][0]
    return out


def compare(a):
    api, loc = modal(HERE / "transcripts" / f"{a.label}.json"), modal(HERE / "transcripts-local" / "census" / f"{a.label}{a.suffix}.json")
    both = [c for c in api if c in loc]
    agree = sum(api[c] == loc[c] for c in both)
    print(f"{a.label}: modal answer agrees in {agree}/{len(both)} categories ({agree / max(len(both), 1):.2f}); "
          f"panel resampling baseline ~0.81 (main vs extra, 4 vs 4 runs)")
    for c in both:
        if api[c] != loc[c]:
            print(f"  {c:16s} api {api[c]:14s} local {loc[c]}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    r = sp.add_parser("run")
    r.add_argument("--battery", choices=BATTERIES, required=True)
    r.add_argument("--label", required=True)
    r.add_argument("--repo", required=True)
    r.add_argument("--weights", required=True)
    r.add_argument("--quant", default="bf16")
    r.add_argument("--runs", type=int, default=8)
    r.add_argument("--max-tokens", type=int, default=256)
    r.add_argument("--prompt-format", default=None, help="literal prompt with {q}; default is the model's chat template")
    r.add_argument("--suffix", default="", help="output file suffix, for framing variants")
    r.add_argument("--batch", type=int, default=32, help="replies generated in parallel; lower for 70B models")
    r.add_argument("--model-config", default=None, help='JSON override for the loader, e.g. {"tie_word_embeddings": false}')
    c = sp.add_parser("compare")
    c.add_argument("--label", required=True)
    c.add_argument("--suffix", default="")
    a = ap.parse_args()
    run(a) if a.cmd == "run" else compare(a)
