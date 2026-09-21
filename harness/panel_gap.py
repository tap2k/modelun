#!/usr/bin/env python3
"""Compare the study panels against the live OpenRouter catalog.

Three questions, in order of how much a wrong answer costs:

1. What is about to disappear? A model with an ``expiration_date``, or one
   already absent from the catalog, can never be run again. Transcripts for it
   are collectable now and never afterwards.
2. What is missing from a panel that another panel already has? Cross-study
   correlations are computed on the overlap, so a model in one panel and not
   another is a row the matrix cannot use.
3. What is new? Models in the catalog that no panel has seen.

Reads each ``studies/<name>/spec/models.txt``; no study semantics live here.

    python3 harness/panel_gap.py                    # all studies with a panel
    python3 harness/panel_gap.py --study conduct consensus
    python3 harness/panel_gap.py --new-since 2026-06-01
    python3 harness/panel_gap.py --json             # machine-readable
    python3 harness/panel_gap.py --snapshot          # also commit today's catalog
"""

import argparse
import datetime as dt
import json
import sys
import urllib.request
from pathlib import Path

CATALOG_URL = "https://openrouter.ai/api/v1/models"
REPO = Path(__file__).resolve().parent.parent


def fetch_catalog(cache: Path | None = None) -> dict:
    """Return {slug: entry}. A cache file makes runs reproducible and offline."""
    if cache and cache.exists():
        data = json.loads(cache.read_text())
    else:
        with urllib.request.urlopen(CATALOG_URL, timeout=60) as r:
            data = json.loads(r.read())
        if cache:
            cache.write_text(json.dumps(data))
    return {m["id"]: m for m in data["data"]}


def panels(names: list[str] | None) -> dict[str, set[str]]:
    out = {}
    for spec in sorted((REPO / "studies").glob("*/spec/models.txt")):
        study = spec.parent.parent.name
        if names and study not in names:
            continue
        out[study] = {l.strip() for l in spec.read_text().splitlines() if l.strip()}
    return out


def released(entry: dict) -> str:
    ts = entry.get("created")
    return dt.date.fromtimestamp(ts).isoformat() if ts else "?"


def snapshot(catalog: dict, out: Path) -> Path:
    """Write a dated, trimmed record of what the catalog held today.

    The live catalog is the only source for what exists, and it forgets: a
    delisted model leaves no trace that it was ever offered, at what price, or
    when it went. Committing one of these per survey gives the archive an
    "exists" side to sit beside the transcripts' "was run" side, and dates every
    disappearance. Descriptions are dropped so the file stays diffable.
    """
    rows = {
        slug: {
            "name": e.get("name"),
            "created": released(e),
            "expiration_date": e.get("expiration_date"),
            "context_length": e.get("context_length"),
            "prompt": e.get("pricing", {}).get("prompt"),
            "completion": e.get("pricing", {}).get("completion"),
        }
        for slug, e in sorted(catalog.items())
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(
        {"as_of": dt.date.today().isoformat(), "count": len(rows), "models": rows},
        indent=1) + "\n")
    return out


def is_variant(slug: str) -> bool:
    """Serving variants and moving aliases, which are not new subjects.

    ``:batch`` / ``:free`` / ``:nitro`` are the same weights on different
    delivery terms. A leading ``~`` marks a floating alias whose target changes
    under the label, which is the one thing a frozen panel must never hold.
    """
    return slug.startswith("~") or ":" in slug


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--study", nargs="*", help="limit to these studies")
    ap.add_argument("--new-since", metavar="YYYY-MM-DD",
                    help="only report unseen models created on or after this date")
    ap.add_argument("--cache", type=Path, help="read/write the catalog JSON here")
    ap.add_argument("--all-variants", action="store_true",
                    help="include :batch/:free serving variants and ~aliases")
    ap.add_argument("--snapshot", nargs="?", const="catalog", metavar="DIR",
                    help="also write catalog/<date>.json, a dated record of "
                         "what the catalog holds today")
    ap.add_argument("--json", action="store_true", dest="as_json")
    args = ap.parse_args()

    catalog = fetch_catalog(args.cache)
    if args.snapshot:
        f = snapshot(catalog, REPO / args.snapshot / f"{dt.date.today().isoformat()}.json")
        print(f"snapshot: {len(catalog)} models -> {f.relative_to(REPO)}")
    p = panels(args.study)
    if not p:
        print("no studies with spec/models.txt", file=sys.stderr)
        return 1
    union = set().union(*p.values())
    today = dt.date.today().isoformat()

    expiring = sorted(
        (catalog[m]["expiration_date"], m, sorted(s for s in p if m in p[s]))
        for m in union & set(catalog)
        if catalog[m].get("expiration_date")
    )
    vanished = sorted(
        (m, sorted(s for s in p if m in p[s])) for m in union - set(catalog)
    )
    # A model one panel has and another does not, restricted to models still
    # runnable: a vanished model cannot be backfilled, so listing it is noise.
    runnable = union & set(catalog)
    misaligned = {
        study: sorted(m for m in runnable - have if m not in vanished)
        for study, have in p.items()
    }
    unseen = sorted(
        (released(catalog[m]), m) for m in set(catalog) - union
        if (args.all_variants or not is_variant(m))
        and (not args.new_since or released(catalog[m]) >= args.new_since)
    )

    if args.as_json:
        print(json.dumps({
            "as_of": today,
            "catalog_size": len(catalog),
            "panels": {k: sorted(v) for k, v in p.items()},
            "expiring": [{"date": d, "model": m, "studies": s} for d, m, s in expiring],
            "vanished": [{"model": m, "studies": s} for m, s in vanished],
            "misaligned": misaligned,
            "unseen": [{"released": d, "model": m} for d, m in unseen],
        }, indent=1))
        return 0

    print(f"catalog {len(catalog)} models, as of {today}")
    for study, have in sorted(p.items()):
        print(f"  {study:16s} {len(have):3d} models")

    print(f"\n== EXPIRING: collect before the date or lose it ({len(expiring)}) ==")
    for d, m, studies in expiring:
        left = (dt.date.fromisoformat(d) - dt.date.today()).days
        print(f"  {d}  ({left:>4}d)  {m}   in: {', '.join(studies)}")
    if not expiring:
        print("  none")

    print(f"\n== GONE: absent from the catalog, unrunnable ({len(vanished)}) ==")
    for m, studies in vanished:
        print(f"  {m}   in: {', '.join(studies)}")
    if not vanished:
        print("  none")

    print("\n== MISALIGNED: still runnable, missing from this panel ==")
    for study, missing in sorted(misaligned.items()):
        print(f"  {study} is missing {len(missing)}:")
        for m in missing:
            exp = catalog[m].get("expiration_date")
            print(f"     {m}{'   EXPIRES ' + exp if exp else ''}")

    label = f" created >= {args.new_since}" if args.new_since else ""
    print(f"\n== UNSEEN: in the catalog, in no panel{label} ({len(unseen)}) ==")
    for d, m in unseen:
        print(f"  {d}  {m}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
