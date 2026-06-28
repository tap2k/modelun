"""
flowstore interchange — `run/result/v0` ⇄ Contract A.

flowstore (whatsupp) evaluates a *full conversational agent* and writes
`run/result/v0`: a flat, agent-first transcript of `{role, content}` turns plus
optional `capability_calls` / `final_variables` / `evaluator_results`. modelun
evaluates at the altitude *below* the agent (bare models, paired stimulus→reply)
and stores Contract A: scenes of `{u, reply}` panels.

This module is the boundary membrane the two altitudes meet at — neither adopts the
other's internal shape (see docs/harness.md "Interchange with flowstore"). It lets a
real agent transcript be pulled INTO modelun so the rigor kernel — human + LLM voted
labelers, quote-grounded, adjudicated — can grade the agent's *behavior* (natural?
grounded? attuned?), which the agent-functional eval (did tools fire, goals met)
can't assess.

Scope: this carries the TRANSCRIPT across the boundary, not the agent's eval semantics.
capability_calls / final_variables are preserved on the scene (so nothing is lost) but
modelun does not judge them — they stay flowstore's concern.

    ingest:  run/result/v0  → Contract A   (implemented — the valuable direction)
    emit:    Contract A      → run/result/v0 (planned)

CLI:
    python harness/flowstore.py ingest <result.json> [<result.json> ...] \
        --study studies/<name> [--scene-id <id>]
"""

import json
import argparse
from pathlib import Path


def _fold_transcript(turns):
    """Flat agent-first `{role, content}` → modelun `(seed, panels)`.

    flowstore agents speak first (`chatbot_initiates`), so the stream is
    agent, user, agent, user, ...  A modelun panel pairs ONE user turn with the
    agent reply that FOLLOWS it. The agent's opening line (before any user turn)
    has no user turn to pair with, so it becomes the scene `seed` — exactly the
    field run.py already injects as a leading assistant message.

        [agent A0, user U1, agent A1, user U2, agent A2]
          → seed = A0
          → panels = [{u:U1, reply:A1}, {u:U2, reply:A2}]

    A trailing user turn with no following agent reply becomes {u, reply:null}
    (the same shape run.py uses for a failed turn), so nothing is dropped.
    """
    seed = None
    panels = []
    i = 0
    n = len(turns)
    # a leading agent turn (no user before it) is the seed
    if n and turns[0].get("role") == "agent":
        seed = turns[0].get("content")
        i = 1
    while i < n:
        t = turns[i]
        if t.get("role") == "user":
            u = t.get("content")
            reply = None
            if i + 1 < n and turns[i + 1].get("role") == "agent":
                reply = turns[i + 1].get("content")
                i += 2
            else:
                i += 1
            panels.append({"u": u, "reply": reply})
        else:
            # consecutive agent turns (agent spoke twice): append to the previous
            # reply so no content is lost, rather than inventing an empty user turn.
            if panels and panels[-1]["reply"] is not None:
                panels[-1]["reply"] += "\n" + (t.get("content") or "")
            i += 1
    return seed, panels


def ingest_result(result, scene_id=None):
    """One `run/result/v0` dict → a (scene_id, Contract-A scene) pair.

    The scene id defaults to the result's `test_case_id`. Agent-eval extras
    (capability_calls, final_variables, evaluator_results) ride along on the scene
    under `flowstore` so the round-trip is lossless and a study MAY use them, but
    modelun's judge ignores them.
    """
    sid = scene_id or result.get("test_case_id") or "agent_run"
    seed, panels = _fold_transcript(result.get("transcript", []))
    scene = {
        "subtitle": result.get("test_case_id", sid),
        "run_date": (result.get("timestamp", "") or "")[:10],
        "seed": seed,
        "runs": [panels],            # one agent run = one arc; matches Contract A
        "flowstore": {               # preserved, not judged — boundary keeps the extras
            "agent_id": result.get("agent_id"),
            "model": result.get("model"),
            "capability_calls": result.get("capability_calls", []),
            "final_variables": result.get("final_variables", {}),
            "evaluator_results": result.get("evaluator_results", []),
        },
    }
    return sid, scene


def ingest_to_transcript(results, model_label=None, slug=None):
    """N `run/result/v0` dicts → one Contract-A transcript file (dict).

    Each result becomes one scene, keyed by test_case_id. model/slug come from the
    first result unless overridden — a Contract-A file is per-model, and a batch of
    agent runs is one agent (= one "model" column) across several scenes.
    """
    first = results[0] if results else {}
    label = model_label or first.get("agent_id") or first.get("model") or "agent"
    data = {
        "model": label,
        "slug": slug or first.get("model", ""),
        "spec_version": "flowstore-run/result/v0",
        "scenes": {},
    }
    for r in results:
        sid, scene = ingest_result(r)
        data["scenes"][sid] = scene
    return data


def main():
    ap = argparse.ArgumentParser(description="flowstore run/result/v0 ⇄ Contract A.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    ing = sub.add_parser("ingest", help="run/result/v0 file(s) → Contract A transcript")
    ing.add_argument("results", nargs="+", help="run/result/v0 JSON file(s)")
    ing.add_argument("--study", required=True, help="study dir to write the transcript into")
    ing.add_argument("--model", default=None, help="override the transcript model label")
    ing.add_argument("--out", default=None, help="output path (default: <study>/transcripts/<model>.json)")
    args = ap.parse_args()

    if args.cmd == "ingest":
        results = [json.loads(Path(p).read_text()) for p in args.results]
        data = ingest_to_transcript(results, model_label=args.model)
        out = Path(args.out) if args.out else Path(args.study) / "transcripts" / f"{data['model']}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        print(f"→ {out}  ({len(data['scenes'])} scene(s) from {len(results)} agent run(s))")


if __name__ == "__main__":
    main()
