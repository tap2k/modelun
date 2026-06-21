"""
Diff the blind non-Claude lead syntheses against Claude's committed framing.

Each lead (gpt-5.4, gemini-3.1-pro) invented its own group NAMES, so we can't
match on labels. Instead we test, name-agnostically:
  1. Co-membership agreement — for every pair of models, do two taxonomies agree
     on whether they share a group? (pairwise clustering agreement; chance-free
     enough for a read.) Computed for each pair: claude/gpt, claude/gemini, gpt/gemini.
  2. Per-Claude-group overlap — for each Claude group, the best-matching group in
     each lead's taxonomy and the Jaccard overlap of members.
  3. The positive-family-trait answers, side by side (the bias we're checking).
  4. Quote integrity — every departure quote string-verified against the source .md.

    .venv/bin/python scout/synth_diff.py
"""

import re
import json
from pathlib import Path
from itertools import combinations

ROOT = Path(__file__).resolve().parent.parent
GROUPS = ROOT / "data" / "groups.json"
BENCH = ROOT / "data" / "benchmark"
SYNTH = ROOT / "reads" / "_synth"

LEADS = {
    "gpt-5.4": "openai__gpt-5.4",
    "gemini-3.1-pro": "google__gemini-3.1-pro-preview",
}
# §1 portraits / groups.json use this alias; reads use the file slug.
ALIASES = {"gpt-4o-mini-2024-07-18": "gpt-4o-mini", "gpt-4o-mini": "gpt-4o-mini-2024-07-18"}


def norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def claude_assignments():
    g = json.loads(GROUPS.read_text())["models"]
    return {k: v["primary"] for k, v in g.items()}


def lead_assignments(flat):
    f = SYNTH / f"{flat}.json"
    if not f.exists():
        return None, None
    d = json.loads(f.read_text())
    if "_error" in d:
        return None, d
    asg = {}
    # prefer explicit model_assignments; fall back to taxonomy members
    for m, grp in (d.get("model_assignments") or {}).items():
        asg[m] = grp
    for t in d.get("taxonomy", []):
        for m in t.get("models", []):
            asg.setdefault(m, t["group"])
    return asg, d


def unify_keys(asg, universe):
    """Map a lead's model keys onto the canonical groups.json slug set."""
    out = {}
    canon = {norm(u): u for u in universe}
    for m, grp in asg.items():
        key = canon.get(norm(m)) or canon.get(norm(ALIASES.get(m, ""))) or m
        out[key] = grp
    return out


def comembership_agreement(a, b):
    """Over models both taxonomies cover: fraction of model-pairs where they agree
    on same-group-or-not."""
    common = sorted(set(a) & set(b))
    if len(common) < 2:
        return None, 0
    agree = total = 0
    for x, y in combinations(common, 2):
        total += 1
        if (a[x] == a[y]) == (b[x] == b[y]):
            agree += 1
    return agree / total, len(common)


def group_overlaps(claude, lead):
    """For each Claude group, the lead group with the largest member overlap."""
    cgroups = {}
    for m, g in claude.items():
        cgroups.setdefault(g, set()).add(m)
    lgroups = {}
    for m, g in lead.items():
        lgroups.setdefault(g, set()).add(m)
    rows = []
    for cg, cmembers in cgroups.items():
        cm = cmembers & set(lead)  # only models the lead also placed
        best, best_j, best_inter = None, 0.0, set()
        for lg, lmembers in lgroups.items():
            inter = cm & lmembers
            union = cm | lmembers
            j = len(inter) / len(union) if union else 0
            if j > best_j:
                best, best_j, best_inter = lg, j, inter
        rows.append((cg, len(cm), best, round(best_j, 2), sorted(best_inter)))
    return rows


def verify_quotes():
    """String-check every departure quote in every read against its source .md."""
    def normq(s):
        s = re.sub(r"[‘’“”]", lambda m: {"‘": "'", "’": "'", "“": '"', "”": '"'}[m.group()], s or "")
        return re.sub(r"\s+", " ", s).strip().lower()

    results = {}
    for label, flat in LEADS.items():
        rdir = ROOT / "reads" / flat
        if not rdir.exists():
            continue
        ok = bad = 0
        misses = []
        for f in sorted(rdir.glob("*.json")):
            d = json.loads(f.read_text())
            slug = d.get("_subject_file", "")
            src = BENCH / f"scout_{f.stem}.md"
            if not src.exists():
                continue
            hay = normq(src.read_text())
            for dep in d.get("departures", []):
                q = normq(dep.get("quote", ""))
                if not q:
                    continue
                if q in hay:
                    ok += 1
                else:
                    bad += 1
                    misses.append(f"{f.stem}: {dep.get('quote','')[:70]}")
        results[label] = {"verified": ok, "failed": bad, "misses": misses[:12]}
    return results


def main():
    claude = claude_assignments()
    universe = set(claude)
    leads = {}
    for label, flat in LEADS.items():
        asg, raw = lead_assignments(flat)
        if asg is None:
            print(f"[skip] {label}: {raw.get('_error') if raw else 'no synth file'}")
            continue
        leads[label] = (unify_keys(asg, universe), raw)

    print("=" * 70)
    print("1. CO-MEMBERSHIP AGREEMENT (name-agnostic clustering agreement)")
    print("=" * 70)
    allmaps = {"claude": claude, **{k: v[0] for k, v in leads.items()}}
    for x, y in combinations(allmaps, 2):
        frac, n = comembership_agreement(allmaps[x], allmaps[y])
        if frac is not None:
            print(f"  {x:14s} vs {y:14s}: {frac:.0%} of {n*(n-1)//2} model-pairs agree  (n={n} common models)")

    for label, (asg, raw) in leads.items():
        print("\n" + "=" * 70)
        print(f"2. PER-CLAUDE-GROUP OVERLAP  —  claude vs {label}")
        print("=" * 70)
        for cg, n, best, j, inter in sorted(group_overlaps(claude, asg), key=lambda r: -r[1]):
            print(f"  Claude '{cg}' ({n} models) -> best match '{best}'  Jaccard={j}")
            if inter:
                print(f"      shared: {', '.join(inter)}")
        print(f"\n  {label} TAXONOMY (its own names):")
        for t in raw.get("taxonomy", []):
            print(f"    - {t['group']}: {', '.join(t.get('models', []))}")
        pf = raw.get("positive_family_trait", {})
        print(f"\n  {label} POSITIVE-FAMILY-TRAIT verdict:")
        print(f"    found={pf.get('found')}  family={pf.get('family')}  trait={pf.get('trait')}")
        if pf.get("neutral_framing"):
            print(f"    neutral:  {pf.get('neutral_framing')}")
        if pf.get("skeptic_framing"):
            print(f"    skeptic:  {pf.get('skeptic_framing')}")
        if raw.get("notes"):
            print(f"    notes: {raw['notes']}")

    print("\n" + "=" * 70)
    print("3. QUOTE INTEGRITY (string-verified vs source transcripts)")
    print("=" * 70)
    for label, v in verify_quotes().items():
        print(f"  {label}: {v['verified']} verified, {v['failed']} failed")
        for m in v["misses"]:
            print(f"      MISS {m}")


if __name__ == "__main__":
    main()
