"""probe_olmo_ladder.py — does post-training put "serendipity" into any_word? Stage ladders of open pipelines.

The census any_word item ("Pick a word. Reply with one word only.") has serendipity as its modal
answer, rising with release date, near 0% on lightly tuned models and 100% on Hermes 3 405B. The
hypothesis under test: pretraining links the prompt to charming words, preference tuning rewards
serendipity, RL collapses onto it. OLMo 3 publishes every stage of one pipeline, so each stage is
sampled locally (harness/local.py: mlx-lm, temperature 1, no system prompt of our own). The pipelines
and their stages are in harness/ladders.json:

  --7b        olmo3-7b              base / SFT / DPO / RL, bf16            -> probes/olmo_ladder/
  --32b       olmo31-32b            base / SFT / DPO / RL, 8-bit           -> probes/olmo_ladder_32b/
  --nemotron  nemotron35-lightning  base / final, 8-bit                    -> probes/nemotron_ladder/
  --tulu      tulu3-8b              Tulu 3 on Llama 3.1 8B, bf16           -> probes/tulu_ladder/
  --rlzero    olmo3-7b-rlzero       RL straight from the 7B base, bf16     -> probes/rlzero_ladder/

Framings (harness/local.py): raw for the base, then the stage's defaults, and raw as well. chat is the
stage's own template, with whatever default system prompt it inserts (OLMo 3 7B: "You are a helpful
function-calling AI assistant..."); nosys is the same turn without it; sysgen, systrain, sysid and think
are the other framings asked for over time. raw is 'Pick a word. Reply with one word only.\\nAnswer:',
first word kept.

Each stage/framing is one Contract-A transcript in probes/<name>/ (scene any_word); probes/<name>.json
holds the summary. Template framings are scored with the census norm(); raw and cloze keep the first
word, since a base model has no stop convention. Share = serendipity / valid answers, Wilson 95% CI.
    ../../.venv/bin/python probe_olmo_ladder.py --7b [N=50]   # needs mlx-lm and the weights
    ../../.venv/bin/python probe_olmo_ladder.py --7b --score  # re-score probes/olmo_ladder/ only
    options: --tag NAME (separate output), --framings chat,nosys,... (instruct stages),
    --prompt "..." swaps the question (the say/pick/favorite/beautiful scale), --cloze '...' gives the
    base stage a natural completion instead of the instruction plus "Answer:"
"""
import json, math, re, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent                      # studies/consensus
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "harness"))
from analyze import norm                                    # same normalization as the paper
import local

SIZE = next((k for k in ("32b", "nemotron", "tulu", "rlzero") if f"--{k}" in sys.argv), "7b")
PIPELINE = {"7b": "olmo3-7b", "32b": "olmo31-32b", "nemotron": "nemotron35-lightning", "tulu": "tulu3-8b",
            "rlzero": "olmo3-7b-rlzero"}[SIZE]


def _arg(flag):
    return sys.argv[sys.argv.index(flag) + 1] if flag in sys.argv else None


TAG = _arg("--tag")                                       # a separate output, e.g. --tag n200
FRAMINGS = _arg("--framings")                             # override the instruct stages' framings
NAME = {"7b": "olmo_ladder", "32b": "olmo_ladder_32b", "nemotron": "nemotron_ladder", "tulu": "tulu_ladder",
        "rlzero": "rlzero_ladder"}[SIZE] + (f"_{TAG}" if TAG else "")
DIR, OUT = HERE / "probes" / NAME, HERE / "probes" / f"{NAME}.json"
PROMPT = _arg("--prompt") or "Pick a word. Reply with one word only."   # --prompt: another item of the scale
CLOZE = _arg("--cloze")                                   # base stage only: a natural completion, e.g. 'My favorite word is "'


def framings(st):
    if st["stage"] == "base":
        return ["cloze"] if CLOZE else ["raw"]
    return FRAMINGS.split(",") if FRAMINGS else st["framings"] + ["raw"]


def first_word(text):
    m = re.search(r"[A-Za-z][A-Za-z'-]*", text)
    return m.group(0).lower().strip("'-") if m else None


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(c - h, 0.0), min(c + h, 1.0))


def sample(n):
    for st in local.stages(PIPELINE):
        todo = [f for f in framings(st) if not local.path(DIR, st, f).exists()]
        if not todo:
            continue
        model = local.load(st)
        for framing in todo:
            spec = {"spec_version": "probe_olmo_ladder",
                    "scenes": [{"id": "any_word", "turns": [CLOZE if framing == "cloze" else PROMPT]}]}
            local.run(spec, st, framing, n, local.path(DIR, st, framing), local.MAX_TOKENS.get(framing, 24), model=model)
        del model
        local.free()


def score():
    """Every transcript in DIR, in ladder order -> {stage/framing: summary}."""
    order = [st["stage"] for st in local.stages(PIPELINE)]
    runs = sorted((json.loads(p.read_text()) for p in DIR.glob("*.json")),
                  key=lambda d: (order.index(d["stage"]), d["framing"]))
    summary = {}
    for d in runs:
        key, framing = f"{d['stage']}/{d['framing']}", d["framing"]
        replies = [r[0]["reply"] for r in d["scenes"]["any_word"]["runs"]]
        score_fn = first_word if framing in ("raw", "cloze") else norm
        answers = [score_fn(r) if r else None for r in replies]   # think: an unclosed trace has no reply
        valid = [a for a in answers if a]
        k = sum(a == "serendipity" for a in valid)
        c = Counter(valid)
        lo, hi = wilson(k, len(valid))
        h = -sum(v / len(valid) * math.log2(v / len(valid)) for v in c.values()) if valid else 0.0
        summary[key] = {"n": len(answers), "valid": len(valid), "serendipity": k,
                        "share": round(k / len(valid), 3) if valid else None,
                        "ci95": [round(lo, 3), round(hi, 3)], "distinct": len(c),
                        "entropy_bits": round(h, 2), "top": c.most_common(8)}
        print(f"{key:10s} valid={len(valid):2d}/{len(answers)} serendipity={k:2d} "
              f"({100 * k / max(len(valid), 1):3.0f}%, CI {100 * lo:.0f}-{100 * hi:.0f})  "
              f"H={h:.2f}  " + ", ".join(f"{w}×{n}" for w, n in c.most_common(6)))
    return summary


if __name__ == "__main__":
    if "--score" not in sys.argv:
        nums = [a for a in sys.argv[1:] if a.isdigit()]
        sample(int(nums[0]) if nums else 50)
    OUT.write_text(json.dumps({"summary": score()}, indent=1, ensure_ascii=False) + "\n")
