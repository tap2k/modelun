"""Contract B label files for closed labeling: the target id and the latest-row rule, in one place.

label_server.py, label_llm.py, label_agree.py and label_notes.py join rows on the same key, so they take it from here
(docs/harness.md § Human labeling: conventions). Internal to the harness; a study that labels through these tools
may import it too.
"""
import json
from pathlib import Path


def target_id(target):
    """the join key of a label: its target without the criterion, as sorted-key JSON"""
    return json.dumps({k: v for k, v in target.items() if k != "criterion"}, sort_keys=True)


def read_jsonl(path):
    path = Path(path)
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()] if path.exists() else []


def latest(rows):
    """target id -> the latest row for it: a relabel appends, and the last row wins"""
    return {target_id(r["target"]): r for r in rows}


def vendor(slug):
    return slug.split("/")[0] if "/" in slug else slug
