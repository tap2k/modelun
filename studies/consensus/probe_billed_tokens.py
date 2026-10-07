"""probe_billed_tokens.py — is text added before our message? Billed input tokens per provider endpoint.

A provider pays to process any text it adds before the caller's message (a default system prompt, an injected
instruction, a different chat template), so it shows in the billed prompt_tokens. Endpoints of one model share a
tokenizer, so each endpoint is compared with its PEERS: for every question, the most common prompt_tokens among the
same model's other endpoints on the same message. Surplus = endpoint's count minus that peer mode. This is the check
AgentProv (arXiv:2609.00052) runs against the official chat template; peers stand in for the template here.

Default: reads the audit's transcripts (transcripts-providers/<model>/<tag>/{core,expanded}/, every call carries
usage) -> transcripts-providers/billed_tokens.json (per endpoint: median, min and max surplus, and the audit's
identification for that endpoint from probes/provider_audit.json).

--probe: pinned diagnostic calls on the audit's four mismatches and peers, three messages each (the census question;
the same with our own one-line system prompt; a longer user message), 2 samples. A surplus that is constant across
message lengths is a fixed prefix; one that disappears under our system prompt is a default system prompt that a
caller's prompt replaces. -> transcripts-providers/billed-probe-<date>.json

Both outputs name providers and stay with transcripts-providers/ out of git.

    ../../.venv/bin/python probe_billed_tokens.py            # peer surplus from existing transcripts
    ../../.venv/bin/python probe_billed_tokens.py --probe    # paid diagnostic calls (54 calls, under $0.01)
"""
import json, statistics as st, sys, time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
ROOT = HERE / "transcripts-providers"

# the audit's four mismatches and their peers; the list names providers, so it lives in the excluded folder
LISTS = ROOT / "followup_endpoints.json"
PROBE_ENDPOINTS = [tuple(e) for e in json.loads(LISTS.read_text())["probe_endpoints"]] if LISTS.exists() else []
Q = "Name a color. Reply with one word only."
CONDS = {"a_plain": (None, Q),
         "b_sys": ("Reply with one word.", Q),
         "c_long": (None, Q + " This sentence is padding added to make the user message longer by a known amount of text.")}


def billed():
    """{model: {endpoint: {(battery, question): [prompt_tokens, ...]}}} from the audit transcripts."""
    data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for f in ROOT.glob("*/*/*/*.json"):
        model, ep, sub = f.relative_to(ROOT).parts[:3]
        for qid, sc in json.loads(f.read_text())["scenes"].items():
            for run in sc["runs"]:
                for t in run:
                    pt = (t.get("usage") or {}).get("prompt_tokens")
                    if pt is not None:
                        data[model][ep][(sub, qid)].append(pt)
    return data


def surplus():
    audit = {r["endpoint"]: r for r in json.loads((HERE / "probes" / "provider_audit.json").read_text())}
    rows = []
    for model, eps in sorted(billed().items()):
        for ep in sorted(eps):
            diffs, counts = [], []
            for q, pts in eps[ep].items():
                others = [p for e2 in eps if e2 != ep for p in eps[e2].get(q, [])]
                if others:
                    mode = Counter(others).most_common(1)[0][0]
                    diffs += [p - mode for p in pts]
                    counts += pts
            if not diffs:
                continue
            a = audit.get(f"{model}/{ep}", {})
            rows.append({"endpoint": f"{model}/{ep}", "calls": len(diffs), "median_prompt_tokens": st.median(counts),
                         "surplus_median": st.median(diffs), "surplus_min": min(diffs), "surplus_max": max(diffs),
                         "identified_as": a.get("identified_as"), "rank_of_claim": a.get("rank_of_claim"),
                         "q": a.get("q")})
    out = ROOT / "billed_tokens.json"
    out.write_text(json.dumps(rows, indent=1) + "\n")
    scored = [r for r in rows if r["rank_of_claim"]]
    pos = [r for r in scored if r["surplus_median"] > 0]
    print(f"{len(scored)} scored endpoints with peers; {len(pos)} billed above peers, "
          f"{sum(r['rank_of_claim'] == 1 for r in pos)} of them identified as claimed")
    for r in pos:
        print(f"  {r['endpoint']:50s} {r['surplus_median']:+6.1f}  id rank {r['rank_of_claim']}")
    print(f"-> {out}")


def probe():
    key = next(l.split("=", 1)[1].strip() for l in (HERE / "../../.env").read_text().splitlines()
               if l.startswith("OPENROUTER_API_KEY="))

    def call(model, tag, cond):
        sysm, u = CONDS[cond]
        msgs = ([{"role": "system", "content": sysm}] if sysm else []) + [{"role": "user", "content": u}]
        body = {"model": model, "messages": msgs, "temperature": 1.0, "max_tokens": 1024,
                "provider": {"order": [tag], "allow_fallbacks": False}}
        err = None
        for _ in range(3):
            try:
                r = json.load(urlopen(Request("https://openrouter.ai/api/v1/chat/completions",
                                              data=json.dumps(body).encode(),
                                              headers={"Authorization": f"Bearer {key}",
                                                       "Content-Type": "application/json"}), timeout=120))
                return dict(model=model, tag=tag, cond=cond, reply=r["choices"][0]["message"].get("content"),
                            usage=r.get("usage"), provider=r.get("provider"))
            except Exception as e:
                err = str(e)
                time.sleep(3)
        return dict(model=model, tag=tag, cond=cond, error=err)

    tasks = [(m, t, c) for m, t in PROBE_ENDPOINTS for c in CONDS for _ in range(2)]
    with ThreadPoolExecutor(12) as ex:
        res = list(ex.map(lambda x: call(*x), tasks))
    out = ROOT / f"billed-probe-{date.today().isoformat()}.json"
    out.write_text(json.dumps(res, indent=1) + "\n")
    for r in res:
        u = r.get("usage") or {}
        print(f"{r['model'].split('/')[1]:32s} {r['tag']:26s} {r['cond']:8s} prompt_tokens={u.get('prompt_tokens')}")
    print(f"cost ${sum((r.get('usage') or {}).get('cost') or 0 for r in res):.4f} -> {out}")


if __name__ == "__main__":
    probe() if "--probe" in sys.argv else surplus()
