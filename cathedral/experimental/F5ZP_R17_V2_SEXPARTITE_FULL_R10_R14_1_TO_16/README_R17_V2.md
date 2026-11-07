# F5ZP R17 V2 — sexpartite Gothic vault (1:16)

**Status: experimentally validated geometry, NOT architecturally approved.**
Open `F5ZP_R17_V2_FULL_R10_R14_GOTHIC_SEXPARTITE_1to16_LIVE_EXPERIMENTAL.blend` on MR.COMPUTER.

The entire primary model, GLB and STL are **actual 1:16 scaled geometry**, not a Blender scene scaled visually. Multiply by exactly 16 to restore native dimensions only when necessary. The Blender object scale is (1,1,1), and there is one 1:16 scene.

## Recovered Gothic vault-surface generator

- R09: full triangular sector loft with shared welded groin seam nodes.
- R10: controlled C1 cubic-Hermite meridians from boundary arch apex to boss.
- R13: reuse of normalized meridian controls for matching Type A sectors.
- R14: separate Type B meridian and `sin(pi*t)^2` interior-only height blending.
- R16: mandatory apex-to-crown and locked-geometry guards, run before and after build.

This is a **port of those actual methods to a new sexpartite boundary skeleton**. The original R10–R14 scripts and their hashes are in `reference/` and `qa/R17_V2_SOURCE_LINEAGE.json`. They are protected and unchanged. The 1:1 Z4296 chapel methods cannot run verbatim for this new Z4700 sexpartite boss without adapting their input geometry.

## Geometry and QA

- Rectangular six-cell sexpartite double bay; 4 diagonal plus 2 intermediate ribs.
- Six true two-centred boundary arches, independent matching groin paths.
- Highest boundary apex native Z4320; central boss Z4700 (380 units higher).
- 98,304 triangular web faces, 49,537 Blender vertices; open intrados only.
- Measured perimeter and groin displacement from prior independent R17 source: zero.
- Measured downhill meridian sag: zero.
- All R16 strict crown and locked-geometry warnings recorded.
- Exact ×16 recovery checked within STL export precision.

**Not verified:** approved masonry thickness, structural bearing, cap/roof clearance, historical design. Original F5ZK-C/F5ZN-A cathedral architecture, Pass 6J, and approved generator sources unchanged. F5ZL-C support schedule remains unresolved.

## Regenerate

`python3 scripts/build_R17_V2_full_surface.py`

`/usr/bin/blender -b --factory-startup --python scripts/make_R17_V2_blender.py`

Both refuse to overwrite their previous experimental outputs; run in a versioned fresh copy. See `qa/R17_V2_FULL_SURFACE_VALIDATION.json` for measurements.
