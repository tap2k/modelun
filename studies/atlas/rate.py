#!/usr/bin/env python3
"""Serve the rating page and append verdicts to verdicts/<reviewer>-<date>.jsonl.

  python views/build_rate.py          # make rate_data.js first
  python rate.py                      # then open http://localhost:8765/rate.html
"""
import json, sys
from collections import defaultdict
from http.server import SimpleHTTPRequestHandler, HTTPServer

import atlas

VERDICTS = atlas.HERE / "verdicts"


class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(atlas.HERE / "views"), **k)

    def do_POST(self):
        if self.path != "/verdicts":
            self.send_error(404); return
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        VERDICTS.mkdir(exist_ok=True)
        by_file = defaultdict(list)
        for v in body:
            by_file[f"{v['reviewer']}-{v['date']}.jsonl"].append(json.dumps(v, ensure_ascii=False) + "\n")
        for name, lines in by_file.items():
            with (VERDICTS / name).open("a") as fh:
                fh.writelines(lines)
        self.send_response(204); self.end_headers()

    def log_message(self, *a): pass


port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
print(f"rating at http://localhost:{port}/rate.html  → {VERDICTS}/")
HTTPServer(("127.0.0.1", port), H).serve_forever()
