#!/usr/bin/env python3
"""run_brands_panel.py — a brand spec on the full English panel, each model run as the brand battery ran it.

Each model is run exactly as it was for the first brand extension: its slug, host, host model, provider pin,
reasoning mode and max_tokens are read from its file in transcripts-brands-ext/, so every brand question shares one
set of conditions. The hybrids that also have default-reasoning brand runs (transcripts-brands-ext-default/) get
the same rerun into <out>-default/.

    python3 run_brands_panel.py spec/stimulus_brands_ext2.json transcripts-brands-ext2 --dry-run
    python3 run_brands_panel.py spec/stimulus_brands_ext2.json transcripts-brands-ext2               # ~$1
    python3 run_brands_panel.py spec/perturb/stimulus_brands_recommend_clamp.json transcripts-brands-recommend-clamp
    python3 run_brands_panel.py spec/perturb/stimulus_brands_pick_clamp.json transcripts-brands-pick-clamp
    ... --skip-existing     # after an interruption: run only the models with no file yet
"""
import json, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN = HERE.parents[1] / "harness" / "run.py"


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


def commands(spec, out):
    for src, dst in (("transcripts-brands-ext", out), ("transcripts-brands-ext-default", out + "-default")):
        for p in sorted((HERE / src).glob("*.json")):
            if "--skip-existing" in sys.argv and (HERE / dst / p.name).exists():
                continue                   # a restart after an interrupted batch: finished models are kept
            yield ["python3", str(RUN), "--study", ".", "--spec", spec, "--out", dst, "--runs", "8"] + settings(p)


def main():
    spec, out = sys.argv[1], sys.argv[2]
    cmds = list(commands(spec, out))
    if "--dry-run" in sys.argv:
        for c in cmds:
            print(" ".join(c[2:]))
        print(f"{len(cmds)} commands")
        return
    def go(c):
        r = subprocess.run(c, cwd=HERE, capture_output=True, text=True)
        return c[-1], r.returncode
    with ThreadPoolExecutor(int(dict(a.split("=") for a in sys.argv[3:] if "=" in a).get("--jobs", 12))) as ex:
        for slug, rc in ex.map(go, cmds):
            print(("ok  " if rc == 0 else "FAIL") + f" {slug}")
    print("run.py exits 0 on failed cells, so check the files for errors")


if __name__ == "__main__":
    main()
