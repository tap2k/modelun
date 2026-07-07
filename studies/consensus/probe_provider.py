"""probe_provider.py — close the provider-routing confound on the DeepSeek lineage contrast.

The main run passed temperature=1.0 to OpenRouter without pinning or logging the serving
provider. If v3-0324 and v3.2 routed to hosts that honor the temperature parameter
differently, part of the peaked-vs-scattered contrast could be effective sampling
temperature rather than the models. This probe re-runs a subset of categories with BOTH
models pinned to the SAME provider (allow_fallbacks=false), temperature 1.0, 4 runs.

    ../../.venv/bin/python probe_provider.py            # -> probes/provider_pinned.json

If v3-0324 still answers 4-of-4 identical and v3.2 still scatters on the same host, the
contrast is a model property, not a routing artifact.
"""

import os
import json
import time
from pathlib import Path
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
PROVIDER = "deepinfra"  # hosts both models (checked 2026-07-07)
MODELS = ["deepseek/deepseek-chat-v3-0324", "deepseek/deepseek-v3.2"]
CATS = ["color", "animal", "city", "country", "fruit", "instrument", "emotion", "occupation"]
RUNS = 4

key = None
for line in (HERE / "../../.env").read_text().splitlines():
    if line.startswith("OPENROUTER_API_KEY="):
        key = line.split("=", 1)[1].strip()
assert key, "OPENROUTER_API_KEY not found in ../../.env"

scenes = {s["id"]: s["turns"][0]
          for s in json.loads((HERE / "spec/stimulus.json").read_text())["scenes"]}

def ask(slug, prompt):
    body = json.dumps({
        "model": slug,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 1.0, "max_tokens": 1024,
        "provider": {"order": [PROVIDER], "allow_fallbacks": False},
    }).encode()
    req = Request("https://openrouter.ai/api/v1/chat/completions", data=body,
                  headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    for attempt in range(3):
        try:
            r = json.load(urlopen(req, timeout=120))
            return {"reply": r["choices"][0]["message"]["content"],
                    "provider": r.get("provider")}
        except Exception as e:
            if attempt == 2:
                return {"reply": None, "error": str(e)}
            time.sleep(3 * (attempt + 1))

out = {"provider_pinned": PROVIDER, "temperature": 1.0, "runs": RUNS,
       "run_date": "2026-07-07", "models": {}}
for slug in MODELS:
    label = slug.split("/")[-1]
    out["models"][label] = {}
    for c in CATS:
        cells = [ask(slug, scenes[c]) for _ in range(RUNS)]
        out["models"][label][c] = cells
        print(label, c, [x.get("reply") for x in cells], flush=True)

(HERE / "probes").mkdir(exist_ok=True)
(HERE / "probes" / "provider_pinned.json").write_text(json.dumps(out, indent=1) + "\n")
print("-> probes/provider_pinned.json")
