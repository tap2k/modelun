"""
Build the open-ended reply viewer: views/open.html reads views/data-open/.

Every free-wording reply that probe_open.py measures (the 137 "Name a X." prompts and the 44 brand nouns asked as
choose, recommend, pick1 and pick2), with its first mention, mentions and shape flags, plus probe_open's summaries.
The brand replies run to ~150 MB of text, so each prompt is its own file (data-open/p<n>.js), loaded when the page
opens it; data-open/index.js holds the prompt list and the summary tables. Generated, gitignored.

    python studies/consensus/views/build_open.py
    open studies/consensus/views/open.html
"""
import json
import shutil
import sys
from collections import defaultdict
from pathlib import Path

VIEWS = Path(__file__).resolve().parent
STUDY = VIEWS.parent
sys.path.insert(0, str(STUDY))
import brand_ladder  # noqa: E402
import probe_open  # noqa: E402

FLAGS = ["bare", "list", "asks", "disclaims", "bold"]
CLAMPED = {"name-brand": "name", "choose": "choose", "recommend": "recommend_clamp", "pick1": "pick1_clamp"}


def main():
    rs = probe_open.records()
    out = VIEWS / "data-open"
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir()
    cells = defaultdict(list)
    for r in rs:
        cells[(r["group"], r["key"])].append(r)
    by = defaultdict(list)
    for r in rs:
        by[r["group"]].append(r)
    prompts = []
    for i, ((g, k), v) in enumerate(sorted(cells.items(), key=lambda kv: (probe_open.GROUPS.index(kv[0][0]), kv[0][1]))):
        rows = [[r["model"], r["run"], [[t["u"], t["reply"]] for t in r["turns"]], r["words"], r["mentions"],
                 sum(1 << j for j, f in enumerate(FLAGS) if r[f]), r.get("t1_mentions")] for r in v]
        (out / f"p{i}.js").write_text(f"OPEN.chunk({i},{json.dumps(rows, ensure_ascii=False, separators=(',', ':'))});\n")
        s = probe_open.summary(v)
        s["top"] = probe_open.Counter(r["first"] for r in v if r["first"]).most_common(12)
        s["models"] = len({r["model"] for r in v})
        s["consistency"] = probe_open.consistency(v)
        prompts.append({"id": i, "group": g, "key": k, "prompt": v[0]["prompt"], **s})
    groups = {g: {**probe_open.summary(by[g]), "consistency": probe_open.consistency(by[g]),
                  "models": len({r["model"] for r in by[g]}), "prompts": len({r["key"] for r in by[g]})}
              for g in probe_open.GROUPS}
    per_model = defaultdict(dict)
    for g in probe_open.GROUPS:
        mm = defaultdict(list)
        for r in by[g]:
            mm[r["model"]].append(r)
        for m, v in mm.items():
            per_model[m]["vendor"] = v[0]["vendor"]
            per_model[m][g] = {**probe_open.summary(v), "consistency": probe_open.consistency(v)}
    per_vendor = defaultdict(dict)
    for g in probe_open.GROUPS:
        vv = defaultdict(list)
        for r in by[g]:
            vv[r["vendor"]].append(r)
        for vd, v in vv.items():
            per_vendor[vd][g] = {**probe_open.summary(v), "models": len({r["model"] for r in v})}
    # the clamped ("Reply with the name only.") counterpart of each brand form, as brand_ladder scores it; pick2 has none
    lv, (_, nouns) = brand_ladder.levels(), probe_open.brand_pools()
    clamped = defaultdict(dict)
    for g, level in CLAMPED.items():
        field = defaultdict(probe_open.Counter)
        for cats in lv[level].values():
            for c, xs in cats.items():
                field[c].update(xs)
        for c, n in field.items():
            if n and c in nouns:
                a, k = n.most_common(1)[0]
                clamped[g][nouns[c]] = [a, round(k / sum(n.values()), 3)]
    saved = json.loads((STUDY / "probes" / "open.json").read_text()) if (STUDY / "probes" / "open.json").exists() else {}
    index = {"flags": FLAGS, "groups": groups, "prompts": prompts, "per_model": per_model, "per_vendor": per_vendor,
             "agreement": saved.get("brand_form_agreement"), "pick2": saved.get("pick2"), "clamped": clamped}
    (out / "index.js").write_text("OPEN.index(" + json.dumps(index, ensure_ascii=False, separators=(",", ":")) + ");\n")
    size = sum(p.stat().st_size for p in out.iterdir()) / 1e6
    print(f"{len(rs)} replies, {len(prompts)} prompts -> {out.relative_to(STUDY.parent.parent)}/ ({size:.0f} MB)")


if __name__ == "__main__":
    main()
