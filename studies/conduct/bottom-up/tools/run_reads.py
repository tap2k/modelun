"""
Personality Atlas — multi-reader synthesis pass (OpenRouter).

Drives a differential read of every subject transcript through ONE reader model,
saving structured JSON per subject. Run it three times with three reader slugs;
the cross-reader agreement pass (done afterward) keeps only findings that
replicate across readers.

    pip install requests python-dotenv   # already in .venv
    export OPENROUTER_API_KEY=sk-or-...  # or .env

    .venv/bin/python scout/run_reads.py --reader openai/gpt-5.4
    .venv/bin/python scout/run_reads.py --reader google/gemini-3.1-pro-preview
    .venv/bin/python scout/run_reads.py --reader anthropic/claude-opus-4.8

Subjects = data/benchmark/*.md + runs/*-evo/*.md (override with --subjects).
Output   = reads/<reader-slug-flattened>/<subject>.json
Self-preference: a read where the reader's vendor == the subject's vendor is
still produced but stamped {"_self_family": true} so the agreement pass can
exclude it. With three readers, every subject still gets >=2 clean reads.

NOTE: readers cannot grep — their quotes are UNVERIFIED here. String-verify
every quote against the source .md afterward (AGENTS.md rule).
"""

import os
import re
import sys
import json
import time
import argparse
import requests
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
API = "https://openrouter.ai/api/v1/chat/completions"


def vendor(slug):
    return slug.split("/")[0] if "/" in slug else slug


def subject_vendor(text):
    """The transcript header line: '# Atlas scout — <label>  (<provider>/<model>)'."""
    m = re.search(r"\(([^/]+)/", text[:300])
    return m.group(1) if m else "?"


def read_one(reader_slug, system_prompt, transcript_text, retries=3):
    body = {
        "model": reader_slug,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "--- TRANSCRIPT ---\n" + transcript_text},
        ],
        "temperature": 0,
        # Reasoning models (gemini-3.x-pro, gpt-5) spend a large hidden budget on
        # `reasoning` before the JSON; 2000 truncated them mid-object. Give ample room.
        "max_tokens": 8000,
        "response_format": {"type": "json_object"},
    }
    last = None
    for attempt in range(retries):
        try:
            r = requests.post(
                API,
                headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
                json=body, timeout=180,
            )
            r.raise_for_status()
            raw = r.json()["choices"][0]["message"].get("content")
            if not raw:
                raise ValueError("empty content")
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                m = re.search(r"\{.*\}", raw, re.DOTALL)
                if m:
                    return json.loads(m.group(0))
                raise
        except Exception as e:  # transient API / parse hiccup — back off and retry
            last = e
            time.sleep(2 * (attempt + 1))
    return {"_error": str(last)}


def main():
    ap = argparse.ArgumentParser(description="Run a differential read of all subjects through one reader model.")
    ap.add_argument("--reader", required=True, help="OpenRouter slug of the reader model")
    ap.add_argument("--prompt", default=str(ROOT / "scout" / "read_prompt.txt"))
    ap.add_argument("--subjects", nargs="*", default=None,
                    help="explicit subject .md files; default = data/benchmark/*.md + runs/*-evo/*.md")
    ap.add_argument("--out", default=str(ROOT / "reads"))
    args = ap.parse_args()

    if not os.environ.get("OPENROUTER_API_KEY"):
        sys.exit("OPENROUTER_API_KEY not set (put it in .env).")

    system_prompt = Path(args.prompt).read_text()

    if args.subjects:
        # resolve to absolute so relative_to(ROOT) works for relative CLI paths
        subjects = [Path(p).resolve() for p in args.subjects]
    else:
        subjects = sorted((ROOT / "data" / "benchmark").glob("scout_*.md"))
        for evo in sorted((ROOT / "runs").glob("*-evo")):
            subjects += sorted(evo.glob("scout_*.md"))

    rv = vendor(args.reader)
    out_dir = Path(args.out) / args.reader.replace("/", "__")
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"reader={args.reader}  subjects={len(subjects)}  ->  {out_dir}/")

    for i, sub in enumerate(subjects, 1):
        text = sub.read_text()
        sv = subject_vendor(text)
        label = sub.stem.replace("scout_", "")
        result = read_one(args.reader, system_prompt, text)
        result["_subject_file"] = str(sub.relative_to(ROOT))
        result["_reader"] = args.reader
        result["_self_family"] = (rv == sv)
        (out_dir / f"{label}.json").write_text(json.dumps(result, indent=2))
        flag = " [self-family]" if result["_self_family"] else ""
        err = " ERROR" if "_error" in result else ""
        print(f"  [{i}/{len(subjects)}] {label}{flag}{err}")

    print(f"done -> {out_dir}/")


if __name__ == "__main__":
    main()
