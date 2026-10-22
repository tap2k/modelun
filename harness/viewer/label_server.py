#!/usr/bin/env python3
"""Local write-back server for closed labeling: one human picks one value per item, written as Contract B.

The human counterpart of an LLM judge on a graded criterion (docs/harness.md § Human labeling: conventions). A study
writes an items file; this serves it one item at a time and appends each label, as soon as it is made, to a
labeler-namespaced Contract B file. Open, manner and trace coding of multi-turn arcs stay with code_server.py.

  items (JSONL, one per item, written by the study):
    {"target": {"model", "scene", "run"},      Contract B's target, less the criterion (this server adds it)
     "show": {"model": ..., ...},              fields displayed above the prompt; --blind hides any of them
     "prompt": "...", "reply": "...",
     "pre": "<value>" | null,                  an optional pre-label, offered and recorded as such; with --form, a dict
                                               {criterion: value} for the pick-one questions
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

--form <form.json> puts several questions on one card in place of --criterion/--values:
    {"questions": [
      {"criterion": "party", "values": ["D", "R", "other", "decline"], "version": "v1"},     pick one
      {"criterion": "issue", "codes": "<codes.jsonl>", "open": true, "skip_if": {"party": ["decline"]}}]}   pick any
A pick-one question writes graded rows to <out>/<criterion>/labels.<labeler>.jsonl. A pick-any question writes, for
each code in its codes file, a binary row (ticked or not) with criterion <criterion>/<code> to
<out>/<criterion>/<code>/labels.<labeler>.jsonl, so every code is a criterion of its own and label_agree.py,
label_llm.py and label_notes.py read each directory as they read a single-criterion one. With "open", the labeler can
add a code from the card: it is appended to the codes file ({"code", "ts", "by"}; append-only) and offered from then
on; items labeled before it have no row for it, which is "not labeled", not "no". "skip_if" leaves the question out
when an earlier answer is one of the listed values. The card's note goes on the first question's row. An item is done
once it has a row for the first question.

No dependencies beyond the stdlib. State lives in repo files; git is the collaboration layer.
"""
import re, sys, json, argparse, socket
from datetime import datetime, timezone
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, HTTPServer

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from labels import target_id, read_jsonl, latest  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--items", required=True, help="the study's items file (JSONL)")
ap.add_argument("--out", required=True, help="directory for the labeler's Contract B file")
ap.add_argument("--labeler", required=True, help="Contract B labeler, e.g. human/Tap")
ap.add_argument("--criterion", default=None, help="criterion id written into each target")
ap.add_argument("--criterion-version", default="v1", help="the version of the criterion's definitions")
ap.add_argument("--values", default=None, help="comma-separated value space, in key order (1, 2, ...)")
ap.add_argument("--form", default=None, help="JSON: several questions on one card, in place of --criterion/--values")
ap.add_argument("--guide", default=None, help="text shown under the item: the definition of each value")
ap.add_argument("--blind", default="", help="comma-separated 'show' fields to hide from the labeler")
ap.add_argument("--pass", dest="pass_", default=None, help="a named second pass (e.g. adjudication): its own file, labels.<labeler>.<pass>.jsonl, and 'pass' on each row, so the first pass stays the reference")
ap.add_argument("--port", type=int, default=8010)
ap.add_argument("--host", default="127.0.0.1", help="0.0.0.0 to label from another device on the local network (no auth)")
args = ap.parse_args()
if bool(args.form) == bool(args.criterion and args.values):
    ap.error("give either --form or both --criterion and --values")

VIEWS = Path(__file__).resolve().parent
ITEMS = read_jsonl(args.items)
BLIND = [b.strip() for b in args.blind.split(",") if b.strip()]
GUIDE = Path(args.guide).read_text() if args.guide else ""
FILE = f"labels.{args.labeler.replace('/', '-')}{'.' + args.pass_ if args.pass_ else ''}.jsonl"
for it in ITEMS:
    it["show"] = {k: v for k, v in (it.get("show") or {}).items() if k not in BLIND}
    it["id"] = target_id(it["target"])
BY_ID = {it["id"]: it for it in ITEMS}
ITEMS_JSON = json.dumps(ITEMS, ensure_ascii=False).encode()     # the item list is fixed for the server's life

if args.form:
    FORM_PATH = Path(args.form)
    QUESTIONS = json.loads(FORM_PATH.read_text())["questions"]
    for q in QUESTIONS:
        q.setdefault("version", "v1")
        if "codes" in q:
            q["codes_path"] = (FORM_PATH.parent / q["codes"]).resolve()
else:
    QUESTIONS = [{"criterion": args.criterion, "values": [v.strip() for v in args.values.split(",") if v.strip()],
                  "version": args.criterion_version}]
FIRST = QUESTIONS[0]


def codes(q):
    return list(dict.fromkeys(r["code"] for r in read_jsonl(q["codes_path"])))


def out_path(q, code=None):
    """the Contract B file of one criterion: --out itself without --form, else one directory per criterion"""
    if not args.form:
        return Path(args.out) / FILE
    return Path(args.out) / q["criterion"] / (code or "") / FILE


def append(path, row):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def config():
    qs = [{k: v for k, v in q.items() if k != "codes_path"} | ({"codes": codes(q)} if "codes_path" in q else {})
          for q in QUESTIONS]
    return {"labeler": args.labeler, "questions": qs, "form": bool(args.form), "guide": GUIDE, "blind": BLIND,
            "out": str(Path(args.out) if args.form else out_path(FIRST)), "criterion_version": FIRST["version"],
            # the single-question page reads these three
            "criterion": FIRST["criterion"], "values": FIRST.get("values")}


def done_labels():
    """target id -> the first question's latest value, note and version, plus each pick-any question's ticked codes"""
    out = {k: {"value": r["value"], "note": r.get("note", ""), "criterion_version": r.get("criterion_version")}
           for k, r in latest(read_jsonl(out_path(FIRST))).items()}
    for q in QUESTIONS[1:]:
        if "codes_path" in q:
            for c in codes(q):
                for k, r in latest(read_jsonl(out_path(q, c))).items():
                    if r["value"] is True and k in out:
                        out[k].setdefault(q["criterion"], []).append(c)
        else:
            for k, r in latest(read_jsonl(out_path(q))).items():
                if k in out:
                    out[k][q["criterion"]] = r["value"]
    return out


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
            return self._json(config())
        if self.path == "/labels":       # latest labels per target, for resuming
            return self._json(done_labels())
        return super().do_GET()

    def do_POST(self):
        b = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        if self.path == "/add_code":
            q = next((q for q in QUESTIONS if q["criterion"] == b.get("question") and q.get("open")), None)
            code = re.sub(r"[^a-z0-9]+", "-", str(b.get("code", "")).strip().lower()).strip("-")
            if q is None or not code:
                return self._json({"error": "no open question, or an empty code"}, 400)
            if code not in codes(q):
                append(q["codes_path"], {"code": code, "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                                         "by": args.labeler})
            return self._json({"ok": True, "code": code, "codes": codes(q)})
        if self.path != "/save":
            return self.send_error(404)
        it = BY_ID.get(b.get("id"))
        if it is None:
            return self._json({"error": "unknown item"}, 400)
        answers = b.get("answers") or {FIRST["criterion"]: b.get("value")}
        if answers.get(FIRST["criterion"]) not in FIRST["values"]:
            return self._json({"error": f"{FIRST['criterion']} must be one of {FIRST['values']}"}, 400)
        pre = it.get("pre")
        base = {"labeler": args.labeler, "ts": b.get("ts"), "secs": b.get("secs"), "blind": BLIND,
                "pre_by": it.get("pre_by")} | ({"pass": args.pass_} if args.pass_ else {})
        rows = []                        # checked in full before anything is written
        for i, q in enumerate(QUESTIONS):
            skip = q.get("skip_if") or {}
            if any(answers.get(c) in vs for c, vs in skip.items()):
                continue
            if "codes_path" in q:
                ticked = set(answers.get(q["criterion"]) or [])
                rows += [(out_path(q, c), base | {"target": {**it["target"], "criterion": f"{q['criterion']}/{c}"},
                                                  "kind": "binary", "value": c in ticked, "note": "", "pre": None, "pre_by": None,
                                                  "criterion_version": q["version"]}) for c in codes(q)]
                continue
            v = answers.get(q["criterion"])
            if v not in q["values"]:
                return self._json({"error": f"{q['criterion']} must be one of {q['values']}"}, 400)
            rows.append((out_path(q), base | {"target": {**it["target"], "criterion": q["criterion"]}, "kind": "graded",
                                              "value": v, "note": b.get("note", "") if i == 0 else "",
                                              "pre": pre.get(q["criterion"]) if isinstance(pre, dict) else pre,
                                              "criterion_version": q["version"]}))
        for path, row in rows:
            append(path, row)
        return self._json({"ok": True})

    def log_message(self, *a): pass


print(f"labeling {len(ITEMS)} items as {args.labeler} on " + ", ".join(q["criterion"] for q in QUESTIONS)
      + (f", hiding {', '.join(BLIND)}" if BLIND else ""))
print(f"open http://localhost:{args.port}/label.html   -> {Path(args.out) if args.form else out_path(FIRST)}", flush=True)
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
