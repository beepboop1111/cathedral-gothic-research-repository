# Gothic tracery moulding generator J01–J05 (research archive)

**Archive date:** 2026-11-09. Separate from R33 masonry research. Never overwrite approved cathedral geometry.

## Pass dispositions

| Pass | Outcome | Status |
|---|---|---|
| J01 | 13 procedural swept members, voxel union and GLB round-trip passed | geometric baseline |
| J02 | Isolated Y junction exact Boolean, 68 exterior controls with zero tested drift | isolated test validated |
| J03 | Full exact-Boolean fusion: 35 boundary edges and 1571 nonmanifold edges | FAIL |
| J04 | Manifold Boolean silently dropped most inputs, despite watertight output | FAIL_INPUT_LOSS |
| J05 | manifold3d union of 13 members; one connected solid, 0 open/nonmanifold edges, GLB roundtrip passed | GEOMETRIC EXPERIMENT PASS |

**No architectural, historical, or structural approval.** Source units are unverified and source-derived plate geometry was not reconstructed.
J05 does not preserve every vertex at intersections; require explicit construction trimming and moulding-flow improvements before approval.
The discarded J04_FULL_PASS.glb is intentionally excluded because it was a FALSE POSITIVE.

## Reproduction

Run individual J01–J04 generator Python scripts in Blender with matching fixture assumptions.
J05: run export_paths.py inside Blender, robust_union.py in local Python (numpy, trimesh, manifold3d==3.5.4), then render_validate.py in Blender.
The installed manifold3d wheel itself is intentionally excluded.
**Executed tests used Blender 5.0.1. Blender 5.1+/5.2+ not tested.**
All saves are experimental; no cathedral baselines were modified.
Next step J06: explicit curve intersections, trimmed junction topology, profile continuity and regression.

## Files
- J01/J01_EXPERIMENTAL_moulding_continuity.glb (10277348 bytes)
- J01/J01_EXPERIMENTAL_scene.blend (7053054 bytes)
- J01/J01_FINAL_moulding_continuity.png (2229620 bytes)
- J01/J01_QA.json (3510 bytes)
- J01/J02_EXPERIMENTAL.blend (874535 bytes)
- J01/J02_FINAL_profile_preservation.png (1931511 bytes)
- J01/J02_QA.json (1751 bytes)
- J01/J02_exact_local_junction.glb (33732 bytes)
- J01/J03_EXPERIMENTAL.blend (7646986 bytes)
- J01/J03_EXPERIMENTAL_full_exact.glb (1196436 bytes)
- J01/J03_FINAL_full_tracery_comparison.png (2051256 bytes)
- J01/J03_QA.json (4801 bytes)
- J01/generate_J01.py (11835 bytes)
- J02/J02_EXPERIMENTAL.blend (874543 bytes)
- J02/J02_FINAL_profile_preservation.png (1915259 bytes)
- J02/J02_QA.json (1751 bytes)
- J02/J02_exact_local_junction.glb (33732 bytes)
- J02/generate_J02.py (7483 bytes)
- J03/J03_EXPERIMENTAL.blend (7646999 bytes)
- J03/J03_EXPERIMENTAL_full_exact.glb (1196436 bytes)
- J03/J03_FINAL_full_tracery_comparison.png (2051256 bytes)
- J03/J03_QA.json (4800 bytes)
- J03/generate_J03.py (7438 bytes)
- J04/J04_EXPERIMENTAL.blend (186176 bytes)
- J04/J04_FINAL_solver_diagnostic.png (1369540 bytes)
- J04/J04_QA.json (9467 bytes)
- J04/generate_J04.py (6193 bytes)
- J05/J05_EXPERIMENTAL.blend (7794656 bytes)
- J05/J05_EXPERIMENTAL_full_tracery.glb (1403916 bytes)
- J05/J05_FINAL_profile_union_comparison.png (2268184 bytes)
- J05/J05_QA.json (3907 bytes)
- J05/J05_kernel_QA.json (2947 bytes)
- J05/export_paths.py (1001 bytes)
- J05/path_00.npz (15967 bytes)
- J05/path_01.npz (16000 bytes)
- J05/path_02.npz (15796 bytes)
- J05/path_03.npz (16159 bytes)
- J05/path_04.npz (16154 bytes)
- J05/path_05.npz (15815 bytes)
- J05/path_06.npz (863 bytes)
- J05/path_07.npz (36843 bytes)
- J05/path_08.npz (36069 bytes)
- J05/path_09.npz (874 bytes)
- J05/path_10.npz (1015 bytes)
- J05/path_11.npz (875 bytes)
- J05/path_12.npz (1012 bytes)
- J05/paths.json (222 bytes)
- J05/render_validate.py (6233 bytes)
- J05/robust_union.py (2014 bytes)
- J05/union_03.npz (45591 bytes)
- J05/union_13.npz (189832 bytes)
- J05/upload_J01_J05_archive.py (4648 bytes)
