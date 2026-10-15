"""probe_brand_checks.py — two reviewer checks on the taste paper (reviews of 2026-10-15).

placebo   Is DPO teaching a general move away from the obvious answer? Over each pipeline's stored log-probabilities
          (probe_brand_logprob.py, all 42 categories), the Named brand's share among the candidates under Recommend,
          minus its share under Name, and its change from SFT to DPO. Compared between the 26 categories where the
          panel's Picked brand differs from its Named brand and the 16 where the panel keeps it. A general aversion to
          the obvious answer would lower the Named brand in both; a taste for particular brands lowers it only in
          the 26.
baseline  Is the two-turn pick just a draw from the model's own list? Over panel two-turn replies whose turn-1 list
          names the model's own default brand, the share that pick it, against the share a uniform draw from the
          brands in that list would give (mean of 1 / brands listed), and against picking the first brand listed.

    ../../.venv/bin/python probe_brand_checks.py      # -> probes/brand_checks.json
"""
import json, math, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from probe_brand_logprob import boot  # noqa: E402

PIPES = ("olmo3-7b", "tulu3-8b", "olmo31-32b")


def share(lp, x):
    m = max(lp.values())
    z = sum(math.exp(v - m) for v in lp.values())
    return math.exp(lp[x] - m) / z


def placebo():
    out = {}
    for p in PIPES:
        d = json.loads((HERE / "probes" / "brand_logprob" / f"{p}.json").read_text())
        pn, S = d["panel"], d["stages"]
        res = {}
        for group, cats in (("flip", [c for c, b in pn.items() if b["pick"] != b["name"]]),
                            ("hold", [c for c, b in pn.items() if b["pick"] == b["name"]])):
            gap = lambda st, c: (share(S[st]["verbs"]["recommend"][c], pn[c]["name"])
                                 - share(S[st]["verbs"]["name"][c], pn[c]["name"]))
            res[group] = {"categories": len(cats),
                          "sft": boot([gap("sft", c) for c in cats]), "dpo": boot([gap("dpo", c) for c in cats]),
                          "sft_to_dpo": boot([gap("dpo", c) - gap("sft", c) for c in cats])}
        out[p] = res
        print(f"{p}: Named-brand share under Recommend minus under Name, SFT->DPO change: "
              f"flip {res['flip']['sft_to_dpo']['mean']:+.3f} {res['flip']['sft_to_dpo']['ci90']} (n {res['flip']['categories']})  "
              f"hold {res['hold']['sft_to_dpo']['mean']:+.3f} {res['hold']['sft_to_dpo']['ci90']} (n {res['hold']['categories']})")
    return out


def baseline():
    import brand_ladder as B
    pats, dflt = B.pools()[4], B.defaults()
    runs = picked = first = 0
    uniform = 0.0
    sizes = []
    for f in [f for r in ("brands-pick2-free", "brands-ext2-pick2-free") for f in sorted((HERE / B.RUNS[r]["dir"]).glob("*.json"))]:
        x = json.loads(f.read_text())
        if x["model"] in B.EXCLUDE:
            continue
        for sid, s in x["scenes"].items():
            c = sid.removesuffix("__pick")
            d = dflt.get(x["model"], {}).get(c)
            if c in B.GENERIC or not d:
                continue
            for r in s["runs"]:
                if not r or len(r) < 2 or any(t.get("error") or not (t.get("reply") or "").strip() for t in r[:2]):
                    continue
                pk = B.committed(c, r[1]["reply"])
                listed = list(dict.fromkeys(B.mentions(r[0]["reply"], pats[c])))
                if pk == B.NO_PICK or d not in listed:
                    continue
                runs += 1
                picked += pk == d
                first += listed[0] == d
                uniform += 1 / len(listed)
                sizes.append(len(listed))
    sizes.sort()
    out = {"replies": runs, "default_picked": picked / runs, "uniform_draw": uniform / runs,
           "default_listed_first": first / runs, "median_brands_listed": sizes[len(sizes) // 2]}
    print(f"two-turn replies whose list names the model's default ({runs}): default picked {out['default_picked']:.0%}; "
          f"a uniform draw from the list would give {out['uniform_draw']:.0%}; default listed first {out['default_listed_first']:.0%}; "
          f"median {out['median_brands_listed']} brands listed")
    return out


def main():
    out = {"placebo": placebo(), "baseline": baseline()}
    (HERE / "probes" / "brand_checks.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
