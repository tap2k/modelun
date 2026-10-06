"""stage_ladder.py — the open training-stage pipelines (OLMo 3 7B, Tulu 3 8B, OLMo 3.1 32B, Nemotron 3.5 Lightning)
scored against the API panel, for the census and brand papers' training-stage sections. Zero API calls; reads
probes/verb_ladder_<pipeline>/ (written by probe_verb_ladder.py).

  verbs   Name vs Choose by stage, on the 96 census and expanded categories. Over the categories where the panel's
          Name and Choose consensus differ: the share of the stage's answers giving the panel's Name and its Choose
          answer. Also: in how many categories the stage's own Name and Choose modes differ.
  brands  The brand ladder by stage on the 41 brand categories, per level (Name, free Name, Choose, free Recommend):
          how often the stage's most frequent brand is the panel's consensus at that level (as served), and how
          often it differs from the stage's own Name brand. Free replies are read by first mention.
  dolci   Does OLMo's post-training data teach the pick brand? For brand categories where the panel's two-turn pick
          differs from its Name brand, Dolci SFT conversations whose first user turn asks for a recommendation in
          that category, by the brand the assistant mentions first (Name, pick, other, none); and the same for
          Dolci DPO chosen against rejected. Reads the external drive's copies at the revisions
          probe_olmo_data.py pins.

The two-turn pick by stage is stage_pick.py.

    ../../.venv/bin/python stage_ladder.py verbs|brands|dolci   -> probes/stage_<verbs|brands|dolci>.json
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from analyze import analyze, answers, load  # noqa: E402

PIPELINES = (("olmo3-7b", "base sft dpo rl"), ("tulu3-8b", "base sft dpo rl"),
             ("olmo31-32b", "base sft dpo rl"), ("nemotron35-lightning", "base final"))
DRIVE = Path("/Volumes/My Passport/models")


def stage_files(pipe, d, st):
    return sorted((HERE / "probes" / f"verb_ladder_{pipe}" / d).glob(f"{pipe}-{st}*.json"))


def clamped(pipe, dirs, st, battery):
    out = {}
    for d, bat in dirs:
        for p in stage_files(pipe, d, st):
            for cats in load(HERE, bat or battery, paths=[p]).values():
                out.update(cats)
    return out


def verbs():
    pn = analyze(HERE, "combined", ans=answers(HERE, "combined"))["per_category"]
    pc = analyze(HERE, "choose", ans=answers(HERE, "choose"))["per_category"]
    diff = [c for c in pn if c in pc and pn[c]["modal"] != pc[c]["modal"]]
    files = {"name": [("stimulus", "census"), ("stimulus_expanded", "expanded")],
             "choose": [("stimulus_choose", "choose_census"), ("stimulus_expanded_choose", "choose_expanded")]}
    mode = lambda xs: Counter(xs).most_common(1)[0][0]
    res = {"categories_name_choose_differ": diff, "pipelines": {}}
    print(f"{len(diff)} of 96 categories where the API panel's Name and Choose consensus differ\n")
    for pipe, stages in PIPELINES:
        print(pipe)
        res["pipelines"][pipe] = {}
        for st in stages.split():
            a = {v: clamped(pipe, files[v], st, None) for v in ("name", "choose")}
            row, cells = {}, []
            for verb in ("name", "choose"):
                cs = [c for c in diff if a[verb].get(c)]
                if not cs:
                    cells.append(f"{verb}: -"); continue
                n = sum(len(a[verb][c]) for c in cs)
                hn = sum(x == pn[c]["modal"] for c in cs for x in a[verb][c]) / n
                hc = sum(x == pc[c]["modal"] for c in cs for x in a[verb][c]) / n
                row[verb] = {"panel_name": round(hn, 3), "panel_choose": round(hc, 3), "answers": n}
                cells.append(f"{verb}: panel-Name {hn:4.0%} panel-Choose {hc:4.0%}")
            both = [c for c in a["name"] if a["choose"].get(c) and a["name"][c]]
            row["own_modes_differ"] = [sum(mode(a["name"][c]) != mode(a["choose"][c]) for c in both), len(both)]
            res["pipelines"][pipe][st] = row
            print(f"  {st:6} {'   |   '.join(cells)}   |  own Name/Choose modal differs: "
                  f"{row['own_modes_differ'][0]}/{len(both)}")
        print()
    return res


def brands():
    import brand_ladder as B
    lv = B.levels()
    panel = {k: {c: B.top(cnt)[0] for c, cnt in B.agg(lv[k]).items()} for k in ("name", "free_name", "choose", "recommend")}
    mode = lambda xs: Counter(x for x in xs if x != B.NO_PICK).most_common(1)[0][0] if any(x != B.NO_PICK for x in xs) else None
    pool = B.pools()[2]

    def free(pipe, d, st, suffix, prefix=""):
        out = {}
        for p in stage_files(pipe, d, st):
            for sid, s in json.loads(p.read_text())["scenes"].items():
                c = sid.removesuffix(suffix).removeprefix(prefix)
                if c in pool:
                    out[c] = [B.first_mention(c, r[0].get("reply")) for r in s["runs"] if r and r[0].get("reply")]
        return out

    res = {"pipelines": {}}
    for pipe, stages in PIPELINES:
        print(pipe)
        res["pipelines"][pipe] = {}
        for st in stages.split():
            a = {"name": clamped(pipe, (("stimulus_brands", None), ("stimulus_brands_ext", None)), st, "brands"),
                 "free_name": free(pipe, "free_brands", st, "_free", "brand_"),
                 "choose": clamped(pipe, (("stimulus_brands_choose", None), ("stimulus_brands_ext_choose", None)), st,
                                   "choose_brands"),
                 "recommend": free(pipe, "recommend", st, "__recommend")}
            own = {c: mode(xs) for c, xs in a["name"].items() if xs}
            row, cells = {}, []
            for k, xs in a.items():
                m = {c: mode(v) for c, v in xs.items() if v and mode(v)}
                if not m:
                    cells.append(f"{k}: -"); continue
                hit = sum(m[c] == panel[k].get(c) for c in m)
                row[k] = {"panel": hit, "categories": len(m)}
                if k != "name":
                    row[k]["moved_from_own_name"] = sum(m[c] != own.get(c) for c in m if own.get(c))
                cells.append(f"{k}: =panel {hit}/{len(m)}" + (f", ≠own Name {row[k]['moved_from_own_name']}" if k != "name" else ""))
            res["pipelines"][pipe][st] = row
            print(f"  {st:6} " + "  |  ".join(cells))
        print()
    return res


def dolci():
    import pyarrow.parquet as pq
    import brand_ladder as B
    lv = B.levels()
    name = {c: B.top(n)[0] for c, n in B.agg(lv["name"]).items()}
    pick = {c: B.top(n)[0] for c, n in B.agg(lv["pick2"]).items()}
    nouns = {}
    for f in ("stimulus_brands.json", "stimulus_brands_ext.json", "stimulus_brands_ext2.json"):
        for s in json.loads((HERE / "spec" / f).read_text())["scenes"]:
            nouns[s["id"]] = re.match(r"Name an? (.+?)\. Reply", s["turns"][0]).group(1)
    cats = {c: n for c, n in nouns.items() if name.get(c) and pick.get(c) and name[c] != pick[c] and n not in ("brand", "company")}
    noun_re = {c: re.compile(r"\b" + re.escape(n) + r"s?\b", re.I) for c, n in cats.items()}
    any_noun = re.compile("|".join(r"\b" + re.escape(n) for n in cats.values()), re.I)
    cue = re.compile(r"\b(recommend|best|which|suggest|pick|choose|favou?rite|should i|good|top)\b", re.I)
    pats = B.pools()[4]

    def first(c, text):
        ms = B.mentions(text or "", pats[c])
        return ms[0] if ms else None

    def label(c, b):
        return "name" if b == name[c] else "pick" if b == pick[c] else ("other" if b else "none")

    def rows(paths, cols):
        for p in paths:
            pf = pq.ParquetFile(p)
            have = [c for c in cols if c in pf.schema_arrow.names]
            for b in pf.iter_batches(batch_size=4096, columns=have):
                yield from b.to_pylist()

    def user_q(msgs):
        u = [m for m in msgs or [] if m.get("role") == "user"]
        return (u[0].get("content") or "") if u else ""

    sft, n_sft = defaultdict(Counter), 0
    for r in rows(sorted((DRIVE / "Dolci-Instruct-SFT" / "data").glob("*.parquet")), ["messages"]):
        n_sft += 1
        q = user_q(r["messages"])
        if len(q) > 600 or not any_noun.search(q) or not cue.search(q):
            continue
        a = next((m.get("content") or "" for m in r["messages"] if m.get("role") == "assistant"), "")
        for c, rx in noun_re.items():
            if rx.search(q):
                sft[c][label(c, first(c, a))] += 1
    dpo, n_dpo = defaultdict(Counter), 0
    for r in rows(sorted((DRIVE / "Dolci-Instruct-DPO" / "data").glob("*.parquet")), ["chosen", "rejected"]):
        n_dpo += 1
        q = user_q(r["chosen"])
        if len(q) > 600 or not any_noun.search(q) or not cue.search(q):
            continue
        ch, rj = (r["chosen"] or [{}])[-1].get("content") or "", (r["rejected"] or [{}])[-1].get("content") or ""
        for c, rx in noun_re.items():
            if rx.search(q):
                dpo[c]["chosen " + label(c, first(c, ch))] += 1
                dpo[c]["rejected " + label(c, first(c, rj))] += 1

    print(f"SFT conversations scanned {n_sft:,}; DPO pairs {n_dpo:,}; {len(cats)} categories where the panel's pick differs from Name\n")
    print(f"{'category':15} {'Name -> pick':28} {'SFT recs: name/pick/other/none':32} {'DPO chosen name/pick':22} {'DPO rejected name/pick'}")
    tot = Counter()
    for c in sorted(cats):
        s, d = sft[c], dpo[c]
        tot.update({"sft " + k: v for k, v in s.items()}); tot.update({"dpo " + k: v for k, v in d.items()})
        print(f"{c:15} {name[c] + ' -> ' + pick[c]:28} {s['name']:4}/{s['pick']:4}/{s['other']:4}/{s['none']:4}{'':12} "
              f"{d['chosen name']:4}/{d['chosen pick']:<4}{'':12} {d['rejected name']:4}/{d['rejected pick']}")
    print(f"\nTOTAL SFT: name {tot['sft name']}, pick {tot['sft pick']}, other {tot['sft other']}, none {tot['sft none']}")
    print(f"TOTAL DPO chosen: name {tot['dpo chosen name']}, pick {tot['dpo chosen pick']} | "
          f"rejected: name {tot['dpo rejected name']}, pick {tot['dpo rejected pick']}")
    return {"sft_scanned": n_sft, "dpo_pairs": n_dpo, "totals": dict(tot),
            "categories": {c: {"name": name[c], "pick": pick[c], "sft": dict(sft[c]), "dpo": dict(dpo[c])} for c in sorted(cats)}}


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    fn = {"verbs": verbs, "brands": brands, "dolci": dolci}.get(cmd)
    if not fn:
        sys.exit(__doc__)
    out = HERE / "probes" / f"stage_{cmd}.json"
    out.write_text(json.dumps(fn(), indent=1, ensure_ascii=False) + "\n")
    print(f"-> {out.relative_to(HERE)}")
