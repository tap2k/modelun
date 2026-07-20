"""Concern-2 prototype: panel-FREE register-invariance, to disentangle active
divergence from passive stranding in the within-column surprisal Δ.

For each model compare its OWN plain answer distribution to its OWN json distribution
(never touching the pool): per-category modal-flip rate and mean Jensen-Shannon divergence.
Cross-tab against the surprisal Δ so stranding (high +Δ, low self-change) is visible.
"""
import io
import importlib.util
import math
import statistics as st
from collections import Counter
from contextlib import redirect_stdout
from pathlib import Path

# Load the sibling analyze.py under a distinct name so its own `from analyze import norm`
# resolves to the census module (both files are named analyze.py). It computes
# s_plain / s_fmt at import; silence its print block.
_spec = importlib.util.spec_from_file_location("fmt_analyze", Path(__file__).resolve().parent / "analyze.py")
A = importlib.util.module_from_spec(_spec)
with redirect_stdout(io.StringIO()):
    _spec.loader.exec_module(A)

labels, cats = A.labels, A.cats_json
s_plain, s_json = A.s_plain, A.s_fmt["json"]

def jsd(p, q):
    """Jensen-Shannon divergence (base 2, in [0,1]) between two answer Counters."""
    keys = set(p) | set(q)
    if not keys:
        return float("nan")
    sp, sq = sum(p.values()), sum(q.values())
    if not sp or not sq:
        return float("nan")
    P = {k: p[k] / sp for k in keys}
    Q = {k: q[k] / sq for k in keys}
    M = {k: 0.5 * (P[k] + Q[k]) for k in keys}
    def kl(X):
        return sum(X[k] * math.log2(X[k] / M[k]) for k in keys if X[k] > 0)
    return 0.5 * kl(P) + 0.5 * kl(Q)

LLAMA = {"llama-4-maverick", "llama-3.3", "mythomax"}
COMPRESSORS = {"deepseek-v3.2", "gpt-4o-mini", "gpt-4-turbo", "gpt-5.6-sol", "qwen3", "gemini-3.1-pro"}

rows = []
for l in labels:
    flips = n = 0
    jsds = []
    for c in cats:
        pa = Counter(A.plain_answers(l, c))
        ja = Counter(A.fmt_answers("json", l, c))
        if not pa or not ja:
            continue
        n += 1
        if pa.most_common(1)[0][0] != ja.most_common(1)[0][0]:
            flips += 1
        jsds.append(jsd(pa, ja))
    mjsd = sum(jsds) / len(jsds) if jsds else float("nan")
    rows.append((l, s_plain[l], s_json[l] - s_plain[l], mjsd, flips, n))

print(f"{'model':26}{'plain':>7}{'Δjson':>7}{'selfJSD':>9}{'flips':>8}   grp")
print("-" * 70)
for l, sp, d, mjsd, flips, n in sorted(rows, key=lambda r: r[2]):
    grp = "LLAMA" if l in LLAMA else ("COMPRESS" if l in COMPRESSORS else "")
    print(f"{l:26}{sp:>7.2f}{d:>+7.2f}{mjsd:>9.3f}{flips:>5}/{n:<3}  {grp}")

# field means for context
allj = [r[3] for r in rows if not math.isnan(r[3])]
print(f"\nfield mean self-JSD (plain vs json): {st.mean(allj):.3f}")
print("LLAMA group self-JSD:  " + ", ".join(f"{l} {mjsd:.3f} (Δ{d:+.2f}, flips {flips}/{n})"
      for l, sp, d, mjsd, flips, n in rows if l in LLAMA))
print("COMPRESS self-JSD:     " + ", ".join(f"{l} {mjsd:.3f} (Δ{d:+.2f}, flips {flips}/{n})"
      for l, sp, d, mjsd, flips, n in rows if l in COMPRESSORS))

# ---- serendipity: locate the 'pick a word' category and report plain/json share ----
print("\n-- 'pick a word' category shares --")
for c in cats:
    pa = Counter(a for l in labels for a in A.plain_answers(l, c))
    ja = Counter(a for l in labels for a in A.fmt_answers("json", l, c))
    if pa and pa.most_common(1)[0][0] == "serendipity":
        pw, pn = pa.most_common(1)[0]
        qw, qn = ja.most_common(1)[0]
        print(f"  cat key: {c!r}")
        print(f"  plain: {pw} {pn/sum(pa.values()):.1%} of {sum(pa.values())}, distinct {len(pa)}")
        print(f"  json:  {qw} {qn/sum(ja.values()):.1%} of {sum(ja.values())}, distinct {len(ja)}")
