"""
Build the lightweight review site: site/data.js (+ a copy of the marker grid).

Bundles every transcript with its marker layer and the bottom-up analyses layered on
top — the 3-reader cross-check reads and the per-model card — plus the synthesis and
catchphrase report. Personal review tool: after running this, open site/index.html
directly in a browser (no server, no build deps).

    python scout/build_review_site.py
"""

import sys
import json
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot_markers import FAMILIES, COLS, SHORT, VERDICT, CAT  # single source of order/colors

ROOT = Path(__file__).resolve().parent.parent
BENCH = ROOT / "data" / "benchmark"
XCHECK = ROOT / "archive" / "v4.1" / "cross-check"
CARDS = ROOT / "archive" / "v4.1" / "cards"
SITE = ROOT / "site"


def main():
    reg = json.loads((ROOT / "registers.json").read_text())
    active = {s["id"]: {"register": r["name"],
                        "dimension": s.get("dimension") or r.get("dimension"),
                        "marker": s.get("marker")}
              for r in reg["registers"] for s in r["scenes"]}
    markers = json.loads((BENCH / "markers.json").read_text())
    mk_models = markers["models"]
    # the 3 cross-check reader dirs are named "<vendor>__<model>"; skip essay-/synth-drafts
    readers = sorted(d for d in XCHECK.iterdir() if d.is_dir() and "__" in d.name) if XCHECK.exists() else []
    fam_of = {lab: fam for fam, labs in FAMILIES for lab in labs}

    models = {}
    for p in sorted(b for b in BENCH.glob("*.json") if b.name != "markers.json"):
        d = json.loads(p.read_text())
        m = d["model"]
        scenes = {sid: {"register": sc.get("register", ""), "subtitle": sc.get("subtitle", sid),
                        "active": sid in active, "marker": active.get(sid, {}).get("marker"),
                        "dimension": active.get(sid, {}).get("dimension"),
                        "runs": [[{"u": pn["u"], "reply": pn.get("reply")} for pn in run]
                                 for run in sc["runs"]]}
                  for sid, sc in d["scenes"].items()}
        reads = {}
        for rd in readers:
            f = rd / f"{m}.json"
            if f.exists():
                try:
                    reads[rd.name] = json.loads(f.read_text())
                except json.JSONDecodeError:
                    pass
        card = CARDS / f"{m}.md"
        models[m] = {"slug": d.get("slug", ""), "family": fam_of.get(m, "Other"),
                     "scenes": scenes, "markers": mk_models.get(m, {}), "reads": reads,
                     "card": card.read_text() if card.exists() else None}

    cat = ROOT / "archive" / "v4.1" / "catchphrases.md"
    blob = {
        "families": [[fam, [l for l in labs if l in models]] for fam, labs in FAMILIES],
        "active": active, "cols": COLS, "short": SHORT,
        "verdictColors": VERDICT, "cat": {k: list(v) for k, v in CAT.items()},
        "readerLabels": {rd.name: rd.name.split("__")[0] for rd in readers},
        "models": models,
        "synthesis": (ROOT / "docs" / "houses.md").read_text(),
        "scenesDoc": (ROOT / "docs" / "scenes.md").read_text(),
        "catchphrases": cat.read_text() if cat.exists() else "",
    }
    SITE.mkdir(exist_ok=True)
    (SITE / "data.js").write_text("window.ATLAS = " + json.dumps(blob, ensure_ascii=False) + ";\n")
    grid = ROOT / "reads" / "markers_grid.png"
    if grid.exists():
        shutil.copy(grid, SITE / "markers_grid.png")
    print(f"wrote {SITE / 'data.js'}  ({len(models)} models, {len(readers)} cross-check readers)")
    print(f"open {SITE / 'index.html'} in a browser")


if __name__ == "__main__":
    main()
