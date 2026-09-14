"""Reconciliation material for open coding: align every coder's quoted spans per arc, list shared spans with both labels, human-only spans, and LLM-only spans by how many LLM coders quote them. Run after the human batch is committed. python harness/reconcile_codes.py > studies/conduct/data/coding/RECONCILIATION-<date>.md"""
import json,glob,re,sys,collections; sys.path.insert(0,'harness/viewer'); from arcs import load_arcs, sample
full,reveal=load_arcs('studies/conduct',{'bad_plan','facts','make_it_better','doctors_note'}); arcs=sample(full,10); order={a['id']:i for i,a in enumerate(arcs)}; byid={a['id']:a for a in arcs}
norm=lambda s: re.sub(r'\s+',' ',(s or '').replace('’',"'").replace('“','"').replace('”','"')).strip().lower()
def text(a): return norm(' \n '.join((t['reply'] or '') for t in a['turns']))
def span(q,T):
    q=norm(q); k=T.find(q); return (k,k+len(q)) if q and k>=0 else None
def ov(s,t): return max(0,min(s[1],t[1])-max(s[0],t[0]))
coders={'Tap':'open_codes.Tap.jsonl','haiku':'open_codes.llm-anthropic_claude-haiku-4.5.jsonl','gemini':'open_codes.llm-google_gemini-3.7-flash.jsonl','mini':'open_codes.llm-openai_gpt-5.4-mini.jsonl'}
C={k:[json.loads(l) for l in open('studies/conduct/data/coding/'+v) if l.strip()] for k,v in coders.items()}
LLM=['haiku','gemini','mini']
P=print
shared_pairs=[]; llm_only=[]; human_only=[]; per_arc_counts=[]
for a in arcs:
    T=text(a); aid=a['id']
    H=[(x,span(x['quote'],T)) for x in C['Tap'] if x['arc']==aid]
    L={k:[(x,span(x['quote'],T)) for x in C[k] if x['arc']==aid] for k in LLM}
    per_arc_counts.append((order[aid],a['scene'],len(H),{k:len(L[k]) for k in LLM}))
    for hx,hs in H:
        if not hs: continue
        m=[(k,lx) for k in LLM for lx,ls in L[k] if ls and ov(hs,ls)>0]
        (shared_pairs if m else human_only).append((aid,hx,m) if m else (aid,hx))
    for k in LLM:
        for lx,ls in L[k]:
            if not ls: continue
            if not any(hs and ov(hs,ls)>0 for _,hs in H):
                others=[k2 for k2 in LLM if k2!=k and any(ls2 and ov(ls,ls2)>0 for _,ls2 in L[k2])]
                llm_only.append((aid,k,lx,others,ls))
nH=sum(1 for x in C['Tap'] if span(x['quote'],text(byid[x['arc']])))
P("== coverage ==")
P(f"human spans {nH}: overlapped by at least one LLM coder {len(shared_pairs)}, by none {len(human_only)}")
P(f"LLM spans not overlapping any human span: {len(llm_only)} (" + ', '.join(f"{k} {sum(1 for r in llm_only if r[1]==k)}" for k in LLM) + ")")
cons=[r for r in llm_only if r[3]]; solo=[r for r in llm_only if not r[3]]
P(f"of those, also quoted by another LLM coder: {len(cons)} rows; by one coder only: {len(solo)} (" + ', '.join(f"{k} {sum(1 for r in solo if r[1]==k)}" for k in LLM) + ")")
P("\n== human spans no LLM coder quoted ==")
for aid,hx in human_only: P(f"  {order[aid]:2} {hx['scene']:15} {hx['code']!r:36} {hx['quote'][:70]!r}")
P("\n== per-arc code counts (human | haiku gemini mini) ==")
for pos,sc,h,l in per_arc_counts: P(f"  {pos:2} {sc:15} {h} | {l['haiku']} {l['gemini']} {l['mini']}" + ("   <- human <=1, an LLM 5+" if h<=1 and max(l.values())>=5 else ""))
P("\n== shared spans: human label vs LLM labels ==")
for aid,hx,m in sorted(shared_pairs,key=lambda r:order[r[0]]):
    P(f"  {order[aid]:2} {hx['scene']:14} H={hx['code']!r}  " + ' | '.join(f"{k}={lx['code']!r}" for k,lx in m))
P("\n== LLM-only spans quoted by 2+ LLM coders (blind-spot candidates), by arc ==")
g=collections.defaultdict(list)
for aid,k,lx,others,ls in cons: g[aid].append((k,lx,ls))
for aid in sorted(g,key=order.get):
    P(f"  -- {order[aid]:2} {byid[aid]['scene']} ({reveal[byid[aid]['blind']]}); human: {[x['code'] for x in C['Tap'] if x['arc']==aid]}")
    for k,lx,ls in sorted(g[aid],key=lambda r:r[2][0]): P(f"     {k:6} {lx['code']!r:48} {lx['quote'][:80]!r}")
