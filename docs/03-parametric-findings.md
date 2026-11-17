# 03 · Parametric and mathematical findings

These are the equations, derived identities and computed results for the 12-hole alto C (A4..F6). Every number in this file is produced by `python kernel/alto_c_study.py` from [`params/alto_c_12hole.toml`](../params/alto_c_12hole.toml). The full output is in [`generated/study-output.md`](generated/study-output.md). If a parameter changes, rerun the script and refresh the tables.

All results are **pre-calibration**: η_w = 0.90, k = 0.80, 27 °C. Treat absolute volumes and diameters as starting values. The ratios, sensitivities and design rules transfer.

## 1. Notation and conventions

| Symbol | Meaning | Baseline |
| --- | --- | --- |
| f_j | frequency of fingering j | A4 = 440 Hz, 12-TET |
| c | speed of sound in the played air | 347.3 m/s (27 °C) |
| V0 | **capped** air volume, all holes closed: cavity plus every chimney up to its outer rim | solved |
| V_j | V0 minus the chimneys of the holes open in fingering j | |
| G_w, η_w | window conductance and window efficiency | η_w = 0.90 (calibrate) |
| G_i, A_i, t_i, d_i | hole conductance, area, chimney height (core + shell), diameter | |
| k | combined inner and outer end-correction coefficient | 0.80 (calibrate) |
| W, h | window length (windway exit to labium edge) and windway exit height | 8.9 mm, 1.20 mm |
| p, U, ρ | blowing pressure, jet speed, air density | ρ = 1.176 kg/m³ |

**Convention (amends the build plan):** the window throat, like every open chimney, is **neck**. It belongs to G_w through t_w and is **not** part of V0.

## 2. Governing equations and derived identities

$$f_j=\frac{c}{2\pi}\sqrt{\frac{\eta_w G_w+\sum_{i\in\text{open}_j}G_i}{V_j}},\qquad G=\frac{A}{t+k\,d_{eq}},\quad d_{eq}=2\sqrt{A/\pi},\qquad V_j=V_0-\sum_{i\in\text{open}_j}A_i t_i$$

$$d=\frac{2}{\pi}\left(Gk+\sqrt{G^2k^2+\pi G t}\right)\qquad V_0=\frac{\eta_w G_w c^2}{4\pi^2 f_0^2}$$

**Sizing with chimney volume (fixed point).** For a linear fingering, hole k satisfies

$$G_k=\frac{4\pi^2}{c^2}f_k^2\Big(V_0-\sum_{i<k}A_it_i-A_k t_k\Big)-\eta_wG_w-\sum_{i<k}G_i,\qquad A_k=\frac{\pi d(G_k)^2}{4}$$

Iterate on A_k. The iteration converges in a few steps because A_k t_k ≪ V0. The round trip (size the holes, then predict every fingering back) closes to **4×10⁻⁹ cents** (`kernel/test_kernel.py`).

### Identity 1: range ratio is fixed by the scale, not by the design

Without chimney volume the sizing equations telescope to

$$\frac{\sum G_i}{\eta_w G_w}=\left(\frac{f_{top}}{f_0}\right)^2-1$$

| Instrument | Range | Σ G / η_w G_w |
| --- | --- | --- |
| 10-hole alto C | C5..F6 | **6.13** |
| 12-hole alto C | A4..F6 | **9.08** (8.94 with chimney volume) |
| Single-chamber ceiling (build plan) | — | 9–10 |

A 12-hole alto C sits at the single-chamber ceiling **by arithmetic**, whatever the window or chamber. The two subholes alone add 48 % to the conductance the holes must supply relative to the window. This is the quantitative form of Pure Ocarinas' observation that 12-holes have steep breath curves, weak lows and airy highs, and that only a small voicing covers the full range. It is also why "build the 10-hole first" (safeguard 6) is sound: same window, 0.707× the chamber, two-thirds of the range ratio.

### Identity 2: uniform scaling

Scaling every length by s gives G ∝ s and V ∝ s³, so **f ∝ 1/s**:

- +1 % uniform scale: **−17.2 cents** (a volume-only change gives −8.6 cents per 1 %)
- 12 % clay shrinkage: **+221 cents**, about a whole tone. This matches the F → G shift Francis (UIUC, 2012) saw after drying.
- For prints, resin or FDM shrinkage of 0.3–1 % is 5–17 cents sharp if uncompensated. The calibration volume factor absorbs it.

### Identity 3: step sizes

Hole k supplies ΔG_k ∝ f_k² − f_{k−1}² = f_{k−1}²(r² − 1), with r = 2^(2/12) for a whole step and 2^(1/12) for a semitone. So:

- semitone holes need about 0.47× the conductance of a whole-step hole at the same pitch
- conductance grows as f² up the scale, so the top holes are the large ones
- two equal holes opened in succession give a flatter second interval, as Paley (Bridges 2015) noted

### Identity 4: error fingerprints (what makes calibration identifiable)

$$\Delta\text{cents}_j\approx 865.6\left(\frac{\Delta G_{tot,j}}{G_{tot,j}}-\frac{\Delta V_j}{V_j}\right)$$

| Error source | Shape across the scale (baseline numbers) |
| --- | --- |
| Volume or temperature | **Uniform**: −8.6 cents per +1 % V, +2.9 cents per +1 °C |
| Window (η_w, W, wall) | **Decays with pitch**, with weight η_wG_w / G_tot,j from 1.0 at A4 to 0.10 at F6. +0.1 mm window length gives +5.8 cents on A4 and +0.6 on F6. |
| Hole i (diameter offset, k) | **Steps on** at the fingering where hole i opens, with weight G_i / G_tot,j |

Because the three fingerprints differ in shape, a single recorded scale from the calibration body can separate volume factor, η_w and hole offset/k. Least squares on these shapes is the Phase 2 fitting method.

## 3. Voicing scaling from Heuer's chart

| Size | Key | Exit mm | Window mm (fired) | W/h | f·W (m/s) | p rel. #1 at same St |
| --- | --- | --- | --- | --- | --- | --- |
| #1 C | C6 | 0.76 | 5.08 | 6.7 | 5.32 | 1.00 |
| #2 G/F | ≈F#5 | 1.14 | 7.62 | 6.7 | 5.64 | 1.13 |
| **#3 C (alto)** | **C5** | **1.14** | **9.65** | **8.4** | **5.05** | **0.90** |
| #4 G/F | ≈F#4 | 1.14 | 11.43 | 10.0 | 4.23 | 0.63 |
| #5 C | C4 | 1.52 | 15.24 | 10.0 | 3.99 | 0.56 |
| #6 G/F | ≈F#3 | 1.52 | 20.32 | 13.3 | 3.76 | 0.50 |
| #7 C | C3 | 1.52 | 25.40 | 16.7 | 3.32 | 0.39 |

(The key for the G/F sizes is the geometric mean of G and F. The other columns are exact conversions.)

- **W ∝ f^−0.75** over all seven sizes (R² = 0.992; C sizes alone give −0.76, R² = 0.995). The window grows **1.68× per octave down**, not 2×. Heuer's sizing is therefore not proportional.
- At constant Strouhal this implies a design pressure **p ∝ f^0.51** across sizes. Heuer's bass is voiced for about 40 % of the soprano's pressure, consistent with makers' experience that low ocarinas take more air and less pressure.
- W/h rises with size, from 6.7 to 16.7, because exit height moves in three steps (0.76 / 1.14 / 1.52 mm) while W grows smoothly.

**The alto band read as pressure** (p ∝ W² at a fixed Strouhal number):

| Rating | W fired mm | Wet mm (Heuer ratio 1.126) | p / p_medium | W / W_soft |
| --- | --- | --- | --- | --- |
| X, too small | 8.13 | 9.15 | 0.71 | 0.914 |
| **Soft (start here)** | **8.89** | 10.01 | **0.85** | 1.000 |
| Medium | 9.65 | 10.87 | 1.00 | 1.086 |
| Loud | 10.41 | 11.73 | 1.16 | 1.171 |
| X, too large | 11.18 | 12.59 | 1.34 | 1.257 |

The playable band is ±0.76 mm (±7.9 %) around Medium, wide compared with printer accuracy. The real precision risks are **windway height and the labium edge**. Set h to a whole number of layers. **1.20 mm** divides evenly into 0.1, 0.12, 0.15, 0.2 and 0.3 mm layers and is +5 % over Heuer's 1.14 mm, which keeps W/h = 7.4 inside the plan's 7–10 band.

## 4. Jet, Strouhal and the breath curve

1. Jet speed: **U = sqrt(2p/ρ)**. UNSW gives P ≈ ½ρv², i.e. 1 kPa ≈ 40 m/s.
2. Disturbances ride the jet at **≈ U/2** (UNSW flute acoustics).
3. Best drive when the transit delay W/(U/2) is about half a period. This is the textbook flue-pipe condition (Fletcher & Rossing); it was **not re-checked in this session** because the Fletcher PDFs had no text layer. It gives **St = fW/U ≈ 0.25**, the centre of the build plan's 0.2–0.4 band.
4. Optimum pressure is then **p\* = ½ρ(fW/St)² ∝ f²W²**.
5. A breath curve **p = p₀(f/f₀)^α = p₀·2^(α·n/12)** is exponential in semitones n. This is the "approximately exponential" curve Pure Ocarinas describes. α = 2 keeps St constant (×10.1 pressure over A4..F6). Real curves are flatter, so St drifts up with pitch.

Baseline window W = 8.9 mm, p(A4) = 150 Pa, α = 1.2 (assumed until a manometer measures them):

| Note | Hz | p Pa (α 1.2) | U m/s | St | p Pa for constant St |
| --- | --- | --- | --- | --- | --- |
| A4 | 440.0 | 150 | 16.0 | 0.245 | 150 |
| C5 | 523.3 | 185 | 17.7 | 0.263 | 212 |
| E5 | 659.3 | 244 | 20.4 | 0.288 | 337 |
| G5 | 784.0 | 300 | 22.6 | 0.309 | 476 |
| A5 | 880.0 | 345 | 24.2 | 0.324 | 600 |
| C6 | 1046.5 | 424 | 26.9 | 0.347 | 849 |
| E6 | 1318.5 | 560 | 30.9 | 0.380 | 1347 |
| F6 | 1396.9 | 600 | 31.9 | 0.389 | 1512 |

The α = 1.2 curve stays inside the plan's bands (0.2–0.3 low, 0.3–0.4 high) at 150 → 600 Pa. That internal consistency supports the bands, but **α, p₀ and the St band must be measured** on a good reference (Phase 1).

## 5. Baseline design: 12-hole alto C

**Inputs** (`params/alto_c_12hole.toml`): teardrop window 8.9 × 6.0 mm with tip radius 1.0 mm, giving 37.0 mm² (d_eq 6.86 mm), in a 3.0 mm wall; η_w 0.90; k 0.80; uniform 3.0 mm chimneys (the Phase 3 plain body); 27 °C.

**Outputs:**

- G_w = 4.355 mm; η_wG_w = 3.919 mm
- **V0 = 61.85 cm³** (capped air); chimneys 0.87 cm³; **core chamber 60.98 cm³**
- Σ G_i = 35.03 mm; range ratio **8.94**
- window area / V0^(2/3) = 0.0236, a size-independent voicing-to-chamber ratio to compare against references

| # | Hole | Step | Finger (typical) | G mm | **d mm** | Chimney cm³ | Check |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | sub1 | A4→B4 | subhole 1 (left) | 1.017 | 2.56 | 0.015 | below 3 mm |
| 2 | sub2 | B4→C5 | subhole 2 (right) | 0.604 | 1.86 | 0.008 | below 3 mm |
| 3 | R_pinky | C5→D5 | right pinky | 1.437 | 3.19 | 0.024 | ok |
| 4 | R_ring | D5→E5 | right ring | 1.809 | 3.71 | 0.032 | ok |
| 5 | R_middle | E5→F5 | right middle | 1.073 | 2.64 | 0.016 | below 3 mm |
| 6 | R_index | F5→G5 | right index | 2.553 | 4.68 | 0.052 | ok |
| 7 | L_pinky | G5→A5 | left pinky | 3.208 | 5.50 | 0.071 | ok |
| 8 | L_ring | A5→B5 | left ring | 4.029 | 6.48 | 0.099 | ok |
| 9 | L_middle | B5→C6 | left middle | 2.390 | 4.47 | 0.047 | ok |
| 10 | L_index | C6→D6 | left index | 5.654 | 8.35 | 0.164 | ok |
| 11 | L_thumb | D6→E6 | left thumb | 7.066 | 9.92 | 0.232 | ok (thumb ≤ 12) |
| 12 | R_thumb | E6→F6 | right thumb | 4.190 | 6.67 | 0.105 | ok |

The finger assignment follows the common 12-hole layout (subholes confirmed by Pure Ocarinas: B = right subhole closed, A = both closed). Confirm it against the chart you adopt; the solver itself only needs the opening order.

**Ignoring chimney volume** when sizing leaves the scale sharp by an amount that grows with the number of open holes: +0.3 (C5), +2.1 (G5), +5.2 (C6), +11.0 (E6), **+12.5 cents (F6)**.

The baseline sits close to the sound-hole sizes makers report: Pure Ocarinas gives about 7–9 mm for a 12-hole alto C, and this window is 8.9 mm long. The volume is also close to maker reports: 70–80 cm³ with a 35–40 mm² teardrop in a thinner wall (§10).

## 6. Sweeps

### 6.1 Window efficiency (the largest unknown)

| η_w | V0 cm³ | Smallest d mm | Largest d mm | Holes < 3 mm |
| --- | --- | --- | --- | --- |
| 0.5 | 34.4 | 1.32 | 6.39 | 5 |
| 0.6 | 41.2 | 1.46 | 7.30 | 5 |
| 0.7 | 48.1 | 1.60 | 8.19 | 4 |
| 0.8 | 55.0 | 1.73 | 9.06 | 4 |
| **0.9** | **61.8** | 1.86 | 9.92 | 3 |
| 1.0 | 68.7 | 1.98 | 10.77 | 3 |

V0 and every G_i scale linearly with η_w. An uncalibrated 10 % error in η_w is about **83 cents** on the low notes, which is why the calibration print is not optional.

**Update 2026-11-17** (amendment A11): the realistic band is **0.85–0.95**, from three real instruments (ECAN3 V0N3 0.86, Eclipse 0.89, Miracle about 0.9). The 0.5–0.8 rows rested mainly on the LES study, which turned out to be a weak data point ([01 §5](01-source-review.md#5-second-source-review-2026-11-17-heuer-chart-re-read-les-paper-read-in-full)). The table is kept as the full sweep that `kernel/alto_c_study.py` reproduces. Inside the band, V0 is about 58–65 cm³ for this baseline.

### 6.2 Chimney height and the subhole problem

| Chimney mm | sub1 | sub2 | R_index | L_index | L_thumb | R_thumb | Core cm³ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2.0 | 2.21 | 1.59 | 4.17 | 7.70 | 9.25 | 6.10 | 61.4 |
| **3.0** | 2.56 | 1.86 | 4.68 | 8.35 | 9.92 | 6.67 | 61.0 |
| 4.0 | 2.85 | 2.09 | 5.12 | 8.90 | 10.48 | 7.14 | 60.5 |
| 5.0 | 3.11 | 2.29 | 5.51 | 9.38 | 10.96 | 7.55 | 60.0 |
| 6.0 | 3.35 | 2.47 | 5.86 | 9.80 | 11.37 | 7.89 | 59.4 |

Chimney height adds about 0.3–0.5 mm of diameter per extra millimetre of wall. To bring the small holes to 3.0 mm:

- **sub1** needs a 4.5 mm chimney (6.7 mm for 3.5 mm)
- **R_middle** (F5) needs a 4.2 mm chimney
- **sub2** needs a **9.3 mm** chimney (13.1 mm for 3.5 mm). The practical form is an **inward tubular boss** inside the core, which leaves the exterior unchanged. The boss wall displaces under 0.1 cm³ of cavity, which the volume measurement picks up.

The alternative is to accept 1.9–2.6 mm subholes and validate them on a coupon. Small holes carry more viscous loss and are the most sensitive to print error (§7).

### 6.3 Window length across Heuer's band

Width, tip radius and wall are held fixed; p(A4) = 150 Pa; α = 1.2.

| Rating | W mm | Area mm² | V0 cm³ | St A4 | St F6 | p(A4) for St 0.25, Pa |
| --- | --- | --- | --- | --- | --- | --- |
| X small | 8.13 | 34.2 | 58.7 | 0.224 | 0.355 | 120 |
| **Soft** | **8.89** | 36.9 | 61.8 | 0.245 | 0.389 | 144 |
| Medium | 9.65 | 39.7 | 65.0 | 0.266 | 0.422 | 170 |
| Loud | 10.41 | 42.6 | 68.1 | 0.287 | 0.455 | 198 |
| X large | 11.18 | 45.5 | 71.1 | 0.308 | 0.489 | 228 |

Two consequences:

1. Window variants are **not interchangeable**. Moving from Soft to Medium changes V0 by 5.2 %, which is about 45 cents if the chamber is not re-solved. Each voicing coupon variant gets its own volume target.
2. With a fixed breath curve, the Loud and X-large windows push St on F6 past the 0.4 band edge. This is a numeric version of "a too-large window loses the top of the range".

## 7. Sensitivities and tolerance budget

Cents per **+0.1 mm** of hole diameter (baseline):

| Hole | d mm | On the note it opens | On F6 |
| --- | --- | --- | --- |
| sub1 | 2.56 | **11.2** | 1.4 |
| sub2 | 1.86 | **8.6** | 1.2 |
| R_pinky | 3.19 | 8.7 | 1.6 |
| R_ring | 3.71 | 7.3 | 1.7 |
| R_middle | 2.64 | 5.7 | 1.5 |
| R_index | 4.68 | 5.5 | 1.8 |
| L_pinky | 5.50 | 4.6 | 1.9 |
| L_ring | 6.48 | 3.8 | 1.9 |
| L_middle | 4.47 | 3.1 | 1.8 |
| L_index | 8.35 | 2.8 | 2.0 |
| L_thumb | 9.92 | 2.3 | 2.1 |
| R_thumb | 6.67 | 1.9 | 1.9 |

Other sensitivities: +1 % V0 gives −8.6 to −8.7 cents on every note; +0.1 mm window length gives +5.8 cents on A4 and +0.6 on F6; +1 °C gives +2.9 cents.

The low holes and subholes are the touchy ones, because each is a large fraction of the small total conductance at the bottom of the scale. **Print them 0.2–0.3 mm undersize and ream to pitch**, or make them larger on longer chimneys.

**Monte Carlo, 4000 virtual builds** (rms / 95th-percentile cents):

| Note | Calibrated: σV 0.5 %, σd 0.05 mm, σ(η_wG_w) 1 % | Loose FDM: 1 %, 0.10 mm, 2 % | Uncalibrated η_w: 10 %, plus loose FDM |
| --- | --- | --- | --- |
| A4 | 9.8 / 19.8 | 19.5 / 39.7 | 88 / 178 |
| C5 | 10.2 / 19.9 | 20.4 / 39.7 | 64 / 128 |
| G5 | 8.0 / 15.7 | 16.0 / 31.4 | 32 / 62 |
| C6 | 6.4 / 12.6 | 12.8 / 25.1 | 20 / 40 |
| F6 | 5.5 / 10.6 | 10.9 / 21.1 | 14 / 28 |

**Budget for the build plan's 15-cent goal.** After calibration removes the bias, the print-to-print scatter of volume and window conductance must stay within about **0.9 % combined** (for example 0.5 % volume and 0.7 % window). Hole scatter of 0.05 mm is a minor contributor. If a printer cannot hold that, add a **volume-trim plug** to the core: ±1 cm³ on 62 cm³ is ∓14 cents across the whole scale. Pure Ocarinas notes that plunger-tunable ocarinas already exist.

## 8. Lumped-model validity: chamber shape

At F6, λ = 248.6 mm:

- The plan's rule L_int < λ/3 gives **82.9 mm**.
- The first closed–closed cavity mode c/(2L) reaches 1.3 × F6 at L = 95.6 mm and equals F6 at **124.3 mm**, the hard limit.

For the baseline core volume of 61 cm³, by ellipsoid proportions:

| Chamber L:W:H | L mm | W mm | H mm | c/(2L) ÷ F6 | Inside λ/3 |
| --- | --- | --- | --- | --- | --- |
| sphere | 48.8 | 48.8 | 48.8 | 2.55 | yes |
| egg 1.6:1.3:1 | 61.2 | 49.7 | 38.3 | 2.03 | yes |
| egg 2.2:1.5:1 | 72.2 | 49.2 | 32.8 | 1.72 | yes |
| transverse 3.0:1.6:1 | 86.9 | 46.3 | 29.0 | 1.43 | no |
| transverse 3.6:1.7:1 | 96.1 | 45.4 | 26.7 | 1.29 | no |

c/(2L) is the conservative (lowest) estimate. A tapered ellipsoid's first mode is higher; a sphere's is 1.33× higher. Francis's large ocarina showed one fixed resonance near 1100 Hz in every fingering, which is consistent with a cavity mode intruding.

**Rule:** keep the Phase 3 chamber at or below about 2.2:1.5:1 (L_int ≤ 75 mm). Sculpted chambers may go longer only with a passing Tier 2 FEM check on the top three fingerings, and never beyond c/(2L) = 1.3 × F6 (L_int ≈ 95 mm). Pure Ocarinas' "bypassing" hypothesis (narrow chambers help high notes) points the other way. It is listed as open question Q6, to test after Phase 3.

## 9. Air composition and design temperature

| Air in the chamber | c m/s | Cents vs plan at 27 °C |
| --- | --- | --- |
| plan formula, dry, 27 °C | 347.3 | 0.0 |
| room air 27 °C, 50 % RH | 348.3 | +4.9 |
| room air 27 °C, saturated | 349.3 | +9.8 |
| exhaled breath 30 °C, saturated (4.2 % CO₂) | 347.8 | +2.7 |
| exhaled breath 27 °C, saturated | 345.7 | −7.9 |
| plan formula, dry, 20 °C | 343.2 | −20.4 |

Humidity raises c, and exhaled CO₂ and the lower O₂ lower it. The net effect is within ±10 cents and is absorbed by η_w at calibration, provided the calibration print is played the way the instrument will be. Pure Ocarinas measures about 0.9 cents per °C of **room** temperature, a third of the 2.9 cents/°C theory, because breath sets most of the internal temperature. **Keep 27 °C as the design temperature and record room temperature with every recording.**

## 10. Cross-checks against external data

| Data | Model result | Reading |
| --- | --- | --- |
| LES ocarina (Kobayashi et al. 2009): 9.4 cm³, 5×5 mm window, 880 Hz | Thin-aperture theory 1274 Hz; implied **η_w 0.48** (0 mm wall), 0.63 (1.5 mm), 0.78 (3 mm) | The jet and labium reduce the window's effective conductance. Supports η_w < 1 and calibration first. **Weak (01 §5):** the 880 Hz is the nominal note of a similar commercial ocarina, not a measurement, and the run was 5 ms long. Real instruments give 0.86–0.9. |
| Maker report: 70–80 cm³, 35–40 mm² teardrop | 72–86 cm³ for η_w 0.9–1.0 with a 1.6 mm wall | Consistent with η_w near 0.9 on thin-walled clay. |
| Build-packet workbook: 130 cm³, 9×5 mm, 4 mm wall | 69 cm³ needed at η_w = 1; 130 cm³ gives 320 Hz | Inconsistent; rejected. |
| Plan's own alto table | All four rows reproduce | Verified. |

## 11. Design rules

These are the actionable results. Each one becomes a solver constraint, an add-on check or a phase gate in [02](02-unified-plan.md).

| ID | Rule | Basis |
| --- | --- | --- |
| R1 | A4..F6 needs Σ G / η_wG_w = 9.08. Build the 10-hole (6.13) first, then add the subholes and the 1.41× larger chamber they need (same window). | Identity 1 |
| R2 | Start the window at **8.9 mm** (soft). Coupon-sweep 8.9 / 9.3 / 9.65 mm, and give each variant its own V0. | §3, §6.3 |
| R3 | Windway exit height = a whole number of layers. Default **1.20 mm**. | §3 |
| R4 | The window throat is neck, excluded from V0. Chimneys of open holes are neck; chimneys of closed holes are cavity. | §1 |
| R5 | Always size with the chimney-volume fixed point. Ignoring it costs up to 12.5 cents at F6. | §5 |
| R6 | Hole floor: 3.0 mm for finger holes. Bring subholes to 3.0 mm with inward bosses (sub1 4.5 mm, sub2 9.3 mm chimney), or validate 1.9–2.6 mm subholes on a coupon. | §6.2 |
| R7 | Print sub1, sub2, R_pinky and R_ring 0.2–0.3 mm undersize and ream to pitch. | §7 |
| R8 | Repeatability budget: volume plus window scatter ≤ 0.9 % combined. Otherwise add a volume-trim plug (±1 cm³ ≈ ∓14 cents). | §7 |
| R9 | Chamber shape: L_int ≤ 75 mm (≈ 2.2:1.5:1) for Phase 3. A longer chamber needs Tier 2 FEM, and L_int must never exceed 95 mm at 61 cm³. | §8 |
| R10 | The calibration fit uses the three error fingerprints: uniform (volume), decaying (window), stepped (holes). | Identity 4 |
| R11 | Treat η_w as unknown between 0.5 and 1.0 until measured. Do not sculpt to a volume before Phase 2. **Update 2026-11-17 (A11):** plan with 0.85–0.95; the gate (measure before sculpting) stays. | §6.1, §10 |
| R12 | Breath model p = p₀·2^(α·n/12). Measure p₀ and α, keep St within 0.2–0.3 (low) and 0.3–0.4 (high). | §4 |
| R13 | Use 64-segment cutters, or compensate the radius (32-gon: −0.64 % area). | §2 (build plan) |
| R14 | Design at 27 °C internal air. Log room temperature, which carries about 0.9 cents/°C. | §9 |
