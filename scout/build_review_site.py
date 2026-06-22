"""
Build the lightweight review site: site/data.js (+ a copy of the marker grid).

Bundles every transcript with its marker layer and the bottom-up analyses layered on
top — the 3-reader cross-check reads and the per-model card — plus the synthesis and
catchphrase report. Personal review tool: after running this, open site/index.html
directly in a browser (no server, no build deps).

    python scout/build_review_site.py
"""

import re
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


def clean_card(text):
    """Strip v4.1 scaffolding from a card: dead source link, internal stability jargon,
    and the never-filled HUMAN template. Keep the measured reflexes + the LLM read."""
    out = []
    for ln in text.splitlines():
        if ln.startswith("## HUMAN"):
            break  # drop the human-fill template (and its <!-- --> placeholders)
        if ln.startswith("_subject:") or ln.startswith("_between-run wander:"):
            continue  # dead scout_*.md link / internal stability metric
        out.append(ln)
    txt = "\n".join(out).rstrip()
    txt = re.sub(r"^## JUDGE-DRAFTED READ.*$", "## Read  *(LLM-drafted from the transcript)*",
                 txt, flags=re.M)
    return txt


def main():
    reg = json.loads((ROOT / "registers.json").read_text())
    active = {s["id"]: {"register": r["name"],
                        "dimension": s.get("dimension") or r.get("dimension"),
                        "marker": s.get("marker"), "turns": s.get("turns", [])}
              for r in reg["registers"] for s in r["scenes"]}
    markers = json.loads((BENCH / "markers.json").read_text())
    mk_models = markers["models"]
    readers = sorted(d for d in XCHECK.iterdir() if d.is_dir() and "__" in d.name) if XCHECK.exists() else []
    fam_of = {lab: fam for fam, labs in FAMILIES for lab in labs}

    models, sample = {}, None
    for p in sorted(b for b in BENCH.glob("*.json") if b.name != "markers.json"):
        d = json.loads(p.read_text())
        m = d["model"]
        scenes = {sid: {"register": sc.get("register", ""), "subtitle": sc.get("subtitle", sid),
                        "active": sid in active, "marker": active.get(sid, {}).get("marker"),
                        "dimension": active.get(sid, {}).get("dimension"),
                        "runs": [[{"u": pn["u"], "reply": pn.get("reply")} for pn in run]
                                 for run in sc["runs"]]}
                  for sid, sc in d["scenes"].items()}
        if sample is None:
            sample = scenes
        reads = {}
        for rd in readers:
            f = rd / f"{m}.json"
            if f.exists():
                try:
                    rj = json.loads(f.read_text())
                    if "_error" not in rj:  # skip stubs where the reader failed on this subject
                        reads[rd.name] = rj
                except json.JSONDecodeError:
                    pass
        card = CARDS / f"{m}.md"
        models[m] = {"slug": d.get("slug", ""), "family": fam_of.get(m, "Other"),
                     "scenes": scenes, "markers": mk_models.get(m, {}), "reads": reads,
                     "card": clean_card(card.read_text()) if card.exists() else None}

    # flat list of all scenes (active first, then archived), with the 4 user turns
    def turns_of(sid, sc):
        return active.get(sid, {}).get("turns") or [p["u"] for p in sc["runs"][0]]
    scene_list = [{"id": sid, "register": active[sid]["register"], "subtitle": sample[sid]["subtitle"],
                   "marker": active[sid]["marker"], "dimension": active[sid]["dimension"],
                   "active": True, "turns": active[sid]["turns"] or turns_of(sid, sample[sid])}
                  for sid in active if sid in sample]
    scene_list += [{"id": sid, "register": sc.get("register", ""), "subtitle": sc["subtitle"],
                    "marker": None, "dimension": None, "active": False, "turns": turns_of(sid, sc)}
                   for sid, sc in sample.items() if sid not in active]

    cat = ROOT / "archive" / "v4.1" / "catchphrases.md"
    blob = {
        "families": [[fam, [l for l in labs if l in models]] for fam, labs in FAMILIES],
        "cols": COLS, "short": SHORT, "verdictColors": VERDICT, "cat": {k: list(v) for k, v in CAT.items()},
        "readerLabels": {rd.name: rd.name.split("__")[0] for rd in readers},
        "models": models, "scenes": scene_list,
        "synthesis": (ROOT / "docs" / "houses.md").read_text(),
        "catchphrases": cat.read_text() if cat.exists() else "",
    }
    SITE.mkdir(exist_ok=True)
    (SITE / "data.js").write_text("window.ATLAS = " + json.dumps(blob, ensure_ascii=False) + ";\n")
    grid = ROOT / "reads" / "markers_grid.png"
    if grid.exists():
        shutil.copy(grid, SITE / "markers_grid.png")
    print(f"wrote {SITE / 'data.js'}  ({len(models)} models, {len(readers)} cross-check readers, "
          f"{len(scene_list)} scenes)")
    print(f"open {SITE / 'index.html'} in a browser")


if __name__ == "__main__":
    main()
