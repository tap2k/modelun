#!/usr/bin/env python3
"""Review the notes in a Contract B labels file: the step between closed coding and a new code or an inductive pass.

docs/harness.md § Human labeling: conventions, rule 7. Prints every labeled target whose latest row carries a note,
grouped by value, with the reply it labeled when an items file is given.

    python harness/label_notes.py <labels.human-X.jsonl> [--items <items.jsonl>] [--chars 300]
"""
import argparse, collections
from labels import target_id, read_jsonl, latest

ap = argparse.ArgumentParser()
ap.add_argument("labels")
ap.add_argument("--items", default=None, help="the items file the labels were made from, to show each reply")
ap.add_argument("--chars", type=int, default=300, help="characters of each reply to show")
args = ap.parse_args()

latest = latest(read_jsonl(args.labels))
items = {target_id(it["target"]): it for it in read_jsonl(args.items)} if args.items else {}

noted = collections.defaultdict(list)
for k, r in latest.items():
    if (r.get("note") or "").strip():
        noted[r["value"]].append((k, r))
n = sum(len(v) for v in noted.values())
print(f"{n} of {len(latest)} labeled targets carry a note\n")
for value, rows in sorted(noted.items(), key=lambda kv: -len(kv[1])):
    print(f"== {value} ({len(rows)})")
    for k, r in rows:
        t = r["target"]
        print(f"  [{t.get('model')} · {t.get('scene')} · run {t.get('run')}] note: {r['note'].strip()}")
        it = items.get(k)
        if it:
            print(f"      prompt: {it['prompt']}")
            print(f"      reply:  {it['reply'][:args.chars].replace(chr(10), ' / ')}")
    print()
