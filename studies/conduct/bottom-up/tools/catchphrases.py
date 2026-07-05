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
                # drop all-numeric grams: these are list markers ("1. ...2. ...")
                # that survived normalization, never verbal tics.
                if all(t.isdigit() for t in gram):
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


def dedupe_subphrases(ranked, counts):
    """Collapse a tic that fragments into its own sub-grams into one row.

    The n-gram net catches a phrase AND its pieces: "i'm sorry you feel" /
    "sorry you feel that way" / "feel that way" are three rows of one apology.
    We keep the highest-ranked gram of a family and drop any other gram that is
    (a) a contiguous token-subsequence of a kept gram, or contains one, AND
    (b) not meaningfully more frequent than that kept gram — i.e. its count is
    mostly explained by the kept phrase rather than standing on its own.

    `ranked` is the score-sorted list of (score, n, spans, shared, phrase).
    Family membership is decided by token-containment, but which member *wins*
    is decided by information, not score: when counts are comparable the longer
    phrase wins (it carries more), and a shorter gram only survives if it's used
    substantially more often than the longer one it sits inside — i.e. it stands
    on its own rather than just leaking through.
    """
    def is_sub(a, b):
        """True if token-list a appears contiguously inside token-list b."""
        if len(a) >= len(b):
            return False
        return any(b[i:i + len(a)] == a for i in range(len(b) - len(a) + 1))

    def beats(p, other):
        """Should p be dropped in favor of `other` (its containment relative)?"""
        np, no = counts[p], counts[other]
        lp, lo = len(p.split()), len(other.split())
        if lo > lp:          # `other` is longer: p survives only if clearly more frequent
            return np <= 1.5 * no
        else:                # `other` is shorter: it must out-frequent p to displace it
            return no > 1.5 * np

    survivors = []
    for row in ranked:
        phrase = row[-1]
        toks = phrase.split()
        if any(beats(phrase, k[-1])
               for k in ranked if k is not row
               and (is_sub(toks, k[-1].split()) or is_sub(k[-1].split(), toks))):
            continue
        survivors.append(row)
    return survivors


def rank_tics(label, md_path, counts, everyone, n_models,
              min_count=3, min_scenes=2, max_shared_frac=0.5):
    """The one true ranking. Returns the deduped, score-sorted tic rows
    (score, n, spans, shared_by, phrase) for one model — used by both the CLI
    and make_cards so the two can never drift.

    counts:   this model's phrase Counter
    everyone: phrase -> how many models use it at all (cohort commonness)
    """
    shared_cap = max_shared_frac * n_models
    # candidate phrases: frequent enough, multi-word, and distinctive — used by
    # at most a fraction of the cohort. A plain "< all models" test let a phrase
    # 27/28 share ('right now') count as a fingerprint; a fraction cap kills it.
    cands = {p for p, n in counts.items()
             if n >= min_count and len(p.split()) >= 2
             and everyone[p] <= shared_cap}
    # scene-span is the key filter: a tic recurs across SITUATIONS, so phrases
    # that live in a single scene (the arithmetic answer, the doctor's-note
    # boilerplate) are dropped here rather than ranked.
    spans = scene_spans(md_path, label, cands)

    ranked = []
    for p in cands:
        if spans[p] < min_scenes:
            continue
        n, shared_by = counts[p], everyone[p]
        # reward: said often, across many scenes, and specific to this model
        score = n * spans[p] / shared_by
        ranked.append((score, n, spans[p], shared_by, p))
    ranked.sort(reverse=True)
    return dedupe_subphrases(ranked, counts)


def cohort_commonness(files):
    """phrase -> number of models using it at all, across a scout run's files."""
    everyone = Counter()
    for f in files:
        _, t = load_replies(f)
        for ph in set(phrases(t)):
            everyone[ph] += 1
    return everyone


def main():
    ap = argparse.ArgumentParser(description="Surface each model's recurring catchphrases from a scout run.")
    ap.add_argument("run_dir", help="a runs/<tag> directory containing scout_*.md")
    ap.add_argument("--top", type=int, default=15, help="phrases to show per model")
    ap.add_argument("--min-count", type=int, default=3, help="ignore phrases said fewer than this many times")
    ap.add_argument("--min-scenes", type=int, default=2,
                    help="a real tic recurs across situations; require it in at least this many scenes "
                         "(set 1 to include scene-bound content like the arithmetic answer)")
    ap.add_argument("--max-shared-frac", type=float, default=0.5,
                    help="drop phrases used by more than this fraction of models — shared assistant "
                         "boilerplate ('right now', 'make sure') is not a fingerprint, even if no "
                         "single model is missing it")
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
        ranked = rank_tics(label, file_for[label], counts[label], everyone, len(labels),
                           min_count=args.min_count, min_scenes=args.min_scenes,
                           max_shared_frac=args.max_shared_frac)

        print(f"── {label} " + "─" * max(2, 40 - len(label)))
        if not ranked:
            print("   (no cross-scene tics above threshold)")
        for _, n, sp, shared, p in ranked[:args.top]:
            tag = "" if shared == 1 else f"  (+{shared-1} other model{'s' if shared>2 else ''})"
            print(f"   {n:>2}x · {sp} scenes  \"{p}\"{tag}")
        print()


if __name__ == "__main__":
    main()
