#!/usr/bin/env python3
"""Local write-back server for blind open coding (studies/<study>/docs/inductive-coding.md).

Serves the study's views/ (code.html) and:
  GET  /arcs.json            every (model, scene, run) arc, transcript only. Model identity is
                             replaced by a blind id; no markers, no reads, no judge output.
  GET  /codes/<coder>        that coder's codes so far (resume, autocomplete, saturation).
  POST /save                 append one JSON line to data/coding/open_codes.<coder>.jsonl
  GET  /reveal               blind id -> model, for the codebook view only (after coding).

    python harness/viewer/code_server.py --study studies/conduct [--scenes bad_plan,facts] [--port 8000]
    open http://localhost:8000/code.html

No dependencies beyond the stdlib. State lives in repo files; git is the collaboration layer.
"""
import json, sys, random, hashlib, argparse
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, HTTPServer

ap = argparse.ArgumentParser()
ap.add_argument("--study", default="studies/conduct")
ap.add_argument("--scenes", default="", help="comma-separated scene ids to code (default: all)")
ap.add_argument("--port", type=int, default=8000)
ap.add_argument("--salt", default="conduct-2026-09", help="blind-id salt; keep fixed within a batch")
args = ap.parse_args()

STUDY = Path(args.study).resolve()
BENCH = STUDY / "data" / "benchmark"
CODING = STUDY / "data" / "coding"
VIEWS = STUDY / "views"
WANT = set(s for s in args.scenes.split(",") if s)

def blind(model):
    return "m" + hashlib.sha1((args.salt + model).encode()).hexdigest()[:6]

def load_arcs():
    arcs, reveal = [], {}
    for p in sorted(BENCH.glob("*.json")):
        if p.name == "markers.json":
            continue
        d = json.loads(p.read_text())
        bid = blind(d["model"]); reveal[bid] = d["model"]
        for sid, sc in d["scenes"].items():
            if WANT and sid not in WANT:
                continue
            for ri, run in enumerate(sc["runs"]):
                arcs.append({"id": f"{bid}/{sid}/{ri}", "blind": bid, "scene": sid,
                             "subtitle": sc.get("subtitle", sid), "register": sc.get("register", ""),
                             "run": ri, "turns": [{"u": t["u"], "reply": t.get("reply")} for t in run]})
    rnd = random.Random(args.salt)
    rnd.shuffle(arcs)  # fixed random order per salt, so every coder walks the same sequence
    return arcs, reveal

ARCS, REVEAL = load_arcs()

class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(VIEWS), **k)

    def _json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

    def do_GET(self):
        if self.path == "/arcs.json":
            return self._json(ARCS)
        if self.path == "/reveal":
            return self._json(REVEAL)
        if self.path.startswith("/codes/"):
            coder = self.path.split("/", 2)[2]
            f = CODING / f"open_codes.{coder}.jsonl"
            rows = [json.loads(l) for l in f.read_text().splitlines() if l.strip()] if f.exists() else []
            return self._json(rows)
        return super().do_GET()

    def do_POST(self):
        if self.path != "/save":
            return self.send_error(404)
        row = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        for k in ("coder", "arc", "code", "quote"):
            if not row.get(k):
                return self._json({"error": f"missing {k}"}, 400)
        CODING.mkdir(exist_ok=True)
        with (CODING / f"open_codes.{row['coder']}.jsonl").open("a") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        return self._json({"ok": True})

    def log_message(self, *a): pass

print(f"coding {len(ARCS)} arcs from {STUDY.name} ({', '.join(sorted(WANT)) or 'all scenes'})")
print(f"open http://localhost:{args.port}/code.html   -> {CODING}/open_codes.<coder>.jsonl")
HTTPServer(("127.0.0.1", args.port), H).serve_forever()
