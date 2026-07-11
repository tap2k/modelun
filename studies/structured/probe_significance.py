"""probe_significance.py — sign-flip permutation tests for the format-register effects.

Two exchangeable units, tested separately: categories (31 paired field-entropy diffs,
plain vs format) and models (44 paired within-column LOO surprisal diffs). 20k sign-flip
draws, two-sided. Results 2026-07-10 (full battery):

  field entropy / cats      per-model surprisal
  json      -0.204 p=.0006  -0.217 p=.0001   <- compresses, both units
  xml       -0.196 p=.0006  -0.180 p=.0032   <- compresses, both units
  yaml      -0.021 p=.76    -0.014 p=.81     <- NO net effect (any_word concentration is category-specific)
  csv       +0.075 p=.15    +0.109 p=.16     <- no net effect
  brackets  +0.138 p=.0052  +0.161 p=.0022   <- significantly LOOSENS
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
def plain(l, c):
    t = json.loads((HERE.parent / "consensus/transcripts" / f"{l}.json").read_text())
    return [w for w in (norm(r[0].get("reply")) for r in t["scenes"][c]["runs"]) if w]
def fmt(f, l, c):
    return [w for w in (pw(f, r) for r in probe["replies"][f][l][c]) if w]
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
    """Per-model Δ(json−plain) sign-flip tests with BH-FDR. 2026-07-10 result: 7/44
    significant, all negative (v3.2, hermes, 4o-mini, 4-turbo, gpt-5.6-sol, qwen3,
    gemini-3.1-pro); every positive Δ individually n.s. Meta-lineage family test:
    pooled +0.44 p=.009; vs rest +0.70 p<1e-4 (two-sample label permutation)."""
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
