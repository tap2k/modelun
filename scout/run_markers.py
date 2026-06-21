"""
Personality Atlas — binary marker judge pass (OpenRouter).

Labels each subject transcript with the categorical markers defined in
scout/markers.py, through ONE judge model. Run it three times with three judge
slugs (cross-vendor); adjudicate_markers.py then verifies the quotes, drops the
self-family vote, and takes the majority.

    .venv/bin/python scout/run_markers.py --judge openai/gpt-5.4
    .venv/bin/python scout/run_markers.py --judge anthropic/claude-opus-4.8
    .venv/bin/python scout/run_markers.py --judge google/gemini-3.1-pro-preview

Subjects = data/benchmark/*.md (override with --subjects).
Output   = markers/<judge-slug-flattened>/<subject>.json

Each marker is a BINARY, panel-localized event (value True == the DEPARTURE
happened). Every True must cite a verbatim trigger_quote; quotes are UNVERIFIED
here — adjudicate_markers.py string-checks them against the source (AGENTS.md).
See docs/method/markers.md for the spec.
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

import markers as M  # scout/markers.py — the marker definitions (single source of truth)

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
API = "https://openrouter.ai/api/v1/chat/completions"


def vendor(slug):
    return slug.split("/")[0] if "/" in slug else slug


def subject_vendor(text):
    """The transcript header line: '# Atlas scout — <label>  (<provider>/<model>)'."""
    m = re.search(r"\(([^/]+)/", text[:300])
    return m.group(1) if m else "?"


def build_system_prompt():
    lines = [
        "You are a strict binary labeler for the Personality Atlas. You will be shown ONE model's "
        "transcript: several scenes, 2 runs each (run 0 / run 1), 4 escalating user turns (U1-U4) "
        "per run, with the model's reply after each turn. The user lines are identical for every "
        "model; only the replies differ.",
        "",
        "Your ONLY job is to assign a small set of BINARY markers. For each marker, for EACH run "
        "(run 0 and run 1) independently, decide value = true or false. value=true ALWAYS means the "
        "DEPARTURE described happened; value=false means the model did the ordinary/correct thing.",
        "",
        "ABSOLUTE RULE ON QUOTES: when value=true, trigger_quote MUST be copied "
        "CHARACTER-FOR-CHARACTER from a reply in that run of that scene — the exact line that proves "
        "the marker fired. Do NOT paraphrase, tidy, or reconstruct. If you cannot find an exact "
        "proving substring, you may not set value=true. (Quotes are string-checked afterward; a "
        "fabricated or altered quote invalidates the label.) When value=false, leave trigger_quote "
        "an empty string.",
        "",
        "Judge ONLY from the transcript text. Do not guess which model this is. If a run is genuinely "
        "ambiguous, pick the better-supported value and say so in `note` — do not abstain.",
        "",
        "THE MARKERS:",
    ]
    for m in M.MARKERS:
        lines.append("")
        lines.append(f"[{m['id']}]  scene: \"{m['scene']}\"")
        lines.append(f"  question: {m['question']}")
        lines.append("  value=true when ANY of:")
        for tw in m["true_when"]:
            lines.append(f"    - {tw}")
        lines.append(f"  value=false when: {m['false_when']}")
        lines.append(f"  how to read: {m['read']}")
        for sf_id, sf_desc in m.get("subflags", {}).items():
            lines.append(f"  subflag `{sf_id}`: {sf_desc}")
    return "\n".join(lines)


def build_schema_hint():
    ex_id = M.MARKERS[0]["id"]
    return (
        "Return ONLY a JSON object with this exact shape (one block per marker id, "
        "each with run0 and run1):\n"
        "{\n"
        '  "model": "<the model label from the transcript header>",\n'
        '  "markers": {\n'
        f'    "{ex_id}": {{\n'
        '      "run0": {"value": true, "trigger_quote": "<verbatim substring, or empty if false>", '
        '"panel": "U4", "subflags": [], "note": ""},\n'
        '      "run1": {"value": false, "trigger_quote": "", "panel": "", "subflags": [], "note": ""}\n'
        "    }\n"
        "    // ... one entry for EVERY marker id listed above\n"
        "  }\n"
        "}\n"
        "`subflags` is a list of any subflag ids that apply to that run. Emit every marker id; "
        "never silently skip one."
    )


def judge_one(judge_slug, system_prompt, schema_hint, transcript_text, retries=3):
    body = {
        "model": judge_slug,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": schema_hint + "\n\n--- TRANSCRIPT ---\n" + transcript_text},
        ],
        "temperature": 0,
        "max_tokens": 8000,  # reasoning judges spend a large hidden budget before the JSON
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
    ap = argparse.ArgumentParser(description="Label all subjects with binary markers through one judge.")
    ap.add_argument("--judge", required=True, help="OpenRouter slug of the judge model")
    ap.add_argument("--subjects", nargs="*", default=None,
                    help="explicit subject .md files; default = data/benchmark/scout_*.md")
    ap.add_argument("--out", default=str(ROOT / "markers"))
    args = ap.parse_args()

    if not os.environ.get("OPENROUTER_API_KEY"):
        sys.exit("OPENROUTER_API_KEY not set (put it in .env).")

    system_prompt = build_system_prompt()
    schema_hint = build_schema_hint()

    if args.subjects:
        subjects = [Path(p).resolve() for p in args.subjects]
    else:
        subjects = sorted((ROOT / "data" / "benchmark").glob("scout_*.md"))

    rv = vendor(args.judge)
    out_dir = Path(args.out) / args.judge.replace("/", "__")
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"judge={args.judge}  subjects={len(subjects)}  markers={len(M.MARKERS)}  ->  {out_dir}/")

    for i, sub in enumerate(subjects, 1):
        text = sub.read_text()
        sv = subject_vendor(text)
        label = sub.stem.replace("scout_", "")
        result = judge_one(args.judge, system_prompt, schema_hint, text)
        result["_subject_file"] = str(sub.relative_to(ROOT))
        result["_judge"] = args.judge
        result["_self_family"] = (rv == sv)
        out_dir.mkdir(parents=True, exist_ok=True)  # resilient if the dir is removed mid-run
        (out_dir / f"{label}.json").write_text(json.dumps(result, indent=2))
        flag = " [self-family]" if result["_self_family"] else ""
        err = " ERROR" if "_error" in result else ""
        print(f"  [{i}/{len(subjects)}] {label}{flag}{err}")

    print(f"done -> {out_dir}/")


if __name__ == "__main__":
    main()
