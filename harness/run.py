"""
Runner — play a study's frozen multi-turn scenes against one or more models (OpenRouter).

Each model is one Contract-A JSON file: <study>/transcripts/<model>.json, scenes keyed by
id. Runs MERGE into that file — running a model creates it; running a scene subset
adds/replaces just those scene keys. Extension is a key-set, never a file rewrite.

    pip install requests python-dotenv
    cp .env.example .env   # OPENROUTER_API_KEY

    # add a model (all scenes) to a study:
    python harness/run.py --study studies/conduct openai/gpt-5.4
    # add / re-run one scene across models:
    python harness/run.py --study studies/conduct $(cat studies/conduct/spec/models.txt) --scenes the_leap
    # second backend: the Claude Agent SDK on the Max plan (harness/backends/agent_sdk.py), effort in place of temperature:
    python harness/run.py --study studies/conduct --backend agent_sdk --effort low claude-sonnet-5 --out studies/conduct/data/sdk-thinking

Read the JSON with harness/render.py (or the viewer). No markdown is the source here.
"""

import os
import sys
import json
import time
import argparse
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from study import Study
from backends import agent_sdk

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
API = "https://openrouter.ai/api/v1/chat/completions"
# OpenAI-compatible hosts for a model the router no longer carries. Same request shape; the key
# comes from the named env var, and the host is stamped in the file header so it is visible in the
# specimen. --provider (an OpenRouter routing pin) does not apply to them.
HOSTS = {
    "openrouter": (API, "OPENROUTER_API_KEY"),
    "fireworks": ("https://api.fireworks.ai/inference/v1/chat/completions", "FIREWORKS_API_KEY"),
    "deepinfra": ("https://api.deepinfra.com/v1/openai/chat/completions", "DEEPINFRA_API_KEY"),
}
REASONING_MODES = ("off", "low", "medium", "high")
BACKENDS = ("openrouter", "agent_sdk")


def pick_backend(slug, backend):
    """A slug prefixed "sdk:" selects the Agent SDK backend regardless of --backend."""
    return "agent_sdk" if agent_sdk.is_sdk_slug(slug) else backend


def reasoning_body(mode):
    """OpenRouter's per-request thinking control. Default (None) sends nothing: the model runs as served.
    "off" disables thinking on hybrid models; an effort level caps it. The mode is stamped on the cell."""
    return {"reasoning": {"enabled": False} if mode == "off" else {"effort": mode}}


class EmptyReply(ValueError):
    """The route answered but returned no content: typically a reasoning model that spent its token
    budget thinking (finish_reason "length"). Carries what the response did report, so the failed cell
    still records how much the model thought."""

    def __init__(self, trace=None, usage=None, finish_reason=None):
        super().__init__("empty/null content in response")
        self.trace, self.usage, self.finish_reason, self.turn = trace, usage, finish_reason, None


def chat(slug, messages, temperature, max_tokens, provider=None, retries=2, reasoning=None, backend="openrouter", effort=None, host="openrouter"):
    """One turn -> (reply, trace_or_None, usage_or_None, finish_reason_or_None). 60s timeout + a retry so a slow/hung route fails fast
    instead of blocking the batch. backend="agent_sdk" routes through the Max-plan adapter (harness/backends/agent_sdk.py):
    reasoning on, trace summarized, default sampling, effort in place of temperature."""
    if backend == "agent_sdk":
        return (*agent_sdk.chat(messages, None, max_tokens, agent_sdk.model_of(slug), effort), None)
    url, key = HOSTS[host]
    last = None
    for attempt in range(retries):
        try:
            r = requests.post(
                url,
                headers={"Authorization": f"Bearer {os.environ[key]}"},
                json={"model": slug, "messages": messages, "temperature": temperature, "max_tokens": max_tokens,
                      **({"provider": {"order": [provider], "allow_fallbacks": False}} if provider else {}),
                      **(reasoning_body(reasoning) if reasoning else {})},
                timeout=60,
            )
            r.raise_for_status()
            body = r.json()
            msg = body["choices"][0]["message"]
            content = msg.get("content")
            finish = body["choices"][0].get("finish_reason")
            if not content:
                raise EmptyReply(msg.get("reasoning"), body.get("usage"), finish)
            # trace, when the route returns one (thinking models); usage as the host reports it (OpenRouter: tokens incl. reasoning, cost in USD)
            return content, msg.get("reasoning"), body.get("usage"), finish
        except Exception as e:
            last = e
            time.sleep(2)
    raise last


def play(slug, scene, temperature, system_prompt, max_tokens, provider=None, reasoning=None, backend="openrouter", effort=None, host="openrouter"):
    """Return [{u, reply[, reasoning]}] across the scene's escalating user turns (+ optional seed).

    `system_prompt` may be overridden per-scene (`scene["system_prompt"]`); the spec-level
    prompt is the fallback. A scene with no prompt at either level runs system-prompt-free.
    """
    messages = []
    sp = scene.get("system_prompt", system_prompt)
    if sp:
        messages.append({"role": "system", "content": sp})
    if scene.get("seed"):
        messages.append({"role": "assistant", "content": scene["seed"]})
    panels = []
    for line in scene["turns"]:
        messages.append({"role": "user", "content": line})
        try:
            reply, trace, usage, finish = chat(slug, messages, temperature, max_tokens, provider, reasoning=reasoning, backend=backend, effort=effort, host=host)
        except EmptyReply as e:
            e.turn = len(panels)
            raise
        messages.append({"role": "assistant", "content": reply})
        panel = {"u": line, "reply": reply}
        if finish and finish != "stop":
            panel["finish_reason"] = finish  # e.g. "length": the budget ran out, possibly mid-thought
        if trace:
            panel["reasoning"] = trace     # the model's thinking trace; not sent back into the conversation
        if usage:
            panel["usage"] = usage         # tokens as billed; agent_sdk: incl. thinking_tokens (0 = the model chose not to think)
        panels.append(panel)
    return panels


def iter_scenes(spec):
    """Yield (register_name, scene) for either spec shape.

    Two stimulus shapes are supported behind one iterator:
      - target (docs): flat `scenes[]`           → register_name is None
      - legacy (conduct): `registers[]` of scenes → register_name is the register's name
    Detection is by key presence; a spec carries exactly one of the two.
    """
    if "scenes" in spec:
        for scene in spec["scenes"]:
            yield None, scene
    else:
        for reg in spec["registers"]:
            for scene in reg["scenes"]:
                yield reg["name"], scene


def save(path, data):
    """Write the model's file atomically (temp file, then rename), so a killed run never leaves a torn file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    os.replace(tmp, path)


def complete(entry, runs, reasoning):
    """A stored scene that already holds this many runs, under the same thinking mode, with no failed cell."""
    return (entry is not None and len(entry.get("runs", [])) == runs and entry.get("reasoning_mode") == reasoning
            and all(c.get("reply") and not c.get("error") for r in entry["runs"] for c in r))


def run_one(slug, spec, runs, temperature, scene_ids, out_dir, run_date, provider=None, max_tokens=None, reasoning=None,
            backend="openrouter", effort=None, host="openrouter", resume=False):
    backend = pick_backend(slug, backend)
    # canonical=host_id: the file and vendor come from the canonical slug, the request goes to the host's id
    host_model = None
    if host != "openrouter" and "=" in slug:
        slug, host_model = slug.split("=", 1)
    model_id = agent_sdk.model_of(slug)
    label = model_id.split("/")[-1] + (f"_sdk_{effort}" if backend == "agent_sdk" else "")
    sp = spec.get("system_prompt")
    spec_max = spec.get("max_tokens", 1200)
    max_tokens = max_tokens or spec_max
    # Version key follows the spec shape: flat → spec_version, legacy → script_version.
    version = spec.get("spec_version") or spec["script_version"]
    version_key = "spec_version" if "spec_version" in spec else "script_version"
    path = out_dir / f"{label}.json"
    if path.exists():
        data = json.loads(path.read_text())
    else:
        data = {"model": label, "slug": slug, version_key: version,
                "temperature": temperature, "max_tokens": spec_max, "scenes": {}}
    if backend == "agent_sdk":                # header: backend, model id, effort, trace mode, sampling (no temperature)
        data.pop("temperature", None)
        data.update(agent_sdk.stamp(model_id, effort))
    if provider:
        data["provider"] = provider          # pinned serving host (allow_fallbacks=false); absent = OpenRouter's choice
    if host != "openrouter":
        data["host"] = host                  # served outside the router (HOSTS); absent = OpenRouter
        if host_model: data["host_model"] = host_model

    for reg_name, scene in iter_scenes(spec):
        if scene_ids and scene["id"] not in scene_ids:
            continue
        if resume and complete(data["scenes"].get(scene["id"]), runs, reasoning):
            continue                       # --resume: a restart keeps the scenes an interrupted run finished
        runs_out = []
        for run in range(runs):
            try:
                runs_out.append(play(host_model or slug, scene, temperature, sp, max_tokens, provider, reasoning, backend, effort, host))
                print(f"  [{label}] {scene['id']} run {run} ✓")
            except Exception as e:
                cells = [{"u": t, "reply": None, "error": str(e)} for t in scene["turns"]]
                if isinstance(e, EmptyReply) and e.turn is not None:   # keep what the empty response reported
                    cells[e.turn].update({k: v for k, v in (("reasoning", e.trace), ("usage", e.usage),
                                                            ("finish_reason", e.finish_reason)) if v})
                runs_out.append(cells)
                print(f"  [{label}] {scene['id']} run {run} FAILED: {e}")
        entry = {"subtitle": scene.get("subtitle", scene["id"]),
                 "run_date": run_date, "runs": runs_out}
        if reg_name is not None:           # legacy shape carries the register tag through
            entry["register"] = reg_name
        if max_tokens != spec_max:         # a raised budget (reasoning models that exhaust the default) is recorded on the cell
            entry["max_tokens"] = max_tokens
        if reasoning:                      # a requested thinking mode is recorded on the cell; absent = the route's default
            entry["reasoning_mode"] = reasoning
        if backend == "agent_sdk":         # per cell too, so a scene stands alone
            entry.update(agent_sdk.stamp(model_id, effort))
        data["scenes"][scene["id"]] = entry
        save(path, data)                   # after every scene: an interrupted run loses at most the scene in flight

    if backend == "agent_sdk":                # re-stamp: the CLI version is known only after the first call
        data.update(agent_sdk.stamp(model_id, effort))
    save(path, data)
    print(f"→ {path}")


def main():
    ap = argparse.ArgumentParser(description="Run a study's scenes against models; merge into per-model JSON.")
    ap.add_argument("models", nargs="+", help="OpenRouter slugs, or sdk:<model-id> for the Agent SDK backend")
    ap.add_argument("--backend", choices=BACKENDS, default="openrouter",
                    help="agent_sdk = Claude Agent SDK on the Max plan (reasoning on, trace summarized, default sampling)")
    ap.add_argument("--effort", choices=agent_sdk.EFFORTS, default=None, help="agent_sdk only: effort level, stamped per cell (required)")
    ap.add_argument("--study", default=".", help="study directory (default: cwd)")
    ap.add_argument("--spec", default=None, help="stimulus spec path (default: <study>/spec/stimulus.json)")
    ap.add_argument("--runs", type=int, default=2)
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--scenes", default=None, help="comma-separated scene ids to run (default: all)")
    ap.add_argument("--out", default=None, help="dataset dir to merge into (default: <study>/transcripts)")
    ap.add_argument("--run-date", default=datetime.now().strftime("%Y-%m-%d"))
    ap.add_argument("--provider", default=None, help="pin the OpenRouter serving provider (no fallbacks), stamped in the file header")
    ap.add_argument("--host", choices=list(HOSTS), default="openrouter", help="OpenAI-compatible host for a model the router no longer carries. Pass the model as <canonical slug>=<host model id> so the file and vendor keep the canonical slug; host and host id are stamped in the header")
    ap.add_argument("--max-tokens", type=int, default=None, help="override the spec's output budget for this run; stamped on each scene it applies to")
    ap.add_argument("--reasoning", choices=REASONING_MODES, default=None,
                    help="request a thinking mode (off | low | medium | high); default sends nothing and takes the route's default")
    ap.add_argument("--resume", action="store_true",
                    help="skip scenes the file already holds with --runs runs, the same thinking mode and no failed cell (restart after an interruption)")
    args = ap.parse_args()

    backends = {pick_backend(m, args.backend) for m in args.models}
    if "openrouter" in backends and not os.environ.get(HOSTS[args.host][1]):
        sys.exit(f"{HOSTS[args.host][1]} not set (put it in .env).")
    if "agent_sdk" in backends and not args.effort:
        sys.exit("--effort is required with the agent_sdk backend (it replaces temperature).")

    study = Study(args.study)
    spec = json.loads(Path(args.spec).read_text()) if args.spec else study.stimulus()
    scene_ids = set(s.strip() for s in args.scenes.split(",")) if args.scenes else None
    out_dir = Path(args.out) if args.out else study.transcripts_dir
    print(f"writing to {out_dir}/  (scenes: {', '.join(scene_ids) if scene_ids else 'all'})")
    for slug in args.models:
        run_one(slug, spec, args.runs, args.temperature, scene_ids, out_dir, args.run_date, args.provider, args.max_tokens, args.reasoning,
                args.backend, args.effort, args.host, args.resume)


if __name__ == "__main__":
    main()
