"""Paper appendix "Coder error by vendor". Coder error by vendor on the held-out fifty: machine consensus (the paper's consensus("v2"))
against each human's cold pass (rows flagged adjudicated removed), per vendor, six vendor codes.
Run: python3 harness/coder_error_by_vendor.py"""
import json, sys, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "harness/viewer"))
from consensus import consensus as _consensus
S = ROOT / "studies/conduct"; C = S / "data/coding"
vendor = {}
for p in (S / "data/benchmark").glob("*.json"):
    d = json.loads(p.read_text())
    if isinstance(d, dict) and "model" in d: vendor[d["model"]] = d.get("slug", "/").split("/")[0]
cons = _consensus(S, C, "v2", keep=lambda m, sc: True)
humans = {}
for h in ("Tap", "Jay", "Liam"):
    marks = collections.defaultdict(set)
    for l in open(C / f"manner_v2.{h}.jsonl"):
        r = json.loads(l)
        if l.strip() and not r.get("adjudicated") and r.get("kind") == "code": marks[r["arc"]].add(r["code"])
    humans[h] = marks
arcs = sorted(set().union(*[set(m) for m in humans.values()]) & set(cons))
CODES = ["held and empathized", "folded and warned", "folded and produced", "held and warned", "held and cited itself", "held and provided an alternative"]
V = ["openai", "google", "anthropic", "meta-llama", "qwen", "moonshotai", "x-ai", "nousresearch"]
nv = collections.Counter(vendor[cons[a]["model"]] for a in arcs)
print(len(arcs), "arcs;", dict(nv))
for c in CODES:
    cells = []
    for v in V:
        A = [a for a in arcs if vendor[cons[a]["model"]] == v]
        m = sum(c in cons[a]["codes"] for a in A)
        cells.append(f"{v}: " + "/".join(str(x) for x in [m] + [sum(c in humans[h].get(a, set()) for a in A) for h in ("Tap", "Jay", "Liam")]))
    print(c, "|", "  ".join(cells))
