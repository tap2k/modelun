#!/usr/bin/env python3
"""Build the conduct study's review site: views/data.js.

    python studies/conduct/views/build.py && open studies/conduct/views/index.html

Per-model conduct measures (fold rate on the three coded scenes, manner signature against the
panel) joined to derived facts (lab, capability index, release date), every transcript, the scenes
that produced it, and codebook v2. Labels come from data/coding/relabel_v2*.llm-*.jsonl: a code is
present when at least three of the six coders marked it; the view shows the count and one quote.
"""
import argparse, collections, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "harness" / "viewer"))
from arcs import load_arcs  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
STUDY = Path(__file__).resolve().parents[1]
VIEWS = STUDY / "views"
CODING = STUDY / "data" / "coding"
SIMPLE = CODING / "codebook" / "CODES-v2-SIMPLE-2026-09-15.md"
XI = ROOT / "studies" / "cross-instrument"
CORE = ("facts", "doctors_note", "bad_plan")     # the scenes the codebook was built on
SECOND = ("boiling", "reference", "review", "exclude", "dropout", "lease")   # the preregistered second set
HOUSE = {"anthropic": "the coach who empathizes", "meta-llama": "the skeptic who caves",
         "openai": "straight to business", "google": "the self-conscious apologist",
         "x-ai": "the flat no"}


def capability():
    """-> model label -> {eci, date}, from the Epoch Capabilities Index file carried in the repo."""
    import csv
    names = {}
    for ln in (XI / "eci_map_2026-09-13.tsv").read_text().splitlines():
        if ln.startswith("#") or "\t" not in ln:
            continue
        ours, theirs = ln.split("\t")[:2]
        names[ours.strip()] = theirs.strip()
    rows = {r["Display name"]: r for r in csv.DictReader((XI / "eci_scores_2026-09-13.csv").open())}
    out = {}
    for ours, theirs in names.items():
        r = rows.get(theirs)
        if r and r.get("eci"):
            out[ours] = {"eci": round(float(r["eci"]), 1), "date": r.get("date", "")}
    # models the snapshot does not cover get a release date, with its source, from the study's own file
    for ln in (STUDY / "spec" / "release-dates.tsv").read_text().splitlines():
        if ln.startswith("#") or "\t" not in ln:
            continue
        m, d = [x.strip() for x in ln.split("\t")[:2]]
        out.setdefault(m, {"eci": None, "date": d})
    return out


def parse_codebook():
    """-> (codes [{code, what, example, side}], positions [{scene, position, held, folded}])."""
    text = SIMPLE.read_text()
    codes, positions, side = [], [], None
    for line in text.splitlines():
        if line.startswith("## If HELD"): side = "HELD"
        elif line.startswith("## If FOLDED"): side = "FOLDED"
        elif line.startswith("## "): side = None
        cells = [c.strip() for c in line.strip().strip("|").split("|")] if line.strip().startswith("|") else []
        if not cells or cells[0] in ("code", "scene") or set(cells[0]) <= set("-: "):
            continue
        if side and len(cells) == 3:
            codes.append({"code": cells[0], "what": cells[1], "example": cells[2].strip('"'), "side": side})
        elif not side and len(cells) == 4:
            positions.append({"scene": cells[0], "position": cells[1], "held": cells[2], "folded": cells[3]})
    return codes, positions


def labels():
    """-> arc id -> {trajectory: {code: n}, codes: {code: (n, quote)}, coders: n}."""
    out = collections.defaultdict(lambda: {"trajectory": collections.Counter(), "codes": {}, "coders": set()})
    for f in sorted(CODING.glob("relabel_v2*.llm-*.jsonl")):
        for line in f.open():
            if not line.strip():
                continue
            r = json.loads(line)
            a = out[r["arc"]]
            a["coders"].add(r["coder"])
            if r["kind"] == "trajectory":
                a["trajectory"][r["code"]] += 1
            elif r["kind"] == "code":
                n, q = a["codes"].get(r["code"], (0, ""))
                a["codes"][r["code"]] = (n + 1, q or (r.get("quote") or "").strip())
    return out


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()

    arcs, reveal = load_arcs(STUDY, specimens=True)
    arcs2, reveal2 = load_arcs(STUDY, bench=STUDY / "data" / "wave2")   # the second set, its own transcripts
    arcs, reveal = arcs + arcs2, {**reveal, **reveal2}
    stim2 = {sc["id"]: sc for reg in json.loads((STUDY / "spec" / "stimulus-v2.json").read_text())["registers"]
             for sc in reg["scenes"]}
    lab = labels()
    codes, positions = parse_codebook()

    scenes, per_model = {}, collections.defaultdict(list)
    for arc in arcs:
        model = reveal[arc["blind"]]
        sc = arc["scene"]
        scenes.setdefault(sc, {"scene": sc, "subtitle": arc.get("subtitle", ""),
                               "set": "second" if sc in SECOND else "first",
                               "position": stim2[sc]["ground_truth"] if sc in stim2 else "",
                               "prompts": [t["u"] for t in arc["turns"]]})
        L = lab.get(arc["id"])
        traj, marks = "", []
        if L:
            traj = L["trajectory"].most_common(1)[0][0] if L["trajectory"] else ""
            marks = sorted(({"code": c, "n": n, "quote": q} for c, (n, q) in L["codes"].items()),
                           key=lambda m: -m["n"])
        per_model[model].append({
            "scene": sc, "run": arc["run"], "trajectory": traj,
            "coders": len(L["coders"]) if L else 0,
            "codes": [m for m in marks if m["n"] >= 3],
            "minority": [m for m in marks if m["n"] < 3],
            "turns": [{"u": t["u"], "reply": t["reply"]} for t in arc["turns"]],
        })

    panel_file = STUDY / "spec" / "models.txt"
    panel = {ln.strip().split("/")[-1] for ln in panel_file.read_text().splitlines() if ln.strip() and not ln.startswith("#")}
    vendors = {}
    for p in sorted((STUDY / "data" / "benchmark").glob("*.json")):
        if p.name == "markers.json":
            continue
        d = json.loads(p.read_text())
        slug = d.get("slug", "") or ""
        if "/" in slug:
            vendors[d["model"]] = slug.split("/")[0]
        else:  # a few early transcripts stored a bare model id
            vendors[d["model"]] = "openai" if d["model"].startswith(("gpt-", "o1", "o3")) else "other"

    # panel means per code, on the scenes the codebook was built on
    cap = capability()
    panel_n = collections.Counter(); panel_c = collections.Counter()
    for model, rows in per_model.items():
        for r in rows:
            if r["scene"] in CORE and r["trajectory"]:
                panel_n[model] += 1
                for m in r["codes"]:
                    panel_c[m["code"]] += 1
    total = sum(panel_n.values())
    panel_mean = {c: n / total for c, n in panel_c.items()}

    index = {"generated": "2026-09-23", "codebook": "v2", "codes": codes, "positions": positions,
             "scenes": [scenes[s] for s in CORE + SECOND if s in scenes] + [scenes[s] for s in sorted(scenes) if s not in CORE + SECOND],
             "panel_mean": {c: round(v, 3) for c, v in sorted(panel_mean.items())},
             "houses": HOUSE, "models": []}
    for model, rows in sorted(per_model.items()):
        order = {s: i for i, s in enumerate(CORE + SECOND)}
        rows.sort(key=lambda r: (order.get(r["scene"], 99), r["scene"], r["run"]))
        slug = re.sub(r"[^a-z0-9._-]+", "-", model.lower())
        folds = [r for r in rows if r["trajectory"] and r["scene"] in CORE]
        folds2 = [r for r in rows if r["trajectory"] and r["scene"] in SECOND]
        rate = collections.Counter()
        for r in folds:
            for m in r["codes"]:
                rate[m["code"]] += 1
        rates = {c: n / len(folds) for c, n in rate.items()} if folds else {}
        sig = sorted(((c, v, v - panel_mean.get(c, 0)) for c, v in rates.items() if v >= 0.25),
                     key=lambda t: -t[2])[:3]
        index["models"].append({
            "model": model, "slug": slug, "vendor": vendors.get(model, "other"),
            "panel": model in panel, "arcs": len(rows), "coded": len(folds),
            "fold_rate": round(sum(1 for r in folds if r["trajectory"] == "FOLDED") / len(folds), 2) if folds else None,
            "fold_rate2": round(sum(1 for r in folds2 if r["trajectory"] == "FOLDED") / len(folds2), 2) if folds2 else None,
            "eci": cap.get(model, {}).get("eci"), "released": cap.get(model, {}).get("date", ""),
            "rates": {c: round(v, 2) for c, v in sorted(rates.items())},
            "signature": [{"code": c, "rate": round(v, 2), "dev": round(d, 2)} for c, v, d in sig],
        })
    blob = {"index": index, "models": {m["slug"]: {"model": m["model"], "arcs": per_model[m["model"]]}
                                       for m in index["models"]}}
    (VIEWS / "data.js").write_text("window.CONDUCT = " + json.dumps(blob, ensure_ascii=False) + ";\n")
    print(f"{len(index['models'])} models, {sum(m['arcs'] for m in index['models'])} transcripts, "
          f"{len(index['scenes'])} scenes -> {VIEWS / 'data.js'}")


if __name__ == "__main__":
    main()
