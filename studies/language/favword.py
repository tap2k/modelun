"""
favword.py — the serendipity inquiry. Three English framings of the open prompt,
all in transcripts_pickword, 44 models x 4 runs each, mechanical exact-match:

  scene "en"           "Pick any word."                        -> the census baseline
  scene "en_fav"       "What is your favorite word?"
  scene "en_beautiful" "What is the most beautiful word ...?"

Question: does the serendipity attractor strengthen when the prompt explicitly asks
the question its listicle/poll meme actually answers? (Yes: 42% -> ~70% -> ~70%.)

    ../../.venv/bin/python favword.py
"""
import json, glob
from collections import Counter
import pickword as P  # reuse the census's exact normalizer — same instrument, same rules

def dist(dirn, scene):
    reps = []
    for f in sorted(glob.glob(f"{dirn}/*.json")):
        sc = json.load(open(f)).get("scenes", {}).get(scene)
        if not sc:
            continue
        for run in sc.get("runs", []):
            if run and (w := P.norm(run[-1].get("reply"), "en")):
                reps.append(w)
    return Counter(reps), len(reps)

def show(name, prompt, c, n):
    ser = c.get("serendipity", 0) + c.get("serendipitous", 0)
    print(f"\n=== {name}  ({prompt!r})  n={n} ===")
    print(f"  serendipity(+ous): {ser}/{n} = {ser/n:.0%}")
    for w, k in c.most_common(6):
        print(f"    {k/n:5.0%}  {w}")

if __name__ == "__main__":
    D = "transcripts_pickword"
    show("PICK ANY WORD (baseline)", "Pick any word.", *dist(D, "en"))
    show("FAVORITE WORD", "What is your favorite word?", *dist(D, "en_fav"))
    show("MOST BEAUTIFUL WORD", "What is the most beautiful word in the English language?",
         *dist(D, "en_beautiful"))
