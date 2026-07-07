"""probe_humannorms.py — human vs. model answer-concentration, using the first-response
column of the Van Overschelde, Rawson & Dunlosky (2004) category norms.

The norms are a timed free-listing task, BUT they tabulate, per exemplar, the proportion of
participants who produced it FIRST -- a clean single-response comparator, which is the right
match for our single-answer model task. We compare, per overlapping category:
  * modal share  -- the top answer's first-response share (human) vs modal share (model field)
  * n>=5%        -- number of distinct answers at >=5% share (same threshold both sides)

The raw norms are the authors' copyrighted data and are NOT redistributed; this script reads a
local copy of the paper (JML 50:289-335) and writes only DERIVED per-category summary numbers
to probes/humannorms.json. Point --pdf at your copy.

    ../../.venv/bin/python probe_humannorms.py --pdf ~/Downloads/1-s2.0-S0749596X03001451-main.pdf
"""

import re
import sys
import json
import argparse
from pathlib import Path
from collections import Counter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from analyze import load

# VO appendix category name (spaces stripped, apostrophe normalized) -> our category id.
# NOTE the wording mismatches flagged below: these categories differ from our prompt and are
# candidates for the exact-wording rerun (studies/humannorms).
VO_TO_OURS = {
    "Apreciousstone": "gemstone", "Ametal": "metal", "Afour-footedanimal": "animal",
    "Atypeoffabric": "fabric", "Acolor": "color", "Afruit": "fruit", "Acountry": "country",
    "Acarpenter'stool": "tool", "Asport": "sport", "Amusicalinstrument": "instrument",
    "Abird": "bird", "Avegetable": "vegetable", "Aflower": "flower", "Atree": "tree",
    "Afish": "fish", "Acity": "city", "Aninsect": "insect", "Atypeofdance": "dance",
    "Anoccupationorprofession": "occupation", "Anherb": "herb",
}
# categories whose VO wording differs materially from our prompt (rerun to de-confound)
WORDING_MISMATCH = {"animal", "tool", "gemstone", "occupation", "dance"}


def parse_vo(pdf_path):
    import pdfplumber
    pdf = pdfplumber.open(pdf_path)
    text = "\n".join((pdf.pages[i].extract_text() or "") for i in range(7, 47))
    cats, cur = {}, None
    for ln in text.split("\n"):
        ln = ln.strip()
        m = re.match(r"^(\d{1,2})\.([A-Za-z].*)", ln.replace(" ", ""))
        if m and 1 <= int(m.group(1)) <= 70:
            cur = m.group(2).replace(" ", "").replace("(cid:1)", "'")
            cats[cur] = []
            continue
        if cur is None or ln.startswith(("Response", "(")) or "Overall" in ln \
                or "VanOverschelde" in ln.replace(" ", ""):
            continue
        nums = re.findall(r"\d+\.\d+", ln)
        if not nums:
            continue
        resp = ln[:ln.find(nums[0])].strip()
        if not resp:
            continue
        vals = [float(x) for x in nums]
        first = vals[1] if len(vals) >= 8 else 0.0  # First present only on full 8-number rows
        cats[cur].append((resp, first))
    return {VO_TO_OURS[k]: v for k, v in cats.items() if k in VO_TO_OURS}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True, help="local copy of Van Overschelde et al. 2004")
    args = ap.parse_args()

    human = parse_vo(Path(args.pdf).expanduser())

    ans = load(HERE)
    models = sorted(m for m in ans if ans[m])
    cats = sorted({c for m in models for c in ans[m]})
    for c in cats:  # plural merge, identical to analyze.py
        pool = Counter(a for m in models for a in ans[m].get(c, []))
        stems = {w: w[:-1] for w in pool if w.endswith("s") and w[:-1] in pool}
        for m in models:
            if c in ans[m]:
                ans[m][c] = [stems.get(a, a) for a in ans[m][c]]

    rows = []
    for ours in sorted(human):
        hb = human[ours]
        h_resp, h_first = max(hb, key=lambda x: x[1])
        h_n5 = sum(1 for _, f in hb if f >= 0.05)
        pool = Counter(a for m in models for a in ans[m].get(ours, []))
        tot = sum(pool.values())
        m_resp, m_n = pool.most_common(1)[0]
        m_n5 = sum(1 for v in pool.values() if v / tot >= 0.05)
        rows.append({"category": ours,
                     "human_modal": h_resp.lower(), "human_modal_first": round(h_first, 3),
                     "human_n_ge5": h_n5,
                     "model_modal": m_resp, "model_modal_share": round(m_n / tot, 3),
                     "model_n_ge5": m_n5,
                     "wording_mismatch": ours in WORDING_MISMATCH})

    import numpy as np
    h = np.array([r["human_modal_first"] for r in rows])
    m = np.array([r["model_modal_share"] for r in rows])
    # tomato: human first-response share for vegetable, vs model
    veg = {a.lower().split("(")[0]: f for a, f in human["vegetable"]}
    veg_pool = Counter(a for mm in models for a in ans[mm].get("vegetable", []))
    tomato = {"human_first": round(veg.get("tomato", 0.0), 3),
              "model_share": round(veg_pool.get("tomato", 0) / sum(veg_pool.values()), 3)}

    out = {"source": "Van Overschelde, Rawson & Dunlosky (2004), JML 50:289-335, first-response column",
           "caveats": "US undergraduates, 2004; free-listing task, first-response column used as single-response comparator",
           "n_categories": len(rows),
           "mean_human_modal_first": round(float(h.mean()), 3),
           "mean_model_modal_share": round(float(m.mean()), 3),
           "model_more_concentrated_n": int((m > h).sum()),
           "mean_human_n_ge5": round(float(np.mean([r["human_n_ge5"] for r in rows])), 2),
           "mean_model_n_ge5": round(float(np.mean([r["model_n_ge5"] for r in rows])), 2),
           "reversals": [r["category"] for r in rows if r["human_modal_first"] > r["model_modal_share"]],
           "tomato": tomato,
           "per_category": sorted(rows, key=lambda r: -r["model_modal_share"])}
    (HERE / "probes").mkdir(exist_ok=True)
    (HERE / "probes" / "humannorms.json").write_text(json.dumps(out, indent=1) + "\n")

    print(f"{out['n_categories']} categories | human modal-first {out['mean_human_modal_first']:.0%} "
          f"vs model modal {out['mean_model_modal_share']:.0%} | model more concentrated "
          f"{out['model_more_concentrated_n']}/{out['n_categories']}")
    print(f"mean n>=5%: human {out['mean_human_n_ge5']} vs model {out['mean_model_n_ge5']}")
    print(f"reversals: {out['reversals']}  (wording-mismatch: {sorted(WORDING_MISMATCH)})")
    print(f"tomato (vegetable): human-first {tomato['human_first']:.0%} vs model {tomato['model_share']:.0%}")
    print("-> probes/humannorms.json")


if __name__ == "__main__":
    main()
