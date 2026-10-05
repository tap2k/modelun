"""analyze_humannorms.py — paper-1 human-comparison numbers.

Compares the model field's answer distribution to the human first-response distribution from
Van Overschelde, Rawson & Dunlosky (2004), across the 20 categories our stimulus shares with
their norms. The 6 categories whose VO wording differs from ours ("a four-footed animal", "a
carpenter's tool", "a precious stone", ...) use the exact-wording rerun (probes/exactword.json)
so the comparison is apples-to-apples. Writes probes/humannorms.json (derived numbers only;
raw VO norms are the authors' copyrighted data and are not redistributed -- reads a local copy
of the paper).

    ../../.venv/bin/python analyze_humannorms.py --pdf ~/Desktop/projects/modelUN/papers/vanoverschelde-2004-category-norms.pdf
    ... --v3   # the v3 field (every panel model, 8 runs; census8) -> probes/humannorms_v3.json. The six
               # wording-mismatch categories still use the exact-wording rerun (probes/exactword.json)
"""
import re, sys, json, argparse
from pathlib import Path
from collections import Counter
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from analyze import norm, answers, compound, HEADS

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

def dedupe(rows):
    """The norms list a combined row ("USA/US/UnitedStates", "NewYork(City)") followed by the variants it sums. Keep
    the combined row and skip the variants after it, so no response is counted twice. A row is combined when its
    name has a "/" or a parenthetical other than the plural "(s)", and its share equals the sum of the next k rows."""
    out, i = [], 0
    while i < len(rows):
        name, f = rows[i]
        out.append((name, f))
        skip = 0
        if "/" in name or ("(" in name and "(s)" not in name):
            for k in range(2, 7):
                if i + k < len(rows) + 1 and abs(f - sum(v for _, v in rows[i + 1:i + 1 + k])) <= 0.02:
                    skip = k
                    break
        i += 1 + skip
    return out


def human_dist(rows, variants, heads=None):
    """{answer: first-response share}, the response read as the census reads a reply: the first alternative of a
    combined row, the census's one-word normalisation, then the census's variant map for the category."""
    out, shown = Counter(), {}
    for name, f in dedupe(rows):
        first = re.split(r"[/(]", name)[0]
        spaced = re.sub(r"([a-z])([A-Z])", r"\1 \2", first)
        a = (heads and compound(spaced, heads)) or norm(spaced) or first.lower()   # compound names as the census joins them
        out[variants.get(a, a)] += f
        shown.setdefault(variants.get(a, a), re.sub(r"([a-z])([A-Z])", r"\1 \2", first).strip())
    return out, shown


def eff(d):
    t = sum(d.values())
    return 2 ** -sum(v / t * np.log2(v / t) for v in d.values() if v > 0)


def merged(toks):
    """The plural merge within one field's pool, for the exact-wording rerun (answers() does it for the panel)."""
    pool = Counter(toks); stems = {w: w[:-1] for w in pool if w.endswith("s") and w[:-1] in pool}
    return Counter(stems.get(t, t) for t in toks)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--pdf", required=True); ap.add_argument("--v3", action="store_true")
    args = ap.parse_args()
    human = parse_vo(Path(args.pdf).expanduser())
    exact = json.loads((HERE / "probes/exactword.json").read_text())["replies"]

    ans = answers(HERE, "census8" if args.v3 else "census"); models = sorted(m for m in ans if ans[m])
    def base_field(cat):
        return Counter(a for m in models for a in ans[m].get(cat, []))
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
    out["field"] = f"{len(models)} models, {'8' if args.v3 else '4'} runs"
    # Whole distributions (2026-10-05), on the categories with identical wording: people's first responses against
    # the model field with one vote per model (its most frequent answer), so both are between-individual spreads.
    variants = json.loads((HERE / "answer_variants.json").read_text())["variants"]
    dist = []
    for ours in sorted(c for c in human if c not in WORDING_MISMATCH):
        h, shown = human_dist(human[ours], variants.get(ours, {}), HEADS.get(ours))
        vote = Counter(Counter(ans[m][ours]).most_common(1)[0][0] for m in models if ans[m].get(ours))
        own = [Counter(ans[m][ours]).most_common(1)[0][1] / len(ans[m][ours]) for m in models if ans[m].get(ours)]
        ht, vt = sum(h.values()), sum(vote.values())
        mt, mn = vote.most_common(1)[0]
        dist.append({"category": ours, "human_top": h.most_common(1)[0][0], "human_top_as_written": shown[h.most_common(1)[0][0]], "human_top_share": round(h.most_common(1)[0][1] / ht, 3),
                     "model_top": mt, "model_top_share_one_vote": round(mn / vt, 3),
                     "human_share_of_model_top": round(h.get(mt, 0) / ht, 3),
                     "single_model_own_top_share": round(float(np.mean(own)), 3),
                     "human_effective_answers": round(float(eff(h)), 1), "model_effective_answers": round(float(eff(vote)), 1),
                     "human_distinct": len(h), "model_distinct": len(vote),
                     "model_votes_on_human_answers": round(sum(v for a, v in vote.items() if h.get(a, 0) > 0) / vt, 3)})
    mean = lambda k: round(float(np.mean([d[k] for d in dist])), 3)
    out["distributions"] = {"n_categories": len(dist), "same_top_answer": sum(d["human_top"] == d["model_top"] for d in dist),
                            **{f"mean_{k}": mean(k) for k in ("human_top_share", "model_top_share_one_vote",
                               "single_model_own_top_share", "human_share_of_model_top", "human_effective_answers",
                               "model_effective_answers", "human_distinct", "model_distinct", "model_votes_on_human_answers")},
                            "per_category": dist}
    (HERE / ("probes/humannorms_v3.json" if args.v3 else "probes/humannorms.json")).write_text(json.dumps(out, indent=1) + "\n")
    print(f"{out['n_categories']} cats | human modal {out['mean_human_modal_first']:.0%} vs model {out['mean_model_modal_share']:.0%} "
          f"| model more concentrated {out['model_more_concentrated_n']}/{out['n_categories']} | reversals {out['reversals']}")
    print(f"distinct >=5%: human {out['mean_human_n_ge5']} vs model {out['mean_model_n_ge5']} | "
          f"tomato human {out['tomato']['human_first']:.0%} vs model {out['tomato']['model_share']:.0%}")
    d = out["distributions"]
    print(f"distributions, {d['n_categories']} identical-wording categories: same top answer {d['same_top_answer']}; top share "
          f"people {d['mean_human_top_share']:.0%}, models one vote {d['mean_model_top_share_one_vote']:.0%}, one model's own runs "
          f"{d['mean_single_model_own_top_share']:.0%}; people giving the models' top {d['mean_human_share_of_model_top']:.0%}; "
          f"effective answers people {d['mean_human_effective_answers']} vs models {d['mean_model_effective_answers']}; "
          f"model votes on answers people gave {d['mean_model_votes_on_human_answers']:.0%}")
    for r in d["per_category"]:
        print(f"   {r['category']:11} people {r['human_top_as_written']} {r['human_top_share']:.0%} | models {r['model_top']} "
              f"{r['model_top_share_one_vote']:.0%} (people {r['human_share_of_model_top']:.0%}) | effective "
              f"{r['human_effective_answers']} vs {r['model_effective_answers']} | on people's answers {r['model_votes_on_human_answers']:.0%}")

if __name__ == "__main__":
    main()
