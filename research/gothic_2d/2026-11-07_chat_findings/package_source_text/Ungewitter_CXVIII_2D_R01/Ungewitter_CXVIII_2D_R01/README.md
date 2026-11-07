# Ungewitter–Mohrmann, Volume II, Plate CXVIII — 2D tracing R01

## Contents
- `ORIGINAL_UNMODIFIED.png`: exact supplied original (byte-for-byte).
- `PLATE_CXVIII_FULL_SCAN_VECTOR.svg`: editable entire historical ink image as black filled contours. Includes all engraved marks, including lettering.
- `FIG_*_SCAN_TRACE.svg`: cropped, individually editable figure traces with light-gray dashed axes.
- `FIG_1204` and `FIG_1205`: black dotted circle candidates and red dashed provisional compass guides. These are NOT confirmed original compass centers.
- `TRACE_MANIFEST.json`: hashes, crop coordinates, processing settings and contour counts.
- `trace_plate.py`: reproducible tracing code.

## Status: experimental — needs geometric validation and user review
The black drawing is *image-derived vector ink*, rather than a mathematically recovered compass-and-straightedge reconstruction. This preserves the distinctive published engraving and is a useful first pass before separately replacing individual curves with fitted true circles. Thin ink and crowded labels can be fragmented; the crop boxes should be checked. Recovered circles shown are approximate reference candidates only. There is **no architectural scale calibration**. The source is not silently promoted to cathedral geometry or a working approved generator.

## Next pass
Individually identify and fit the circular arcs in figures 1204, 1205 and 1209 from selectively sampled ink points, then test tangencies, intersections and source residuals. Keep solid outlines black; axes light-gray dashed; full recovered circles dotted black; conjectures red dashed.

Run: `python trace_plate.py plate.png output_folder` (requires opencv-python, numpy, Pillow; CairoSVG optional for PNG previews).
