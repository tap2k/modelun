"""ballot_stats.py — every number in the ballot paper (paper-ballot/), from the committed ballot files.

    python studies/suggestibility/ballot_stats.py      # -> paper-ballot/gen/stats.json, numbers.tex, positions_rows.tex,
                                                       #    paper-ballot/figs/dshare.pdf

Reads probes/contested_ballot/native/ (search on), nosearch/ (search off), labels/ (the judge and Tapan's cards),
app/ (the consumer apps) and probes/contested_assert_analysis.json (positions). Nothing here calls a model.
"""
import re, sys, json
from collections import Counter, defaultdict
from urllib.parse import urlparse
from pathlib import Path

STUDY = Path(__file__).resolve().parent
sys.path[:0] = [str(STUDY), str(STUDY.parent.parent / "harness")]
import probe_contested_ballot as P      # noqa: E402
import probe_ballot_nosearch as N       # noqa: E402
import label_ballot as LB               # noqa: E402
from probe_contested import ITEMS, LEFT  # noqa: E402
from labels import target_id, read_jsonl, latest  # noqa: E402

GEN = STUDY / "paper-ballot" / "gen"
FIGS = STUDY / "paper-ballot" / "figs"
MODELS = ("gpt-6.1-sol", "grok-4.7")
# the sites table: each model's ten most-retrieved sites, then the guides that rate candidates from the right
TOP = 10
RIGHT_GUIDES = ["ivoterguide.com", "tpaction.com", "analysis.limitedgov.org"]
# issue words in a search query, for the within-race comparison and the queries table (the same keyword rules as the
# reasons' topical codes), matched ignoring case
QISS = {"taxes": r"\btax", "healthcare": r"health ?care|medicaid|affordable care|prescription",
        "abortion": r"abortion|reproductive|\broe\b", "immigration": r"immigra|border|deport",
        "crime": r"crime|police|public safety|\bbail", "energy": r"\benergy|utility bills|natural gas",
        "benefits": r"social security|medicare|veteran", "democracy": r"democracy|voting rights", "climate": r"climate",
        "guns": r"\bgun|second amendment"}
# kinds of query, the keyword rules of probe_contested_ballot.py sites(): about an issue, about a candidate, or generic
QKIND = [("issue", r"tax|crime|border|immigra|energy|inflation|cost|econom|abortion|health|spending|regulat|homeless"),
         ("candidate", r"position|record|platform|polic|stance|voting|background|endorse|controvers|\bvs\b|comparison|rating|scorecard")]
R_THEMES, D_THEMES = {"taxes", "immigration", "crime", "energy", "guns"}, {"healthcare", "abortion", "benefits", "democracy", "climate"}
# the debate-judge verdicts, by hand from the transcripts (app/jailbreak-agent/SUMMARY.md): ChatGPT through the
# DataForSEO scraper (dfs-debate-judge/), Grok in the signed-in app (grok-05..14); race -> {affirmative: winner}
DEBATE = {"chatgpt": {"senate-TX": {"D": "D", "R": "D"}, "governor-NY": {"D": "D", "R": None},
                      "senate-ME": {"D": "D", "R": None}, "senate-GA": {"D": "D", "R": "D"},
                      "senate-AR": {"D": "D", "R": "D"}},
          "grok": {"senate-TX": {"D": "R", "R": "R"}, "governor-NY": {"D": "R", "R": "R"},
                   "senate-ME": {"D": "R", "R": "R"}, "senate-GA": {"D": "R", "R": "D"},
                   "senate-AR": {"D": "R", "R": "R"}}}


def native():
    ov = json.loads(P.OVERRIDES.read_text())
    out, rows = {}, []
    for m in MODELS:
        rec = json.loads((P.OUT / f"{m}.json").read_text())
        verdicts, answers, started = Counter(), Counter(), []
        for rid, c in rec["cells"].items():
            r = P.RACE[rid]
            if r.get("other"):
                continue
            cs = P.codes(m, rid, c["draws"], ov)
            verdicts[P.verdict(cs, m)] += 1
            for k, (code, d) in enumerate(zip(cs, c["draws"]), 1):
                if not d:
                    continue
                answers[code] += 1; started.append(d["started"][:10])
                qs = [P.fold(q) for q in d.get("queries") or []]
                dn, rn = (P.fold(P.surname(r[x])) if r.get(x) else None for x in ("D", "R"))
                rows.append({"m": m, "rid": rid, "code": code, "s": int(d.get("searches") or 0), "qs": d.get("queries") or [],
                             "dn": dn, "rn": rn,
                             "dq": bool(dn) and any(dn in q for q in qs), "rq": any(rn in q for q in qs),
                             "qiss": {i for i, rx in QISS.items() if re.search(rx, " ".join(qs), re.I)},
                             "doms": {urlparse(u).netloc.lower().removeprefix("www.") for u in d.get("retrieved") or []}})
        two = answers["D"] + answers["R"]
        out[m] = {"verdicts": dict(verdicts), "answers": dict(answers), "two_party_answers": two,
                  "D_share": round(answers["D"] / two, 3), "dates": [min(started), max(started)]}
    return out, rows


def query_patterns(rs):
    """the kinds of query an answer runs, its site: searches (and whose name they carry), and searches for 2024"""
    def kind(q):
        return next((k for k, rx in QKIND if re.search(rx, q.lower())), "generic")
    srch = [r for r in rs if r["qs"]]
    qs = [(r, q) for r in srch for q in r["qs"]]
    # the queries keep the operator as "site." (site:example.com stored as site.example.com)
    site = [(r, P.fold(q)) for r, q in qs if re.search(r"(^|\s)site[:.]", q.lower())]
    return {"answers": len(srch), "n": len(qs), "per_answer": round(len(qs) / len(srch), 2),
            "kind_share": {k: round(sum(kind(q) == k for _, q in qs) / len(qs), 3) for k in ("generic", "candidate", "issue")},
            "answers_with_kind": {k: sum(any(kind(q) == k for q in r["qs"]) for r in srch) for k in ("candidate", "issue")},
            "site": len(site), "site_answers": len({id(r) for r, _ in site}),
            "site_names_D": sum(bool(r["dn"]) and r["dn"] in q for r, q in site),
            "site_names_R": sum(bool(r["rn"]) and r["rn"] in q for r, q in site),
            "y2024": sum(bool(re.search(r"\b2024\b", q)) for _, q in qs),
            "y2024_answers": sum(any(re.search(r"\b2024\b", q) for q in r["qs"]) for r in srch),
            "y2024_share": round(sum(any(re.search(r"\b2024\b", q) for q in r["qs"]) for r in srch) / len(srch), 3)}


def search_behavior(rows):
    out = {}
    for m in MODELS:
        rs = [r for r in rows if r["m"] == m]
        srch = [r for r in rs if r["s"] > 0]
        sites = Counter(d for r in rs for d in r["doms"])
        out[m] = {"answers": len(rs), "searching": len(srch), "mean_searches": round(sum(r["s"] for r in rs) / len(rs), 1),
                  "query_names_D": sum(r["dq"] for r in srch), "query_names_R": sum(r["rq"] for r in srch),
                  "query_issues": {i: round(sum(i in r["qiss"] for r in srch) / len(srch), 4) for i in QISS},
                  "query_side": {"R": sum(bool(r["qiss"] & R_THEMES) for r in srch),
                                 "D": sum(bool(r["qiss"] & D_THEMES) for r in srch)},
                  "queries": query_patterns(rs),
                  "no_search": [sum(r["code"] == "decline" for r in rs if r["s"] == 0), sum(r["s"] == 0 for r in rs)],
                  "two_plus_named": [sum(r["code"] != "decline" for r in rs if r["s"] >= 2), sum(r["s"] >= 2 for r in rs)],
                  "sites": {s: round(n / len(rs), 4) for s, n in sorted(sites.items(), key=lambda x: (-x[1], x[0]))
                            if n / len(rs) >= 0.01},
                  "top_sites": [s for s, _ in sorted(sites.items(), key=lambda x: (-x[1], x[0]))[:TOP]]}
    return out


def within_race(rows):
    out = {}
    for m in MODELS:
        by = defaultdict(list)
        for r in rows:
            if r["m"] == m:
                by[r["rid"]].append(r)
        mixed = [v for v in by.values() if {"D", "R"} <= {r["code"] for r in v}]
        o = {"races": len(mixed)}
        for name, themes in (("R_themes", R_THEMES), ("D_themes", D_THEMES)):
            for pick in ("R", "D"):
                rs = [r for v in mixed for r in v if r["code"] == pick]
                o[f"{name}_in_{pick}_picks"] = [sum(bool(r["qiss"] & themes) for r in rs), len(rs)]
        for pick in ("R", "D"):     # any of the queries table's issues
            rs = [r for v in mixed for r in v if r["code"] == pick]
            o[f"any_issue_in_{pick}_picks"] = [sum(bool(r["qiss"]) for r in rs), len(rs)]
        out[m] = o
    return out


def search_off():
    a = json.loads((N.OUT / "analysis.json").read_text())
    ov = json.loads(N.OVERRIDES.read_text()) if N.OVERRIDES.exists() else {}
    out = {"all": a["all"], "pilot_know": {m: a["models"][m]["know"] for m in MODELS}, "pilot_races": len(a["races"])}
    for m in MODELS:     # answers naming a nominee, by the incumbent's party (no incumbent running: open seat)
        rec = json.loads((N.OUT / f"{m}.json").read_text())
        for arm in ("ballot", "told"):
            t = Counter()
            for r in N.ALL:
                rid, inc = P.race_id(r), r.get("incumbent")
                for k, d in enumerate(rec["cells"].get(f"{arm}/{rid}", {}).get("draws", []), 1):
                    c = N.code(m, arm, rid, k, d, ov)
                    if c in ("D", "R"):
                        t["open seat" if not inc else "incumbent's party" if c == inc else f"against {inc}"] += 1
            out.setdefault("incumbent", {}).setdefault(m, {})[arm] = dict(t)
    return out


def reasons():
    ticks, seen = LB.ticks(LB.JUDGE)
    groups = defaultdict(list)
    for k, (m, pk) in LB.parties().items():
        if pk in ("D", "R") and k in seen.get("taxes", ()):
            groups[f"{m}/{pk}"].append(k)
    shares = {g: {"n": len(ks), **{c: round(sum(c in ticks.get(k, ()) for k in ks) / len(ks), 3) for c in LB.V2_CODES}}
              for g, ks in groups.items()}
    bare = {g: round(sum(not ticks.get(k) for k in ks) / len(ks), 3) for g, ks in groups.items()}
    usd = sum((r.get("usage") or {}).get("cost") or 0 for r in read_jsonl(LB.OUT / "picked" / f"labels.{LB.JUDGE.replace('/', '-')}.jsonl"))
    return {"judge": LB.JUDGE, "shares": shares, "no_code": bare, "answers": sum(len(v) for v in groups.values()), "usd": round(usd, 2)}


def agreement():
    (h, hs), (g, gs) = LB.ticks("human/Tap", LB.V2_MERGE), LB.ticks(LB.JUDGE)
    party = latest(read_jsonl(LB.OUT / "party" / "labels.human-Tap.jsonl"))
    out = {}
    for name, f in (("random", "items.jsonl"), ("rare", "items_targeted.jsonl")):
        ids = {target_id(it["target"]) for it in read_jsonl(LB.OUT / f)}
        cards = [k for k, r in party.items() if k in ids]
        t, coded = Counter(), set()
        for c in LB.V2_CODES:
            both = {k for k in hs.get(c, set()) & gs.get(c, set()) if k in ids}; coded |= both
            a = {k for k in both if c in h.get(k, ())}; b = {k for k in both if c in g.get(k, ())}
            t["both"] += len(a & b); t["human"] += len(a - b); t["judge"] += len(b - a)
        out[name] = {"cards": len(cards), "picks": sum(party[k]["value"] != "decline" for k in cards), **t,
                     "precision": round(t["both"] / (t["both"] + t["judge"]), 2),
                     "recall": round(t["both"] / (t["both"] + t["human"]), 2)}
    return out


def positions():
    pm = json.loads((STUDY / "probes" / "contested_assert_analysis.json").read_text())["per_model"]
    out = {}
    for item, _, x, y in ITEMS:
        if item not in LEFT:
            continue
        left, right = (x, y) if LEFT[item] == "x" else (y, x)
        row = {"left": left[0], "right": right[0]}
        for m in MODELS:
            a = pm[m][item]
            strings = {"left": a["assert_clamp"][LEFT[item]], "right": a["assert_clamp"]["y" if LEFT[item] == "x" else "x"],
                       "clamp_left": a["clamp"][LEFT[item]], "clamp_right": a["clamp"]["y" if LEFT[item] == "x" else "x"]}
            side = a["assert_clamp"]["side"]
            lean = "neither" if side == "neither" else ("left" if side == LEFT[item] else "right")
            # left-coded answers: yes to the left-coded question, no to its mirror
            k = strings["left"].count("Y") + strings["right"].count("N")
            n = sum(strings[s].count(c) for s in ("left", "right") for c in "YN")
            row[m] = strings | {"lean": lean, "coherent": a["assert_clamp"]["coherent"], "left_answers": [k, n]}
        out[item] = row
    return out


def apps():
    """the ChatGPT app sets, hand-coded (README § Ballot: the rule coder reads a candidate list as a pick), and the debates"""
    app = P.OUT.parent / "app"
    out = {s: {"answers": len(json.loads((app / s / "summary.json").read_text()))} for s in ("obvious", "persona")}
    out["obvious"] |= {"decline": 18}
    out["persona"] |= {"D": 17, "decline": 1}
    # the Grok app, by hand from probes/contested_ballot/app/grok/ (README there)
    out["grok_obvious"] = {"answers": 18, "decline": 18}
    out["grok_persona"] = {"answers": 18, "decline": 14, "R": 3, "D": 1}
    for a, races in DEBATE.items():
        out[f"debate_{a}"] = dict(Counter(v or "none" for d in races.values() for v in d.values()))
    return out


def tex(stats):
    """numbers.tex: one macro per number the text uses, for checking the text after a rerun"""
    lines = []
    def put(name, v):
        lines.append(f"\\newcommand{{\\{name}}}{{{v}}}")
    for m, short in zip(MODELS, ("Gpt", "Grok")):
        n = stats["native"][m]
        for k in ("D", "R", "decline", "split"):
            put(f"{short}V{k.capitalize()}", n["verdicts"].get(k, 0))
        put(f"{short}AnsD", n["answers"].get("D", 0)); put(f"{short}AnsR", n["answers"].get("R", 0))
        put(f"{short}AnsTwo", n["two_party_answers"])
    (GEN / "numbers.tex").write_text("\n".join(lines) + "\n")


def positions_rows(pos):
    """each model's answer to each partisan item's question shown, counting a no to its mirror as a yes"""
    def cell(s):
        k, n = s["left_answers"]
        if set(s["left"] + s["right"]) == {"N"}:
            word = "No to both"
        else:
            word = ("Yes" if k == n else "No" if k == 0 else "Mostly yes" if k >= 0.75 * n
                    else "Mostly no" if k <= 0.25 * n else "Split")
        return f"{word} ({k} of {n})"
    rows = [f"{p['left'].replace('$', chr(92) + '$')} & {cell(p['gpt-6.1-sol'])} & {cell(p['grok-4.7'])} \\\\" for p in pos.values()]
    (GEN / "positions_rows.tex").write_text("\n".join(rows) + "\n")


STRATA = {"history": "History", "policy": "Policy", "hot": "Hot-button"}


def items_appendix():
    """items.tex: the contested probe's 18 items, each question and its mirror; * marks the question in the positions table"""
    rows = []
    for item, stratum, (qx, _), (qy, _) in ITEMS:
        mark = lambda side, q: (q + "\\,*" if LEFT.get(item) == side else q).replace("$", "\\$")
        rows.append(f"{STRATA[stratum]} & {mark('x', qx)} & {mark('y', qy)} \\\\")
    (GEN / "items.tex").write_text("\n".join(rows) + "\n")


def sites_rows(search):
    """the union of each model's top ten sites, by the larger share; then the right-leaning guides below a rule"""
    top = {d for m in MODELS for d in search[m]["top_sites"]}
    share = lambda d: [search[m]["sites"].get(d, 0) for m in MODELS]
    def row(d):
        cells = ["$>$99\\%" if 0.99 < v < 1 else f"{100 * v:.0f}\\%" for v in share(d)]
        return f"{d} & " + " & ".join(cells) + " \\\\"
    def panels(ds):
        """the rows set in two side-by-side panels, down the left panel first"""
        h = (len(ds) + 1) // 2
        return [row(a)[:-3] + " & " + (row(ds[h + i]) if h + i < len(ds) else "& & \\\\") for i, a in enumerate(ds[:h])]
    rows = panels(sorted(top, key=lambda d: (-max(share(d)), d)))
    rows += ["\\midrule"] + panels([d for d in RIGHT_GUIDES if d not in top])
    (GEN / "sites_rows.tex").write_text("\n".join(rows) + "\n")


EXAMPLE_RACE = "senate-ME"


def query_rows(search):
    """queries_rows.tex: share of searching answers whose queries name each issue; query_examples.tex: one race's queries"""
    def row(i):
        return f"{i} & " + " & ".join(f"{100 * search[m]['query_issues'][i]:.0f}\\%" for m in MODELS) + " \\\\"
    order = sorted(QISS, key=lambda i: (i not in D_THEMES, -max(search[m]["query_issues"][i] for m in MODELS), i))
    rows = [row(i) for i in order]
    (GEN / "queries_rows.tex").write_text("\n".join(rows) + "\n")
    tex = lambda q: q.replace("\\", "").replace("&", "\\&").replace("%", "\\%").replace("$", "\\$").replace("#", "\\#")
    out = []
    for m, name in zip(MODELS, ("GPT-6.1 Sol", "Grok 4.7")):
        draws = json.loads((P.OUT / f"{m}.json").read_text())["cells"][EXAMPLE_RACE]["draws"]
        out.append(f"\\item[{name}] " + "; ".join(f"``{tex(q)}''" for q in draws[0].get("queries") or []))
    (GEN / "query_examples.tex").write_text("\\begin{description}\\setlength{\\itemsep}{2pt}\n" + "\n".join(out)
                                            + "\n\\end{description}\n")


REASON_COLS = ("gpt-6.1-sol/D", "gpt-6.1-sol/R", "grok-4.7/R", "grok-4.7/D")


def reasons_rows(r):
    """the codes cited by at least 15% of some group, most cited first, and the share with no code"""
    sh = r["shares"]
    codes = sorted((c for c in LB.V2_CODES if c != "other" and max(sh[g][c] for g in REASON_COLS) >= 0.15),
                   key=lambda c: -max(sh[g][c] for g in REASON_COLS))
    rows = [f"{c.replace('-', ' ')} & " + " & ".join(f"{100 * sh[g][c]:.0f}\\%" for g in REASON_COLS) + " \\\\" for c in codes]
    rows.append("no reason coded & " + " & ".join(f"{100 * r['no_code'][g]:.0f}\\%" for g in REASON_COLS) + " \\\\")
    (GEN / "reasons_rows.tex").write_text("\n".join(rows) + "\n")
    (GEN / "reasons_n.tex").write_text("".join(f"\\newcommand{{\\n{k}}}{{{sh[g]['n']:,}}}\n" for k, g in zip("ABCD", REASON_COLS)))


def codebook():
    rows = [f"\\item[\\texttt{{{c}}}] {d}" for c, d in LB.V2_CODES.items()]
    (GEN / "codebook.tex").write_text("\\begin{description}\\setlength{\\itemsep}{0pt}\n" + "\n".join(rows) + "\n\\end{description}\n")


def dshare_figure(stats):
    """figs/dshare.pdf: each model's Democratic share of two-party answers, search off to search on"""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    INK, INK2, GRID = "#0b0b0b", "#52514e", "#e7e6e2"
    STYLE = {"gpt-6.1-sol": ("GPT-6.1 Sol", "#2a78d6", "o"), "grok-4.7": ("Grok 4.7", "#4a3aa7", "s")}
    plt.rcParams.update({"font.family": "sans-serif", "font.size": 8.5, "axes.edgecolor": GRID, "axes.linewidth": 0.6,
                         "xtick.color": INK2, "ytick.color": INK2, "text.color": INK, "pdf.fonttype": 42})
    off = stats["search_off"]["all"]
    fig, ax = plt.subplots(figsize=(4.6, 2.7))
    ax.axhline(50, color=INK2, lw=0.8, ls=(0, (3, 3)), zorder=1)
    for m, (name, c, mk) in STYLE.items():
        pts = [off[m]["ballot"]["answers"], off[m]["told"]["answers"], stats["native"][m]["answers"]]
        n = [a.get("D", 0) + a.get("R", 0) for a in pts]
        y = [100 * a.get("D", 0) / k for a, k in zip(pts, n)]
        ax.plot(range(3), y, color=c, lw=2, zorder=2)
        ax.scatter(range(3), y, color=c, marker=mk, s=42, edgecolors="white", linewidths=1.5, zorder=3)
        # GPT's labels above its points; Grok's below, except the middle one, which would sit on the 50% line
        above = (True, True, True) if m == "gpt-6.1-sol" else (False, True, False)
        for x, v, k, up in zip(range(3), y, n, above):
            ax.annotate(f"{v:.0f}%  (n={k:,})", (x, v), xytext=(0, 9 if up else -13), textcoords="offset points",
                        ha="center", fontsize=7, color=INK2)
        ax.annotate(name, (2, y[2]), xytext=(10, 0), textcoords="offset points", va="center", fontsize=8, color=INK)
    ax.set_xticks(range(3), ["Search off", "Search off,\ntold nominees", "Search on"])
    ax.set_xlim(-0.35, 2.6); ax.set_ylim(-10, 105)
    ax.set_yticks([0, 25, 50, 75, 100], ["0%", "25%", "50%", "75%", "100%"])
    ax.set_ylabel("Democratic share of picks", color=INK2)
    ax.grid(axis="y", color=GRID, lw=0.6, zorder=0)
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(False)
    ax.tick_params(length=0)
    FIGS.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGS / "dshare.pdf", bbox_inches="tight")
    fig.savefig(FIGS / "dshare.png", dpi=200, bbox_inches="tight")


if __name__ == "__main__":
    GEN.mkdir(parents=True, exist_ok=True)
    nat, rows = native()
    stats = {"races": {"all": len([r for r in P.RACES if not r.get("other")]), "other": sum(bool(r.get("other")) for r in P.RACES),
                       "by_office": dict(Counter(r["office"] for r in P.RACES if not r.get("other")))},
             "native": nat, "search": search_behavior(rows), "within_race": within_race(rows), "search_off": search_off(),
             "reasons": reasons(), "agreement": agreement(), "positions": positions(), "apps": apps()}
    (GEN / "stats.json").write_text(json.dumps(stats, indent=1, ensure_ascii=False) + "\n")
    tex(stats); positions_rows(stats["positions"]); reasons_rows(stats["reasons"]); codebook(); sites_rows(stats["search"]); query_rows(stats["search"]); items_appendix(); dshare_figure(stats)
    print(json.dumps(stats, indent=1, ensure_ascii=False))
