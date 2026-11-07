# Gothic 2D face-and-trace test — experimental

This is a reproducible **raster-derived** SVG, **not yet** a genuinely measured circular-arc reconstruction. Each detected background region is an independent `<path>` with `id="face_NNN"`, accessible in SVG editors. The black linework is vectorized from the source ink; the original source is not changed.

Files:
- `BLACK_TRACE_WITH_SELECTABLE_FACES.svg`: selectable face objects plus separate black-ink layer.
- `FACE_DETECTION_QA.png`: diagnostic color only (green-tinted fully enclosed image regions; blue-tinted regions touching the crop border). These colors do **not** imply physical open/closed classification.
- `FACE_REGISTER.csv`/`.json`: pixel areas, positions, crop-boundary status, unclassified semantics.
- `build_gothic_svg_test.py`: repeatable script.

Next validation stage: identify each foil and moulding boundary, manually assign semantic opening/closed/stone states, locate and fit arc centers with source pixels, evaluate residuals and junction tangencies, and replace the traced stroke with analytic SVG A/arcs or parametric curves. Retain all failed hypotheses in a QA log. Depth is not determinable from this elevation.

No prior scripts, approved generators or cathedral geometry were touched.
