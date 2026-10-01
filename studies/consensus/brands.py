"""Whole-name scoring for the brand battery (spec 1.0-brands); analyze.scorer("brands") uses it.

The census's norm() keeps the last word, which is right for one-word answers and wrong for brands
("Delta Air Lines" -> "lines"). brand_name() applies norm's junk guard, keeps the first line as a whole
name, strips markup, quotes, tags and trailing punctuation, drops parentheticals, rejects answers over
five words, and merges variants through ALIASES. ALIASES applies to brand transcripts only;
answer_variants.json is the census's per-category variant map, kept out of the published numbers.
"""
import re
import unicodedata

from analyze import JUNK, ACK

# Variant -> canonical name. Spellings and full vs. short names of one brand. Console product lines
# merge into their family (PlayStation 5 -> playstation); iPhone stays separate from Apple.
ALIASES = {
    "coke": "coca-cola", "coca cola": "coca-cola", "cocacola": "coca-cola",
    "mcdonalds": "mcdonald's", "mc donald's": "mcdonald's",
    "lays": "lay's", "hersheys": "hershey's", "hershey": "hershey's", "kelloggs": "kellogg's", "kellogg": "kellogg's",
    "amazon web services": "aws",
    "delta air lines": "delta", "delta airlines": "delta",
    "jpmorgan chase": "chase", "jp morgan chase": "chase", "chase bank": "chase",
    "marriott international": "marriott", "marriott bonvoy": "marriott",
    "hilton hotels": "hilton", "hilton worldwide": "hilton",
    "google chrome": "chrome", "mozilla firefox": "firefox",
    "playstation 5": "playstation", "playstation 4": "playstation", "playstation 2": "playstation",
    "ps5": "playstation", "sony playstation": "playstation",
    "nintendo switch": "nintendo", "nintendo switch 2": "nintendo",
    "twitter": "twitter/x", "x": "twitter/x",
    "open ai": "openai", "google deepmind": "deepmind",
    "google search": "google", "amazon.com": "amazon", "apple inc": "apple",
    "colgate-palmolive": "colgate", "cheerios cereal": "cheerios", "tesla motors": "tesla",
    "hermes": "hermès", "hilton hotels & resorts": "hilton", "jpmorgan chase & co": "chase",
    "ihg hotels & resorts": "ihg",
}
TAG = re.compile(r"<[^>]*>")
INVISIBLE = re.compile(r"[\u200b-\u200f\u2060\ufeff]")
# A sentence around the name: keep the name ("the brand is converse" -> "converse").
LEAD_IN = re.compile(r"^(?:(?:sure|okay|ok)[!,.]?\s+)?(?:(?:the (?:brand|name|answer|company)(?: name)? is|my name is"
                     r"|i am|i'm|it's|it is|i'd (?:say|pick|go with)|i would (?:say|pick)|how about)\s+)?")
# Not an answer at all: talk about the task, or reasoning leaking into the reply.
NON_ANSWER = re.compile(r"^(?:i'll|i will|i think|let me|\d+\.)|user's request")
DASHES = str.maketrans({"’": "'", "‐": "-", "–": "-"})


def brand_name(reply):
    if not reply:
        return None
    r = unicodedata.normalize("NFKC", reply).strip().split("\n")[0]
    r = TAG.sub("", r)
    if JUNK.search(r) or ACK.match(r):
        return None
    r = re.sub(r"[*_`\"“”]", "", r).translate(DASHES)
    r = re.sub(r"\s*\(.*?\)\s*", " ", r).strip().lower()
    r = re.sub(r"^[^\w]+|[^\w'&+!]+$", "", INVISIBLE.sub("", r)).rstrip("!").strip()
    if NON_ANSWER.search(r):
        return None
    r = LEAD_IN.sub("", r)
    if not r or len(r.split()) > 5:
        return None
    return ALIASES.get(r, r)
