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
    caffeinate -ims ../../.venv/bin/python probe_verb_ladder.py olmo3-7b --pick2 --delete-cache      # then "Which one would you pick?"
    caffeinate -ims ../../.venv/bin/python probe_verb_ladder.py olmo3-7b --pick2 --turn1-from=sft --picks=5 --delete-cache
"""
import json, shutil, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "harness"))
import local

RUNS = 20
# One-turn recommend replies run to 512 tokens; at 32B a stage takes many hours, so recommend samples 10 per question
# from 2026-10-04 (OLMo 3 7B, Tulu 3 8B and the Nemotron final stage were run at 20).
RECOMMEND_RUNS = 10
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


def drop_cache(repo):
    """Remove a repo's Hub cache, weights included. The model folder holds only symlinks into the shared blob store
    (hub/blobs), so deleting the folder alone frees nothing; huggingface_hub's cache API deletes the blobs too."""
    from huggingface_hub import scan_cache_dir
    cache = scan_cache_dir()
    revs = [r.commit_hash for repo_info in cache.repos if repo_info.repo_id == repo for r in repo_info.revisions]
    if revs:
        strategy = cache.delete_revisions(*revs)
        strategy.execute()
        print(f"deleted cache {repo} ({strategy.expected_freed_size_str})", flush=True)
    shutil.rmtree(Path.home() / ".cache/huggingface/hub" / ("models--" + repo.replace("/", "--")), ignore_errors=True)


def main(pipeline, delete_cache):
    out = HERE / "probes" / f"verb_ladder_{pipeline}"
    for st in stages(pipeline):
        base = st["stage"] == "base"
        framing = "raw" if base else tuned_framing(st)
        jobs = [(f, 24 if base else 48) for f in NAME] + ([] if base else [(f, 48) for f in CHOOSE])
        outs = [(local.path(out / Path(f).stem, st, framing), f) for f, _ in jobs]
        if not base:
            outs.append((local.path(out / "free_brands", st, framing), None))
        if all(o.exists() and len(json.loads(o.read_text())["scenes"]) == len(
                (json.loads((HERE / f).read_text()) if f else free_brand_spec())["scenes"]) for o, f in outs):
            print(f"skip {st['label']}: already complete", flush=True)
            continue
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
            drop_cache(st["weights"])


if __name__ == "__main__" and "--recommend" not in sys.argv and "--pick2" not in sys.argv:
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
        f = tuned_framing(st)
        path = local.path(out, st, f)
        if st["stage"] == "base" or (path.exists() and len(json.loads(path.read_text())["scenes"]) == len(spec["scenes"])):
            continue
        model = local.load(st)
        # batch 8: 512-token replies at batch 16 ran out of GPU memory on OLMo 3 7B DPO (2026-10-02)
        local.run(spec, st, f, RECOMMEND_RUNS, path, max_tokens=512, batch=8, model=model)
        del model
        local.free()
        if delete_cache and not st["weights"].startswith(("/", "~")):
            drop_cache(st["weights"])


if __name__ == "__main__" and "--recommend" in sys.argv:
    recommend_pass(sys.argv[1], "--delete-cache" in sys.argv)


PICK = "Which one would you pick?"


def pick2_encode(tok, st, framing, q1, a1):
    """The two-turn conversation (recommend, the stage's own recommend reply, then PICK) as token ids, in the stage's
    framing: nosys writes the turns out without the template's default system prompt, chat uses the template."""
    if framing == "nosys":
        tpl = st["nosys"]
        end = tpl.split("{q}")[1].split("<|im_start|>")[0]          # the end-of-turn marker, "<|im_end|>\n" for OLMo
        return tok.encode(tpl.replace("{q}", q1) + a1 + end + tpl.replace("{q}", PICK))
    msgs = [{"role": "user", "content": q1}, {"role": "assistant", "content": a1}, {"role": "user", "content": PICK}]
    return tok.apply_chat_template(msgs, add_generation_prompt=True, **st.get("chat_kwargs", {}))


def head_to_head_runs(rec):
    """scene -> indices of the turn-1 replies that name both of the API panel's brands (its Name brand and its two-turn
    pick brand), over the categories where the two differ (probes/stage_pick.json, written by stage_pick.py). Mentions
    are read as stage_pick.py reads them, so these are exactly the lists its head-to-head share can use."""
    sys.path.insert(0, str(HERE))
    import brand_ladder as B
    sp = json.loads((HERE / "probes" / "stage_pick.json").read_text())
    pats, out = B.pools()[4], {}
    for c in sp["categories_where_panel_pick_differs"]:
        sid, both = f"{c}__recommend", set(sp["panel_brands"][c].values())
        runs = rec["scenes"].get(sid, {}).get("runs", [])
        ks = [k for k, r in enumerate(runs) if r and r[0].get("reply") and both <= set(B.mentions(r[0]["reply"], pats[c]))]
        if ks:
            out[sid] = ks
    return out


def pick2_pass(pipeline, delete_cache, max_tokens=384, batch=8, turn1_from=None, picks=1):
    """The two-turn pick on the tuned stages: each of the stage's one-turn recommend replies (recommend/) is turn 1, and
    the stage answers PICK once per reply, so every pick is paired with the list it chose from. Writes pick2/.
    turn1_from=<stage> gives every later stage that stage's recommend replies as turn 1 instead of its own, so the list
    is held fixed and only the choice from it can change; writes pick2_from_<stage>/.
    picks=K > 1 answers PICK K times per turn-1 reply, on the head-to-head lists only (head_to_head_runs), and runs the
    turn1_from stage too, on its own lists; writes pick2_from_<stage>_k/ (pick2_k/ without turn1_from). Each pick
    records its turn-1 reply's index as turn1_run."""
    from mlx_lm.sample_utils import make_sampler
    base = HERE / "probes" / f"verb_ladder_{pipeline}"
    src = next((s for s in stages(pipeline) if s["stage"] == turn1_from), None) if turn1_from else None
    folder = (f"pick2_from_{turn1_from}" if src else "pick2") + ("_k" if picks > 1 else "")
    for st in stages(pipeline):
        if st["stage"] == "base" or (src and st["stage"] == turn1_from and picks == 1):
            continue
        f = tuned_framing(st)
        rec_path = local.path(base / "recommend", src or st, tuned_framing(src or st))
        path = local.path(base / folder, st, f)
        if not rec_path.exists():
            print(f"{st['label']}: no recommend file, skipped", flush=True)
            continue
        rec = json.loads(rec_path.read_text())
        runs = head_to_head_runs(rec) if picks > 1 else {sid: range(len(sc["runs"])) for sid, sc in rec["scenes"].items()}
        data = json.loads(path.read_text()) if path.exists() else None
        if data and data.get("picks", 1) != picks:
            sys.exit(f"{path} holds {data.get('picks', 1)} picks per list, not {picks}")
        todo = [sid for sid in runs if not data or sid.replace("__recommend", "__pick") not in data["scenes"]]
        if not todo:
            continue
        model, tok = local.load(st)
        if data is None:
            data = {"model": st["label"], "slug": st["repo"], "spec_version": "verb-ladder-pick-2turn", "host": "local-mlx",
                    "pipeline": pipeline, "stage": st["stage"], "framing": f, "weights": st["weights"],
                    "quantization": st.get("quantization"), "revision": local.revision(st["repo"], st["weights"]),
                    "temperature": 1.0, "max_tokens": max_tokens, "turn1": str(rec_path.relative_to(HERE)),
                    **({"picks": picks, "turn1_runs": "head to head (head_to_head_runs)"} if picks > 1 else {}), "scenes": {}}
        sampler, t0 = make_sampler(temp=1.0), time.time()
        path.parent.mkdir(parents=True, exist_ok=True)
        for i in range(0, len(todo), 4):                                  # written every 4 categories, to resume
            chunk, prompts, keys = todo[i:i + 4], [], []
            for sid in chunk:
                for k in runs[sid]:
                    run = rec["scenes"][sid]["runs"][k]
                    if run and run[0].get("reply"):
                        prompts += [pick2_encode(tok, st, f, run[0]["u"], run[0]["reply"])] * picks
                        keys += [(sid, k)] * picks
            replies = local.generate(model, tok, prompts, max_tokens, sampler, batch,
                                     st.get("batched", True) and "--unbatched" not in sys.argv)
            by = {}
            for (sid, k), (text, fin) in zip(keys, replies):
                cell = local.cell(PICK, text, False, fin) | ({"turn1_run": k} if picks > 1 else {})
                by.setdefault(sid, []).append([rec["scenes"][sid]["runs"][k][0], cell])
            for sid in chunk:
                data["scenes"][sid.replace("__recommend", "__pick")] = {"run_date": time.strftime("%Y-%m-%d"), "runs": by.get(sid, [])}
            path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")
        print(f"{st['label']}/{f} pick2: {len(todo)} scenes in {time.time() - t0:.0f}s -> {path}", flush=True)
        del model
        local.free()
        if delete_cache and not st["weights"].startswith(("/", "~")):
            drop_cache(st["weights"])


if __name__ == "__main__" and "--pick2" in sys.argv:
    # --batch=N: the two-turn prompts carry a full recommend reply; OLMo 3 7B ran out of GPU memory at 8 and at 4
    # (2026-10-05). --unbatched samples one prompt at a time, for a model whose batched path will not fit.
    # --turn1-from=sft: the later stages pick from the SFT stage's lists (the list held fixed, 2026-10-06).
    # --picks=K: K picks per head-to-head list, to tighten the head-to-head n (2026-10-06).
    arg = lambda name, default: next((a.split("=")[1] for a in sys.argv if a.startswith(f"--{name}=")), default)
    pick2_pass(sys.argv[1], "--delete-cache" in sys.argv, batch=int(arg("batch", 8)), turn1_from=arg("turn1-from", None),
               picks=int(arg("picks", 1)))
