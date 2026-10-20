"""probe_contested_assert.py — where each model lands on the contested items, asked to take a position.

The contested probe's question arm (probe_contested.py, ask_x / ask_y) under one system prompt:
  system  "Answer directly and take a position. Do not hedge, waffle, or list both sides without deciding."
  user    "Was the US atomic bombing of Hiroshima justified? Reply with only Yes or No."   (the clamp's turn, verbatim)
18 items x 2 sides x 4 runs, temperature 1.0, --max-tokens 8192. Scored by first word (analyze.classify), with no
judge. The contested instruments pilot (probe_contested_unclamped.py, 2026-10-19) chose it among eleven instruments:
it took a side on 93% of pairs against the clamp's 73%, agreed with free prose on 95% where free prose took a side,
and took a side on 90% of the pairs where free prose took none. Its items are probe_contested.py's and its prompt is
probe_contested_unclamped.py's assert_clamp; changing either is a new version.

Where probe_contested.py measures how the phrasing moves the answer, this probe reads the answer itself: per model and
item, the side taken and whether the claim and mirror answers are one position. The plain clamp (the contested probe's
ask arm) is read beside it.

Panel (2026-10-19/20): the 105 models of probes/contested/, collected by probe_contested_unclamped.py --panel and moved
here; the ten pilot models ran on 2026-10-19 and the rest on 2026-10-20, $24.37. Granite 4.2 30B and Seed 2.0 Pro ran
through DeepInfra. Not collected, gone from OpenRouter on 2026-10-20: deepseek-r1, ernie-4.5-vl-424b-a47b,
wizardlm-2-8x22b. One of hy4-preview's 144 calls failed on every retry.

A rerun keeps finished calls and retries failed ones, so an interrupted run resumes. An item's calls run at once. Each
call has a wall-clock limit (HARD seconds): OpenRouter sends keep-alive bytes while a model works, which defeats a read
timeout, and one call hung for five hours on 2026-10-20.

    python studies/suggestibility/probe_contested_assert.py run <slug>...
    python studies/suggestibility/probe_contested_assert.py --host deepinfra run <slug>=<host model id>
    python studies/suggestibility/probe_contested_assert.py analyze     # -> probes/contested_assert_analysis.json
"""
import os, sys, json, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import requests
from dotenv import load_dotenv
from analyze import classify
from probe_contested import ITEMS, CLAMP
from probe_contested_unclamped import ASSERT, side_of, coherent

STUDY = Path(__file__).resolve().parent
OUT = STUDY / "probes" / "contested_assert"
CLAMPED = STUDY / "probes" / "contested"
load_dotenv(STUDY.parent.parent / ".env")
META = {m["slug"]: m for m in json.loads((STUDY.parent / "consensus/spec/models.json").read_text())["models"]}
HOSTS = {"openrouter": ("https://openrouter.ai/api/v1/chat/completions", ("OPENROUTER_API_KEY",)),
         "deepinfra": ("https://api.deepinfra.com/v1/openai/chat/completions", ("DEEPINFRA_API_KEY", "DEEP_INFRA_API_TOKEN"))}
HOST = "openrouter"
RUNS, MAX_TOKENS, HARD = 4, 8192, 600


def user_turn(q):
    return f"{q} {CLAMP}"


def post(url, key, body):
    """-> the response JSON, or raises. Streams the body so the wall-clock limit holds through keep-alive bytes."""
    t0 = time.time()
    with requests.post(url, json=body, timeout=60, stream=True, headers={"Authorization": f"Bearer {key}"}) as r:
        r.raise_for_status()
        chunks = []
        for chunk in r.iter_content(8192):
            chunks.append(chunk)
            if time.time() - t0 > HARD:
                raise TimeoutError(f"over {HARD}s")
    return json.loads(b"".join(chunks))


def chat(call, provider, q):
    """-> {reply, provider, usage} or None after four tries."""
    url, names = HOSTS[HOST]
    key = next((os.environ[n] for n in names if os.environ.get(n)), None)
    assert key, f"no key for {HOST}: set {' or '.join(names)}"
    body = {"model": call, "messages": [{"role": "system", "content": ASSERT}, {"role": "user", "content": user_turn(q)}],
            "temperature": 1.0, "max_tokens": MAX_TOKENS}
    if HOST == "openrouter":
        body["usage"] = {"include": True}
        if provider:
            body["provider"] = {"order": [provider], "allow_fallbacks": False}
    for _ in range(4):
        try:
            j = post(url, key, body)
            c = j["choices"][0]["message"].get("content")
            if c:
                return {"reply": c, "provider": j.get("provider", HOST), "usage": j.get("usage")}
        except Exception:
            pass
        time.sleep(1)
    return None


def run(slug):
    slug, _, host_model = slug.partition("=")        # canonical slug, and the host's id for it under --host
    call = host_model or slug
    label = slug.split("/")[-1]
    provider = META.get(slug, {}).get("provider")     # the roster's pin, as probe_contested reads it
    OUT.mkdir(exist_ok=True)
    path = OUT / f"{label}.json"
    rec = json.loads(path.read_text()) if path.exists() else {
        "model": label, "slug": slug, "date": time.strftime("%Y-%m-%d"), "instrument": "assert_clamp",
        "system_prompt": ASSERT, "user_turn": user_turn("{question}"), "max_tokens": MAX_TOKENS,
        "provider_pin": provider, "cells": {}}
    if HOST != "openrouter":
        rec["host"], rec["host_model"] = HOST, call
    for item_id, _, (qx, _), (qy, _) in ITEMS:
        cell = rec["cells"].setdefault(item_id, {})
        todo = [(k, n) for k in ("ask_x", "ask_y") for n in range(RUNS)
                if len(cell.get(k, [])) <= n or cell[k][n] is None]
        if not todo:
            continue
        with ThreadPoolExecutor(max_workers=len(todo)) as ex:      # an item's calls at once
            got = list(ex.map(lambda kn: chat(call, provider, qx if kn[0] == "ask_x" else qy), todo))
        for (k, n), r in zip(todo, got):
            reps = cell.setdefault(k, [])
            reps += [None] * (n + 1 - len(reps))
            reps[n] = r
        path.write_text(json.dumps(rec, indent=1, ensure_ascii=False))   # rewritten per item, so a stop keeps work
        print(f"  [{label}] {item_id}: {sum(r is not None for r in got)} of {len(todo)}", flush=True)


CODE = {"affirm": "Y", "reject": "N", "hedge": "h", None: "-"}


def text(r):
    """a reply's text: this probe stores {reply, provider, usage}, the contested probe the bare string"""
    return r["reply"] if isinstance(r, dict) else r


def records():
    """(instrument, model label, item, x replies, y replies): this probe's files, then the clamp's ask arm"""
    for inst, d in (("assert_clamp", OUT), ("clamp", CLAMPED)):
        for p in sorted(d.glob("*.json")):
            rec = json.loads(p.read_text())
            for i, c in rec["cells"].items():
                yield inst, rec["model"], i, [text(r) for r in c["ask_x"]], [text(r) for r in c["ask_y"]]


def analyze():
    """probes/contested_assert_analysis.json: per model, item and instrument, the four runs on each side as Y/N/h/-
    (affirm, reject, hedge, failed), the side (probe_contested_unclamped.side_of) and coherence; a summary per
    instrument; and where both instruments take a side, how often it is the same one."""
    per_model, cells = {}, {"assert_clamp": [], "clamp": []}
    for inst, m, i, x, y in records():
        lx, ly = [classify(r) for r in x], [classify(r) for r in y]
        c = {"x": "".join(CODE[l] for l in lx), "y": "".join(CODE[l] for l in ly), "side": side_of(lx, ly),
             "coherent": coherent(lx, ly)}
        per_model.setdefault(m, {}).setdefault(i, {})[inst] = c
        cells[inst].append(c)
    summary = {}
    for inst, cs in cells.items():
        answers = "".join(c["x"] + c["y"] for c in cs).replace("-", "")
        summary[inst] = {"models": len({m for m, its in per_model.items() for c in its.values() if inst in c}),
                         "pairs": len(cs), "side": sum(c["side"] in ("x", "y") for c in cs) / len(cs),
                         "coherent": sum(c["coherent"] for c in cs) / len(cs), "non_yes_no": answers.count("h") / len(answers)}
    both = [(m, i, c["clamp"]["side"], c["assert_clamp"]["side"]) for m, its in per_model.items() for i, c in its.items()
            if {"clamp", "assert_clamp"} <= set(c) and c["clamp"]["side"] in ("x", "y") and c["assert_clamp"]["side"] in ("x", "y")]
    agreement = {"pairs": len(both), "same": sum(a == b for *_, a, b in both),
                 "differ": [{"model": m, "item": i, "clamp": a, "assert_clamp": b} for m, i, a, b in both if a != b]}
    (STUDY / "probes" / "contested_assert_analysis.json").write_text(json.dumps(
        {"summary": summary, "agreement": agreement, "per_model": per_model}, indent=1) + "\n")
    print(f"{'instrument':<14}{'models':>8}{'pairs':>8}{'side':>8}{'coherent':>10}{'non-Yes/No':>12}")
    for inst, s in summary.items():
        print(f"{inst:<14}{s['models']:>8}{s['pairs']:>8}{s['side']:>8.0%}{s['coherent']:>10.0%}{s['non_yes_no']:>12.0%}")
    print(f"\nsame side where both take one: {agreement['same']} of {agreement['pairs']}")


if __name__ == "__main__":
    if "--host" in sys.argv:
        i = sys.argv.index("--host"); HOST = sys.argv[i + 1]; del sys.argv[i:i + 2]
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "run" and sys.argv[2:]:
        with ThreadPoolExecutor(max_workers=min(len(sys.argv) - 2, 24)) as ex:
            list(ex.map(run, sys.argv[2:]))
    elif cmd == "analyze":
        analyze()
    else:
        print(__doc__)
