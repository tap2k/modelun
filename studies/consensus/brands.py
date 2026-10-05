"""Whole-name scoring for the brand battery (spec 1.0-brands); analyze.scorer("brands") uses it.

The census's norm() keeps the last word, which is right for one-word answers and wrong for brands
("Delta Air Lines" -> "lines"). brand_name() applies norm's junk guard, keeps the first line as a whole
name, strips markup, quotes, tags and trailing punctuation, drops parentheticals, rejects answers over
five words, and merges variants through ALIASES. ALIASES applies to brand transcripts only;
answer_variants.json is the census's per-category variant map, kept out of the published numbers.
"""
import re
import unicodedata

from analyze import JUNK, ACK, clean

# Variant -> canonical name. Spellings and full vs. short names of one brand. Console product lines
# merge into their family (PlayStation 5 -> playstation), and iPhone merges into Apple.
ALIASES = {
    "coke": "coca-cola", "coca cola": "coca-cola", "cocacola": "coca-cola", "iphone": "apple",
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
    # misspellings and variant spellings (found by a near-miss scan against each category's common answers)
    "toyoya": "toyota", "cornflakes": "corn flakes", "wal-mart": "walmart", "nintendo 64": "nintendo",
    # from the 2026-10-01 category review (category-specific merges such as google -> google cloud are not
    # made here: this table is global, and google is also a search engine)
    "southwest": "southwest airlines", "united": "united airlines", "kitkat": "kit kat", "legoland usa": "legoland",
    "visa gowns": "visa", "coca puffs": "cocoa puffs", "kellogg's frosted flakes": "frosted flakes",
    "kellogg's corn flakes": "corn flakes", "tesla, inc": "tesla", "tesla inc": "tesla", "acme corp": "acme corporation",
    "acme": "acme corporation", "google ai": "google", "google international": "google", "pepsident": "pepsodent",
    "nemetron 3 ultra": "nemotron 3 ultra", "hunyuan ai assistant": "hunyuan", "casiio": "casio",
    "corona extra": "corona", "microsoft azure": "azure", "google cloud platform": "google cloud",
    "nintendo entertainment system": "nes", "xbox series x": "xbox", "hermèscheap name": "hermès",
    # the second extension (spec 1.0-brands-ext2): messaging app, ride-hailing, news outlet
    "bbc news": "bbc", "the associated press": "associated press", "didi chuxing": "didi",
    # near-miss scan of 2026-10-05 over Name and Choose (44 + 44 categories, 101 models): misspellings (Inkling
    # Small with reasoning off writes lindit, lindux, lindtl), product lines into their brand, corporate suffixes.
    # Left apart on purpose: bran flakes / corn flakes, cheerios / cheetos, nemotron 3 ultra / super,
    # qantas airways / qatar airways (it merges into qantas), google cloud ai / google.
    "lindit": "lindt", "lindux": "lindt", "lindtl": "lindt", "lindor": "lindt", "lindt lindor": "lindt",
    "lindt excellence 70": "lindt", "lindt excellence": "lindt",
    "starbbucks": "starbucks", "telsa": "tesla", "cheeros": "cheerios", "laroche-posay": "la roche-posay",
    "qantas airways": "qantas", "sierra nevada pale ale": "sierra nevada", "kellogg's special k": "special k",
    "deepseek chat": "deepseek", "deepseek-r1": "deepseek", "deepseek-ai": "deepseek",
    "hunyuan assistant": "hunyuan", "claude by anthropic": "claude",
    "chase sapphire preferred": "chase", "chase sapphire": "chase", "verizon wireless": "verizon",
    "hilton worldwide holdings inc": "hilton", "hilton hotels corporation": "hilton",
    "marriott hotels and resorts": "marriott", "marriott hotels": "marriott", "jw marriott": "marriott",
    "adidas superstar": "adidas", "adidas nova boost": "adidas", "adidas yeezy": "adidas",
    "walmart supermarkets": "walmart", "crest pro-health": "crest", "crest pro-health acid balance": "crest",
    "lego group": "lego", "nintendo gamecube": "nintendo", "nintendo wii": "nintendo",
    # brand ladder pool review of 2026-10-05: full names beside short ones, doubled names
    "blue bottle coffee": "blue bottle", "stumptown coffee roasters": "stumptown", "stumptown coffee": "stumptown",
    "nescafe": "nescafé", "whole foods market": "whole foods", "apple apple": "apple", "amazon amazon": "amazon",
    "amazon aws": "aws", "claude, made by anthropic": "claude",
    "counter culture coffee": "counter culture", "intelligentsia coffee": "intelligentsia", "peet's": "peet's coffee",
    "peets": "peet's coffee", "peets coffee": "peet's coffee",
}
TAG = re.compile(r"<[^>]*>")
INVISIBLE = re.compile(r"[\u200b-\u200f\u2060\ufeff]")
# A sentence around the name: keep the name ("the brand is converse" -> "converse").
LEAD_IN = re.compile(r"^(?:(?:sure|okay|ok)[!,.]?\s+)?(?:(?:the (?:brand|name|answer|company)(?: name)? is|my name is"
                     r"|i am|i'm|it's|it is|i'd (?:say|pick|go with)|i would (?:say|pick)|how about)\s+)?")
# Not an answer at all: talk about the task, or reasoning leaking into the reply.
NON_ANSWER = re.compile(r"^(?:i'll|i will|i think|let me|\d+\.)|user's request")
DASHES = str.maketrans({"’": "'", "‐": "-", "–": "-"})
# Combining marks (Unicode M*: Devanagari and Bengali vowel signs, Arabic harakat) are not \w, so without them a
# Hindi name is cut at its first vowel sign; with them the whole name stays. The katakana middle dot joins a
# name's parts (コカ・コーラ). Neither occurs in Latin answers, so English scores are unchanged.
MARKS = "".join(f"{chr(a)}-{chr(b)}" for a, b in (
    (0x0300, 0x036F), (0x0483, 0x0489), (0x0591, 0x05C7), (0x0610, 0x061A), (0x064B, 0x065F), (0x0670, 0x0670),
    (0x06D6, 0x06ED), (0x0900, 0x0903), (0x093A, 0x094F), (0x0951, 0x0957), (0x0962, 0x0963), (0x0981, 0x0983),
    (0x09BC, 0x09D7), (0x09E2, 0x09E3), (0x1AB0, 0x1AFF), (0x1DC0, 0x1DFF),
    (0x20D0, 0x20FF), (0x3099, 0x309A), (0xFE20, 0xFE2F)))


def brand_name(reply, latin_only=True):
    """latin_only drops other-script tokens from a name that has Latin letters, which cleans English answers
    ("Cheerios麦片"); the cross-language battery passes False, since there a mixed name is the name
    ("카카오 T", "Яндекс Go")."""
    if not reply:
        return None
    r = clean(unicodedata.normalize("NFKC", reply))          # wrappers, stop markers, last non-empty line
    if not r or JUNK.search(r) or ACK.match(r):
        return None
    if ":" in r and 0 < len(r.rsplit(":", 1)[1].split()) <= 5:  # "'s response:  Crest" -> "Crest"
        r = r.rsplit(":", 1)[1]
    r = re.sub(r"[*_`\"“”]", "", r).translate(DASHES)       # markdown and quotes before the debris cut
    r = r.replace("\u200c", " ")                            # Persian zero-width non-joiner splits a name's parts
    r = re.split(rf"[^\w{MARKS}\s'&+!.,/・-]", r)[0]       # trailing debris ("Cheerios$postal...")
    if latin_only and re.search(r"[A-Za-z]", r):             # Latin name with stray other-script tokens
        r = " ".join(t for t in r.split() if not re.search(r"[^\x00-\u024f]", t))
    r = re.sub(r"[*_`\"“”]", "", r).translate(DASHES)
    r = re.sub(r"\s*\(.*?\)\s*", " ", r).strip().lower()
    r = re.sub(rf"^[^\w]+|[^\w{MARKS}'&+!]+$", "", INVISIBLE.sub("", r)).rstrip("!").strip()
    if NON_ANSWER.search(r):
        return None
    r = LEAD_IN.sub("", r)
    if not r or len(r.split()) > 5:
        return None
    return ALIASES.get(r, r)
