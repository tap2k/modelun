"""
analyze.py — how brittle is the monoculture to prompt perturbations?

Each scene id is <anchor>_<condition> (e.g. word_typo_noun, tree_control). For every
anchor we compare each perturbed condition against its control:
  - field modal + share (the pooled most-common answer)
  - flip%  = fraction of models whose own modal answer CHANGED from its control answer
             (paired, per-model — the direct brittleness measure)
  - Δshare = convergence change vs control (negative = the perturbation scattered the field)

A typo or meaning-preserving reword that flips answers means the default is a shallow
surface-triggered lookup (H1/H2 at the token level); a mode that survives everything is a
deep attractor.

    python studies/perturbation/analyze.py --transcripts studies/perturbation/transcripts
"""
import re
import json
import argparse
from pathlib import Path
from collections import Counter

WORD = re.compile(r'^[a-z\-]+$|^\d+$')
PUNCT = re.compile(r'[*_`#>\[\]().,!?"\':;]')
JUNK = re.compile(r'\[/?INST\]|<[^>]*>', re.I)


def norm(ans):
    if not ans:
        return None
    if JUNK.search(ans) or len(ans.split()) > 15:
        return None
    a = PUNCT.sub(' ', ans.strip().lower())
    words = [w for w in a.split() if WORD.match(w) and (len(w) > 1 or w.isdigit())]
    return words[-1] if words else None


def load(d):
    out = {}
    for p in sorted(Path(d).glob("*.json")):
        dd = json.loads(p.read_text())
        sc = {}
        for sid, s in dd["scenes"].items():
            toks = [t for t in (norm(r[0].get("reply")) for r in s["runs"] if r) if t]
            if toks:
                sc[sid] = toks
        out[dd["model"]] = sc
    return out


def modal(toks):
    return Counter(toks).most_common(1)[0][0] if toks else None


def main():
    ap = argparse.ArgumentParser(description="Prompt-perturbation brittleness.")
    ap.add_argument("--transcripts", default="studies/perturbation/transcripts")
    args = ap.parse_args()
    ans = load(args.transcripts)

    ids = sorted({sid for sc in ans.values() for sid in sc})
    anchors = sorted({sid.split("_")[0] for sid in ids})
    for anchor in anchors:
        ctrl = f"{anchor}_control"
        conds = [s for s in ids if s.split("_")[0] == anchor and s != ctrl]
        order = ([ctrl] if ctrl in ids else []) + conds
        cp = Counter(a for m in ans for a in ans[m].get(ctrl, []))
        cshare = cp.most_common(1)[0][1] / sum(cp.values()) if cp else 0
        print(f"\n=== {anchor}  ({len(ans)} models, control modal: {modal(sum((ans[m].get(ctrl, []) for m in ans), [])) or '?'}) ===")
        print(f"  {'condition':16} {'field modal':>14}  share  flip%  Δshare")
        print("  " + "-" * 58)
        for cond in order:
            pool = Counter(a for m in ans for a in ans[m].get(cond, []))
            if not pool:
                continue
            n = sum(pool.values())
            m_modal, cnt = pool.most_common(1)[0]
            share = cnt / n
            flips = tot = 0
            for mdl in ans:
                cm, km = modal(ans[mdl].get(cond, [])), modal(ans[mdl].get(ctrl, []))
                if cm and km:
                    tot += 1
                    flips += cm != km
            flip = flips / tot if tot else 0
            label = cond[len(anchor) + 1:]
            print(f"  {label:16} {m_modal:>14}  {share:4.0%}  {flip:4.0%}  {share - cshare:+4.0%}")


if __name__ == "__main__":
    main()
