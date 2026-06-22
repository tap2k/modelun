"""
Render a per-model JSON transcript into a readable view.

JSON is the source of truth (data/benchmark/<model>.json); this produces the
human/judge-facing text. Used by run_markers.py to feed the judge, and as a CLI
to read a transcript by eye.

    python scout/render.py claude-opus-4.8           # print one model
    python scout/render.py --all --out reads/transcripts   # write every model's view
"""

import json
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BENCH = ROOT / "data" / "benchmark"


def _quote(text):
    if text is None:
        return "> [no reply]"
    return "\n".join("> " + ln if ln else ">" for ln in text.split("\n"))


def render_model(data, scene_ids=None):
    """JSON transcript -> readable markdown string (scene headers + escalating panels).

    scene_ids: if given, render only those scene ids (e.g. the active instrument scenes),
    skipping any scene that isn't in the active instrument. Default renders everything."""
    out = [f"# {data['model']}  ({data.get('slug', '')})",
           f"_script_version: {data.get('script_version', '?')} · temp: {data.get('temperature', '?')}_\n"]
    for sid, sc in data["scenes"].items():
        if scene_ids is not None and sid not in scene_ids:
            continue
        head = f"{sc.get('register', '')} · {sc.get('subtitle', sid)}".strip(" ·")
        out.append(f"\n## {head}  [{sid}]" + (f"  _({sc['run_date']})_" if sc.get("run_date") else "") + "\n")
        for i, run in enumerate(sc["runs"]):
            out.append(f"\n### run {i}\n")
            for panel in run:
                out.append(f"\n**U:** {panel['u']}\n\n{_quote(panel.get('reply'))}\n")
    return "\n".join(out)


def load(model):
    p = model if str(model).endswith(".json") else BENCH / f"{model}.json"
    return json.loads(Path(p).read_text())


def main():
    ap = argparse.ArgumentParser(description="Render a per-model JSON transcript to readable text.")
    ap.add_argument("model", nargs="?", help="model label or path to <model>.json")
    ap.add_argument("--all", action="store_true", help="render every model in data/benchmark")
    ap.add_argument("--out", default=None, help="write to <dir>/<model>.md instead of stdout")
    args = ap.parse_args()

    targets = sorted(p.stem for p in BENCH.glob("*.json") if p.name != "markers.json") if args.all else [args.model]
    if not targets or targets == [None]:
        ap.error("give a model label or --all")
    out_dir = Path(args.out) if args.out else None
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)
    for m in targets:
        text = render_model(load(m))
        if out_dir:
            (out_dir / f"{m}.md").write_text(text + "\n")
        else:
            print(text)


if __name__ == "__main__":
    main()
