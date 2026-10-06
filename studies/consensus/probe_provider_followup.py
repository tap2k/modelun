"""probe_provider_followup.py — score the follow-up runs on the provider audit's four mismatches.

Reads transcripts-providers/followup-<date>/<arm>/ (run_provider_followup.py) and scores each endpoint as
probe_provider_audit.py does:
  identified_as / rank_of_claim   among the panel's profiles (no system prompt), by likelihood
  distance / p / q                (sysgen arm) against the pooled answers of the same model's other endpoints in the
                                  same arm, by permutation; Benjamini-Hochberg within the arm
  billed_prompt_tokens            median billed prompt_tokens per call, and the surplus over the peers' median

  plain   the four mismatches on a later day, no system prompt: do they still not identify as claimed?
  sysgen  every endpoint of the four models under "You are a helpful assistant.": with a default prompt replaced
          by ours, do the mismatches identify as claimed, as their peers do?

    ../../.venv/bin/python probe_provider_followup.py [--date 2026-10-06]
    # -> transcripts-providers/followup-<date>/followup.json (names providers; stays out of git)
"""
import json, math, random, statistics as st, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from analyze import answers
from probe_fingerprint import panel
from probe_provider_audit import endpoint_answers, perm_p

ROOT = HERE / "transcripts-providers"


def billed(d):
    pts = [(t.get("usage") or {}).get("prompt_tokens") for f in d.glob("*/*.json")
           for s in json.loads(f.read_text())["scenes"].values() for r in s["runs"] for t in r]
    pts = [p for p in pts if p is not None]
    return st.median(pts) if pts else None


def main():
    day = sys.argv[sys.argv.index("--date") + 1] if "--date" in sys.argv else "2026-10-06"
    base = ROOT / f"followup-{day}"
    meta = json.loads((ROOT / "endpoints-2026-10-02.json").read_text())
    A = panel()
    models = sorted(A)
    field_c, field_e = answers(HERE), answers(HERE, "expanded")
    vocab = {c: len({a for m in models for a in A[m].get(c, [])}) + 1 for m in models for c in A[m]}
    rng = random.Random(0)
    out = {}
    for arm_dir in sorted(p for p in base.iterdir() if p.is_dir()):
        arm = arm_dir.name
        keys = sorted(str(p.relative_to(arm_dir)) for p in arm_dir.glob("*/*") if p.is_dir())
        ans = {k: endpoint_answers(arm_dir / k, field_c, field_e) for k in keys}
        rows = []
        for k in keys:
            info, E = meta[k], ans[k]
            claim = info["model"].split("/")[1]
            row = {"endpoint": k, "quantization": info.get("quantization"), "billed_prompt_tokens": billed(arm_dir / k)}
            cats = [c for c in E if len(E[c]) >= 2 and len(A[claim].get(c, [])) >= 4]
            if not cats:
                rows.append({**row, "status": "no data"})
                continue
            score = {m: sum(math.log((Counter(A[m].get(c, []))[a] + 0.1) / (len(A[m].get(c, [])) + 0.1 * vocab[c]))
                            for c in cats for a in E[c]) for m in models}
            ranked = sorted(models, key=score.get, reverse=True)
            row.update(questions=len(cats), identified_as=ranked[0], rank_of_claim=ranked.index(claim) + 1,
                       margin_nats_per_q=round((score[ranked[0]] - score[claim]) / len(cats), 2))
            peers = [p for p in keys if p != k and meta[p]["model"] == info["model"] and ans[p]]
            if peers:
                P = {c: [a for p in peers for a in ans[p].get(c, [])] for c in cats}
                pc = [c for c in cats if P[c]]
                dist, p = perm_p(E, P, pc, rng)
                row.update(peers=len(peers), distance=round(dist, 3), p=round(p, 4))
                pb = [billed(arm_dir / q) for q in peers]
                pb = [b for b in pb if b is not None]
                if pb and row["billed_prompt_tokens"] is not None:
                    row["billed_surplus_vs_peer_median"] = row["billed_prompt_tokens"] - st.median(pb)
            rows.append(row)
        scored = sorted((r for r in rows if "p" in r), key=lambda r: r["p"])
        for i, r in enumerate(scored):
            r["q"] = round(min(1.0, min(s["p"] * len(scored) / (j + 1) for j, s in enumerate(scored) if j >= i)), 4)
        out[arm] = rows
        print(f"== {arm}")
        for r in rows:
            print(f"  {r['endpoint']:50s} {str(r.get('identified_as', r.get('status'))):30s} rank {r.get('rank_of_claim')}"
                  f"  dist {r.get('distance')}  q {r.get('q')}  billed {r.get('billed_prompt_tokens')}"
                  f" ({r.get('billed_surplus_vs_peer_median')})")
    (base / "followup.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"-> {base / 'followup.json'}")


if __name__ == "__main__":
    main()
