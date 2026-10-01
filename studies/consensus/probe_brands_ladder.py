"""probe_brands_ladder.py — the brand battery on local stage ladders, with and without identity prompts.

Asks the 37-category brand battery (spec/stimulus_brands.json) of every stage of OLMo 3.1 32B and
Nemotron 3.5 Lightning, 20 samples per category at temperature 1, through harness/local.py. Base stages
run raw. Instruct stages run with no system prompt (nosys) and with the template as shipped (chat). The
final stages add a named prompt: OLMo's training-time systrain and its released "You are Olmo..." template;
Nemotron's sysid ("You are Nemotron..."). This separates what the weights say from what a serving prompt
adds, for self-naming ("Name an AI assistant") and every other brand default.

Run one pipeline per process: two large checkpoints resident at once overload a 64 GB machine and Metal
returns garbage logits. Run under caffeinate, since a sleeping Mac stalls loads from the external drive.

    caffeinate -ims ../../.venv/bin/python probe_brands_ladder.py olmo31-32b         # -> probes/brands_ladder_32b/
    caffeinate -ims ../../.venv/bin/python probe_brands_ladder.py nemotron35-lightning  # -> probes/brands_ladder_nemotron/
"""
import json, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "harness"))
import local

SPEC = json.loads((HERE / "spec" / "stimulus_brands.json").read_text())
RUNS = 20
PLAN = {"olmo31-32b": ("brands_ladder_32b", {"base": ["raw"], "sft": ["nosys", "chat"], "dpo": ["nosys", "chat"],
                                             "rl": ["nosys", "systrain", "chat"]}),
        "nemotron35-lightning": ("brands_ladder_nemotron", {"base": ["raw"], "final": ["chat", "sysid"]})}


def main(pipeline):
    import mlx.core as mx
    name, stages = PLAN[pipeline]
    for stage, framings in stages.items():
        st = local.stage(pipeline, stage)
        t0 = time.time()
        model = local.load(st)
        print(f"loaded {st['label']} in {time.time() - t0:.0f}s", flush=True)
        for f in framings:
            local.run(SPEC, st, f, RUNS, local.path(HERE / "probes" / name, st, f),
                      max_tokens=24 if f == "raw" else 48, batch=8, model=model)
        del model
        mx.clear_cache()


if __name__ == "__main__":
    main(sys.argv[1])
