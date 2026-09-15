#!/usr/bin/env python3
"""Adjudication material for a human manner pass against the LLM coders' majority, per coder.

Writes results/ADJUDICATION-<version>-<coder>-<date>.md: for every code, the arcs where the
human and the majority (3 or more of 6) split, in both directions, with the human's quote and
memo on one side and the coders' most-agreed quote and count on the other. Also the human's
recall and precision by position in coding order (first half vs second half), which separates
fatigue from threshold. The human reads the file and decides; --apply takes a decisions file
(one line per accepted split: "<arc> <tab> <code> <tab> <reason>") and appends the accepted marks
to the human's file flagged adjudicated, with the coders' quote.

    python harness/adjudicate_manner.py --study studies/conduct --version v2 --coder <name>
    python harness/adjudicate_manner.py --study studies/conduct --version v2 --coder <name> --apply decisions.tsv
"""
import json, sys, glob, argparse, collections, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "viewer"))
from arcs import load_arcs

ap = argparse.ArgumentParser(); ap.add_argument("--study", default="studies/conduct"); ap.add_argument("--version", default="v2"); ap.add_argument("--coder", required=True)
ap.add_argument("--arcs-file", default=None); ap.add_argument("--apply", default=None); ap.add_argument("--min-coders", type=int, default=3)
args = ap.parse_args(); study = Path(args.study)
_, reveal = load_arcs(study, (), specimens=True)
hf = study / f"data/coding/manner_{args.version}.{args.coder}.jsonl"
H = [json.loads(l) for l in open(hf) if l.strip()]
harcs = sorted({r["arc"] for r in H}, key=lambda a: min(r["ts"] for r in H if r["arc"] == a))  # coding order
hq = collections.defaultdict(dict)
for r in sorted(H, key=lambda r: r["ts"]):
    if r.get("kind") == "code": hq[r["arc"]].setdefault(r["code"], (r["quote"], r.get("memo", ""), bool(r.get("adjudicated"))))
files = sorted(glob.glob(str(study / f"data/coding/relabel_{args.version}.llm-*.jsonl"))); coders = [Path(f).name[len(f"relabel_{args.version}."):-6] for f in files]
C = collections.defaultdict(lambda: collections.defaultdict(list))
for f, c in zip(files, coders):
    for r in (json.loads(l) for l in open(f) if l.strip()):
        if r["kind"] == "code" and r["arc"] in hq or (r["kind"] == "code" and r["arc"] in set(harcs)): C[r["arc"]][r["code"]].append(r["quote"])
codes = sorted({c for a in harcs for c in list(hq[a]) + list(C[a])})
name = lambda a: f"{reveal.get(a.split('/')[0], a.split('/')[0])} {a.split('/')[1]} run {a.split('/')[2]}"

if args.apply:
    dec = [l.rstrip("\n").split("\t") for l in open(args.apply) if l.strip() and not l.startswith("#")]
    ts = datetime.datetime.utcnow().isoformat(timespec="milliseconds") + "Z"; n = 0
    with open(hf, "a") as fh:
        for arc, code, *why in dec:
            if code in hq[arc] or not C[arc][code]: continue
            q, k = collections.Counter(C[arc][code]).most_common(1)[0]; b, sc, run = arc.split("/")
            fh.write(json.dumps({"coder": args.coder, "arc": arc, "blind": b, "scene": sc, "run": int(run), "kind": "code", "code": code, "quote": q, "memo": f"adjudicated {ts[:10]} ({k} of {len(coders)} coders): {' '.join(why)}", "ts": ts, "sitting": f"adjudication-{ts[:10]}", "codebook": args.version, "adjudicated": True}, ensure_ascii=False) + "\n"); n += 1
    print(f"applied {n} accepted splits to {hf}"); sys.exit()

out = study / "data/coding/results" / f"ADJUDICATION-{args.version}-{args.coder}-{datetime.date.today().isoformat()}.md"
L = [f"# Adjudication material: {args.coder}, codebook {args.version} ({datetime.date.today().isoformat()})", "",
     f"{len(harcs)} arcs in coding order. Splits between the human and the coders' majority ({args.min_coders} or more of {len(coders)}). HUMAN ONLY: the human marked it, fewer than {args.min_coders} coders did. CODERS ONLY: the majority marked it, the human did not. Decide each against the definition: accept (the human missed it), reject (the coders are wrong or the definition excludes it), or note that the definition is underspecified and write the sentence. Decisions go in a tab-separated file: arc, code, reason; then --apply.", ""]
half = len(harcs) // 2
for label, arcs in (("first half", harcs[:half]), ("second half", harcs[half:])):
    hb = cb = both = 0
    for a in arcs:
        for c in codes:
            h = c in hq[a] and not hq[a][c][2]; k = len(C[a][c]) >= args.min_coders
            hb += h; cb += k; both += h and k
    L.append(f"- {label} of the coding order: human marks {hb}, coders' majority marks {cb}, both {both}; recall {both/max(1,hb):.2f}, precision {both/max(1,cb):.2f}")
L.append("")
for code in codes:
    ho = [a for a in harcs if code in hq[code and a] and not hq[a][code][2] and len(C[a][code]) < args.min_coders]
    co = [a for a in harcs if code not in hq[a] and len(C[a][code]) >= args.min_coders]
    if not ho and not co: continue
    L.append(f"\n## {code}  (human only: {len(ho)}; coders only: {len(co)})\n")
    for a in ho:
        q, memo, _ = hq[a][code]; L.append(f"- HUMAN ONLY, {name(a)} ({len(C[a][code])} coders): \"{q[:160]}\"" + (f"  [memo: {memo[:80]}]" if memo else ""))
    for a in co:
        q, k = collections.Counter(C[a][code]).most_common(1)[0]; L.append(f"- CODERS ONLY, {name(a)} ({k} of {len(coders)}): \"{q[:160]}\"  [human coded: {', '.join(hq[a]) or 'nothing'}]\n  `{a}\t{code}\t`")
out.write_text("\n".join(L) + "\n"); print(f"wrote {out}")
