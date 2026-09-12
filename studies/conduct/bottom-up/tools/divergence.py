#!/usr/bin/env python3
"""Divergence screen: rank conduct scenes by how much models split on them.

Judge-free where possible. Four readings per scene, each in [0,1], higher = more split:
  marker   balance of the marker departure rate across models (6 marker scenes only): 1-|2p-1|
  readers  balance of the 3-reader departure rate (fraction of (model,reader) naming the scene)
  lexical  mean pairwise Jaccard distance between models' U4 replies (token sets), avg over runs
  length   coefficient of variation of U4 reply length across models (clipped to 1)
  hedge    balance of the U4 hedge/refusal-phrase rate across models
"""
import json, re, sys, itertools, statistics as st
from pathlib import Path
from collections import defaultdict

STUDY = Path(sys.argv[1] if len(sys.argv) > 1 else "studies/conduct")
BENCH = STUDY / "data" / "benchmark"
XCHECK = STUDY / "bottom-up" / "cross-check"
HEDGE = re.compile(r"\b(i can'?t|i cannot|i'?m sorry|i apologi[sz]e|i'?m not able|i won'?t|as an ai|i understand)\b", re.I)
TOK = re.compile(r"[a-z']+")

def toks(s): return set(TOK.findall((s or "").lower()))
def bal(p): return 1 - abs(2*p - 1)

models = {}
for p in sorted(BENCH.glob("*.json")):
    if p.name == "markers.json": continue
    d = json.loads(p.read_text()); models[d["model"]] = d
scenes = list(next(iter(models.values()))["scenes"].keys())
markers = json.loads((BENCH / "markers.json").read_text())["models"]

# readers: scene subtitle -> fraction of (model, reader) pairs naming it a departure
subtitle = {sid: sc.get("subtitle", sid) for sid, sc in next(iter(models.values()))["scenes"].items()}
dep = defaultdict(int); pairs = 0
for rd in sorted(XCHECK.iterdir()):
    if not rd.is_dir() or rd.name.endswith("drafts"): continue
    for f in rd.glob("*.json"):
        r = json.loads(f.read_text()); pairs += 1
        named = {x["scene"].split("·")[-1].strip() for x in r.get("departures", [])}
        for sid, sub in subtitle.items():
            if sub in named: dep[sid] += 1

rows = []
for sid in scenes:
    # marker balance
    mk = None
    for m, md in markers.items():
        for mid, mv in md.items():
            if mv.get("scene") == sid and mv.get("type") == "binary":
                mk = mid
    if mk:
        vals = [v for m in markers.values() if mk in m for v in m[mk]["runs"] if v is not None]
        p = sum(1 for v in vals if v) / len(vals)
        splits = sum(1 for m in markers.values() if mk in m and m[mk].get("verdict") == "split") / sum(1 for m in markers.values() if mk in m)
        marker_b, marker_p = bal(p), p
    else:
        marker_b = marker_p = splits = None
    readers_p = dep[sid] / pairs if pairs else 0
    # U4 replies per model per run
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
    rows.append((sid, marker_p, splits, readers_p, lexical, length, hedge_p, st.mean(parts)))

rows.sort(key=lambda r: -r[-1])
print(f"{'scene':<15}{'mkr_p':>7}{'split':>7}{'rdr_p':>7}{'lex':>6}{'len':>6}{'hedge':>7}{'score':>7}")
for sid, mp, sp, rp, lx, ln, hp, sc in rows:
    f = lambda x: "   -" if x is None else f"{x:.2f}"
    print(f"{sid:<15}{f(mp):>7}{f(sp):>7}{rp:>7.2f}{lx:>6.2f}{ln:>6.2f}{hp:>7.2f}{sc:>7.2f}")
print(f"\nmodels={len(models)}  reader-pairs={pairs}")
