"""Concern-b: is the brackets loosening robust to the junk/echo-guard decision?

The paper reports brackets Δ trimmed +0.16 (raw) -> +0.13 (full echo guard). Here we sweep
three guard variants and confirm the sign and significance survive all of them:
  raw          — no echo guard (category noun / placeholder kept)
  placeholder  — drop only "answer"/"word" (the template slot), keep the category noun
  full         — drop category noun + "answer"/"word"  (the paper's guard)
Reported on both exchangeable units (per-model surprisal, per-category field entropy).
"""
import math
from collections import Counter

import probe_significance as PS  # reuse norm, pw, labels, cats, entropy, signflip_p

labels, cats = PS.labels, PS.cats

def make_ok(variant):
    def ok(w, c):
        if w is None:
            return False
        if variant == "raw":
            return True
        drop = {"answer", "word"}
        if variant == "full":
            hn = PS._head_noun(c)
            if hn:
                drop = drop | {hn}
        return w not in drop
    return ok

def plain(l, c, ok):
    import json
    t = json.loads((PS.HERE.parent / "consensus/transcripts" / f"{l}.json").read_text())
    return [w for w in (PS.norm(r[0].get("reply")) for r in t["scenes"][c]["runs"]) if ok(w, c)]

def fmt(f, l, c, ok):
    return [w for w in (PS.pw(f, r) for r in PS.probe["replies"][f][l][c]) if ok(w, c)]

def surprisal(get):
    per = {c: {l: get(l, c) for l in labels} for c in cats}
    out = {}
    for l in labels:
        s = []
        for c in cats:
            field = Counter(a for o in labels if o != l for a in per[c][o])
            mine = per[c][l]
            vc = len(set(field) | set(mine)); n = sum(field.values())
            s += [-math.log2((field[a] + 1) / (n + vc)) for a in mine]
        out[l] = sum(s) / len(s) if s else float("nan")
    return out

print(f"{'variant':12}{'perModelΔ':>11}{'p(model)':>10}{'entropyΔ':>11}{'p(cat)':>9}")
print("-" * 53)
for variant in ("raw", "placeholder", "full"):
    ok = make_ok(variant)
    sp = surprisal(lambda l, c: plain(l, c, ok))
    sb = surprisal(lambda l, c: fmt("brackets", l, c, ok))
    dm = [sb[l] - sp[l] for l in labels]
    obs_m, p_m = PS.signflip_p(dm)
    dc = [PS.entropy(Counter(a for l in labels for a in fmt("brackets", l, c, ok))) -
          PS.entropy(Counter(a for l in labels for a in plain(l, c, ok))) for c in cats]
    obs_c, p_c = PS.signflip_p(dc)
    print(f"{variant:12}{obs_m:>+11.3f}{p_m:>10.4f}{obs_c:>+11.3f}{p_c:>9.4f}")
