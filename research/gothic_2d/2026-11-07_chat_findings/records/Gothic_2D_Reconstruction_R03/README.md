# Gothic 2D Reconstruction R03 — experimental / for review

**Source authority:** `SOURCE_MIRRORED_UNMODIFIED.png` (unchanged copy; checksum in QA_REPORT.json). The supplied symmetrical composition is a modern mirrored image, not evidence that the historical original included its reflected half.

## Outputs
- `01_BLACK_ONLY.svg`: whole sheet, image-derived vector paths, no axes or colors.
- `02_SELECTABLE_FACES.svg`: independent background-region SVG paths and black ink overlay, faces are white (unclassified in appearance).
- `03_CONSTRUCTION_ANALYSIS.svg`: whole-sheet black trace, thin dashed light gray axes, dotted black fitted circle candidates, dashed red hypothetical regulating connections.
- `04_CLASSIFIED_CANDIDATE_FACES.svg`: *provisional* orange opening-seed faces and green closed-seed faces. White means unclassified. Never take this as verified open-vs-stone classification.
- `CIRCLE_FIT_REGISTER.csv`: repeat-foil frame candidates, center, radius, pixel-fit RMSE and fraction of circular samples hitting ink.
- `FACE_REGISTER.csv`: face positions and tentative semantics.
- `QA_REPORT.json`: quantitative checks, provenance and limits.
- `reconstruct_r03.py`: repeatable source-to-output workflow.

## Evidence levels
1. **Source ink:** traced black pixel boundaries (vectorized); some line thickness artefacts remain.
2. **Measured analytical candidates:** circles matched to the ink of roundel frames, 11 rings total. Their centers/radii are measurable in source pixels, NOT historical CAD-grade construction circles.
3. **Experimental hypotheses:** red links, classifications, relationship to symmetry; must be checked manually.

The central sixfoil is not yet proven to use identical six circular arcs; no precise cusp/tangency construction has been certified. For future fitting select contour points belonging to each separate arc and check residuals against independent scan pixels. The R03 result is a diagnostic baseline, not approved generator code.

No modifications to V08, cathedral geometry, locked dimensions or existing generators.
