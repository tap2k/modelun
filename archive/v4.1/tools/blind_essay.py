"""
Per-judge blind essay — each reader model writes its OWN field-guide essay.

Unbiased by construction: each judge authors from ITS OWN blind reads
(reads/<reader>/, produced via read_prompt_blind.txt), in its own voice, with NO
sight of docs/essay.md, Claude's taxonomy, or any other judge's essay. Run it for
each judge to get a set of independent essays to compare side by side.

    .venv/bin/python scout/blind_essay.py --reader openai/gpt-5.4
    .venv/bin/python scout/blind_essay.py --reader google/gemini-3.1-pro-preview
    .venv/bin/python scout/blind_essay.py --reader anthropic/claude-opus-4.8

Output -> reads/_essay/<reader-flattened>.md
"""

import os
import sys
import time
import argparse
import requests
from pathlib import Path
from dotenv import load_dotenv
from blind_synth import compact_reads  # reuse the per-model read folder

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
API = "https://openrouter.ai/api/v1/chat/completions"

ESSAY_PROMPT = """You are an essayist and analyst. You ran a differential read of a set of language models \
placed in nine awkward, escalating situations — subtracting the generic RLHF-assistant "species" (the apologies, \
the "happy to help," the tidy closing question) and keeping only where each model DEPARTED from that consensus. \
Below are your own per-model reads: each model's distinctive line, its departures (each with a verbatim quote), and its signature.

Write a FIELD GUIDE essay — readable, honest, in your own voice — characterizing how these models differ under pressure. \
This is YOUR essay; there is no house style and no predefined taxonomy. Decide your own structure and your own group names \
from what you actually see in the reads.

Hard rules:
- Differential only. Never characterize a model by something true of every assistant. If a model is near-modal, say so plainly — that is an honest result, not a gap to fill with invented color.
- Every quote you use MUST be copied verbatim from the reads below (they were string-verified against transcripts). Do not invent or embellish quotes.
- Group models by behavioral tell (the behavior is the unit; models are exhibits). Name the groups yourself.
- If you find a trait that is both positive/admirable AND shared across one vendor's family, name it — but if that family is your OWN vendor, be especially skeptical and give the unflattering reading too.
- These are reads from N=2 runs per scene, read by eye. Say so. No false precision.

Write 900-1500 words of prose (section headers are fine). Output ONLY the essay in Markdown — no preamble, no JSON."""


def call(reader_slug, content, retries=3):
    body = {
        "model": reader_slug,
        "messages": [
            {"role": "system", "content": ESSAY_PROMPT},
            {"role": "user", "content": content},
        ],
        "temperature": 0.7,   # essay voice, not labeling — allow some prose latitude
        "max_tokens": 16000,
    }
    last = None
    for attempt in range(retries):
        try:
            r = requests.post(
                API,
                headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
                json=body, timeout=400,
            )
            r.raise_for_status()
            raw = r.json()["choices"][0]["message"].get("content")
            if not raw or not raw.strip():
                raise ValueError("empty content")
            return raw.strip()
        except Exception as e:
            last = e
            time.sleep(3 * (attempt + 1))
    return f"<!-- ERROR: {last} -->"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reader", required=True)
    args = ap.parse_args()
    if not os.environ.get("OPENROUTER_API_KEY"):
        sys.exit("OPENROUTER_API_KEY not set")

    reader_dir = ROOT / "reads" / args.reader.replace("/", "__")
    if not reader_dir.exists():
        sys.exit(f"no reads at {reader_dir} — run run_reads.py first")

    content = "--- PER-MODEL READS ---\n\n" + compact_reads(reader_dir)
    n = content.count("MODEL:")
    print(f"reader={args.reader}  reads folded={n}  chars={len(content)}")
    essay = call(args.reader, content)

    out_dir = ROOT / "reads" / "_essay"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{args.reader.replace('/', '__')}.md"
    header = f"<!-- Blind field-guide essay authored by {args.reader} from its own reads ({n} models). No sight of docs/essay.md or any other judge. -->\n\n"
    out.write_text(header + essay + "\n")
    status = "ERROR" if essay.startswith("<!-- ERROR") else f"{len(essay.split())} words"
    print(f"-> {out.relative_to(ROOT)}  ({status})")


if __name__ == "__main__":
    main()
