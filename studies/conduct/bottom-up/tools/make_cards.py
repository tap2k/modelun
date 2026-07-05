"""
make_cards — assemble a one-page "card" per model from a scout run.

A card has three tiers of trust, kept visually separate:

  MEASURED            — computed from the transcript, no judgment (tics, reflexes)
  JUDGE-DRAFTED       — a read drafted by an LLM that is NOT under test, and every
                        claim must cite a transcript quote. Marked UNVERIFIED.
  (HUMAN)             — blank slots for you to correct/confirm the read by eye.

The script NEVER writes the character read itself. The judge drafts it (cited),
you own it. This keeps the artifact honest to "read, not measured."

    export OPENROUTER_API_KEY=...   # or .env
    python scout/make_cards.py runs/v4.1-clamp --judge x-ai/grok-4.1

--judge is REQUIRED and has no default: you must choose the reader, and it must
not belong to a family under test (or you reintroduce the self-preference leak).
The script warns if the judge's vendor matches a subject in the run.
"""

import os
import re
import sys
import json
import argparse
import requests
from pathlib import Path
from collections import Counter

from dotenv import load_dotenv
import catchphrases  # reuse the tic finder (same dir)

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
API = "https://openrouter.ai/api/v1/chat/completions"

REPLY_RE = re.compile(r"^\*\*(?P<label>[^*]+):\*\*\s*$")
USER_RE = re.compile(r"^\*\*U(?P<n>\d+):\*\*\s*(?P<text>.*)$")


# ── transcript parsing ──────────────────────────────────────────────────────
def parse(md_path):
    """Return (label, panels) where panels is a list of dicts:
    {scene, run, panel, user, reply}."""
    label = md_path.stem.replace("scout_", "")
    scene = run = None
    panels, cur_user, cur_panel, buf, capturing = [], None, 0, [], False

    def flush_reply():
        if cur_user is not None and buf:
            panels.append({"scene": scene, "run": run, "panel": cur_panel,
                           "user": cur_user, "reply": "\n".join(buf).strip()})

    for line in md_path.read_text().splitlines():
        if line.startswith("## "):
            flush_reply(); buf = []; capturing = False
            scene = line[3:].strip(); cur_user = None; cur_panel = 0
        elif line.startswith("### run"):
            flush_reply(); buf = []; capturing = False
            run = line.split("run", 1)[1].strip(); cur_user = None; cur_panel = 0
        elif USER_RE.match(line):
            flush_reply(); buf = []; capturing = False
            m = USER_RE.match(line)
            cur_user, cur_panel = m.group("text").strip(), int(m.group("n"))
        elif REPLY_RE.match(line):
            capturing = REPLY_RE.match(line).group("label").strip() == label
            buf = []
        elif capturing and line.startswith(">"):
            buf.append(line.lstrip("> ").rstrip())
    flush_reply()
    return label, panels


# ── MEASURED layer ──────────────────────────────────────────────────────────
HEDGES = ("i think", "maybe", "perhaps", "it depends", "sort of", "kind of",
          "i'm not sure", "it might", "possibly", "in some ways")
HELP_OFFERS = ("if you want", "i can help", "i'd be happy to", "happy to help",
               "let me help", "i can also", "want me to", "i'll help")
AI_DISCLAIM = ("i'm an ai", "i am an ai", "as an ai", "i'm just an ai")


def reflexes(panels):
    n = len(panels) or 1
    replies = [p["reply"] for p in panels]
    low = [r.lower() for r in replies]
    ends_q = sum(1 for r in replies if r.rstrip().endswith("?"))
    hedge = sum(any(h in r for h in HEDGES) for r in low)
    helps = sum(any(h in r for h in HELP_OFFERS) for r in low)
    emoji = sum(1 for r in replies if re.search(r"[\U0001F300-\U0001FAFF☀-➿]", r))
    ai = sum(any(a in r for a in AI_DISCLAIM) for r in low)
    words = [len(r.split()) for r in replies]
    return {
        "replies": n,
        "avg_words": round(sum(words) / n),
        "ends_on_question_pct": round(100 * ends_q / n),
        "hedge_pct": round(100 * hedge / n),
        "offers_help_pct": round(100 * helps / n),
        "emoji_pct": round(100 * emoji / n),
        "ai_disclaimer_count": ai,
    }


def cohort_line(metric, val, cohort_vals):
    """Express a metric relative to the run's median — quirks are only legible vs the pack."""
    if not cohort_vals:
        return ""
    s = sorted(cohort_vals)
    med = s[len(s) // 2]
    if med == 0:
        return "  (cohort median 0)"
    ratio = val / med
    if ratio >= 1.5:
        return f"  ↑ {ratio:.1f}× the cohort median"
    if ratio <= 0.67 and val < med:
        return f"  ↓ {ratio:.1f}× the cohort median"
    return "  (~cohort median)"


def wander_note(panels):
    """One-line honesty flag: how similar are the two runs of each scene?
    Cheap proxy — average Jaccard word-overlap between run pairs of the same scene/panel."""
    by_key = {}
    for p in panels:
        by_key.setdefault((p["scene"], p["panel"]), []).append(set(p["reply"].lower().split()))
    sims = []
    for sets in by_key.values():
        for i in range(len(sets)):
            for j in range(i + 1, len(sets)):
                a, b = sets[i], sets[j]
                if a or b:
                    sims.append(len(a & b) / len(a | b))
    if not sims:
        return "between-run wander: n/a (single run)"
    avg = sum(sims) / len(sims)
    label = "tight" if avg > 0.5 else "moderate" if avg > 0.3 else "loose — read with caution"
    return f"between-run wander: {label} (avg run-pair word overlap {avg:.2f})"


# ── JUDGE layer ─────────────────────────────────────────────────────────────
JUDGE_SYS = (
    "You are reading transcripts where one fixed, escalating user script was run "
    "against a single language model across several emotional 'registers' (confrontation, "
    "imploring, absurd play, confiding, reassuring, deciding, vague). The user lines are "
    "identical for every model; only the model's replies differ. Your job is to characterize "
    "THIS model's expressed personality from how it conducts itself — warm or cold, holds or "
    "folds, plays or stays literal, carries emotional weight or snaps back.\n"
    "ABSOLUTE RULE ON QUOTES — read carefully: every evidence_quote must be copied "
    "CHARACTER-FOR-CHARACTER from the transcript text below. Do NOT paraphrase, reconstruct, "
    "tidy up, or 'remember' a quote — if you cannot find the exact string in the transcript, "
    "you may not make the claim. Before writing each quote, locate it in the text and copy it "
    "verbatim. A fabricated or approximated quote is the worst possible error here and "
    "invalidates the whole card. When in doubt, quote less and shorter. Prefer a 5-10 word "
    "exact snippet over a long approximate one.\n"
    "OTHER RULES: (1) Characterize behavior, not branding — you are not told which model this "
    "is and must not guess. (2) Be specific, falsifiable, and UNFLATTERING by default. Do not "
    "round every model up to 'warm but principled' — that is the failure mode of lazy reads. "
    "Name what is distinctive and what is off-putting, blunt, or weak, not just what is nice. "
    "If a model folds, hedges, over-apologizes, or template-spams, say so plainly. "
    "(3) Make the reads DISCRIMINATE: pick shapes and glosses that would let a reader tell this "
    "model apart from a generically helpful assistant. "
    "(4) COVERAGE: produce exactly one row for EVERY register present in the transcript — never "
    "silently skip one. If you cannot find a clean verbatim quote for a register, still emit its "
    "row with shape \"uncertain\", a brief gloss of why, and an empty evidence_quote. A missing "
    "row reads as 'no behavior here', which is misleading; an explicit uncertain row is honest. "
    "Return ONLY JSON matching the schema."
)

JUDGE_SCHEMA_HINT = """Return JSON exactly like:
{
  "one_line_fingerprint": "<= 12 words capturing the character",
  "signature_move": "the recurring move this model makes (e.g. 'reassures while disagreeing')",
  "reads": [
    {"register": "Reassuring (day-trader)", "shape": "holds | folds | climbs | flat | warms | hedges | uncertain",
     "gloss": "<= 8 words", "evidence_quote": "verbatim snippet from a reply (empty string if shape is uncertain)", "panel": "U4 run1"}
  ],
  "failure_mode": "the most characteristic way it goes wrong, with a verbatim quote inside it",
  "least_flattering_true_thing": "one specific, unflattering-but-accurate observation about this model"
}
Cover as many registers as the transcript supports. Every evidence_quote must be copied
character-for-character from the transcript — if you can't find it exactly, drop the claim."""


def judge_read(judge_slug, label, transcript_text):
    body = {
        "model": judge_slug,
        "messages": [
            {"role": "system", "content": JUDGE_SYS},
            {"role": "user", "content": JUDGE_SCHEMA_HINT + "\n\n--- TRANSCRIPT ---\n" + transcript_text},
        ],
        "temperature": 0,
        "max_tokens": 1500,
        "response_format": {"type": "json_object"},
    }
    r = requests.post(API, headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
                      json=body, timeout=180)
    r.raise_for_status()
    raw = r.json()["choices"][0]["message"]["content"]
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        return json.loads(m.group(0)) if m else {"_parse_error": raw[:500]}


# ── card assembly ───────────────────────────────────────────────────────────
def vendor(slug):
    return slug.split("/")[0] if "/" in slug else slug


def card_md(label, slug, run_dir, judge_slug, metrics, cohort, tics, wander, read):
    L = []
    L.append(f"# Card — {label}")
    L.append(f"_subject: `{slug}` · source: [{run_dir}/scout_{label}.md](../../{run_dir}/scout_{label}.md)_")
    L.append(f"_{wander}_\n")

    L.append("## MEASURED  *(computed; no judgment)*\n")
    L.append("**Conversational reflexes**\n")
    rows = [
        ("avg words / reply", metrics["avg_words"], cohort["avg_words"]),
        ("ends on a question", f'{metrics["ends_on_question_pct"]}%', cohort["ends_on_question_pct"]),
        ("hedges", f'{metrics["hedge_pct"]}%', cohort["hedge_pct"]),
        ("offers to help", f'{metrics["offers_help_pct"]}%', cohort["offers_help_pct"]),
        ("emoji", f'{metrics["emoji_pct"]}%', cohort["emoji_pct"]),
    ]
    L.append("| metric | value | vs cohort |")
    L.append("|---|---|---|")
    for name, val, cvals in rows:
        raw = val if isinstance(val, int) else int(str(val).rstrip("%"))
        L.append(f"| {name} | {val} |{cohort_line(name, raw, cvals)} |")
    if metrics["ai_disclaimer_count"]:
        L.append(f"\n_\"I'm an AI\" disclaimers: {metrics['ai_disclaimer_count']}_")

    L.append("\n**Catchphrases** *(distinctive, cross-scene)*\n")
    if tics:
        for n, sp, p in tics:
            L.append(f"- `{p}` — {n}×, {sp} scenes")
    else:
        L.append("- _(none above threshold)_")

    L.append("\n## JUDGE-DRAFTED READ  *(model: `%s` · UNVERIFIED — every claim cites a quote)*\n" % judge_slug)
    if "_parse_error" in read:
        L.append("> ⚠️ judge returned unparseable output:\n>\n> " + read["_parse_error"])
    else:
        L.append(f"**Fingerprint:** {read.get('one_line_fingerprint','—')}  ")
        L.append(f"**Signature move:** {read.get('signature_move','—')}\n")
        L.append("| register | shape | gloss | evidence |")
        L.append("|---|---|---|---|")
        for r in read.get("reads", []):
            q = (r.get("evidence_quote", "") or "").replace("|", "\\|").strip()
            if len(q) > 90:
                q = q[:90] + "…"
            if q:
                ev = f'_{r.get("panel","")}:_ "{q}"'
            else:
                ev = "— _(no clean quote)_"
            L.append(f"| {r.get('register','')} | {r.get('shape','')} | {r.get('gloss','')} | {ev} |")
        if read.get("failure_mode"):
            L.append(f"\n**Failure mode:** {read['failure_mode']}")
        if read.get("least_flattering_true_thing"):
            L.append(f"\n**Least flattering true thing:** {read['least_flattering_true_thing']}")

    L.append("\n## HUMAN  *(fill / correct by eye — this overrides the draft above)*\n")
    L.append("- **Confirmed fingerprint:** <!-- your one line -->")
    L.append("- **Where the judge is wrong:** <!-- -->")
    L.append("- **Best pull-quote:** <!-- paste the keeper -->\n")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description="Build a per-model card from a scout run.")
    ap.add_argument("run_dir", help="a runs/<tag> directory with scout_*.md")
    ap.add_argument("--judge", required=True,
                    help="REQUIRED. OpenRouter slug for the read. Must NOT be a family under test.")
    ap.add_argument("--out", default=None, help="output dir (default: cards/<tag>)")
    ap.add_argument("--no-judge", action="store_true", help="skip the LLM read; emit measured-only cards")
    args = ap.parse_args()

    run_dir = Path(args.run_dir)
    files = sorted(run_dir.glob("scout_*.md"))
    if not files:
        sys.exit(f"no scout_*.md in {run_dir}")
    if not args.no_judge and not os.environ.get("OPENROUTER_API_KEY"):
        sys.exit("OPENROUTER_API_KEY not set (needed for the judge). Use --no-judge to skip.")

    parsed = {}
    slug_of = {}
    for f in files:
        label, panels = parse(f)
        parsed[label] = panels
        # recover full slug from the file header line
        head = f.read_text().splitlines()[:5]
        slug_of[label] = next((re.search(r"\((.*?)\)", l).group(1)
                               for l in head if l.startswith("# Atlas scout")), label)

    # self-preference guard
    if not args.no_judge:
        jv = vendor(args.judge)
        clashes = [l for l, s in slug_of.items() if vendor(s) == jv]
        if clashes:
            print(f"⚠️  SELF-PREFERENCE WARNING: judge vendor '{jv}' also appears among subjects "
                  f"({', '.join(clashes)}). The plan flags this as a leak. Continuing anyway.\n")

    # metrics for all models first (so we can express each vs the cohort)
    all_metrics = {l: reflexes(p) for l, p in parsed.items()}
    cohort = {k: [m[k] for m in all_metrics.values()]
              for k in ("avg_words", "ends_on_question_pct", "hedge_pct", "offers_help_pct", "emoji_pct")}

    # tics via catchphrases module (reuse its scene-span logic). Cohort
    # commonness is computed once, not per-model.
    out_dir = Path(args.out) if args.out else Path("cards") / run_dir.name
    out_dir.mkdir(parents=True, exist_ok=True)
    everyone = catchphrases.cohort_commonness(files)

    for f in files:
        label = f.stem.replace("scout_", "")
        panels = parsed[label]
        metrics = all_metrics[label]
        wander = wander_note(panels)

        # top distinctive cross-scene tics for this model — one ranking, shared
        # with the catchphrases CLI via rank_tics (dedup + shared-frac cap live there).
        _, text = catchphrases.load_replies(f)
        counts = Counter(catchphrases.phrases(text))
        ranked = catchphrases.rank_tics(label, f, counts, everyone, len(files))
        tics = [(n, sp, p) for _, n, sp, _, p in ranked[:8]]

        if args.no_judge:
            read = {"one_line_fingerprint": "<!-- run with --judge to draft -->", "reads": []}
        else:
            transcript = f.read_text()
            print(f"  judging {label} with {args.judge} …")
            read = judge_read(args.judge, label, transcript)

        dest = out_dir / f"{label}.md"
        dest.write_text(card_md(label, slug_of[label], run_dir.name, args.judge,
                                metrics, cohort, tics, wander, read))
        print(f"→ {dest}")


if __name__ == "__main__":
    main()
