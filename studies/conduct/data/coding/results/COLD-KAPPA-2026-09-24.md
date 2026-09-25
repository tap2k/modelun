# Cold per-code kappa against the machine consensus (2026-09-24)

Each human pass before adjudication (Tap, Jay, Liam) against the six v2 coders (present in 3 of 6),
fifty held-out arcs, 95% bootstrap intervals over arcs (2,000 resamples, seed 0). `n=human/consensus`
is how many arcs each marks. Basis of Appendix "Reliability before adjudication" in the conduct paper.
Run from `data/coding/`.

    code | Tap | Jay | Liam
    50 arcs
    folded and apologized | 0.70 [0.36,0.94] n=9/7 | 0.62 [0.15,0.92] n=5/7 | 0.70 [0.39,0.94] n=9/7
    folded and conceded | 0.90 [0.64,1.00] n=5/6 | 0.91 [0.65,1.00] n=7/6 | 0.90 [0.64,1.00] n=5/6
    folded and encouraged | 0.83 [0.50,1.00] n=6/8 | 0.50 [0.09,0.81] n=6/8 | 0.55 [0.15,0.85] n=8/8
    folded and produced | 1.00 [1.00,1.00] n=3/3 | 0.48 [0.00,1.00] n=1/3 | 0.85 [0.00,1.00] n=4/3
    folded and warned | 0.48 [-0.04,1.00] n=2/2 | -0.04 [-0.08,0.00] n=2/2 | 0.00 [0.00,0.00] n=0/2
    held and apologized | 0.48 [0.16,0.75] n=5/13 | 0.78 [0.56,0.95] n=11/13 | 0.38 [0.07,0.67] n=10/13
    held and cited itself | 0.36 [0.00,0.74] n=2/8 | 0.50 [0.10,0.81] n=6/8 | 0.00 [-0.00,0.00] n=0/8
    held and defended the fact | 0.78 [0.55,0.95] n=11/13 | 0.63 [0.36,0.85] n=12/13 | 0.64 [0.40,0.83] n=19/13
    held and diverted | 0.69 [0.23,1.00] n=6/5 | 1.00 [1.00,1.00] n=5/5 | 0.62 [0.15,0.92] n=7/5
    held and empathized | 0.48 [0.27,0.70] n=10/22 | 0.83 [0.67,0.96] n=18/22 | 0.63 [0.39,0.84] n=19/22
    held and explained | 0.15 [-0.11,0.54] n=6/3 | 0.17 [-0.07,0.44] n=13/3 | 0.12 [-0.07,0.36] n=16/3
    held and gave the user an out | 0.72 [0.44,0.93] n=10/13 | 0.65 [0.37,0.88] n=9/13 | 0.42 [0.08,0.70] n=9/13
    held and probed | 0.91 [0.65,1.00] n=6/7 | 0.61 [0.20,0.88] n=8/7 | 0.55 [0.19,0.83] n=9/7
    held and provided an alternative | 0.82 [0.62,0.96] n=14/18 | 0.69 [0.46,0.89] n=17/18 | 0.32 [0.04,0.57] n=20/18
    held and supported the person | 1.00 [1.00,1.00] n=4/4 | 0.70 [0.26,1.00] n=7/4 | 0.39 [-0.03,0.71] n=9/4
    held and supported with evidence | 0.79 [0.52,1.00] n=7/10 | 0.73 [0.42,0.94] n=8/10 | 0.65 [0.30,0.90] n=7/10
    held and warned | 0.34 [0.08,0.60] n=4/15 | 0.80 [0.59,0.95] n=13/15 | 0.38 [0.08,0.65] n=11/15

Script:

```python
import json,glob,collections,random
def load(c,adj):
    H=[json.loads(l) for l in open(f"manner_v2.{c}.jsonl") if l.strip()]
    H=[r for r in H if not r.get("rejected")] if adj else [r for r in H if not r.get("adjudicated")]
    d=collections.defaultdict(set); arcs=set()
    for r in H:
        if r.get("kind")=="code": d[r["arc"]].add(r["code"]); arcs.add(r["arc"])
        if r.get("kind")=="trajectory": arcs.add(r["arc"])
    return d,arcs
M=collections.Counter()
for f in glob.glob("relabel_v2.llm-*.jsonl"):
    s=set()
    for l in open(f):
        if not l.strip(): continue
        r=json.loads(l)
        if isinstance(r,dict) and r.get("kind")=="code": s.add((r["arc"],r["code"]))
    for k in s: M[k]+=1
maj=collections.defaultdict(set)
for (a,c),n in M.items():
    if n>=3: maj[a].add(c)
def kap(p):
    n=len(p); po=sum(a==b for a,b in p)/n; pa=sum(a for a,_ in p)/n; pb=sum(b for _,b in p)/n
    pe=pa*pb+(1-pa)*(1-pb); return (po-pe)/(1-pe) if pe<1 else float('nan')
random.seed(0)
hum={c:load(c,False) for c in ["Tap","Jay","Liam"]}
arcs=sorted(set.intersection(*[h[1] for h in hum.values()]))
codes=sorted({c for h in hum.values() for a in arcs for c in h[0][a]}|{c for a in arcs for c in maj[a]})
print(len(arcs),"arcs")
for code in codes:
    row=[code]
    for c,(d,_) in hum.items():
        p=[(code in d[a], code in maj[a]) for a in arcs]
        k=kap(p); bs=[kap([random.choice(p) for _ in p]) for _ in range(2000)]
        bs=sorted(x for x in bs if x==x); lo,hi=bs[int(.025*len(bs))],bs[int(.975*len(bs))-1]
        row.append(f"{k:.2f} [{lo:.2f},{hi:.2f}] n={sum(x for x,_ in p)}/{sum(y for _,y in p)}")
    print(" | ".join(row))
```
