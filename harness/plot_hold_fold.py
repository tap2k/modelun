#!/usr/bin/env python3
"""Held-or-folded grid for every model on the three coded scenes, as a standalone SVG.

    python harness/plot_hold_fold.py --out ../convovo-site/public/images/conduct-hold-fold.svg

One row per model, grouped by vendor and ordered by how often it folds. Six cells per row: three
scenes, two runs each. Filled cell means the model gave its position up on that run.
"""
import argparse, collections, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STUDY = ROOT / "studies" / "conduct"
SCENES = [("facts", "arithmetic"), ("doctors_note", "the note"), ("bad_plan", "day-trader")]
VEND = {"anthropic": "Anthropic", "openai": "OpenAI", "google": "Google", "meta-llama": "Meta",
        "x-ai": "xAI", "deepseek": "DeepSeek", "qwen": "Qwen", "moonshotai": "Moonshot",
        "mistralai": "Mistral", "cohere": "Cohere"}


def load(data_js):
    """Read the study view's data blob (studies/conduct/views/data.js, built by views/build.py)."""
    blob = json.loads(Path(data_js).read_text().split("=", 1)[1].rstrip().rstrip(";"))
    idx, models = blob["index"], blob["models"]
    rows = []
    for m in idx["models"]:
        d = models[m["slug"]]
        cells = {}
        for a in d["arcs"]:
            if a["scene"] in dict(SCENES) and a["trajectory"]:
                cells[(a["scene"], a["run"])] = a["trajectory"]
        if cells:
            rows.append({"model": m["model"], "vendor": m["vendor"], "cells": cells,
                         "folds": sum(1 for v in cells.values() if v == "FOLDED") / len(cells)})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(STUDY / "views" / "data.js"), help="the view blob; run views/build.py first")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rows = load(a.data)

    by = collections.defaultdict(list)
    for r in rows:
        by[r["vendor"] if r["vendor"] in VEND else "other"].append(r)
    order = sorted(by, key=lambda v: (v == "other", sum(x["folds"] for x in by[v]) / len(by[v])))

    L, CELL, GAP, RH = 196, 22, 16, 21         # label width, cell, gap between scenes, row height
    W = L + 6 * CELL + 2 * GAP + 74
    head, y, out = 54, 0, []
    for v in order:
        y += 26 + RH * len(by[v])
    H = head + y + 26
    P = out.append
    P(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif">')
    P(f'<rect width="{W}" height="{H}" fill="none"/>')
    P(f'<style>text{{fill:#2b2a27}} .mut{{fill:#77746d}} @media (prefers-color-scheme: dark){{text{{fill:#e8e6e1}} .mut{{fill:#9a978f}}}}</style>')
    P(f'<text x="0" y="14" font-size="13" font-weight="650">Who gives the position up</text>')
    P(f'<text x="0" y="31" font-size="11.5" class="mut">Each row is a model, each cell one run. Filled means it folded.</text>')
    for i, (sid, label) in enumerate(SCENES):
        x = L + i * (2 * CELL + GAP)
        P(f'<text x="{x}" y="48" font-size="10.5" class="mut">{label}</text>')
    y = head
    for v in order:
        P(f'<text x="0" y="{y + 12}" font-size="11" class="mut" letter-spacing="0.6">{VEND.get(v, "Other vendors").upper()}</text>')
        y += 20
        for r in sorted(by[v], key=lambda x: (-x["folds"], x["model"])):
            name = r["model"] if len(r["model"]) <= 27 else r["model"][:26] + "\u2026"
            P(f'<text x="0" y="{y + 13}" font-size="11.5">{name}</text>')
            for i, (sid, _) in enumerate(SCENES):
                for run in (0, 1):
                    x = L + i * (2 * CELL + GAP) + run * CELL
                    t = r["cells"].get((sid, run))
                    fill = "#c0392b" if t == "FOLDED" else ("#e8e6e1" if t == "HELD" else "none")
                    op = "1" if t == "FOLDED" else "0.55"
                    P(f'<rect x="{x}" y="{y + 3}" width="{CELL - 3}" height="{CELL - 6}" rx="3" fill="{fill}" fill-opacity="{op}" stroke="#bdb9b1" stroke-width="0.7"/>')
            pct = round(100 * r["folds"])
            P(f'<text x="{L + 6 * CELL + 2 * GAP + 8}" y="{y + 13}" font-size="11" class="mut">{pct}%</text>')
            y += RH
        y += 6
    P(f'<text x="0" y="{H - 8}" font-size="11" class="mut">Sixty models, two runs per scene, codebook v2. Percentages are the share of the six runs the model folded.</text>')
    P('</svg>')
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text("\n".join(out))
    print(f"{len(rows)} models -> {a.out}")


if __name__ == "__main__":
    main()
