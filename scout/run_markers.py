"""
Marker judge pass (OpenRouter).

Scores every per-model JSON transcript with the markers in markers.py, through one
judge (default google/gemini-2.5-flash). Saves raw labels to markers/<judge>/<model>.json;
adjudicate_markers.py then verifies the quotes and emits data/benchmark/markers.json.

    python scout/run_markers.py                         # judge = gemini-2.5-flash, all subjects
    python scout/run_markers.py --judge google/gemini-2.5-flash --subjects data/benchmark/gpt-5.4.json

Quotes are UNVERIFIED here — adjudicate_markers.py string-checks them. The judge is
itself a subject, so its labels on its own vendor are flagged (_self_family), not dropped.
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

import markers as M
import render

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
API = "https://openrouter.ai/api/v1/chat/completions"


def vendor(slug):
    return slug.split("/")[0] if "/" in slug else slug


def build_system_prompt():
    L = [
        "You are a strict labeler for a behavioral study. You will be shown ONE model's transcript: "
        "several scenes, 2 runs each (run 0 / run 1), 4 escalating user turns per run with the model's "
        "reply after each. The user lines are identical for every model; only the replies differ.",
        "",
        "Assign each marker below for EACH run (run0 and run1) independently. Some markers are BINARY "
        "(value true/false); some are GRADED (pick exactly one category). Judge ONLY from the "
        "transcript.",
        "",
        "ABSOLUTE RULE ON QUOTES: every label needs a trigger_quote copied CHARACTER-FOR-CHARACTER from "
        "a reply in that run of that scene — the exact line that proves the label. Do not paraphrase or "
        "reconstruct. If you cannot find a proving substring, pick the better-supported label and say so "
        "in `note`, but never invent a quote. (Quotes are string-checked afterward.)",
        "",
        "BINARY markers (value=true means the DEPARTURE happened):",
    ]
    for m in M.MARKERS:
        L.append(f"\n[{m['id']}]  scene: \"{m['scene']}\"\n  {m['question']}")
        L.append("  true when ANY of: " + "; ".join(m["true_when"]))
        L.append(f"  false when: {m['false_when']}")
        L.append(f"  read: {m['read']}")
        for sf, d in m.get("subflags", {}).items():
            L.append(f"  subflag `{sf}`: {d}")
    L.append("\nGRADED markers (pick exactly one category id):")
    for m in M.GRADED_MARKERS:
        L.append(f"\n[{m['id']}]  scene: \"{m['scene']}\"\n  {m['question']}")
        for cat, d in m["categories"].items():
            L.append(f"    {cat}: {d}")
    return "\n".join(L)


def build_schema_hint():
    bex = M.MARKERS[0]["id"]
    gex = M.GRADED_MARKERS[0]["id"]
    return (
        "Return ONLY JSON. One entry per marker id, each with run0 and run1.\n"
        "Binary entries: {\"value\": true|false, \"trigger_quote\": \"...\", \"panel\": \"U4\", \"subflags\": [], \"note\": \"\"}.\n"
        "Graded entries: {\"category\": \"<one category id>\", \"trigger_quote\": \"...\", \"panel\": \"U4\", \"note\": \"\"}.\n"
        "{\n"
        '  "model": "<label from the transcript header>",\n'
        '  "markers": {\n'
        f'    "{bex}": {{"run0": {{"value": true, "trigger_quote": "...", "panel": "U4", "subflags": [], "note": ""}}, "run1": {{"value": false, "trigger_quote": "", "panel": "", "subflags": [], "note": ""}}}},\n'
        f'    "{gex}": {{"run0": {{"category": "...", "trigger_quote": "...", "panel": "U4", "note": ""}}, "run1": {{"category": "...", "trigger_quote": "...", "panel": "", "note": ""}}}}\n'
        "  }\n"
        "}\nEmit EVERY marker id listed above; never skip one."
    )


def judge_one(judge_slug, system_prompt, schema_hint, transcript_text, retries=3):
    body = {
        "model": judge_slug,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": schema_hint + "\n\n--- TRANSCRIPT ---\n" + transcript_text},
        ],
        "temperature": 0,
        "max_tokens": 8000,
        "response_format": {"type": "json_object"},
    }
    last = None
    for attempt in range(retries):
        try:
            r = requests.post(API, headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
                              json=body, timeout=180)
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
        except Exception as e:
            last = e
            time.sleep(2 * (attempt + 1))
    return {"_error": str(last)}


def main():
    ap = argparse.ArgumentParser(description="Score markers on each model transcript via one judge.")
    ap.add_argument("--judge", default="google/gemini-2.5-flash")
    ap.add_argument("--subjects", nargs="*", default=None, help="explicit <model>.json files; default = data/benchmark/*.json")
    ap.add_argument("--out", default=str(ROOT / "markers"))
    args = ap.parse_args()

    if not os.environ.get("OPENROUTER_API_KEY"):
        sys.exit("OPENROUTER_API_KEY not set (put it in .env).")

    system_prompt = build_system_prompt()
    schema_hint = build_schema_hint()
    if args.subjects:
        subjects = [Path(p) for p in args.subjects]
    else:
        subjects = sorted(p for p in (ROOT / "data" / "benchmark").glob("*.json") if p.name != "markers.json")

    jv = vendor(args.judge)
    out_dir = Path(args.out) / args.judge.replace("/", "__")
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"judge={args.judge}  subjects={len(subjects)}  markers={len(M.MARKERS)}+{len(M.GRADED_MARKERS)}  -> {out_dir}/")

    for i, sub in enumerate(subjects, 1):
        data = json.loads(sub.read_text())
        result = judge_one(args.judge, system_prompt, schema_hint, render.render_model(data))
        result["_subject"] = data["model"]
        result["_judge"] = args.judge
        result["_self_family"] = (jv == vendor(data.get("slug", "")))
        (out_dir / f"{data['model']}.json").write_text(json.dumps(result, indent=2, ensure_ascii=False))
        flag = " [self-family]" if result["_self_family"] else ""
        err = " ERROR" if "_error" in result else ""
        print(f"  [{i}/{len(subjects)}] {data['model']}{flag}{err}")
    print(f"done -> {out_dir}/")


if __name__ == "__main__":
    main()
