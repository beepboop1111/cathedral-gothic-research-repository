# F5ZP M01 — R22–R26 bounded continuation (2026-11-05)

**Status: EXPERIMENTAL. M01 remains OPEN. No architecture promoted, no source generator replaced.**

## Recovered and independently repeated result — R22

In the saved R21 B Blender checkpoint, the seven `R21_FRAME_EXP_R03_AMB_M_*` experimental V13 comparison objects reopened with **identity matrices**, despite R21's in-memory build comparing reflected geometry. A first read of the reopened scene therefore incorrectly returned zero comparator intersections and ~9,269-unit apparent separations; **that read is superseded and must not be used**.

R22 corrected the comparator **only in seven separate locally copied mesh objects**, baking its XY interchange into the copy's vertices (`x'=20213+y; y'=x-20213`, determinant −1). It did not change the original R03/V13 file, F5ZN-A, any R21 candidate web, or protected geometry.

In-memory R22 comparison: 14 outer webs, 7 corrected comparison webs, **15 intersecting object pairs, 222 triangle-pair intersection hits**; maximum sampled interface separation **145.6676025390625 native units**.

**Independent Blender 5.0.1 reopen repeated exactly 15 intersecting object pairs and 222 triangle-pair hits.** This fixes comparator checkpoint persistence, **not** the underlying experimental web mismatch. The V13 overlay is still a provisionally registered comparator, not approved reference masonry; we did not distort 14 vault webs to fit it.

MR COMPUTER native Blender file:  
`/home/christopher/Desktop/F5ZP_M01_R22_R26_EXPERIMENTAL_20261105/F5ZP_M01_R22_B_FRAME_CORRECTED_EXPERIMENTAL.blend`  
SHA-256 `ea6d97c8fc3018da0b144c7df82e318fbcac201053c136917634a0802fcd4511`.

The separate experimental scripts and both raw/independent QA JSON reports are saved beside that file.

## R23 chapel comparison — experimental recommendation only

Preserve candidate A (70°/90°/110°) and candidate B (50°/90°/130°). B is preferred for further architectural study because it respects the W–C–W–AXIAL C–W–C–W sequence and has **zero tested cross-chapel wall/cheek surface-intersection pairs** versus **nine for A**. The nine may include intended shared masonry; B's zero does not prove full-cathedral fit. No chapel-station selection approved.

## R24 receiving faces — BLOCKED

R21 showed 14 inward trial contacts with saved *preliminary, unapproved* R5285 pier-core solids, and 14 outward trial sweep contacts with proposed pads. There are **zero documented authentic approved masonry-bearing contacts**. The `CATHEDRAL_F5ZL_C_PHYSICAL_SUPPORTS.csv` schedule with 248 supports remains missing. Trial contacts are geometric evidence, not structural approval.

## R25 vertical and openings — OPEN

The trial third-ambulatory springing Z2300 remains 700 native units lower than protected AMB-M springing Z3000; supported vertical masonry junction still unresolved. R21 top web maximum Z4276.941 is only 19.059 below protected AMB-M boss/crown reference Z4296; this number does **not** prove physical clearance of real webs, gallery or windows. Actual seven passage openings, chapel threshold geometry, responds, roofs, buttress contacts and drainage remain unverified. No protected levels changed.

## R26 combined review — M01 NOT COMPLETE

Technical regression and read-only source recovery were carried forward, and R22's saved model was reopened. The source files remain hash-protected:

- F5ZN-A `/home/christopher/Desktop/newgen_F5ZN_A_CHEVET_STUDY_1to1.blend`: `d5ef438c269c99dc27052d26a1885f7965065d52ea51162cca4329d4419174bc`.
- V03 original experimental scene: `c1273df02f4a0c6d7db100169b184bef76227c6e0d1df1400951fc22d7fa6527`.
- R21 B linked source scene: `ab79eb0d7bf28b484057b3b9c27ca23fdc8886c05320e450a623331fd1186dff`.

Fourteen transition webs have prior R21 mesh-closure QA, not 14 structurally accepted Gothic vaults. Preserve working inner/middle ambulatory generator, Pass 6J, F5ZK-C, F5ZN-A, V13 source, exact 1:1 native project scale and discarded outer-ring decision.

**Completion gates still open:** approved inner/middle web interface authority, fourteen supported vaults, actual receiving face solids, chapel arrangement approval, seven real passages, 700-unit spring transition, gallery/window elevations, chapel roofs and flyers, whole-cathedral collisions, historical and independent structural validation. No claim of completion or approval is made.

A separate user-facing ChatGPT ZIP packages the status/QA source snapshots, diagnostic plot, R21 baseline comparisons, gate matrix, and reproducible R22 comparator-frame script; the R22 native `.blend` itself is retained on MR COMPUTER and not in the ZIP.

**Do not treat the provisional GitHub governance file as geometry approval; do not modify the existing governance or approved branches.**