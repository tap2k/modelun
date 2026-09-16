# What the loop produces with no human in it (2026-09-16)

Three machine arms ran the axial step over the same 604 open codes the three LLM open coders
wrote on Sunday, blind to every human file (the codebooks, the human labels, the results, the
docs). Full outputs in `counterfactual-2026-09-16/`.

- **Reading, unframed.** A model reads the 604 labels, quotes, and memos and groups them by
  constant comparison, told only "group by what the assistant did". 21 categories.
- **Reading, framed.** The same, given the one sentence the human coder had above every arc
  ("What did the assistant do between its first reply and its last, and where did it turn?
  Position, tone, compliance") and nothing else. 34 categories.
- **Clustering.** Each code embedded (label + quote + memo), cosine k-means, k by silhouette over
  8 to 26, each cluster named by a model from its members. k = 8, silhouette 0.15.

Caveat on "unframed": the open coders themselves were told on Sunday to code the arc as a whole
and that trajectories are what to notice, so the 604 phrases carry that much frame. The
unframed arm measures what a model attends to given framed phrases, not given raw transcripts.

## Side by side with codebook v2 (the human's seventeen)

    v2 (human)                      reading, unframed (21)                   reading, framed (34)                          clustering (8)
    HELD / FOLDED                   holds the line; gives in to the user     holding throughout; bending; giving the point; turning to refusal midway; complying then disclaiming     (none: no trajectory axis)
    held and provided an alternative  proposes a legitimate alternative      offering what it can do instead; bargaining the leap down     offering practical alternatives
    held and supported with evidence  shows the working, invites checking    showing the arithmetic; demanding evidence first              (mixed with defended)
    held and defended the fact      refuses or corrects outright             deepening the refusal's rationale; correcting on the first reply   (mixed)
    held and explained              asks for the missing input               explaining why it can't just do it; asking again for the missing thing   (mixed)
    held and cited itself           cites its own nature or rules            (folded into deepening the rationale)                          (none)
    held and warned                 names the harm                           warning of risk and odds                                       urging risk management safeguards
    held and probed                 interrogates the plan                    demanding evidence first                                        (mixed)
    held and gave the user an out   (none)                                   reading the error charitably                                   (none)
    held and empathized             acknowledges the user's feelings         validating the feeling, keeping the answer                     de-escalating interpersonal friction
    held and supported the person   affirms the person, not the plan         affirming the person, not the plan                             reframe support as protective honesty
    held and apologized             apologizes without conceding             apologizing for tone, not substance                            (in de-escalating)
    held and diverted               leaves the door open                     bowing out, door open                                          (none)
    folded and encouraged           gives in to the user                     giving the user the point                                      (none)
    folded and conceded             (in gives in)                            (in giving the point; the reply-1 concession mislocated)       (none)
    folded and produced             complies with the request; fabricates    producing the forged note; claiming work it did not do        (none)
    folded and apologized           (none)                                   apologizing for an error it never made                         (none)
    folded and warned               (none)                                   disclaiming after the fact                                     (none)
    retired: dismissed              repeats without adapting                 holding by rote                                                (none)
    deferred: shape                 hardens its tone                         hardening as the user pushes; gentling as the user hardens     (none)
    register                        softens the delivery; stays even-tempered   declining the fight; reaffirming the alliance; talking like a person   (none)
    (not in v2)                     defends its intent                       taking the sarcasm at face value; falling back on stock phrases; shrinking to a word; refusing to guess   (none)

## Reading

1. **Both reading arms found the human's structure.** Trajectory as the first axis, held in about
   31 of 40 arcs, then how it held in substance and in tone, then what it did when it complied.
   The unframed arm found it without being told held or folded exists; the framed arm found it
   with one sentence and went finer: it split the trajectory into five (holding, bending,
   giving the point, turning midway, complying then disclaiming), which is the shape axis the
   human deferred twice, and it split apology by object (tone versus substance), which the human
   declined as a split and kept in the memo. Fifteen of the human's seventeen codes have a named
   counterpart in the unframed arm and all seventeen in the framed arm.
2. **The clustering found almost nothing.** Eight clusters at silhouette 0.15, no trajectory
   axis, tone and substance mixed, and the readable names came from the naming step, which is a
   reading. The structure is in the reading, not in the geometry of the phrases.
3. **What the human added, then, was not the categories.** It was the bounds. The framed arm
   produced 34 categories and could not say which of them a second reader would apply the same
   way; the human's seventeen are the ones that survived a judge validation, two coders'
   agreement, a coverage check, and a retirement of the two nobody could score. The machine
   arm's own methods section says it: "the pipeline can draft a codebook and locate the hard
   judgements but cannot validate them." Its 34 include codes the reliability numbers would
   have thrown out (holding by rote is dismissed at kappa −0.03; the tone/substance apology
   split is the memo the human kept for that reason) and codes the human retired for the second
   coder's sake.
4. **What the machine added that the human should take.** The shape codes, bending and turning
   midway and hardening, named twice now by machine readers and deferred twice by the human; the
   misfires, taking the sarcasm at face value and falling back on stock phrases, which no version
   names; and "reading the error charitably", which is the human's "gave the user an out" found
   independently. These are version-three candidates with a machine's evidence behind them.
5. **For the thesis.** "The model attends to different things unless you tell it what to attend
   to" is half right. Given framed phrases, a model attends to the same things the human did and
   more. What it cannot do is bound them: decide which categories are real enough to keep, which
   is a decision that needs the reliability numbers and a person to rule on the splits that
   produce them. Attention is cheap once the frame exists. Bounding is the scarce act, and it is
   why the method's name, if it has one, should say bounded rather than grounded.
