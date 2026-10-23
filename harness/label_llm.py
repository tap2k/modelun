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

--form <form.json>: label_server.py's form, every question in one call (docs/harness.md § Human labeling). A pick-one
question gets one value; a pick-any question gets the codes that apply, each with a verbatim quote from the reply, and
a quote that is not a substring of the reply (whitespace and markdown emphasis ignored) drops its code. Rows go where
label_server.py writes them: <out>/<criterion>/labels.<judge>.jsonl, and <out>/<criterion>/<code>/... for each code,
binary, with the quote. "skip_if" leaves a question unasked when the judge's earlier answer is a listed value.

    python harness/label_llm.py --items <items.jsonl> --out <dir> --judge google/gemini-3.8-flash \
        --form <form.json> --guide <guide.txt> [--limit 10]

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
ap.add_argument("--criterion", default=None)
ap.add_argument("--criterion-version", default="v1")
ap.add_argument("--values", default=None)
ap.add_argument("--form", default=None, help="label_server.py's form JSON: several questions in one call, in place of --criterion/--values")
ap.add_argument("--guide", required=True, help="the codebook: value definitions and rules")
ap.add_argument("--examples", default=None)
ap.add_argument("--only", default=None, help="JSON list of target ids (sorted-key JSON of the target) to label")
ap.add_argument("--limit", type=int, default=None, help="label at most this many (the sample before a full run)")
ap.add_argument("--workers", type=int, default=8)
ap.add_argument("--max-tokens", type=int, default=8192)
ap.add_argument("--example-chars", type=int, default=1500, help="an example reply longer than this keeps its start and end")
args = ap.parse_args()
if bool(args.form) == bool(args.criterion and args.values):
    ap.error("give either --form or both --criterion and --values")

VALUES = [v.strip() for v in (args.values or "").split(",") if v.strip()]
QUESTIONS = []
if args.form:
    QUESTIONS = json.loads(Path(args.form).read_text())["questions"]
    for q in QUESTIONS:
        q.setdefault("version", "v1")
        if "codes" in q:
            q["codes"] = list(dict.fromkeys(r["code"] for r in read_jsonl(Path(args.form).parent / q["codes"])))
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
if args.form:
    shape = ", ".join(f'"{q["criterion"]}": ' + (f'[{{"code": one of {q["codes"]}, "quote": "the exact words of the reply"}}, ...]'
                      if "codes" in q else f"one of {q['values']}") for q in QUESTIONS)
    skips = "".join(f"\nLeave out {q['criterion']} when " + " or ".join(f"{c} is {', '.join(vs)}" for c, vs in q["skip_if"].items()) + "."
                    for q in QUESTIONS if q.get("skip_if"))
    SYSTEM += (f"\n\nAnswer with one JSON object only: {{{shape}}}. For each code, the quote is copied word for word from the"
               f" reply and shows the code applies; an empty list when none applies.{skips}")
else:
    SYSTEM += f"\n\nAnswer with one word only: {', '.join(VALUES)}."
PROMPT_VERSION = hashlib.sha256(SYSTEM.encode()).hexdigest()[:12]

FILE = f"labels.{args.judge.replace('/', '-')}.jsonl"
OUT = Path(args.out) / (QUESTIONS[0]["criterion"] if args.form else "") / FILE    # the first question marks an item done
OUT.parent.mkdir(parents=True, exist_ok=True)
done = {target_id(r["target"]) for r in read_jsonl(OUT) if r.get("prompt_version") == PROMPT_VERSION and r.get("value")}
todo = [it for it in ITEMS if target_id(it["target"]) not in done]
if args.only:
    only = set(json.loads(Path(args.only).read_text()))
    todo = [it for it in todo if target_id(it["target"]) in only]
if args.limit:
    todo = todo[:args.limit]


def parse_form(text):
    """the JSON object in the answer, its pick-one values checked, or None"""
    try:
        j = json.loads(text[text.index("{"):text.rindex("}") + 1])
    except ValueError:
        return None
    q1 = QUESTIONS[0]
    return j if isinstance(j, dict) and j.get(q1["criterion"]) in q1["values"] else None


def flat(s):
    return " ".join(s.replace("*", "").replace("_", "").split()).lower()


def parse(text):
    """the first word of the answer that is a value, or None"""
    if args.form:
        return parse_form(text)
    for w in text.lower().replace("*", " ").replace(".", " ").split():
        if w.strip("\"'`:,") in VALUES:
            return w.strip("\"'`:,")
    return None


def form_rows(it, ans, base):
    """-> [(path, row)]: a graded row per pick-one question, a binary row per code of each pick-any one. A failed parse
    writes the first question's row with value None, so the item is retried on a rerun."""
    q1 = QUESTIONS[0]
    if ans is None:
        return [(OUT, base | {"target": {**it["target"], "criterion": q1["criterion"]}, "kind": "graded", "value": None,
                              "criterion_version": q1["version"]})]
    reply, rows = flat(it["reply"]), []
    for q in QUESTIONS:
        if any(ans.get(c) in vs for c, vs in (q.get("skip_if") or {}).items()):
            continue
        d = Path(args.out) / q["criterion"]
        if "codes" not in q:
            rows.append((d / FILE, base | {"target": {**it["target"], "criterion": q["criterion"]}, "kind": "graded",
                                           "value": ans.get(q["criterion"]), "criterion_version": q["version"]}))
            continue
        got = {}
        for x in ans.get(q["criterion"]) or []:
            if isinstance(x, dict) and x.get("code") in q["codes"] and x.get("quote") and flat(x["quote"]) in reply:
                got.setdefault(x["code"], x["quote"])
        dropped = [x.get("code") for x in ans.get(q["criterion"]) or [] if isinstance(x, dict) and x.get("code") not in got]
        for c in q["codes"]:
            rows.append((d / c / FILE, base | {"target": {**it["target"], "criterion": f"{q['criterion']}/{c}"}, "kind": "binary",
                                               "value": c in got, "quote": got.get(c), "criterion_version": q["version"]}
                         | ({"dropped": True} if c in dropped else {})))
    rows.sort(key=lambda pr: pr[0] != OUT)       # the first question's row first: it carries the answer and usage
    return rows


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
    base = {"labeler": args.judge, "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "blind": sorted((it.get("show") or {}).keys()), "prompt_version": PROMPT_VERSION, "provider": provider}
    rows = form_rows(it, parse(raw or ""), base) if args.form else [(OUT, base | {
        "target": {**it["target"], "criterion": args.criterion}, "kind": "graded", "value": parse(raw or ""),
        "criterion_version": args.criterion_version})]
    rows[0][1].update(raw=raw, usage=usage)     # once per call, on the first question's row
    with lock:
        for path, row in rows:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a") as fh:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        spent[0] += usd(usage); spent[1] += 1
        if spent[1] % 100 == 0:
            print(f"  {spent[1]}/{len(todo)}  ${spent[0]:.3f}", flush=True)


print(f"{args.judge}: {len(todo)} to label, prompt {PROMPT_VERSION} ({len(EXAMPLES)} examples, {len(SYSTEM)} chars)", flush=True)
with ThreadPoolExecutor(args.workers) as ex:
    list(ex.map(label, todo))
print(f"{args.judge}: labeled {spent[1]}, ${spent[0]:.3f} -> {OUT}", flush=True)
