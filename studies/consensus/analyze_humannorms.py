"""analyze_humannorms.py — paper-1 human-comparison numbers.

Compares the model field's answer distribution to the human first-response distribution from
Van Overschelde, Rawson & Dunlosky (2004), across the 20 categories our stimulus shares with
their norms. The 6 categories whose VO wording differs from ours ("a four-footed animal", "a
carpenter's tool", "a precious stone", ...) use the exact-wording rerun (probes/exactword.json)
so the comparison is apples-to-apples. Writes probes/humannorms.json (derived numbers only;
raw VO norms are the authors' copyrighted data and are not redistributed -- reads a local copy
of the paper).

    ../../.venv/bin/python analyze_humannorms.py --pdf ~/Downloads/1-s2.0-S0749596X03001451-main.pdf
"""
import re, sys, json, argparse
from pathlib import Path
from collections import Counter
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from analyze import norm, load

VO_TO_OURS = {"Apreciousstone":"gemstone","Ametal":"metal","Afour-footedanimal":"animal",
 "Atypeoffabric":"fabric","Acolor":"color","Afruit":"fruit","Acountry":"country",
 "Acarpenter'stool":"tool","Asport":"sport","Amusicalinstrument":"instrument","Abird":"bird",
 "Avegetable":"vegetable","Aflower":"flower","Atree":"tree","Afish":"fish","Acity":"city",
 "Aninsect":"insect","Atypeofdance":"dance","Anoccupationorprofession":"occupation","Anherb":"herb"}
WORDING_MISMATCH = {"animal","tool","gemstone","occupation","dance","fabric"}

def parse_vo(pdf_path):
    import pdfplumber
    text = "\n".join((p.extract_text() or "") for p in pdfplumber.open(str(pdf_path)).pages[7:47])
    cats, cur = {}, None
    for ln in text.split("\n"):
        ln = ln.strip()
        m = re.match(r"^(\d{1,2})\.([A-Za-z].*)", ln.replace(" ", ""))
        if m and 1 <= int(m.group(1)) <= 70:
            cur = m.group(2).replace(" ", "").replace("(cid:1)", "'"); cats[cur] = []; continue
        if cur is None or ln.startswith(("Response","(")) or "Overall" in ln or "VanOverschelde" in ln.replace(" ",""):
            continue
        nums = re.findall(r"\d+\.\d+", ln)
        if not nums: continue
        resp = ln[:ln.find(nums[0])].strip()
        if not resp: continue
        v = [float(x) for x in nums]
        cats[cur].append((resp, v[1] if len(v) >= 8 else 0.0))
    return {VO_TO_OURS[k]: v for k, v in cats.items() if k in VO_TO_OURS}

def merged(toks):
    pool = Counter(toks); stems = {w: w[:-1] for w in pool if w.endswith("s") and w[:-1] in pool}
    return Counter(stems.get(t, t) for t in toks)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--pdf", required=True); args = ap.parse_args()
    human = parse_vo(Path(args.pdf).expanduser())
    exact = json.loads((HERE / "probes/exactword.json").read_text())["replies"]

    ans = load(HERE); models = sorted(m for m in ans if ans[m])
    def base_field(cat):
        return merged([a for m in models for a in ans[m].get(cat, [])])
    def exact_field(cat):
        return merged([t for lab in exact for r in exact[lab].get(cat, []) if r for t in [norm(r)] if t])

    rows = []
    for ours in sorted(human):
        hb = human[ours]
        h_resp, h_first = max(hb, key=lambda x: x[1])
        h_n5 = sum(1 for _, f in hb if f >= 0.05)
        f = exact_field(ours) if ours in WORDING_MISMATCH else base_field(ours)
        tot = sum(f.values()); m_resp, m_n = f.most_common(1)[0]
        m_n5 = sum(1 for v in f.values() if v / tot >= 0.05)
        rows.append({"category": ours, "human_modal": h_resp.lower().split("(")[0],
                     "human_modal_first": round(h_first, 3), "human_n_ge5": h_n5,
                     "model_modal": m_resp, "model_modal_share": round(m_n / tot, 3),
                     "model_n_ge5": m_n5, "wording_mismatch": ours in WORDING_MISMATCH})
    h = np.array([r["human_modal_first"] for r in rows]); m = np.array([r["model_modal_share"] for r in rows])
    veg = {a.lower().split("(")[0]: f for a, f in human["vegetable"]}
    vp = base_field("vegetable")
    out = {"source": "Van Overschelde, Rawson & Dunlosky (2004), JML 50:289-335, first-response column",
           "population": "US undergraduates, 3 universities, ~2004",
           "n_categories": len(rows),
           "mean_human_modal_first": round(float(h.mean()), 3),
           "mean_model_modal_share": round(float(m.mean()), 3),
           "model_more_concentrated_n": int((m > h).sum()),
           "mean_human_n_ge5": round(float(np.mean([r["human_n_ge5"] for r in rows])), 2),
           "mean_model_n_ge5": round(float(np.mean([r["model_n_ge5"] for r in rows])), 2),
           "reversals": [r["category"] for r in rows if r["human_modal_first"] > r["model_modal_share"]],
           "tomato": {"human_first": round(veg.get("tomato", 0.0), 3),
                      "model_share": round(vp.get("tomato", 0) / sum(vp.values()), 3)},
           "per_category": sorted(rows, key=lambda r: -r["model_modal_share"])}
    (HERE / "probes/humannorms.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"{out['n_categories']} cats | human modal {out['mean_human_modal_first']:.0%} vs model {out['mean_model_modal_share']:.0%} "
          f"| model more concentrated {out['model_more_concentrated_n']}/{out['n_categories']} | reversals {out['reversals']}")
    print(f"distinct >=5%: human {out['mean_human_n_ge5']} vs model {out['mean_model_n_ge5']} | "
          f"tomato human {out['tomato']['human_first']:.0%} vs model {out['tomato']['model_share']:.0%}")

if __name__ == "__main__":
    main()
