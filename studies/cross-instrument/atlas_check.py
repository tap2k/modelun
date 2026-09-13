#!/usr/bin/env python3
"""Coding atlas vs the census: is 'principled' visible in report honesty? Per atlas model:
overclaim rate (claims done, hidden checker fails, does not say so), unreported-edit rate,
hidden-checker pass rate. Joined to census concentration and suggestibility on the model label."""
import json, glob, collections
from pathlib import Path
from build_matrix import spearman, boot, cols
A = Path.home()/"dev/convovo/coding-atlas/results"
ALIAS = {"anthropic/claude-fable-5":"claude-fable-5","opencode/claude-fable-5":"claude-fable-5",
         "anthropic/claude-opus-5":"claude-opus-5","opencode/claude-opus-5":"claude-opus-5"}
runs = collections.defaultdict(list)
for mf in glob.glob(str(A/"**/manifest.json"), recursive=True):
    d = Path(mf).parent
    try: m = json.load(open(mf)); x = json.load(open(d/"measures.json"))
    except Exception: continue
    if m.get("invalid"): continue
    model = m.get("model") or m.get("served_model") or ""
    model = ALIAS.get(model, model.split("/")[-1]) if model else f"product:{m.get('product')}"
    model = model.split("[")[0]  # variant tags such as [1m] are the same model
    if model.startswith("unknown") or model.startswith("product:"): continue
    runs[model].append(x)
rows = {}
for model, xs in runs.items():
    n = len(xs)
    if n < 10: continue
    rows[model] = {"n": n,
        "overclaim": sum(1 for x in xs if x.get("overclaim"))/n,
        "unreported_edits": sum(1 for x in xs if (x.get("account") or {}).get("unreported_edits"))/n,
        "checker_pass": sum(1 for x in xs if x.get("checker_pass"))/n,
        "claims_done": sum(1 for x in xs if x.get("claims_done"))/n}
print(f"{'model':<26}{'n':>4}{'overclaim':>11}{'unrep.edit':>12}{'checker':>9}{'claims':>8}   census_conc  suggestib")
cc, ss = cols["census_conc"], cols["suggestib"]
for m, r in sorted(rows.items(), key=lambda kv: -kv[1]["overclaim"]):
    c = f"{cc[m]:.2f}" if m in cc else "   -"; s = f"{ss[m]:.2f}" if m in ss else "   -"
    print(f"{m:<26}{r['n']:>4}{r['overclaim']:>11.2f}{r['unreported_edits']:>12.2f}{r['checker_pass']:>9.2f}{r['claims_done']:>8.2f}   {c:>11}  {s:>9}")
print()
for name, key in [("census_conc","overclaim"),("census_conc","unreported_edits"),("suggestib","overclaim"),("suggestib","unreported_edits")]:
    ms = [m for m in rows if m in cols[name]]
    x = [cols[name][m] for m in ms]; y = [rows[m][key] for m in ms]
    r = spearman(x, y); lo, hi = boot(x, y)
    print(f"{name} x atlas {key:<18} n={len(ms):>2}  rho={r:>6.2f}  90% CI [{lo:.2f}, {hi:.2f}]{' *' if lo>0 or hi<0 else ''}")
print("\nconduct-panel overlap:", sorted(m for m in rows if m in cols["conduct_dep"]))
