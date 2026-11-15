# Ergonomic reference: shared photos of a well-rated 12-hole alto C

Five pictures the owner shared on 2026-11-15 of a 12-hole alto C design that online discussion rates well for ergonomics and tuning. They are screenshots from videos and product photos, not our own photographs. They have no scale. They are a reference, not an absolute.

| File | What it shows | Used for |
| --- | --- | --- |
| [01_hand_hold_side.png](images/01_hand_hold_side.png) | Blue glossy body seen from the back, held in two hands | Window at the root of the mouthpiece on the thumb side; two thumb holes |
| [02_hand_hold_top_face.png](images/02_hand_hold_top_face.png) | Same body, top face, roughly the player's view (mouthpiece toward the camera) | Rough check of the hole layout (perspective, motion blur) |
| [03_held_top_face_mouthpiece_up.png](images/03_held_top_face_mouthpiece_up.png) | Same body, top face, mouthpiece up | Rough check of the hole layout (mild perspective) |
| [04_top_face_yellow_orthographic.png](images/04_top_face_yellow_orthographic.png) | Matte yellow body of the same design, top face, mouthpiece up, near-orthographic | **Main measurement** |
| [05_top_face_blue_orthographic.png](images/05_top_face_blue_orthographic.png) | Glossy blue body, same view as 04 | Visual check only (reflections spoil the measurement) |
| [10_annotated_yellow.png](images/10_annotated_yellow.png) | Generated: photo 04 with hole names | — |

Script: [measure_reference.py](measure_reference.py). Output: [measure_output.md](measure_output.md). The script also measures the Miracle (from its table) and the add-on bodies P0–P3 at 80 cm³ in the same frame, so the numbers are comparable.

## How the holes were named

A mouthpiece-up photo is the top face turned 180° from the player's view: the player's side is the mouthpiece side, and the bulb (left hand) is at the image right. In the player's view the bulb is on the left, the tail on the right, and the window sits under the mouthpiece on the thumb side, as on the Miracle.

Each hand has four finger holes and one subhole. The two index holes sit almost on one line across the body (within 6 mm along it), so x order alone cannot tell them apart. They are named so that each hand's four holes form a smooth arc. Every photo then shows the same pattern as the Miracle: **the left index hole is near the far edge and the right index hole is near the player**, about 30 mm apart across the body.

## What the photos share with the Miracle

Numbers are in mm, with each photo scaled so that its pinky-to-pinky span equals the Miracle's (104.2 mm). Photo 04's body would then be 143 mm long; its true size is unknown.

| Feature | Miracle (measured) | Photo 04 | Photo 03 | Photo 02 (rough) |
| --- | --- | --- | --- | --- |
| Finger pitch, left hand (pinky → index) | 17.1–17.7 | 19.6–20.5 | 16.0–19.6 | 17.4–18.9 |
| Finger pitch, right hand | 17.1–18.6 | 15.9–18.8 | 14.6–17.6 | 14.2–18.4 |
| Tilt of the pinky → index line (L / R) | 16.5° / −15.9° | 4.1° / −15.5° | 22.9° / −21.5° | 4.7° / −9.8° |
| Arch: ring and middle off that line, toward the fingertips (L / R) | 3.7, 4.7 / 4.4, 5.7 | 2.8, 3.0 / 3.0, 3.8 | 4.6, 3.2 / 2.9, 2.5 | 2.5, 3.8 / 2.5, 1.4 |
| Index holes: across / along the body | 23.5 / 5.2 | 29.4 / −5.8 | 31.2 / 9.6 | 30.5 / 2.1 |
| Left subhole: parent, offset along the finger | L index, +15.2 | L ring, +11.3 | L ring, +9.0 | L ring, +10.0 |
| Right subhole: parent, offset along the finger | R middle, +6.4 | R middle, +8.1 | R middle, +8.7 | R middle, +8.5 |
| Pinky hole to body end, bulb / tail | 13.0 / 32.8 | 15.4 / 23.5 | – | – |

What this says:

1. **Each hand's holes follow the fingertip arc.** The ring and middle holes stand 1.4 to 5.7 mm off the line from pinky to index, always on the side the fingertips point to. The fingertips point toward the player for the left hand and toward the far side for the right hand. This is the "arch of the fingers" in numbers.
2. **Neighbouring finger holes sit 14 to 20 mm apart**, centre to centre. Each hand spans about 48 to 60 mm from pinky to index.
3. **The two hand lines tilt** 4° to 23° against the body. The two index holes meet in the middle of the body, staggered across it by 23 to 31 mm.
4. **Each subhole lies in the direction its finger points, 7 to 15 mm from its parent hole.** The finger reaches it by straightening and sliding forward, which matches the Pure Ocarinas description. On the photos the left subhole belongs to the left ring finger; on the Miracle, to the left index. The right subhole belongs to the right middle finger on all of them.
5. **There is room past the outer holes:** at least 13 mm at the bulb and more than 20 mm at the tail. The pinkies rest there on high notes.
6. **The holes sit in a band 10 to 16 mm from the far edge** (all except the right index), on a body about 42 to 49 mm wide at the holes (photo 04, scaled). The body is flat enough there that the holes face up.

## Limits

- No scale: lengths are relative to the pinky span. The photos give shape and proportion, not size.
- Photos 02 and 03 have perspective, and 02 is blurred. Their tilt angles are least reliable.
- The thumb holes are only seen at an angle (photo 01): one sits near the bulb end below the window, the other under the right hand. This matches the Miracle (left thumb under the left pinky/ring region, right thumb under the right index/middle). Not measured.
- Hole diameters are not used. The visible opening includes the rim bevel and depends on lighting.
