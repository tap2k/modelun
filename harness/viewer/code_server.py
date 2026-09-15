#!/usr/bin/env python3
"""Local write-back server for blind open coding (studies/<study>/docs/inductive-coding.md).

Serves the study's views/ (code.html) and:
  GET  /arcs.json            every (model, scene, run) arc, transcript only. Model identity is
                             replaced by a blind id; no markers, no reads, no judge output.
  GET  /codes/<coder>        that coder's codes so far (resume, autocomplete, saturation).
  POST /save                 append one JSON line to data/coding/open_codes.<coder>.jsonl
  POST /update, /delete      edit or remove one code (matched on arc + ts); /rename relabels a code everywhere
  GET  /reveal               blind id -> model, for the codebook view only (after coding).

    python harness/viewer/code_server.py --study studies/conduct [--scenes bad_plan,facts] [--per-scene 10] [--port 8000]
    open http://localhost:8000/code.html

  Trace mode (docs/inductive-coding.md § Trace coding): each turn shows the stored thinking trace beside the
  reply; per turn, two fixed yes/no questions and a verbatim span from the trace; writes data/coding/trace.<coder>.jsonl.
    python harness/viewer/code_server.py --study studies/conduct --trace --bench studies/conduct/data/openrouter-thinking/high --scenes the_leap,doctors_note

No dependencies beyond the stdlib. State lives in repo files; git is the collaboration layer.
"""
import json, sys, argparse, re
from pathlib import Path
from arcs import load_arcs, sample
from http.server import SimpleHTTPRequestHandler, HTTPServer

ap = argparse.ArgumentParser()
ap.add_argument("--study", default="studies/conduct")
ap.add_argument("--scenes", default="", help="comma-separated scene ids to code (default: all)")
ap.add_argument("--port", type=int, default=8000)
ap.add_argument("--salt", default="conduct-2026-09", help="blind-id salt; keep fixed within a batch")
ap.add_argument("--limit", type=int, default=0, help="serve only the first N arcs of the fixed order")
ap.add_argument("--per-scene", type=int, default=0, help="serve the first N arcs of each scene (a balanced sample); use the same value for the LLM coders")
ap.add_argument("--codebook", default=None, help="manner mode: apply this codebook version (markdown) code by code; the page offers its code names, shows its text, and writes data/coding/manner_<version>.<coder>.jsonl")
ap.add_argument("--version", default="v2", help="codebook version tag for the manner file")
ap.add_argument("--codes", default=None, help="the simple code list (code | what it is | example, plus the per-scene table); the page renders it as cards")
ap.add_argument("--arcs-file", default=None, help="serve only the arc ids listed in this file (the held-out fifty)")
ap.add_argument("--directed", action="store_true", help="directed mode: show each scene's marker question and take a held/departed verdict; writes data/coding/directed.<coder>.jsonl")
ap.add_argument("--trace", action="store_true", help="trace mode: show each turn's thinking trace; two fixed questions per turn; writes data/coding/trace.<coder>.jsonl")
ap.add_argument("--bench", default=None, help="transcripts dir to code (default: <study>/data/benchmark); with a bench dir every file is the coding set")
args = ap.parse_args()

STUDY = Path(args.study).resolve()
BENCH = STUDY / "data" / "benchmark"
CODING = STUDY / "data" / "coding"
VIEWS = STUDY / "views"
WANT = set(s for s in args.scenes.split(",") if s)

ARCS, REVEAL = load_arcs(STUDY, WANT, args.salt, bench=args.bench, traces=args.trace)
ARCS = sample(ARCS, args.per_scene, args.limit)
if args.arcs_file:
    _keep = {l.strip() for l in open(args.arcs_file) if l.strip() and not l.startswith("#")}
    ARCS = [a for a in ARCS if a["id"] in _keep]
if args.trace:                       # only arcs with at least one trace can be trace-coded
    ARCS = [a for a in ARCS if any(t.get("reasoning") for t in a["turns"])]
FILE = "trace" if args.trace else "directed" if args.directed else f"manner_{args.version}" if args.codebook else "open_codes"
CODEBOOK = None
if args.codebook:
    from codebook_text import codebook_text  # the same coder-facing rendering the LLM coders get: sections A to D, evidence stripped
    _cb = codebook_text(args.codebook)
    CODEBOOK = {"version": args.version, "names": sorted(set(re.findall(r"\*\*([a-z][a-z ]+)\.\*\*", _cb))), "text": _cb}
    if args.codes:
        _cards, _scenes, _ties, _sec = [], [], [], None
        for ln in Path(args.codes).read_text().splitlines():
            if ln.startswith("## "): _sec = ln[3:].strip()
            elif ln.startswith("|") and not re.match(r"^\|[-| ]+\|$", ln):
                cells = [c.strip() for c in ln.strip("|").split("|")]
                if _sec and _sec.startswith("What held") and cells[0] != "scene": _scenes.append({"scene": cells[0], "position": cells[1], "held": cells[2], "folded": cells[3]})
                elif _sec in ("If HELD", "If FOLDED") and cells[0] != "code": _cards.append({"code": re.sub(r"\s*\*\(rare\)\*", "", cells[0]), "what": cells[1], "example": cells[2].strip('"'), "traj": "HELD" if _sec == "If HELD" else "FOLDED"})
            elif ln.startswith("- ") and _sec and _sec.startswith("When two"): _ties.append(ln[2:].strip())
        _keys = {"the arithmetic": "facts", "the doctor": "doctors_note", "the day-trader": "bad_plan", "make it better": "make_it_better", "the grief": "pivot"}
        for sc in _scenes: sc["id"] = next((v for k, v in _keys.items() if sc["scene"].lower().startswith(k)), None)
        CODEBOOK.update({"cards": _cards, "scenes": _scenes, "ties": _ties})
        _names = {c["code"] for c in _cards}
        if _names != set(CODEBOOK["names"]): print(f"WARNING: simple list and codebook differ: only in list {sorted(_names - set(CODEBOOK['names']))}, only in codebook {sorted(set(CODEBOOK['names']) - _names)}")
MARKERS = {}
if args.directed:
    sys.path.insert(0, str(STUDY / "spec"))
    from codebook import MARKERS as _M
    mk = json.loads((BENCH / "markers.json").read_text())["models"]
    scene_of = {}
    for md in mk.values():
        for mid, mv in md.items(): scene_of[mid] = mv.get("scene")
    for m in _M:
        if m.get("tier") and scene_of.get(m["id"]):
            MARKERS[scene_of[m["id"]]] = {"id": m["id"], "question": m["question"], "true_when": m["true_when"], "false_when": m["false_when"], "read": m.get("read", "")}
    ARCS = [a for a in ARCS if a["scene"] in MARKERS]
    for a in ARCS: a["marker"] = MARKERS[a["scene"]]

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
        if self.path == "/mode":
            return self._json({"directed": args.directed, "trace": args.trace, "bench": str(args.bench or "data/benchmark"), "codebook": CODEBOOK})
        if self.path == "/reveal":
            return self._json(REVEAL)
        if self.path.startswith("/codes/"):
            coder = self.path.split("/", 2)[2]
            f = CODING / f"{FILE}.{coder}.jsonl"
            rows = [json.loads(l) for l in f.read_text().splitlines() if l.strip()] if f.exists() else []
            return self._json(rows)
        return super().do_GET()

    def _rows(self, coder):
        f = CODING / f"{FILE}.{coder}.jsonl"
        return f, ([json.loads(l) for l in f.read_text().splitlines() if l.strip()] if f.exists() else [])

    def _write(self, f, rows):
        f.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        if self.path == "/update":  # replace one row, matched on (arc, ts)
            f, rows = self._rows(body["coder"]); key = body["key"]; new = body["row"]; n = 0
            for i, r in enumerate(rows):
                if r.get("arc") == key["arc"] and r.get("ts") == key["ts"]:
                    rows[i] = {**r, **new}; n += 1
            self._write(f, rows); return self._json({"ok": True, "updated": n})
        if self.path == "/delete":
            f, rows = self._rows(body["coder"]); key = body["key"]
            kept = [r for r in rows if not (r.get("arc") == key["arc"] and r.get("ts") == key["ts"])]
            self._write(f, kept); return self._json({"ok": True, "deleted": len(rows) - len(kept)})
        if self.path == "/rename":  # rename a code label everywhere (misspellings, merges)
            f, rows = self._rows(body["coder"]); n = 0
            for r in rows:
                if r.get("code") == body["from"]:
                    r["code"] = body["to"]; n += 1
            self._write(f, rows); return self._json({"ok": True, "renamed": n})
        if self.path != "/save":
            return self.send_error(404)
        row = body
        if args.trace:      # one row per (arc, turn): the two answers, a span from the trace when either is yes
            need = ("coder", "arc", "names_move", "intent_split") + (("quote",) if "yes" in (row.get("names_move"), row.get("intent_split")) else ())
        else:
            need = ("coder", "arc", "code") + (() if (args.directed and row.get("verdict") == "held") or row.get("kind") == "trajectory" else ("quote",))  # held is an absence: no span; a trajectory row in manner mode has none
        for k in need:
            if row.get(k) in (None, ""):
                return self._json({"error": f"missing {k}"}, 400)
        CODING.mkdir(exist_ok=True)
        with (CODING / f"{FILE}.{row['coder']}.jsonl").open("a") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        return self._json({"ok": True})

    def log_message(self, *a): pass

print(f"coding {len(ARCS)} arcs from {STUDY.name} ({', '.join(sorted(WANT)) or 'all scenes'})")
print(f"open http://localhost:{args.port}/code.html   -> {CODING}/{FILE}.<coder>.jsonl" + ("   [DIRECTED: marker question, held/departed]" if args.directed else "") + (f"   [TRACE: bench {args.bench}]" if args.trace else ""))
HTTPServer(("127.0.0.1", args.port), H).serve_forever()
