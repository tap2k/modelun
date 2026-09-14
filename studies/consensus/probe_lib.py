"""probe_lib.py — shared battery runner for the auxiliary probes.

Parallelizes at the individual-CALL level (not per-model), so one slow reasoning-model call
occupies a single worker instead of blocking a whole model's remaining calls. Logs progress
to stderr as it goes (no tail-buffering surprises). No new deps beyond stdlib.
"""

import sys
import json
import time
from pathlib import Path
from urllib.request import Request, urlopen
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "harness"))
from backends import agent_sdk          # second backend: "sdk:<model-id>" slugs run on the Max plan


def _key():
    for line in (Path(__file__).resolve().parent / "../../.env").read_text().splitlines():
        if line.startswith("OPENROUTER_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError("OPENROUTER_API_KEY not found")


def _ask(slug, prompt, system, key, extra=None, effort=None):
    """-> (reply, trace_or_None, usage_or_None). OpenRouter unless the slug is sdk:<model-id>."""
    msgs = ([{"role": "system", "content": system}] if system else []) + \
           [{"role": "user", "content": prompt}]
    if agent_sdk.is_sdk_slug(slug):
        try:
            return agent_sdk.chat(msgs, system, 1024, agent_sdk.model_of(slug), effort)
        except Exception as e:
            print(f"  [agent_sdk] {slug} {prompt[:30]!r}: {e}", file=sys.stderr, flush=True)
            return None, None, None
    payload = {"model": slug, "messages": msgs, "temperature": 1.0, "max_tokens": 1024}
    if extra:
        payload.update(extra)
    body = json.dumps(payload).encode()
    req = Request("https://openrouter.ai/api/v1/chat/completions", data=body,
                  headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    for attempt in range(3):
        try:
            r = json.load(urlopen(req, timeout=90))
            return r["choices"][0]["message"].get("content"), None, None
        except Exception:
            if attempt == 2:
                return None, None, None
            time.sleep(2 * (attempt + 1))


def run_battery(prompts, models, runs, out_path, system=None, workers=20, meta=None, extra=None, effort=None):
    """prompts: {cat: prompt}. models: [{label, slug}]. Writes {..., replies:{label:{cat:[...]}}}.

    extra: optional dict merged into each request body (e.g. a response_format schema for
    enforced structured output). Applied to every call in the run.
    effort: agent_sdk slugs only (sdk:<model-id>); stamped on the file with the backend, trace mode and
    sampling. Traces land in a parallel `reasoning` tree, token usage in `usage`."""
    sdk = any(agent_sdk.is_sdk_slug(m["slug"]) for m in models)
    key = _key() if not all(agent_sdk.is_sdk_slug(m["slug"]) for m in models) else None
    tasks = [(m["label"], m["slug"], c, p, r)
             for m in models for c, p in prompts.items() for r in range(runs)]
    total = len(tasks)
    out = {m["label"]: {c: [None] * runs for c in prompts} for m in models}
    traces = {m["label"]: {c: [None] * runs for c in prompts} for m in models}
    usage = {m["label"]: {c: [None] * runs for c in prompts} for m in models}
    done = 0
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        fut = {ex.submit(_ask, slug, p, system, key, extra, effort): (lab, c, r)
               for (lab, slug, c, p, r) in tasks}
        for f in as_completed(fut):
            lab, c, r = fut[f]
            out[lab][c][r], traces[lab][c][r], usage[lab][c][r] = f.result()
            done += 1
            if done % 100 == 0 or done == total:
                print(f"  {done}/{total} calls  ({time.time()-t0:.0f}s)", flush=True)
    payload = {"runs": runs, "prompts": prompts, "replies": out}
    if system:
        payload["system"] = system
    if sdk:
        payload.update(agent_sdk.stamp({m["label"]: agent_sdk.model_of(m["slug"]) for m in models}, effort))
        payload["reasoning"] = traces      # summarized thinking per call, None where the model chose not to think
        payload["usage"] = usage
    if meta:
        payload.update(meta)
    Path(out_path).write_text(json.dumps(payload, indent=1) + "\n")
    print(f"-> {out_path}", flush=True)
    return out
