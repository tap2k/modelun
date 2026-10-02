"""probe_provider_audit.py — does each OpenRouter provider serve the model it claims?

Each endpoint in transcripts-providers/<model>/<provider-tag>/{core,expanded}/ answered the 96 census and expanded
questions four times, pinned to that provider (harness/run.py --provider, no fallbacks). Endpoint metadata
(declared precision, price) is in transcripts-providers/endpoints-<date>.json.

Per endpoint:
  identified_as  the panel model whose profile (transcripts/ + transcripts-extra/ + transcripts-expanded/, 8 answers
                 per question, OpenRouter's default routing) gives the endpoint's answers the highest likelihood
  rank_of_claim  where the claimed model ranks among all profiles (1 = identified correctly)
  distance       mean Jensen-Shannon divergence (bits) between the endpoint's answers and its PEERS: the pooled
                 answers of every other provider of the same model, collected the same day. Not the panel profile,
                 which is one unknown provider on an earlier date.
  p              permutation test of that distance: per category, the endpoint's and its peers' answers are pooled
                 and relabeled at random (sizes kept), 1,000 times; p = share of shuffles at least as far apart as
                 observed. A small p means the endpoint stands out from the other providers of its model by more
                 than sampling noise. Benjamini-Hochberg across endpoints is reported as q. Models with one
                 provider have no peers and get no p.

    ../../.venv/bin/python probe_provider_audit.py      # -> probes/provider_audit.json
"""
import json, math, random, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from analyze import against, answers, load
from probe_fingerprint import panel

ROOT = HERE / "transcripts-providers"
PERMS = 1000


def jsd(a, b):
    ca, cb = Counter(a), Counter(b)
    na, nb = len(a), len(b)
    s = 0.0
    for k in set(ca) | set(cb):
        p, q = ca[k] / na, cb[k] / nb
        m = (p + q) / 2
        if p:
            s += 0.5 * p * math.log2(p / m)
        if q:
            s += 0.5 * q * math.log2(q / m)
    return s


def endpoint_answers(d, field_c, field_e):
    out = {}
    for sub, battery, field in (("core", "census", field_c), ("expanded", "expanded", field_e)):
        files = sorted((d / sub).glob("*.json"))
        if files:
            for cats in against(field, load(HERE, battery, paths=files), HERE, battery).values():
                out.update(cats)
    return out


def perm_p(E, R, cats, rng):
    obs = sum(jsd(E[c], R[c]) for c in cats) / len(cats)
    hits = 0
    for _ in range(PERMS):
        tot = 0.0
        for c in cats:
            pool = E[c] + R[c]
            rng.shuffle(pool)
            tot += jsd(pool[:len(E[c])], pool[len(E[c]):])
        hits += tot / len(cats) >= obs
    return obs, (hits + 1) / (PERMS + 1)


def main():
    A = panel()
    models = sorted(A)
    field_c, field_e = answers(HERE), answers(HERE, "expanded")
    meta = json.loads(sorted(ROOT.glob("endpoints-*.json"))[-1].read_text())
    vocab = {c: len({a for m in models for a in A[m].get(c, [])}) + 1 for m in models for c in A[m]}
    rng = random.Random(0)
    rows = []
    ans = {key: endpoint_answers(ROOT / key, field_c, field_e) for key in meta}
    for key, info in sorted(meta.items()):
        claim = info["model"].split("/")[1]
        E = ans[key]
        peers = [k for k in meta if k != key and meta[k]["model"] == info["model"] and ans[k]]
        if claim not in A or not E:
            rows.append({"endpoint": key, **info, "status": "no data" if not E else "claimed model not in panel"})
            continue
        cats = [c for c in E if len(E[c]) >= 2 and len(A[claim].get(c, [])) >= 4]
        score = {m: sum(math.log((Counter(A[m].get(c, []))[a] + 0.1) / (len(A[m].get(c, [])) + 0.1 * vocab[c]))
                        for c in cats for a in E[c]) for m in models}
        ranked = sorted(models, key=score.get, reverse=True)
        row = {"endpoint": key, **info, "questions": len(cats), "identified_as": ranked[0],
               "rank_of_claim": ranked.index(claim) + 1, "peers": len(peers),
               "margin_nats_per_q": round((score[ranked[0]] - score[claim]) / len(cats), 2)}
        if peers:
            P = {c: [a for k in peers for a in ans[k].get(c, [])] for c in cats}
            pc = [c for c in cats if P[c]]
            dist, p = perm_p(E, P, pc, rng)
            row.update(distance=round(dist, 3), p=round(p, 4))
        rows.append(row)
    scored = sorted((r for r in rows if "p" in r), key=lambda r: r["p"])
    n = len(scored)
    for i, r in enumerate(scored):        # Benjamini-Hochberg
        r["q"] = round(min(1.0, min(s["p"] * n / (j + 1) for j, s in enumerate(scored) if j >= i)), 4)
    (HERE / "probes" / "provider_audit.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n")
    print(f"{'endpoint':52s} {'prec':7s} {'$out/M':>7s} {'id as':28s} {'rank':>4s} {'dist':>6s} {'q':>6s}")
    for r in sorted(rows, key=lambda r: r["endpoint"]):
        if "identified_as" not in r:
            print(f"{r['endpoint']:52s} {r.get('status')}")
            continue
        if "p" not in r:
            r.update(distance=float("nan"), q=float("nan"))
        print(f"{r['endpoint']:52s} {str(r.get('quantization')):7s} {float(r['price_out']) * 1e6:7.2f} "
              f"{r['identified_as']:28s} {r['rank_of_claim']:4d} {r['distance']:6.3f} {r['q']:6.3f}")


if __name__ == "__main__":
    main()
