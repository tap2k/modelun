#!/usr/bin/env python3
"""Get peer reviews of a paper from several models through OpenRouter, with the cost of each.

Sends the LaTeX source, with every \\input{...} inlined and figures replaced by a note (captions
stay), to each model with a program-committee reviewer brief, at a chosen reasoning effort. Writes
one markdown review and one cost record per model, plus SUMMARY.md with scores and costs, to the
output directory. Nothing here knows what a study is; any paper that builds from one .tex works.

    python harness/review_paper.py studies/conduct/paper/main.tex
    python harness/review_paper.py studies/conduct/paper/main.tex --models openai/gpt-6-astra,x-ai/grok-4.7 --effort high
    python harness/review_paper.py studies/conduct/paper/main.tex --dry-run      # build the prompt, send nothing

Output defaults to <paper dir>/reviews/<date>/, which is gitignored: reviews are working material,
and where they are kept is the author's call.
"""
import os, re, sys, json, time, argparse, datetime, concurrent.futures as cf
from pathlib import Path
import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
API = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODELS = "openai/gpt-6-astra,anthropic/claude-opus-5.5,x-ai/grok-4.7,google/gemini-3.8-flash"
BRIEF = ("You are an experienced reviewer for {venue}. Review the paper below as you would for the "
         "program committee: rigorous, specific and fair. Structure your review as: 1. Summary (3-5 sentences). "
         "2. Strengths. 3. Weaknesses, numbered, most serious first, each citing the section or passage and saying "
         "concretely why it matters. 4. Questions for the authors. 5. Requested changes for a revision, numbered. "
         "6. Scores: soundness, presentation, contribution (each 1-4) and overall recommendation (1-10) with a "
         "one-line justification. The paper is given as LaTeX source with its generated tables inlined; figures are "
         "not shown, only their captions.")


def flatten(tex_path):
    """The .tex with each \\input{...} replaced by the file's text and each figure image by a note."""
    base = tex_path.parent
    def inline(m):
        p = base / m.group(1)
        p = p if p.suffix else p.with_suffix(".tex")
        return p.read_text() if p.exists() else m.group(0)
    tex = re.sub(r"\\input\{([^}]+)\}", inline, tex_path.read_text())
    return re.sub(r"\\includegraphics(\[[^\]]*\])?\{[^}]+\}", "[FIGURE: image not included; caption follows.]", tex)


def review(slug, system, paper, effort, out, max_tokens=24000):
    body = {"model": slug, "messages": [{"role": "system", "content": system}, {"role": "user", "content": paper}],
            "reasoning": {"effort": effort}, "max_tokens": max_tokens, "usage": {"include": True}}
    last = None
    for _ in range(3):
        try:
            r = requests.post(API, headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
                              json=body, timeout=900)
            r.raise_for_status(); d = r.json()
            text = (d["choices"][0]["message"].get("content") or "").strip()
            if not text:
                raise ValueError("empty content")
            u = d.get("usage") or {}
            rec = {"model": slug, "provider": d.get("provider"), "effort": effort, "cost": u.get("cost"),
                   "prompt_tokens": u.get("prompt_tokens"), "completion_tokens": u.get("completion_tokens"),
                   "reasoning_tokens": (u.get("completion_tokens_details") or {}).get("reasoning_tokens")}
            name = slug.split("/")[-1]
            (out / f"{name}.md").write_text(text + "\n")
            (out / f"{name}.json").write_text(json.dumps(rec, indent=1) + "\n")
            rec["overall"] = score(text)
            return rec
        except Exception as e:
            last = e; time.sleep(5)
    return {"model": slug, "error": str(last)}


def score(text):
    """The overall recommendation, best effort: the first 'overall ... N/10' or 'overall ... N' in the scores."""
    tail = text[text.lower().rfind("score"):] if "score" in text.lower() else text
    m = re.search(r"overall[^\d\n]{0,60}(\d{1,2})(?:\s*/\s*10)?", tail, re.I)
    return int(m.group(1)) if m else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tex", type=Path)
    ap.add_argument("--models", default=DEFAULT_MODELS)
    ap.add_argument("--effort", default="medium", choices=["low", "medium", "high"])
    ap.add_argument("--venue", default="a top machine-learning venue (COLM)")
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--dry-run", action="store_true", help="build the prompt and report its size; send nothing")
    a = ap.parse_args()
    paper = flatten(a.tex)
    system = BRIEF.format(venue=a.venue)
    models = [m for m in a.models.split(",") if m]
    if a.dry_run:
        print(f"{len(paper)} characters (~{len(paper) // 4} tokens) to each of {len(models)} models: {', '.join(models)}")
        return
    if not os.environ.get("OPENROUTER_API_KEY"):
        sys.exit("OPENROUTER_API_KEY not set (put it in .env).")
    out = a.out or a.tex.parent / "reviews" / datetime.date.today().isoformat()
    out.mkdir(parents=True, exist_ok=True)
    with cf.ThreadPoolExecutor(len(models)) as ex:
        recs = list(ex.map(lambda m: review(m, system, paper, a.effort, out), models))
    lines = [f"# Reviews of {a.tex} ({datetime.date.today().isoformat()}, effort {a.effort})", "",
             "| Reviewer | Overall | Cost | Tokens in / out |", "|---|---|---|---|"]
    for r in recs:
        if "error" in r:
            lines.append(f"| {r['model']} | error: {r['error'][:60]} | | |")
        else:
            lines.append(f"| {r['model']} | {r['overall'] if r['overall'] is not None else '?'} | "
                         f"${r['cost'] or 0:.3f} | {r['prompt_tokens']} / {r['completion_tokens']} |")
    total = sum(r.get("cost") or 0 for r in recs)
    lines += ["", f"Total ${total:.3f}.", ""]
    (out / "SUMMARY.md").write_text("\n".join(lines))
    print("\n".join(lines)); print(f"-> {out}/")


if __name__ == "__main__":
    main()
