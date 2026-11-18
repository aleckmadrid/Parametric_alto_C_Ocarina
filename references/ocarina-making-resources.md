# Ocarina-making resources (ergonomics, chamber shape, limits of the model)

Collected on 2026-11-15 for the hole-layout and chamber-shape review (see [docs/05-ergonomics.md](../docs/05-ergonomics.md)). Summaries are in our words. Short quotes are marked.

## The Art of Ocarina Making (book) and Pure Ocarinas (maker site)

- **Book:** [ocarinamaking.com](https://ocarinamaking.com/). An e-book (PDF, over 300 photos and diagrams, last updated 2019). The site credits **Robert Hickman** as the author and says it is run as part of Pure Ocarinas (a UK maker). Its listed chapters include "Designing ocarinas with good ergonomics", windway, labium and sound hole, playing the whole range, breath curves, tuning 10/11/12-hole ocarinas, weak high notes on 12-hole ocarinas, and a debugging section. The chapters are paid content and were not read.
- **Free page of the book site:** [Why make ocarinas?](https://ocarinamaking.com/page/why_make_ocarinas). It says that hole placement and weight distribution matter a lot for playability. It says intonation does not depend on where the holes are, unlike most wind instruments. It also says an instrument that suits one player can hurt another, which is a reason to make instruments for your own hands.
- **Pure Ocarinas articles** (same author). These are the most concrete free sources on transverse ocarina ergonomics:
  - [The ergonomics of transverse ocarinas](https://pureocarinas.com/ocarina-ergonomics): aim for straight wrists and gently curved fingers. Holes far enough apart that fingers do not touch. Flat areas around the holes so the fingers do not slide off a curved surface. A slightly angled mouthpiece leaves room between the right hand and the face; mouthpieces range from 90° to the body to fully inline. Balance has top priority: the main balance line runs from the right thumb hole to the tail. A right thumb hole too far toward the tail makes the instrument feel heavy; too far toward the mouthpiece and it falls away from the pinky. Sculptural designs often place holes for looks, not for the player.
  - [How to hold an ocarina](https://pureocarinas.com/ocarina-tutorial/how-to-hold-an-ocarina): the hands come from opposite directions. The **right palm faces away from the player** (fingers reach over from the player side). The **left palm faces the player** (fingers reach over from the far side), "rotated 180 degrees". The right-hand fingers lie roughly parallel along a gradual curve. Most people angle the right hand slightly to the left. A subhole is closed by straightening the finger and sliding the tip forward, along the line between the two holes. Fingers may overhang holes, but must not cover a subhole by accident.
  - [Holding an ocarina on the high notes](https://pureocarinas.com/ocarina-tutorial/play-hold-ocarina-high-notes): on high notes the right thumb carries the weight. The right pinky rests on the tail beside its hole from about G up, which supports up to high D. Above that the left index rests on the "cappello" (the bump near the mouthpiece), with the right thumb and pinky.
  - [Why do I get hand pain from playing the ocarina?](https://pureocarinas.com/ocarina-hand-pain): finger holes placed opposite the thumb hole keep the author's wrist neutral, which may not hold for other people. Poor hole alignment forces the wrist to fold.
  - [Identifying playable ocarinas](https://pureocarinas.com/identifying-playable-ocarinas): leave room past the outermost holes for the fingers to rest. Holes butted against the ends, and very rounded bodies, are signs of a poor design. Sound hole about 7–9 mm for a 12-hole alto C.
  - [The ocarina's fingering system](https://pureocarinas.com/ocarina-fingering-system): 12-hole layouts add two subholes. In the Taiwanese layout they sit next to the middle-finger holes; in the Japanese layout, next to the right index and middle holes. In the second octave the left thumb opens first (D), then the right thumb (E).
  - [Why are subholes considered limiting?](https://pureocarinas.com/forum/thread/14): subholes fix the angle of the hand, which does not suit everyone. A finger cannot overhang its hole if the overhang would cover a subhole. A subhole also changes the size every other hole needs.

No free source gives hole spacing in millimetres, an arc radius or a hand angle in degrees. Those numbers come from measuring instruments: the Miracle ([Analizes_ocarinas/Miracle_M](../Analizes_ocarinas/Miracle_M/Miracle_M.md)) and the shared photos ([Analizes_ocarinas/Ergonomic_reference_12hole](../Analizes_ocarinas/Ergonomic_reference_12hole/Ergonomic_reference_12hole.md)).

## Maker comment on the limits of the Helmholtz model

A comment by **Mike Jones** in a Facebook ocarina-making group, shared by the owner on 2026-11-15. The owner described the commenter as the author of the book above; the book's site credits Robert Hickman, so the attribution is to be confirmed. His points, summarised:

1. Nobody has made a useful model that gives hole sizes directly. The Helmholtz equation gets "in the ballpark" only.
2. It ignores the pitch change caused by blowing pressure, and several other non-linear effects he has measured.
3. Holes cannot be sized one at a time: air leaving through the open holes changes the size the other holes need.
4. The shape of the chamber, and how far a hole is from the voicing, both affect the pitch.
5. The chamber shape affects the pitch reached, the hole sizes, the timbre and how the instrument feels to play.
6. In his experience an ocarina cannot be reduced to a simple formula without simulating the whole instrument with computational fluid dynamics.

How this project already meets each point, and where it does not:

| Point | In the project | Gap |
| --- | --- | --- |
| 1. Ballpark only | The kernel is the first guess. Stages 2 and 3 print, measure and fit (`kernel/fitter.py`), then size again from the fitted constants. | None in the plan; nothing is measured yet. |
| 2. Blowing pressure | Each note's pressure is recorded and a breath curve (p0, alpha) is fitted. | The pitch is not corrected for pressure (decision in C2). Tuning holds only along the recorded breath curve. |
| 3. Holes interact | The kernel sizes all holes together: each note sees the sum of the open holes. The fitter sizes holes from note pairs. | The interaction is assumed linear (conductances add). What is left over goes into the per-hole position factor ψ. |
| 4. Shape and distance from the voicing | ψ per hole name and per body shape, fitted from the prints. | ψ belongs to one hole layout. **If the layout changes, the fitted ψ of that shape no longer applies.** Fix the layout before Stage 2 is printed. |
| 5. Shape affects pitch, timbre, feel | Stage 2 prints P0–P3 to test shape. | Timbre and feel are not measured. |
| 6. CFD | An air mesh is exported for acoustic FEM (`*_air_fem.stl`). | No fluid simulation of the jet. The project relies on measurement instead. |
