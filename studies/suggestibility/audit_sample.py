"""audit_sample.py — a stratified, blind sample for hand-auditing analyze.classify.

classify() reads the leading token: a leading Yes-family word is affirm, a leading No-family word is
reject, anything else is a hedge. Reviewers asked whether that misreads replies like "Absolutely not"
(affirm by rule), "Not enough information" (reject by rule) or "I agree" (hedge by rule). A bare
"Yes"/"No" (optionally with a period) cannot be misread, so the sample draws only from the rest and
reports the bare share, which scales the audit's error rate to the whole corpus.

Pool: the main transcripts' plant and ask arms, probes/righteffect (tag arm) and probes/contested
(all arms). Strata: classifier label (affirm / reject / hedge) x source (core / contested), equal
numbers per stratum, seeded. Writes, under audit/:

  sheet.csv   id, prompt, reply, human_label (blank)  -> give this to the coder; no classifier labels
  key.csv     id, model, source, arm, classifier_label

The coder fills human_label with affirm / reject / hedge by the same meaning: does the reply endorse
the claim, decline to endorse it, or neither. Score with `python audit_sample.py score`.

    python studies/suggestibility/audit_sample.py [--per-stratum 25]
    python studies/suggestibility/audit_sample.py score --key ~/Desktop/projects/modelUN/suggestibility/audit-key.csv

The key stays out of the repo until labelling is done: move it to the private planning folder after drawing
the sample (audit/key.csv is gitignored), and pass its path to score with --key.
"""
import csv, json, random, re, sys
from pathlib import Path
from analyze import classify
from probe_righteffect import ITEMS as CORE_ITEMS, tag_prompt
import probe_contested

STUDY = Path(__file__).resolve().parent
OUT = STUDY / "audit"
BARE = re.compile(r"^\W*(yes|no)\W*$", re.I)


def pool():
    items = []
    for p in sorted((STUDY / "transcripts").glob("*.json")):
        d = json.loads(p.read_text())
        for sid, sc in d["scenes"].items():
            for run in sc["runs"]:
                if run and run[0].get("reply"):
                    items.append((d["model"], "core", sid.split("__")[-1], run[0].get("u", ""), run[0]["reply"]))
    core = {i: (d, x, y) for i, d, x, y in CORE_ITEMS}
    for p in sorted((STUDY / "probes" / "righteffect").glob("*.json")):
        d = json.loads(p.read_text())
        for item, c in d["tag"].items():
            dec, x, y = core[item]
            for side, o in (("x", x), ("y", y)):
                for r in c.get(side, []):
                    if r:
                        items.append((d["model"], "core", "tag", tag_prompt(dec, o), r))
    cont = {i: (qx, qy) for i, _, qx, qy in probe_contested.ITEMS}
    for p in sorted((STUDY / "probes" / "contested").glob("*.json")):
        d = json.loads(p.read_text())
        for item, c in d["cells"].items():
            for key, reps in c.items():
                arm, side = key.rsplit("_", 1)
                q, cl = cont[item][0 if side == "x" else 1]
                for r in reps:
                    if r:
                        items.append((d["model"], "contested", arm, probe_contested.prompt(arm, q, cl), r))
    return items


def sample(per):
    rows = pool()
    bare = sum(1 for r in rows if BARE.match(r[4].strip()))
    rest = [r for r in rows if not BARE.match(r[4].strip()) and classify(r[4]) is not None]
    rng = random.Random(7)
    strata = {}
    for r in rest:
        strata.setdefault((classify(r[4]), r[1]), []).append(r)
    picked = []
    for key in sorted(strata):
        picked += [(key, r) for r in rng.sample(strata[key], min(per, len(strata[key])))]
    rng.shuffle(picked)
    OUT.mkdir(exist_ok=True)
    with open(OUT / "sheet.csv", "w", newline="") as fs, open(OUT / "key.csv", "w", newline="") as fk:
        ws, wk = csv.writer(fs), csv.writer(fk)
        ws.writerow(["id", "prompt", "reply", "human_label"]); wk.writerow(["id", "model", "source", "arm", "classifier_label"])
        for i, ((label, src), (m, _, arm, prompt, reply)) in enumerate(picked, 1):
            ws.writerow([i, prompt, reply[:1500], ""]); wk.writerow([i, m, src, arm, label])
    meta = {"pool": len(rows), "bare_yes_no": bare, "bare_share": bare / len(rows), "non_bare": len(rest),
            "strata": {f"{k[0]}/{k[1]}": len(v) for k, v in strata.items()}, "sampled": len(picked)}
    (OUT / "meta.json").write_text(json.dumps(meta, indent=1))
    print(json.dumps(meta, indent=1))
    print(f"-> audit/sheet.csv ({len(picked)} rows, blind) and audit/key.csv")


def score():
    k = Path(sys.argv[sys.argv.index("--key") + 1]).expanduser() if "--key" in sys.argv else OUT / "key.csv"
    key = {r["id"]: r for r in csv.DictReader(open(k))}
    sheet = [r for r in csv.DictReader(open(OUT / "sheet.csv")) if r["human_label"].strip()]
    meta = json.loads((OUT / "meta.json").read_text())
    agree = sum(1 for r in sheet if r["human_label"].strip().lower() == key[r["id"]]["classifier_label"])
    by = {}
    for r in sheet:
        k = key[r["id"]]["classifier_label"]
        by.setdefault(k, [0, 0]); by[k][1] += 1
        by[k][0] += r["human_label"].strip().lower() == k
    acc = agree / len(sheet) if sheet else None
    print(f"labeled {len(sheet)}; agreement {acc:.1%} on non-bare replies")
    for k, (a, n) in sorted(by.items()):
        print(f"  classifier said {k}: {a}/{n} confirmed")
    if acc is not None:
        print(f"corpus-level accuracy (bare replies counted as correct): "
              f"{meta['bare_share'] + (1 - meta['bare_share']) * acc:.1%}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "score":
        score()
    else:
        per = int(sys.argv[sys.argv.index("--per-stratum") + 1]) if "--per-stratum" in sys.argv else 25
        sample(per)
