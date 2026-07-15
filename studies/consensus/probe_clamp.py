"""
probe_clamp.py — does the one-word clamp MANUFACTURE the convergence, or just extract it?

For ten census categories spanning the convergence range, each asked clamped ("... Reply
with one word only.") and free (bare), we ask: when the clamp is removed and models answer
in prose, does the field's clamped-modal answer still dominate? We measure it robustly by
substring presence (the clamped modal appearing anywhere in the free reply), which sidesteps
the last-word normalizer's failure on sentences.

If clamped-share ≈ free-presence, the monoculture is a property of what models CHOOSE, not of
how we ASK — a direct rebuttal to "isn't this a one-word-prompt artifact?"

    python studies/consensus/probe_clamp.py --transcripts studies/consensus/transcripts-clamp
"""
import re
import json
import argparse
from pathlib import Path
from collections import Counter

WORD = re.compile(r'^[a-z\-]+$|^\d+$')
PUNCT = re.compile(r'[*_`#>\[\]().,!?"\':;]')


def norm(ans):
    """One-word extraction, as in the census (last valid token)."""
    if not ans:
        return None
    a = PUNCT.sub(' ', ans.strip().lower())
    words = [w for w in a.split() if WORD.match(w) and (len(w) > 1 or w.isdigit())]
    return words[-1] if words else None


def main():
    ap = argparse.ArgumentParser(description="One-word-clamp method-defense probe.")
    ap.add_argument("--transcripts", default="studies/consensus/transcripts-clamp")
    args = ap.parse_args()

    # gather replies per scene
    clamp_toks, free_replies = {}, {}
    for p in sorted(Path(args.transcripts).glob("*.json")):
        dd = json.loads(p.read_text())
        for sid, s in dd["scenes"].items():
            cat, cond = sid.rsplit("_", 1)
            for r in s["runs"]:
                if not r:
                    continue
                reply = r[0].get("reply")
                if cond == "clamp":
                    t = norm(reply)
                    if t:
                        clamp_toks.setdefault(cat, Counter())[t] += 1
                else:
                    free_replies.setdefault(cat, []).append((reply or "").lower())

    cats = [c for c in clamp_toks if c in free_replies]
    cats.sort(key=lambda c: -(clamp_toks[c].most_common(1)[0][1] / sum(clamp_toks[c].values())))

    print(f"\n{'category':10} {'clamp modal':>12}  clamp-share  free-has-modal   (n free)")
    print("-" * 62)
    for c in cats:
        pool = clamp_toks[c]
        modal, cnt = pool.most_common(1)[0]
        share = cnt / sum(pool.values())
        frees = free_replies[c]
        has = sum(1 for r in frees if re.search(rf'\b{re.escape(modal)}\b', r))
        pres = has / len(frees) if frees else 0
        print(f"{c:10} {modal:>12}  {share:9.0%}  {pres:11.0%}     ({len(frees)})")
    print("-" * 62)
    print("clamp-share ≈ free-has-modal  ⇒  the clamp extracts the mode, it does not create it.")


if __name__ == "__main__":
    main()
