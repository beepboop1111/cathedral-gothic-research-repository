# F5ZP — Crossing masonry floor plan R06 (experimental drawing checkpoint)

Date: 2026-11-05
Branch: cathedral/crossing-masonry-floor-plan-r06-2026-11-05
Status: DRAWING/TECHNICAL CHECKPOINT ONLY. No new architecture approved or promoted.

## Recovered source and decision
- Original selected, locked preferred spatial concept: Crossing_Full_Cell_R05 (PREFERRED_SOLUTION.md).
- Original files: Crossing_Full_Cell_R05.blend, Crossing_Full_Cell_R05.glb, Crossing_Full_Cell_R05_Package.zip, preserved unchanged in personal Library.
- R05 GLB SHA-256: 1e0d1d498673182f27f33fd78bfeb3f816dade9247eca1a7fb9c426059c44861.
- Source geometry and vault script inputs: R05 PARENT_R02_GEOMETRY.json, TWO_REMAINING_VAULTS.json.
- Governance master: cathedral/governance/CATHEDRAL_MASTER_REFERENCE.md, branch cathedral/governance-r01, SHA 1d7e358ff7562fcc64088854baa2abd3d31a729e.

## Result
- A separate R06 two-panel architectural floor-plan rendering and 1:1 source-coordinate SVG were generated from the saved R05 source, using a newly versioned independent Python drawing script.
- Exactly four complete J11 former vault cells become solid masonry, one at each crossing corner.
- Four compound masonry footprints, area 1,929,216 project-unit² each, include the prior crossing core.
- J12 and J13 remain at each corner: eight remaining low-vault bays; zero J11 vault cells retained.
- Clear central crossing reference: 4970 native project units.
- No substitute vault, passage, partial stone fill, or corbel in the J11 cells.
- All eight J12/J13 bay footprints have zero area overlap with the selected solid masonry footprints.
- Four saved GLB masonry footprint polygons agree with PARENT_R02 source exactly: four zero-area symmetric differences.
- The saved R05 GLB contained 118 geometry records and was opened read-only for footprint comparison.
- SVG XML parsing and ZIP integrity checks passed.

## Local review deliverables (not committed into GitHub by this note)
- F5ZP_Crossing_Floor_Plan_Masonry_R06_FOR_REVIEW.zip
- Crossing_Masonry_Floor_Plan_R06.png
- Crossing_Masonry_Floor_Plan_R06.svg
- Crossing_Masonry_1to1_Source_Coordinates.svg
- Plan_Geometry_QA.json
- build_crossing_plan.py and README.md

## Unresolved and unchanged
- This is a local crossing-area plan; a calibrated, aligned, authoritative whole-cathedral floor plan has **not** been recovered for integration.
- Source geometry uses 1:1 native numeric project units; physical unit conversion is unverified. Do not rescale blindly.
- The R05 height of 4392 and upper 896-square support prism are study assumptions, not approved construction data.
- Structural thrust, bonding, loads, foundations and F5ZL-C support schedule remain unresolved.
- F5ZK-C, F5ZN-A, all approved cathedral geometry, working inner/middle ambulatory vault generator and Pass 6J were not modified.
- No change to governance master or protected project branches.
