"""probe_olmo_data.py — where "serendipity" sits in OLMo 3 7B Instruct's post-training data.

Companion to probe_olmo_ladder.py. Counts case-insensitive 'serendipit' in the Dolci Instruct mixes
that trained each stage (per each dataset's README; the model cards' metadata disagree with them):

  SFT  allenai/Dolci-Instruct-SFT, allenai/Dolci-Instruct-SFT-Tool-Use-SA   assistant vs user turns
  DPO  allenai/Dolci-Instruct-DPO                                             final chosen vs rejected turn
  RL   allenai/Dolci-Instruct-RL                                              prompts; stored rollouts

Also: DPO sign test on pairs with the word on one side only; the "word" fields that synthetic
tool calls return in the SFT tool-use source; and short pick-a-word prompts with their answers.
Raw substring counts, no deduplication. Downloads ~4 GB of parquet into the HF cache.
    ../../.venv/bin/python probe_olmo_data.py            # -> probes/olmo_data.json
"""
import json, math, re
from collections import Counter
from pathlib import Path

import pyarrow.parquet as pq
from huggingface_hub import snapshot_download

HERE = Path(__file__).resolve().parent                      # studies/consensus
OUT = HERE / "probes" / "olmo_data.json"
REVS = {
    "allenai/Dolci-Instruct-SFT": "bd3c8f3a9b2cc5a9682e44b96ddd0bb2ff027221",
    "allenai/Dolci-Instruct-SFT-Tool-Use-SA": "21456eced24a739c062e9a117ebdc6c3c05da448",
    "allenai/Dolci-Instruct-DPO": "aed155cf32e809b590490b6c3577ee4b0d0a5019",
    "allenai/Dolci-Instruct-RL": "1a8d79b1012d77e4bb1fd7f699c5c7eb33ef931e",
}
PAT = re.compile(r"serendipit", re.I)
WORD_PROMPT = re.compile(
    r"((pick|choose|name|give|say|think of|tell)\b.{0,20}\bword\b|favou?rite word|\bone word\b|single word|\ba word\b)",
    re.I | re.S)
RANDOM_WORD = re.compile(r"random word|word of the day", re.I)
SHORT = 300                                                 # pick-a-word prompts are short
N_EX = 5


def files(repo):
    root = snapshot_download(repo, repo_type="dataset", revision=REVS[repo], allow_patterns=["data/*"])
    return sorted(Path(root).glob("data/*.parquet"))


def rows(paths, cols, bs=4096):
    for f in paths:
        pf = pq.ParquetFile(f)
        have = set(pf.schema_arrow.names)
        for b in pf.iter_batches(batch_size=bs, columns=[c for c in cols if c in have]):
            yield from b.to_pylist()


def text(msgs, role):
    return "\n".join((m.get("content") or "") for m in msgs if m.get("role") == role)


def trunc(s, n=200):
    s = s.replace("\n", " ")
    return s if len(s) <= n else s[:n] + "..."


def answer_key(resp):
    """Crude: the word a reply gives (short reply, else first bold span, else first three words)."""
    r = resp.strip()
    b = re.search(r"\*\*([^*\n]{1,40})\*\*", r)
    a = r if len(r.split()) <= 4 else b.group(1) if b else " ".join(r.split()[:3])
    return re.sub(r"[^\w' -]", "", a).strip().lower()[:40]


def do_sft():
    c, src, answers, tool_words = Counter(), Counter(), Counter(), Counter()
    paths = files("allenai/Dolci-Instruct-SFT") + files("allenai/Dolci-Instruct-SFT-Tool-Use-SA")
    for row in rows(paths, ["messages", "source_dataset", "dataset_source"]):
        msgs = row["messages"] or []
        s = row.get("source_dataset") or row.get("dataset_source")
        a, u = text(msgs, "assistant"), text(msgs, "user")
        c["examples"] += 1
        c["assistant_words"] += len(a.split())
        na = len(PAT.findall(a))
        c["assistant_occ"] += na
        c["examples_assistant_hit"] += bool(na)
        c["examples_user_hit"] += bool(PAT.search(u))
        if na:
            src[str(s)] += 1
        users = [m for m in msgs if m.get("role") == "user"]
        asst = [m for m in msgs if m.get("role") == "assistant"]
        if users and asst:
            p, r = users[0].get("content") or "", asst[0].get("content") or ""
            if len(p) <= SHORT and WORD_PROMPT.search(p):
                c["word_prompts"] += 1
                c["word_prompts_serendipity_answer"] += bool(PAT.search(r))
                answers[answer_key(r)] += 1
        if s == "Dolci Instruct Tool Use" and RANDOM_WORD.search(u):
            env = text(msgs, "environment")
            c["tool_random_word_convs"] += 1
            c["tool_random_word_env_hit"] += bool(PAT.search(env))
            c["tool_random_word_assistant_hit"] += bool(PAT.search(a))
            tool_words.update(w.lower() for w in re.findall(r'"word"\s*:\s*"([^"]+)"', env))
    c["assistant_per_M_words"] = round(c["assistant_occ"] / c["assistant_words"] * 1e6, 3)
    return {"counts": dict(c), "assistant_hit_sources": dict(src.most_common()),
            "word_prompt_answers_top": answers.most_common(20),
            "tool_random_word_fields_top": tool_words.most_common(15)}


def do_dpo():
    c, src_c, src_r, ex = Counter(), Counter(), Counter(), {"chosen_only": [], "rejected_only": []}
    for row in rows(files("allenai/Dolci-Instruct-DPO"),
                    ["chosen", "rejected", "preference_type", "chosen_model", "rejected_model"]):
        ch, rj = row["chosen"] or [], row["rejected"] or []
        c["pairs"] += 1
        if not ch or not rj or ch[-1].get("role") != "assistant" or rj[-1].get("role") != "assistant":
            c["malformed"] += 1
            continue
        cr, rr = ch[-1].get("content") or "", rj[-1].get("content") or ""
        prompt = "\n".join(m.get("content") or "" for m in ch[:-1])
        c["chosen_words"] += len(cr.split())
        c["rejected_words"] += len(rr.split())
        nc, nr = len(PAT.findall(cr)), len(PAT.findall(rr))
        c["chosen_occ"] += nc
        c["rejected_occ"] += nr
        c["prompt_hit"] += bool(PAT.search(prompt))
        c["chosen_hit"] += bool(nc)
        c["rejected_hit"] += bool(nr)
        c["both_hit"] += bool(nc and nr)
        pt = str(row.get("preference_type"))
        if nc:
            src_c[pt] += 1
        if nr:
            src_r[pt] += 1
        side = "chosen_only" if nc and not nr else "rejected_only" if nr and not nc else None
        if side:
            c[side] += 1
            if len(ex[side]) < N_EX:
                ex[side].append({"type": pt, "chosen_model": row.get("chosen_model"),
                                 "rejected_model": row.get("rejected_model"),
                                 "prompt": trunc(ch[-2].get("content") or "" if len(ch) > 1 else ""),
                                 "chosen": trunc(cr), "rejected": trunc(rr)})
        lastu = next((m.get("content") or "" for m in reversed(ch[:-1]) if m.get("role") == "user"), "")
        if len(lastu) <= SHORT and WORD_PROMPT.search(lastu):
            c["word_prompts"] += 1
            c["word_prompts_chosen_serendipity"] += bool(nc)
            c["word_prompts_rejected_serendipity"] += bool(nr)
    c["chosen_per_M_words"] = round(c["chosen_occ"] / c["chosen_words"] * 1e6, 3)
    c["rejected_per_M_words"] = round(c["rejected_occ"] / c["rejected_words"] * 1e6, 3)
    k, n = c["rejected_only"], c["chosen_only"] + c["rejected_only"]
    p = min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)
    return {"counts": dict(c), "sign_test_two_sided_p": p, "chosen_hit_types": dict(src_c),
            "rejected_hit_types": dict(src_r), "examples": ex}


def do_rl():
    c, hits = Counter(), []
    for row in rows(files("allenai/Dolci-Instruct-RL"), ["prompt", "outputs", "dataset_source"], bs=1024):
        p, outs = row["prompt"] or "", row["outputs"] or []
        c["prompts"] += 1
        if PAT.search(p):
            c["prompt_hit"] += 1
            hits.append({"src": row["dataset_source"], "prompt": trunc(p)})
        c["output_words"] += sum(len((o or "").split()) for o in outs)
        no = sum(len(PAT.findall(o or "")) for o in outs)
        c["outputs_occ"] += no
        c["rows_outputs_hit"] += bool(no)
    c["outputs_per_M_words"] = round(c["outputs_occ"] / c["output_words"] * 1e6, 3)
    return {"counts": dict(c), "prompt_hits": hits}


if __name__ == "__main__":
    out = {"revisions": REVS}
    for name, fn in (("sft", do_sft), ("dpo", do_dpo), ("rl", do_rl)):
        out[name] = fn()
        print(name, json.dumps(out[name]["counts"]), flush=True)
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False))
