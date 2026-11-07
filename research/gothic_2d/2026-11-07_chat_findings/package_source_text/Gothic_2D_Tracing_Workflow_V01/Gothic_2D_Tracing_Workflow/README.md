# Gothic Plate Tracing — Read-only Work Package V01

## Priorities

**HIGH 1 — Ungewitter figures 1193–1198** (`plate_1193_1198.png`): six separate 2D traces, first study of rounded trifoils 1193–1195 before pointed 1196–1198. Confirm their source-to-trace curves and arc centers before reuse.

**HIGH 2 — final four-circle screenshot** (`four_circle_construction.png`): center-square construction, tangencies, major regulating circle, and exact numerical relationships. The nominal geometric model is a *candidate*, not a new verified measurement.

**Secondary — trefoil/quatrefoil, Figure 1236**: raster-derived trace and separated color layers. They are generated diagram references, **not untouched historical originals**. Figure 1236 has a proposed rather than proven historical reconstruction.

## Run on a local computer

```bash
python -m pip install numpy opencv-python cairosvg scipy pillow
python scripts/trace_plates.py
python scripts/four_circle_analysis.py
python -m unittest discover -s scripts -p 'test_*.py' -v
```

For genuine circle recovery, copy `docs/ARC_POINT_TEMPLATE.json`, fill each arc with at least three carefully selected **original image-coordinate** (x,y) pixel locations, and run:

```bash
python scripts/fit_arcs.py my_traced_arc_points.json -o outputs/1193_measured_circles
```

The empty template **must not** be run without selecting actual source points.

## Technical boundary

The tracing step recovers *color-classified ink boundaries* as editable vector **polylines**; each thick stroke is traced along its ink edges (sometimes both edges), so **it is not yet a single analytical centerline**. Text inside crops may survive. Color separation is not independent evidence of historical geometry. Its output is for guided review; approval requires comparing the SVG against the original figure crop, selecting the accurate original arc centerline, fitting circles independently, and recording fit residuals.

No historical scale is inferred from pixels, and no physical dimensions, 3D stone depth or cathedral geometry are modified. Existing V08 and STL scripts are unchanged.

## Drawing conventions

- Visible black historical/derived ink: **black**, source crop in separate group.
- Dividing axes: **thin dashed light gray**.
- Uncertain or alternative constructions: **red dashed**.
- Optional recovered full compass circles: **dotted black**.
- During analytical QA only: green circle centers; red calculated intersections.

## Approval gate

1. Check six 1193–1198 source crops and generated outline-only SVGs, particularly the step at the upper right of 1193 and the alternative upper arc on 1195.
2. In 1193–1195, click three or more well-spaced points on each **visible** arc, then run `fit_arcs.py`. Never impose equal radii merely to improve symmetry.
3. For last four-circle study, validate four K/I/J/H centers and the outer A circle against full-resolution source pixels; record corrected center and radius coordinates in a new version, never overwriting original evidence.
4. Confirm tangent/intersection identities; mark doubtful relationships red dashed.
5. Only after user approval promote individual methods into reusable `gothic_geometry.py` adapters, and then into actual 3D work.

## Expected outputs

- `outputs/1193_VECTOR_TRACE.svg` through `outputs/1198_VECTOR_TRACE.svg` (plus PNG reference renders and crops)
- `outputs/TREFOIL_VECTOR_TRACE.svg`, `outputs/QUATREFOIL_VECTOR_TRACE.svg`, `outputs/1236_VECTOR_TRACE.svg`
- `outputs/FOUR_CIRCLE_VECTOR_TRACE.svg` (raster-faithful review)
- `outputs/FOUR_CIRCLE_ANALYTICAL.svg` and `FOUR_CIRCLE_GEOMETRY.json` (provisional measured-point-based mathematical construction)
- `outputs/TRACE_QA.json` (source hash, crop, segment counts, warnings)
- `docs/SOURCE_MANIFEST.json` (exact original bytes and duplicate record)

**Important distinction:** Figures 1193–1198 are traced from a *previously generated composite reference plate*, not the untouched original Ungewitter scan. Before historical certification, replace it with an actual source scan and compare line by line.
