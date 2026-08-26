#!/usr/bin/env python3
"""Collect the atlas everyday battery: every model x every anchor x n samples, single-turn.

Writes transcripts/<label>.json, one file per model, merging into existing files (a cell
with n samples already is skipped, so reruns only fill gaps). Every sample stores the
reply, finish_reason, the provider-reported model id, and OpenRouter's usage block
including USD cost; the run prints per-call and per-model cost and a grand total.

  python collect.py                      # whole panel from spec/models.json
  python collect.py anthropic/claude-sonnet-5 --anchors resist-a1,edit-a1
  python collect.py --dry-run            # verify slugs, count calls, no requests
"""
import argparse, json, os, sys, time
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
load_dotenv(ROOT / ".env")
API = "https://openrouter.ai/api/v1"


def headers():
    return {"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"}


def verify_slugs(slugs):
    served = {m["id"] for m in requests.get(f"{API}/models", headers=headers(), timeout=30).json()["data"]}
    missing = [s for s in slugs if s not in served]
    if missing:
        sys.exit(f"not served on OpenRouter: {', '.join(missing)}")


def call(slug, prompt, system_prompt, retries=3):
    """One single-turn call. No temperature and no max_tokens: both as served."""
    messages = ([{"role": "system", "content": system_prompt}] if system_prompt else []) + \
               [{"role": "user", "content": prompt}]
    body = {"model": slug, "messages": messages, "usage": {"include": True}}
    last = None
    for _ in range(retries):
        try:
            t0 = time.monotonic()
            r = requests.post(f"{API}/chat/completions", headers=headers(), json=body, timeout=180)
            latency = time.monotonic() - t0
            r.raise_for_status()
            j = r.json()
            choice = j["choices"][0]
            reply = choice["message"].get("content")
            if not reply:
                raise ValueError("empty content")
            return {"reply": reply,
                    "finish_reason": choice.get("finish_reason"),
                    "model_version": j.get("model"),
                    "generation_id": j.get("id"),
                    "latency_s": round(latency, 3),
                    "usage": j.get("usage", {})}
        except Exception as e:
            last = e
            time.sleep(3)
    raise last


def iter_cells(spec, anchor_ids):
    for t in spec["templates"]:
        for a in t["anchors"] + t.get("rotation", []):
            if anchor_ids and a["id"] not in anchor_ids:
                continue
            yield t, a, t["template"].replace("{text}", a["text"])


def collect(model, spec, n, anchor_ids, out_dir, run_date):
    label, slug = model["label"], model["slug"]
    path = out_dir / f"{label}.json"
    data = json.loads(path.read_text()) if path.exists() else {
        "model": label, "slug": slug, "spec_version": spec["spec_version"],
        "cells": {}}
    spent = 0.0
    for t, a, prompt in iter_cells(spec, anchor_ids):
        cell = data["cells"].setdefault(a["id"], {"template": t["id"], "prompt": prompt, "samples": []})
        while len(cell["samples"]) < n:
            i = len(cell["samples"])
            try:
                s = call(slug, prompt, spec.get("system_prompt"))
                s["run_date"] = run_date
                cost = s["usage"].get("cost") or 0.0
                spent += cost
                words = len(s["reply"].split())
                flag = "" if s["finish_reason"] == "stop" else f" [{s['finish_reason']}]"
                print(f"  {label:20} {a['id']:14} #{i}  {words:4}w  {s['latency_s']:6.1f}s  ${cost:.4f}{flag}")
            except Exception as e:
                s = {"reply": None, "error": str(e), "run_date": run_date}
                print(f"  {label:20} {a['id']:14} #{i}  FAILED: {e}")
            cell["samples"].append(s)
            out_dir.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"→ {path}   ${spent:.4f}")
    return spent


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("models", nargs="*", help="OpenRouter slugs (default: spec/models.json panel)")
    ap.add_argument("--n", type=int, default=None, help="samples per cell (default: spec sampling.n_per_cell)")
    ap.add_argument("--anchors", default=None, help="comma-separated anchor ids (default: all)")
    ap.add_argument("--out", default=str(HERE / "transcripts"))
    ap.add_argument("--run-date", default=datetime.now().strftime("%Y-%m-%d"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not os.environ.get("OPENROUTER_API_KEY"):
        sys.exit("OPENROUTER_API_KEY not set (put it in .env).")
    spec = json.loads((HERE / "spec/stimulus.json").read_text())
    panel = json.loads((HERE / "spec/models.json").read_text())["models"]
    if args.models:
        by_slug = {m["slug"]: m for m in panel}
        panel = [by_slug.get(s, {"slug": s, "label": s.split("/")[-1]}) for s in args.models]
    n = args.n or spec["sampling"]["n_per_cell"]
    anchor_ids = set(a.strip() for a in args.anchors.split(",")) if args.anchors else None

    verify_slugs([m["slug"] for m in panel])
    cells = list(iter_cells(spec, anchor_ids))
    print(f"spec {spec['spec_version']} · {len(panel)} models × {len(cells)} anchors × n={n} = {len(panel)*len(cells)*n} calls")
    if args.dry_run:
        return
    total = 0.0
    for m in panel:
        total += collect(m, spec, n, anchor_ids, Path(args.out), args.run_date)
    print(f"total ${total:.4f}")


if __name__ == "__main__":
    main()
