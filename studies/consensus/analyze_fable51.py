"""analyze_fable51.py — is the Fable 5 -> 5.1 census drop a release change or serving drift?

Scores four answer sets leave-one-out against ONE fixed reference field — the wave-1 (paper)
panel minus Fable 5 itself, 43 models, July transcripts — so the numbers are comparable:

  fable-5   Jul  (census transcript, n=4)     fable-5.1  Sep  (wave-2 transcript, n=4)
  fable-5   Sep  (probes/resnapshot_fable, 8)  fable-5.1  Sep  (probes/resnapshot_fable, 8)

Then lists, per category, the modal answer of each set, flagging where Fable 5 moved between
July and September (drift) and where 5.1 differs from same-day Fable 5 (release).

    ../../.venv/bin/python analyze_fable51.py
"""
import json
import math
from collections import Counter
from pathlib import Path

from analyze import norm

HERE = Path(__file__).resolve().parent
PAPER_N = 44
meta = json.loads((HERE / "spec/models.json").read_text())["models"]
FIELD = [m["label"] for m in meta[:PAPER_N] if m["label"] != "claude-fable-5"]


def from_transcript(label):
    d = json.loads((HERE / f"transcripts/{label}.json").read_text())
    return {c: [t for t in (norm(r[0].get("reply")) for r in sc["runs"] if r) if t] for c, sc in d["scenes"].items()}


def from_probe(label):
    d = json.loads((HERE / "probes/resnapshot_fable.json").read_text())
    return {c: [t for t in (norm(r) for r in reps) if t] for c, reps in d["replies"][label].items()}, d["run_date"]


field = {m: from_transcript(m) for m in FIELD}
cats = sorted({c for m in field.values() for c in m})
pool = {c: Counter(a for m in field.values() for a in m.get(c, [])) for c in cats}
modal = {c: pool[c].most_common(1)[0][0] for c in cats}


def score(ans):
    surp, avoid, selfd = [], [], []
    for c in cats:
        mine = ans.get(c, [])
        if not mine:
            continue
        total, vocab = sum(pool[c].values()), len(set(pool[c]) | set(mine))
        for a in mine:
            surp.append(-math.log2((pool[c].get(a, 0) + 1) / (total + vocab)))
            avoid.append(a != modal[c])
        selfd.append(len(set(mine)) / len(mine))
    n = len(surp)
    return sum(surp) / n, sum(avoid) / n, sum(selfd) / len(selfd), n


sets = {"fable-5 Jul": from_transcript("claude-fable-5"), "fable-5.1 Sep(n4)": from_transcript("claude-fable-5.1")}
p5, date = from_probe("claude-fable-5")
p51, _ = from_probe("claude-fable-5.1")
sets[f"fable-5 {date}"] = p5
sets[f"fable-5.1 {date}"] = p51
sets["sonnet-5 Jul"] = from_transcript("claude-sonnet-5")

print(f"reference field: {len(FIELD)} wave-1 models, July\n")
print(f"{'set':22}{'surprisal':>10}{'avoid':>8}{'selfd':>8}{'n':>5}")
for k, v in sets.items():
    s, a, d, n = score(v)
    print(f"{k:22}{s:10.2f}{a:8.0%}{d:8.0%}{n:5}")


def top(ans, c):
    m = ans.get(c)
    return Counter(m).most_common(1)[0][0] if m else "-"


print(f"\n{'category':18}{'field':14}{'F5 Jul':14}{'F5 ' + date:16}{'F5.1 ' + date:16}  flags")
drift = release = 0
for c in cats:
    a, b, d = top(sets["fable-5 Jul"], c), top(p5, c), top(p51, c)
    flags = []
    if a != b:
        flags.append("DRIFT"); drift += 1
    if b != d:
        flags.append("RELEASE"); release += 1
    if d == modal[c] and b != modal[c]:
        flags.append("->modal")
    print(f"{c:18}{modal[c]:14}{a:14}{b:16}{d:16}  {' '.join(flags)}")
print(f"\ncategories where Fable 5 drifted Jul->Sep: {drift};  where 5.1 differs from same-day Fable 5: {release}")
