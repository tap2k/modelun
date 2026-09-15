"""Blind arc loader shared by the human coding page (code_server.py) and the LLM open coder
(harness/open_code.py). Same salt -> same blind ids and the same fixed random order, so every
coder, human or model, walks the same sequence."""
import json, random, hashlib
from pathlib import Path


def blind(model, salt):
    return "m" + hashlib.sha1((salt + model).encode()).hexdigest()[:6]


def load_arcs(study, scenes=(), salt="conduct-2026-09", specimens=False):
    """-> (arcs, reveal). arcs: [{id, blind, scene, subtitle, register, run, turns:[{u, reply}]}]
    in a fixed shuffled order; reveal: blind id -> model.

    The order is shuffled over the frozen panel (spec/models.txt) only, so adding a transcript
    file never moves an arc a coder has already seen. Models in data/benchmark that are not on
    the panel are dated specimens; with specimens=True they are appended AFTER the panel's
    order, in their own shuffled block, and never enter the per-scene sample."""
    study = Path(study); bench = study / "data" / "benchmark"
    want = set(scenes)
    panel_file = study / "spec" / "models.txt"
    panel = {ln.strip().split("/")[-1] for ln in panel_file.read_text().splitlines() if ln.strip() and not ln.startswith("#")} if panel_file.exists() else None
    arcs, extra, reveal = [], [], {}
    for p in sorted(bench.glob("*.json")):
        if p.name == "markers.json":
            continue
        d = json.loads(p.read_text())
        on_panel = panel is None or d["model"] in panel or d.get("slug", "").split("/")[-1] in panel
        if not on_panel and not specimens:
            continue
        bid = blind(d["model"], salt); reveal[bid] = d["model"]
        target = arcs if on_panel else extra
        for sid, sc in d["scenes"].items():
            if want and sid not in want:
                continue
            for ri, run in enumerate(sc["runs"]):
                target.append({"id": f"{bid}/{sid}/{ri}", "blind": bid, "scene": sid,
                               "subtitle": sc.get("subtitle", sid), "register": sc.get("register", ""),
                               "run": ri, "turns": [{"u": t["u"], "reply": t.get("reply")} for t in run],
                               **({"specimen": True} if target is extra else {})})
    random.Random(salt).shuffle(arcs)
    random.Random(salt + "-specimens").shuffle(extra)
    return arcs + extra, reveal


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
            if a.get("specimen"):
                continue
            if seen.get(a["scene"], 0) < per_scene:
                seen[a["scene"]] = seen.get(a["scene"], 0) + 1
                out.append(a)
        return out
    return arcs[:limit] if limit else arcs
