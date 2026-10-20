#!/usr/bin/env python3
"""Agreement between LLM judges and a human on a closed-labeling items file, and the files that follow from it.

Reads the Contract B files label_llm.py and label_server.py write in one directory (labels.<judge>.jsonl,
labels.human-<name>.jsonl, labels.human-<name>.adjudication.jsonl). Each judge's latest prompt_version is used unless
--prompt-version names one. A judge's calls on its own family are left out of the majority (docs/harness.md,
AGENTS.md): the family is the vendor of the subject's slug (the items file's `slug`) against the judge's. Of the rest,
a value held by more than half is the majority; anything else is a split. Reports each judge and the majority against
the human's blind labels: agreement, Cohen's kappa and n, overall and per group (the first part of target.scene), and
the confusion table.

    python harness/label_agree.py --dir <dir> --items <items.jsonl> --human human/Tap \\
        [--half dev|test] [--ids <ids.json>] [--blind-before <iso time>] [--exclude <examples.jsonl>] \\
        [--adjudicate <out.jsonl>] [--prelabel <items_queue.jsonl> --prelabel-out <out.jsonl>] [--resolved <out.jsonl>]

--adjudicate writes the items to settle: human-labeled targets where the majority differs from the human or splits.
Each shows the judges' labels and the human's blind label (as `pre`); serve it with label_server.py --pass
adjudication. --prelabel rewrites a queue with the majority as each unlabeled item's pre-label, for labeling after
the judges are licensed (the row records the pre-label and `pre_by`). --resolved writes every target's label for
analysis: the adjudicated one, else the human's, else the majority, with its source.
"""
import json, hashlib, argparse, collections
from pathlib import Path
from labels import target_id, read_jsonl, latest, vendor

ap = argparse.ArgumentParser()
ap.add_argument("--dir", required=True)
ap.add_argument("--items", required=True)
ap.add_argument("--human", required=True, help="the human labeler, e.g. human/Tap")
ap.add_argument("--ids", default=None, help="JSON list of target ids to score")
ap.add_argument("--half", choices=["dev", "test"], default=None,
                help="score one half of the blind labels, split by a hash of the target (docs/harness.md, labeling rule 10)")
ap.add_argument("--blind-before", default=None, help="ISO time: only human rows labeled before it (before judges were shown)")
ap.add_argument("--exclude", default=None, help="worked examples (JSONL with target), left out of the scoring")
ap.add_argument("--prompt-version", action="append", default=[], help="judge=version; default each judge's latest")
ap.add_argument("--adjudicate", default=None)
ap.add_argument("--prelabel", default=None)
ap.add_argument("--prelabel-out", default=None)
ap.add_argument("--resolved", default=None)
args = ap.parse_args()

D = Path(args.dir)
ITEMS = {target_id(it["target"]): it for it in read_jsonl(args.items)}
stem = args.human.replace("/", "-")
human = latest(read_jsonl(D / f"labels.{stem}.jsonl"))
adjudicated = latest(read_jsonl(D / f"labels.{stem}.adjudication.jsonl"))

pinned = dict(kv.split("=") for kv in args.prompt_version)
judges = {}      # judge slug -> {target id: its latest row under the prompt version in use}
for f in sorted(D.glob("labels.*.jsonl")):
    rows = read_jsonl(f)
    if not rows or rows[0]["labeler"].startswith("human/"):
        continue
    j = rows[0]["labeler"]
    v = pinned.get(j, rows[-1].get("prompt_version"))
    judges[j] = latest(r for r in rows if r.get("prompt_version") == v)
    print(f"{j}: prompt {v}, {len(judges[j])} labels")


def majority(k):
    fam = vendor(ITEMS[k].get("slug", "")) if k in ITEMS else None
    votes = [lab[k]["value"] for j, lab in judges.items() if k in lab and lab[k]["value"] and vendor(j) != fam]
    if not votes:
        return None
    v, n = collections.Counter(votes).most_common(1)[0]
    return v if n * 2 > len(votes) else "split"


MAJ = {k: majority(k) for k in set().union(*judges.values())} if judges else {}
judges_str = lambda k: ", ".join(f"{j.split('/')[-1]}={lab[k]['value']}" for j, lab in judges.items() if k in lab)

ids = set(json.loads(Path(args.ids).read_text())) if args.ids else set(human)
if args.exclude:
    ids -= {target_id(r["target"]) for r in read_jsonl(args.exclude)}
if args.half:
    ids = {k for k in ids if int(hashlib.sha256(k.encode()).hexdigest(), 16) % 2 == (args.half == "test")}
if args.blind_before:
    ids = {k for k in ids if (human[k].get("ts") or "") < args.blind_before}
ids &= set(human)
group = lambda k: json.loads(k)["scene"].split("/")[0]


def kappa(pairs):
    n = len(pairs)
    if not n:
        return None, None
    po = sum(a == b for a, b in pairs) / n
    ca, cb = collections.Counter(a for a, _ in pairs), collections.Counter(b for _, b in pairs)
    pe = sum(ca[v] * cb[v] for v in ca) / n / n
    return po, (po - pe) / (1 - pe) if pe < 1 else None


def report(name, get):
    pairs = {k: (human[k]["value"], get(k)) for k in ids if get(k)}
    po, k = kappa(list(pairs.values()))
    if po is None:
        return
    print(f"\n{name}: agreement {po:.0%}, kappa {k:.2f}, n {len(pairs)}")
    by = collections.defaultdict(list)
    for key, p in pairs.items():
        by[group(key)].append(p)
    for g, ps in sorted(by.items()):
        po, kk = kappa(ps)
        print(f"  {g:22s} {po:4.0%}  kappa {kk if kk is None else round(kk, 2)}  n {len(ps)}")
    conf = collections.Counter(pairs.values())
    vals = sorted({v for p in pairs.values() for v in p})
    print("  human \\ judge " + " ".join(f"{v:>7s}" for v in vals))
    for a in vals:
        print(f"  {a:14s} " + " ".join(f"{conf[(a, b)]:7d}" for b in vals))


def write(path, rows):
    Path(path).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))


for j, lab in judges.items():
    report(j, lambda k, lab=lab: lab[k]["value"] if k in lab else None)
report("majority (self-family excluded)", MAJ.get)

if args.adjudicate:
    out = []
    for k in sorted(set(human) & set(ITEMS)):
        m = MAJ.get(k)
        if m and m != human[k]["value"]:
            it = dict(ITEMS[k])
            it["show"] = {**it.get("show", {}), "judges": judges_str(k), "majority": m, "your label": human[k]["value"]}
            it["pre"], it["pre_by"] = human[k]["value"], args.human
            out.append(it)
    write(args.adjudicate, out)
    print(f"\n{len(out)} to adjudicate -> {args.adjudicate}")

if args.prelabel:
    q = read_jsonl(args.prelabel)
    for it in q:
        k = target_id(it["target"])
        if k not in human and not it.get("pre"):
            m = MAJ.get(k)
            it["pre"] = m if m and m != "split" else None
            it["pre_by"] = "judges: " + ", ".join(f"{j}@{lab[k]['prompt_version']}" for j, lab in judges.items() if k in lab)
            it["show"] = {**it.get("show", {}), "judges": judges_str(k)}
    write(args.prelabel_out, q)
    print(f"pre-labeled queue -> {args.prelabel_out}")

if args.resolved:
    out = []
    for k in sorted(set(adjudicated) | set(human) | set(MAJ)):
        src, r = next(((s, x[k]) for s, x in (("adjudication", adjudicated), ("human", human)) if k in x), (None, None))
        v = r["value"] if r else (MAJ[k] if MAJ.get(k) != "split" else None)
        if v:
            out.append({"target": json.loads(k), "value": v, "source": src or "majority"})
    write(args.resolved, out)
    print(f"{len(out)} resolved labels -> {args.resolved}")
