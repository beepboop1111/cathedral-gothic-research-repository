# F5ZP M01 — RIB-ONLY RECOVERY R01 (EXPERIMENTAL)

Date: 2026-11-05
Status: recovered and technically verified; M01 remains OPEN. This record does not authorize or approve modifications to existing ribs, webs, piers or moulding generators.

## Source objects extracted without regeneration

- R22 saved baseline: `/home/christopher/Desktop/F5ZP_M01_R22_R26_EXPERIMENTAL_20261105/F5ZP_M01_R22_B_FRAME_CORRECTED_EXPERIMENTAL.blend`, SHA-256 `ea6d97c8fc3018da0b144c7df82e318fbcac201053c136917634a0802fcd4511`.
- Earlier R21 B linked experimental scene preserved, and R22 made no changes to R21 rib objects.
- New third-ambulatory R21 geometry: 28 ogive curves; 7 crown ridges; 7 inward arches; 14 boss meshes. Exactly 56 objects.
- Separate middle-ambulatory source: `/home/christopher/Desktop/newgen_F5ZN_A_GOTHIC_POINTED_ARCH_RIB_TRIAL_1to1.blend`, SHA-256 `f455a9a88727dae3bcf4b3777dfd1c604587e547a26d8153ae61810816b31d7d`.
- Recovered middle reference: 28 ogive curves; 8 doubleau curves; 7 trial boss markers (43 objects). Reference objects are not promoted or changed.
- Protected chevet scene: `/home/christopher/Desktop/newgen_F5ZN_A_CHEVET_STUDY_1to1.blend`, SHA-256 `d5ef438c269c99dc27052d26a1885f7965065d52ea51162cca4329d4419174bc`.

## Verified numerical tests

- 99/99 recovered Blender objects match saved source object geometry and transforms exactly, including curve spline point data and bevel attributes. The independent check reopened the source files.
- 28/28 R21 ogives terminate on their intended trial boss center points at stored precision; 7/7 ridges connect the paired trial bosses exactly.
- Ogive inner spring Z3000 (14), outer spring Z2300 (14); trial radial endpoints span R5285–R6685 project-native units.
- New R21 curve bevel depths: ogives 31, ridge 24, entrance arch 38. F5ZN-A middle rib trial bevel depths: ogives 23, doubleaux 28. Simple circular tube bevels are **not** historic Gothic profile validation.
- Isolated new rib GLB reimport: 56 meshes, 37,534 vertices. Reference GLB reimport: 36 meshes, 23,364 vertices. Seven source trial boss EMPTY markers are in Blender checkpoint only.
- No approved real masonry contacts verified, and the F5ZL-C physical supports schedule remains missing.

## Deliverables on MR COMPUTER

Directory: `/home/christopher/Desktop/F5ZP_M01_RIB_RECOVERY_R01_EXPERIMENTAL`

- `F5ZP_RIB_ONLY_R21_WITH_MIDDLE_REFERENCE_R01_EXPERIMENTAL.blend` — editable, source separated collections.
- `F5ZP_R21_RIBS_ONLY_R01_EXPERIMENTAL.glb` — standalone new third-ambulatory rib network.
- `F5ZN_A_MIDDLE_RIB_REFERENCE_R01.glb` — separate middle reference.
- `RIB_PATHS.json`, `RIB_ENDPOINTS.csv`, `RIB_RECOVERY_QA.json`, `SOURCE_GEOMETRY_EXACT_MATCH_QA.json`, `GLB_REIMPORT_QA.json`, `README_RECOVERY.md`, and procedural QA scripts.
- `F5ZP_M01_RIB_RECOVERY_R01_EXPERIMENTAL.zip`: verified ZIP integrity, SHA-256 `76d0f6e23b58a254e23dd1b0385c52b233e1ec4c538a9231c6d966d63bda1334`.

These files were saved on the authorized computer; this GitHub commit records the experimental checkpoint but does not include the binary models.

## Next isolated rib-only investigation

Evaluate springing tangent directions and cusp/boss curvature, check 14 interbay rib junctions against the saved middle-ambulatory profiles, and identify the exact profile source before attempting to replace circular tube bevels with approved moulding sweeps. Keep geometry unchanged until regression tests and design review. No vault web or chapel modeling in this pass.

Architectural, historical and structural validation remain OPEN. Original generator and Pass 6J records remain protected, and the discarded outer-ring decision remains in force.
