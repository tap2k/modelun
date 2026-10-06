"""
probe_clamp.py — does the one-word clamp MANUFACTURE the convergence, or just extract it?

Each category is asked clamped ("... Reply with one word only.", or "the name only" for brands) and free
(the same question, bare). The clamped answers give the field's pool of answers for the category and its modal
answer. A free reply in prose can name several candidates ("blue, red or green"), so it is scored three ways
against that pool, by whole-word regex (plurals and, for brands, brands.py aliases included):

  presence   the modal answer appears anywhere in the reply (the original measure; an upper bound when replies list)
  first      the earliest-mentioned pool answer is the modal one (the prose analogue of the one-word choice; main)
  single     the reply names exactly one pool answer (reported, with the modal share among those replies)

If the clamped modal share ≈ the free first-mention modal share, the convergence belongs to what models choose,
not to how they are asked. Per model: the share of free replies whose first mention avoids the modal answer,
rank-correlated with the model's clamped census surprisal (analysis.json).

Data: transcripts-clamp/ (spec/clamp.json, 10 census categories), transcripts-clamp-ext/ (spec/clamp_ext.json,
20 expanded categories across the convergence range plus 5 brand categories) and transcripts-clamp-free/
(spec/clamp_free_all.json: the free question for every other census, expanded and brand category, 98). Where a
category has no clamped re-ask, its pool is the battery's own one-word answers (analyze.answers: census, expanded,
brands; 8 samples per model). Scene id = <category>_<clamp|free>, split on the last underscore; brand scenes start
with brand_.

    ../../.venv/bin/python probe_clamp.py      # -> probes/clamp_rank.json
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from brands import ALIASES, brand_name  # noqa: E402

DIRS = ["transcripts-clamp", "transcripts-clamp-ext", "transcripts-clamp-free", "transcripts-clamp-free-brands-ext"]
WORD = re.compile(r'^[a-z\-]+$|^\d+$')
PUNCT = re.compile(r'[*_`#>\[\]().,!?"\':;]')


def norm(ans):
    """One-word extraction, as in the census (last valid token)."""
    if not ans:
        return None
    a = PUNCT.sub(' ', ans.strip().lower())
    words = [w for w in a.split() if WORD.match(w) and (len(w) > 1 or w.isdigit())]
    return words[-1] if words else None


def patterns(cat, pool):
    """Answer -> compiled whole-word regex, with a plural for words and the alias spellings for brands. An apostrophe
    matches a curly one (McDonald’s is mcdonald's)."""
    q = lambda f: re.escape(f).replace("'", "['\u2018\u2019]")
    out = {}
    for a in pool:
        if cat.startswith("brand_"):
            forms = [a] + [k for k, v in ALIASES.items() if v == a]
            out[a] = re.compile(r"\b(" + "|".join(q(f) for f in forms) + r")\b", re.I)
        else:
            out[a] = re.compile(rf"\b{q(a)}s?\b", re.I)
    return out


def mentions(reply, pats):
    """Pool answers named in a reply, in order of first appearance; at the same position the longer match wins
    ("Amazon Web Services" is aws, not amazon), and an answer found only inside a longer one is dropped."""
    hits = sorted(((m.start(), -len(m.group(0)), a, m.end()) for a, p in pats.items() if (m := p.search(reply))))
    out, covered = [], -1
    for start, _, a, end in hits:
        if start < covered:
            continue
        out.append(a)
        covered = end
    return out


def load(dirs=DIRS):
    clamp, free = {}, {}
    for d in dirs:
        for p in sorted((HERE / d).glob("*.json")):
            dd = json.loads(p.read_text())
            for sid, s in dd["scenes"].items():
                cat, cond = sid.rsplit("_", 1)
                for r in s["runs"]:
                    reply = (r[0].get("reply") or "") if r else ""
                    if not reply.strip():
                        continue
                    if cond == "clamp":
                        t = brand_name(reply) if cat.startswith("brand_") else norm(reply)
                        if t:
                            clamp.setdefault(cat, {}).setdefault(dd["model"], []).append(t)
                    else:
                        free.setdefault(cat, {}).setdefault(dd["model"], []).append(reply)
    return clamp, free


def battery_pool(clamp, free):
    """Categories with free replies but no clamped re-ask take the battery's one-word answers as their pool. Brand
    categories use the 41-category brand battery, which like the free replies holds every model as served."""
    from analyze import answers
    need = [c for c in free if c not in clamp]
    if not need:
        return
    bats = {b: answers(HERE, b) for b in ("census", "expanded", "brands_all")}
    for c in need:
        bat, key = ("brands_all", c[len("brand_"):]) if c.startswith("brand_") else (None, c)
        sources = [bats[bat]] if bat else [bats["census"], bats["expanded"]]
        for ans in sources:
            for m, cats in ans.items():
                if cats.get(key):
                    clamp.setdefault(c, {}).setdefault(m, []).extend(cats[key])


def main():
    clamp, free = load()
    battery_pool(clamp, free)
    cats = [c for c in clamp if c in free]
    pool = {c: Counter(x for xs in clamp[c].values() for x in xs) for c in cats}
    modal = {c: pool[c].most_common(1)[0][0] for c in cats}
    cats.sort(key=lambda c: -pool[c][modal[c]] / sum(pool[c].values()))
    per_cat, first_by_model = {}, {}
    print(f"\n{'category':24} {'modal':>14}  clamped  presence  first  single(share)  n")
    for c in cats:
        pats = patterns(c, [a for a, k in pool[c].items() if k >= 2 or a == modal[c]])
        n = pres = first = single = single_modal = 0
        for m, replies in free[c].items():
            for r in replies:
                ms = mentions(r, pats)
                n += 1
                pres += modal[c] in ms
                if ms:
                    first += ms[0] == modal[c]
                    first_by_model.setdefault(m, []).append(ms[0] != modal[c])
                if len(ms) == 1:
                    single += 1
                    single_modal += ms[0] == modal[c]
        share = pool[c][modal[c]] / sum(pool[c].values())
        per_cat[c] = {"modal": modal[c], "clamped_share": round(share, 3), "free_presence": round(pres / n, 3),
                      "free_first": round(first / n, 3), "single_reply_share": round(single / n, 3),
                      "modal_among_single": round(single_modal / single, 3) if single else None, "n_free": n}
        print(f"{c:24} {modal[c]:>14}  {share:6.0%}  {pres / n:7.0%}  {first / n:5.0%}  "
              f"{single / n:5.0%} ({(single_modal / single if single else 0):4.0%})  {n}")

    census = json.loads((HERE / "analysis.json").read_text())["per_model"]
    ms = sorted(m for m in first_by_model if m in census and len(first_by_model[m]) >= 20)
    x = np.array([census[m]["surprisal"] for m in ms])
    y = np.array([np.mean(first_by_model[m]) for m in ms])
    rx, ry = np.argsort(np.argsort(x)), np.argsort(np.argsort(y))
    rho = float(np.corrcoef(rx, ry)[0, 1])
    rng = np.random.default_rng(7)
    pval = float(np.mean([abs(np.corrcoef(rx, rng.permutation(ry))[0, 1]) >= abs(rho) for _ in range(20000)]))
    print(f"\nper model: census surprisal vs free first-mention avoiding the modal answer ({len(cats)} categories), "
          f"n={len(ms)}: spearman {rho:.2f} (perm p={pval:.4f})")
    (HERE / "probes" / "clamp_rank.json").write_text(json.dumps(
        {"n": len(ms), "categories": len(cats), "spearman_first_avoid": rho, "perm_p": pval, "per_category": per_cat,
         "per_model": {m: {"surprisal": census[m]["surprisal"], "free_first_avoid": round(float(np.mean(first_by_model[m])), 3)}
                       for m in ms}}, indent=1) + "\n")


if __name__ == "__main__":
    main()
