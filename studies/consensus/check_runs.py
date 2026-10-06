"""check_runs.py — does spec/runs.json describe the transcript directories as they are?

spec/runs.json is the study's list of what was run (intent); the transcript files are what happened (fact).
This reads every file an entry names and reports where they disagree: a spec_version that is not the entry's
spec, scenes the spec does not have or the file lacks, a run count, a reasoning setting or temperature that is
not the entry's arm, failed cells, a published tag that does not exist, and transcript directories on disk
that no entry covers. Zero API calls.

--index rewrites the README's run table (between the runs:start and runs:end markers) from the manifest and
the file counts.

    ../../.venv/bin/python check_runs.py            # report; exit 1 on a disagreement
    ../../.venv/bin/python check_runs.py --index    # also rewrite the README table
"""

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "spec" / "runs.json"
README = HERE / "README.md"
TIERS = ("core", "extended", "check", "probe", "local")
ARMS = ("served", "off", "temp0")


def manifest():
    return json.loads(MANIFEST.read_text())["runs"]


def files(entry):
    d = HERE / entry["dir"]
    return sorted(d.glob("*/*.json" if entry.get("layout") else "*.json"))


def spec_of(entry):
    s = json.loads((HERE / entry["spec"]).read_text())
    return s.get("spec_version") or s.get("script_version"), {sc["id"] for sc in s["scenes"]}


def check(entry, tags, hybrids):
    """(problems, notes, files read). A problem is a disagreement with the manifest; a note is a fact the files
    record that a reader should know (failed cells, files with no answer at all)."""
    out, notes, fs = [], [], files(entry)
    if not fs:
        return [f"no files in {entry['dir']}"], notes, 0
    if entry["tier"] not in TIERS or entry["arm"] not in ARMS:
        out.append(f"tier {entry['tier']!r} or arm {entry['arm']!r} not one of {TIERS} / {ARMS}")
    for t in entry.get("published", []):
        if t not in tags:
            out.append(f"published tag {t} does not exist")
    version, scenes = spec_of(entry)
    bad_version, extra, missing, runs, modes, temps, failed, empty = Counter(), set(), 0, Counter(), Counter(), Counter(), 0, []
    hybrid_modes, partial = Counter(), 0      # "partial": models the entry declares stopped early, with the reason in its note
    for f in fs:
        d = json.loads(f.read_text())
        want = {s for s in scenes if s.endswith("__" + f.parent.name)} if entry.get("layout") else scenes
        if d.get("spec_version") != version:
            bad_version[d.get("spec_version")] += 1
        temps[d.get("temperature")] += 1
        extra |= set(d["scenes"]) - want
        if f.stem in entry.get("partial", ()):
            partial += len(want - set(d["scenes"]))
        else:
            missing += len(want - set(d["scenes"]))
        cells = [cell for sc in d["scenes"].values() for run in sc["runs"] for cell in run]
        for sc in d["scenes"].values():
            runs[len(sc["runs"])] += 1
            modes[sc.get("reasoning_mode")] += 1
            if f.stem in hybrids:
                hybrid_modes[sc.get("reasoning_mode")] += 1
        n = sum(1 for cell in cells if cell.get("error"))
        failed += n
        if cells and n == len(cells):
            empty.append(d.get("model", f.stem))
    if bad_version:
        out.append(f"spec_version is not {version!r}: {dict(bad_version)}")
    if extra:
        out.append(f"{len(extra)} scene ids not in {entry['spec']}, e.g. {sorted(extra)[:3]}")
    if missing:
        out.append(f"{missing} model x scene cells missing from the files")
    if partial:
        notes.append(f"{partial} cells missing from models declared partial: {', '.join(entry['partial'])}")
    if set(runs) != {entry["runs"]}:
        out.append(f"runs per scene {dict(runs)}, manifest says {entry['runs']}")
    arm, other = entry["arm"], set(modes) - {None, "off"}
    if other:
        out.append(f"reasoning_mode {sorted(other)} present")
    if arm == "served" and hybrid_modes.get("off"):
        out.append(f"arm served but {hybrid_modes['off']} hybrid scenes ran reasoning off")
    if arm == "off" and (not modes.get("off") or set(hybrid_modes) - {"off"}):
        out.append(f"arm off but reasoning_mode is {dict(modes)} (hybrids {dict(hybrid_modes)})")
    if set(temps) != {0.0 if arm == "temp0" else 1.0}:
        out.append(f"temperature {dict(temps)} does not fit arm {arm}")
    if entry["models"] == "hybrids" and {f.stem for f in fs} - set(hybrids):
        out.append(f"models hybrids but files for {sorted({f.stem for f in fs} - set(hybrids))}")
    if empty:
        notes.append(f"{len(empty)} files with no answer at all (every cell failed): {', '.join(sorted(empty))}")
    if failed:
        notes.append(f"{failed} failed cells recorded in the files")
    return out, notes, len(fs)


def orphans(entries):
    """Transcript directories holding Contract-A files that no entry names."""
    named = {e["dir"] for e in entries}
    found = set()
    for d in HERE.glob("transcripts*"):
        if any(d.glob("*.json")):
            found.add(d.name)
        for sub in d.iterdir():
            if sub.is_dir() and any(sub.glob("*.json")) and d.name not in named:
                found.add(f"{d.name}/{sub.name}")
    return sorted(found - named)


def index(entries, counts):
    """The README table: one row per entry, grouped by tier."""
    rows = []
    for tier in TIERS:
        group = [e for e in entries if e["tier"] == tier]
        if not group:
            continue
        rows += [f"\n**{tier}**\n", "| id | directory | battery | form | wording | arm | models | runs |",
                 "|---|---|---|---|---|---|---|---|"]
        for e in group:
            pub = " (published)" if e.get("published") else ""
            rows.append(f"| {e['id']} | `{e['dir']}/`{pub} | {e['battery']} ({e['categories']}) | {e['form']} "
                        f"| {e['wording']} | {e['arm']} | {e['models']} ({counts[e['id']]}) | {e['runs']} |")
    return "\n".join(rows).lstrip("\n")


def write_index(text):
    readme = README.read_text()
    start, end = "<!-- runs:start -->", "<!-- runs:end -->"
    if start not in readme or end not in readme:
        sys.exit(f"README.md has no {start} ... {end} block")
    head, rest = readme.split(start, 1)
    README.write_text(head + start + "\n" + text + "\n" + end + rest.split(end, 1)[1])


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--index", action="store_true", help="rewrite the README run table")
    args = ap.parse_args()
    entries = manifest()
    hybrids = set(json.loads(MANIFEST.read_text()).get("hybrids", []))
    ids = Counter(e["id"] for e in entries)
    tags = set(subprocess.run(["git", "tag"], cwd=HERE, capture_output=True, text=True).stdout.split())
    problems, counts = 0, {}
    for e in entries:
        out, notes, counts[e["id"]] = check(e, tags, hybrids)
        if ids[e["id"]] > 1:
            out.append("duplicate id")
        problems += len(out)
        print(f"{'ok ' if not out else '!! '} {e['id']:<32} {counts[e['id']]:>3} files")
        for line in out:
            print(f"      {line}")
        for line in notes:
            print(f"      note: {line}")
    for d in orphans(entries):
        problems += 1
        print(f"!!  {d}: transcripts on disk with no entry in spec/runs.json")
    if args.index:
        write_index(index(entries, counts))
        print(f"→ {README.name} run table")
    print(f"\n{len(entries)} entries, {problems} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
