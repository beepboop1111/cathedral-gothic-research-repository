# F5ZP Phase 3A — CXVIII / 1205b inner-arc research

Research checkpoint, 3 November 2026. **EXPERIMENTAL reconstruction of engraved ink; no architectural calibration or approval.**

The recovered drawing supports six circular arc pieces rather than one complete circle for each lobe. The top lobe and upper halves of the side lobes have radii approximately 43 pixels; the bottom lobe and lower side halves have radii approximately 36 pixels. Two upper cusp intersections are recoverable. The lower pairs are separated even when their supporting circles are completed. The SVG preserves those open ends.

![Matched source, overlay and analytic reconstruction](derived/comparison.png)

## Source and inherited authority

Ungewitter–Mohrmann, Volume II (1892), original PDF page 281, Plate CXVIII, figure 1205b. Original source book SHA-256: `39a90b73c3ac7883ba82739b487573796c9e05edc98a75d30bad945c058467cf`. The supplied 144-DPI page/crop and all 24 handoff-manifest files remain byte-identical. The book itself was read without editing; it is not duplicated in this package.

The inherited outer circle is held fixed: center **(109.21742236738913, 111.23955699522183)**, radius **93.51694870364518 px**. Its prior conditional fit RMS remains **0.6915841262264908 px**, 339/360 inliers. This experiment does not refit or promote that reference.

A 432-DPI derivative was rendered directly from the matching PDF, not by enlarging the supplied PNG. Re-rendering at 144 DPI reproduced the supplied crop pixel for pixel. The PDF page contains a 2259 × 3271 detail image; rendering at 432 DPI is still resampling, not a claim of new scan resolution. No additional historical facts are inferred from extra render pixels.

## Coordinates and measurement

All table values use the original **144-DPI crop pixel coordinates**. Origin is the center of the crop's top-left pixel, X right, Y down. Positive angles run clockwise from +X. Page coordinates add (114,239). A high-resolution pixel index maps to reference coordinates as **(index − 1)/3**; this accounts for pixel-center alignment. The SVG has viewBox `0 0 225 226` and uses those same units. Its display size does not define physical units. Full-precision numeric parameters are in `derived/geometry.json`.

| Arc | Center X | Center Y | Radius | Fit RMS | Samples retained | Block holdout RMS |
|---|---:|---:|---:|---:|---:|---:|
| N | 109.745 | 59.420 | 42.727 | 0.153 | 86/86 | 0.188 |
| E_upper | 160.934 | 112.288 | 43.011 | 0.120 | 40/40 | 0.152 |
| E_lower | 167.001 | 112.074 | 36.402 | 0.149 | 52/52 | 0.285 |
| S | 108.447 | 169.018 | 36.056 | 0.162 | 104/105 | 0.335 |
| W_lower | 51.102 | 111.627 | 36.457 | 0.145 | 54/54 | 0.169 |
| W_upper | 58.705 | 112.460 | 43.808 | 0.154 | 41/41 | 0.295 |

Radii and centers were fitted independently. No rotational symmetry, common radius, outer-circle tangency or closed topology was imposed. The values are engraving centerline measurements, not stone or opening boundaries.

## Intersections and cusp geometry

| Upper junction | X | Y | Acute tangent crossing |
|---|---:|---:|---:|
| N__W_upper | 68.276 | 69.710 | 63.444° |
| N__E_upper | 151.028 | 70.434 | 61.746° |

Each upper pair has a second supporting-circle intersection inside the figure. It is recorded in JSON but is outside the chosen engraved arc spans and is not used as a cusp. Acute tangent crossing is the smaller angle between the two tangent lines, not an assigned masonry cusp angle.

The completed south/west-lower circles have a **8.617 px** minimum separation; the south/east-lower circles have a **9.219 px** separation. There is no real intersection to use for either lower cusp. Extending or closing them would invent geometry. Lower free endpoints are read approximately from the stroke and projected onto their fitted circles; their location is uncertain by about 1 reference pixel.

The independently measured upper/lower side arcs leave endpoint discrepancies of **0.870 px west** and **0.582 px east**. They remain separate paths. Their apparent common side contact is consistent at ink scale, but an exact analytic join has not been established. Inner-circle internal-tangency errors relative to the inherited outer circle range from 0.322 to 1.221 px. Exact outer tangency is therefore not claimed.

All 21 supporting-circle pairs, including the outer reference, have relation/intersection records in JSON. Supporting-circle intersections are not automatically part of the visible geometry.

## Sampling, alternatives and numerical validation

The unchanged supplied grayscale and threshold scripts produced fixed-155, fixed-180 and adaptive alternatives. The supplied hatch script was run in no-fill mode as a diagnostic; it was excluded from fitting because closing can bridge construction marks or alter cusps. There is no masonry mask.

The new wrapper uses V08 plate inspection, ink extraction, `circle_fit` and `sample_arc`. A human-interpreted seed circle and angular window isolate each stroke. At 2° steps, a ±4 px radial search identifies contiguous dark runs; a darkness-weighted radial centroid supplies each sample. Runs wider than 2.5 px and rays within 6° of the guide axes are rejected. A robust preliminary circle rejects residuals over 1 px, then V08 fits the retained points. Of 378 sampled positions, 377 are retained. The CSV records every candidate sample, width, residual and retention flag. These are **conditional local fits**, not independent arc detection or statistical proof of a historical construction.

On the identical raw sample set, the four-circle model has **0.667 px RMS** and the six-arc model has **0.205 px RMS**. These models have 12 and 18 free circle parameters respectively. The different side-arc radii improve the descriptive fit substantially; the comparison does not establish an author's intended construction.

Five angular-block holdouts are fitted on the other four blocks before residual rejection; the table reports prediction RMS on held-out samples. Holdouts test local arc extrapolation within the selected strokes. They are not a new engraving or independently annotated ground truth.

Thresholds 110,135,155,180 change centers by at most **0.151 px** and radii by at most **0.147 px** relative to threshold 155. Six-block bootstrap percentile bounds (250 deterministic resamples) are supplied as sensitivity ranges, not metrological confidence intervals: scan distortion, seed selection, ink thickness and shared pixel errors remain unmodeled.

![Sample selection](derived/selected_samples.png)

The source/overlay views, segmentation sheet and per-arc residual plots were visually inspected. All 11 supplied V08 tests pass. SVG re-parsing verifies all six circular `A` commands and endpoint circle equations within 1e-7 px; upper intersection equation errors are below 3e-14 px. Those tiny errors validate analytic export consistency, not the accuracy of the drawing. The SVG is not a faceted polyline and contains no forced closing segment.

## Historical interpretation and limits

Primary-source observation: the upper strokes meet at visible pointed cusps, the lower strokes stop with gaps, and several fine guide curves coexist in the lower-left quadrant. The figure may be contrasting construction choices or radius regimes, rather than depicting a single completed symmetric opening. That is an experimental interpretation; accompanying explanatory text has not been checked. The fine guide curves, a/b/c lettering and diagonal lines are retained in the source, excluded from the lobe fit and not assigned verified construction-center identities.

The two upper cusp candidates and six local circular pieces are measurable research results. This is not a fully closed quatrefoil, a verified stone section, or an approved design. No STL is made. No cathedral geometry, locked dimensions or existing generator has been changed.

## Contents and reproduction

- `derived/1205b_measured.svg`: six editable circular paths, centers and unchanged outer reference.
- `derived/1205b_overlay.svg`: self-contained SVG with original crop embedded for comparison.
- `derived/geometry.json`: full-precision centers, radii, spans, endpoints, lengths, intersections and coordinate conventions.
- `derived/stroke_samples.csv`, `threshold_sensitivity.json`, `model_comparison.json`, `validation.json`: numeric evidence and provenance.
- `derived/comparison.png`, `selected_samples.png`, `radial_residuals.png`, `segmentation_alternatives.png`: visual evidence.
- `source_handoff/`: complete supplied handoff and unchanged tools.
- `CHECKPOINT.md`: bounded continuation instructions.
- `research_report.html`: self-contained offline visual report.

Run `python scripts/reconstruct.py` to regenerate measurements and visuals from the bundled derivative, then `python scripts/make_report.py` to rebuild this report. Optional source reproduction: `python scripts/render_source.py /path/to/lehrbuchdergotis02unge.pdf` before reconstruction. Dependencies and recorded versions are in `requirements-recorded.txt`. No network or cathedral generator is required for regeneration.

Next bounded research task: locate the explanatory text for 1205b and verify the a/b/c construction alternatives; then test explicitly labeled constrained construction variants alongside these measurements. Preserve this measured candidate and inherited outer reference. Do not silently fill the lower gaps or substitute an idealized symmetric design.
