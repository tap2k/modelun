"""analyze_sweep.py — the prompt-strength U-curve for paper 2.

For each rung of the ladder (L0 baseline .. L4 extreme anti-mode), compute the model field's
mean effective population size (inverse Simpson) and mean Jensen-Shannon distance to the human
first-response distribution, across the 20 human-overlap categories. Prediction: effective-N
rises monotonically; JS-to-human is U-shaped and never reaches 0.

    ../../.venv/bin/python analyze_sweep.py   -> probes/sweep_curve.json, probes/sweep_curve.pdf
"""
import json, sys, re
from pathlib import Path
from collections import Counter
import numpy as np
import pdfplumber
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from analyze import norm, load

# ---- human first-response distributions (from local VO PDF; not redistributed) ----
VO = Path("~/Downloads/1-s2.0-S0749596X03001451-main.pdf").expanduser()
text = "\n".join((p.extract_text() or "") for p in pdfplumber.open(str(VO)).pages[7:47])
cats, cur = {}, None
for ln in text.split("\n"):
    ln = ln.strip()
    m = re.match(r"^(\d{1,2})\.([A-Za-z].*)", ln.replace(" ", ""))
    if m and 1 <= int(m.group(1)) <= 70:
        cur = m.group(2).replace(" ", "").replace("(cid:1)", "'"); cats[cur] = []; continue
    if cur is None or ln.startswith(("Response", "(")) or "Overall" in ln or "VanOverschelde" in ln.replace(" ", ""):
        continue
    nums = re.findall(r"\d+\.\d+", ln)
    if not nums: continue
    resp = ln[:ln.find(nums[0])].strip()
    if not resp: continue
    v = [float(x) for x in nums]
    cats[cur].append((resp, v[1] if len(v) >= 8 else 0.0))
MAP = {'Apreciousstone':'gemstone','Ametal':'metal','Afour-footedanimal':'animal','Atypeoffabric':'fabric',
 'Acolor':'color','Afruit':'fruit','Acountry':'country',"Acarpenter'stool":'tool','Asport':'sport',
 'Amusicalinstrument':'instrument','Abird':'bird','Avegetable':'vegetable','Aflower':'flower','Atree':'tree',
 'Afish':'fish','Acity':'city','Aninsect':'insect','Atypeofdance':'dance','Anoccupationorprofession':'occupation','Anherb':'herb'}
hnorm = lambda s: norm(re.sub(r"\(.*?\)", "", s).lower()) or s.lower()
human = {MAP[k]: Counter({hnorm(r): f for r, f in v if f > 0}) for k, v in cats.items() if k in MAP}

def dist(counter):
    n = sum(counter.values()); return {k: v / n for k, v in counter.items()}
def js(p, q):
    keys = set(p) | set(q)
    P = np.array([p.get(k, 0) for k in keys]); Q = np.array([q.get(k, 0) for k in keys]); M = (P + Q) / 2
    kl = lambda a, b: np.sum(a[a > 0] * np.log2(a[a > 0] / b[a > 0]))
    return 0.5 * kl(P, M) + 0.5 * kl(Q, M)
def eff_n(counter):
    ps = np.array(list(dist(counter).values())); return 1.0 / np.sum(ps ** 2)

def merged(toks):
    pool = Counter(toks); stems = {w: w[:-1] for w in pool if w.endswith("s") and w[:-1] in pool}
    return Counter(stems.get(t, t) for t in toks)
def field_from_replies(replies, cat):
    return merged([t for lab in replies for r in replies[lab].get(cat, []) if r for t in [norm(r)] if t])

# ---- baseline (L0) from the main study ----
ans = load(HERE); models = sorted(m for m in ans if ans[m])
def l0_field(cat):
    return merged([a for m in models for a in ans[m].get(cat, [])])

CATS = list(human)
LEVELS = [("L0", None), ("L1", "probes/sweep_L1.json"), ("L2", "probes/sweep_L2.json"),
          ("L3", "probes/persona.json"), ("L4", "probes/sweep_L4.json")]

curve = []
for lvl, path in LEVELS:
    replies = json.loads((HERE / path).read_text())["replies"] if path else None
    effs, jss, mods = [], [], []
    for c in CATS:
        f = l0_field(c) if replies is None else field_from_replies(replies, c)
        if not f: continue
        effs.append(eff_n(f)); jss.append(js(dist(f), dist(human[c])))
        mods.append(f.most_common(1)[0][1] / sum(f.values()))
    curve.append({"level": lvl, "eff_n": round(float(np.mean(effs)), 2),
                  "js_to_human": round(float(np.mean(jss)), 3),
                  "modal_share": round(float(np.mean(mods)), 3)})

human_eff = round(float(np.mean([eff_n(human[c]) for c in CATS])), 2)
print(f"{'level':6} {'eff-N':>6} {'JS->human':>10} {'modal share':>12}")
for r in curve:
    print(f"{r['level']:6} {r['eff_n']:6.2f} {r['js_to_human']:10.3f} {r['modal_share']:11.0%}")
print(f"{'human':6} {human_eff:6.2f} {0.0:10.3f}  (reference)")

(HERE / "probes/sweep_curve.json").write_text(json.dumps(
    {"curve": curve, "human_eff_n": human_eff, "n_categories": len(CATS)}, indent=1) + "\n")

# ---- figure: eff-N and JS-to-human vs prompt strength ----
xs = np.arange(len(curve)); labs = [r["level"] for r in curve]
fig, ax1 = plt.subplots(figsize=(5.2, 3.4))
BLUE, AMBER = "#2a78d6", "#b07500"
ax1.plot(xs, [r["eff_n"] for r in curve], "-o", color=BLUE, label="effective N")
ax1.axhline(human_eff, color=BLUE, ls=":", lw=1, alpha=0.6)
ax1.set_ylabel("effective population size", color=BLUE)
ax1.set_xticks(xs); ax1.set_xticklabels(labs)
ax1.set_xlabel("prompt strength (L0 none $\\rightarrow$ L4 extreme anti-mode)")
ax2 = ax1.twinx()
ax2.plot(xs, [r["js_to_human"] for r in curve], "-s", color=AMBER, label="JS to human")
ax2.set_ylabel("JS distance to human", color=AMBER)
ax1.spines["top"].set_visible(False); ax2.spines["top"].set_visible(False)
fig.tight_layout(); fig.savefig(HERE / "probes/sweep_curve.pdf")
print("-> probes/sweep_curve.json, probes/sweep_curve.pdf")
