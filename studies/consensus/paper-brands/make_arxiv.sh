#!/usr/bin/env bash
# Build the arXiv source package (arxiv/, taste-arxiv.tar.gz, arxiv-abstract.txt); see harness/make_arxiv.py.
exec python3 "$(dirname "$0")/../../../harness/make_arxiv.py" "$(dirname "$0")" --name taste
