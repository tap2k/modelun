"""probe_local_census.py: compare a census battery run locally (mlx-lm) with the same model's API census, for
panel models whose OpenRouter endpoint is gone but whose weights are open (Hermes 4 70B, Granite 4.1 8B).

The local run is harness/local.py, which writes Contract A to transcripts-local/<battery>/<label>.json
(<label>_<framing>.json for a framing other than the chat template), stamped with host "local-mlx", the
weights, quantization and Hub revision. Prompts, temperature (1.0) and the absence of a system prompt
follow the battery's spec; replies are capped at 256 tokens (the spec's 1024 is a ceiling for reasoning
models, and these answer in a few tokens). The models and their loader fixes are in harness/ladders.json.
Nothing here is merged into the API transcripts: calibrate first, by comparing the local 31-category census
with the model's API census, against the panel's resampling baseline (modal agreement ~0.81, main vs extra).

    ../../.venv/bin/python ../../harness/local.py --study . --spec spec/stimulus.json \\
        --pipeline hermes-4-70b --stage final --out transcripts-local/census
    ../../.venv/bin/python probe_local_census.py --label hermes-4-70b [--suffix _nosys]
"""
import argparse
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from analyze import load  # noqa: E402


def modal(path):
    """{category: modal answer} of one transcript, scored as the panel's are."""
    (cats,) = load(HERE, "census", paths=[path]).values()
    return {c: Counter(a).most_common(1)[0][0] for c, a in cats.items()}


def compare(a):
    api, loc = modal(HERE / "transcripts" / f"{a.label}.json"), modal(HERE / "transcripts-local" / "census" / f"{a.label}{a.suffix}.json")
    both = [c for c in api if c in loc]
    agree = sum(api[c] == loc[c] for c in both)
    print(f"{a.label}: modal answer agrees in {agree}/{len(both)} categories ({agree / max(len(both), 1):.2f}); "
          f"panel resampling baseline ~0.81 (main vs extra, 4 vs 4 runs)")
    for c in both:
        if api[c] != loc[c]:
            print(f"  {c:16s} api {api[c]:14s} local {loc[c]}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True)
    ap.add_argument("--suffix", default="", help="file suffix of a framing variant, e.g. _nosys")
    compare(ap.parse_args())
