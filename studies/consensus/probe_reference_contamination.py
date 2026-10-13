"""probe_reference_contamination.py — are the panel profiles of the audited models mixed with the endpoints the audit flags?

The panel transcripts were collected through OpenRouter's default routing and record no provider, so a model's
reference profile may include answers from any of its providers, the flagged ones among them. Two checks, from
files already on disk (no API calls):

  mixture   For each audited model with a mismatched endpoint, the share of the panel profile's answers that came
            from that endpoint, estimated by EM over a two-part mixture: the mismatch's answer distribution and the
            pooled distribution of the model's endpoints that identify as claimed. Per source file (transcripts/,
            -extra/, -expanded/) and overall. A share near zero means the profile is clean of that endpoint.

  pinned    Every audited endpoint rescored with its claimed model's profile replaced by a pinned one: eight answers
            per question drawn (seeded) from the same model's other endpoints that identify as claimed on the audit
            day, the endpoint itself left out. Other models keep their panel profiles. Reports the claimed model's
            rank and margin under both references. The margin is the claimed model's score minus the best other
            model's, in nats per question; positive means identified. Over the matching endpoints it is the
            honest-endpoint null for reading a mismatch.

    ../../.venv/bin/python probe_reference_contamination.py   # -> probes/reference_contamination.json

Reads transcripts-providers/ and probes/provider_audit.json, which name providers and stay out of git; the output
keys endpoints by model and a letter, not by provider.
"""
import json, math, random, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from analyze import against, answers, load
from probe_fingerprint import panel
from probe_provider_audit import ROOT, endpoint_answers

K = 0.1


def prob(counts, n, v):
    return lambda a: (counts[a] + K) / (n + K * v)


def mixture(obs, px, ph, iters=200):
    """EM for the share w of answers drawn from px rather than ph."""
    w = 0.5
    for _ in range(iters):
        r = [w * px(c, a) / (w * px(c, a) + (1 - w) * ph(c, a)) for c, a in obs]
        w = sum(r) / len(r)
    return w


def main():
    A = panel()
    models = sorted(A)
    field_c, field_e = answers(HERE), answers(HERE, "expanded")
    extra = against(field_c, load(HERE, "census", paths=sorted((HERE / "transcripts-extra").glob("*.json"))), HERE)
    sources = {"transcripts": field_c, "transcripts-extra": extra, "transcripts-expanded": field_e}
    meta = json.loads(sorted(ROOT.glob("endpoints-*.json"))[-1].read_text())
    audit = {r["endpoint"]: r for r in json.loads((HERE / "probes" / "provider_audit.json").read_text())}
    vocab = {c: len({a for m in models for a in A[m].get(c, [])}) + 1 for m in models for c in A[m]}
    ans = {key: endpoint_answers(ROOT / key, field_c, field_e) for key in meta}
    rng = random.Random(0)

    by_model = {}
    for key, info in sorted(meta.items()):
        claim = info["model"].split("/")[1]
        if claim in A and audit[key].get("rank_of_claim"):
            by_model.setdefault(claim, []).append(key)
    alias = {key: f"{claim}/{chr(65 + i)}" for claim, keys in by_model.items() for i, key in enumerate(keys)}

    def pooled(keys, c):
        return [a for k in keys for a in ans[k].get(c, [])]

    out = {"mixture": [], "pinned": []}
    for claim, keys in sorted(by_model.items()):
        honest = [k for k in keys if audit[k]["rank_of_claim"] == 1]
        for x in (k for k in keys if audit[k]["rank_of_claim"] != 1):
            cache = {}

            def dist(pool_keys, c, tag):
                if (tag, c) not in cache:
                    p = pooled(pool_keys, c)
                    cache[tag, c] = prob(Counter(p), len(p), vocab.get(c, 1))
                return cache[tag, c]
            px = lambda c, a: dist([x], c, "x")(a)
            ph = lambda c, a: dist(honest, c, "h")(a)
            row = {"endpoint": alias[x], "identified_as": audit[x]["identified_as"], "honest_peers": len(honest)}
            allobs = []
            for name, src in sources.items():
                obs = [(c, a) for c, v in src.get(claim, {}).items() if ans[x].get(c) and pooled(honest, c) for a in v]
                allobs += obs
                row[name] = {"answers": len(obs), "share": round(mixture(obs, px, ph), 3) if obs else None}
            row["overall"] = {"answers": len(allobs), "share": round(mixture(allobs, px, ph), 3)}
            out["mixture"].append(row)

        for key in keys:
            E = ans[key]
            cats = [c for c in E if len(E[c]) >= 2 and len(A[claim].get(c, [])) >= 4]
            refs = [k for k in keys if k != key and audit[k]["rank_of_claim"] == 1]
            row = {"endpoint": alias[key], "audit_rank": audit[key]["rank_of_claim"], "questions": len(cats),
                   "pinned_peers": len(refs)}
            for name, prof in (("panel", A[claim]), ("pinned", None)):
                if prof is None:
                    if not refs:
                        continue
                    prof = {}
                    for c in cats:
                        p = pooled(refs, c)
                        prof[c] = rng.sample(p, 8) if len(p) >= 8 else p
                score = {m: sum(math.log((Counter((prof if m == claim else A[m]).get(c, []))[a] + K) /
                                         (len((prof if m == claim else A[m]).get(c, [])) + K * vocab[c]))
                                for c in cats for a in E[c]) for m in models}
                ranked = sorted(models, key=score.get, reverse=True)
                best_other = max(score[m] for m in models if m != claim)
                row[name] = {"identified_as": ranked[0], "rank": ranked.index(claim) + 1,
                             "margin_nats_per_q": round((score[claim] - best_other) / len(cats), 3)}
            out["pinned"].append(row)

    (HERE / "probes" / "reference_contamination.json").write_text(json.dumps(out, indent=1) + "\n")
    for r in out["mixture"]:
        print(r["endpoint"], "->", r["identified_as"], {k: v for k, v in r.items() if k.startswith(("trans", "overall"))})
    for r in out["pinned"]:
        print(f"{r['endpoint']:42s} audit rank {r['audit_rank']:3d}  panel {r['panel']['rank']:3d} {r['panel']['margin_nats_per_q']:+.2f}"
              + (f"  pinned {r['pinned']['rank']:3d} {r['pinned']['margin_nats_per_q']:+.2f} ({r['pinned']['identified_as']})" if "pinned" in r else "  no pinned peers"))


if __name__ == "__main__":
    main()
