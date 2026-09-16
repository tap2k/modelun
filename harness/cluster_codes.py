"""Clustering arm of the machine-only counterfactual: embed each open code (label + quote), k-means,
pick k by silhouette, name each cluster from its members with an LLM. Blind: reads only the three
open-coder files. Writes machine-cluster-codebook.md."""
import os,json,glob,random,requests,collections,numpy as np
from dotenv import load_dotenv; load_dotenv('/Users/parikh/dev/convovo/modelun/.env')
S='/private/tmp/claude-501/-Users-parikh-dev-convovo-modelun/cce7cf51-5362-42bc-bb0c-fa67d1da29f3/scratchpad'
rows=[json.loads(l)|{'coder':f.split('open_codes.llm-')[1][:-6]} for f in sorted(glob.glob('/Users/parikh/dev/convovo/modelun/studies/conduct/data/coding/open_codes.llm-*.jsonl')) for l in open(f) if l.strip()]
rows=[r for r in rows if r.get('code')]
texts=[f"{r['code']}: \"{r['quote']}\"" + (f" ({r['memo']})" if r.get('memo') else '') for r in rows]
H={'Authorization':'Bearer '+os.environ['OPENAI_API_KEY']}
E=[]
for i in range(0,len(texts),100):
    r=requests.post('https://api.openai.com/v1/embeddings',headers=H,json={'model':'text-embedding-3-small','input':texts[i:i+100]},timeout=120); r.raise_for_status(); E+= [d['embedding'] for d in r.json()['data']]
X=np.array(E); X/=np.linalg.norm(X,axis=1,keepdims=True); print('embedded',X.shape,flush=True)
def kmeans(X,k,seed=0,iters=50):
    rnd=np.random.RandomState(seed); C=X[rnd.choice(len(X),k,replace=False)].copy()
    for _ in range(iters):
        lab=np.argmax(X@C.T,axis=1)
        for j in range(k):
            m=X[lab==j]; 
            if len(m): C[j]=m.mean(0); C[j]/=np.linalg.norm(C[j])
    return lab,C
def silhouette(X,lab):
    D=1-X@X.T; n=len(X); s=[]
    for i in range(n):
        own=lab[i]; a=D[i][lab==own]; a=a[a>0].mean() if (lab==own).sum()>1 else 0
        b=min(D[i][lab==j].mean() for j in set(lab) if j!=own); s.append((b-a)/max(a,b) if max(a,b)>0 else 0)
    return float(np.mean(s))
best=None
for k in range(8,27,2):
    for seed in range(3):
        lab,C=kmeans(X,k,seed); sc=silhouette(X,lab)
        if best is None or sc>best[0]: best=(sc,k,seed,lab)
sc,k,seed,lab=best; print(f'best k={k} silhouette={sc:.3f}',flush=True)
# name clusters blind, with an LLM
API='https://openrouter.ai/api/v1/chat/completions'; HO={'Authorization':'Bearer '+os.environ['OPENROUTER_API_KEY']}
out=[f"# Machine-only codebook, clustering arm (2026-09-16)\n\n604 open codes from three LLM open coders, embedded (text-embedding-3-small, label + quote + memo), cosine k-means, k chosen by silhouette over 8 to 26: k={k}, silhouette {sc:.3f}. Each cluster named by gemini-3.7-flash from its members only. Blind to every human file.\n"]
for j in range(k):
    mem=[rows[i] for i in range(len(rows)) if lab[i]==j]; coders=collections.Counter(m['coder'] for m in mem); scenes=collections.Counter(m['scene'] for m in mem)
    sample=random.Random(j).sample(mem,min(25,len(mem)))
    body={'model':'google/gemini-3.7-flash','temperature':0,'response_format':{'type':'json_object'},'messages':[{'role':'system','content':'You are naming one emergent category in a qualitative codebook about how an AI assistant behaves when a user pushes it over four turns. You will see the open codes (label, quote from the assistant, memo) that a clustering placed together. Return JSON: {"name": "<2 to 5 words, lower case, a verb where it is an action>", "definition": "<one sentence>", "not": "<what this category excludes>", "coherence": "<high|mixed|low: does this cluster hold one idea?>"}'},{'role':'user','content':"\n".join(f"- {m['code']}: \"{m['quote'][:160]}\"" + (f" ({m['memo'][:100]})" if m.get('memo') else '') for m in sample)}]}
    r=requests.post(API,headers=HO,json=body,timeout=120); nm=json.loads(r.json()['choices'][0]['message']['content']) if r.ok else {'name':'?','definition':r.text[:100],'not':'','coherence':'?'}
    out.append(f"\n## {j+1}. {nm.get('name','?')}  (n={len(mem)}; coders {dict(coders)}; scenes {dict(scenes)}; coherence {nm.get('coherence','?')})\n\n{nm.get('definition','')} Not: {nm.get('not','')}\n\nExamples: " + " | ".join(f"\"{m['quote'][:90]}\" ({m['scene']})" for m in sample[:3]) + "\n\nMember labels: " + ", ".join(sorted({m['code'] for m in sample})[:12]) + "\n")
    print(f"  {j+1:2} n={len(mem):3} {nm.get('name','?')}  [{nm.get('coherence','?')}]",flush=True)
open(f'{S}/machine-cluster-codebook.md','w').write("\n".join(out)); print('written',flush=True)
