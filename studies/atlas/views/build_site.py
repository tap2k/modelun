#!/usr/bin/env python3
"""transcripts + labels → views/site/index.html: a static draft of the atlas for reviewing
the data. Profile table, model entries, then one section per scenario from SECTIONS.
Pilot data is placeholder; the design is what's under review.  python views/build_site.py"""
import html, re, statistics as st, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import atlas

T, L = atlas.transcripts(), atlas.labels()
SPEC = atlas.spec(); PROMPT = atlas.prompts(SPEC)
CRITERIA, _ = atlas.criteria()
SPANS = atlas.span_index(L)
models = list(T)
esc = html.escape
short = atlas.short
S = {(m, a): atlas.samples(T, m, a) for m in models for a in T[m]["cells"]}   # cell → non-errored samples
mean = lambda xs: st.mean(xs) if xs else 0

def spans(m, a, i, c): return SPANS.get((m, a, i), {}).get(c, [])
def per_sample(m, a, c): return [len(spans(m, a, i, c)) for i, _ in enumerate(S.get((m, a), []))]
def per_anchor_mean(m, c): return mean([len(spans(m, a, i, c)) for a in T[m]["cells"] for i, _ in enumerate(S[(m, a)])])

# ---------- profile ----------
def global_rows():
    rows = []
    for m in models:
        acc = Counter(); eff = []; out = usd = n = 0
        for a in T[m]["cells"]:
            for s in S[(m, a)]:
                n += 1; acc.update(atlas.metrics(s["reply"]))
                vis, rt, cost = atlas.usage_split(s.get("usage"))
                if vis > 0: eff.append(rt / vis); out += vis; usd += cost
        rows.append({"model": m, **{k: v / n for k, v in acc.items()}, "asks": per_anchor_mean(m, "questions_to_user"),
                     "offers": per_anchor_mean(m, "offers_help"), "effort": st.median(eff) if eff else 0, "cost": 1000 * usd / out if out else 0})
    return rows

def bar(v, vmax, w=60): return f'<span class="bar" style="width:{int(w * v / vmax) if vmax else 0}px"></span>'

def table(cols, rows, fmt):
    vmax = {c: max((r[c] for r in rows), default=0) for c in cols if c != "model"}
    h = "<table><tr>" + "".join(f"<th{'' if c == 'model' else ' class=num'}>{esc(c)}</th>" for c in cols) + "</tr>"
    for r in rows:
        h += "<tr>" + "".join(f"<td><b>{esc(short(r[c]))}</b></td>" if c == "model" else f"<td class=num>{fmt.get(c, '{:.1f}').format(r[c])} {bar(r[c], vmax[c])}</td>" for c in cols) + "</tr>"
    return h + "</table>"

# ---------- pieces ----------
def link(m, a=None): return f'../index.html?{"anchor=" + a + "&" if a else ""}model={m}'

def receipts(a, crit=None, maxlen=420):
    """one card per model: the criterion's first span, or the first reply"""
    h = '<div class="receipts">'
    for m in models:
        ss = S.get((m, a))
        if not ss: continue
        if crit:
            sp = next((x["span"] for i, _ in enumerate(ss) for x in spans(m, a, i, crit)), None)
            body = f"“{esc(sp)}”" if sp else "<span class=mut>none</span>"
        else:
            body = esc(ss[0]["reply"][:maxlen]) + ("…" if len(ss[0]["reply"]) > maxlen else "")
        h += f'<div class="r"><b><a href="{link(m, a)}">{esc(short(m))}</a></b><div>{body}</div></div>'
    return h + "</div>"

def grid(a, cols):
    """cols: (label, criterion, 'yes'|'count') — yes = samples with any span, count = mean spans"""
    h = "<table><tr><th>model</th>" + "".join(f"<th class=num>{esc(q)}</th>" for q, _, _ in cols) + "</tr>"
    for m in models:
        h += f"<tr><td><b>{esc(short(m))}</b></td>"
        for _, c, kind in cols:
            v = per_sample(m, a, c)
            h += f"<td class=num>{sum(1 for x in v if x)}/{len(v)}</td>" if kind == "yes" else f"<td class=num>{mean(v):.1f}</td>"
        h += "</tr>"
    return h + "</table>"

def ranked(counter, top=12, label=lambda k: k):
    vmax = max(counter.values(), default=0)
    return "<table>" + "".join(f"<tr><td>{esc(label(k))}</td><td class=num>{c} {bar(c, vmax)}</td></tr>" for k, c in counter.most_common(top)) + "</table>"

# ---------- scenario-specific pieces ----------
JOKES = [("dark mode", "dark mode"), ("eggs", "egg"), ("oct 31 == dec 25", "oct")]   # cluster key by needle in reply
def joke_key(reply):
    r = reply.lower()
    return next((k for k, needle in JOKES if needle in r), atlas.norm(reply)[:40])

def joke_census():
    C = Counter(); who = {}
    for m in models:
        for s in S.get((m, "create-a1"), []):
            k = joke_key(s["reply"]); C[k] += 1; who.setdefault(k, set()).add(short(m))
    total = sum(C.values())
    return ("<table><tr><th>joke</th><th class=num>share of panel</th><th>who</th></tr>"
            + "".join(f"<tr><td>{esc(k)}</td><td class=num>{c}/{total} {bar(c, total)}</td><td class=mut>{esc(', '.join(sorted(who[k])))}</td></tr>" for k, c in C.most_common())
            + "</table>" + receipts("create-a1", maxlen=160))

def coffee():
    C = Counter(); ex = {}
    for m in models:
        for i, _ in enumerate(S.get((m, "create-a3"), [])):
            for x in spans(m, "create-a3", i, "names_offered"):
                k = atlas.norm(x["span"]); C[k] += 1; ex.setdefault(k, x["span"].strip('*" '))
    per = ", ".join(f"{esc(short(m))} {mean(per_sample(m, 'create-a3', 'names_offered')):.0f}" for m in models)
    return f"<p>Names per reply (the prompt asks for one): {per}</p>" + ranked(C, label=lambda k: ex[k])

REF_WORDS = ["Elias", "Mara", "Elara", "keeper", "baker", "mayor", "clockmaker", "fisherman", "librarian", "conductor", "lighthouse"]
def story():
    stories = [s["reply"] for m in models for s in S.get((m, "create-a2"), [])]
    hits = Counter(w for r in stories for w in REF_WORDS if re.search(r"\b" + w + r"s?\b", r, re.I))
    anyhit = sum(any(re.search(r"\b" + w + r"s?\b", r, re.I) for w in REF_WORDS) for r in stories)
    lead = f"Hamilton &amp; Mimno (2026) find at least one of eleven words in 88% of stories from four small-tier models; here {anyhit}/{len(stories)} ({100*anyhit/max(len(stories),1):.0f}%) contain one."
    return lead, ("<table><tr><th>reference word</th><th class=num>stories containing it</th></tr>"
                  + "".join(f"<tr><td>{w}</td><td class=num>{hits[w]}/{len(stories)} {bar(hits[w], len(stories))}</td></tr>" for w in REF_WORDS if hits[w])
                  + "</table>" + receipts("create-a2", maxlen=140))

# ---------- sections: (title, lead, body) driven by anchors and criteria ----------
TITLES = {"resist-a1": "Day-trader", "resist-a2": "Restaurant review", "console-a1": "Console: dad’s sick", "console-a2": "Console: didn’t get the job",
          "interpret-a3": "Step counts", "interpret-a1": "Circle back", "interpret-a2": "Interesting approach", "advise-a1": "Job offer", "advise-a2": "Sister’s loan"}
def title_for(a): return TITLES.get(a, a)

SECTIONS = [
    ("resist-a1", "Three questions, answered per sample.", [("tells them not to", "tells_them_not_to", "yes"), ("encourages", "encourages", "yes"), ("probes", "probes", "yes"), ("asks (any question)", "questions_to_user", "yes")], "tells_them_not_to"),
    ("resist-a2", "Not yet collected on the pilot panel.", [("writes it", "writes_it", "yes"), ("offers another way", "offers_another_way", "yes"), ("preaches (sentences)", "preaches", "count")], "offers_another_way"),
    ("console-a2", "Sentences that stay with the feeling vs sentences that move to action, per reply.", [("stays with feeling", "stays_with_feeling", "count"), ("pivots to action", "pivots_to_action", "count"), ("asks", "questions_to_user", "yes"), ("offers resources", "offers_resources", "yes")], None),
    ("console-a1", "Same measures.", [("stays with feeling", "stays_with_feeling", "count"), ("pivots to action", "pivots_to_action", "count"), ("asks", "questions_to_user", "yes"), ("offers resources", "offers_resources", "yes")], None),
    ("interpret-a3", "The numbers are flat. Reading a pattern into them is the tell.", [("restates the data", "restates_data", "count"), ("reads a pattern", "reads_a_pattern", "count"), ("adds outside context", "adds_outside_context", "count")], "reads_a_pattern"),
    ("interpret-a1", "", [("readings offered", "readings", "count"), ("asks", "questions_to_user", "yes")], None),
    ("advise-a1", "", [("options offered", "options", "count"), ("takes a side", "directional", "yes"), ("asks", "questions_to_user", "yes")], None),
]

# ---------- model entries: caricature, facts, receipts ----------
def entry(m):
    g = next(r for r in G if r["model"] == m)
    rank = lambda k: sorted(G, key=lambda r: -r[k]).index(g) + 1
    names = [x["span"].strip('*" ') for x in spans(m, "create-a3", 0, "names_offered")]
    same_joke = sum(joke_key(s["reply"]) == "dark mode" for s in S.get((m, "create-a1"), []))
    protag = [next((x["span"] for x in spans(m, "create-a2", i, "protagonist")), "—") for i, _ in enumerate(S.get((m, "create-a2"), []))]
    piv, stay = mean(per_sample(m, "console-a2", "pivots_to_action")), mean(per_sample(m, "console-a2", "stays_with_feeling"))
    tell, probes = mean(per_sample(m, "resist-a1", "tells_them_not_to")), mean(per_sample(m, "resist-a1", "questions_to_user"))
    opts = mean([len(spans(m, a, i, "options")) for a in CRITERIA["options"]["applies_to"] for i, _ in enumerate(S.get((m, a), []))])
    # ordered (predicate, caricature, fact): first true wins
    TRAITS = [
        (rank("asks") == 1 and g["asks"] > 0, "Interviews you.", "Asks a question back in more replies than any model on the panel."),
        (g["asks"] == 0, "Answers and leaves.", "Never asks a question back."),
        (len(names) >= 20, "Gives you everything.", f"{len(names)} names when you asked for one; {opts:.0f} versions of every draft."),
        (len(names) == 1 and opts < 1.2, "One answer.", "One name where others give a list; one draft, no options."),
        (piv >= 2, "Moves to action.", "Told you didn't get the job, it tells you what to do next."),
        (tell >= 1.5, "Tells you no.", "Told you're quitting to day-trade, it says don't, twice per reply."),
        (rank("effort") == 1 and g["effort"] > 1, "Thinks first.", f"Spends {g['effort']:.0f}× more tokens thinking than saying."),
        (rank("bold") == 1, "Formats everything.", "More bold and headers than any model on the panel."),
        (rank("words") == len(G), "Short.", "The shortest replies on the panel."),
        (True, "Middle of the panel.", "No habit stands out; that is the finding."),
    ]
    head, facts = next(((h, [f]) for ok, h, f in TRAITS if ok))
    if same_joke == 3: facts.append("Tells the same joke as everyone else, three times out of three.")
    if len(set(protag)) == 1 and protag[0] != "—": facts.append(f"Names the protagonist {protag[0]} every time.")
    if stay >= 2 and piv <= 0.5: facts.append("Told you didn't get the job, it stays with it and doesn't push you to act.")
    if probes >= 1: facts.append(f"Told you're quitting to day-trade, it asks {probes:.0f} question{'s' if probes >= 1.5 else ''} before it advises.")
    first_span = lambda a, c: next((x["span"] for i, _ in enumerate(S.get((m, a), [])) for x in spans(m, a, i, c)), None)
    first_reply = lambda a, n=170: (S[(m, a)][0]["reply"].strip().replace("\n", " ")[:n] + "…") if S.get((m, a)) else None
    rec = [("console-a2", "“I didn’t get the job.”", first_span("console-a2", "pivots_to_action") or first_reply("console-a2")),
           ("create-a3", "Name for a coffee shop", " · ".join(names[:6]) + (f" … (+{len(names)-6})" if len(names) > 6 else "") if names else None),
           ("create-a2", "Write a story, three times", " · ".join(protag) if protag else None),
           ("resist-a1", "Day-trader", first_span("resist-a1", "tells_them_not_to") or first_span("resist-a1", "questions_to_user") or first_reply("resist-a1"))]
    h = f'<div class="entry"><h3><a href="{link(m)}">{esc(short(m))}</a> <span class=mut>· Aug 2026 · pilot</span></h3><p><b>{esc(head)}</b> {esc(" ".join(facts[:3]))}</p><ul>'
    h += "".join(f'<li><i><a href="{link(m, a)}">{esc(k)}</a>:</i> {esc(v)}</li>' for a, k, v in rec if v)
    return h + "</ul></div>"

# ---------- page ----------
G = global_rows()
lead_story, body_story = story()
sec = [("Profile", "Global measures on every cell, per model, pilot panel. <b>words</b>, <b>bullets</b>, <b>headers</b>, <b>bold</b>: means per reply. <b>modals</b>: " + " / ".join(atlas.MODAL_WORDS) + " per 100 words. <b>asks</b>: questions the reply expects you to answer, per reply. <b>offers</b>: offers to do more work, per reply. <b>effort</b>: median reasoning tokens ÷ visible output tokens. <b>cost</b>: USD per 1k visible output tokens.",
        table(["model", "words", "bullets", "headers", "bold", "modals", "asks", "offers", "effort", "cost"], G, {"words": "{:.0f}", "modals": "{:.2f}", "effort": "{:.2f}", "cost": "${:.4f}"})),
       ("Entries", "One caricature per model, the two or three facts that make it true, and the receipts that prove it. Caricatures are template-generated here; on the site they come from an edited entries file.", "".join(entry(m) for m in models)),
       ("Joke census", f"“{esc(PROMPT['create-a1'])}” Convergence: share of the panel's replies telling the same joke.", joke_census()),
       ("Coffee shop", f"“{esc(PROMPT['create-a3'])}” Names suggested across the panel; the top of the list is what everyone reaches for.", coffee()),
       ("Short story", f"“{esc(PROMPT['create-a2'])}” Nothing was planted. {lead_story}", body_story)]
sec += [(title_for(a), f"“{esc(PROMPT[a])}” {lead}", grid(a, cols) + receipts(a, rc, maxlen=200)) for a, lead, cols, rc in SECTIONS]

CSS = """.receipts{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:8px;margin:10px 0}
.r{background:var(--soft);border-radius:6px;padding:8px 10px;font-size:12.5px;line-height:1.4}.r b{display:block;margin-bottom:4px}
.entry{background:var(--soft);border-radius:8px;padding:12px 16px;margin:10px 0}.entry h3{margin:0 0 6px;font-size:15px}.entry p{margin:0 0 6px}.entry ul{margin:0;padding-left:18px;font-size:13px;color:var(--mut)}.entry li i{color:var(--fg);font-style:normal;font-weight:500}
nav{font-size:13px;color:var(--mut);margin:8px 0 20px}nav a{margin-right:10px}"""
nav = "".join(f'<a href="#s{i}">{esc(t.split(":")[0])}</a>' for i, (t, _, _) in enumerate(sec))
body = f"<h1>atlas · draft</h1><p class=lead>Pilot panel, {len(models)} models, spec {esc(SPEC['spec_version'])}. Placeholder data; the layout is what is under review. Every model name and receipt links to the full transcripts.</p><nav>{nav}</nav>"
body += "".join(f'<h2 id="s{i}">{t}</h2><p class=lead>{d}</p>{h}' for i, (t, d, h) in enumerate(sec))
(atlas.HERE / "views/site/index.html").write_text(f'<!doctype html><meta charset=utf-8><title>atlas · draft</title><link rel=stylesheet href="../atlas.css"><style>{CSS}</style><main>{body}</main>\n')
print(f"→ views/site/index.html  {len(sec)} sections")
