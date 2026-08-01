"""
Aggregate the house_style grep scan: phrase hits per model, normalized per
transcript. Reads Scout's stored parquet directly.

    .venv/bin/python aggregate_phrases.py
"""

import glob
import json
import re
from collections import Counter, defaultdict

import pandas as pd

f = sorted(glob.glob("scans/scan_id=*/house_style.parquet"))[-1]
df = pd.read_parquet(f)

per_model_hits = defaultdict(Counter)  # model -> phrase -> hits
per_model_n = Counter()  # model -> transcripts scanned

for _, row in df.iterrows():
    meta = json.loads(row["transcript_metadata"])
    m = meta["model_name"]
    per_model_n[m] += 1
    if row["value_type"] == "number" and float(row["value"] or 0) > 0:
        for phrase in re.findall(r"\*\*(.+?)\*\*", str(row["explanation"])):
            per_model_hits[m][phrase.strip()] += 1

phrase_totals = Counter()
for c in per_model_hits.values():
    phrase_totals.update(c)

print(f"scan file: {f}")
print(f"transcripts: {sum(per_model_n.values())}, models: {len(per_model_n)}\n")

print("== phrase totals across the field ==")
for p, n in phrase_totals.most_common():
    models_using = sum(1 for c in per_model_hits.values() if c[p] > 0)
    print(f"  {n:4d} hits  {models_using:2d}/{len(per_model_n)} models  {p!r}")

print("\n== per-model rate (hits per 100 transcripts, any phrase) ==")
rates = {
    m: 100 * sum(per_model_hits[m].values()) / per_model_n[m] for m in per_model_n
}
for m, r in sorted(rates.items(), key=lambda x: -x[1]):
    top = ", ".join(p for p, _ in per_model_hits[m].most_common(2)) or "-"
    print(f"  {r:6.1f}  {m:32s} {top}")
