#!/usr/bin/env python3
"""Divergence screen: rank conduct scenes by how much models split on them.

A prioritization heuristic, not a finding: the marker and reader columns are LLM-derived
(the Gemini judge; three LLM readers), the lexical column is flat at token granularity, and no
transcript was read to produce this. Five readings per scene, each in [0,1], higher = more split:
  marker   binary markers: balance of the departure rate across models, 1-|2p-1|;
           graded markers: normalized entropy of the category spread (mkr_p = modal share)
  readers  balance of the 3-reader departure rate (fraction of (model,reader) naming the scene)
  lexical  mean pairwise Jaccard distance between models' U4 replies (token sets), avg over runs
  length   coefficient of variation of U4 reply length across models (clipped to 1)
  hedge    balance of the U4 hedge/refusal-phrase rate across models

    python bottom-up/tools/divergence.py studies/conduct      # prints the table
    from divergence import screen; screen("studies/conduct")   # rows for views/build.py
"""
import json, re, sys, math, itertools, statistics as st
from pathlib import Path
from collections import defaultdict, Counter

HEDGE = re.compile(r"\b(i can'?t|i cannot|i'?m sorry|i apologi[sz]e|i'?m not able|i won'?t|as an ai|i understand)\b", re.I)
TOK = re.compile(r"[a-z']+")
KEYS = ("scene", "marker_p", "splits", "readers_p", "lexical", "length", "hedge_p", "score")


def toks(s): return set(TOK.findall((s or "").lower()))
def bal(p): return 1 - abs(2 * p - 1)


def screen(study):
    """One dict per scene (keys: KEYS), sorted by score, highest first."""
    STUDY = Path(study)
    BENCH = STUDY / "data" / "benchmark"
    XCHECK = STUDY / "bottom-up" / "cross-check"

    models = {}
    for p in sorted(BENCH.glob("*.json")):
        if p.name == "markers.json":
            continue
        d = json.loads(p.read_text()); models[d["model"]] = d
    scenes = list(next(iter(models.values()))["scenes"].keys())
    markers = json.loads((BENCH / "markers.json").read_text())["models"]

    subtitle = {sid: sc.get("subtitle", sid) for sid, sc in next(iter(models.values()))["scenes"].items()}
    dep = defaultdict(int); pairs = 0
    if XCHECK.exists():
        for rd in sorted(XCHECK.iterdir()):
            if not rd.is_dir() or rd.name.endswith("drafts"):
                continue
            for f in rd.glob("*.json"):
                r = json.loads(f.read_text()); pairs += 1
                named = {x["scene"].split("·")[-1].strip() for x in r.get("departures", [])}
                for sid, sub in subtitle.items():
                    if sub in named:
                        dep[sid] += 1

    rows = []
    for sid in scenes:
        mk, mtype = None, None
        for m, md in markers.items():
            for mid, mv in md.items():
                if mv.get("scene") == sid:
                    mk, mtype = mid, mv.get("type")
        have = [m for m in markers.values() if mk in m] if mk else []
        if mk and mtype == "binary":
            vals = [v for m in have for v in m[mk]["runs"] if v is not None]
            p = sum(1 for v in vals if v) / len(vals)
            splits = sum(1 for m in have if m[mk].get("verdict") == "split") / len(have)
            marker_b, marker_p = bal(p), p
        elif mk:
            cats = Counter(v for m in have for v in m[mk]["runs"] if v is not None)
            n = sum(cats.values()); k = len(cats)
            H = -sum(c / n * math.log(c / n) for c in cats.values()) if n else 0.0
            marker_b = H / math.log(k) if k > 1 else 0.0
            marker_p = cats.most_common(1)[0][1] / n if n else None
            splits = sum(1 for m in have if len(set(m[mk]["runs"])) > 1) / len(have)
        else:
            marker_b = marker_p = splits = None
        readers_p = dep[sid] / pairs if pairs else 0.0

        u4 = {m: [run[-1].get("reply") or "" for run in d["scenes"][sid]["runs"]] for m, d in models.items()}
        lex, lens, hed = [], [], []
        for run in range(2):
            sets = {m: toks(r[run]) for m, r in u4.items() if len(r) > run}
            ms = list(sets)
            dists = [1 - len(sets[a] & sets[b]) / max(1, len(sets[a] | sets[b])) for a, b in itertools.combinations(ms, 2)]
            lex.append(st.mean(dists))
            L = [len(u4[m][run].split()) for m in ms]
            lens.append(st.pstdev(L) / max(1, st.mean(L)))
            hed.append(sum(1 for m in ms if HEDGE.search(u4[m][run])) / len(ms))
        lexical = st.mean(lex); length = min(1.0, st.mean(lens)); hedge_p = st.mean(hed)
        parts = [x for x in (marker_b, bal(readers_p), lexical, length, bal(hedge_p)) if x is not None]
        rows.append(dict(zip(KEYS, (sid, marker_p, splits, readers_p, lexical, length, hedge_p, st.mean(parts)))))
    rows.sort(key=lambda r: -r["score"])
    return rows


def main():
    study = sys.argv[1] if len(sys.argv) > 1 else "studies/conduct"
    rows = screen(study)
    f = lambda x: "   -" if x is None else f"{x:.2f}"
    print(f"{'scene':<15}{'mkr_p':>7}{'split':>7}{'rdr_p':>7}{'lex':>6}{'len':>6}{'hedge':>7}{'score':>7}")
    for r in rows:
        print(f"{r['scene']:<15}{f(r['marker_p']):>7}{f(r['splits']):>7}{r['readers_p']:>7.2f}{r['lexical']:>6.2f}{r['length']:>6.2f}{r['hedge_p']:>7.2f}{r['score']:>7.2f}")
    n = len([p for p in (Path(study) / "data" / "benchmark").glob("*.json") if p.name != "markers.json"])
    print(f"\nmodels={n}")


if __name__ == "__main__":
    main()
