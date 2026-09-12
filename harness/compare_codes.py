#!/usr/bin/env python3
"""Compare open coders (human and LLM) on the arcs they both coded. Judge-free.

For each pair of coders: span overlap (how much of A's quoted text B also quoted, and vice
versa, measured in characters of the assistant replies), codes per arc, and the arcs coded by
both. Labels are not matched here; that is the reconciliation pass a person does afterwards.

    python harness/compare_codes.py --study studies/conduct
"""
import json, re, argparse, itertools
from pathlib import Path
from collections import defaultdict
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent / "viewer"))
from arcs import load_arcs


def norm(s):
    return re.sub(r"\s+", " ", (s or "").replace("’", "'").replace("“", '"').replace("”", '"')).strip().lower()


def spans(quotes, text):
    out = []
    for q in quotes:
        q = norm(q)
        if not q:
            continue
        k = text.find(q)
        if k >= 0:
            out.append((k, k + len(q)))
    return out


def covered(spans_):
    cov = set()
    for a, b in spans_:
        cov.update(range(a, b))
    return cov


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--study", default="studies/conduct")
    ap.add_argument("--salt", default="conduct-2026-09")
    args = ap.parse_args()
    arcs, reveal = load_arcs(args.study, (), args.salt)
    text = {a["id"]: norm(" ".join(t["reply"] or "" for t in a["turns"])) for a in arcs}
    coding = Path(args.study) / "data" / "coding"
    coders = {}
    for f in sorted(coding.glob("open_codes.*.jsonl")):
        rows = [json.loads(l) for l in f.read_text().splitlines() if l.strip()]
        by = defaultdict(list)
        for r in rows:
            by[r["arc"]].append(r)
        coders[f.stem.replace("open_codes.", "")] = by
    names = list(coders)
    print(f"{'coder':<40}{'arcs':>6}{'codes':>7}{'codes/arc':>10}")
    for n in names:
        arcs_n = [a for a, rs in coders[n].items() if any(r["code"] for r in rs)]
        nc = sum(1 for rs in coders[n].values() for r in rs if r["code"])
        print(f"{n:<40}{len(arcs_n):>6}{nc:>7}{(nc / len(arcs_n) if arcs_n else 0):>10.2f}")
    print()
    print(f"{'A':<32}{'B':<32}{'both':>5}{'A→B':>7}{'B→A':>7}")
    print("  A→B = share of A's quoted characters that B also quoted (on arcs both coded)")
    for a, b in itertools.combinations(names, 2):
        both = [x for x in coders[a] if x in coders[b] and x in text]
        if not both:
            continue
        ab = ba = 0.0
        for x in both:
            ca = covered(spans([r["quote"] for r in coders[a][x]], text[x]))
            cb = covered(spans([r["quote"] for r in coders[b][x]], text[x]))
            ab += (len(ca & cb) / len(ca)) if ca else 0.0
            ba += (len(ca & cb) / len(cb)) if cb else 0.0
        print(f"{a:<32}{b:<32}{len(both):>5}{ab / len(both):>7.2f}{ba / len(both):>7.2f}")


if __name__ == "__main__":
    main()
