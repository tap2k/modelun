"""
Personality Atlas — scout run (OpenRouter)

Takes a scripts JSON file and one or more model slugs. Plays every scene a few
times against each model and writes one readable file per model.

No alias map, no config: OpenRouter IS the model registry. Pass raw slugs.
For a saved list, keep them in a text file and let the shell expand it.

    pip install requests
    export OPENROUTER_API_KEY=sk-or-...

    python atlas_scout.py registers.json openai/gpt-5.1
    python atlas_scout.py registers.json openai/gpt-5.1 anthropic/claude-opus-4.1 x-ai/grok-4.1
    python atlas_scout.py registers.json $(cat models.txt) --runs 3

Each model writes scout_<name>.md independently — a flaked model is a one-line
redo, and failures never clobber another model's file.

No markers, no judge, no aggregation. The question now is just: do the models
pull apart when you read them side by side?
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

API = "https://openrouter.ai/api/v1/chat/completions"

# Load .env from the project root (one level up from scout/). Real exported
# shell vars still win — load_dotenv won't override what's already set.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def chat(slug, messages, temperature):
    r = requests.post(
        API,
        headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
        json={"model": slug, "messages": messages,
              "temperature": temperature, "max_tokens": 1200},
        timeout=120,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def play(slug, scene, temperature, system_prompt=None):
    """A scene has optional 'seed' (assistant's prior turn) and 'turns' (user lines)."""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    if scene.get("seed"):
        messages.append({"role": "assistant", "content": scene["seed"]})
    panels = []
    for line in scene["turns"]:
        messages.append({"role": "user", "content": line})
        reply = chat(slug, messages, temperature)
        messages.append({"role": "assistant", "content": reply})
        panels.append((line, reply))
    return panels


def quote(text):
    """Blockquote a reply so its own markdown (headers, lists) can't hijack the
    file's outline — keeps the model's formatting readable but inert as structure."""
    return "\n".join("> " + line if line else ">" for line in text.split("\n"))


def run_one(slug, spec, runs, temperature, out_dir):
    label = slug.split("/")[-1]
    system_prompt = spec.get("system_prompt")
    out = [f"# Atlas scout — {label}  ({slug})",
           f"_script_version: {spec['script_version']} · runs/scene: {runs} · temp: {temperature}_\n",
           "_Read these, don't average them. Does this model pull apart from the others?_\n"]
    if system_prompt:
        out.append(f"_[system prompt for every turn]: {system_prompt}_\n")

    for reg in spec["registers"]:
        for scene in reg["scenes"]:
            out.append(f"\n## {reg['name']} · {scene.get('subtitle', scene['id'])}\n")
            if scene.get("seed"):
                out.append(f"_[seed — model's prior turn]: {scene['seed']}_\n")
            for run in range(runs):
                try:
                    panels = play(slug, scene, temperature, system_prompt)
                except Exception as e:
                    out.append(f"\n**run {run} — FAILED:** {e}\n")
                    print(f"  [{label}] {reg['id']}/{scene['id']} run {run} FAILED: {e}")
                    continue
                out.append(f"\n### run {run}\n")
                for i, (user, reply) in enumerate(panels, 1):
                    out.append(f"\n**U{i}:** {user}\n\n**{label}:**\n\n{quote(reply)}\n")
                print(f"  [{label}] {reg['id']}/{scene['id']} run {run} ✓")

    dest = out_dir / f"scout_{label}.md"
    dest.write_text("\n".join(out))
    print(f"→ {dest}")


def main():
    ap = argparse.ArgumentParser(description="Run the atlas scripts against one or more models.")
    ap.add_argument("registers", help="path to the scripts JSON (e.g. registers.json)")
    ap.add_argument("models", nargs="+", help="one or more raw OpenRouter slugs")
    ap.add_argument("--runs", type=int, default=2,
                    help="runs per scene (default 2 — to eyeball spread, not to average)")
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--out", default="runs", help="base output directory")
    ap.add_argument("--tag", default=None,
                    help="label for this run's subdir (default: a timestamp). "
                         "Each run lands in <out>/<tag>/ so runs never overwrite each other.")
    args = ap.parse_args()

    if not os.environ.get("OPENROUTER_API_KEY"):
        sys.exit("OPENROUTER_API_KEY is not set. Put it in .env (see .env.example) "
                 "or export it in your shell.")

    spec = json.loads(Path(args.registers).read_text())
    # Dated specimens: every run gets its own subdir so a re-run can't clobber
    # an earlier one. Pass --tag to name it; otherwise it's stamped with the clock.
    tag = args.tag or datetime.now().strftime("%Y-%m-%dT%H%M")
    out_dir = Path(args.out) / tag
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"writing to {out_dir}/")

    for slug in args.models:          # each model isolated: its own file, its own failures
        run_one(slug, spec, args.runs, args.temperature, out_dir)


if __name__ == "__main__":
    main()
