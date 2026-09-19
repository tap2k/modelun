#!/usr/bin/env python3
"""Build the public conduct data viewer: scenes and their prompts, every transcript, and the codes
the LLM coders applied under codebook v2.

    python harness/build_conduct_viewer.py --out ../convovo-site/public/conduct

Writes index.json (scenes, codebook, model list), models/<slug>.json (one per model, transcripts
with labels) and copies the page. Labels come from data/coding/relabel_v2*.llm-*.jsonl: consensus
is presence in at least three of six coders; the viewer shows the count and one coder's quote.
"""
import argparse, collections, json, re, shutil, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "viewer"))
from arcs import load_arcs  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
STUDY = ROOT / "studies" / "conduct"
CODING = STUDY / "data" / "coding"
SIMPLE = CODING / "codebook" / "CODES-v2-SIMPLE-2026-09-15.md"


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
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="output directory (served statically)")
    a = ap.parse_args()
    out = Path(a.out).expanduser().resolve()
    (out / "models").mkdir(parents=True, exist_ok=True)

    arcs, reveal = load_arcs(STUDY, specimens=True)
    lab = labels()
    codes, positions = parse_codebook()

    scenes, per_model = {}, collections.defaultdict(list)
    for arc in arcs:
        model = reveal[arc["blind"]]
        sc = arc["scene"]
        scenes.setdefault(sc, {"scene": sc, "subtitle": arc.get("subtitle", ""),
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

    index = {"generated": "2026-09-19", "codebook": "v2", "codes": codes, "positions": positions,
             "scenes": [scenes[s] for s in sorted(scenes)],
             "models": []}
    for model, rows in sorted(per_model.items()):
        rows.sort(key=lambda r: (r["scene"], r["run"]))
        slug = re.sub(r"[^a-z0-9._-]+", "-", model.lower())
        (out / "models" / f"{slug}.json").write_text(json.dumps({"model": model, "arcs": rows}, ensure_ascii=False))
        CORE = ("facts", "doctors_note", "bad_plan")
        folds = [r for r in rows if r["trajectory"] and r["scene"] in CORE]
        index["models"].append({
            "model": model, "slug": slug, "vendor": vendors.get(model, "other"),
            "panel": model in panel, "arcs": len(rows), "coded": len(folds),
            "fold_rate": round(sum(1 for r in folds if r["trajectory"] == "FOLDED") / len(folds), 2) if folds else None,
        })
    (out / "index.json").write_text(json.dumps(index, ensure_ascii=False))

    page = Path(__file__).parent / "viewer" / "public_viewer.html"
    if page.exists():
        shutil.copy(page, out / "index.html")
    print(f"{len(index['models'])} models, {sum(m['arcs'] for m in index['models'])} transcripts, "
          f"{len(index['scenes'])} scenes -> {out}")


if __name__ == "__main__":
    main()
