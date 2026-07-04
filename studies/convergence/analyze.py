"""
analyze.py — the convergence study's spine: transcripts -> answer-similarity -> analysis.json.

Reads every <study>/transcripts/<label>.json (Contract A), embeds each reply, and builds
per-prompt cross-model similarity. From those embeddings it derives:

  cross_pairs   = mean similarity across models, ALL runs vs ALL runs (honest about run noise)
  cross_centroid= mean similarity across models' per-model CENTROIDS (smooths run noise)
  within        = mean similarity across a model's own runs (self-consistency floor)

The gap between cross_pairs and cross_centroid IS the within-model-noise signal: when models
wobble run-to-run (they do — "name a number" gives 7,7,42), all-pairs reads lower than centroid.
We report both and never silently pick one.

Also: modal clustering (# distinct answers / plurality share) for discrete agreement, and Axis-B
per-model cross-FAMILY similarity (same-lineage pairs excluded) over spec/models.json metadata.

Deps kept lean: numpy for vector math, REST via requests for embeddings. NO LLM in the analysis
loop — an earlier LLM "cleaning" pass was tested and DROPPED (it hallucinated prose on short answers
and gave no aggregate lift; see OBSERVATIONS.md). Analysis is fully mechanical and reproducible.

Absolute cosine has no fixed zero (two unrelated texts embed ~0.1–0.64), so a bare cross number is
not directly interpretable — read it against a per-prompt baseline (see OBSERVATIONS.md; baselines
are the next design step). This script emits the raw numbers; views/ draws them.

    python studies/convergence/analyze.py --study studies/convergence
"""

import sys
import os
import json
import argparse
import itertools
from pathlib import Path

import numpy as np
import requests
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "harness"))
from study import Study  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(ROOT / ".env")


# ── pluggable strategies (embedder + metric) ─────────────────────────────────

def embed_openai(texts, model="text-embedding-3-small", batch=128):
    """texts -> list[vector]. Batches to the OpenAI embeddings REST endpoint."""
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        sys.exit("OPENAI_API_KEY not set (put it in .env).")
    out = []
    for i in range(0, len(texts), batch):
        chunk = texts[i:i + batch]
        r = requests.post(
            "https://api.openai.com/v1/embeddings",
            headers={"Authorization": f"Bearer {key}"},
            json={"model": model, "input": chunk},
            timeout=60,
        )
        r.raise_for_status()
        out.extend(e["embedding"] for e in r.json()["data"])
    return out


EMBEDDERS = {"openai/text-embedding-3-small": lambda t: embed_openai(t, "text-embedding-3-small"),
             "openai/text-embedding-3-large": lambda t: embed_openai(t, "text-embedding-3-large")}


def cosine(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(a @ b / (na * nb)) if na and nb else 0.0


METRICS = {"cosine": cosine}


def mean(xs):
    xs = [x for x in xs if x is not None]
    return float(np.mean(xs)) if xs else None


def modal_cluster(vecs, sim, threshold=0.80):
    """Greedy single-link clustering by similarity threshold -> (plurality_share, n_clusters).
    Generic across prompts (no hand-keyed categories): two answers are "the same" iff sim >=
    threshold. The honest metric for discrete agreement on short pattern-laden prompts, where
    cosine-mean undercounts modal clustering. Uses one representative vector per model."""
    n = len(vecs)
    if n == 0:
        return None, 0
    clusters = []
    for i in range(n):
        for cl in clusters:
            if sim(vecs[i], vecs[cl[0]]) >= threshold:
                cl.append(i)
                break
        else:
            clusters.append([i])
    sizes = sorted((len(c) for c in clusters), reverse=True)
    return sizes[0] / n, len(clusters)


# ── load ─────────────────────────────────────────────────────────────────────

def load_replies(study):
    """-> {label: {scene_id: [reply_text per run]}}. Skips failed/empty cells."""
    out = {}
    for p in sorted(study.transcripts_dir.glob("*.json")):
        d = json.loads(p.read_text())
        scenes = {}
        for sid, sc in d["scenes"].items():
            reps = [run[0]["reply"] for run in sc["runs"]
                    if run and run[0].get("reply")]
            if reps:
                scenes[sid] = reps
        out[d["model"]] = scenes
    return out


# ── analysis ─────────────────────────────────────────────────────────────────

def analyze(study, embedder_key, metric_key):
    embed = EMBEDDERS[embedder_key]
    sim = METRICS[metric_key]

    meta = {m["label"]: m for m in json.loads((study.root / "spec" / "models.json").read_text())["models"]}
    spec = study.stimulus()
    scene_ids = [s["id"] for s in spec["scenes"]]
    replies = load_replies(study)

    # Embed every reply once, keyed by (label, sid, run_idx). No normalization — raw text.
    flat_keys, flat_texts = [], []
    for label, scenes in replies.items():
        for sid, reps in scenes.items():
            for i, txt in enumerate(reps):
                flat_keys.append((label, sid, i))
                flat_texts.append(txt)
    print(f"embedding {len(flat_texts)} replies via {embedder_key} …")
    vecs = dict(zip(flat_keys, embed(flat_texts)))

    def runs_of(label, sid):
        return [vecs[(label, sid, i)] for i in range(len(replies[label][sid]))]

    def centroid(label, sid):
        return list(np.mean(np.asarray(runs_of(label, sid), float), axis=0))

    labels = [lab for lab in replies if replies[lab]]

    per_prompt = {}
    for sid in scene_ids:
        present = [lab for lab in labels if sid in replies[lab]]

        # within-model floor: mean pairwise sim over a model's own runs
        within = {lab: mean(sim(a, b) for a, b in itertools.combinations(runs_of(lab, sid), 2))
                  for lab in present}

        # cross-model, ALL runs vs ALL runs across distinct models (honest about run noise)
        allpair = []
        for a, b in itertools.combinations(present, 2):
            for va in runs_of(a, sid):
                for vb in runs_of(b, sid):
                    allpair.append(sim(va, vb))

        # cross-model via per-model CENTROID (smooths run noise)
        cents = {lab: centroid(lab, sid) for lab in present}
        cpair = {f"{a}|{b}": sim(cents[a], cents[b]) for a, b in itertools.combinations(present, 2)}

        open_labs = [l for l in present if meta.get(l, {}).get("open")]
        closed_labs = [l for l in present if not meta.get(l, {}).get("open")]

        def tier(subset, allruns):
            if allruns:
                ps = [sim(va, vb) for a, b in itertools.combinations(subset, 2)
                      for va in runs_of(a, sid) for vb in runs_of(b, sid)]
            else:
                ps = [cpair[f"{a}|{b}"] for a, b in itertools.combinations(subset, 2) if f"{a}|{b}" in cpair]
            return mean(ps)

        plur, ndist = modal_cluster([cents[l] for l in present], sim)

        per_prompt[sid] = {
            "subtitle": next((s.get("subtitle", sid) for s in spec["scenes"] if s["id"] == sid), sid),
            "n_models": len(present),
            "cross_pairs": mean(allpair),                 # all-runs cross-model (noise-honest)
            "cross_centroid": mean(cpair.values()),       # centroid cross-model (noise-smoothed)
            "cross_pairs_closed": tier(closed_labs, True),
            "cross_pairs_open": tier(open_labs, True),
            "cross_centroid_closed": tier(closed_labs, False),
            "cross_centroid_open": tier(open_labs, False),
            "within_mean": mean(within.values()),
            "within_by_model": within,
            "plurality_share": plur,
            "n_distinct": ndist,
            "centroid_matrix": cpair,
        }

    # ── Per-model layer: characterize the MODEL, not the prompt. ─────────────────────────
    # HEADLINE metric = UNIQUENESS = distance from consensus ("does this model give a DIFFERENT
    # answer, or the same one everyone gives"). The buyer's question. Roster-relative on purpose,
    # centroid-based (robust to the temperature confound), no packaging strip needed.
    #   Secondary/context: conformity_field (flat, doesn't discriminate), self_consistency (largely
    #   effective-TEMPERATURE — see exact_dup_rate — NOT "voice"), exact_dup_rate (near-greedy proxy).
    # NOT computed: a "distinctiveness / recognizable-voice" NN-attribution metric was tried and
    # DROPPED — it conflated packaging tics, determinism, and style, and flipped ranking with each
    # definition (text embeddings entangle style/topic/packaging). See OBSERVATIONS.md.
    per_model = {}
    for lab in labels:
        fam = meta.get(lab, {}).get("family")
        field, pool, selfsim = [], [], []
        for sid in scene_ids:
            if sid not in replies[lab]:
                continue
            va = centroid(lab, sid)
            for other in labels:
                if other == lab or sid not in replies[other]:
                    continue
                s = sim(va, centroid(other, sid))
                pool.append(s)
                if meta.get(other, {}).get("family") != fam:
                    field.append(s)
            rv = runs_of(lab, sid)
            if len(rv) > 1:
                selfsim.append(mean(sim(a, b) for a, b in itertools.combinations(rv, 2)))
        conf_field = mean(field)
        conf_pool = mean(pool)
        self_cons = mean(selfsim)

        # UNIQUENESS = distance from consensus (the headline: "gives different answers, not the
        # crowd's"). Per prompt: 1 - cos(this model's centroid, mean of OTHER models' centroids).
        # Roster-relative on purpose (unique vs the current field). Centroid-based → robust to the
        # temperature confound. No packaging strip needed (tics wash out into the consensus equally).
        uniq = []
        for sid in scene_ids:
            if sid not in replies[lab]:
                continue
            others = [centroid(o, sid) for o in labels if o != lab and sid in replies[o]]
            if not others:
                continue
            cons = np.mean(np.asarray(others, float), axis=0)
            uniq.append(1 - sim(centroid(lab, sid), cons))

        # exact_dup_rate = effective-temperature proxy. Fraction of prompts where 2+ of a model's 3
        # runs are BYTE-IDENTICAL → near-greedy. We send temp=1.0 but many models ignore it; this
        # exposes that. self_consistency is thus largely EFFECTIVE-TEMP, not "a committed voice".
        dup, tot = 0, 0
        for sid in scene_ids:
            reps = replies[lab].get(sid, [])
            if len(reps) >= 2:
                tot += 1
                if len(set(reps)) < len(reps):
                    dup += 1

        per_model[lab] = {
            "family": fam,
            "generation": meta.get(lab, {}).get("generation"),
            "size_tier": meta.get(lab, {}).get("size_tier"),
            "open": meta.get(lab, {}).get("open"),
            # HEADLINE: gives-different-answers score (consensus distance), roster-relative, temp-robust
            "uniqueness": mean(uniq),
            # effective-temperature proxy — reframes self_consistency (see below)
            "exact_dup_rate": (dup / tot) if tot else None,
            "self_consistency": self_cons,   # NOTE: largely effective-temp, NOT "voice" — read with exact_dup_rate
            # secondary / roster-dependent context (kept, not headlined)
            "conformity_field": conf_field,
            "cross_family_mean": conf_field,   # alias — Axis B uses this name
        }

    return {
        "embedder": embedder_key,
        "metric": metric_key,
        "scene_order": scene_ids,
        "per_prompt": per_prompt,
        "per_model": per_model,
    }


def main():
    ap = argparse.ArgumentParser(description="Convergence analysis: transcripts -> analysis.json.")
    ap.add_argument("--study", default=str(Path(__file__).resolve().parent))
    ap.add_argument("--embedder", default="openai/text-embedding-3-small", choices=list(EMBEDDERS))
    ap.add_argument("--metric", default="cosine", choices=list(METRICS))
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    study = Study(args.study)
    result = analyze(study, args.embedder, args.metric)
    out = Path(args.out) if args.out else Path(args.study) / "analysis.json"
    out.write_text(json.dumps(result, indent=2) + "\n")

    print(f"\n→ {out}\n")
    print("prompt          pairs  centroid  within | closed_c open_c | plur  #dist")
    for sid in result["scene_order"]:
        p = result["per_prompt"].get(sid)
        if not p:
            continue
        def f(x): return f"{x:.3f}" if x is not None else "  –  "
        def pc(x): return f"{x:.0%}" if x is not None else " – "
        print(f"  {sid:<13} {f(p['cross_pairs'])} {f(p['cross_centroid'])}  {f(p['within_mean'])} |"
              f"  {f(p['cross_centroid_closed'])} {f(p['cross_centroid_open'])} |"
              f" {pc(p['plurality_share']):>4}  {p['n_distinct']}")

    # Per-model layer: UNIQUENESS (distance from consensus) is the headline. exact_dup_rate is the
    # effective-temperature proxy that reframes self_consistency (temp=1.0 is sent but not honored).
    print("\nPER-MODEL  (uniqueness = distance from consensus; higher = gives more DIFFERENT answers)")
    print(f"  {'model':<26}{'uniq':>7}{'self_cons':>10}{'dup_rate':>9}  (dup=effective-temp proxy)")
    pm = result["per_model"]
    for lab in sorted(pm, key=lambda l: -(pm[l]['uniqueness'] or 0)):
        m = pm[lab]
        def g(x): return f"{x:.3f}" if x is not None else "  –  "
        print(f"  {lab:<26}{g(m['uniqueness']):>7}{g(m['self_consistency']):>10}{g(m['exact_dup_rate']):>9}")


if __name__ == "__main__":
    main()
