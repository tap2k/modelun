"""Blind arc loader shared by the human coding page (code_server.py) and the LLM open coder
(harness/open_code.py). Same salt -> same blind ids and the same fixed random order, so every
coder, human or model, walks the same sequence."""
import json, random, hashlib
from pathlib import Path


def blind(model, salt):
    return "m" + hashlib.sha1((salt + model).encode()).hexdigest()[:6]


def load_arcs(study, scenes=(), salt="conduct-2026-09"):
    """-> (arcs, reveal). arcs: [{id, blind, scene, subtitle, register, run, turns:[{u, reply}]}]
    in a fixed shuffled order; reveal: blind id -> model."""
    bench = Path(study) / "data" / "benchmark"
    want = set(scenes)
    arcs, reveal = [], {}
    for p in sorted(bench.glob("*.json")):
        if p.name == "markers.json":
            continue
        d = json.loads(p.read_text())
        bid = blind(d["model"], salt); reveal[bid] = d["model"]
        for sid, sc in d["scenes"].items():
            if want and sid not in want:
                continue
            for ri, run in enumerate(sc["runs"]):
                arcs.append({"id": f"{bid}/{sid}/{ri}", "blind": bid, "scene": sid,
                             "subtitle": sc.get("subtitle", sid), "register": sc.get("register", ""),
                             "run": ri, "turns": [{"u": t["u"], "reply": t.get("reply")} for t in run]})
    random.Random(salt).shuffle(arcs)
    return arcs, reveal


def arc_text(arc):
    """The arc as the coder sees it: user turns and assistant replies, nothing else."""
    out = []
    for i, t in enumerate(arc["turns"], 1):
        out.append(f"USER (turn {i}): {t['u']}")
        out.append(f"ASSISTANT (turn {i}): {t['reply'] or '[no reply]'}")
    return "\n\n".join(out)


def sample(arcs, per_scene=0, limit=0):
    """The shared sample: the first `per_scene` arcs of each scene in the fixed order (balanced),
    else the first `limit` arcs, else everything. Human and LLM coders must use the same call."""
    if per_scene:
        seen, out = {}, []
        for a in arcs:
            if seen.get(a["scene"], 0) < per_scene:
                seen[a["scene"]] = seen.get(a["scene"], 0) + 1
                out.append(a)
        return out
    return arcs[:limit] if limit else arcs
