#!/usr/bin/env python3
"""Codebook coverage check: does the codebook have a home for every open code the other coders
produced? Each open code (label, quote, memo) from every open_codes.*.jsonl except the codebook
author's is mapped by a model to one codebook code or NONE; the NONE pile is what the codebook
cannot say, clustered by the same model into candidate codes for the next version. Runs between
the draft and the freeze, and again on each version. Never decides; the human reads the pile.

    python harness/coverage_check.py --study studies/conduct --codebook studies/conduct/data/coding/CODEBOOK-v1-2026-09-14.md \
        --version v1 --author Tap --mapper google/gemini-3.7-flash
"""
import os, re, sys, json, glob, argparse, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from relabel import codebook_text, call

ap = argparse.ArgumentParser()
ap.add_argument("--study", default="studies/conduct"); ap.add_argument("--codebook", required=True); ap.add_argument("--version", required=True)
ap.add_argument("--author", default="Tap"); ap.add_argument("--mapper", default="google/gemini-3.7-flash"); ap.add_argument("--batch", type=int, default=25)
args = ap.parse_args()
cb = codebook_text(args.codebook); names = sorted(set(re.findall(r"\*\*([a-z][a-z ]+)\.\*\*", cb)))
files = [f for f in glob.glob(str(Path(args.study) / "data/coding/open_codes.*.jsonl")) if f".{args.author}." not in f and "-anchor" not in f]
rows = [json.loads(l) | {"_file": Path(f).name} for f in files for l in open(f) if l.strip()]
rows = [r for r in rows if r.get("code")]
SYS = ("You map open codes from a qualitative study onto a fixed codebook. For each open code (label, verbatim quote, memo), "
       "answer with the ONE codebook code that says the same thing about the assistant's conduct, or NONE if no codebook code "
       "covers it. Be strict: NONE when the open code notices something the codebook has no name for (a manner, a move, a "
       "trajectory the codebook lacks), not merely a different wording of an existing code. Use code names exactly.\n"
       "Return JSON: {\"map\": [{\"i\": <index>, \"to\": \"<codebook code>|NONE\", \"why\": \"<ten words>\"}]}\n\n=== CODEBOOK ===\n" + cb)
out = Path(args.study) / "data/coding" / f"COVERAGE-{args.version}.jsonl"
done = {(r["_file"], r["arc"], r["code"]) for r in (json.loads(l) for l in open(out))} if out.exists() else set()
todo = [r for r in rows if (r["_file"], r["arc"], r["code"]) not in done]
print(f"{len(rows)} open codes from {len(files)} coders; {len(todo)} to map -> {out}", flush=True)
for k in range(0, len(todo), args.batch):
    batch = todo[k:k + args.batch]
    text = "\n\n".join(f"[{i}] scene={r['scene']}\nlabel: {r['code']}\nquote: {r['quote']}\nmemo: {r.get('memo','')}" for i, r in enumerate(batch))
    res = call(args.mapper, SYS, text)
    m = {int(x["i"]): x for x in (res.get("map") or []) if str(x.get("i", "")).isdigit()} if "_error" not in res else {}
    with out.open("a") as fh:
        for i, r in enumerate(batch):
            x = m.get(i, {}); to = re.sub(r"[\s.:;,\"']+$", "", (x.get("to") or "").strip())
            to = to if to in names else ("NONE" if to.upper() == "NONE" or not to else f"UNKNOWN:{to}")
            fh.write(json.dumps({"_file": r["_file"], "arc": r["arc"], "scene": r["scene"], "code": r["code"], "quote": r["quote"], "memo": r.get("memo", ""), "to": to, "why": x.get("why", "")}, ensure_ascii=False) + "\n")
    print(f"  {k + len(batch)}/{len(todo)}", flush=True)
res = [json.loads(l) for l in open(out)]
c = collections.Counter(r["to"] for r in res)
print(f"\nmapped: {sum(v for k_, v in c.items() if k_ != 'NONE' and not k_.startswith('UNKNOWN'))}  NONE: {c['NONE']}  unknown: {sum(v for k_, v in c.items() if k_.startswith('UNKNOWN'))}")
for name in names: print(f"  {c[name]:4}  {name}")
