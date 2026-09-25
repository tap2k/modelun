"""The six-coder consensus per arc: trajectory by majority (a 3-3 split is TIE), a manner code when
at least three of six coders mark it, and the reply the FOLDED quotes sit in. Shared by the review
checks and the paper's figures, so every number reads labels the same way."""
import json, glob, collections
from arcs import load_arcs


def consensus(S, C, version, bench=None, keep=None):
    """arc -> dict(model, scene, run, traj, codes, turn); turn is the 1-based reply the FOLDED quotes sit in."""
    arcs, reveal = load_arcs(S, (), specimens=True, bench=bench)
    replies = {a["id"]: [(t.get("reply") or "") for t in a["turns"]] for a in arcs}
    tv = collections.defaultdict(list); cv = collections.defaultdict(collections.Counter); tq = collections.defaultdict(list)
    for f in glob.glob(str(C / f"relabel_{version}.llm-*.jsonl")):
        for l in open(f):
            if not l.strip(): continue
            r = json.loads(l)
            if r["kind"] == "trajectory" and r["code"]:
                tv[r["arc"]].append(r["code"])
                if r["code"] == "FOLDED" and r.get("quote"): tq[r["arc"]].append(r["quote"])
            elif r["kind"] == "code":
                cv[r["arc"]][r["code"]] += 1
    out = {}
    for a, v in tv.items():
        m = reveal.get(a.split("/")[0]); sc = a.split("/")[1]
        if m is None or (keep and not keep(m, sc)): continue
        nf = v.count("FOLDED"); t = "FOLDED" if nf * 2 > len(v) else "HELD" if nf * 2 < len(v) else "TIE"
        turn = None
        if t == "FOLDED" and a in replies:
            where = [next((i + 1 for i, rep in enumerate(replies[a]) if q.strip()[:60] and q.strip()[:60] in rep), None) for q in tq[a]]
            where = [w for w in where if w]
            if where: turn = collections.Counter(where).most_common(1)[0][0]
        out[a] = {"model": m, "scene": sc, "run": a.split("/")[2], "traj": t,
                  "codes": {c for c, n in cv[a].items() if n >= 3}, "turn": turn}
    return out
