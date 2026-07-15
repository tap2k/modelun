"""run_defaults_resample.py — high-n re-sample of the stable-default cells.

For every (model, category) that holds a stable off-modal default in the 4-sample chat
census (same non-crowd answer four runs of four), re-collect N samples in BOTH registers
— plain chat and requested-JSON. N=20 lets us estimate each default's per-sample
probability and separate a real register shift from n=4 sampling noise (the W1 null the
reviewer flagged). Same conditions as the study: no system prompt, temperature 1.0.

    ../../.venv/bin/python run_defaults_resample.py   # -> probes/defaults_resample.json
"""
import json
import sys
import time
from pathlib import Path
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = Path(__file__).resolve().parent
CONSENSUS = HERE.parent / "consensus"
sys.path.insert(0, str(CONSENSUS))
from analyze import norm
from probe_lib import _ask, _key

N = 20
reg = json.loads((HERE / "probes/format_register.json").read_text())
STIM = json.loads((CONSENSUS / "spec/stimulus.json").read_text())
PLAIN_PROMPT = {s["id"]: s["turns"][0] for s in STIM["scenes"]}     # full census one-word prompt
JSON_PROMPT = reg["formats"]["json"]                               # {cat: question + JSON clause}
ROSTER = {m["label"]: m["slug"]
          for m in json.loads((CONSENSUS / "spec/models.json").read_text())["models"]}
labels = sorted(reg["replies"]["json"].keys())
cats = sorted(reg["replies"]["json"][labels[0]].keys())


def plain_answers(label, cat):
    t = json.loads((CONSENSUS / "transcripts" / f"{label}.json").read_text())
    return [w for w in (norm(r[0].get("reply")) for r in t["scenes"][cat]["runs"]) if w]


field_modal = {c: Counter(a for l in labels for a in plain_answers(l, c)).most_common(1)[0][0]
               for c in cats}

# identify the stable-default cells: chat 4/4, all identical, off the field mode
cells = []
for l in labels:
    for c in cats:
        pl = plain_answers(l, c)
        if len(pl) == 4 and len(set(pl)) == 1 and pl[0] != field_modal[c]:
            cells.append((l, c, pl[0]))
n_models = len(set(l for l, _, _ in cells))
print(f"{len(cells)} default cells across {n_models} models; "
      f"{len(cells)} x 2 x {N} = {len(cells) * 2 * N} calls", file=sys.stderr)

# task list: each cell x {plain, json} x N samples
tasks = []
for (l, c, _w) in cells:
    slug = ROSTER[l]
    for reg_name, prompt in (("plain", PLAIN_PROMPT[c]), ("json", JSON_PROMPT[c])):
        for i in range(N):
            tasks.append((l, c, reg_name, slug, prompt, i))

out = {}
for (l, c, w) in cells:
    out.setdefault(l, {})[c] = {"default": w, "field_modal": field_modal[c],
                                "plain": [None] * N, "json": [None] * N}

if __name__ == "__main__":
    key = _key()
    total = len(tasks)
    done = 0
    t0 = time.time()

    def work(t):
        l, c, reg_name, slug, prompt, i = t
        return (l, c, reg_name, i, _ask(slug, prompt, None, key))

    with ThreadPoolExecutor(max_workers=24) as ex:
        futs = [ex.submit(work, t) for t in tasks]
        for f in as_completed(futs):
            l, c, reg_name, i, reply = f.result()
            out[l][c][reg_name][i] = reply
            done += 1
            if done % 200 == 0 or done == total:
                print(f"  {done}/{total} ({time.time()-t0:.0f}s)", file=sys.stderr, flush=True)

    payload = {"n": N, "run_date": "2026-07-15", "cells": len(cells),
               "note": "high-n re-sample of stable-default cells (plain + requested-json) "
                       "for the W1 null: estimate per-cell p, separate real register shift "
                       "from n=4 sampling noise.",
               "field_modal": field_modal, "replies": out}
    (HERE / "probes/defaults_resample.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=1) + "\n")
    print(f"-> probes/defaults_resample.json  ({total} calls, {time.time()-t0:.0f}s)", file=sys.stderr)
