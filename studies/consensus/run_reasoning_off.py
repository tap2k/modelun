#!/usr/bin/env python3
"""run_reasoning_off.py — the hybrids' reasoning-off reruns of the as-served batteries (2026-10-03).

Every battery's headline runs as served, so a hybrid (a model whose endpoint accepts reasoning off and that reasons
by default; the list is in spec/runs.json) answers with reasoning on. These reruns put the hybrids through the
batteries with reasoning off, each with the host, provider and token budget of its brand reasoning-off file
(transcripts-brands-ext-off/, read by run_brands_panel.settings), at the battery's own run count:

    census    spec/stimulus.json               -> transcripts-off/ (also holds the other models that accept off), 8 runs
    expanded  spec/stimulus_expanded.json      -> transcripts-expanded-off/, 8 runs
    pickword  ../language/spec/pickword.json   -> ../language/transcripts_pickword_reasoning_off/, 4 runs

    python3 run_reasoning_off.py --dry-run
    python3 run_reasoning_off.py
"""
import json, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from run_brands_panel import HERE, RUN, settings

HYBRIDS = json.loads((HERE / "spec" / "runs.json").read_text())["hybrids"]
BATTERIES = [  # study dir, spec, out dir, runs
    (HERE, "spec/stimulus.json", "transcripts-off", 8),
    (HERE, "spec/stimulus_expanded.json", "transcripts-expanded-off", 8),
    (HERE.parent / "language", "spec/pickword.json", "transcripts_pickword_reasoning_off", 4),
]


def commands():
    for study, spec, out, runs in BATTERIES:
        for h in HYBRIDS:
            if (study / out / f"{h}.json").exists():
                continue                       # already run
            args = settings(HERE / "transcripts-brands-ext-off" / f"{h}.json")
            if "--reasoning" not in args:
                sys.exit(f"{h}: no reasoning-off setting in transcripts-brands-ext-off")
            yield study, ["python3", str(RUN), "--study", ".", "--spec", spec, "--out", out, "--runs", str(runs)] + args


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
