"""The coder-facing rendering of a codebook file: sections A to D only, the author's evidence
notes and meta sentences stripped, checked before anyone reads it. Shared by the LLM coder
(harness/relabel.py) and the coding page server (harness/viewer/code_server.py), so a human and a
machine coder read the same text. Standard library only, so a clone of the repo can run the page
with nothing installed."""
import re
from pathlib import Path


def codebook_text(path):
    """The coder-facing rendering: sections A to D only, with the author's evidence notes
    stripped. A coder must never see "[v2 tightened; kappa 0.19, over-applied]" or the
    decisions log: on 2026-09-14 six coders read those and under-applied the named codes."""
    s = Path(path).read_text()
    out, keep = [], True
    for line in s.splitlines():
        if line.startswith("## "):
            keep = bool(re.match(r"## [A-D]\b", line))
        if keep:
            out.append(line)
    t = "\n".join(out)
    t = re.sub(r"\*\*\[v\d[^\]]*\]\*\*\s*", "", t)      # **[v2 tightened; ...]**
    t = re.sub(r"\[v\d[^\]]*\]\s*", "", t)                # [v2] / [v2 new] / [v2 new, decide]
    t = re.sub(r"\(v1 text\.?\)\s*", "", t)               # (v1 text.)
    t = re.sub(r"\n\*Considered and dropped[^\n]*\n(?:[^\n]*\n)?", "\n", t)
    t = re.sub(r"(?m)^(\*\*Shape deferred again[^\n]*\n(?:[^\n]+\n)*)", "", t)
    t = t[t.find("## A"):] if "## A" in t else t                # drop the author's preamble
    # drop any sentence that talks about the evidence rather than the code
    META = re.compile(r"judge|coder|pass.one|the human|kappa|\bv[12]\b|decided|residue|unknown.name|reached for|recoded|adjudicat|merged from", re.I)
    # work on paragraphs (a list item or a numbered code is one paragraph even when wrapped)
    paras = re.split(r"\n(?=\n|## |\d+\. \*\*|- \*|\*\*[A-Z])", t)
    out = []
    for para in paras:
        if para.startswith("#") or not para.strip():
            out.append(para); continue
        flat = re.sub(r"\s*\n\s*", " ", para.strip())
        sents = re.split(r"(?<=[.!?])\s+(?=[A-Z\"'(*])", flat)
        kept = [x for x in sents if not META.search(x)]
        out.append(" ".join(kept))
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out))

