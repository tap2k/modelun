#!/usr/bin/env python3
"""run_extra.py — four more runs of a 4-run battery, in their own directory, so every model reaches 8 (2026-10-03).

The census keeps its second four runs in transcripts-extra/; this fills the models that lack them, and gives
pickword the same: language/transcripts_pickword_extra/. Each model is run as its original file was (host, host
model, provider pin; as served, no reasoning flag), at the spec's own max_tokens; empty replies from reasoning
models are refilled afterwards at --max-tokens 8192, as the originals were. The original 4-run files are not
touched, so published numbers keep their basis, and the new runs double as a re-snapshot of each model.

    python3 run_extra.py --dry-run
    python3 run_extra.py
"""
import json, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN = HERE.parents[1] / "harness" / "run.py"
LANG = HERE.parent / "language"
# No longer served on OpenRouter (404 as of 2026-10-03); Granite and Hermes have local runs (transcripts-local/).
RETIRED = {"anthropic/claude-3-haiku", "ibm-granite/granite-4.1-8b", "nousresearch/hermes-4-70b"}
BATTERIES = [  # study dir, spec, source dir (the 4-run original), out dir
    (HERE, "spec/stimulus.json", "transcripts", "transcripts-extra"),
    (LANG, "spec/pickword.json", "transcripts_pickword", "transcripts_pickword_extra"),
]


def settings(path):
    d = json.loads(path.read_text())
    if {s.get("reasoning_mode") for s in d["scenes"].values()} != {None}:
        sys.exit(f"{path}: has a reasoning mode; this battery runs as served")
    args, slug = [], d["slug"]
    if d.get("host"):
        args += ["--host", d["host"]]
        slug = f"{slug}={d['host_model']}"
    if d.get("provider"):
        args += ["--provider", d["provider"]]
    budgets = {s.get("max_tokens") for s in d["scenes"].values()}
    if len(budgets) == 1 and budgets != {None}:   # a raised budget on every scene was the model's setting
        args += ["--max-tokens", str(budgets.pop())]
    return args + [slug]


def commands():
    for study, spec, src, out in BATTERIES:
        for p in sorted((study / src).glob("*.json")):
            if (study / out / p.name).exists() or json.loads(p.read_text())["slug"] in RETIRED:
                continue
            yield study, ["python3", str(RUN), "--study", ".", "--spec", spec, "--out", out, "--runs", "4"] + settings(p)


def main():
    cmds = list(commands())
    if "--dry-run" in sys.argv:
        for study, c in cmds:
            print(study.name, " ".join(c[2:]))
        print(f"{len(cmds)} commands")
        return
    def go(sc):
        study, c = sc
        return study.name, c[-1], subprocess.run(c, cwd=study, capture_output=True, text=True).returncode
    with ThreadPoolExecutor(12) as ex:
        for study, slug, rc in ex.map(go, cmds):
            print(("ok  " if rc == 0 else "FAIL") + f" {study} {slug}")
    print("run.py exits 0 on failed cells, so check the files for errors")


if __name__ == "__main__":
    main()
