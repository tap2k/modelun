#!/usr/bin/env python3
"""Build a paper's arXiv source package: <paper>/arxiv/ (staged, with the package's own PDF) and
<paper>/<name>-arxiv.tar.gz, plus <paper>/arxiv-abstract.txt for the submission form.

arXiv compiles with pdflatex and wants the .bbl rather than a BibTeX run, so the package carries main.bbl from a
clean build. Every local \\input{...} and \\rows{...} (the papers' table-row macro) is inlined into one main.tex,
full-line comments are stripped because arXiv publishes the source, and \\pdfoutput=1 goes on the first line.
Figures named by \\includegraphics and any local .sty, .cls or .bst the source uses are copied beside it. The package
is then built on its own (without \\pdfoutput, which under tectonic's XeTeX makes hyperref pick the pdfTeX driver)
and its page count is checked against the paper's. Nothing here knows what a study is.

    python3 harness/make_arxiv.py studies/consensus/paper-brands --name taste
    python3 harness/make_arxiv.py studies/conduct/paper                      # name defaults to the study's

The outputs are regenerable and gitignored in each paper directory.
"""
import argparse, re, shutil, subprocess, sys, tarfile
from pathlib import Path

ABSTRACT_LIMIT = 1920
ROWS_DEF = re.compile(r"\\makeatletter\\newcommand\{\\rows\}\[1\]\{\\@@input #1 \}\\makeatother\n?")
INCLUDE = re.compile(r"\\(?:input|rows)\{([^}]+)\}")


def flatten(base, text):
    """Inline every local \\input / \\rows file, recursively; leave anything that is not a local file alone."""
    def inline(m):
        p = base / m.group(1)
        p = p if p.suffix else p.with_suffix(".tex")
        return "\n" + flatten(base, p.read_text()).strip() + "\n" if p.is_file() else m.group(0)
    return INCLUDE.sub(inline, text)


def strip_comments(text):
    return "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("%")) + "\n"


def pages(pdf):
    out = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
    return int(re.search(r"Pages:\s+(\d+)", out).group(1))


def assets(base, src):
    """Local files the source needs beside main.tex: figures, and .sty / .cls / .bst it names."""
    found = set()
    for g in re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", src):
        p = base / g
        cands = [p] if p.suffix else [p.with_suffix(e) for e in (".pdf", ".png", ".jpg", ".jpeg", ".eps")]
        hit = next((c for c in cands if c.is_file()), None)
        if not hit:
            sys.exit(f"figure not found: {g}")
        found.add(hit)
    for kind, ext in (("usepackage", ".sty"), ("documentclass", ".cls"), ("bibliographystyle", ".bst")):
        for names in re.findall(r"\\" + kind + r"(?:\[[^\]]*\])?\{([^}]+)\}", src):
            for n in names.split(","):
                p = base / (n.strip() + ext)
                if p.is_file():
                    found.add(p)
    return sorted(found)


def plain_abstract(src):
    m = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", src, re.S)
    if not m:
        return None
    a = m.group(1)
    for tex, txt in [("\\noindent", ""), ("\\medskip", "\n\n"), ("\\dots", "..."), ("\\ldots", "..."), ("``", '"'),
                     ("''", '"'), ("\\%", "%"), ("{,}", ","), ("\\leq", " <= "), ("\\log_2", "log2"), ("\\alpha", "alpha"),
                     ("\\kappa", "kappa"), ("\\eta", "eta"), ("\\rho", "rho"), ("\\&", "&")]:
        a = a.replace(tex, txt)
    a = re.sub(r"\\(?:emph|textit|textbf)\{([^}]*)\}", r"\1", a)
    a = re.sub(r"\$([^$]*)\$", lambda m: m.group(1).replace("^", "").replace("{", "").replace("}", ""), a)
    a = a.replace("~", " ")
    return "\n\n".join(" ".join(p.split()) for p in a.split("\n\n") if p.strip())


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("paper", type=Path, help="the paper directory (holds main.tex and references.bib)")
    ap.add_argument("--name", help="bundle name, <name>-arxiv.tar.gz; default: the study's directory name")
    ap.add_argument("--tex", default="main.tex")
    a = ap.parse_args()
    base = a.paper.resolve()
    name = a.name or base.parent.name
    tex = base / a.tex
    stage, tarball = base / "arxiv", base / f"{name}-arxiv.tar.gz"
    shutil.rmtree(stage, ignore_errors=True)
    tarball.unlink(missing_ok=True)
    (stage / ".build").mkdir(parents=True)

    # 1. the .bbl, and the paper's own PDF, from a clean build of the real source
    subprocess.run(["tectonic", "--keep-intermediates", "--outdir", str(stage / ".build"), str(tex)],
                   check=True, capture_output=True)
    shutil.copy(stage / ".build" / (tex.stem + ".bbl"), stage / "main.bbl")
    paper_pages = pages(stage / ".build" / (tex.stem + ".pdf"))
    shutil.rmtree(stage / ".build")

    # 2. one source file, comments stripped, \pdfoutput=1 first
    src = strip_comments(flatten(base, ROWS_DEF.sub("", tex.read_text())))
    if INCLUDE.search(src):
        sys.exit(f"left unresolved: {INCLUDE.search(src).group(0)}")
    (stage / "main.tex").write_text("\\pdfoutput=1\n" + src)
    shutil.copy(base / "references.bib", stage / "references.bib")
    files = ["main.tex", "main.bbl", "references.bib"]
    for p in assets(base, src):
        rel = p.relative_to(base)
        (stage / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(p, stage / rel)
        files.append(str(rel))

    # 3. the package builds on its own, to the paper's page count
    check = stage / ".check"
    shutil.copytree(stage, check, ignore=shutil.ignore_patterns(".check"))
    (check / "main.tex").write_text(src)
    r = subprocess.run(["tectonic", "main.tex"], cwd=check, capture_output=True, text=True)
    if r.returncode:
        sys.exit("arxiv/main.tex does not build:\n" + r.stderr[-2000:])
    shutil.move(check / "main.pdf", stage / "main.pdf")
    shutil.rmtree(check)
    pkg_pages = pages(stage / "main.pdf")
    if pkg_pages != paper_pages:
        sys.exit(f"page count differs: paper {paper_pages}, package {pkg_pages}")
    with tarfile.open(tarball, "w:gz") as t:
        for f in files:
            t.add(stage / f, arcname=f)
    print(f"-> {tarball.relative_to(Path.cwd()) if tarball.is_relative_to(Path.cwd()) else tarball}: "
          f"{', '.join(files)} ({pkg_pages} pages, as the paper)")

    # 4. the abstract as plain text for the submission form
    t = plain_abstract(src)
    if t is None:
        print("no abstract environment found; arxiv-abstract.txt not written")
    elif re.search(r"[\\$]", t):
        sys.exit("TeX left in the plain-text abstract: " + t[:200])
    elif len(t) > ABSTRACT_LIMIT:
        print(f"abstract is {len(t)} characters, over arXiv's {ABSTRACT_LIMIT}; arxiv-abstract.txt not written")
    else:
        (base / "arxiv-abstract.txt").write_text(t + "\n")
        print(f"wrote arxiv-abstract.txt, {len(t)} characters")


if __name__ == "__main__":
    main()
