#!/usr/bin/env python3
"""LLM judge for closed labeling: the machine counterpart of harness/viewer/label_server.py on the same items file.

One judge reads each item's prompt and reply with the codebook (--guide) and answers with one value. Each label is a
Contract B row, appended as made to <out>/labels.<judge with / as ->.jsonl, so judge rows and human rows
(labels.human-<name>.jsonl) sit side by side and label_agree.py compares them. A rerun skips targets this judge has
already labeled under the same prompt (prompt_version, a hash of the system prompt), so a changed guide or example set
relabels everything.

    python harness/label_llm.py --items <items.jsonl> --out <dir> --judge qwen/qwen3.7-plus \\
        --criterion position --criterion-version v2 --values affirm,reject,hedge,refuse,none \\
        --guide <guide.txt> [--examples <examples.jsonl>] [--only <ids.json>] [--limit 10] [--workers 8]

--examples: JSONL rows {"target": {...}, "value": ..., "why": "..."}; each example's prompt and reply come from the
items file and are shown in the system prompt. Example targets are labeled like any other and must be left out of an
agreement check (label_agree.py does). The judge sees the prompt and the reply only: every "show" field is hidden
and the row's `blind` lists them. The judge is itself a subject; label_agree.py excludes its calls on its own family.
"""
import os, json, time, hashlib, argparse, threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import requests
from dotenv import load_dotenv
from labels import target_id, read_jsonl
from cost import usd

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
API = "https://openrouter.ai/api/v1/chat/completions"

ap = argparse.ArgumentParser()
ap.add_argument("--items", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--judge", required=True, help="OpenRouter slug")
ap.add_argument("--criterion", required=True)
ap.add_argument("--criterion-version", default="v1")
ap.add_argument("--values", required=True)
ap.add_argument("--guide", required=True, help="the codebook: value definitions and rules")
ap.add_argument("--examples", default=None)
ap.add_argument("--only", default=None, help="JSON list of target ids (sorted-key JSON of the target) to label")
ap.add_argument("--limit", type=int, default=None, help="label at most this many (the sample before a full run)")
ap.add_argument("--workers", type=int, default=8)
ap.add_argument("--max-tokens", type=int, default=8192)
ap.add_argument("--example-chars", type=int, default=1500, help="an example reply longer than this keeps its start and end")
args = ap.parse_args()

VALUES = [v.strip() for v in args.values.split(",") if v.strip()]
ITEMS = read_jsonl(args.items)
BY_ID = {target_id(it["target"]): it for it in ITEMS}


def clip(s, n):
    return s if len(s) <= n else s[:n * 2 // 3] + "\n[...]\n" + s[-n // 3:]


def item_text(it):
    return f"Question: {it['prompt']}\n\nReply:\n{it['reply']}"


SYSTEM = Path(args.guide).read_text().strip()
EXAMPLES = []
if args.examples:
    EXAMPLES = read_jsonl(args.examples)
    SYSTEM += "\n\nWorked examples:"
    for n, ex in enumerate(EXAMPLES, 1):
        it = BY_ID[target_id(ex["target"])]
        SYSTEM += (f"\n\n--- Example {n}\nQuestion: {it['prompt']}\n\nReply:\n{clip(it['reply'], args.example_chars)}"
                   f"\n\nLabel: {ex['value']}" + (f"  ({ex['why']})" if ex.get("why") else ""))
SYSTEM += f"\n\nAnswer with one word only: {', '.join(VALUES)}."
PROMPT_VERSION = hashlib.sha256(SYSTEM.encode()).hexdigest()[:12]

OUT = Path(args.out) / f"labels.{args.judge.replace('/', '-')}.jsonl"
OUT.parent.mkdir(parents=True, exist_ok=True)
done = {target_id(r["target"]) for r in read_jsonl(OUT) if r.get("prompt_version") == PROMPT_VERSION and r.get("value")}
todo = [it for it in ITEMS if target_id(it["target"]) not in done]
if args.only:
    only = set(json.loads(Path(args.only).read_text()))
    todo = [it for it in todo if target_id(it["target"]) in only]
if args.limit:
    todo = todo[:args.limit]


def parse(text):
    """the first word of the answer that is a value, or None"""
    for w in text.lower().replace("*", " ").replace(".", " ").split():
        if w.strip("\"'`:,") in VALUES:
            return w.strip("\"'`:,")
    return None


lock = threading.Lock()
spent = [0.0, 0]


def label(it):
    body = {"model": args.judge, "temperature": 0, "max_tokens": args.max_tokens, "usage": {"include": True},
            "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": item_text(it)}]}
    raw, usage, provider = None, {}, None
    for _ in range(4):
        try:
            r = requests.post(API, timeout=300, json=body,
                              headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"})
            r.raise_for_status()
            j = r.json()
            raw, usage, provider = j["choices"][0]["message"].get("content") or "", j.get("usage") or {}, j.get("provider")
            if parse(raw):
                break
        except Exception:
            pass
        time.sleep(1)
    row = {"labeler": args.judge, "target": {**it["target"], "criterion": args.criterion}, "kind": "graded",
           "value": parse(raw or ""), "raw": raw, "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
           "blind": sorted((it.get("show") or {}).keys()), "criterion_version": args.criterion_version,
           "prompt_version": PROMPT_VERSION, "provider": provider, "usage": usage}
    with lock:
        with OUT.open("a") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        spent[0] += usd(usage); spent[1] += 1
        if spent[1] % 100 == 0:
            print(f"  {spent[1]}/{len(todo)}  ${spent[0]:.3f}", flush=True)


print(f"{args.judge}: {len(todo)} to label, prompt {PROMPT_VERSION} ({len(EXAMPLES)} examples, {len(SYSTEM)} chars)", flush=True)
with ThreadPoolExecutor(args.workers) as ex:
    list(ex.map(label, todo))
print(f"{args.judge}: labeled {spent[1]}, ${spent[0]:.3f} -> {OUT}", flush=True)
