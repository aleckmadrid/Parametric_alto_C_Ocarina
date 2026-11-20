### P4-80, the seed: where the voicing and the mouthpiece lie

| Trial | Port | Foot of the neck | Pipe | Window inside the player-side edge | Window faces, from straight down | Mouthpiece against the level of the body | Mouth end beyond the body's edge | Mouth end against the middle of the body | Neck below the body's lowest point | Checks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `lv-30` | 30° (built 30.9°) | 32 mm | 30 mm | 7.9 mm (16 % of 49 mm) | 25° | 17° above | 24.2 mm | 2.5 mm below | 0.0 mm | passes |
| `lv-20` | 20° (built 19.7°) | 32 mm | 30 mm | 11.9 mm (24 % of 49 mm) | 15° | 7° above | 21.8 mm | 10.2 mm below | 0.0 mm | **fails `hole_to_voicing`** |
| `lv-20f` | 20° (built 19.7°) | 29 mm | 30 mm | 11.9 mm (24 % of 49 mm) | 15° | 7° above | 21.8 mm | 10.2 mm below | 0.0 mm | passes |
| `lv-20fw` | 20° (built 19.7°) | 29 mm | 45 mm | 11.9 mm (24 % of 49 mm) | 15° | 7° above | 36.7 mm | 8.3 mm below | 0.0 mm | passes |
| `lv-15f` | 15° (built 14.1°) | 29 mm | 30 mm | 14.1 mm (29 % of 49 mm) | 11° | 3° above | 20.1 mm | 13.7 mm below | 0.0 mm | passes |
| `lv-10` | 10° (built 11.2°) | 32 mm | 30 mm | 15.2 mm (31 % of 49 mm) | 9° | 1° above | 19.2 mm | 15.4 mm below | 0.0 mm | **fails `hole_to_voicing`** |
| `lv-10f` | 10° (built 11.2°) | 29 mm | 30 mm | 15.2 mm (31 % of 49 mm) | 9° | 1° above | 19.2 mm | 15.4 mm below | 0.0 mm | passes |
| `lv-10fw` | 10° (built 11.2°) | 29 mm | 45 mm | 15.2 mm (31 % of 49 mm) | 9° | 1° above | 34.2 mm | 15.2 mm below | 0.0 mm | passes |
| `lv-10fd` | 10° (built 11.2°) | 29 mm | 30 mm | 15.2 mm (31 % of 49 mm) | 9° | 1° above | 19.2 mm | 15.4 mm below | 0.0 mm | passes |
| `lv-10fn` | 10° (built 11.2°) | 29 mm | 30 mm | 15.2 mm (31 % of 49 mm) | 9° | 1° above | 19.2 mm | 15.4 mm below | 0.0 mm | passes |
| `lv-10fwdn` | 10° (built 11.2°) | 29 mm | 45 mm | 15.2 mm (31 % of 49 mm) | 9° | 1° above | 34.2 mm | 15.2 mm below | 0.0 mm | passes |
| `lv-10fwdnr` | 10° (built 11.2°) | 29 mm | 45 mm | 15.2 mm (31 % of 49 mm) | 9° | 1° above | 34.2 mm | 15.2 mm below | 0.0 mm | passes |
| `lv-5f` | 5° (built 5.6°) | 29 mm | 30 mm | 17.4 mm (35 % of 49 mm) | 4° | 4° below | 17.1 mm | 18.6 mm below | 2.6 mm | passes |
| `lv-5fw` | 5° (built 5.6°) | 29 mm | 45 mm | 17.4 mm (35 % of 49 mm) | 4° | 4° below | 32.0 mm | 19.6 mm below | 3.5 mm | passes |
| `lv-0` | 0° (built 0.0°) | 32 mm | 30 mm | 19.7 mm (40 % of 49 mm) | 0° | 8° below | 14.7 mm | 21.6 mm below | 5.6 mm | **fails `hole_to_voicing`** |
| `lv-0f` | 0° (built 0.0°) | 29 mm | 30 mm | 19.7 mm (40 % of 49 mm) | 0° | 8° below | 14.7 mm | 21.6 mm below | 5.6 mm | passes |

### P4-80, the seed: what the checks and the theory read

| Trial | L thumb hole edge to the window / to the neck's box | R thumb hole edge to the window / to the neck's box | Free air below the window (the check's number) | Upright wall under the exit | Chamber wall along the jet, radius | Pocket | First cavity mode ÷ F6 | Steepest plastic seen from the window rim | Thinnest plastic | Plastic | Capped air | Voicing hash |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `lv-30` | 15.9 / 1.7 mm | 24.6 / 10.1 mm | 29.4 mm | 2.57 mm | 22.6 mm | 0.181 cm³ | 1.361 | 11° (5.6 mm high) | 1.19 mm | 55.0 cm³ | 79.91 cm³ | `312011ec9f0e` |
| `lv-20` | 13.8 / 0.3 mm | 22.6 / 8.5 mm | 29.8 mm | 2.20 mm | 25.1 mm | 0.154 cm³ | 1.361 | 11° (5.6 mm high) | 1.21 mm | 54.6 cm³ | 79.80 cm³ | `312011ec9f0e` |
| `lv-20f` | 13.8 / 1.8 mm | 22.6 / 9.9 mm | 29.8 mm | 2.20 mm | 25.1 mm | 0.154 cm³ | 1.361 | 11° (5.6 mm high) | 1.27 mm | 54.4 cm³ | 79.80 cm³ | `312011ec9f0e` |
| `lv-20fw` | 13.8 / 1.8 mm | 22.6 / 9.9 mm | 29.8 mm | 2.20 mm | 25.1 mm | 0.154 cm³ | 1.361 | 10° (7.0 mm high) | 1.23 mm | 57.8 cm³ | 79.80 cm³ | `40688a48d1c7` |
| `lv-15f` | 13.0 / 1.8 mm | 21.7 / 9.4 mm | 30.1 mm | 2.07 mm | 26.0 mm | 0.145 cm³ | 1.361 | 11° (5.6 mm high) | 1.19 mm | 54.3 cm³ | 79.77 cm³ | `312011ec9f0e` |
| `lv-10` | 12.7 / 0.3 mm | 21.4 / 7.8 mm | 30.2 mm | 2.02 mm | 26.4 mm | 0.141 cm³ | 1.361 | 11° (5.6 mm high) | 1.24 mm | 54.4 cm³ | 79.76 cm³ | `312011ec9f0e` |
| `lv-10f` | 12.7 / 1.8 mm | 21.4 / 9.3 mm | 30.2 mm | 2.02 mm | 26.4 mm | 0.141 cm³ | 1.361 | 11° (5.6 mm high) | 1.24 mm | 54.2 cm³ | 79.76 cm³ | `312011ec9f0e` |
| `lv-10fw` | 12.7 / 1.8 mm | 21.4 / 9.3 mm | 30.2 mm | 2.02 mm | 26.4 mm | 0.141 cm³ | 1.361 | 10° (7.0 mm high) | 1.19 mm | 57.5 cm³ | 79.76 cm³ | `40688a48d1c7` |
| `lv-10fd` | 12.7 / 1.8 mm | 21.4 / 9.3 mm | 30.2 mm | 2.02 mm | 26.4 mm | 0.141 cm³ | 1.361 | 11° (5.6 mm high) | 1.24 mm | 54.1 cm³ | 79.76 cm³ | `516c4a7d665a` |
| `lv-10fn` | 12.7 / 1.8 mm | 21.4 / 9.3 mm | 30.2 mm | 2.02 mm | 26.4 mm | 0.141 cm³ | 1.361 | 11° (5.6 mm high) | 1.19 mm | 54.6 cm³ | 79.76 cm³ | `312011ec9f0e` |
| `lv-10fwdn` | 12.7 / 1.8 mm | 21.4 / 9.3 mm | 30.2 mm | 2.02 mm | 26.4 mm | 0.141 cm³ | 1.361 | 10° (7.0 mm high) | 1.20 mm | 58.3 cm³ | 79.76 cm³ | `13e7f53d5150` |
| `lv-10fwdnr` | 12.7 / 1.8 mm | 21.4 / 9.3 mm | 30.2 mm | 2.02 mm | 26.4 mm | 0.141 cm³ | 1.361 | 10° (7.0 mm high) | 1.24 mm | 60.0 cm³ | 79.76 cm³ | `13e7f53d5150` |
| `lv-5f` | 12.2 / 1.8 mm | 20.7 / 9.2 mm | 30.5 mm | 1.94 mm | 26.8 mm | 0.136 cm³ | 1.361 | 11° (5.6 mm high) | 1.26 mm | 54.1 cm³ | 79.75 cm³ | `312011ec9f0e` |
| `lv-5fw` | 12.2 / 1.8 mm | 20.7 / 9.2 mm | 30.5 mm | 1.94 mm | 26.8 mm | 0.136 cm³ | 1.361 | 10° (7.0 mm high) | 1.26 mm | 57.3 cm³ | 79.75 cm³ | `40688a48d1c7` |
| `lv-0` | 12.0 / 0.3 mm | 20.1 / 7.7 mm | 30.9 mm | 1.88 mm | 27.0 mm | 0.132 cm³ | 1.361 | 11° (5.6 mm high) | 1.23 mm | 54.2 cm³ | 79.77 cm³ | `312011ec9f0e` |
| `lv-0f` | 12.0 / 1.8 mm | 20.1 / 9.2 mm | 30.9 mm | 1.88 mm | 27.0 mm | 0.132 cm³ | 1.361 | 11° (5.6 mm high) | 1.29 mm | 54.0 cm³ | 79.77 cm³ | `312011ec9f0e` |

Warnings, the same on every trial of this body: `ergo_finger_pitch`, `ergo_hole_lean_side`.

- `lv-20` fails `hole_to_voicing`: nearest hole edge to the window: L_thumb, 13.8 mm (at least 10 mm); holes that touch the voicing block or the labium ramp: L_thumb
- `lv-10` fails `hole_to_voicing`: nearest hole edge to the window: L_thumb, 12.7 mm (at least 10 mm); holes that touch the voicing block or the labium ramp: L_thumb
- `lv-0` fails `hole_to_voicing`: nearest hole edge to the window: L_thumb, 12.0 mm (at least 10 mm); holes that touch the voicing block or the labium ramp: L_thumb

### P1-80, the teardrop: where the voicing and the mouthpiece lie

| Trial | Port | Foot of the neck | Pipe | Window inside the player-side edge | Window faces, from straight down | Mouthpiece against the level of the body | Mouth end beyond the body's edge | Mouth end against the middle of the body | Neck below the body's lowest point | Checks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `lv-30` | 30° (built 30.9°) | 42 mm | 30 mm | 9.8 mm (17 % of 57 mm) | 23° | 15° above | 22.7 mm | 4.9 mm below | 0.0 mm | passes |
| `lv-20` | 20° (built 19.7°) | 42 mm | 30 mm | 14.5 mm (26 % of 57 mm) | 14° | 6° above | 19.4 mm | 12.3 mm below | 0.0 mm | **fails `hole_to_voicing`** |
| `lv-20f` | 20° (built 19.7°) | 34 mm | 30 mm | 14.5 mm (26 % of 57 mm) | 14° | 6° above | 19.4 mm | 12.3 mm below | 0.0 mm | passes |
| `lv-10` | 10° (built 11.2°) | 42 mm | 30 mm | 18.2 mm (32 % of 57 mm) | 8° | 0° above | 16.1 mm | 17.2 mm below | 0.0 mm | **fails `hole_to_voicing`** |
| `lv-10f` | 10° (built 11.2°) | 34 mm | 30 mm | 18.2 mm (32 % of 57 mm) | 8° | 0° above | 16.1 mm | 17.2 mm below | 0.0 mm | passes |
| `lv-10fwdn` | 10° (built 11.2°) | 34 mm | 45 mm | 18.2 mm (32 % of 57 mm) | 8° | 0° above | 31.1 mm | 17.2 mm below | 0.0 mm | passes |
| `lv-10fwdnr` | 10° (built 11.2°) | 34 mm | 45 mm | 18.2 mm (32 % of 57 mm) | 8° | 0° above | 31.1 mm | 17.2 mm below | 0.0 mm | passes |
| `lv-0` | 0° (built 0.0°) | 42 mm | 30 mm | 23.5 mm (41 % of 57 mm) | 0° | 8° below | 11.0 mm | 23.0 mm below | 5.6 mm | **fails `hole_to_voicing`** |
| `lv-0f` | 0° (built 0.0°) | 34 mm | 30 mm | 23.5 mm (41 % of 57 mm) | 0° | 8° below | 11.0 mm | 23.0 mm below | 5.6 mm | passes |

### P1-80, the teardrop: what the checks and the theory read

| Trial | L thumb hole edge to the window / to the neck's box | R thumb hole edge to the window / to the neck's box | Free air below the window (the check's number) | Upright wall under the exit | Chamber wall along the jet, radius | Pocket | First cavity mode ÷ F6 | Steepest plastic seen from the window rim | Thinnest plastic | Plastic | Capped air | Voicing hash |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `lv-30` | 20.6 / 1.4 mm | 22.5 / 4.9 mm | 31.7 mm | 2.06 mm | 27.9 mm | 0.196 cm³ | 1.632 | 11° (5.6 mm high) | 1.24 mm | 51.8 cm³ | 80.01 cm³ | `312011ec9f0e` |
| `lv-20` | 18.6 / -0.4 mm | 19.8 / 1.3 mm | 32.3 mm | 1.72 mm | 31.8 mm | 0.163 cm³ | 1.632 | 11° (5.6 mm high) | 1.24 mm | 51.2 cm³ | 79.99 cm³ | `312011ec9f0e` |
| `lv-20f` | 18.6 / 3.8 mm | 19.8 / 4.5 mm | 32.3 mm | 1.72 mm | 31.8 mm | 0.163 cm³ | 1.632 | 11° (5.6 mm high) | 1.39 mm | 50.6 cm³ | 79.99 cm³ | `312011ec9f0e` |
| `lv-10` | 17.6 / -0.4 mm | 18.1 / -0.8 mm | 32.9 mm | 1.56 mm | 33.7 mm | 0.148 cm³ | 1.631 | 11° (5.6 mm high) | 1.25 mm | 50.8 cm³ | 79.96 cm³ | `312011ec9f0e` |
| `lv-10f` | 17.6 / 3.8 mm | 18.1 / 3.1 mm | 32.9 mm | 1.56 mm | 33.7 mm | 0.148 cm³ | 1.631 | 11° (5.6 mm high) | 1.25 mm | 50.3 cm³ | 79.96 cm³ | `312011ec9f0e` |
| `lv-10fwdn` | 17.6 / 3.8 mm | 18.1 / 3.1 mm | 32.9 mm | 1.56 mm | 33.7 mm | 0.148 cm³ | 1.631 | 10° (7.0 mm high) | 1.23 mm | 54.5 cm³ | 79.96 cm³ | `13e7f53d5150` |
| `lv-10fwdnr` | 17.6 / 3.8 mm | 18.1 / 3.1 mm | 32.9 mm | 1.56 mm | 33.7 mm | 0.148 cm³ | 1.631 | 10° (7.0 mm high) | 1.22 mm | 56.2 cm³ | 79.96 cm³ | `13e7f53d5150` |
| `lv-0` | 17.0 / -0.4 mm | 16.5 / -1.3 mm | 33.7 mm | 1.45 mm | 34.7 mm | 0.138 cm³ | 1.632 | 11° (5.6 mm high) | 1.26 mm | 50.5 cm³ | 79.93 cm³ | `312011ec9f0e` |
| `lv-0f` | 17.0 / 3.8 mm | 16.5 / 2.8 mm | 33.7 mm | 1.45 mm | 34.7 mm | 0.138 cm³ | 1.632 | 11° (5.6 mm high) | 1.21 mm | 50.1 cm³ | 79.93 cm³ | `312011ec9f0e` |

Warnings, the same on every trial of this body: `ergo_hand_span`, `ergo_rest_space`, `ergo_hole_lean_end`, `ergo_hole_lean_side`.

- `lv-20` fails `hole_to_voicing`: nearest hole edge to the window: L_thumb, 18.6 mm (at least 10 mm); holes that touch the voicing block or the labium ramp: L_thumb
- `lv-10` fails `hole_to_voicing`: nearest hole edge to the window: L_thumb, 17.6 mm (at least 10 mm); holes that touch the voicing block or the labium ramp: L_thumb, R_thumb
- `lv-0` fails `hole_to_voicing`: nearest hole edge to the window: R_thumb, 16.5 mm (at least 10 mm); holes that touch the voicing block or the labium ramp: L_thumb, R_thumb

