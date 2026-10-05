"""probe_recommend.py — does the brand a model names in the census match the brand it recommends?

transcripts-brands-recommend-free/ holds one turn, "Can you recommend a soda brand?", for the 41 brand categories (spec/
stimulus_brands_recommend.json, 4 runs, reasoning off where the endpoint allows it). A reply is scored by its first-
mentioned brand among the Name and Choose batteries' answers (probe_clamp.patterns: whole-word regex with brands.py aliases; answers
that repeat a word of the question are dropped). Compared
with the brand battery (Name, brands_all) and brand Choose (choose_brands_all):

  per model: the share of categories where the model's top recommended brand equals its own top Name brand / Choose brand
  per category: the panel's recommend consensus and its share, against the Name and Choose consensus

    ../../.venv/bin/python probe_recommend.py      # -> probes/recommend.json
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from analyze import answers                      # noqa: E402
from probe_clamp import mentions, patterns        # noqa: E402


def top(xs):
    return Counter(xs).most_common(1)[0][0] if xs else None


def main():
    name, choose = answers(HERE, "brands_all"), answers(HERE, "choose_brands_all")
    pool = {}                                    # brands known from Name and Choose, so quality picks (Chick-fil-A) are found
    for src in (name, choose):
        for m, cats in src.items():
            for c, xs in cats.items():
                pool.setdefault(c, Counter()).update(xs)
    # answers that repeat a word of the question ("assistant" for "an AI assistant") are not brands
    asked = {sc["id"].removesuffix("__recommend"): sc["turns"][0].lower()
             for sc in json.loads((HERE / "spec" / "stimulus_brands_recommend.json").read_text())["scenes"]}
    pats = {c: patterns("brand_" + c, [a for a, k in p.items() if k >= 2 and not re.search(rf"\b{re.escape(a)}\b", asked.get(c, ""))])
            for c, p in pool.items()}
    rec, listed, n_replies = {}, 0, 0
    for f in sorted((HERE / "transcripts-brands-recommend-free").glob("*.json")):
        d = json.loads(f.read_text())
        for sid, s in d["scenes"].items():
            c = sid.removesuffix("__recommend")
            for r in s["runs"]:
                ms = mentions((r[0].get("reply") or "") if r else "", pats[c])
                if ms:
                    rec.setdefault(d["model"], {}).setdefault(c, []).append(ms[0])
                    n_replies += 1
                    listed += len(ms) > 1
    per_model = {}
    for m, cats in rec.items():
        cs = [c for c in cats if name.get(m, {}).get(c)]
        cc = [c for c in cats if choose.get(m, {}).get(c)]
        per_model[m] = {"categories": len(cs),
                        "rec_eq_name": round(sum(top(cats[c]) == top(name[m][c]) for c in cs) / len(cs), 3) if cs else None,
                        "rec_eq_choose": round(sum(top(cats[c]) == top(choose[m][c]) for c in cc) / len(cc), 3) if cc else None}
    per_cat = {}
    for c in pool:
        r = Counter(x for m in rec.values() for x in m.get(c, []))
        nm = Counter(x for m in name.values() for x in m.get(c, []))
        ch = Counter(x for m in choose.values() for x in m.get(c, []))
        if not r:
            continue
        share = lambda k: (k.most_common(1)[0][0], round(k.most_common(1)[0][1] / sum(k.values()), 3))
        per_cat[c] = {"recommend": share(r), "name": share(nm), "choose": share(ch) if ch else None,
                      "name_top_share_in_recommend": round(r[nm.most_common(1)[0][0]] / sum(r.values()), 3)}
    eqn = [v["rec_eq_name"] for v in per_model.values() if v["rec_eq_name"] is not None]
    eqc = [v["rec_eq_choose"] for v in per_model.values() if v["rec_eq_choose"] is not None]
    same = sum(v["recommend"][0] == v["name"][0] for v in per_cat.values())
    samec = sum(v["choose"] and v["recommend"][0] == v["choose"][0] for v in per_cat.values())
    print(f"{len(rec)} models, {n_replies} scored replies, {listed / n_replies:.0%} name more than one brand")
    print(f"per model: top recommended brand = own top Name brand in {sum(eqn) / len(eqn):.0%} of categories; "
          f"= own top Choose brand in {sum(eqc) / len(eqc):.0%}")
    print(f"per category: recommend consensus = Name consensus in {same}/{len(per_cat)}; = Choose consensus in {samec}/{len(per_cat)}")
    print(f"\n{'category':16} {'recommend':>22} {'name':>22} {'choose':>22}")
    for c, v in sorted(per_cat.items(), key=lambda kv: kv[1]["recommend"][0] == kv[1]["name"][0]):
        fmt = lambda t: f"{t[0]} {t[1]:.0%}" if t else "-"
        print(f"{c:16} {fmt(v['recommend']):>22} {fmt(v['name']):>22} {fmt(v['choose']):>22}")
    (HERE / "probes" / "recommend.json").write_text(json.dumps(
        {"models": len(rec), "replies": n_replies, "multi_brand_share": round(listed / n_replies, 3),
         "rec_eq_name_mean": round(sum(eqn) / len(eqn), 3), "rec_eq_choose_mean": round(sum(eqc) / len(eqc), 3),
         "per_category": per_cat, "per_model": per_model}, indent=1, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
