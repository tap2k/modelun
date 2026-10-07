"""run_provider_followup.py — the follow-up runs on the provider audit's four mismatches.

The 2026-10-02 audit (probe_provider_audit.py) found four endpoints that do not identify as the model they claim, and
all four are billed a fixed prefix above their peers (probe_billed_tokens.py). Two follow-ups:

  plain   the four mismatches again on a later day, same stimuli, no system prompt
  sysgen  every endpoint of the four models (mismatch and peers) under one neutral system prompt, "You are a helpful
          assistant." (spec/perturb/stimulus_sysgen.json and stimulus_expanded_sysgen.json). A caller's system prompt
          replaces a provider's default one, so if a default prompt explains a mismatch, the mismatch should identify
          as claimed here, and its peers give the same-condition reference.
  off     every endpoint of Kimi K2.5 with reasoning off (harness --reasoning off), no system prompt. The Kimi K2.5
          mismatch serves without reasoning (3 output tokens against about 175 at its peers) and identifies as Kimi
          K2, the non-reasoning predecessor; this tests whether the peers do the same with reasoning off.

Each endpoint is pinned (harness/run.py --provider, no fallbacks), 96 questions x 4 runs. Output, kept out of git
with the rest of transcripts-providers/ (provider names):
  transcripts-providers/followup-<date>/<arm>/<model>/<provider-tag>/{core,expanded}/<model>.json

    ../../.venv/bin/python run_provider_followup.py [plain|sysgen|off ...] [--date YYYY-MM-DD]

Scored by probe_provider_followup.py.
"""
import json, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE / "transcripts-providers"
# the audit's four mismatches, as <model>/<provider-tag> keys; they name providers, so they live in the excluded folder
MISMATCHES = json.loads((ROOT / "followup_endpoints.json").read_text())["mismatches"]
SPECS = {"plain": ("spec/stimulus.json", "spec/stimulus_expanded.json"),
         "off": ("spec/stimulus.json", "spec/stimulus_expanded.json"),
         "sysgen": ("spec/perturb/stimulus_sysgen.json", "spec/perturb/stimulus_expanded_sysgen.json")}


def endpoints(arm):
    meta = json.loads((ROOT / "endpoints-2026-10-02.json").read_text())
    if arm == "plain":
        keys = MISMATCHES
    else:
        models = {meta[k]["model"] for k in MISMATCHES} if arm == "sysgen" else {"moonshotai/kimi-k2.5"}
        keys = [k for k in sorted(meta) if meta[k]["model"] in models and any((ROOT / k).glob("*/*.json"))]
    return [(k, meta[k]) for k in keys]


def run(arm, key, info, day):
    out = ROOT / f"followup-{day}" / arm / key
    for sub, spec in zip(("core", "expanded"), SPECS[arm]):
        cmd = [sys.executable, str(HERE / "../../harness/run.py"), info["model"], "--study", str(HERE), "--spec",
               str(HERE / spec), "--runs", "4", "--provider", info["tag"], "--out", str(out / sub), "--run-date", day,
               "--resume"] + (["--reasoning", "off"] if arm == "off" else [])
        r = subprocess.run(cmd, capture_output=True, text=True)
        print(f"{arm} {key} {sub}: exit {r.returncode} {r.stdout.strip().splitlines()[-1:] if r.stdout else ''}",
              flush=True)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    day = sys.argv[sys.argv.index("--date") + 1] if "--date" in sys.argv else date.today().isoformat()
    args = [a for a in args if a != day]
    arms = args or ["plain", "sysgen"]
    jobs = [(arm, k, info) for arm in arms for k, info in endpoints(arm)]
    with ThreadPoolExecutor(12) as ex:
        list(ex.map(lambda j: run(*j, day), jobs))


if __name__ == "__main__":
    main()
