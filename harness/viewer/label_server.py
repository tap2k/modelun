#!/usr/bin/env python3
"""Local write-back server for closed labeling: one human picks one value per item, written as Contract B.

The human counterpart of an LLM judge on a graded criterion (docs/harness.md § Human labeling: conventions). A study
writes an items file; this serves it one item at a time and appends each label, as soon as it is made, to a
labeler-namespaced Contract B file. Open, manner and trace coding of multi-turn arcs stay with code_server.py.

  items (JSONL, one per item, written by the study):
    {"target": {"model", "scene", "run"},      Contract B's target, less the criterion (this server adds it)
     "show": {"model": ..., ...},              fields displayed above the prompt; --blind hides any of them
     "prompt": "...", "reply": "...",
     "pre": "<value>" | null,                  an optional pre-label, offered and recorded as such
     "pre_by": "<source>" | null,              what made it (a rule, or the judges), recorded with it
     "redo": true}                             relabel under the current --criterion-version: the item counts as
                                               done only once it has a row at that version (docs/harness.md, rule 8)

  out: <out>/labels.<labeler with / as ->.jsonl, append-only. A relabel appends a new row; the latest row per target
  wins. Each row is Contract B plus the labeling record:
    {"labeler", "target": {..., "criterion"}, "kind": "graded", "value", "note",
     "ts", "secs", "blind": [hidden fields], "pre", "pre_by", "criterion_version"}

    python harness/viewer/label_server.py --items <items.jsonl> --out <dir> --labeler human/Tap \\
        --criterion position --values affirm,reject,hedge,refuse [--guide guide.md] [--blind model] [--pass adjudication]
        [--port 8010] [--host 0.0.0.0]
    open http://localhost:8010/label.html

No dependencies beyond the stdlib. State lives in repo files; git is the collaboration layer.
"""
import sys, json, argparse, socket
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, HTTPServer

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from labels import target_id, read_jsonl, latest  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--items", required=True, help="the study's items file (JSONL)")
ap.add_argument("--out", required=True, help="directory for the labeler's Contract B file")
ap.add_argument("--labeler", required=True, help="Contract B labeler, e.g. human/Tap")
ap.add_argument("--criterion", required=True, help="criterion id written into each target")
ap.add_argument("--criterion-version", default="v1", help="the version of the criterion's definitions")
ap.add_argument("--values", required=True, help="comma-separated value space, in key order (1, 2, ...)")
ap.add_argument("--guide", default=None, help="text shown under the item: the definition of each value")
ap.add_argument("--blind", default="", help="comma-separated 'show' fields to hide from the labeler")
ap.add_argument("--pass", dest="pass_", default=None, help="a named second pass (e.g. adjudication): its own file, labels.<labeler>.<pass>.jsonl, and 'pass' on each row, so the first pass stays the reference")
ap.add_argument("--port", type=int, default=8010)
ap.add_argument("--host", default="127.0.0.1", help="0.0.0.0 to label from another device on the local network (no auth)")
args = ap.parse_args()

VIEWS = Path(__file__).resolve().parent
ITEMS = read_jsonl(args.items)
VALUES = [v.strip() for v in args.values.split(",") if v.strip()]
BLIND = [b.strip() for b in args.blind.split(",") if b.strip()]
OUT = Path(args.out) / f"labels.{args.labeler.replace('/', '-')}{'.' + args.pass_ if args.pass_ else ''}.jsonl"
GUIDE = Path(args.guide).read_text() if args.guide else ""
for it in ITEMS:
    it["show"] = {k: v for k, v in (it.get("show") or {}).items() if k not in BLIND}
    it["id"] = target_id(it["target"])
BY_ID = {it["id"]: it for it in ITEMS}
ITEMS_JSON = json.dumps(ITEMS, ensure_ascii=False).encode()     # the item list is fixed for the server's life


class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(VIEWS), **k)

    def _json(self, obj, code=200):
        body = obj if isinstance(obj, bytes) else json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

    def do_GET(self):
        if self.path == "/items.json":
            return self._json(ITEMS_JSON)
        if self.path == "/config":
            return self._json({"labeler": args.labeler, "criterion": args.criterion, "values": VALUES,
                               "guide": GUIDE, "blind": BLIND, "out": str(OUT),
                               "criterion_version": args.criterion_version})
        if self.path == "/labels":       # latest value per target, for resuming
            return self._json({k: {"value": r["value"], "note": r.get("note", ""), "criterion_version": r.get("criterion_version")}
                               for k, r in latest(read_jsonl(OUT)).items()})
        return super().do_GET()

    def do_POST(self):
        if self.path != "/save":
            return self.send_error(404)
        b = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        if b.get("value") not in VALUES:
            return self._json({"error": f"value must be one of {VALUES}"}, 400)
        it = BY_ID.get(b.get("id"))
        if it is None:
            return self._json({"error": "unknown item"}, 400)
        row = {"labeler": args.labeler, "target": {**it["target"], "criterion": args.criterion}, "kind": "graded",
               "value": b["value"], "note": b.get("note", ""), "ts": b.get("ts"), "secs": b.get("secs"),
               "blind": BLIND, "pre": it.get("pre"), "pre_by": it.get("pre_by"),
               "criterion_version": args.criterion_version}
        if args.pass_:
            row["pass"] = args.pass_
        OUT.parent.mkdir(parents=True, exist_ok=True)
        with OUT.open("a") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        return self._json({"ok": True})

    def log_message(self, *a): pass


print(f"labeling {len(ITEMS)} items as {args.labeler} on '{args.criterion}' ({', '.join(VALUES)})"
      + (f", hiding {', '.join(BLIND)}" if BLIND else ""))
print(f"open http://localhost:{args.port}/label.html   -> {OUT}", flush=True)
if args.host != "127.0.0.1":
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1)); lan = s.getsockname()[0]
    except OSError:
        lan = "<this machine's address>"
    finally:
        s.close()
    print(f"on the local network: http://{lan}:{args.port}/label.html   (no auth: anyone on this network can label)", flush=True)
HTTPServer((args.host, args.port), H).serve_forever()
