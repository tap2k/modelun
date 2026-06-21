"""
Atlas scout — run the frozen scenes against one or more models (OpenRouter).

Each model is one JSON file: data/benchmark/<model>.json, scenes keyed by id.
Runs MERGE into that file — running a model creates it; running a scene subset
adds/replaces just those scene keys. Extension is a key-set, never a file rewrite.

    pip install requests python-dotenv
    cp .env.example .env   # OPENROUTER_API_KEY

    # add a model (all scenes):
    python scout/atlas_scout.py registers.json openai/gpt-5.4
    # add / re-run one scene across models:
    python scout/atlas_scout.py registers.json $(cat models.txt) --scenes the_leap,self_label

Read the JSON with scout/render.py (or the site). No markdown is the source here.
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

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
API = "https://openrouter.ai/api/v1/chat/completions"


def chat(slug, messages, temperature, retries=2):
    """One turn. 60s timeout + a retry so a slow/hung route fails fast instead of blocking the batch."""
    last = None
    for attempt in range(retries):
        try:
            r = requests.post(
                API,
                headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
                json={"model": slug, "messages": messages, "temperature": temperature, "max_tokens": 1200},
                timeout=60,
            )
            r.raise_for_status()
            content = r.json()["choices"][0]["message"].get("content")
            if not content:
                raise ValueError("empty/null content in response")
            return content
        except Exception as e:
            last = e
            time.sleep(2)
    raise last


def play(slug, scene, temperature, system_prompt):
    """Return [{u, reply}] across the scene's escalating user turns (+ optional seed)."""
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
        panels.append({"u": line, "reply": reply})
    return panels


def run_one(slug, spec, runs, temperature, scene_ids, out_dir, run_date):
    label = slug.split("/")[-1]
    sp = spec.get("system_prompt")
    path = out_dir / f"{label}.json"
    if path.exists():
        data = json.loads(path.read_text())
    else:
        data = {"model": label, "slug": slug, "script_version": spec["script_version"],
                "temperature": temperature, "scenes": {}}

    for reg in spec["registers"]:
        for scene in reg["scenes"]:
            if scene_ids and scene["id"] not in scene_ids:
                continue
            runs_out = []
            for run in range(runs):
                try:
                    runs_out.append(play(slug, scene, temperature, sp))
                    print(f"  [{label}] {scene['id']} run {run} ✓")
                except Exception as e:
                    runs_out.append([{"u": t, "reply": None, "error": str(e)} for t in scene["turns"]])
                    print(f"  [{label}] {scene['id']} run {run} FAILED: {e}")
            data["scenes"][scene["id"]] = {
                "register": reg["name"], "subtitle": scene.get("subtitle", scene["id"]),
                "run_date": run_date, "runs": runs_out,
            }

    out_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"→ {path}")


def main():
    ap = argparse.ArgumentParser(description="Run the atlas scenes against models; merge into per-model JSON.")
    ap.add_argument("registers", help="path to the scripts JSON (registers.json)")
    ap.add_argument("models", nargs="+", help="OpenRouter slugs")
    ap.add_argument("--runs", type=int, default=2)
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--scenes", default=None, help="comma-separated scene ids to run (default: all)")
    ap.add_argument("--out", default=str(ROOT / "data" / "benchmark"),
                    help="dataset dir to merge into (default: data/benchmark)")
    ap.add_argument("--run-date", default=datetime.now().strftime("%Y-%m-%d"))
    args = ap.parse_args()

    if not os.environ.get("OPENROUTER_API_KEY"):
        sys.exit("OPENROUTER_API_KEY not set (put it in .env).")

    spec = json.loads(Path(args.registers).read_text())
    scene_ids = set(s.strip() for s in args.scenes.split(",")) if args.scenes else None
    out_dir = Path(args.out)
    print(f"writing to {out_dir}/  (scenes: {', '.join(scene_ids) if scene_ids else 'all'})")
    for slug in args.models:
        run_one(slug, spec, args.runs, args.temperature, scene_ids, out_dir, args.run_date)


if __name__ == "__main__":
    main()
