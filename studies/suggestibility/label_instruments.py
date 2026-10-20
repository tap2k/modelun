"""label_instruments.py — the labeling items for probe_contested_unclamped.py, served by harness/viewer/label_server.py.

    python studies/suggestibility/label_instruments.py [--full]     # writes <run>/items.jsonl and <run>/guide.txt
    python harness/viewer/label_server.py --items studies/suggestibility/probes/contested_instruments/pilot/items_queue.jsonl \\
        --out studies/suggestibility/probes/contested_instruments/pilot --labeler human/Tap \\
        --criterion position --criterion-version v2 --values affirm,reject,hedge,refuse,none \\
        --guide studies/suggestibility/probes/contested_instruments/pilot/guide.txt
    open http://localhost:8010/label.html

One item per reply, in a fixed shuffled order; a rebuild keeps that order and appends new replies.
items_queue.jsonl is the human's queue: every reply without a pre-label. Contract B target: model, scene = <instrument>/<item>/<arm>_<side>,
run. The model, the instrument and its system prompt are shown (Tapan, 2026-10-19: unblinded, single coder). Short
replies (one word, one sentence) carry word_label()'s pre-label. The labels land in <run>/labels.human-Tap.jsonl,
which probe_contested_unclamped.py analyze reads. Inductive coding of the same replies is a separate study and goes
through harness/viewer/code_server.py.
"""
import sys, json, random
from pathlib import Path

STUDY = Path(__file__).resolve().parent
sys.path.insert(0, str(STUDY))
import probe_contested_unclamped as P   # noqa: E402
from labels import target_id, read_jsonl, latest   # noqa: E402  (harness/, on the path via the probe)

GUIDE = "guide_v2.txt"    # the frozen codebook, kept in the run dir; guide_v1.txt is the one the first labels saw
KEYS = "Keys: 1-5 for the values, Enter accepts the selected or pre-labeled value, arrows move. Every label is saved as made."


def build():
    q = {i: {"x": qx, "y": qy} for i, _, qx, qy in P.ITEMS}
    items = []
    for p in sorted(P.run_dir().glob("*/*.json")):
        d = json.loads(p.read_text())
        how = P.SCORE[d["instrument"]]
        if how == "first_word":       # scored by the opening word, as the clamp is; nothing to label
            continue
        for item, cell in d["cells"].items():
            for k, reps in cell.items():
                arm, side = k.rsplit("_", 1)
                for i, r in enumerate(reps):
                    if not r:
                        continue
                    pre = P.word_label(r["reply"], item, side) if how == "word_label" else None
                    items.append({"target": {"model": d["model"], "scene": f"{d['instrument']}/{item}/{k}", "run": i},
                                  "slug": d["slug"],     # for the judges' self-family exclusion; not shown
                                  "show": {"model": d["model"], "instrument": d["instrument"],
                                           "system": "system: " + d["system_prompt"] if d.get("system_prompt") else "no system prompt"},
                                  "prompt": P.user_text(d["instrument"], arm, *q[item][side]), "reply": r["reply"],
                                  "pre": pre, "pre_by": "word_label" if how == "word_label" else None})
    ids = {id(it): target_id(it["target"]) for it in items}
    tid = lambda it: ids[id(it)]
    # keep the order already being labeled; new replies go after it, shuffled among themselves
    out = P.run_dir() / "items.jsonl"
    order = {target_id(it["target"]): n for n, it in enumerate(read_jsonl(out))}
    new = [it for it in items if tid(it) not in order]
    random.Random(20261019 + len(order)).shuffle(new)
    items = sorted((it for it in items if tid(it) in order), key=lambda it: order[tid(it)]) + new
    out.write_text("".join(json.dumps(it, ensure_ascii=False) + "\n" for it in items))
    # the human queue: everything without a pre-label (pre-labeled short replies are scored by word_label)
    # labeled replies keep their place; the unlabeled are shuffled together, old and new, so labeling in order is a
    # random sample across instruments
    done = set(latest(read_jsonl(P.run_dir() / "labels.human-Tap.jsonl")))
    queue = [it for it in items if not it["pre"]]
    rest = [it for it in queue if tid(it) not in done]
    random.Random(20261019 + len(done)).shuffle(rest)
    # first, replies a codebook change may move (relabel_<version>.json, marked redo so the page asks for them again),
    # then targeted blind batches of a rare value (targeted_<version>.json), which a random sample has too few of
    # (docs/harness.md, labeling rules 8-9)
    redo = {i for f in P.run_dir().glob("relabel_*.json") for i in json.loads(f.read_text())}
    front = list(dict.fromkeys(i for f in sorted(P.run_dir().glob("relabel_*.json")) + sorted(P.run_dir().glob("targeted_*.json"))
                               for i in json.loads(f.read_text())))
    by = {tid(it): it for it in queue}
    for i in redo & set(by):
        by[i]["redo"] = True
    first = set(front)
    queue = ([by[i] for i in front if i in by] + [it for it in queue if tid(it) in done and tid(it) not in first]
             + [it for it in rest if tid(it) not in first])
    (P.run_dir() / "items_queue.jsonl").write_text("".join(json.dumps(it, ensure_ascii=False) + "\n" for it in queue))
    (P.run_dir() / "guide.txt").write_text((P.run_dir() / GUIDE).read_text() + "\n" + KEYS + "\n")
    print(f"wrote {out} ({len(items)} items, {len(new)} new, {sum(1 for it in items if it['pre'])} pre-labeled) "
          f"and items_queue.jsonl ({len(queue)} for the human), guide.txt")

if __name__ == "__main__":
    P.PILOT = "--full" not in sys.argv
    build()
