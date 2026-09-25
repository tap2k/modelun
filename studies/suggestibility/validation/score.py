#!/usr/bin/env python3
"""Score the hand labels in validation/sample.csv against the exact-match rule (validation/key.json).

Reports the confusion matrix, Cohen's kappa on the sample, and accuracy reweighted to the corpus:
each stratum's agreement weighted by its share of all ask and tag replies on the July 45.

    python3 validation/score.py > validation/RESULT-<date>.md
"""
import csv, json, collections
from pathlib import Path

HERE = Path(__file__).resolve().parent
key = json.loads((HERE / "key.json").read_text())
labs = {r["id"]: r["label"].strip().lower() for r in csv.DictReader(open(HERE / "sample.csv")) if r["label"].strip()}
L = ["affirm", "reject", "hedge", "failed"]
bad = {i: l for i, l in labs.items() if l not in L}
assert not bad, f"labels must be one of {L}: {bad}"
pairs = [(key["items"][i]["rule"], l, key["items"][i]["stratum"]) for i, l in labs.items()]
print(f"# Classifier validation\n\n{len(pairs)} of {len(key['items'])} replies labeled.\n")
cm = collections.Counter((a, b) for a, b, _ in pairs)
print("| rule \\ human | " + " | ".join(L) + " |\n|---" * (len(L) + 1) + "|")
for a in L: print(f"| {a} | " + " | ".join(str(cm[(a, b)]) for b in L) + " |")
n = len(pairs); po = sum(a == b for a, b, _ in pairs) / n
pe = sum(sum(a == x for a, _, _ in pairs) * sum(b == x for _, b, _ in pairs) for x in L) / n ** 2
print(f"\nAgreement on the sample {po:.3f}, Cohen's kappa {(po - pe) / (1 - pe):.3f}.\n")
tot = sum(key["corpus_counts"].values()); acc = 0.0
print("| stratum | corpus share | sample n | agreement |\n|---|---|---|---|")
for s, c in sorted(key["corpus_counts"].items(), key=lambda kv: -kv[1]):
    ps = [(a, b) for a, b, st in pairs if st == s]
    ag = sum(a == b for a, b in ps) / len(ps) if ps else None
    if ag is not None: acc += ag * c / tot
    print(f"| {s} | {100 * c / tot:.1f}% | {len(ps)} | {'' if ag is None else f'{ag:.2f}'} |")
print(f"\nAgreement reweighted to the corpus: {acc:.3f} (strata with no labels count as zero).")
aff = [(a == "affirm", b == "affirm", st) for a, b, st in pairs]
acc2 = 0.0
for s, c in key["corpus_counts"].items():
    ps = [(a, b) for a, b, st in aff if st == s]
    acc2 += (sum(a == b for a, b in ps) / len(ps) if ps else (1.0 if s.endswith("/bare") or s.startswith("reject") or s.startswith("failed") else 0.0)) * c / tot
print(f"Agreement on affirm versus not, the distinction the tag effect uses, reweighted to the corpus: {acc2:.3f} "
      "(unsampled strata are bare replies, long rejections and failed cells, none of which the rule calls affirm; "
      "they are counted as agreeing, so this assumes no long rejection is a hidden affirmation).")
