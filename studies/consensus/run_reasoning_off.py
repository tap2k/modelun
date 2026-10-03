#!/usr/bin/env python3
"""run_reasoning_off.py — the hybrids' reasoning-off reruns of the as-served batteries (2026-10-03).

The census, expanded and pickword batteries run as served, so a hybrid (a model whose endpoint accepts reasoning
off and that reasons by default) answers them with reasoning on. The brand battery runs reasoning off. These reruns
put the 24 hybrids (the models with transcripts-brands-ext-default/) through the as-served batteries with reasoning
off, each with the host, provider and token budget it had in the brand battery (run_brands_panel.settings), at the
battery's own run count:

    census    spec/stimulus.json               -> transcripts-reasoning-off/ (exists for 91 models; fills the 6
                                                  hybrids added since), 8 runs as there
    expanded  spec/stimulus_expanded.json      -> transcripts-expanded-reasoning-off/, 8 runs
    pickword  ../language/spec/pickword.json   -> ../language/transcripts_pickword_reasoning_off/, 4 runs

    python3 run_reasoning_off.py --dry-run
    python3 run_reasoning_off.py
"""
import subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from run_brands_panel import HERE, RUN, settings

HYBRIDS = sorted((HERE / "transcripts-brands-ext-default").glob("*.json"))
BATTERIES = [  # study dir, spec, out dir, runs
    (HERE, "spec/stimulus.json", "transcripts-reasoning-off", 8),
    (HERE, "spec/stimulus_expanded.json", "transcripts-expanded-reasoning-off", 8),
    (HERE.parent / "language", "spec/pickword.json", "transcripts_pickword_reasoning_off", 4),
]


def commands():
    for study, spec, out, runs in BATTERIES:
        for h in HYBRIDS:
            if (study / out / h.name).exists():
                continue                       # the census reruns already hold 18 of the 24
            args = settings(HERE / "transcripts-brands-ext" / h.name)
            if "--reasoning" not in args:
                sys.exit(f"{h.name}: no reasoning-off setting in transcripts-brands-ext")
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
