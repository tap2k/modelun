#!/usr/bin/env python3
"""run_brands_ext2.py — the three added brand categories (spec/stimulus_brands_ext2.json) on the full English panel.

Each model is run exactly as it was for the first brand extension: its slug, host, host model, provider pin,
reasoning mode and max_tokens are read from its file in transcripts-brands-ext/, so the 44 English brand categories
share one set of conditions. The hybrids that also have default-reasoning brand runs
(transcripts-brands-ext-default/) get the same rerun into transcripts-brands-ext2-default/.

    python3 run_brands_ext2.py --dry-run     # print the commands
    python3 run_brands_ext2.py               # 8 runs, 8 models at a time; ~101 models x 3 categories, about $1
"""
import json, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN = HERE.parents[1] / "harness" / "run.py"
SPEC = "spec/stimulus_brands_ext2.json"


def settings(path):
    """The run.py arguments that reproduce how this model's brand-extension file was run."""
    d = json.loads(path.read_text())
    scenes = list(d["scenes"].values())
    modes = {s.get("reasoning_mode") for s in scenes}
    budgets = {s.get("max_tokens") for s in scenes}
    if len(modes) > 1 or len(budgets) > 1:
        sys.exit(f"{path.name}: mixed settings across scenes {modes} {budgets}; decide by hand")
    args, slug = [], d["slug"]
    if d.get("host"):
        args += ["--host", d["host"]]
        slug = f"{slug}={d['host_model']}"
    if d.get("provider"):
        args += ["--provider", d["provider"]]
    if modes != {None}:
        args += ["--reasoning", modes.pop()]
    if budgets != {None}:
        args += ["--max-tokens", str(budgets.pop())]
    return args + [slug]


def commands():
    for src, out in (("transcripts-brands-ext", "transcripts-brands-ext2"),
                     ("transcripts-brands-ext-default", "transcripts-brands-ext2-default")):
        for p in sorted((HERE / src).glob("*.json")):
            yield ["python3", str(RUN), "--study", ".", "--spec", SPEC, "--out", out, "--runs", "8"] + settings(p)


def main():
    cmds = list(commands())
    if "--dry-run" in sys.argv:
        for c in cmds:
            print(" ".join(c[2:]))
        print(f"{len(cmds)} commands")
        return
    def go(c):
        r = subprocess.run(c, cwd=HERE, capture_output=True, text=True)
        return c[-1], r.returncode
    with ThreadPoolExecutor(8) as ex:
        for slug, rc in ex.map(go, cmds):
            print(("ok  " if rc == 0 else "FAIL") + f" {slug}")
    print("run.py exits 0 on failed cells, so check the files for errors")


if __name__ == "__main__":
    main()
