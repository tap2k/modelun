"""
Local backend — sample open checkpoints with mlx-lm and write ordinary Contract-A transcripts.

The OpenRouter runner (run.py) asks a hosted model. This asks a checkpoint loaded on this machine: a stage
of an open post-training pipeline (base / SFT / DPO / RL), or a panel model whose endpoint is gone. The
checkpoints are listed in harness/ladders.json. Every file is stamped with host "local-mlx", the pipeline,
stage and framing, the weights loaded, their quantization, the Hub revision of the source repo and any
loader or template overrides, so a study reads it like any other transcript.

A framing is how a single-turn question becomes the model's input:

  raw       the question plus "\\nAnswer:" as plain text (a base checkpoint has no chat convention)
  cloze     the question as plain text, as given (a natural completion, e.g. 'My favorite word is "')
  chat      the stage's own chat template, as shipped (with whatever default system prompt it inserts)
  nosys     the pipeline's chat turn written out by hand without that default system prompt
  sysgen    the chat template with a generic "You are a helpful assistant."
  <name>    the chat template with the pipeline's named system prompt (systrain, sysid, ...)
  think     the chat template with reasoning on. The reply is split at the last </think>: "reply" is the
            answer after it, "reasoning" the trace before it. A trace that never closed has no answer
            (reply null, with an error), whatever its last words were.

Replies end at end-of-text or end-of-turn (<|eot_id|>, <|im_end|>; some tokenizers list only the
former). Sampling is batched; lower --batch for large models (a 70B at 4 bits needs about 16 on 64 GB).

    python harness/local.py --study studies/consensus --spec studies/consensus/spec/stimulus.json \\
        --pipeline tulu3-8b --stage sft --framing chat --runs 2 --out /tmp/smoke

A study that builds its battery in code imports run() and passes the spec as a dict. Runs resume: a scene
already in the output file is skipped, so delete the file to re-run it.
"""

import argparse
import functools
import json
import os
import time
from pathlib import Path

from study import Study

LADDERS = {k: v for k, v in json.loads((Path(__file__).resolve().parent / "ladders.json").read_text()).items()
           if not k.startswith("_")}
SYSGEN = "You are a helpful assistant."
STOPS = ("<|eot_id|>", "<|im_end|>", "<|end_of_text|>", "<|endoftext|>")
THINK_END = "</think>"
MAX_TOKENS = {"raw": 8, "cloze": 8, "think": 4096}     # defaults; anything else 256


def stage(pipeline, name):
    """One stage of a pipeline, with the pipeline-wide fields (quantization, nosys, system_prompts,
    chat_kwargs, model_config, batch) folded in. label defaults to <pipeline>-<stage>."""
    st = next((s for s in stages(pipeline) if s["stage"] == name), None)
    if st is None:
        raise KeyError(f"{pipeline} has no stage {name!r}; it has {[s['stage'] for s in stages(pipeline)]}")
    return st


def stages(pipeline):
    p = LADDERS[pipeline]
    shared = {k: v for k, v in p.items() if k not in ("stages", "note")}
    return [{"pipeline": pipeline, "label": f"{pipeline}-{s['stage']}", **shared, **s} for s in p["stages"]]


def path(out_dir, st, framing):
    """Where a stage/framing's transcript lives: <label>.json for chat, <label>_<framing>.json otherwise."""
    return Path(out_dir) / f"{st['label']}{'' if framing == 'chat' else '_' + framing}.json"


def load(st):
    """mlx-lm model and tokenizer for a stage, with its loader override and end-of-turn stop tokens."""
    from mlx_lm import load as mlx_load
    model, tok = mlx_load(os.path.expanduser(st["weights"]), model_config=st.get("model_config"))
    stops = set(tok.eos_token_ids)
    for name in STOPS:
        tid = tok.convert_tokens_to_ids(name)
        if isinstance(tid, int) and tid >= 0 and tid != getattr(tok, "unk_token_id", None):
            stops.add(tid)
    tok.eos_token_ids = stops
    return model, tok


def free():
    """Release a dropped model's memory. Call after `del model` and before loading the next one: mlx keeps
    freed buffers in its cache, and two large checkpoints resident at once on a 64 GB machine gave garbage
    (<unk>) replies rather than an error (Nemotron after OLMo 3.1 32B, 2026-10-01)."""
    import gc
    import mlx.core as mx
    gc.collect()
    mx.clear_cache()


def system_prompt(st, framing):
    return SYSGEN if framing == "sysgen" else st.get("system_prompts", {}).get(framing)


def encode(tok, st, framing, q):
    """Token ids for question q under a framing."""
    if framing == "raw":
        return tok.encode(q + "\nAnswer:")
    if framing == "cloze":
        return tok.encode(q)
    if framing == "nosys":
        return tok.encode(st["nosys"].replace("{q}", q))
    sp = system_prompt(st, framing)
    if framing not in ("chat", "think") and sp is None:
        raise ValueError(f"unknown framing {framing!r} for {st['label']}")
    kw = {**st.get("chat_kwargs", {}), **({"enable_thinking": True} if framing == "think" else {})}
    msgs = ([{"role": "system", "content": sp}] if sp else []) + [{"role": "user", "content": q}]
    return tok.apply_chat_template(msgs, add_generation_prompt=True, **kw)


@functools.cache
def revision(repo):
    from huggingface_hub import model_info
    return model_info(repo).sha


def generate(model, tok, prompts, max_tokens, sampler, batch, batched=True):
    """[(text, finish_reason)] per prompt, in order: batch_generate, keeping each reply's finish reason
    ("stop" at an end-of-text or end-of-turn token, "length" when max_tokens ran out). batched=False samples
    one prompt at a time, for models whose batched path is broken in mlx-lm (ladders.json "batched")."""
    if not batched:
        from mlx_lm import stream_generate
        out = []
        for p in prompts:
            text, finish = "", None
            for r in stream_generate(model, tok, p, max_tokens=max_tokens, sampler=sampler):
                text, finish = text + r.text, r.finish_reason or finish
            out.append((text, finish))
        return out
    from mlx_lm.generate import BatchGenerator
    gen = BatchGenerator(model, stop_tokens=[[t] for t in tok.eos_token_ids], sampler=sampler,
                         completion_batch_size=batch)
    uids = gen.insert(prompts, [max_tokens] * len(prompts))
    tokens, finish = {u: [] for u in uids}, {}
    while responses := gen.next_generated():
        for r in responses:
            if r.finish_reason != "stop":
                tokens[r.uid].append(r.token)
            if r.finish_reason is not None:
                finish[r.uid] = r.finish_reason
    gen.close()
    return [(tok.decode(tokens[u]), finish[u]) for u in uids]


def cell(q, text, think, finish=None):
    """One Contract-A cell; finish_reason only when it is not "stop", as run.py records it. Think: the answer
    after the last </think>, the trace kept beside it. An unclosed trace is no answer, whether the budget ran
    out or the model ended its turn inside it."""
    c = {"u": q, "reply": text}
    if think:
        if THINK_END in text:
            trace, c["reply"] = text.rsplit(THINK_END, 1)
            c["reasoning"] = trace
        else:
            c.update(reply=None, reasoning=text, error="reasoning did not close: " + (
                "the turn ended inside it" if finish == "stop" else "max_tokens ran out" if finish == "length"
                else "no </think>"))
    if finish and finish != "stop":
        c["finish_reason"] = finish
    return c


def run(spec, st, framing, runs, out, max_tokens=None, batch=None, temperature=1.0, model=None):
    """Sample every single-turn scene of spec (a dict) `runs` times and merge the scenes into the Contract-A
    file `out`. model: an already loaded (model, tok) for this stage, to reuse across framings. A stage's
    batch in ladders.json is a memory ceiling, applied to any batch asked for."""
    from mlx_lm.sample_utils import make_sampler

    if spec.get("system_prompt"):
        raise ValueError("spec-level system prompts are not supported locally; use a framing")
    max_tokens = max_tokens or MAX_TOKENS.get(framing, 256)
    batch = min(batch or 32, st.get("batch", batch or 32))
    out = Path(out)
    data = json.loads(out.read_text()) if out.exists() else None
    if data:                                             # resuming: the file's settings must be these
        asked = {"framing": framing, "max_tokens": max_tokens, "temperature": temperature}
        clash = {k: (data.get(k), v) for k, v in asked.items() if data.get(k) != v}
        if clash:
            raise ValueError(f"{out} was sampled with other settings (file, asked): {clash}")
    todo = [s for s in spec["scenes"] if not data or s["id"] not in data["scenes"]]
    if not todo:
        return out
    for s in todo:
        if len(s["turns"]) != 1:
            raise ValueError(f"scene {s['id']}: the local backend runs single-turn scenes only")
    model, tok = model or load(st)
    sp = system_prompt(st, framing)
    if data is None:
        data = {"model": st["label"], "slug": st["repo"],
                "spec_version": spec.get("spec_version") or spec.get("script_version"),
                "host": "local-mlx", "pipeline": st["pipeline"], "stage": st["stage"], "framing": framing,
                "weights": st["weights"], "quantization": st.get("quantization"),
                "revision": revision(st["repo"]), "temperature": temperature, "max_tokens": max_tokens,
                **{k: st[k] for k in ("model_config", "chat_kwargs") if st.get(k)},
                **({"system_prompt": sp} if sp else {}),
                "example_prompt": tok.decode(encode(tok, st, framing, todo[0]["turns"][0])), "scenes": {}}
    sampler = make_sampler(temp=temperature)
    per_chunk = -(-4 * batch // runs)                    # ~4 batches per call; written after each, to resume
    out.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    for i in range(0, len(todo), per_chunk):
        chunk = todo[i:i + per_chunk]
        prompts = [encode(tok, st, framing, s["turns"][0]) for s in chunk]
        replies = generate(model, tok, [p for p in prompts for _ in range(runs)], max_tokens, sampler, batch,
                           st.get("batched", True))
        date = time.strftime("%Y-%m-%d")
        for j, s in enumerate(chunk):
            q = s["turns"][0]
            data["scenes"][s["id"]] = {"subtitle": s.get("subtitle", s["id"]), "run_date": date,
                                       "runs": [[cell(q, t, framing == "think", f)] for t, f in replies[j * runs:(j + 1) * runs]]}
        out.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")
    print(f"{st['label']}/{framing}: {len(todo)} scenes x {runs} in {time.time() - t0:.0f}s -> {out}", flush=True)
    return out


def main():
    ap = argparse.ArgumentParser(description="Sample a local checkpoint on a study's single-turn spec; write Contract A.")
    ap.add_argument("--study", default=".", help="study directory (default: cwd)")
    ap.add_argument("--spec", default=None, help="stimulus spec path (default: <study>/spec/stimulus.json)")
    ap.add_argument("--pipeline", choices=list(LADDERS), required=True)
    ap.add_argument("--stage", required=True)
    ap.add_argument("--framing", default=None, help="default: the stage's first default framing")
    ap.add_argument("--runs", type=int, default=8)
    ap.add_argument("--max-tokens", type=int, default=None, help="default: raw/cloze 8, think 4096, otherwise 256")
    ap.add_argument("--batch", type=int, default=None, help="replies generated in parallel (default: the stage's, else 32)")
    ap.add_argument("--out", default=None, help="output directory (default: <study>/transcripts-local)")
    a = ap.parse_args()
    st = stage(a.pipeline, a.stage)
    framing = a.framing or st["framings"][0]
    study = Study(a.study)
    out_dir = Path(a.out) if a.out else study.root / "transcripts-local"
    run(json.loads(Path(a.spec).read_text()) if a.spec else study.stimulus(), st, framing, a.runs, path(out_dir, st, framing), a.max_tokens, a.batch)


if __name__ == "__main__":
    main()
