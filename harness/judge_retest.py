#!/usr/bin/env python3
"""Judge test-retest: two adjudicated stores built by the same judge and codebook over the same
transcripts, compared cell by cell. A cell is one marker's value on one run of one model (binary:
True/False; graded: the category, or None when the quote failed verification). Reports agreement
overall and per marker over the models both stores cover, optionally restricted to a panel file.

The older store is read from git, since a re-judge overwrites it in place:

    python harness/judge_retest.py --study studies/conduct --old 16a4d2d~1 \
        [--new <rev>] [--panel studies/cross-instrument/paper/panel.txt] [--json]

Only valid when the transcripts did not change between the two passes. Each store is taken to have
been judged on the transcripts present at the commit that last wrote it; the script compares their
scenes (metadata such as the slug may differ) for every model and refuses if any changed.
"""
import sys, json, argparse, subprocess
from pathlib import Path
from collections import defaultdict

ap = argparse.ArgumentParser()
ap.add_argument("--study", default="studies/conduct")
ap.add_argument("--old", required=True, help="git rev of the earlier store")
ap.add_argument("--new", default=None, help="git rev of the later store (default: working tree)")
ap.add_argument("--panel", default=None, help="restrict to the models listed (one per line, # comments)")
ap.add_argument("--json", action="store_true")
args = ap.parse_args()

study = Path(args.study)
paths = json.loads((study / "spec/paths.json").read_text()) if (study / "spec/paths.json").exists() else {}
store_rel = study / paths.get("store", "store.json")
bench_rel = study / paths.get("transcripts", "transcripts")

def at(rev, path):
    if rev is None:
        return Path(path).read_text()
    return subprocess.check_output(["git", "show", f"{rev}:{path}"], text=True)

old = json.loads(at(args.old, store_rel))["models"]
new = json.loads(at(args.new, store_rel))["models"]
models = sorted(set(old) & set(new))
if args.panel:
    pin = {l.strip() for l in Path(args.panel).read_text().splitlines() if l.strip() and not l.startswith("#")}
    models = [m for m in models if m in pin]

# each store was judged on the transcripts present when it was written, not at the rev asked for
def written(rev):
    return subprocess.check_output(["git", "log", "-1", "--format=%H", rev or "HEAD", "--", str(store_rel)], text=True).strip()
old_bench = written(args.old)
new_bench = args.new and written(args.new)

changed = []
for m in models:
    f = f"{bench_rel}/{m}.json"
    try:
        if json.loads(at(old_bench, f))["scenes"] != json.loads(at(new_bench, f))["scenes"]:
            changed.append(m)
    except subprocess.CalledProcessError:
        changed.append(m)
if changed:
    sys.exit(f"transcripts differ between the two passes for: {', '.join(changed)}; not a test-retest")

by = defaultdict(lambda: [0, 0])
for m in models:
    for mk, cell in old[m].items():
        if not isinstance(cell, dict) or "runs" not in cell:
            continue
        for a, b in zip(cell["runs"], new[m][mk]["runs"]):
            by[mk][0] += 1
            by[mk][1] += a == b

n = sum(t for t, _ in by.values()); same = sum(s for _, s in by.values())
out = {"models": len(models), "cells": n, "overall": round(same / n, 3),
       "by_marker": {mk: round(s / t, 3) for mk, (t, s) in sorted(by.items(), key=lambda kv: -kv[1][1] / kv[1][0])}}
if args.json:
    print(json.dumps(out, indent=1))
else:
    print(f"models {out['models']}  cells {n}  agreement {out['overall']}")
    for mk, r in out["by_marker"].items():
        print(f"  {mk:22} {r:.3f}  ({by[mk][0]} cells)")
