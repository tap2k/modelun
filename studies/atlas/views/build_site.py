#!/usr/bin/env python3
"""transcripts + labels → views/site/index.html: a static draft of the atlas for reviewing the data.
Global profile table, then one section per scenario with its measures and receipts.
Pilot data is placeholder; the design is what's under review.  python views/build_site.py"""
import json, re, html, statistics as st
from pathlib import Path
from collections import Counter, defaultdict

HERE = Path(__file__).resolve().parent; STUDY = HERE.parent
T = {p.stem: json.loads(p.read_text()) for p in (STUDY / "transcripts").glob("*.json")}
L = {p.stem: json.loads(p.read_text()) for p in (STUDY / "labels").glob("*.json")}
SPEC = json.loads((STUDY / "spec/stimulus.json").read_text())
PROMPT = {a["id"]: a["text"] for t in SPEC["templates"] for a in t["anchors"]}
models = [m["label"] for m in json.loads((STUDY / "spec/models.json").read_text())["models"] if m["label"] in T]
lab = {(m, s["anchor"], s["i"]): s["spans"] for m in L for s in L[m]["samples"]}
esc = html.escape
MOD = re.compile(r"\b(may|might|could|probably|usually|perhaps)\b", re.I)

def samples(m, a): return [s for s in T[m]["cells"].get(a, {}).get("samples", []) if s.get("reply")]
def spans(m, a, i, c): return lab.get((m, a, i), {}).get(c, [])
def nsp(m, a, c): return [len(spans(m, a, i, c)) for i, _ in enumerate(samples(m, a))]
def mean(xs): return st.mean(xs) if xs else 0
def short(m): return m.replace("-2.4t-a95b", "").replace("gpt-5.6-", "gpt-5.6 ").replace("claude-", "")

# ---------- global profile ----------
def global_rows():
    rows = []
    for m in models:
        allr = [(a, s) for a in T[m]["cells"] for s in samples(m, a)]
        words = [len(s["reply"].split()) for a, s in allr]
        bullets = [len(re.findall(r"^\s*[-*•]\s", s["reply"], re.M)) for a, s in allr]
        headers = [len(re.findall(r"^#+\s", s["reply"], re.M)) for a, s in allr]
        bold = [len(re.findall(r"\*\*[^*]+\*\*", s["reply"])) for a, s in allr]
        modals = [100 * len(MOD.findall(s["reply"])) / max(len(s["reply"].split()), 1) for a, s in allr]
        asks = [len(spans(m, a, i, "questions_to_user")) for a in T[m]["cells"] for i, _ in enumerate(samples(m, a))]
        offers = [len(spans(m, a, i, "offers_help")) for a in T[m]["cells"] for i, _ in enumerate(samples(m, a))]
        eff = []; cost = []; out = 0; usd = 0
        for a, s in allr:
            u = s.get("usage") or {}; ct = u.get("completion_tokens", 0); rt = (u.get("completion_tokens_details") or {}).get("reasoning_tokens") or 0
            if ct - rt > 0: eff.append(rt / (ct - rt)); out += ct - rt; usd += u.get("cost", 0)
        rows.append(dict(model=m, words=mean(words), bullets=mean(bullets), headers=mean(headers), bold=mean(bold), modals=mean(modals),
                         asks=mean(asks), offers=mean(offers), effort=st.median(eff) if eff else 0, cost=1000 * usd / out if out else 0))
    return rows

def bar(v, vmax, w=90):
    return f'<span class="bar" style="width:{int(w * v / vmax) if vmax else 0}px"></span>'

def table(cols, rows, fmt):
    h = "<table><tr>" + "".join(f"<th{' class=num' if c != 'model' else ''}>{esc(c)}</th>" for c in cols) + "</tr>"
    maxes = {c: max((r[c] for r in rows), default=0) for c in cols if c != "model"}
    for r in rows:
        h += "<tr>" + "".join(f"<td><b>{esc(short(r[c]))}</b></td>" if c == "model" else f"<td class=num>{fmt.get(c, '{:.1f}').format(r[c])} {bar(r[c], maxes[c], 60)}</td>" for c in cols) + "</tr>"
    return h + "</table>"

def receipts(a, crit=None, label=None, n=1, maxlen=420):
    """one quoted reply (sample 0) per model, or the spans for a criterion"""
    h = '<div class="receipts">'
    for m in models:
        ss = samples(m, a)
        if not ss: continue
        if crit:
            sp = [x["span"] for i, _ in enumerate(ss) for x in spans(m, a, i, crit)][:n]
            body = "<br>".join(f"“{esc(x)}”" for x in sp) if sp else "<span class=mut>none</span>"
        else:
            body = esc(ss[0]["reply"][:maxlen]) + ("…" if len(ss[0]["reply"]) > maxlen else "")
        h += f'<div class="r"><b>{esc(short(m))}</b>{(" · " + label(m)) if label else ""}<div>{body}</div></div>'
    return h + "</div>"

def yesno_grid(a, qs):
    """qs: list of (question, criterion, kind) kind = 'yes' (any span) or 'count'"""
    h = "<table><tr><th>model</th>" + "".join(f"<th class=num>{esc(q)}</th>" for q, _, _ in qs) + "</tr>"
    for m in models:
        ss = samples(m, a); h += f"<tr><td><b>{esc(short(m))}</b></td>"
        for q, c, kind in qs:
            vals = [len(spans(m, a, i, c)) for i, _ in enumerate(ss)]
            if kind == "yes": h += f"<td class=num>{sum(1 for v in vals if v)}/{len(vals)}</td>"
            else: h += f"<td class=num>{mean(vals):.1f}</td>"
        h += "</tr>"
    return h + "</table>"

def cluster(a, crit, key=lambda s: s):
    C = Counter(); ex = {}
    for m in models:
        for i, _ in enumerate(samples(m, a)):
            for x in spans(m, a, i, crit):
                k = key(x["span"]); C[k] += 1; ex.setdefault(k, x["span"])
    return C, ex

def norm(s): return re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()

# ---------- sections ----------
sec = []
G = global_rows()
sec.append(("Profile", "Global measures on every cell, per model, pilot panel. <b>words</b>, <b>bullets</b>, <b>headers</b>, <b>bold</b>: means per reply. <b>modals</b>: may / might / could / probably / usually / perhaps per 100 words. <b>asks</b>: questions the reply expects you to answer, per reply. <b>offers</b>: offers to do more work, per reply. <b>effort</b>: median reasoning tokens ÷ visible output tokens. <b>cost</b>: USD per 1k visible output tokens.",
            table(["model", "words", "bullets", "headers", "bold", "modals", "asks", "offers", "effort", "cost"], G,
                  {"words": "{:.0f}", "modals": "{:.2f}", "effort": "{:.2f}", "cost": "${:.4f}"})))

# joke census
punch = Counter(); exm = defaultdict(list)
for m in models:
    for s in samples(m, "create-a1"):
        r = s["reply"]; k = "dark mode" if "dark mode" in r.lower() else ("eggs" if "egg" in r.lower() else ("oct 31" if "oct" in r.lower() else norm(r)[:40]))
        punch[k] += 1; exm[k].append(short(m))
h = "<table><tr><th>joke</th><th class=num>share of panel</th><th>who</th></tr>"
for k, c in punch.most_common(): h += f"<tr><td>{esc(k)}</td><td class=num>{c}/{sum(punch.values())} {bar(c, sum(punch.values()))}</td><td class=mut>{esc(', '.join(sorted(set(exm[k]))))}</td></tr>"
sec.append(("Joke census", f"“{esc(PROMPT['create-a1'])}” Convergence: share of the panel’s replies telling the same joke.", h + "</table>" + receipts("create-a1", maxlen=160)))

# coffee shop
C, ex = cluster("create-a3", "names_offered", key=lambda s: norm(s.strip('*"')))
h = "<p>Names per reply (the prompt asks for one): " + ", ".join(f"{esc(short(m))} {mean(nsp(m, 'create-a3', 'names_offered')):.0f}" for m in models) + "</p>"
h += "<table><tr><th>name</th><th class=num>times suggested</th></tr>" + "".join(f"<tr><td>{esc(ex[k])}</td><td class=num>{c} {bar(c, C.most_common(1)[0][1])}</td></tr>" for k, c in C.most_common(12)) + "</table>"
sec.append(("Coffee shop", f"“{esc(PROMPT['create-a3'])}” Names suggested across the panel; the top of the list is what everyone reaches for.", h))

# story
W = ["Elias", "Mara", "Elara", "lighthouse", "clockmaker", "librarian"]
hits = {w: sum(1 for m in models for s in samples(m, "create-a2") if re.search(r"\b" + w + r"\b", s["reply"], re.I)) for w in W}
tot = sum(len(samples(m, "create-a2")) for m in models)
h = "<table><tr><th>reference word (Hamilton &amp; Mimno 2026)</th><th class=num>stories containing it</th></tr>" + "".join(f"<tr><td>{w}</td><td class=num>{c}/{tot} {bar(c, tot)}</td></tr>" for w, c in hits.items()) + "</table>"
anyhit = sum(1 for m in models for s in samples(m, "create-a2") if any(re.search(r"\b" + w + r"s?\b", s["reply"], re.I) for w in ["Elias", "Mara", "Elara", "keeper", "baker", "mayor", "clockmaker", "fisherman", "librarian", "conductor", "lighthouse"]))
sec.append(("Short story", f"“{esc(PROMPT['create-a2'])}” Nothing was planted. Hamilton &amp; Mimno (2026) find at least one of eleven words in 88% of stories from four small-tier models; here {anyhit}/{tot} ({100*anyhit/tot:.0f}%) contain one. Per-word counts below.", h + receipts("create-a2", maxlen=140)))

# day-trader
sec.append(("Day-trader", f"“{esc(PROMPT['resist-a1'])}” Three questions, answered per sample.",
            yesno_grid("resist-a1", [("tells them not to", "tells_them_not_to", "yes"), ("encourages", "encourages", "yes"), ("probes", "probes", "yes"), ("asks (any question)", "questions_to_user", "yes")]) + receipts("resist-a1", "tells_them_not_to")))
# doctor's note
sec.append(("Doctor’s note", f"“{esc(PROMPT['resist-a2'])}”",
            yesno_grid("resist-a2", [("writes the note", "writes_the_note", "yes"), ("offers another way", "offers_another_way", "yes"), ("preaches (sentences)", "preaches", "count")]) + receipts("resist-a2", "offers_another_way")))
# fridge app
sec.append(("Fridge app", f"“{esc(PROMPT['resist-a3'])}” A decent idea in a crowded space.",
            yesno_grid("resist-a3", [("names flaws (count)", "names_flaws", "count"), ("verdict given", "verdict", "yes")]) + receipts("resist-a3", "idea_stance", label=lambda m: ", ".join(sorted({x.get('label', '') for i, _ in enumerate(samples(m, 'resist-a3')) for x in spans(m, 'resist-a3', i, 'idea_stance')})))))
# console
for a in ["console-a2", "console-a1"]:
    sec.append((f"Console: “{esc(PROMPT[a])}”", "Sentences that stay with the feeling vs sentences that move to action, per reply.",
                yesno_grid(a, [("stays with feeling", "stays_with_feeling", "count"), ("pivots to action", "pivots_to_action", "count"), ("asks", "questions_to_user", "yes"), ("offers resources", "offers_resources", "yes")]) + receipts(a, maxlen=220)))
# step counts
sec.append(("Step counts", f"“{esc(PROMPT['interpret-a3'])}” The numbers are flat. Reading a pattern into them is the tell.",
            yesno_grid("interpret-a3", [("restates the data", "restates_data", "count"), ("reads a pattern", "reads_a_pattern", "count"), ("adds outside context", "adds_outside_context", "count")]) + receipts("interpret-a3", "reads_a_pattern")))
# circle back
sec.append(("Circle back", f"“{esc(PROMPT['interpret-a1'])}”",
            yesno_grid("interpret-a1", [("readings offered", "readings", "count"), ("asks", "questions_to_user", "yes")]) + receipts("interpret-a1", maxlen=200)))
# advise
sec.append(("Job offer", f"“{esc(PROMPT['advise-a1'])}”",
            yesno_grid("advise-a1", [("options offered", "options", "count"), ("takes a side", "directional", "yes"), ("asks", "questions_to_user", "yes")]) + receipts("advise-a1", maxlen=200)))

# ---------- page ----------
css = """
:root{--bg:#fff;--fg:#1a1a1a;--mut:#6b6b6b;--line:#e4e4e4;--acc:#2a5db0;--soft:#f6f7f9}
@media(prefers-color-scheme:dark){:root{--bg:#141518;--fg:#e8e8e8;--mut:#9a9a9a;--line:#2c2e33;--acc:#7aa2e8;--soft:#1d1f24}}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 -apple-system,system-ui,sans-serif}
main{max-width:1000px;margin:0 auto;padding:24px 20px}
h1{font-size:22px;margin:0 0 4px}h2{font-size:18px;margin:36px 0 6px;padding-top:12px;border-top:1px solid var(--line)}
p.lead{color:var(--mut);margin:0 0 12px}.mut{color:var(--mut)}
table{border-collapse:collapse;font-size:13px;margin:8px 0}th,td{padding:5px 8px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
th{color:var(--mut);font-weight:500}td.num,th.num{text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}
.bar{display:inline-block;height:8px;background:var(--acc);vertical-align:middle;border-radius:2px;margin-left:6px;opacity:.7}
.receipts{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:8px;margin:10px 0}
.r{background:var(--soft);border-radius:6px;padding:8px 10px;font-size:12.5px;line-height:1.4}.r b{display:block;margin-bottom:4px}
nav{font-size:13px;color:var(--mut);margin:8px 0 20px}nav a{color:var(--acc);text-decoration:none;margin-right:10px}
"""
nav = "".join(f'<a href="#s{i}">{esc(re.sub(r"[“”].*", "", t).strip(": "))}</a>' for i, (t, _, _) in enumerate(sec))
body = f"<h1>atlas · draft</h1><p class=lead>Pilot panel, {len(models)} models, spec {esc(SPEC['spec_version'])}. Placeholder data; the layout is what is under review.</p><nav>{nav}</nav>"
body += "".join(f'<h2 id="s{i}">{t}</h2><p class=lead>{d}</p>{h}' for i, (t, d, h) in enumerate(sec))
(HERE / "site/index.html").write_text(f"<!doctype html><meta charset=utf-8><title>atlas · draft</title><style>{css}</style><main>{body}</main>\n")
print(f"→ {HERE/'site/index.html'}  {len(sec)} sections")
