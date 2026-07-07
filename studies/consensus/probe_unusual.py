"""probe_unusual.py — the conditional-mode probe, run properly: the full 39-model roster.

"Name an unusual fruit. Reply with one word only." under the main run's conditions (no
system prompt, temperature 1.0, no provider pinning, 4 runs). The question: does asking
for divergence release the distribution, or open a new column with its own mode?

    ../../.venv/bin/python probe_unusual.py        # -> probes/unusual_fruit.json
"""

import json
import time
from pathlib import Path
from urllib.request import Request, urlopen
from concurrent.futures import ThreadPoolExecutor

HERE = Path(__file__).resolve().parent
PROMPT = "Name an unusual fruit. Reply with one word only."
RUNS = 4

key = None
for line in (HERE / "../../.env").read_text().splitlines():
    if line.startswith("OPENROUTER_API_KEY="):
        key = line.split("=", 1)[1].strip()
assert key, "OPENROUTER_API_KEY not found in ../../.env"

models = json.loads((HERE / "spec/models.json").read_text())["models"]

def ask(slug):
    body = json.dumps({
        "model": slug,
        "messages": [{"role": "user", "content": PROMPT}],
        "temperature": 1.0, "max_tokens": 1024,
    }).encode()
    req = Request("https://openrouter.ai/api/v1/chat/completions", data=body,
                  headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    for attempt in range(3):
        try:
            r = json.load(urlopen(req, timeout=120))
            return r["choices"][0]["message"]["content"]
        except Exception as e:
            if attempt == 2:
                return None
            time.sleep(3 * (attempt + 1))

def run_model(m):
    replies = [ask(m["slug"]) for _ in range(RUNS)]
    print(m["label"], replies, flush=True)
    return m["label"], replies

with ThreadPoolExecutor(max_workers=10) as ex:
    results = dict(ex.map(run_model, models))

(HERE / "probes").mkdir(exist_ok=True)
(HERE / "probes" / "unusual_fruit.json").write_text(json.dumps(
    {"prompt": PROMPT, "temperature": 1.0, "runs": RUNS, "run_date": "2026-07-07",
     "replies": results}, indent=1) + "\n")
print("-> probes/unusual_fruit.json")
