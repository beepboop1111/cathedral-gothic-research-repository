# Consolidated Gothic 2D development findings — through November 7, 2026

## Goal
Build a reusable historical scan -> geometric understanding -> black SVG trace
-> face classification -> selectable contours -> QA -> approved reusable
2D geometry engine, with an independently developed 3D stonework generator.
The two systems will share geometric source data only once both are validated.

## Historical construction and tracing
- Ungewitter Vol II, Plate CXVIII, figs. 1203-1212a: complete scan-derived
  plate trace in research R02, plus individual figure studies R01.
  Not all arcs and intersection points are historically verified.
- Ungewitter figure 1205b: a/b/c compass annotations and guide positions
  remain unresolved; avoid inventing physical measurements from raster pixels.
- Ungewitter figure 1236 (Plate CXX): eight recovered circle candidates
  (four inner and four outer concentric), mean inner radius 41.47
  source pixels, outer radius 49.62 source pixels. The fit is experimental.
- Research handoff includes figs. 1193-1198, trefoil/quatrefoil, sexfoil,
  Paynter geometric methods and V08 geometry modules; references are not
  approvals of cathedral geometry.

## Five illustrated preliminary 2D workflows
Quatrefoil; octafoil in ring; sexfoil in ring; sexfoil below pointed arch;
octafoil below pointed arch. Initial pictures were generated illustrations,
not geometric scripts. Subsequent source-based SVG workflows are separately
packaged as experimental implementations.

## Mirrored 2D window studies
- Face Test R02: 150 selectable regions, 119 enclosed, 31 open to edges.
- Reconstruction R03: 236 candidate face regions, 232 enclosed,
  11 candidate roundel-frame circles. These are vectorized raster outlines.
- Sixfoil R04: 42 measured circular lobe-section fits across seven upper
  sixfoils; pooled RMS residual approximately 0.302 source pixel on selected
  circular portions only. Six have similar orientation and the central foil
  is rotated by 30 degrees. Cusp intersections/tangencies were not resolved.
- Mirrored depth R02: 358 candidate faces; orange opening, green solid/closed,
  purple through cyan layer styles are provisional semantic/display labels.
- The user accepted the color composition as a VISUAL reference, not as
  measured masonry depth or a validated 3D construction.

## Two-stage original tracery stonework kit
- tracery_regions.py: read black/white drawing, optional mirror/gap bridges,
  classify glass/stone/outside, apply manual ID overrides and export a map.
- tracery_build.py: signed distance fields, chamfer/round/hollow outer profiles,
  line grooves and marching-cubes STL. Default model width is 150 mm,
  which is NOT a calibrated full-size cathedral dimension.

### Final recovered window logs
| Window | Glass regions | Bridges | STL triangles | Reported bounds (mm) |
|---|---:|---:|---:|---|
| Haina 1264 | 21 | 482 | 1692084 | 143x220x5.9 |
| Haina 1265 | 30 | 268 | 1577612 | 142x182x5.9 |
| Meaux | 48 | 530 | 1138024 | 140x125x5.9 |
| Chalons | 19 | 245 | 662720 | 148x75x5.9 |

Final table from user-provided logs. Some region classifications independently
reproduced in previous audit; do not claim all final STL files were rerun here.
The supplied Meaux STL was previously found to have six nonmanifold welded
edges and seven effectively degenerate triangles. The printed one-stone-piece
result verifies 2D mask connectivity, not 3D manifoldness or structure.

## Planned milestones
M01 record four benchmark windows and provenance. M02 isolated Meaux mesh repair.
M03 semantic, stable face IDs and reversible bridging. M04 exact circular geometry,
cusps and tangent joins. M05 independent four-window regressions and GLB validation.
M06 review and approval. M07 shared 2D/3D geometry. M08 architectural expansion to
windows, buttresses, piers, arches and floor plans.

## Validation statuses
Technical, geometric, historical, architectural, structural and approval
categories are different. No automatic promotion to Approved or Locked
should occur from archive publication.
