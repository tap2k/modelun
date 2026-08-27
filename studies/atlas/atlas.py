"""Shared helpers for the atlas study: paths, spec/criteria/panel loading, transcript and
label loading, code-count metrics, usage split, span normalization/verification, and the
OpenRouter client. Every script in the study imports from here."""
import json, os, re, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "harness")]   # harness modules import each other bare (from study import Study)
from harness.adjudicate import normalize as norm  # noqa: E402  smart quotes, dashes, markdown chars, whitespace, case

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

API = "https://openrouter.ai/api/v1"
TRANSCRIPTS = HERE / "transcripts"
LABELS = HERE / "labels"


# ---------- spec ----------
def spec():
    return json.loads((HERE / "spec/stimulus.json").read_text())


def criteria():
    """{id: criterion dict} plus the file's version, from spec/criteria.json."""
    c = json.loads((HERE / "spec/criteria.json").read_text())
    return {x["id"]: x for x in c["criteria"]}, c["version"]


def panel():
    return json.loads((HERE / "spec/models.json").read_text())["models"]


def iter_anchors(sp=None):
    """(template, anchor, prompt) over anchors and rotation items, in spec order."""
    for t in (sp or spec())["templates"]:
        for a in t["anchors"] + t.get("rotation", []):
            yield t, a, t["template"].replace("{text}", a["text"])


def prompts(sp=None):
    return {a["id"]: p for _, a, p in iter_anchors(sp)}


def applies(crit, anchor_id):
    return crit["applies_to"] == "*" or anchor_id in crit["applies_to"]


# ---------- data ----------
def transcripts():
    """{label: transcript dict} for every model file, in panel order then alphabetical."""
    T = {p.stem: json.loads(p.read_text()) for p in TRANSCRIPTS.glob("*.json")}
    order = [m["label"] for m in panel()]
    return {m: T[m] for m in sorted(T, key=lambda m: (m not in order, order.index(m) if m in order else 0, m))}


def labels():
    """{label: labels dict} for every model with a label file."""
    return {p.stem: json.loads(p.read_text()) for p in LABELS.glob("*.json")}


def samples(T, m, a):
    """Non-errored samples of one cell."""
    return [s for s in T[m]["cells"].get(a, {}).get("samples", []) if s.get("reply")]


def span_index(L):
    """{(model, anchor, i): spans} over all label files."""
    return {(m, s["anchor"], s["i"]): s["spans"] for m in L for s in L[m]["samples"]}


def short(m, _cache={}):
    if not _cache:
        _cache.update({x["label"]: x.get("short", x["label"]) for x in panel()})
    return _cache.get(m, m)


# ---------- metrics (code counts) ----------
MODAL_WORDS = ["may", "might", "could", "probably", "usually", "perhaps"]
_MOD = re.compile(r"\b(" + "|".join(MODAL_WORDS) + r")\b", re.I)
_BULLET = re.compile(r"^\s*[-*•]\s", re.M)
_HEADER = re.compile(r"^#+\s", re.M)
_BOLD = re.compile(r"\*\*[^*]+\*\*")


def metrics(reply):
    w = len(reply.split())
    return {"words": w, "bullets": len(_BULLET.findall(reply)), "headers": len(_HEADER.findall(reply)),
            "bold": len(_BOLD.findall(reply)), "exclaim": reply.count("!"),
            "modals": 100 * len(_MOD.findall(reply)) / max(w, 1)}


def usage_split(usage):
    """(visible output tokens, reasoning tokens, USD) from an OpenRouter usage block."""
    u = usage or {}
    ct = u.get("completion_tokens", 0)
    rt = (u.get("completion_tokens_details") or {}).get("reasoning_tokens") or 0
    return ct - rt, rt, u.get("cost", 0) or 0


# ---------- spans ----------
_WS = re.compile(r"\s+")


def find_span(reply, span):
    """(start, end) of the span in the reply: exact, then case-insensitive, then
    whitespace/quote-tolerant. None if it cannot be located."""
    i = reply.find(span)
    if i < 0:
        i = reply.lower().find(span.lower())
    if i >= 0:
        return i, i + len(span)
    parts = [re.escape(p) for p in _WS.split(span.strip()) if p]
    if not parts:
        return None
    pat = r"\s+".join(parts).replace("'", "['’]").replace('"', '["“”]')
    m = re.search(pat, reply, re.I)
    return (m.start(), m.end()) if m else None


def verify_spans(reply, items, labels_allowed=None):
    """Keep items whose span is found in the reply; attach start/end and the verbatim
    text. Returns (kept, dropped)."""
    kept, dropped = [], []
    for it in items or []:
        sp = (it.get("span") or "").strip() if isinstance(it, dict) else ""
        pos = find_span(reply, sp) if sp else None
        if not pos:
            dropped.append(sp)
            continue
        rec = {"span": reply[pos[0]:pos[1]], "start": pos[0], "end": pos[1]}
        if labels_allowed and it.get("label") in labels_allowed:
            rec["label"] = it["label"]
        kept.append(rec)
    return kept, dropped


def merge_adjacent(reply, recs):
    """Merge spans separated only by whitespace/punctuation into one instance."""
    out = []
    for r in sorted(recs, key=lambda r: r["start"]):
        if out and re.fullmatch(r"[\s.,;:!?\-–—*)\]\"'”’]*", reply[out[-1]["end"]:r["start"]]):
            out[-1] = {**out[-1], "end": r["end"], "span": reply[out[-1]["start"]:r["end"]]}
        else:
            out.append(r)
    return out


# ---------- OpenRouter ----------
def headers():
    return {"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"}


def post(body, retries=3, timeout=180):
    """POST /chat/completions with retry; returns the parsed response."""
    import requests
    last = None
    for attempt in range(retries):
        try:
            r = requests.post(f"{API}/chat/completions", headers=headers(), json=body, timeout=timeout)
            r.raise_for_status()
            j = r.json()
            if not j["choices"][0]["message"].get("content"):
                raise ValueError("empty content")
            return j
        except Exception as e:
            last = e
            time.sleep(2 * (attempt + 1))
    raise last


def parse_json(raw):
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if m:
            return json.loads(m.group(0))
        raise
