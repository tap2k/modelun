"""
Build the browsable-site data blob from the repo's frozen markdown.

Parses every `data/benchmark/scout_<slug>.md` transcript (rigid grammar:
`# Atlas scout — <label>  (<route>)`, `## <scene>`, `### run N`, `**U1:**` user
lines, `**<label>:**` then `> ` blockquote reply), plus the essay's bestiary
grouping and the synthesis §1 differential portrait, and emits one JSON file the
Astro site renders. This IS the "compile dynamically from data in the repo" step
— rerun it whenever data/ or the docs change.

    .venv/bin/python scout/build_site_data.py            # -> site/src/data/atlas.json
    .venv/bin/python scout/build_site_data.py --check    # parse + validate, write nothing

Output is a build artifact (gitignored); data/ + the docs are the source of truth.
"""

import re
import sys
import json
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BENCH = ROOT / "data" / "benchmark"
ESSAY = ROOT / "docs" / "essay.md"
SYNTH = ROOT / "docs" / "method" / "synthesis.md"
GROUPS = ROOT / "data" / "groups.json"
REGISTERS = ROOT / "registers.json"

# §1 portraits key models by display name; map the few that differ from the file slug.
PORTRAIT_ALIASES = {"gpt-4o-mini": "gpt-4o-mini-2024-07-18"}
OUT = ROOT / "site" / "src" / "data" / "atlas.json"

# ── transcript parsing ───────────────────────────────────────────────────────
HEADER_RE = re.compile(r"^#\s+Atlas scout\s+[—-]\s+(?P<label>.+?)\s+\((?P<route>[^)]+)\)")
SCENE_RE = re.compile(r"^##\s+(?P<title>.+?)\s*$")
RUN_RE = re.compile(r"^###\s+run\s+(?P<n>\d+)")
USER_RE = re.compile(r"^\*\*U(?P<n>\d+):\*\*\s*(?P<text>.*)$")


def parse_transcript(path):
    """One scout_<slug>.md -> {slug, label, route, scenes:[{title, runs:[{idx, turns:[{user, reply}]}]}]}."""
    lines = path.read_text().splitlines()
    label = route = None
    scenes = []
    scene = run = None
    pending_user = None          # text of the user turn whose reply we're collecting
    reply_lines = None           # accumulating blockquote lines for the current reply
    expect_reply = False         # saw `**label:**`, next blockquote block is the reply

    def flush_reply():
        nonlocal reply_lines, pending_user
        if pending_user is not None and run is not None:
            reply = "\n".join(reply_lines).strip() if reply_lines else ""
            run["turns"].append({"user": pending_user, "reply": reply})
        pending_user, reply_lines = None, None

    for ln in lines:
        m = HEADER_RE.match(ln)
        if m:
            label, route = m.group("label").strip(), m.group("route").strip()
            continue
        m = SCENE_RE.match(ln)
        if m and not ln.startswith("###"):
            flush_reply()
            scene = {"title": m.group("title").strip(), "runs": []}
            scenes.append(scene)
            run = None
            continue
        m = RUN_RE.match(ln)
        if m:
            flush_reply()
            run = {"idx": int(m.group("n")), "turns": []}
            scene["runs"].append(run)
            continue
        m = USER_RE.match(ln)
        if m:
            flush_reply()
            pending_user = m.group("text").strip()
            expect_reply = False
            reply_lines = None
            continue
        # the model-label line: `**<something>:**` that isn't a U-turn
        if re.match(r"^\*\*[^*]+:\*\*\s*$", ln) and not USER_RE.match(ln):
            expect_reply = True
            reply_lines = []
            continue
        if expect_reply and ln.startswith(">"):
            reply_lines.append(re.sub(r"^>\s?", "", ln))
            continue
        # blank line inside a reply block: keep collecting (handles multi-para blockquotes)

    flush_reply()
    return {
        "slug": path.stem.replace("scout_", ""),
        "label": label,
        "route": route,
        "scenes": scenes,
    }


# ── bestiary group per model (authoritative manifest) ────────────────────────
def load_groups():
    """data/groups.json -> {group_defs, per-model {primary, secondary?, note?}}."""
    g = json.loads(GROUPS.read_text())
    return g.get("groups", {}), g.get("models", {})


# ── synthesis §1: distinctive line + signature per model ─────────────────────
def parse_synthesis_portraits(slug_set):
    txt = SYNTH.read_text()
    # isolate section 1
    m = re.search(r"^##\s+1\.\s+The atlas.*?(?=^##\s+2\.)", txt, re.S | re.M)
    sec = m.group(0) if m else txt
    portraits = {}
    # entries: **<slug-or-name>** — *<distinctive>* ... up to next ** entry or ###
    for block in re.split(r"\n(?=\*\*[^*]+\*\*\s+—)", sec):
        bm = re.match(r"\*\*(?P<name>[^*]+?)(?:\s+\(evo\))?\*\*\s+—\s+\*(?P<distinctive>.+?)\*", block, re.S)
        if not bm:
            continue
        name = bm.group("name").strip()
        slug = name if name in slug_set else PORTRAIT_ALIASES.get(name)
        if slug is None or slug not in slug_set:
            continue
        # all quoted spans in the block, in order: *"<quote>"*
        quoted = [re.sub(r"\s+", " ", q).strip()
                  for q in re.findall(r'\*"([^"]+?)"\*', block, re.S)]
        # prefer the quote that follows a `signature:` marker; else the first quote.
        sig = None
        sm = re.search(r"\*signature:\*.*?\*\"([^\"]+?)\"\*", block, re.S)
        if sm:
            sig = re.sub(r"\s+", " ", sm.group(1)).strip()
        elif quoted:
            sig = quoted[0]
        portraits[slug] = {
            "distinctive": re.sub(r"\s+", " ", bm.group("distinctive")).strip(),
            "signature": sig,
        }
    return portraits



def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="parse + validate, write nothing")
    args = ap.parse_args()

    files = sorted(BENCH.glob("scout_*.md"))
    models = [parse_transcript(f) for f in files]
    slug_set = {m["slug"] for m in models}

    group_defs, group_map = load_groups()
    portraits = parse_synthesis_portraits(slug_set)

    # validate uniform shape + coverage
    problems = []
    for m in models:
        ns = len(m["scenes"])
        nturns = sum(len(r["turns"]) for s in m["scenes"] for r in s["runs"])
        if ns != 9 or nturns != 72:
            problems.append(f"{m['slug']}: scenes={ns} turns={nturns} (expected 9 / 72)")
        if not m["route"]:
            problems.append(f"{m['slug']}: missing route header")
        if m["slug"] not in group_map:
            problems.append(f"{m['slug']}: no entry in data/groups.json")
        if m["slug"] not in portraits:
            problems.append(f"{m['slug']}: no §1 portrait matched")
        m["group"] = group_map.get(m["slug"])
        m["portrait"] = portraits.get(m["slug"])

    registers = json.loads(REGISTERS.read_text())
    blob = {
        "script_version": registers.get("script_version"),
        "system_prompt": registers.get("system_prompt"),
        "n_models": len(models),
        "group_defs": group_defs,
        "models": models,
    }

    print(f"parsed {len(models)} models | grouped: {len(group_map)} | "
          f"portraits matched: {len(portraits)}")
    if problems:
        print("VALIDATION PROBLEMS:")
        for p in problems:
            print("  " + p)
    else:
        print("validation: all 38 models — 9 scenes / 72 turns, route + group + portrait present ✓")

    if args.check:
        return
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(blob, indent=1))
    print(f"-> {OUT.relative_to(ROOT)}  ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
