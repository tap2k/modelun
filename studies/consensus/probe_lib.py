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


def _key():
    for line in (Path(__file__).resolve().parent / "../../.env").read_text().splitlines():
        if line.startswith("OPENROUTER_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError("OPENROUTER_API_KEY not found")


def _ask(slug, prompt, system, key, extra=None):
    msgs = ([{"role": "system", "content": system}] if system else []) + \
           [{"role": "user", "content": prompt}]
    payload = {"model": slug, "messages": msgs, "temperature": 1.0, "max_tokens": 1024}
    if extra:
        payload.update(extra)
    body = json.dumps(payload).encode()
    req = Request("https://openrouter.ai/api/v1/chat/completions", data=body,
                  headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    for attempt in range(3):
        try:
            r = json.load(urlopen(req, timeout=90))
            return r["choices"][0]["message"].get("content")
        except Exception:
            if attempt == 2:
                return None
            time.sleep(2 * (attempt + 1))


def run_battery(prompts, models, runs, out_path, system=None, workers=20, meta=None, extra=None):
    """prompts: {cat: prompt}. models: [{label, slug}]. Writes {..., replies:{label:{cat:[...]}}}.

    extra: optional dict merged into each request body (e.g. a response_format schema for
    enforced structured output). Applied to every call in the run."""
    key = _key()
    tasks = [(m["label"], m["slug"], c, p, r)
             for m in models for c, p in prompts.items() for r in range(runs)]
    total = len(tasks)
    out = {m["label"]: {c: [None] * runs for c in prompts} for m in models}
    done = 0
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        fut = {ex.submit(_ask, slug, p, system, key, extra): (lab, c, r)
               for (lab, slug, c, p, r) in tasks}
        for f in as_completed(fut):
            lab, c, r = fut[f]
            out[lab][c][r] = f.result()
            done += 1
            if done % 100 == 0 or done == total:
                print(f"  {done}/{total} calls  ({time.time()-t0:.0f}s)", flush=True)
    payload = {"runs": runs, "prompts": prompts, "replies": out}
    if system:
        payload["system"] = system
    if meta:
        payload.update(meta)
    Path(out_path).write_text(json.dumps(payload, indent=1) + "\n")
    print(f"-> {out_path}", flush=True)
    return out
