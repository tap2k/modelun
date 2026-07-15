"""run_acquired_resample.py — high-n re-sample of the ACQUIRED-default cells.

Companion to run_defaults_resample.py. An "acquired" default is a (model, category) where
JSON shows a stable off-modal answer four-of-four that the model never gave in chat
(Fable's cerulean/carpenter). We re-collect N=20 in both registers to test whether the
JSON rate of that word genuinely exceeds its chat rate (~0) — i.e. the register installs
a new default — rather than an n=4 fluke.

    ../../.venv/bin/python run_acquired_resample.py   # -> probes/acquired_resample.json
"""
import json
import re
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
PLAIN_PROMPT = {s["id"]: s["turns"][0] for s in STIM["scenes"]}
JSON_PROMPT = reg["formats"]["json"]
ROSTER = {m["label"]: m["slug"]
          for m in json.loads((CONSENSUS / "spec/models.json").read_text())["models"]}
labels = sorted(reg["replies"]["json"].keys())
cats = sorted(reg["replies"]["json"][labels[0]].keys())
JP = re.compile(r'"word"\s*:\s*"([^"]+)"')


def pj(r):
    if not r:
        return None
    m = JP.search(r)
    return norm(m.group(1)) if m else norm(r)


def ja(l, c):
    return [w for w in (pj(r) for r in reg["replies"]["json"][l][c]) if w]


def plain_answers(label, cat):
    t = json.loads((CONSENSUS / "transcripts" / f"{label}.json").read_text())
    return [w for w in (norm(r[0].get("reply")) for r in t["scenes"][cat]["runs"]) if w]


field_modal = {c: Counter(a for l in labels for a in plain_answers(l, c)).most_common(1)[0][0]
               for c in cats}

# acquired cells: JSON 4/4 identical, off the field mode, absent from chat
cells = []
for l in labels:
    for c in cats:
        jl, pl = ja(l, c), plain_answers(l, c)
        if len(jl) == 4 and len(set(jl)) == 1 and jl[0] != field_modal[c] and jl[0] not in pl:
            cells.append((l, c, jl[0]))
print(f"{len(cells)} acquired cells across {len(set(l for l,_,_ in cells))} models; "
      f"{len(cells)*2*N} calls", file=sys.stderr)

tasks = []
for (l, c, _w) in cells:
    slug = ROSTER[l]
    for reg_name, prompt in (("plain", PLAIN_PROMPT[c]), ("json", JSON_PROMPT[c])):
        for i in range(N):
            tasks.append((l, c, reg_name, slug, prompt, i))

out = {}
for (l, c, w) in cells:
    out.setdefault(l, {})[c] = {"acquired": w, "field_modal": field_modal[c],
                                "plain": [None] * N, "json": [None] * N}

if __name__ == "__main__":
    key = _key()
    total, done, t0 = len(tasks), 0, time.time()

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
               "note": "high-n re-sample of ACQUIRED-default cells (json-only defaults) "
                       "to test register-installed defaults at n=20.",
               "field_modal": field_modal, "replies": out}
    (HERE / "probes/acquired_resample.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=1) + "\n")
    print(f"-> probes/acquired_resample.json  ({total} calls, {time.time()-t0:.0f}s)", file=sys.stderr)
