"""analyze_enforced.py — plain vs requested-JSON vs enforced structured output.

Three columns on the same 44-panel, 31 categories:
  plain     — census transcripts (no format ask)
  requested — "Reply with JSON only, ..." clause (format_register.json, json column)
  enforced  — same clause + response_format json_schema (enforced_json.json)

Key question: does enforcement compress the field FURTHER than the mere request, or is
the request already saturating? Reports per-model plain/req/enf surprisal, the
enforced-vs-requested delta, field means, enforced parse survival, and default retention
under enforcement (compare to the ~47% under the request).
"""
import json
import math
import re
import sys
from pathlib import Path
from collections import Counter

HERE = Path(__file__).resolve().parent
CONSENSUS = HERE.parent / "consensus"
sys.path.insert(0, str(CONSENSUS))
from analyze import norm

reg = json.loads((HERE / "probes/format_register.json").read_text())
enf = json.loads((HERE / "probes/enforced_json.json").read_text())

JSONPAT = re.compile(r'"word"\s*:\s*"([^"]+)"')


def pj(reply):
    if not reply:
        return None
    m = JSONPAT.search(reply)
    return norm(m.group(1)) if m else norm(reply)


labels = sorted(enf["replies"].keys())
cats = sorted(reg["replies"]["json"][labels[0]].keys())

# echo guard (see views/build.py): drop the category noun / template placeholder as a non-answer.
def _head_noun(cat):
    p = (reg.get("formats", {}).get("json") or {}).get(cat)
    m = re.match(r"Name (?:a |an |any |some )?(.+?)\.", p) if p else None
    return m.group(1).split()[-1].lower() if m else None

ECHO = {c: {n for n in (_head_noun(c),) if n} | {"answer", "word"} for c in cats}
def _ok(w, c):
    return w is not None and w not in ECHO[c]


def req_ans(l, c):
    return [w for w in (pj(r) for r in reg["replies"]["json"][l][c]) if _ok(w, c)]


def enf_ans(l, c):
    return [w for w in (pj(r) for r in enf["replies"][l][c]) if _ok(w, c)]


def plain_ans(l, c):
    t = json.loads((CONSENSUS / "transcripts" / f"{l}.json").read_text())
    return [w for w in (norm(r[0].get("reply")) for r in t["scenes"][c]["runs"]) if _ok(w, c)]


# enforced-support coverage per model: fraction of cells yielding a valid word.
# Models whose OpenRouter path rejects strict json_schema return all-None -> coverage 0.
cov = {}
for l in labels:
    tot = ok = 0
    for c in cats:
        for r in enf["replies"][l][c]:
            tot += 1
            ok += pj(r) is not None
    cov[l] = ok / tot
SUPPORTED = [l for l in labels if cov[l] >= 0.90]
UNSUPPORTED = [l for l in labels if cov[l] < 0.90]


def surprisal(get, pool):
    """Within-column LOO surprisal, field restricted to `pool` (identical composition
    across columns for a fair enf-vs-req comparison)."""
    per = {c: {l: get(l, c) for l in pool} for c in cats}
    out = {}
    for l in pool:
        sc = []
        for c in cats:
            mine = per[c][l]
            field = Counter(a for o in pool if o != l for a in per[c][o])
            vc = len(set(field) | set(mine))
            n = sum(field.values())
            sc += [-math.log2((field[a] + 1) / (n + vc)) for a in mine]
        out[l] = sum(sc) / len(sc) if sc else float("nan")
    return out


sp = surprisal(plain_ans, SUPPORTED)
sr = surprisal(req_ans, SUPPORTED)
se = surprisal(enf_ans, SUPPORTED)

print(f"panel {len(labels)} models; {len(SUPPORTED)} support enforced json_schema, "
      f"{len(UNSUPPORTED)} do not\n")
if UNSUPPORTED:
    print("NO ENFORCED SUPPORT (all-None under response_format): "
          + ", ".join(f"{l} ({cov[l]:.0%})" for l in UNSUPPORTED) + "\n")

print("Three columns on the identical " + str(len(SUPPORTED)) + "-model supported field:\n")
print(f"{'model':26}{'plain':>7}{'req':>7}{'enf':>7}{'Δreq':>7}{'Δenf':>8}{'enf-req':>9}")
for l in sorted(SUPPORTED, key=lambda x: -sp[x]):
    print(f"{l:26}{sp[l]:>7.2f}{sr[l]:>7.2f}{se[l]:>7.2f}"
          f"{sr[l]-sp[l]:>+7.2f}{se[l]-sp[l]:>+8.2f}{se[l]-sr[l]:>+9.2f}")
n = len(SUPPORTED)
mp, mr, me = (sum(d.values()) / n for d in (sp, sr, se))
print(f"{'FIELD MEAN':26}{mp:>7.2f}{mr:>7.2f}{me:>7.2f}"
      f"{mr-mp:>+7.2f}{me-mp:>+8.2f}{me-mr:>+9.2f}")
enfreq = [se[l] - sr[l] for l in SUPPORTED]
comp = sum(1 for d in enfreq if d < -0.05)
loos = sum(1 for d in enfreq if d > 0.05)
print(f"\nenf-req: mean {sum(enfreq)/n:+.2f} bits | "
      f"{comp} models compress further, {loos} loosen, {n-comp-loos} flat (|Δ|<0.05)")

print("\nenforced parse survival (non-None replies yielding a valid word), supported models:")
tot = ok = 0
for l in SUPPORTED:
    for c in cats:
        for r in enf["replies"][l][c]:
            if r is not None:
                tot += 1
                ok += pj(r) is not None
print(f"  {ok}/{tot} = {ok/tot:.1%}")

field_modal = {c: Counter(a for l in labels for a in plain_ans(l, c)).most_common(1)[0][0]
               for c in cats}


def retention(ansfn, pool):
    tot = kept = 0
    for l in pool:
        stable = [c for c in cats
                  if len(set(plain_ans(l, c))) == 1 and len(plain_ans(l, c)) == 4
                  and plain_ans(l, c)[0] != field_modal[c]]
        kept += sum(1 for c in stable
                    if (jc := Counter(ansfn(l, c)))
                    and jc.most_common(1)[0][0] == plain_ans(l, c)[0]
                    and jc.most_common(1)[0][1] >= 3)
        tot += len(stable)
    return kept, tot


kr, tr = retention(req_ans, SUPPORTED)
ke, te = retention(enf_ans, SUPPORTED)
print(f"\ndefault retention (supported models' {tr} stable chat defaults): "
      f"requested {kr}/{tr} ({kr/tr:.0%}) | enforced {ke}/{te} ({ke/te:.0%})")
