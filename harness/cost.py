#!/usr/bin/env python3
"""What one model costs to run, per study.

The recurring decision is per model: a release appears, and the question is what
it costs to put it through the battery. So the unit here is one model, and any
panel figure is that number summed.

A study's token requirement is a property of the study, not something to
recompute per run. The stimulus is frozen, so its prompt tokens are fixed; reply
length varies by model, so the completion figure is a measured median. Both live
in ``studies/<name>/spec/tokens.json``, written by ``--measure`` and read by
everything else. Re-measure when ``script_version`` bumps, and not otherwise.

    python3 harness/cost.py --measure                  # (re)write every tokens.json
    python3 harness/cost.py openai/gpt-6-astra         # one model, whole battery
    python3 harness/cost.py --panel consensus --top 15
    python3 harness/cost.py --study conduct --panel conduct
"""

import argparse
import datetime as dt
import json
import statistics
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from study import Study  # noqa: E402

CATALOG_URL = "https://openrouter.ai/api/v1/models"
REPO = Path(__file__).resolve().parent.parent

# The battery is whatever each study's spec/runs.json marks ``tier: core`` or
# ``extended`` (``Study.standing``). A study without that file is not in the
# battery, so enrolling one stays a decision someone writes down. Directories
# owed only by hybrids (the off arms) are left out of the price; a hybrid runs
# them too, at about the served cost again.
def studies() -> dict[str, list[dict]]:
    """Study -> its standing entries owed by every panel model."""
    out = {}
    for f in sorted((REPO / "studies").glob("*/spec/runs.json")):
        runs = [e for e in Study(f.parent.parent).standing()[0] if e["owed_by"] == "panel"]
        if runs:
            out[f.parent.parent.name] = runs
    return out


def stimulus_version(study: str) -> str | None:
    """The study's frozen-stimulus version, or None if it does not carry one.

    A study with no single stimulus.json (language keeps one spec per language)
    cannot be staleness-checked this way, so it returns None and is trusted.
    """
    f = REPO / "studies" / study / "spec" / "stimulus.json"
    if not f.exists():
        return None
    d = json.loads(f.read_text())
    return d.get("script_version") or d.get("spec_version")


def fetch_catalog() -> dict:
    with urllib.request.urlopen(CATALOG_URL, timeout=60) as r:
        return {m["id"]: m for m in json.loads(r.read())["data"]}


def price(entry: dict) -> tuple[float, float]:
    p = entry.get("pricing", {})
    return float(p.get("prompt") or 0), float(p.get("completion") or 0)


def tokens_path(study: str) -> Path:
    return REPO / "studies" / study / "spec" / "tokens.json"


# ---------------------------------------------------------------- measuring

def system_prompt_chars(study: str, spec: str) -> int:
    f = REPO / "studies" / study / spec
    if f.suffix == ".json" and f.exists():
        return len(json.loads(f.read_text()).get("system_prompt") or "")
    return 0


def measure_one(path: Path, system_chars: int, cpt: float) -> tuple[float, float]:
    """(prompt, completion) tokens for one model's full run of a study.

    A turn resends the conversation so far, so an n-turn scene is charged the
    running prefix summed over its turns, not the scene length once.
    """
    doc = json.loads(path.read_text())
    scenes = doc.get("scenes", {})
    scenes = scenes.values() if isinstance(scenes, dict) else scenes
    prompt = completion = 0
    for scene in scenes:
        for run in scene.get("runs", []):
            prefix = system_chars
            for turn in run:
                prefix += len(turn.get("u", ""))
                prompt += prefix
                reply = len(turn.get("reply") or "")
                completion += reply
                prefix += reply
    return prompt / cpt, completion / cpt


def measure(cpt: float, names: list[str]) -> None:
    """Sum, over a study's standing directories, the median model's tokens in each.

    A directory whose files are not Contract A transcripts (a probe's own format)
    measures as zero; it is named in the file as not priced rather than counted
    as free.
    """
    found = studies()
    for study in names:
        pt = ct = lo = hi = 0.0
        priced, unpriced, n = [], [], 0
        for e in found[study]:
            files = sorted((REPO / "studies" / study / e["dir"]).glob("*.json"))
            sysc = system_prompt_chars(study, e["spec"])
            m = [s for s in (measure_one(f, sysc, cpt) for f in files) if s[0] > 0 and s[1] > 0]
            if not m:
                unpriced.append(e["dir"])
                continue
            pt += statistics.median(s[0] for s in m)
            ct += statistics.median(s[1] for s in m)
            lo += min(s[1] for s in m)
            hi += max(s[1] for s in m)
            priced.append(e["dir"])
            n = max(n, len(m))
        if not priced:
            print(f"{study}: no standing directory holds Contract A transcripts, "
                  f"not written", file=sys.stderr)
            continue
        out = {
            "note": "Token cost of one model through this study's standing directories "
                    "(spec/runs.json, tier core or extended, served arm). Prompt is fixed "
                    "by the frozen stimulus; completion is the median observed reply "
                    "length per directory, summed. Re-measure when the stimulus version "
                    "bumps or a standing directory is added.",
            "stimulus_version": stimulus_version(study),
            "prompt_tokens": round(pt),
            "completion_tokens": round(ct),
            "completion_spread": [round(lo), round(hi)],
            "priced": priced,
            "not_priced": unpriced,
            "measured": {"date": dt.date.today().isoformat(),
                         "models": n, "chars_per_token": cpt},
        }
        tokens_path(study).write_text(json.dumps(out, indent=1) + "\n")
        print(f"{study:16s} {out['prompt_tokens']:>8,}p {out['completion_tokens']:>7,}c"
              f"   {len(priced)} dirs priced, {len(unpriced)} not"
              f" -> {tokens_path(study).relative_to(REPO)}")


# ------------------------------------------------------------------ pricing

def load_shapes(names: list[str]) -> dict[str, tuple[int, int]]:
    """Stored token shapes, refusing any that no longer match the stimulus.

    A stale tokens.json is worse than a missing one: it prices a study that has
    since changed, silently and plausibly. So a version mismatch is an error
    telling you to re-measure, never a warning you can read past.
    """
    out, stale = {}, []
    for s in names:
        f = tokens_path(s)
        if not f.exists():
            print(f"{s}: no spec/tokens.json — run --measure", file=sys.stderr)
            continue
        d = json.loads(f.read_text())
        live = stimulus_version(s)
        if live is not None and d.get("stimulus_version") != live:
            stale.append(f"{s} (measured against {d.get('stimulus_version')!r}, "
                         f"stimulus is now {live!r})")
            continue
        out[s] = (d["prompt_tokens"], d["completion_tokens"])
    if stale:
        raise SystemExit("stale spec/tokens.json — re-run --measure for:\n  "
                         + "\n  ".join(stale))
    return out


def panel_slugs(name: str) -> list[str]:
    f = REPO / "studies" / name / "spec" / "models.txt"
    if not f.exists():
        raise SystemExit(f"no panel file at {f}")
    return [l.strip() for l in f.read_text().splitlines() if l.strip()]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("models", nargs="*", help="model slugs to price")
    ap.add_argument("--measure", action="store_true",
                    help="recompute spec/tokens.json from transcripts, then exit")
    ap.add_argument("--panel", help="price every model in this study's models.txt")
    ap.add_argument("--study", nargs="*", choices=sorted(studies()),
                    help="limit the battery to these studies")
    ap.add_argument("--top", type=int, help="show only the N most expensive")
    ap.add_argument("--chars-per-token", type=float, default=4.0)
    args = ap.parse_args()

    battery = args.study or sorted(studies())
    if args.measure:
        measure(args.chars_per_token, battery)
        return 0

    shp = load_shapes(battery)
    if not shp:
        return 1
    battery = [s for s in battery if s in shp]

    slugs = list(args.models) + (panel_slugs(args.panel) if args.panel else [])
    if not slugs:
        raise SystemExit("give model slugs, or --panel <study>, or --measure")

    catalog = fetch_catalog()
    print("battery, tokens per model (from each study's spec/tokens.json):")
    for s in battery:
        print(f"  {s:16s} {shp[s][0]:9,} prompt  {shp[s][1]:8,} completion")

    rows, missing = [], []
    for m in dict.fromkeys(slugs):
        e = catalog.get(m)
        if not e:
            missing.append(m)
            continue
        pr, co = price(e)
        per = {s: shp[s][0] * pr + shp[s][1] * co for s in battery}
        rows.append((sum(per.values()), m, per))
    rows.sort(reverse=True)

    shown = rows[:args.top] if args.top else rows
    head = "".join(f"{s[:9]:>10}" for s in battery)
    print(f"\n{'model':38s}{head}{'TOTAL':>10}")
    for total, m, per in shown:
        print(f"{m:38s}" + "".join(f"{per[s]:10.4f}" for s in battery) + f"{total:10.4f}")

    if rows:
        t = [r[0] for r in rows]
        print(f"\n{len(rows)} models priced"
              + (f", showing {len(shown)}" if args.top else "")
              + f"\n  one model: median ${statistics.median(t):.4f}, "
                f"mean ${statistics.mean(t):.4f}, max ${max(t):.4f}"
                f"\n  all of them, one sweep: ${sum(t):.2f}")
    if missing:
        print(f"\nnot in the catalog ({len(missing)}): {', '.join(sorted(missing))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
