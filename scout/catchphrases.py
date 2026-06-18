"""
Catchphrases — surface each model's recurring verbal tics from a scout run.

A model's catchphrases are an involuntary fingerprint: "if you want, I can help"
(GPT), "100%" / "takes a lot of guts" (Gemini), "in good conscience" (Sonnet).
This is a *reading aid*, not a scorer — it turns "I noticed Gemini keeps saying
100%" into "Gemini: '100%' x7, across 5 scenes". No judge, no model calls.

    python scout/catchphrases.py runs/v4.1-clamp

It reads every scout_<model>.md in that dir, pulls each model's replies, and
prints the phrases that are (a) frequent for that model and (b) distinctive —
i.e. NOT said about equally by every model (those are shared boilerplate).
"""

import re
import sys
import argparse
from pathlib import Path
from collections import Counter

# Reply blocks look like:  **<label>:**\n\n> line\n> line ...
REPLY_RE = re.compile(r"^\*\*(?P<label>[^*]+):\*\*\s*$")

# Words so generic they drown out the signal as phrase-edges. We don't drop the
# words, just avoid starting/ending a phrase on them (keeps "of guts", kills "of the").
STOP_EDGES = {
    "the", "a", "an", "to", "of", "and", "or", "but", "is", "are", "was", "i",
    "you", "it", "that", "this", "in", "on", "for", "with", "as", "at", "be",
    "your", "my", "so", "if", "not", "do", "can", "will", "just", "we", "they",
}


def load_replies(md_path):
    """Return the concatenated reply text for the single model in this file."""
    lines = md_path.read_text().splitlines()
    label = md_path.stem.replace("scout_", "")
    out, capturing = [], False
    for line in lines:
        m = REPLY_RE.match(line)
        if m:
            capturing = m.group("label").strip() == label
            continue
        if capturing and line.startswith(">"):
            out.append(line.lstrip("> ").rstrip())
        elif line.startswith(("**U", "##", "###", "**run")):
            capturing = False
    return label, " \n ".join(out)


def normalize(text):
    text = text.lower()
    # keep words (incl. internal apostrophes: don't, you'd) and spaces; drop the rest
    text = text.replace("’", "'")
    text = re.sub(r"[^a-z0-9\s']", " ", text)
    text = re.sub(r"\s'\s", " ", text)       # stray apostrophes that aren't inside a word
    return text


def phrases(text, n_lo=2, n_hi=5):
    """Yield n-grams (n_lo..n_hi) that don't start/end on a stop-edge word."""
    for chunk in text.split("\n"):
        toks = normalize(chunk).split()
        for n in range(n_lo, n_hi + 1):
            for i in range(len(toks) - n + 1):
                gram = toks[i:i + n]
                if gram[0] in STOP_EDGES or gram[-1] in STOP_EDGES:
                    continue
                yield " ".join(gram)


def scene_spans(md_path, label, phrase_set):
    """For each phrase, how many distinct scenes (## headers) it appears in —
    a phrase spanning many scenes is a true tic, not a scene-bound artifact."""
    spans = {p: set() for p in phrase_set}
    scene = None
    capturing = False
    buf = []

    def flush():
        if scene is None:
            return
        text = normalize(" ".join(buf))
        for p in phrase_set:
            if p in text:
                spans[p].add(scene)

    for line in md_path.read_text().splitlines():
        if line.startswith("## "):
            flush(); buf = []; scene = line[3:].strip(); capturing = False
        elif REPLY_RE.match(line):
            capturing = REPLY_RE.match(line).group("label").strip() == label
        elif capturing and line.startswith(">"):
            buf.append(line.lstrip("> "))
    flush()
    return {p: len(s) for p, s in spans.items()}


def main():
    ap = argparse.ArgumentParser(description="Surface each model's recurring catchphrases from a scout run.")
    ap.add_argument("run_dir", help="a runs/<tag> directory containing scout_*.md")
    ap.add_argument("--top", type=int, default=15, help="phrases to show per model")
    ap.add_argument("--min-count", type=int, default=3, help="ignore phrases said fewer than this many times")
    ap.add_argument("--min-scenes", type=int, default=2,
                    help="a real tic recurs across situations; require it in at least this many scenes "
                         "(set 1 to include scene-bound content like the arithmetic answer)")
    args = ap.parse_args()

    files = sorted(Path(args.run_dir).glob("scout_*.md"))
    if not files:
        sys.exit(f"no scout_*.md files in {args.run_dir}")

    # Pass 1: per-model phrase counts.
    counts = {}      # label -> Counter
    texts = {}       # label -> raw reply text
    for f in files:
        label, text = load_replies(f)
        texts[label] = text
        counts[label] = Counter(phrases(text))

    labels = list(counts)
    # A phrase's "commonness" = how many models use it at all. Distinctive
    # phrases are used by few models; boilerplate is used by all.
    everyone = Counter()
    for c in counts.values():
        for p in c:
            everyone[p] += 1

    print(f"Catchphrases across {len(labels)} models in {args.run_dir}\n"
          f"(frequent for the model AND not shared by everyone)\n")

    file_for = {f.stem.replace("scout_", ""): f for f in files}
    for label in labels:
        c = counts[label]
        # candidate phrases: frequent enough, multi-word, not universal boilerplate
        cands = {p for p, n in c.items()
                 if n >= args.min_count and len(p.split()) >= 2
                 and everyone[p] < len(labels)}
        # scene-span is the key filter: a tic recurs across SITUATIONS, so phrases
        # that live in a single scene (the arithmetic answer, the doctor's-note
        # boilerplate) are dropped here rather than ranked.
        spans = scene_spans(file_for[label], label, cands)

        ranked = []
        for p in cands:
            if spans[p] < args.min_scenes:
                continue
            n, shared_by = c[p], everyone[p]
            # reward: said often, across many scenes, and specific to this model
            score = n * spans[p] / shared_by
            ranked.append((score, n, spans[p], shared_by, p))
        ranked.sort(reverse=True)

        print(f"── {label} " + "─" * max(2, 40 - len(label)))
        if not ranked:
            print("   (no cross-scene tics above threshold)")
        for _, n, sp, shared, p in ranked[:args.top]:
            tag = "" if shared == 1 else f"  (+{shared-1} other model{'s' if shared>2 else ''})"
            print(f"   {n:>2}x · {sp} scenes  \"{p}\"{tag}")
        print()


if __name__ == "__main__":
    main()
