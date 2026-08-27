#!/usr/bin/env python3
"""Collect the atlas battery: every model x every anchor x n samples, single-turn.

Writes transcripts/<label>.json, one file per model, merging into existing files (cells
already at n are skipped). Every sample stores the reply, finish_reason, the provider
model id, wall-clock latency, the OpenRouter generation id, and the usage block with USD
cost; the run prints per-call and per-model cost. No temperature is sent (as served);
max_tokens is the spec default or the model's override in spec/models.json.

  python collect.py                      # whole panel
  python collect.py anthropic/claude-sonnet-5 --anchors resist-a1,edit-a1
  python collect.py --dry-run            # verify slugs, count calls, no requests
"""
import argparse, json, os, sys, time
from datetime import datetime
from pathlib import Path

import requests
import atlas


def verify_slugs(slugs):
    served = {m["id"] for m in requests.get(f"{atlas.API}/models", headers=atlas.headers(), timeout=30).json()["data"]}
    missing = [s for s in slugs if s not in served]
    if missing:
        sys.exit(f"not served on OpenRouter: {', '.join(missing)}")


def call(slug, prompt, system_prompt, max_tokens):
    messages = ([{"role": "system", "content": system_prompt}] if system_prompt else []) + [{"role": "user", "content": prompt}]
    t0 = time.monotonic()
    j = atlas.post({"model": slug, "messages": messages, "max_tokens": max_tokens, "usage": {"include": True}})
    choice = j["choices"][0]
    return {"reply": choice["message"]["content"], "finish_reason": choice.get("finish_reason"),
            "model_version": j.get("model"), "generation_id": j.get("id"),
            "latency_s": round(time.monotonic() - t0, 3), "usage": j.get("usage", {})}


def collect(model, sp, n, anchor_ids, out_dir, run_date):
    label, slug = model["label"], model["slug"]
    max_tokens = model.get("max_tokens") or sp["max_tokens"]
    path = out_dir / f"{label}.json"
    data = json.loads(path.read_text()) if path.exists() else {
        "model": label, "slug": slug, "spec_version": sp["spec_version"], "max_tokens": max_tokens, "cells": {}}
    spent = 0.0
    for t, a, prompt in atlas.iter_anchors(sp):
        if anchor_ids and a["id"] not in anchor_ids:
            continue
        cell = data["cells"].setdefault(a["id"], {"template": t["id"], "prompt": prompt, "samples": []})
        for i in range(len(cell["samples"]), n):
            try:
                s = call(slug, prompt, sp.get("system_prompt"), max_tokens)
                s["run_date"] = run_date
                cost = s["usage"].get("cost") or 0.0
                spent += cost
                flag = "" if s["finish_reason"] == "stop" else f" [{s['finish_reason']}]"
                print(f"  {label:20} {a['id']:14} #{i}  {len(s['reply'].split()):4}w  {s['latency_s']:6.1f}s  ${cost:.4f}{flag}")
            except Exception as e:
                s = {"reply": None, "error": str(e), "run_date": run_date}
                print(f"  {label:20} {a['id']:14} #{i}  FAILED: {e}")
            cell["samples"].append(s)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")   # once per cell
    print(f"→ {path}   ${spent:.4f}")
    return spent


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("models", nargs="*", help="OpenRouter slugs (default: spec/models.json panel)")
    ap.add_argument("--n", type=int, default=None, help="samples per cell (default: spec sampling.n_per_cell)")
    ap.add_argument("--anchors", default=None, help="comma-separated anchor ids (default: all)")
    ap.add_argument("--out", default=str(atlas.TRANSCRIPTS))
    ap.add_argument("--run-date", default=datetime.now().strftime("%Y-%m-%d"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not os.environ.get("OPENROUTER_API_KEY"):
        sys.exit("OPENROUTER_API_KEY not set (put it in .env).")
    sp = atlas.spec()
    models = atlas.panel()
    if args.models:
        by_slug = {m["slug"]: m for m in models}
        models = [by_slug.get(s, {"slug": s, "label": s.split("/")[-1]}) for s in args.models]
    n = args.n or sp["sampling"]["n_per_cell"]
    anchor_ids = set(a.strip() for a in args.anchors.split(",")) if args.anchors else None

    verify_slugs([m["slug"] for m in models])
    cells = [a for _, a, _ in atlas.iter_anchors(sp) if not anchor_ids or a["id"] in anchor_ids]
    print(f"spec {sp['spec_version']} · {len(models)} models × {len(cells)} anchors × n={n} = {len(models)*len(cells)*n} calls")
    if args.dry_run:
        return
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    total = sum(collect(m, sp, n, anchor_ids, out_dir, args.run_date) for m in models)
    print(f"total ${total:.4f}")


if __name__ == "__main__":
    main()
