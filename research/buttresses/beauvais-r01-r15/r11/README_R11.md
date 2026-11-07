# F5ZP R11 — Source-guided Beauvais Flying Arch (EXPERIMENTAL / FOR REVIEW)

Source: Viollet-le-Duc Volume I, figure 61; Wikimedia 630x1021 original, recorded SHA-256.
The 315x550 Project Gutenberg edition is preserved separately and is NOT the source used in R11 QA.
R08–R10, existing cathedral geometry and all approved generators remain unchanged.

## Distinct geometry
The uppermost boundary is a sloping stone coping/roof line, not necessarily a circular extrados.
The lower flying arch has ornament above the inclined outer edge, not part of the arch curvature.
Individual high and low flying-arch spans are interrupted by an intermediate receiving pier.
Only visible core spans are drawn black; adjoining terminal guesses are red dashed.

## Quantitative observations in IMAGE pixels (NOT architectural metres or blocks)
- upper_coping: 73 core pixels; 83.6% dark; line RMSE 0.99px; quadratic RMSE 0.98px; circle RMSE 0.82px. Provisional.
- upper_intrados: 61 core pixels; 75.4% dark; line RMSE 3.00px; quadratic RMSE 0.94px; circle RMSE 0.62px. Provisional.
- lower_coping: 72 core pixels; 81.9% dark; line RMSE 3.58px; quadratic RMSE 1.53px; circle RMSE 0.92px. Provisional.
- lower_intrados: 59 core pixels; 71.2% dark; line RMSE 2.68px; quadratic RMSE 0.52px; circle RMSE 0.52px. Provisional.

## Architectural limitations
Source does NOT supply an unambiguous metrological springing coordinate or thickness at decorative joints.
Figure 60 is a different *view* of the Beauvais support concept, but it is not dimensionally registered to 61.
Ungewitter figure 912 is from a different historical reconstruction and is NOT a matching scale view.
No numerical force analysis, true compass center, calibrated plan/elevation or cathedral build is certified.

## Reproduction
Run: python3 build_r11.py from this folder. The downloaded original must be present in the folder.
All source hashes/edge points/QA and overlays regenerate without touching prior experiment files.

## Span topology (image-only)
- upper: min rail separation 11.0px; max 27.0px; no crossing in core = True.
- lower: min rail separation 16.0px; max 24.0px; no crossing in core = True.

Figure 61 labels 4,50 and 6,45, and gives 46,50 to ground. This study intentionally does not derive an architectural unit calibration from them.
