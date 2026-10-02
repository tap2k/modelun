"""probe_verb_ladder.py — where in training do typical answers and preferred answers form?

The verb ladder on each stage of an open pipeline: "Name a X" (the typical example) and "Choose a X" (a preference)
for the 96 census + expanded categories, and Name, Choose and free Name ("Name a X." with no reply instruction) for
the 41 brand categories. 20 samples per question at temperature 1, through harness/local.py. The base stage runs
raw (plain completion) on the Name questions only, since an instruction verb means little to a base model; the
tuned stages run nosys (the chat turn without the template's default system prompt).

Predictions recorded before the run (Converging on Serendipity plan, 2026-10-02): Claude, Name fixes at SFT while
Choose moves at DPO or RL; Tapan, everything forms at SFT.

One stage at a time: the weights are loaded (downloaded from the Hub if needed), every spec is run, the model is
freed, and --delete-cache removes the stage's Hub cache before the next, so a 7B ladder never needs more than one
stage on disk.

    caffeinate -ims ../../.venv/bin/python probe_verb_ladder.py olmo3-7b --delete-cache              # Name/Choose/free
    caffeinate -ims ../../.venv/bin/python probe_verb_ladder.py olmo3-7b --recommend --delete-cache  # one-turn recommend, 41 brands
"""
import json, shutil, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "harness"))
import local

RUNS = 20
NAME = ["spec/stimulus.json", "spec/stimulus_expanded.json", "spec/stimulus_brands.json", "spec/stimulus_brands_ext.json"]
CHOOSE = ["spec/perturb/stimulus_choose.json", "spec/perturb/stimulus_expanded_choose.json",
          "spec/perturb/stimulus_brands_choose.json", "spec/perturb/stimulus_brands_ext_choose.json"]
FREE = ["spec/clamp_free_all.json", "spec/clamp_free_brands_ext.json"]


def free_brand_spec():
    """Free brand questions only (the clamp_free_all spec also holds census and expanded categories)."""
    scenes = []
    for f in FREE:
        scenes += [s for s in json.loads((HERE / f).read_text())["scenes"] if s["id"].startswith("brand_")]
    for f in ("spec/clamp_ext.json",):
        scenes += [s for s in json.loads((HERE / f).read_text())["scenes"] if s["id"].startswith("brand_") and s["id"].endswith("_free")]
    return {"spec_version": "verb-ladder-free-brands", "system_prompt": None, "scenes": scenes}


def tuned_framing(st):
    """No system prompt: nosys where the pipeline writes it out (OLMo), else the chat template, for pipelines whose
    template adds no system prompt of its own (Tulu 3, Nemotron 3.5 final)."""
    return "nosys" if st.get("nosys") else "chat"


def stages(pipeline):
    """The pipeline's stages, with --weights stage=path overrides (e.g. a local copy instead of the external drive)."""
    over = dict(a.split("=", 1) for a in sys.argv if "=" in a and not a.startswith("-"))
    return [{**st, "weights": over.get(st["stage"], st["weights"])} for st in local.stages(pipeline)]


def main(pipeline, delete_cache):
    out = HERE / "probes" / f"verb_ladder_{pipeline}"
    for st in stages(pipeline):
        base = st["stage"] == "base"
        framing = "raw" if base else tuned_framing(st)
        jobs = [(f, 24 if base else 48) for f in NAME] + ([] if base else [(f, 48) for f in CHOOSE])
        t0 = time.time()
        model = local.load(st)
        print(f"loaded {st['label']} in {time.time() - t0:.0f}s", flush=True)
        for f, mt in jobs:
            spec = json.loads((HERE / f).read_text())
            local.run(spec, st, framing, RUNS, local.path(out / Path(f).stem, st, framing), max_tokens=mt, batch=16, model=model)
        if not base:
            local.run(free_brand_spec(), st, framing, RUNS, local.path(out / "free_brands", st, framing), max_tokens=256,
                      batch=16, model=model)
        del model
        local.free()
        if delete_cache and not st["weights"].startswith(("/", "~")):
            cache = Path.home() / ".cache/huggingface/hub" / ("models--" + st["weights"].replace("/", "--"))
            shutil.rmtree(cache, ignore_errors=True)
            print(f"deleted cache {cache.name}", flush=True)


if __name__ == "__main__" and "--recommend" not in sys.argv:
    main(sys.argv[1], "--delete-cache" in sys.argv)


def recommend_spec():
    """One turn, 'Can you recommend <noun>?', for all 41 brand categories (battery + extension), the noun taken from
    the battery question ('Name a soda brand. Reply with the name only.' -> 'a soda brand')."""
    scenes = []
    for f in ("spec/stimulus_brands.json", "spec/stimulus_brands_ext.json"):
        for sc in json.loads((HERE / f).read_text())["scenes"]:
            noun = sc["turns"][0].removeprefix("Name ").split(". Reply with")[0]
            scenes.append({"id": f"{sc['id']}__recommend", "turns": [f"Can you recommend {noun}?"]})
    return {"spec_version": "verb-ladder-recommend-1turn", "system_prompt": None, "scenes": scenes}


def recommend_pass(pipeline, delete_cache):
    """The one-turn recommend question on the tuned stages (a base model does not take requests)."""
    out = HERE / "probes" / f"verb_ladder_{pipeline}" / "recommend"
    spec = recommend_spec()
    for st in stages(pipeline):
        if st["stage"] == "base":
            continue
        model = local.load(st)
        f = tuned_framing(st)
        local.run(spec, st, f, RUNS, local.path(out, st, f), max_tokens=512, batch=16, model=model)
        del model
        local.free()
        if delete_cache and not st["weights"].startswith(("/", "~")):
            shutil.rmtree(Path.home() / ".cache/huggingface/hub" / ("models--" + st["weights"].replace("/", "--")), ignore_errors=True)


if __name__ == "__main__" and "--recommend" in sys.argv:
    recommend_pass(sys.argv[1], "--delete-cache" in sys.argv)
