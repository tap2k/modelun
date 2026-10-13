"""fingerprint_paper.py — the fingerprint paper's tables and checked numbers, from the committed probe outputs.

Reads probes/fingerprint.json, fingerprint_baselines.json, fingerprint_robust.json, provider_audit.json,
reference_contamination.json, the specs and the panel, and writes paper-fingerprint/gen/. Zero API calls; no
recomputation (each probe script owns its numbers).

    python3 fingerprint_paper.py
"""
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from probe_fingerprint import panel

GEN = HERE / "paper-fingerprint" / "gen"
P = lambda name: json.loads((HERE / "probes" / name).read_text())


def pct(x, d=0):
    return f"{100 * x:.{d}f}\\%"


def tex(s):
    return s.replace("_", "\\_").replace("&", "\\&")


def write(name, lines):
    (GEN / name).write_text("\n".join(lines) + "\n")


def main():
    GEN.mkdir(parents=True, exist_ok=True)
    fp, base, rob = P("fingerprint.json"), P("fingerprint_baselines.json"), P("fingerprint_robust.json")
    audit, cont = P("provider_audit.json"), P("reference_contamination.json")
    bq = fp["by_questions"]

    # 4.1 curve
    write("curve_rows.tex", [f"{k} & {pct(bq[f'{k}q_x1']['exact'], 1)} & {pct(bq[f'{k}q_x1']['family'], 1)} & "
                             f"{pct(bq[f'{k}q_x2']['exact'], 1)} & {pct(bq[f'{k}q_x2']['family'], 1)} \\\\" for k in (5, 10, 20, 40, 96)])

    # 4.1 scorer comparison (main text) and full table (appendix)
    res = base["results"]
    names = {"likelihood 0.1": "likelihood", "jsd": "nearest neighbour, Jensen--Shannon", "modal": "most common answer"}
    write("scorer_rows.tex", [f"{label} & " + " & ".join(pct(res[b][s]["mean"]) for b in ("10q_x1", "20q_x1", "40q_x1", "40q_x2")) + " \\\\"
                              for s, label in names.items()])
    budgets = [b for b in res]
    scorers = list(res[budgets[0]])
    write("scorer_full_rows.tex", [tex(s) + " & " + " & ".join(f"{100 * res[b][s]['mean']:.1f} ({100 * res[b][s]['sd']:.1f})" for b in budgets) + " \\\\"
                                   for s in scorers])
    times = " $\\times$ "
    write("scorer_full_head.tex", ["scorer & " + " & ".join(b.replace("q_x", times) for b in budgets) + " \\\\"])

    # 4.2 selection (main) and both halves (appendix)
    mean = fp["best_subset_x2"]["mean_of_splits"]
    write("selection_rows.tex", [f"{k} & {pct(mean[k]['selected'], 1)} & {pct(mean[k]['random'], 1)} \\\\" for k in sorted(mean, key=int)])
    sp = fp["best_subset_x2"]["splits"]
    rows = []
    for i in range(25):
        a, b = sp[0]["greedy"][i], sp[1]["greedy"][i]
        q = lambda g: g["question"].replace("_", " ")
        rows.append(f"{i + 1} & {q(a)} & {pct(a['eval_exact'])} & {q(b)} & {pct(b['eval_exact'])} \\\\")
    write("selection_full_rows.tex", rows)

    # 4.4 system prompt
    ident = rob["identification"]
    label = {"base": "no system prompt, a later day", "sysgen": "``You are a helpful assistant.''",
             "ava": "``You are Ava, a friendly assistant.''"}
    write("sysprompt_rows.tex", [f"{label[v]} & " + " & ".join(pct(ident[v][c]) for c in ("10x2", "20x2", "31x2", "31x4")) + " \\\\"
                                 for v in label])

    # Appendix A: questions
    core = [s["id"] for s in json.loads((HERE / "spec" / "stimulus.json").read_text())["scenes"]]
    exp = [s["id"] for s in json.loads((HERE / "spec" / "stimulus_expanded.json").read_text())["scenes"]]
    items = sorted([(c.replace("_", " "), c in core) for c in core + exp])
    dag = "$^\\dagger$"
    write("questions.tex", [", ".join(n + (dag if d else "") for n, d in items) + "."])

    # Appendix B: models
    A = panel()
    meta = {r["label"]: r for r in json.loads((HERE / "spec" / "models.json").read_text())["models"]}
    robust = {"claude-opus-5.5", "deepseek-v4-pro", "gemini-3.8-flash", "gemma-4-31b-it", "glm-5.3", "gpt-4o-mini-2024-07-18",
              "gpt-6.1-sol", "grok-4.7", "kimi-k3", "llama-3.3-70b-instruct", "mistral-small-2603", "muse-spark-1.3",
              "nemotron-3-ultra-550b-a55b", "qwen3.8-2.4t-a95b"}
    blind = set(json.loads((HERE / "probes" / "blind-deepinfra-2026-10-02.json").read_text())["key"].values())

    def dates(m):
        ds = set()
        for d in ("transcripts", "transcripts-extra", "transcripts-expanded"):
            ds |= {s.get("run_date") for s in json.loads((HERE / d / f"{m}.json").read_text())["scenes"].values()}
        ds.discard(None)
        return min(ds), max(ds)
    rows = []
    for m in sorted(A):
        lo, hi = dates(m)
        mark = (dag if m in robust else "") + ("$^\\ast$" if m in blind else "")
        rows.append(f"{tex(m)}{mark} & {tex(meta[m]['family'])} & {lo[5:]}" + (f" to {hi[5:]}" if hi != lo else "") + " \\\\")
    write("models_rows.tex", rows)

    # Appendix G: the audit, endpoints keyed by model and letter (the order reference_contamination.json uses)
    endpoints = json.loads(sorted((HERE / "transcripts-providers").glob("endpoints-*.json"))[-1].read_text())
    by_model, scored = {}, [r for r in audit if r.get("rank_of_claim")]
    for r in sorted(scored, key=lambda r: r["endpoint"]):
        by_model.setdefault(r["endpoint"].split("/")[0], []).append(r)
    pinned = {r["endpoint"]: r for r in cont["pinned"]}
    rows = []
    for model, rs in sorted(by_model.items()):
        for i, r in enumerate(rs):
            alias = f"{model}/{chr(65 + i)}"
            c = pinned[alias]
            info = endpoints[r["endpoint"]]
            q = f"{r['q']:.3f}" if r.get("q") is not None else "--"
            pin = f"{c['pinned']['rank']}" if "pinned" in c else "--"
            prec = info.get("quantization") if info.get("quantization") not in (None, "unknown") else "unstated"
            rows.append(f"{tex(alias)} & {prec} & {float(info['price_out']) * 1e6:.2f} & "
                        f"{tex(r['identified_as'])} & {r['rank_of_claim']} & {c['panel']['margin_nats_per_q']:+.2f} & {pin} & {q} \\\\")
    write("audit_rows.tex", rows)

    # numbers the text cites, for checking after a rerun
    write("numbers.tex", [
        f"% generated by fingerprint_paper.py; the text writes these values out",
        f"\\newcommand{{\\nModels}}{{{fp['models']}}}",
        f"\\newcommand{{\\nChance}}{{{pct(fp['chance'], 1)}}}",
        f"\\newcommand{{\\nFortyExact}}{{{pct(bq['40q_x1']['exact'], 1)}}}",
        f"\\newcommand{{\\nSelTen}}{{{pct(mean['10']['selected'])}}}",
        f"\\newcommand{{\\nRandTen}}{{{pct(mean['10']['random'])}}}",
        f"\\newcommand{{\\nAuditScored}}{{{len(scored)}}}",
        f"\\newcommand{{\\nAuditMatch}}{{{sum(r['rank_of_claim'] == 1 for r in scored)}}}",
    ])
    print(f"wrote {GEN}")


if __name__ == "__main__":
    main()
