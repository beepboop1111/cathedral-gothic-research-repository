# NEW CHAT HANDOFF — F5ZP Phase 3A / Ungewitter II / CXVIII / 1205b

## Mission
Continue the *existing* experiment on the circular quatrefoil motif labelled 1205b from Ungewitter–Mohrmann, *Lehrbuch der gotischen Konstruktionen*, Volume II (1892), original PDF page 281 (1-based), plate CXVIII. Recover the *inner* quatrefoil arcs, construction centers, arc intersections and cusp geometry; do not simply repeat the already-completed outer-circle test.

## Materials in this ZIP
- `experiment/`: original page, unscaled figure crop, source-derived grayscale and transparent working images, sampled points, outer-circle overlay, measurements, README.
- `tools/preprocessing/`: three user-provided Python scripts, unchanged.
- `tools/V08/`: user-provided V08 geometric reconstruction code and tests, unchanged.
- `HANDOFF.md` (this file) and `MANIFEST_SHA256.json`.

## Verified baseline (from experiment measurements)
- Source: `lehrbuchdergotis02unge.pdf`; Volume II 1892; PDF page 281; plate CXVIII, motif 1205b.
- Outer circle only: center in crop (109.2174, 111.2396) px; radius 93.5169 px.
- Fit: 360 sampled locations, 339 inliers, RMS radial residual 0.6916 px. This was a *conditional local fit* using approximate boundary points, not independent detection.
- Original page render recorded as 144 DPI; motif crop 225 x 226 px. Physical architectural scale unknown.
- No inner quatrefoil arcs have been reconstructed yet. No verified Gothic geometric centers or masonry/opening segmentation.

## Work order
1. Inspect original crop and full page. Identify the ink that belongs to inner lobe arcs vs construction circles, dimension marks, hatch/print artifacts.
2. Generate multiple reversible segmentation alternatives using provided preprocessing; preserve untouched originals.
3. Isolate one lobe at a time and fit circles/arcs with sufficient coverage, report sample selection and residuals. Treat incomplete or ambiguous segments as provisional.
4. Determine candidate center relationships and intersections; do not force symmetry if the drawing doesn't support it. Distinguish idealized historical construction from scanned ink measurements.
5. Create vector outputs (SVG and optionally JSON with centers, radii, angle spans), fit/overlay PNGs and numeric QC.
6. Produce a concise report and a zipped result; do not create STL until geometry is verified.

## Constraints
- Do not modify cathedral F5ZP locked geometry, floor plan, vaults, piers, moulding standards, existing generators or source images.
- Do not promote image-pixel measurements to 1:1 architectural scale.
- Distinguish primary-source facts, historical interpretations, and experimental inference.
- Keep scripts unchanged; modifications should be new wrapper/experiment files.
- Work on motif 1205b before moving to other plates.
- Original source full-book PDF remains in Research Project; this package already includes the necessary original plate image.

## Suggested opening request
“Continue Phase 3A from HANDOFF.md. Reconstruct and validate the inner quatrefoil of Ungewitter II Plate CXVIII figure 1205b, producing measured SVG/JSON geometry, overlays and QC. Preserve all source material and do not modify cathedral models.”
