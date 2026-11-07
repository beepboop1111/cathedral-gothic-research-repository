# F5ZP 90° paired buttress test — R07

## Source and protection

The unchanged source is **R21-B EXPERIMENTAL** saved on MR.COMPUTER, not an approved cathedral baseline. Only 16 named reference components were embedded in the outgoing 1:1 GLB; 60 new study components (two seats and 28 voussoir pieces per flyer, per side) were added without changing the source GLB.

- Trial pier cores at R5285 / 78° and 102°.
- Trial outer landing pads O80 and O100.
- Native coordinate frame: **Y vertical**, X/Z plan coordinates.
- Both half-cell webs, ribs, inner arch and middle A4 spring polygon included as reference.
- Outer ambulatory, Pass 6J, F5ZK-C and F5ZN-A approved source models were not regenerated or changed.

## Executed validation

- 76 meshes round-trip imported into Blender 5.0.1 (16 reference + 60 experimental).
- All 60 new generated component solids are watertight and have positive volume.
- 8 of 8 specified seat/solid geometric volume intersections are positive.
- Blender BVH comparison of 60 new members against 12 captured vault/rib/arch/springing reference surfaces yielded **zero intersecting triangle pairs**. This does not certify all clearances or any load capacity.
- Source reference bounding boxes unchanged after GLB export.
- The XZ prism-intersection method is appropriate only for the specific trial extrusions tested.

## LIMITATIONS — NOT APPROVED

- A bearing overlap is not a historically correct masonry receiving face, bonded stonework or structural load-path proof.
- The sketch proportions are synthetic: source figure 892 is normalized, then morphed to trial spring/landing locations. Do **not** classify it as historically reconstructed at F5ZP scale.
- F5ZL-C 248-support schedule is missing. Do not reconstruct real support locations from trial pads.
- R21 B chapel arrangement remains experimental. The 14 inner/middle vaults are preserved as a separate protected working-generator family.
- No clearance audit has been performed against all chapels, outer masonry, full roof paths or site passages.

## Reproduction

`python3 scripts/build_r07_testbay.py` uses the original local R21-B GLB path and produces the isolated trial output on MR.COMPUTER. It must not run against approved cathedral files. Blender BVH verification: `blender -b --factory-startup --python scripts/check_bvh_source_collisions.py`. Both scripts include local paths which must be adapted on another machine.
