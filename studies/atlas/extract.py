#!/usr/bin/env python3
"""Criterion + spans extraction over transcripts → labels/<model>.json.

For each sample, one call to the extractor model with the reply and the criteria that
apply to it (spec/criteria.json: applies_to '*' or a list of anchor ids). The model
returns JSON {criterion: [{span, label?}]}. Every span is string-verified against the
reply (whitespace-normalized); unverifiable spans go to dropped_spans. Criteria and seeds
live in spec/criteria.json and freeze with the battery.

  python extract.py                      # all models, sample 0 only
  python extract.py --samples all
  python extract.py --models claude-sonnet-5 --anchors resist-a1
"""
import argparse, json, os, re, sys, time
from pathlib import Path
import requests
from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
load_dotenv(HERE.parent.parent / ".env")
API = "https://openrouter.ai/api/v1/chat/completions"
EXTRACTOR = "google/gemini-3.7-flash"
CRIT = json.loads((HERE / "spec/criteria.json").read_text())
PROMPT_VERSION = CRIT["version"]
# id → (applies_to, text, seeds, labels); the criteria file is the source of truth
CRITERIA = {c["id"]: (c["applies_to"], c["text"], c["seeds"], c.get("labels")) for c in CRIT["criteria"]}


def norm(s):
    return re.sub(r"\s+", " ", s.replace("’", "'").replace("“", '"').replace("”", '"')).strip().lower()


def build_prompt(reply, crits):
    lines = ["Extract spans from the REPLY below. For each criterion, return every span in the reply that meets it, copied verbatim (exact characters, no paraphrase). If none, return an empty list.",
             "Return only JSON: {\"<criterion_id>\": [{\"span\": \"...\", \"label\": \"...\"}]} — include \"label\" only where the criterion lists labels.", "", "CRITERIA:"]
    for cid, (_, text, seeds, labels) in crits.items():
        lines.append(f"- {cid}: {text} Examples: {'; '.join(seeds)}." + (f" Labels: {', '.join(labels)}." if labels else ""))
    lines += ["", "REPLY:", reply]
    return "\n".join(lines)


def call(prompt, retries=3):
    last = None
    for _ in range(retries):
        try:
            r = requests.post(API, headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
                              json={"model": EXTRACTOR, "messages": [{"role": "user", "content": prompt}],
                                    "response_format": {"type": "json_object"}, "usage": {"include": True}}, timeout=180)
            r.raise_for_status(); j = r.json()
            return json.loads(j["choices"][0]["message"]["content"]), j.get("usage", {}).get("cost", 0)
        except Exception as e:
            last = e; time.sleep(3)
    raise last


def verify(reply, out, crits):
    nr = norm(reply); spans, dropped = {}, []
    for cid in crits:
        spans[cid] = []
        for item in out.get(cid, []) or []:
            if not isinstance(item, dict) or not item.get("span"): continue
            sp = item["span"].strip()
            if norm(sp) and norm(sp) in nr:
                rec = {"span": sp}
                if crits[cid][3] and item.get("label") in crits[cid][3]: rec["label"] = item["label"]
                spans[cid].append(rec)
            else:
                dropped.append({"criterion": cid, "span": sp})
    return spans, dropped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default=None); ap.add_argument("--anchors", default=None)
    ap.add_argument("--samples", default="0", help="'0' (default) or 'all'")
    a = ap.parse_args()
    models = a.models.split(",") if a.models else [p.stem for p in sorted((HERE / "transcripts").glob("*.json"))]
    anchors = set(a.anchors.split(",")) if a.anchors else None
    total = 0.0
    for m in models:
        d = json.loads((HERE / "transcripts" / f"{m}.json").read_text())
        (HERE / "labels").mkdir(exist_ok=True)
        lp = HERE / "labels" / f"{m}.json"
        L = json.loads(lp.read_text()) if lp.exists() else {"model": m, "slug": d["slug"], "spec_version": d["spec_version"],
                                                           "extractor": {"model": EXTRACTOR, "prompt_version": PROMPT_VERSION}, "samples": []}
        done = {(s["anchor"], s["i"]) for s in L["samples"]}
        for aid, c in d["cells"].items():
            if anchors and aid not in anchors: continue
            for i, s in enumerate(c["samples"]):
                if a.samples != "all" and i != 0: continue
                if (aid, i) in done or not s.get("reply"): continue
                crits = {k: v for k, v in CRITERIA.items() if v[0] == "*" or aid in v[0]}
                try:
                    out, cost = call(build_prompt(s["reply"], crits)); total += cost
                    spans, dropped = verify(s["reply"], out, crits)
                    L["samples"].append({"anchor": aid, "i": i, "spans": spans, "dropped_spans": dropped})
                    print(f"  {m:20} {aid:14} #{i}  spans={sum(len(v) for v in spans.values()):3} dropped={len(dropped)}  ${cost:.4f}")
                except Exception as e:
                    print(f"  {m:20} {aid:14} #{i}  FAILED: {e}")
                lp.write_text(json.dumps(L, indent=2, ensure_ascii=False) + "\n")
    print(f"total ${total:.3f}")


if __name__ == "__main__":
    main()
