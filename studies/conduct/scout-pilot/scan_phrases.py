"""
Judge-free house-style sweep: assistant-side hedge/empathy boilerplate across
the conduct corpus, aggregated per model. No LLM involved (grep_scanner).

    .venv/bin/python scan_phrases.py
"""

from collections import defaultdict

from inspect_scout import Scanner, Transcript, grep_scanner, scan, scanner, transcripts_from

PHRASES = [
    "I hear you",
    "It's important to note",
    "It's worth noting",
    "I understand your frustration",
    "I appreciate your",
    "That said,",
    "I'm sorry you're",
    "You're absolutely right",
    "I must respectfully",
    "As an AI",
]


@scanner(messages=["assistant"])
def house_style() -> Scanner[Transcript]:
    return grep_scanner(PHRASES)


def main():
    status = scan(
        scanners=[house_style()],
        transcripts=transcripts_from("db/benchmark"),
    )
    print(type(status))
    print(status)


if __name__ == "__main__":
    main()
