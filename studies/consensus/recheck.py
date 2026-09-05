"""recheck.py — has a model's census answer set drifted since its transcript was collected?

Re-collects the full 31-category chat battery for the named labels today (census conditions:
no system prompt, temperature 1.0, n=8, same day), then scores each label twice against ONE
fixed reference field — the wave-1 paper panel minus the label itself, July transcripts — so the
numbers are comparable: the transcript in transcripts/ (n=4, dated) vs today's snapshot. Then a
per-category table of modal answers, flagging DRIFT where today's modal differs from the
transcript's and ->modal / <-modal where the move lands on or leaves the field's #1 answer.

The Fable 5 -> 5.1 pair was the first use of this design (probe_fable51.py / analyze_fable51.py,
which add the same-day cross-release comparison); this is the generic single-label version.

    ../../.venv/bin/python recheck.py gpt-5.6-sol gpt-5.6-terra gpt-5.6-luna
        # -> probes/recheck_<date>.json (labels merged into the day's file), then the report
    ../../.venv/bin/python recheck.py --score probes/recheck_2026-09-04.json
        # report only, from an existing file
"""
import json
import math
import sys
from collections import Counter
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from analyze import norm
from probe_lib import run_battery

PAPER_N = 44
STIM = json.loads((HERE / "spec/stimulus.json").read_text())
PROMPTS = {s["id"]: s["turns"][0] for s in STIM["scenes"]}
ROSTER = json.loads((HERE / "spec/models.json").read_text())["models"]
WAVE1 = [m["label"] for m in ROSTER[:PAPER_N]]


def from_transcript(label):
    d = json.loads((HERE / f"transcripts/{label}.json").read_text())
    ans = {c: [t for t in (norm(r[0].get("reply")) for r in sc["runs"] if r) if t] for c, sc in d["scenes"].items()}
    dates = sorted({sc.get("run_date") for sc in d["scenes"].values()})
    return ans, dates[0] if len(dates) == 1 else f"{dates[0]}..{dates[-1]}"


def make_scorer(exclude):
    field = {m: from_transcript(m)[0] for m in WAVE1 if m != exclude}
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

    return score, cats, modal, len(field)


def top(ans, c):
    m = ans.get(c)
    return Counter(m).most_common(1)[0][0] if m else "-"


def report(probe):
    today = probe["run_date"]
    for label, reps in probe["replies"].items():
        now = {c: [t for t in (norm(r) for r in rs) if t] for c, rs in reps.items()}
        then, then_date = from_transcript(label)
        score, cats, modal, nfield = make_scorer(label)
        print(f"\n== {label}   reference field: {nfield} wave-1 models, July (leave-one-out)")
        print(f"{'set':26}{'surprisal':>10}{'avoid':>8}{'selfd':>8}{'n':>5}")
        for k, v in ((f"transcript {then_date}", then), (f"recheck {today}", now)):
            s, a, d, n = score(v)
            print(f"{k:26}{s:10.2f}{a:8.0%}{d:8.0%}{n:5}")
        print(f"\n{'category':18}{'field':14}{'transcript':14}{'today':14}  flags")
        drift = 0
        for c in cats:
            a, b = top(then, c), top(now, c)
            flags = []
            if a != b:
                flags.append("DRIFT"); drift += 1
                if b == modal[c]:
                    flags.append("->modal")
                elif a == modal[c]:
                    flags.append("<-modal")
            print(f"{c:18}{modal[c]:14}{a:14}{b:14}  {' '.join(flags)}")
        print(f"\n{label}: modal answer moved in {drift}/{len(cats)} categories since {then_date}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["--score"]:
        report(json.loads(Path(args[1]).read_text()))
        sys.exit()
    want = set(args)
    models = [m for m in ROSTER if m["label"] in want]
    missing = want - {m["label"] for m in models}
    assert not missing, f"not in spec/models.json: {sorted(missing)}"
    out = HERE / "probes" / f"recheck_{date.today().isoformat()}.json"
    prior = json.loads(out.read_text()) if out.exists() else None
    # probe_lib applies `extra` to a whole call, so pinned models (spec/models.json "provider") run separately
    replies = {}
    for pin in sorted({m.get("provider") for m in models}, key=str):
        group = [m for m in models if m.get("provider") == pin]
        extra = {"provider": {"order": [pin], "allow_fallbacks": False}} if pin else None
        tmp = HERE / "probes" / "_recheck_tmp.json"
        replies.update(run_battery(PROMPTS, group, 8, tmp, extra=extra))
        tmp.unlink()
    if prior:
        prior["replies"].update(replies)
        probe = prior
    else:
        probe = {"runs": 8, "prompts": PROMPTS, "replies": replies, "run_date": date.today().isoformat(),
                 "note": "same-day chat re-snapshot (n=8) of transcript models: serving drift check"}
    out.write_text(json.dumps(probe, indent=1) + "\n")
    print(f"-> {out}", flush=True)
    report(probe)
