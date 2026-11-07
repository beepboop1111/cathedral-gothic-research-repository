# Gothic 2D tracing and depth-classification workflow — R01 experimental

## What the recent studies taught us

1. **Source and reconstruction are different objects.** The uploaded historical crop is evidence. The clean black-line illustration was image-generated, not an authenticated pixel-perfect tracing or an analytically fitted circular reconstruction. Never claim the image-generation result proves source geometry.
2. **One foil is not the window.** Local cinquefoil/sexfoil/trefoil outlines must be placed within circular rings, parent pointed arches, outer encompassing tracery, cusps, joints, mouldings, shafts and capitals. Geometry must be checked at connections, not merely as individually plausible motifs.
3. **Topology matters.** The real task is to distinguish open spaces from continuous closed architectural regions, including tiny spandrels, narrow channels and returns. A color fill is a *classification hypothesis*, not a physical-stone proof.
4. **Geometry, face class and drawing appearance are independent.** A single shape can be rendered as monochrome evidence, an open/closed classification diagram, or a layer/depth study without altering any of its coordinates.
5. **A richer palette reveals nested mouldings.** Outer visual layers can be purple, indigo, blue, azure and cyan; intermediate rings yellow; deeper drawn outlines warm orange/red. This is a **diagrammatic ranking** until supported by section evidence, not measured 3D relief.
6. **The user wants progressive development with approvals.** Test a drawing, display directly, correct it, save method and parameters; only after explicit approval promote to the project baseline. Never overwrite the cathedral's locked geometry or original generators.

## Visual modes

- **TRACE**: black solid edges, white paper. When exposing geometry, thin gray dashed regulating axes, black dotted complete recovered circles and red dashed uncertainty overlays. No such auxiliary marks when the user requests *black trace only*.
- **OPEN_CLOSED**: black ink remains; orange fills denote observed open voids; green fills denote visually closed faces. White = unreviewed or reserved.
- **DEPTH_STUDY**: same source geometry, manually assigned ordered appearance bands: purple → indigo → blue → cyan → yellow → orange/red as reading moves inwards. This color is interpretive unless original sectional/depth data supports it.

## Working procedure

1. Preserve original scan bytes and SHA-256. Log the image's resolution and coordinates; do not infer architectural dimensions from pixels.
2. Crop for analysis if needed but keep the source scan and a whole-page audit image.
3. Build or select a **black vector trace**: fit arcs, record centers/radii, test tangencies and cusp intersections; label verified/measured/provisional. For purely presentational images, explicitly mark them *image-generated study*.
4. Close only demonstrated boundaries, and record each manual closure. Do not bridge nearby lines automatically if this could change topology.
5. Identify each bounded face: `open`, `closed`, or `unclassified`. Maintain source anchors and a face ID register.
6. If useful, annotate moulding bands `outer`, `frame`, `middle`, `inner`, `ring`, `deep`. These are relative drawing levels and require external evidence for physical depth.
7. Generate monochrome output first. Produce optional orange/green and multicolor depth overlays as **separate derivatives**. Keep black outlines visible.
8. QA by comparison to original: profile preservation, cusp connections, enclosed-area leaks, overfilled spandrels, ambiguous joins, topological area counts and whether an apparently closed face is genuinely solid.
9. Submit work for review; only save as approved working method upon explicit acceptance.

## What is NOT learned or verified

- The image-generation steps did not produce auditable scripts or prove compass-and-straightedge accuracy.
- Flat elevation images cannot establish actual stepped depth, masonry relief, structural continuity or historic color schemes.
- The supplied image crop alone does not justify inventing hidden or cropped portions of tracery.
- A region inside a boundary is not automatically stone: triangular spandrels may be voids, solid infill, or recessed backgrounds. Classify against source and construction evidence.

## Experimental script: `depth_classify.py`

```
python depth_classify.py experimental_black_line_source.png example_seeds.json --out example_preview.png
```

Requires `Pillow`, `numpy`, `scipy`. Edit `example_seeds.json` to place an `(x,y)` seed **inside** each genuinely closed raster face and set its class. The script finds white connected components behind dark ink, optionally dilates line barriers one pixel to reduce leaks, colors only the selected faces, and paints the original ink back as black. No source is modified. It also writes a JSON QA report listing classified faces and warnings.

**Caveats:** Fine raster gaps leak, extremely narrow faces might disappear under dilation, exterior and adjoining regions can be connected, and some sample seeds may select the same connected region. The included preview is deliberately an **incomplete test of the fill engine**, not a fully classified version of the entire design. It is not an analytic SVG trace and does not replace V08 circle fitting. For project-scale work, SVG closed-path region IDs and explicit construction geometry should supersede raster flood fill after review.

## Evidence / origins

- User-supplied Gothic historical fragment: `Pasted image.png` (not changed).
- Prior black-line image-generation study included in this package for a functional example, not as verified historical tracing.
- V08 `gothic_plate_reader.py`, `gothic_geometry.py`, `gothic_patterns.py`, `gothic_stonework.py` remain separate, unmodified dependencies of the larger 2D/3D research environment. None is required for this classification preview.

## Approval

**Status: EXPERIMENTAL — NOT APPROVED.** This package is provided for review and must not silently replace any approved 2D scripts, locked cathedral geometry, or existing 3D generators.
