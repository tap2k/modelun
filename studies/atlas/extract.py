#!/usr/bin/env python3
"""Criterion + spans extraction over transcripts → labels/<model>.json.

One call per sample with the reply and the criteria that apply to its anchor
(spec/criteria.json). The model returns JSON {criterion: [{span, label?}]}. Every span is
located in the reply (atlas.find_span) and stored with start/end offsets; spans that
cannot be located go to dropped_spans. Phrase-unit criteria merge adjacent spans.

  python extract.py                      # all models, sample 0 only
  python extract.py --samples all
  python extract.py --models claude-sonnet-5 --anchors resist-a1
"""
import argparse, json
from functools import lru_cache

import atlas

EXTRACTOR = "google/gemini-3.7-flash"
CRITERIA, VERSION = atlas.criteria()


@lru_cache(maxsize=None)
def prompt_prefix(anchor_id):
    crits = [c for c in CRITERIA.values() if atlas.applies(c, anchor_id)]
    lines = ["Extract spans from the REPLY below. For each criterion, return every span in the reply that meets it, copied verbatim (exact characters, no paraphrase). If none, return an empty list.",
             "Units: for criteria marked [item], return one span per distinct point; several points inside one sentence are separate spans, and one point elaborated over several sentences is ONE span covering all of them. For criteria marked [phrase], return the expression itself; a list of such expressions in one clause is one span.",
             'Return only JSON: {"<criterion_id>": [{"span": "...", "label": "..."}]} — include "label" only where the criterion lists labels.', "", "CRITERIA:"]
    for c in crits:
        lines.append(f"- {c['id']} [{c.get('unit', 'phrase')}]: {c['text']} Examples: {'; '.join(c['seeds'])}."
                     + (f" Labels: {', '.join(c['labels'])}." if c.get("labels") else ""))
    return tuple(c["id"] for c in crits), "\n".join(lines) + "\n\nREPLY:\n"


def extract_one(reply, anchor_id):
    ids, prefix = prompt_prefix(anchor_id)
    j = atlas.post({"model": EXTRACTOR, "messages": [{"role": "user", "content": prefix + reply}],
                    "response_format": {"type": "json_object"}, "usage": {"include": True}})
    out = atlas.parse_json(j["choices"][0]["message"]["content"])
    spans, dropped = {}, []
    for cid in ids:
        kept, drop = atlas.verify_spans(reply, out.get(cid), CRITERIA[cid].get("labels"))
        if CRITERIA[cid].get("unit", "phrase") == "phrase" and len(kept) > 1:
            kept = atlas.merge_adjacent(reply, kept)
        spans[cid] = kept
        dropped += [{"criterion": cid, "span": s} for s in drop]
    return spans, dropped, (j.get("usage") or {}).get("cost", 0) or 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default=None); ap.add_argument("--anchors", default=None)
    ap.add_argument("--samples", default="0", help="'0' (default) or 'all'")
    a = ap.parse_args()
    T = atlas.transcripts()
    models = a.models.split(",") if a.models else list(T)
    anchors = set(a.anchors.split(",")) if a.anchors else None
    atlas.LABELS.mkdir(exist_ok=True)
    total = 0.0
    for m in models:
        d = T[m]
        lp = atlas.LABELS / f"{m}.json"
        L = json.loads(lp.read_text()) if lp.exists() else {"model": m, "slug": d["slug"], "spec_version": d["spec_version"],
                                                           "extractor": {"model": EXTRACTOR, "criteria_version": VERSION}, "samples": []}
        done = {(s["anchor"], s["i"]) for s in L["samples"]}
        for aid, c in d["cells"].items():
            if anchors and aid not in anchors:
                continue
            for i, s in enumerate(c["samples"]):
                if (a.samples != "all" and i != 0) or (aid, i) in done or not s.get("reply"):
                    continue
                try:
                    spans, dropped, cost = extract_one(s["reply"], aid)
                    total += cost
                    L["samples"].append({"anchor": aid, "i": i, "spans": spans, "dropped_spans": dropped})
                    print(f"  {m:20} {aid:14} #{i}  spans={sum(len(v) for v in spans.values()):3} dropped={len(dropped)}  ${cost:.4f}")
                except Exception as e:
                    print(f"  {m:20} {aid:14} #{i}  FAILED: {e}")
            lp.write_text(json.dumps(L, indent=2, ensure_ascii=False) + "\n")   # once per cell
    print(f"total ${total:.3f}")


if __name__ == "__main__":
    main()
