#!/usr/bin/env python3
"""Serve the rating page and append verdicts to verdicts/<reviewer>-<date>.jsonl.

  python views/build_rate.py          # make rate_data.js first
  python rate.py                      # then open http://localhost:8765/rate.html
"""
import json, sys
from datetime import date
from http.server import SimpleHTTPRequestHandler, HTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
VERDICTS = HERE / "verdicts"


class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(HERE / "views"), **k)

    def do_POST(self):
        if self.path != "/verdicts":
            self.send_error(404); return
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        VERDICTS.mkdir(exist_ok=True)
        for v in body:
            f = VERDICTS / f"{v['reviewer']}-{v['date']}.jsonl"
            with f.open("a") as fh: fh.write(json.dumps(v, ensure_ascii=False) + "\n")
        self.send_response(204); self.end_headers()

    def log_message(self, *a): pass


port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
print(f"rating at http://localhost:{port}/rate.html  → {VERDICTS}/")
HTTPServer(("127.0.0.1", port), H).serve_forever()
