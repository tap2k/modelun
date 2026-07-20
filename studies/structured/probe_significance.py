"""probe_significance.py — sign-flip permutation tests for the format-register effects.

Two exchangeable units, tested separately: categories (31 paired field-entropy diffs,
plain vs format) and models (44 paired within-column LOO surprisal diffs). 20k sign-flip
draws, two-sided. Results 2026-07-10, with the echo guard (category-noun / template
placeholder dropped as a non-answer — see build.py):

  field entropy / cats      per-model surprisal
  json      -0.204 p=.0006  -0.217 p=.0002   <- compresses, both units
  xml       -0.202 p=.0004  -0.186 p=.0022   <- compresses, both units
  yaml      -0.022 p=.75    -0.015 p=.80     <- NO net effect (any_word concentration is category-specific)
  csv       +0.038 p=.46    +0.069 p=.35     <- no net effect (echo guard drops its apparent loosening)
  brackets  +0.117 p=.0135  +0.131 p=.0089   <- significantly LOOSENS
  deepseek-v3.2 individual json collapse: p<1e-4; json-vs-yaml gradient paired: p<1e-4
"""
import json, re, sys, math
import numpy as np
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "consensus"))
from analyze import norm
rng = np.random.default_rng(7)

probe = json.loads((HERE / "probes/format_register.json").read_text())
PATS = {"json": r'"word"\s*:\s*"([^"]+)"', "xml": r"<word>([^<]+)</word>",
        "brackets": r"\[([^\]]+)\]", "yaml": r"(?i)\bword\s*:\s*(.+)",
        "csv": r'(?im)^\s*"?word"?\s*\r?\n\s*(.+?)\s*$'}
def pw(f, r):
    if not r: return None
    m = re.search(PATS[f], r)
    return norm(m.group(1)) if m else norm(r)
labels = sorted(probe["replies"]["json"].keys())
cats = sorted(probe["replies"]["json"][labels[0]].keys())
# echo guard (see build.py): drop the category noun / template placeholder as a non-answer.
def _head_noun(c):
    for f in PATS:
        p = (probe.get("formats", {}).get(f) or {}).get(c)
        m = re.match(r"Name (?:a |an |any |some )?(.+?)\.", p) if p else None
        if m: return m.group(1).split()[-1].lower()
    return None
ECHO = {c: {n for n in (_head_noun(c),) if n} | {"answer", "word"} for c in cats}
def ok(w, c): return w is not None and w not in ECHO[c]
def plain(l, c):
    t = json.loads((HERE.parent / "consensus/transcripts" / f"{l}.json").read_text())
    return [w for w in (norm(r[0].get("reply")) for r in t["scenes"][c]["runs"]) if ok(w, c)]
def fmt(f, l, c):
    return [w for w in (pw(f, r) for r in probe["replies"][f][l][c]) if ok(w, c)]
def entropy(pool):
    n = sum(pool.values())
    return -sum(k/n*math.log2(k/n) for k in pool.values())
def signflip_p(diffs, n=20000):
    diffs = np.array(diffs); obs = diffs.mean()
    null = (rng.choice([-1,1], size=(n, len(diffs))) * np.abs(diffs)).mean(axis=1)
    return obs, float((np.abs(null) >= abs(obs)).mean())
def surprisal(get):
    per = {c: {l: get(l, c) for l in labels} for c in cats}
    out = {}
    for l in labels:
        s = []
        for c in cats:
            field = Counter(a for o in labels if o != l for a in per[c][o])
            mine = per[c][l]; vc = len(set(field) | set(mine)); n = sum(field.values())
            s += [-math.log2((field[a]+1)/(n+vc)) for a in mine]
        out[l] = sum(s)/len(s)
    return out

if __name__ == "__main__":
    print("field-entropy per category (negative = format more concentrated):")
    for f in PATS:
        diffs = [entropy(Counter(a for l in labels for a in fmt(f, l, c))) -
                 entropy(Counter(a for l in labels for a in plain(l, c))) for c in cats]
        obs, p = signflip_p(diffs)
        print(f"  {f:9} Δ {obs:+.3f}  p={p:.4f}  ({sum(d<0 for d in diffs)}/31 concentrate)")
    sp = surprisal(plain)
    print("per-model Δ-surprisal (44 paired):")
    for f in PATS:
        sf = surprisal(lambda l, c, f=f: fmt(f, l, c))
        obs, p = signflip_p([sf[l]-sp[l] for l in labels])
        print(f"  {f:9} Δ {obs:+.3f}  p={p:.4f}")

def per_model_fdr(q=0.10, n_perm=20000):
    """Per-model Δ(json−plain) sign-flip tests with BH-FDR. 2026-07-10 result (echo
    guard): 6/44 significant, all negative (v3.2, qwen3, 4o-mini, gpt-5.6-sol, 4-turbo,
    gemini-3.1-pro; hermes just over threshold); every positive Δ individually n.s. The
    positive tail is read as register-invariant stranding vs. genuine divergence via the
    panel-free check in analyze_register_invariance.py, not as a lineage effect."""
    per_p = {c: {l: plain(l, c) for l in labels} for c in cats}
    per_j = {c: {l: fmt("json", l, c) for l in labels} for c in cats}
    def cat_s(per, l, c):
        field = Counter(a for o in labels if o != l for a in per[c][o])
        mine = per[c][l]
        if not mine: return None
        vc = len(set(field) | set(mine)); n = sum(field.values())
        return sum(-math.log2((field[a]+1)/(n+vc)) for a in mine) / len(mine)
    res = []
    for l in labels:
        d = np.array([j - p for c in cats
                      if (p := cat_s(per_p, l, c)) is not None
                      and (j := cat_s(per_j, l, c)) is not None])
        null = (rng.choice([-1, 1], size=(n_perm, len(d))) * np.abs(d)).mean(axis=1)
        res.append((l, d.mean(), float((np.abs(null) >= abs(d.mean())).mean())))
    res.sort(key=lambda x: x[2])
    k = max((i for i, (_, _, p) in enumerate(res, 1) if p <= q * i / len(res)), default=0)
    print(f"per-model Δ significant at BH-FDR q={q}: {k}/{len(labels)}")
    for l, obs, p in res[:k]:
        print(f"  {l:26} Δ {obs:+.2f}  p={p:.4f}")
    return res
