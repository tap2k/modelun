"""trace_table.py — tabulate trace codes (data/coding/trace.<coder>.jsonl) into the 2x2 per model.

Rows are one per (arc, turn): names_move yes/no, intent_split yes/no, a span from the trace when either
is yes. Model identity is revealed here, after coding, from the bench dir the codes were made on.

    python harness/trace_table.py --study studies/conduct --coder Tap --bench studies/conduct/data/openrouter-thinking/high
"""
import json, argparse
from pathlib import Path
from collections import Counter, defaultdict
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent / "viewer"))
from arcs import load_arcs

ap = argparse.ArgumentParser()
ap.add_argument("--study", default="studies/conduct")
ap.add_argument("--coder", required=True)
ap.add_argument("--bench", default=None, help="the transcripts dir the codes were made on (blind ids depend on it)")
ap.add_argument("--salt", default="conduct-2026-09")
a = ap.parse_args()

_, reveal = load_arcs(a.study, salt=a.salt, bench=a.bench, traces=True)
f = Path(a.study) / "data" / "coding" / f"trace.{a.coder}.jsonl"
rows = [json.loads(l) for l in f.read_text().splitlines() if l.strip()]
by = defaultdict(Counter)
for r in rows:
    by[reveal.get(r["blind"], r["blind"])][(r["names_move"], r["intent_split"])] += 1
print(f"{len(rows)} turns coded by {a.coder}\n")
print(f"{'model':22}{'turns':>6}{'names/split':>13}{'names/match':>13}{'blind/split':>13}{'blind/match':>13}")
for m, c in sorted(by.items()):
    n = sum(c.values())
    print(f"{m:22}{n:>6}{c[('yes','yes')]:>13}{c[('yes','no')]:>13}{c[('no','yes')]:>13}{c[('no','no')]:>13}")
print("\nnames = trace names the user's move; split = trace states an intent the reply does not carry.")
for r in rows:
    if r.get("intent_split") == "yes":
        print(f"\n[{reveal.get(r['blind'], r['blind'])} {r['scene']} run {r['run']} turn {r['turn']+1}] “{r['quote']}”" + (f" — {r['memo']}" if r.get("memo") else ""))
