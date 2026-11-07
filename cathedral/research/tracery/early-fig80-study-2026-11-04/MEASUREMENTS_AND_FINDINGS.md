# Early St. Leu Fig. 80 — Measurements, experiments and QA

All numbers below refer to the source **545 × 825 px engraving**, not architectural units. Do not equate small source-ink residuals with actual historical surveying accuracy.

## Early R01 — upper circular tracery

A manually seeded robust circle fit sampled ink around the source. The measured candidates were:

| Element | Center X | Center Y | Radius px | Selected-ink RMS px | Samples |
|---|---:|---:|---:|---:|---:|
| Central opening | 269.94 | 212.99 | 38.48 | 0.31 | 120 |
| Oculus ring | 267.81 | 209.96 | 85.99 | 1.05 | 64 |
| Upper left lobe | 244.26 | 168.81 | 20.85 | 0.74 | 66 |
| Upper right lobe | 296.50 | 169.24 | 21.20 | 0.62 | 66 |
| Left lobe | 218.01 | 214.17 | 20.95 | 0.61 | 56 |
| Right lobe | 319.50 | 213.20 | 20.69 | 0.95 | 51 |
| Lower left lobe | 242.57 | 254.57 | 19.60 | 0.55 | 35 |
| Lower right lobe | 296.46 | 254.54 | 20.40 | 0.65 | 25 |

A candidate regular sixfold construction has regulating-center position (269.55, 212.42) px, ring radius 50.45 px and **1.78 px RMS** positional difference between proposed and measured centers. Twelve mathematical circle–circle intersections were calculated; they were **not** independently established as twelve visible architectural junctions. Unsighted arc continuations were left uncertain.

## Early R02 — upper enclosing arch and two lancets

The left-side fitted half-arcs below were seeded with manually picked points and represent provisional **circular-arc hypotheses**. The right side was mirrored rather than independently measured. The source plate includes glazing bars and masonry hatching that were intentionally not treated as stone sections.

| Half-arc | Radius px | Fit RMS px | Approx. center (x,y) px |
|---|---:|---:|---|
| Outer enclosing arch, inner left | 875.56 | 3.23 | (884.81, 703.73) |
| Outer enclosing arch, outer left | 752.15 | 2.39 | (767.15, 626.01) |
| Left lancet, inner left | 189.22 | 0.48 | (282.68, 432.09) |
| Left lancet, inner right | 180.36 | 0.62 | (69.74, 429.79) |
| Left lancet, outer left | 191.76 | 0.60 | (275.89, 431.83) |
| Left lancet, outer right | 192.78 | 0.43 | (68.07, 435.93) |

R02's disconnected proof-of-workflow used three individually closed rail sweeps (5,276 triangles each) and a simplified 12-triangle boxed mullion, totaling **15,840 triangles**. Each swept arch piece was reported watertight with consistent winding and zero calculated rail-position discrepancy. The assembly, however, **did not prove connected architectural stonework**. All profiles were hypothetical.

## Early R03 — unified masonry prototype

An independent R03 model formed a continuous planar stone region and two 3D variants from it. The oculus opening is **one union of seven candidate circles**, not seven separate glass holes, plus two lancet cuts. The plain/profiled variants were both reported to be one connected, watertight, consistently wound volume, without degenerate triangles below area2 threshold 1e-10.

| Geometric check | Plain | Profiled |
|---|---:|---:|
| Vertices | 5,260 | 28,067 |
| Triangles | 10,520 | 56,134 |
| Mesh connected bodies | 1 | 1 |
| Watertight | Yes | Yes |
| Volume, trial pixel-cubed units | 1,282,475.759 | 1,490,707.786 |
| Max provisional face depth, image units | 12.0 | 15.8 |

R03 reported one 2D connected stone polygon; stone face area ~106,872.98 pixel²; two open lancet cuts; one unioned central foil cut. Reported pre-join crown seam gaps: enclosing outer 1.682 px; left inner lancet 0.991 px; left outer lancet 0.830 px. They were corrected/merged during this experiment; this does **not** establish exact historical junctions.

MR.COMPUTER recreated the plain model at **5,260 vertices / 10,520 faces / 1,282,475.7590 volume** and the profiled model at **28,067 vertices / 56,134 faces / 1,490,707.7863 volume**, both watertight and with one connected body. The Blender scene and independent QA are archived next to these findings. The copied MR exports differ in file checksums from the original locally exported R03 STL/GLB, despite numeric agreement; do not assert bit-for-bit equality.

## Source uncertainty and no-promotion status

- Left-side ink fits and theoretical symmetry are provisional; the mirrored right side has not been independently surveyed.
- Inner oculus and foil intersection curves, stone thickness, voussoirs, glazing rebates, tooling, and load path remain unverified.
- The R03 face-relief cross-section is a *demonstration* and **not** a historically identified profile.
- Black = source-supported outlines; dashed gray = construction; dashed red = uncertain candidate geometry.
- Validation levels (technical/geometric/architectural/historical/structural) are separate. Source-coordinate fits and watertight meshes **do not** establish architectural, historical or structural approval.
- Existing later St. Leu R04–R07 reports and geometries in the repository are independent subsequent experiments; do not overwrite them or call this early R03 their approved source.
