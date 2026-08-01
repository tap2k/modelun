"""
Import conduct Contract-A transcripts into a local Scout transcript db.

One Scout transcript per (model, scene, run). Idempotent (transcript_id is
stable), so re-running after new benchmark runs only adds the new cells.

    .venv/bin/python import_transcripts.py            # data/benchmark
    .venv/bin/python import_transcripts.py unclamped  # data/benchmark-unclamped
"""

import asyncio
import json
import sys
from pathlib import Path

from inspect_ai.model import ChatMessageAssistant, ChatMessageUser
from inspect_scout import Transcript, transcripts_db

STUDY = Path(__file__).resolve().parent.parent
VARIANT = "benchmark-unclamped" if "unclamped" in sys.argv[1:] else "benchmark"
DATA = STUDY / "data" / VARIANT
DB = Path(__file__).resolve().parent / "db" / VARIANT


skipped = []


def iter_transcripts():
    for f in sorted(DATA.glob("*.json")):
        doc = json.loads(f.read_text())
        if "scenes" not in doc:  # markers.json etc. share the dir
            continue
        slug, model = doc["slug"], doc["model"]
        for scene_id, scene in doc["scenes"].items():
            for i, run in enumerate(scene["runs"]):
                if any(turn.get("reply") is None for turn in run):
                    skipped.append(f"{slug}:{scene_id}:{i}")
                    continue
                messages = []
                for turn in run:
                    messages.append(ChatMessageUser(content=turn["u"]))
                    messages.append(ChatMessageAssistant(content=turn["reply"]))
                yield Transcript(
                    transcript_id=f"{slug.replace(chr(47), chr(95))}:{scene_id}:{i}",
                    source_type="modelun-conduct",
                    source_id=f"{VARIANT}/{doc.get('script_version', '?')}",
                    metadata={
                        "model_name": model,
                        "slug": slug,
                        "scene": scene_id,
                        "run": i,
                        "register": scene.get("register"),
                        "script_version": doc.get("script_version"),
                        "temperature": doc.get("temperature"),
                    },
                    messages=messages,
                )


async def main():
    n = 0
    async with transcripts_db(str(DB)) as db:
        batch = []
        for t in iter_transcripts():
            batch.append(t)
            n += 1
        await db.insert(batch)
    print(f"imported {n} transcripts -> {DB}")
    if skipped:
        print(f"skipped {len(skipped)} error-stub runs (null replies): {skipped[:5]}{'...' if len(skipped) > 5 else ''}")


asyncio.run(main())
