"""factors.py — the separate effects of the clamp, the verb and reasoning on what models answer.

Every contrast compares a baseline condition A with a changed condition B over the same models and categories:
  * the clamp:     clamped ("Reply with one word only" / "the name only") vs free, same verb
  * the verb:      Name vs Choose / pick / Recommend, same clamp
  * reasoning:     the 25 hybrids as served vs with reasoning off, same question
Two measures per contrast, each with a noise floor from splitting A's own runs into two random halves:
  * consensus moved: share of categories where the field's most common answer under B is not the one under A
  * own answer kept: share of a model's B answers that equal its own most common A answer (answers naming nothing
    are left out; their share is reported as "no answer")
Free replies are reduced by first mention (free Name, Recommend) or by the brand the reply commits to (free
Choose, picks), as brand_ladder.py does; census and expanded free replies by first mention of the panel's answers.
Zero API calls. Writes probes/factors.json.

    ../../.venv/bin/python factors.py
"""
import json
import random
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import brand_ladder as B                                     # noqa: E402
from analyze import answers, load                            # noqa: E402
import probe_clamp                                           # noqa: E402

NONE = B.NO_PICK
HYB = json.loads((HERE / "spec/runs.json").read_text())["hybrids"]
DIRS = {e["id"]: e["dir"] for e in json.loads((HERE / "spec/runs.json").read_text())["runs"]}


def top(pool):
    pool = Counter({k: v for k, v in pool.items() if k != NONE})
    return pool.most_common(1)[0][0] if pool else None


def modal(xs):
    return top(Counter(xs))


def compare(A, Bc, models=None, draws=20):
    """The two measures and their split-half floors, over the models and categories both conditions hold."""
    ms = [m for m in (models or A) if m in A and m in Bc]
    cats = sorted({c for m in ms for c in A[m]} & {c for m in ms for c in Bc[m]})
    moved = sum(top(Counter(x for m in ms for x in A[m].get(c, []))) != top(Counter(x for m in ms for x in Bc[m].get(c, [])))
                for c in cats)
    kept, nb, na = [], 0, 0
    for m in ms:
        for c in cats:
            d, ys = modal(A[m].get(c, [])), Bc[m].get(c, [])
            nb += len(ys); na += sum(y == NONE for y in ys)
            ys = [y for y in ys if y != NONE]
            if d and ys:
                kept.append(sum(y == d for y in ys) / len(ys))
    fm, fk = [], []
    for _ in range(draws):
        h1, h2 = {}, {}
        for m in ms:
            for c in cats:
                xs = list(A[m].get(c, []))
                random.shuffle(xs)
                h1.setdefault(m, {})[c], h2.setdefault(m, {})[c] = xs[:len(xs) // 2], xs[len(xs) // 2:]
        fm.append(sum(top(Counter(x for m in ms for x in h1[m][c])) != top(Counter(x for m in ms for x in h2[m][c]))
                      for c in cats))
        k = []
        for m in ms:
            for c in cats:
                d, ys = modal(h1[m][c]), [y for y in h2[m][c] if y != NONE]
                if d and ys:
                    k.append(sum(y == d for y in ys) / len(ys))
        fk.append(sum(k) / len(k))
    return {"models": len(ms), "categories": len(cats), "consensus_moved": moved / len(cats),
            "floor_moved": sum(fm) / draws / len(cats), "own_kept": sum(kept) / len(kept),
            "floor_kept": sum(fk) / draws, "no_answer_B": na / nb if nb else 0.0}


def free_general():
    """Census and expanded free Name ("Name a fruit."): first mention of an answer from the clamped panel's pool."""
    pool = {}
    for b in ("census8", "expanded"):
        for cats in answers(HERE, b).values():
            for c, xs in cats.items():
                pool.setdefault(c, Counter()).update(xs)
    _, free = probe_clamp.load()
    out = {}
    for c, by in free.items():
        if c.startswith("brand_") or c not in pool:
            continue
        pats = probe_clamp.patterns(c, [a for a, k in pool[c].items() if k >= 2])
        for m, replies in by.items():
            out.setdefault(m, {})[c] = [(probe_clamp.mentions(r, pats) or [NONE])[0] for r in replies]
    return out


def off_brand(level):
    """A brand level's reasoning-off arm (the hybrids), scored as brand_ladder scores the level."""
    ids = {"name": ("brands-off", "brands-ext-off", "brands-ext2-off"),
           "choose": ("brands-choose-off", "brands-ext-choose-off", "brands-ext2-choose-off"),
           "pick1_clamp": ("brands-pick1-clamp-off", "brands-ext2-pick1-clamp-off"),
           "recommend_clamp": ("brands-recommend-clamp-off", "brands-ext2-recommend-clamp-off"),
           "free_choose": ("brands-choose-free-off", "brands-ext2-choose-free-off"),
           "pick1": ("brands-pick1-free-off", "brands-ext2-pick1-free-off"),
           "recommend": ("brands-recommend-free-off", "brands-ext2-recommend-free-off"),
           "pick2": ("brands-pick2-free-off", "brands-ext2-pick2-free-off")}[level]
    if level in ("name", "choose", "pick1_clamp", "recommend_clamp"):
        return load(HERE, "brands", paths=[p for i in ids for p in sorted((HERE / DIRS[i]).glob("*.json"))])
    spec = {"free_choose": ("__choosefree", 0, "open"), "pick1": ("__youpick", 0, "open"),
            "recommend": ("__recommend", 0, "first"), "pick2": ("__pick", 1, "open")}[level]
    return B.load(list(ids), *spec)


def main():
    random.seed(0)
    lv = B.levels()
    g_name = {**{m: dict(c) for m, c in answers(HERE, "census8").items()}}
    for m, cats in answers(HERE, "expanded").items():
        g_name.setdefault(m, {}).update(cats)
    g_choose = answers(HERE, "choose")
    g_free = free_general()
    census = set(answers(HERE, "census8")[next(iter(answers(HERE, "census8")))])
    split = lambda d, keep: {m: {c: x for c, x in cats.items() if (c in census) == keep} for m, cats in d.items()}

    rows = []
    def add(factor, battery, contrast, A, Bc, models=None):
        r = compare(A, Bc, models)
        rows.append({"factor": factor, "battery": battery, "contrast": contrast, **r})

    # the clamp: clamped -> free, same verb
    add("clamp", "census", "Name", split(g_name, True), split(g_free, True))
    add("clamp", "expanded", "Name", split(g_name, False), split(g_free, False))
    for verb, a, b in (("Name", "name", "free_name"), ("Choose", "choose", "free_choose"),
                       ("pick", "pick1_clamp", "pick1"), ("Recommend", "recommend_clamp", "recommend")):
        add("clamp", "brands", verb, lv[a], lv[b])
    # the verb: Name -> other verb, clamped; and free Name -> other verb, free
    add("verb", "census", "Name -> Choose", split(g_name, True), split(g_choose, True))
    add("verb", "expanded", "Name -> Choose", split(g_name, False), split(g_choose, False))
    for verb, b in (("Choose", "choose"), ("pick", "pick1_clamp"), ("Recommend", "recommend_clamp")):
        add("verb", "brands", "Name -> " + verb, lv["name"], lv[b])
    for verb, b in (("Choose", "free_choose"), ("pick", "pick1"), ("Recommend", "recommend"), ("two-turn pick", "pick2")):
        add("verb (free)", "brands", "free Name -> " + verb, lv["free_name"], lv[b])
    # reasoning: the hybrids as served -> reasoning off
    c_off = load(HERE, "census", paths=sorted((HERE / "transcripts-off").glob("*.json")))
    e_off = load(HERE, "expanded", paths=sorted((HERE / "transcripts-expanded-off").glob("*.json")))
    add("reasoning", "census", "Name", split(g_name, True), {m: c_off[m] for m in c_off}, HYB)
    add("reasoning", "expanded", "Name", split(g_name, False), {m: e_off[m] for m in e_off}, HYB)
    for lab, level in (("Name", "name"), ("Choose", "choose"), ("pick", "pick1_clamp"), ("Recommend", "recommend_clamp"),
                       ("free Choose", "free_choose"), ("free pick", "pick1"), ("free Recommend", "recommend"),
                       ("two-turn pick", "pick2")):
        add("reasoning", "brands", lab, lv[level], off_brand(level), HYB)

    (HERE / "probes" / "factors.json").write_text(json.dumps(rows, indent=1) + "\n")
    print(f"{'factor':12} {'battery':9} {'contrast':30} {'models':>6} {'cats':>4}  {'consensus moved':>17}  {'own answer kept':>17}  {'no answer':>9}")
    for r in rows:
        print(f"{r['factor']:12} {r['battery']:9} {r['contrast']:30} {r['models']:6} {r['categories']:4}  "
              f"{r['consensus_moved']:6.0%} (floor {r['floor_moved']:3.0%})  {r['own_kept']:6.0%} (floor {r['floor_kept']:3.0%})  {r['no_answer_B']:8.0%}")


if __name__ == "__main__":
    main()
