"""brands_paper.py — the taste paper's tables and checked numbers, from the committed probe outputs.

Reads probes/brand_ladder.json (brand_ladder.py), brand_logprob.json and brand_logprob_ownlist.json
(probe_brand_logprob.py), stage_pick.json (stage_pick.py), answer_logprob_steps.json (probe_answer_logprob.py score),
stage_dolci.json and stage_tulu.json (stage_ladder.py), and writes paper-brands/gen/. Zero API calls; no recomputation
(each probe script owns its numbers). Brand categories are the 42 that name a product (GENERIC left out).

    python3 brands_paper.py
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
GEN = HERE / "paper-brands" / "gen"
P = lambda name: json.loads((HERE / "probes" / name).read_text())
PIPES = (("olmo3-7b", "OLMo 3 7B"), ("tulu3-8b", "Tulu 3 8B"), ("olmo31-32b", "OLMo 3.1 32B"))
LEVELS = (("name", "Name"), ("choose", "Choose"), ("recommend_clamp", "Recommend"), ("pick2", "Recommend, then pick"))


def pct(x, d=0):
    return f"{100 * x:.{d}f}\\%"


def ci(b, scale=100, d=0, sign=False):
    f = (lambda v: f"{scale * v:+.{d}f}") if sign else (lambda v: f"{scale * v:.{d}f}")
    return f"{f(b['mean'])} [{f(b['ci90'][0])}, {f(b['ci90'][1])}]"


def write(name, lines):
    (GEN / name).write_text("\n".join(lines) + "\n")


def main():
    GEN.mkdir(parents=True, exist_ok=True)
    lad, lp, own, sp = P("brand_ladder.json"), P("brand_logprob.json"), P("brand_logprob_ownlist.json"), P("stage_pick.json")
    cen, dol, tul = P("answer_logprob_steps.json"), P("stage_dolci.json"), P("stage_tulu.json")
    lv = lad["levels_specific"]

    # the verb ladder on the panel: clamped rows, free rows, the two-turn pick
    write("ladder_rows.tex", [f"{label} & {lv[k]['flips']} & {pct(lv[k]['top_share'])} & {pct(lv[k]['retention'])} \\\\"
                              for k, label in LEVELS])

    # the verb and clamp factors against their split-half floors (factors.py)
    fac = {(r["factor"], r["contrast"]): r for r in P("factors.json") if r["battery"] == "brands"}
    rows = []
    for key, label in ((("verb", "Name -> Choose"), "Name $\\to$ Choose"), (("verb", "Name -> Recommend"), "Name $\\to$ Recommend"),
                       (("verb (free)", "free Name -> two-turn pick"), "free Name $\\to$ two-turn pick"),
                       (("clamp", "Name"), "one name $\\to$ free Name"), (("clamp", "Choose"), "one name $\\to$ free Choose"),
                       (("clamp", "Recommend"), "one name $\\to$ free Recommend")):
        r = fac[key]
        rows.append(f"{label} & {pct(r['consensus_moved'])} & {pct(r['floor_moved'])} & {pct(r['own_kept'])} & {pct(r['floor_kept'])} \\\\")
    write("factor_rows.tex", rows)

    # the categories where the two-turn pick leaves the Name brand
    cs = lv["name"]["consensus"]
    spell = {"chatgpt": "ChatGPT", "mcdonald's": "McDonald's", "chick-fil-a": "Chick-fil-A", "whatsapp": "WhatsApp",
             "t-mobile": "T-Mobile", "duckduckgo": "DuckDuckGo", "kind": "KIND", "aws": "AWS"}
    nice = lambda b: spell.get(b) or " ".join(w[:1].upper() + w[1:] for w in (b or "--").split())
    cat = {"ai_assistant": "AI assistant", "ev": "electric car", "pm_software": "project management software"}
    write("flip_rows.tex", [f"{cat.get(c, c.replace('_', ' '))} & {nice(cs[c][0])} & {nice(lv['choose']['consensus'][c][0])} & "
                            f"{nice(lv['recommend_clamp']['consensus'][c][0])} & {nice(lv['pick2']['consensus'][c][0])} \\\\"
                            for c in sorted(cs) if lv["pick2"]["consensus"][c][0] != cs[c][0]])

    # the fixed-list pick by stage (both orders), and the verb shift under Recommend
    rows = []
    for p, label in PIPES:
        s = lp[p]["stages"]
        rows.append(f"{label} & " + " & ".join(pct(s[st]["pick_h2h"]["mean"]) for st in ("base", "sft", "dpo", "rl"))
                    + f" & {ci(lp[p]['steps']['sft->dpo']['pick_h2h'], sign=True)} \\\\")
    write("stage_pick_rows.tex", rows)
    write("stage_shift_rows.tex", [f"{label} & " + " & ".join(f"{lp[p]['stages'][st]['pick']['shift']['recommend']['mean']:+.2f}"
                                                              for st in ("base", "sft", "dpo", "rl"))
                                   + f" & {ci(lp[p]['steps']['sft->dpo']['shift_recommend'], scale=1, d=2, sign=True)} \\\\"
                                   for p, label in PIPES])

    # sampled picks against log-probabilities on the SFT stage's own lists
    hf = sp["held_fixed_pooled"]
    write("agreement_rows.tex", [f"{label} & {st.upper()} & {pct(hf[f'{p}-{st}']['complete']['head_to_head'])} & "
                                 f"{pct(own[p]['stages'][st]['mean'])} \\\\"
                                 for p, label in PIPES for st in ("sft", "dpo", "rl")])

    # census Choose: the same verb shift outside brands
    write("census_rows.tex", [f"{label} & " + " & ".join(f"{cen[p]['stages'][st]['mean']:+.2f}" for st in ("base", "sft", "dpo", "rl"))
                              + f" & {ci(cen[p]['steps']['sft->dpo'], scale=1, d=2, sign=True)} \\\\" for p, label in PIPES])

    # brand recommendations in the post-training data
    t = lambda d, k: d["totals"].get(k, 0)
    write("data_rows.tex", [f"{label} & {t(d, 'sft name')} & {t(d, 'sft pick')} & {t(d, 'dpo chosen name')} & {t(d, 'dpo chosen pick')} & "
                            f"{t(d, 'dpo rejected name')} & {t(d, 'dpo rejected pick')} \\\\"
                            for label, d in (("OLMo 3 (Dolci)", dol), ("Tulu 3", tul))])

    # headline values, for checking the text after a rerun
    labs = {k: v for k, v in P("brand_confounds.json")["by_lab"].items() if v["models"] >= 3}
    nums = {"labsThreePlus": len(labs), "labModels": sum(v["models"] for v in labs.values()),
            "labPickMovedMin": pct(min(v["consensus_moved_pick2"] for v in labs.values())),
            "labPickMovedMax": pct(max(v["consensus_moved_pick2"] for v in labs.values())),
            "pickFirstListedConfound": pct(P("brand_confounds.json")["list_position"]["position"]["first"]),
            "panelModels": lv["name"]["models"], "brandCategories": lv["name"]["cats"],
            "pickTwoFlips": lv["pick2"]["flips"], "pickTwoKept": pct(lv["pick2"]["retention"]),
            "defaultInList": pct(lad["two_turn"]["default_in_list"]), "defaultPicked": pct(lad["two_turn"]["default_picked"]),
            "pickFirstListed": pct(lad["two_turn"]["first_listed"])}
    for p, label in PIPES:
        key = label.replace(" ", "").replace(".", "")
        nums[f"dpoStep{key}"] = pct(lp[p]["steps"]["sft->dpo"]["pick_h2h"]["mean"])
    write("numbers.tex", [f"% {k} = {v}" for k, v in nums.items()])
    print(f"-> {GEN.relative_to(HERE)}/: " + ", ".join(sorted(f.name for f in GEN.glob('*.tex'))))


if __name__ == "__main__":
    main()
