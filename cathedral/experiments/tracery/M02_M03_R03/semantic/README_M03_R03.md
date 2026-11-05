# M03 — semantic face registry R03

**Experimental. No historical, architectural, or generator approval is implied.**

`tracery_semantics_R03.py` adds a read-only semantic layer over the unchanged region maps produced by the recovered original `tracery_regions.py`. It does not modify any map, 3D input, cathedral geometry, or authoritative generator.

Each connected source-map region has a selectable SVG path and a JSON record. Records distinguish `opening`, `closed_stone`, provisional `moulding`, `outside`, and `uncertain`; they include confidence, evidence, source-map SHA-256, pixel bounds, normalized reference anchor, normalized area, shape signature, raster hole count, crop-edge contacts, and review flags. The original map class remains in `input_kind` even if the semantic interpretation changes.

## Identity and corrections

IDs are scoped to `source_family`. Their digest includes normalized bounds, centroid, area fraction, a 32×32 normalized occupancy signature, and raster hole count. It excludes flood-fill labels, component enumeration, display palette, and filename. Unchanged inputs reproduce the same IDs. Exact nearest-neighbor 2× scaling also preserves IDs in the executed tests.

Manual decisions live in a separate correction JSON. Every override must carry a source-family ID, normalized anchor, expected area/bounds, shape signature, and hole count. Replay requires exactly one region containing the anchor, area change at most 2.5%, coordinate-bound change at most 0.003 of the image, equal normalized shape signature, and equal raster hole count. Duplicate decisions or unmatched/split/merged regions are reported as conflicts; the CLI exits with code 2. These guards deliberately require reconciliation when source geometry changes. They are not a proof of arbitrary-resolution or arbitrary-edit correspondence. A confidence of 1 on a manual correction records that the supplied decision was applied; it does not establish historical correctness or user approval.

The default palette contract decodes the four original map colors. `--palette-json` accepts another explicit color-to-meaning contract. Palette-independent correction replay does not rely on the displayed color.

## Conservative classification

- Openings and outside regions inherit the original region-map decisions; the inherited decisions are not new historical evidence.
- Broad white faces can remain closed stone. Thin or long white bands are **provisional moulding candidates** with low confidence, without any inferred physical depth.
- Very small white regions remain uncertain. Detached stone-mask islands smaller than 2% of the largest stone network are flagged as possible annotation/fragment candidates; they are retained rather than removed.
- Ink is retained as observed linework. Its physical interpretation is uncertain: it may include outlines, moulding marks, axes, or printed text.
- Every region touching the image boundary carries a crop-contact flag. Openings at a crop boundary are not silently called complete historical openings.

The source maps contain thousands of tiny enclosed raster details. The total face count includes those details; it is not a count of architectural panels or manufactured stones.

## Geometry and units

SVG paths sample the source raster at half-pixel contour positions. They are individually selectable/editable and retain stable IDs, but they are not exact fitted arcs, compass constructions, or CAD moulding sections. JSON pixel areas and coverage refer to the unchanged raster; SVG rasterization can differ at subpixel corners. There is no physical calibration or inferred historic thickness. Colors visualize semantics, not physical depth.

The retained source-map opening counts are Meaux 48, Haina 1264 21, Haina 1265 30, and Châlons 19. These are classification counts. The builder's cleanup and meshing can produce a different number of actual through-holes, which must be checked separately in the M02 mesh QA.

## Reproduce

From the checkpoint root:

```bash
bash semantic/reproduce_semantics_R03.sh
```

For one map:

```bash
python semantic/tracery_semantics_R03.py baseline/maps/meaux_map.png \
  --out-dir semantic/meaux --family meaux
```

To replay an explicitly edited correction sidecar, add `--corrections-json PATH`. The delivered `*_corrections_TEMPLATE_R03.json` files contain empty override lists; the example decision has not been applied.

## Validation delivered

`unit_tests_R03.log` records synthetic tests for deterministic/reordered enumeration, alternate palettes, exact 2× identity and decision replay, split rejection, merge rejection, hole-topology guard, wrong-source rejection, missing guards/invalid classes, crop contacts, and unknown marks. `semantic_benchmark_tests_R03.json` records full-resolution tests for all four maps: expected opening components, complete pixel coverage, ID stability under reordered enumeration, manual-decision replay, and exact 2× ID preservation for every source opening. `svg_validation_R03.json` checks that every face has a unique selectable SVG path matching its JSON record.

`validate_semantic_exports_R03.py` creates the matching source/semantic comparison sheet and consolidated semantic QA. When Inkscape is installed, it independently renders every delivered SVG to PNG and records the result in `svg_render_validation_R03.json`; PIL-based previews remain available without Inkscape.

No source corrections, face promotions, historic arc reconstructions, or changes to the 3D input map are included. Further architectural interpretation of the uncertain tiny faces and provisional moulding bands remains review work.
