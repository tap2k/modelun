"""fill_missing.py — re-ask only the None cells in probes/format_register.json (merge in place).

For when a run is interrupted (rate limits, credits): finds every None reply, re-asks it
with the stored prompt, and writes the file back. Idempotent; run until it reports 0 missing.

    ../../.venv/bin/python fill_missing.py
"""
import json
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = Path(__file__).resolve().parent
CONSENSUS = HERE.parent / "consensus"
sys.path.insert(0, str(CONSENSUS))
from probe_lib import _ask, _key

PATH = HERE / "probes" / "format_register.json"
probe = json.loads(PATH.read_text())
slug = {m["label"]: m["slug"]
        for m in json.loads((CONSENSUS / "spec/models.json").read_text())["models"]}

todo = [(fmt, lab, cat, i)
        for fmt, reps in probe["replies"].items()
        for lab, cats in reps.items()
        for cat, runs in cats.items()
        for i, r in enumerate(runs) if r is None]
print(f"{len(todo)} missing cells")
if not todo:
    sys.exit(0)

key = _key()
done = 0
with ThreadPoolExecutor(max_workers=20) as ex:
    futs = {ex.submit(_ask, slug[lab], probe["formats"][fmt][cat], None, key): (fmt, lab, cat, i)
            for (fmt, lab, cat, i) in todo}
    for f in as_completed(futs):
        fmt, lab, cat, i = futs[f]
        probe["replies"][fmt][lab][cat][i] = f.result()
        done += 1
        if done % 200 == 0 or done == len(todo):
            print(f"  {done}/{len(todo)}", flush=True)

PATH.write_text(json.dumps(probe, indent=1, ensure_ascii=False) + "\n")
still = sum(1 for fmt, reps in probe["replies"].items() for lab, cats in reps.items()
            for cat, runs in cats.items() for r in runs if r is None)
print(f"-> {PATH.name} written; {still} still missing")
