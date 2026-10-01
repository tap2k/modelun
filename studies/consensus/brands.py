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
    "hermes": "hermès",
}
TAG = re.compile(r"<[^>]*>")
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
    r = re.sub(r"^[^\w]+|[^\w'&+!]+$", "", r).rstrip("!").strip()
    if not r or len(r.split()) > 5:
        return None
    return ALIASES.get(r, r)
