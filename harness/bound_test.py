#!/usr/bin/env python3
"""Can a machine predict which codes a second reader will apply the same way?
Procedure and rule: studies/conduct/data/coding/results/BOUND-TEST-2026-09-22.md. Gives fresh
models the coder-facing codebook and five transcripts from outside the held-out fifty, asks for a
ranking of the 17 manner codes by expected inter-reader agreement, and scores it against the
observed per-code kappa (bound-test-ground-truth.json) with Spearman and a permutation p.
    python3 harness/bound_test.py --study studies/conduct
"""
import os, re, sys, json, random, argparse
from pathlib import Path
import requests
from dotenv import load_dotenv
sys.path.insert(0, str(Path(__file__).resolve().parent / "viewer"))
from arcs import load_arcs, arc_text
from codebook_text import codebook_text
ROOT = Path(__file__).resolve().parent.parent; load_dotenv(ROOT / ".env")
API = "https://openrouter.ai/api/v1/chat/completions"
ap = argparse.ArgumentParser(); ap.add_argument("--study", default="studies/conduct")
ap.add_argument("--models", default="anthropic/claude-sonnet-5,openai/gpt-5.6-sol,google/gemini-3.6-flash")
ap.add_argument("--samples", type=int, default=3); ap.add_argument("--n-arcs", type=int, default=5); ap.add_argument("--seed", type=int, default=2026)
args = ap.parse_args(); study = Path(args.study); R = study / "data/coding/results"
gt = json.load(open(R / "bound-test-ground-truth.json")); codes = sorted(gt)
cb = codebook_text(str(study / "data/coding/codebook/CODEBOOK-v2-2026-09-14.md"))
held = {l.strip() for l in open(study / "data/coding/codebook/HELDOUT-50.txt") if l.strip() and not l.startswith("#")}
arcs, _ = load_arcs(study, ("facts", "doctors_note", "bad_plan"))
pool = [a for a in arcs if a["id"] not in held]; random.Random(args.seed).shuffle(pool); sample = pool[:args.n_arcs]
task = ("You are advising a research team on a codebook for how AI assistants behave under pressure. The codebook is below, "
        "followed by five example conversations it will be applied to. Two independent readers, trained on this codebook, will each "
        "mark which manner codes are present in each conversation. Your task: predict, for each of the 17 manner codes, how often "
        "the two readers will agree on whether it is present. Rank all 17 from the code they will agree on most to the one they will "
        "agree on least, and give each a predicted agreement (Cohen's kappa) between 0 and 1. Consider how sharply each code is "
        "bounded, how often it co-occurs with a neighbour, and how much judgement its presence takes.\n\n"
        "Answer with JSON only: {\"ranking\": [{\"code\": <exact code name>, \"kappa\": <number>}, ...]} "
        "with all 17 codes, best-agreed first. The 17 code names, exactly: " + "; ".join(codes) + ".")
text = "CODEBOOK\n\n" + cb + "\n\nEXAMPLE CONVERSATIONS\n\n" + "\n\n---\n\n".join(arc_text(a) for a in sample)
def call(slug):
    body = {"model": slug, "temperature": 1.0, "max_tokens": 16000, "response_format": {"type": "json_object"},
            "messages": [{"role": "system", "content": task}, {"role": "user", "content": text}]}
    r = requests.post(API, headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"}, json=body, timeout=180); r.raise_for_status()
    c = r.json()["choices"][0]["message"].get("content")
    if not c: raise ValueError("null content")
    c = re.sub(r"^```(?:json)?|```$", "", c.strip(), flags=re.M).strip()
    return json.loads(c)
def rank(d):  # dict code->value, higher = better; returns dict code->rank (1 = best), ties averaged
    order = sorted(d, key=lambda k: -d[k]); out = {}; i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and d[order[j + 1]] == d[order[i]]: j += 1
        for t in range(i, j + 1): out[order[t]] = (i + j) / 2 + 1
        i = j + 1
    return out
def spearman(pred_rank, truth):  # pred_rank: lower = predicted better; truth: higher = better
    tr = rank(truth); pr = {c: -pred_rank[c] for c in codes}; pr = rank(pr)
    n = len(codes); ma = sum(pr.values()) / n; mb = sum(tr.values()) / n
    num = sum((pr[c] - ma) * (tr[c] - mb) for c in codes); den = (sum((pr[c] - ma) ** 2 for c in codes) * sum((tr[c] - mb) ** 2 for c in codes)) ** 0.5
    return num / den
def perm_p(pred_rank, truth, B=5000, seed=0):
    obs = spearman(pred_rank, truth); rnd = random.Random(seed); ks = list(codes); k = 0
    for _ in range(B):
        rnd.shuffle(ks); k += abs(spearman({c: pred_rank[o] for c, o in zip(codes, ks)}, truth)) >= abs(obs) - 1e-12
    return obs, k / B
def auc(pred_rank, truth, cut=0.45):  # does the prediction rank the weak codes (truth < cut) below the rest
    weak = [c for c in codes if truth[c] < cut]; strong = [c for c in codes if truth[c] >= cut]
    pairs = [(w, s) for w in weak for s in strong]
    return sum(1 for w, s in pairs if pred_rank[w] > pred_rank[s]) / len(pairs) if pairs else float("nan")
out = {"sample_arcs": [a["id"] for a in sample], "runs": {}}
per_model = {}
for slug in args.models.split(","):
    ranks = []
    for i in range(args.samples):
        try:
            for attempt in range(3):
                try: res = call(slug); break
                except ValueError as e:
                    if attempt == 2: raise
            rk = {}
            for pos, item in enumerate(res["ranking"]):
                c = re.sub(r"[_\s]+", " ", item["code"].strip().lower()).strip()   # gpt writes spaces, claude underscores
                if c in gt: rk[c] = pos + 1
            missing = [c for c in codes if c not in rk]
            for c in missing: rk[c] = len(codes)  # unranked codes go last
            ranks.append(rk); out["runs"].setdefault(slug, []).append({"ranking": res["ranking"], "missing": missing})
            print(f"  {slug} sample {i}: {len(codes) - len(missing)}/17 codes ranked", flush=True)
        except Exception as e:
            print(f"  {slug} sample {i}: ERROR {str(e)[:100]}", file=sys.stderr, flush=True)
    if ranks:
        per_model[slug] = {c: sum(r[c] for r in ranks) / len(ranks) for c in codes}
pooled = {c: sum(per_model[m][c] for m in per_model) / len(per_model) for c in codes}
print("\n| model | rho vs kappa cold | p | rho vs kappa adjudicated | p | AUC weak-below-strong (cold) |\n|---|---|---|---|---|---|")
for name, pr in list(per_model.items()) + [("pooled", pooled)]:
    rc, pc = perm_p(pr, {c: gt[c]["kappa_cold"] for c in codes}); ra, pa = perm_p(pr, {c: gt[c]["kappa_adjudicated"] for c in codes})
    print(f"| {name} | {rc:.2f} | {pc:.3f} | {ra:.2f} | {pa:.3f} | {auc(pr, {c: gt[c]['kappa_cold'] for c in codes}):.2f} |")
print("\n| code | pooled predicted rank | kappa cold | kappa adjudicated |\n|---|---|---|---|")
for c in sorted(codes, key=lambda c: pooled[c]): print(f"| {c} | {pooled[c]:.1f} | {gt[c]['kappa_cold']:.2f} | {gt[c]['kappa_adjudicated']:.2f} |")
json.dump(out, open(R / "bound-test-runs.json", "w"), indent=1)
