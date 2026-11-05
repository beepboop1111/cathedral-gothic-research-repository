# F5ZP M01 — Axial Threshold Rib Connection R02 (EXPERIMENTAL)

Date: 2026-11-05. **Rib-only scope**: 90° third-ambulatory approach, deep axial threshold, axial chapel bays 1 and 2. No companion chapels, other ambulatory bays, walls, vault webs or buttresses. No changes to protected sources or generators. M01 remains open.

## Recovery and source limitations

MR COMPUTER was offline during this R02 modeling session. The previously recovered R21 exact axial rib-only Blender objects could not be reopened or included in the locally generated GLB. Source geometry used for the portable model was the **R15 archived GLB**, earlier than R21, from the attached `F5ZP_M01_R15_R20_Integrated_Chevet_EXPERIMENTAL.zip`. Exact preserved source subsets: one `R17_OUTER_DOUBLEAU_090` mesh, eight `R18_AXIAL_BAY1/2_RIB_*` meshes, two chapel boss meshes. The new connector meshes are explicitly named `TRIAL_*`.

R21 saved records report two axial approach boss elevations Z3966.0601 and Z4046.0601, but the exact R21 90° spline paths could not be compared in this run. This R02 model **is not a substitution for R21**.

## Experimental connection

- Longitudinal trial ridge crown stations (world X, Z): (26898,3550), (28000,3750), (28600,3750), (29800,4150), (32200,4400), Y=0.
- A piecewise cubic smoothstep makes the ridge continuous and C1 at every station; zero crest-coordinate error and max numerical central-difference slope below 0.000001 at interior join stations. Not necessarily C2 between segments.
- Two trial transverse threshold arches at X28000 and X28600: 2200 native-unit spans, spring Z2300, crown Z3750. The two-centered circular construction has rise1450 greater than halfwidth1100 and is monotonic. Arch cusps are intentional at Y=0.
- Original R15 axial chapel trial ribs, four per bay, **unchanged**: first-bay spring Z3300 and boss Z4150; second-bay spring Z3400 and boss Z4400.
- First-bay original R15 rib tangent at spring is ~55.17° from vertical and at boss ~70.79° from vertical; second-bay ~51.76° and ~66.22° respectively. The trial crown ridge does not imply tangent continuity across the multi-rib boss.
- New low-tier threshold arch springers are 1000 below first-bay chapel rib springers. A same-spring Z3300 monotonic two-centered arch spanning 2200 would require a crown of at least Z4400, **650 above** the trial Z3750 threshold and **104 above** reference middle crown Z4296. Neither option is architecturally approved. Actual stepped masonry bearing detail is missing.

## Technical QA

- Isolated GLB has 14 named objects: 11 meshes copied unchanged from R15 archive, plus 3 new trial rib meshes (one longitudinal, two transverse).
- All meshes watertight; GLB re-import object count matched.
- Six trial transverse spring endpoints and crown apex points were analytically validated (two arches each have two springers and one apex).
- The trial crest has zero numeric station error and C1 junction derivatives below tolerance.
- **No real masonry contact**, structural capacity, approved architectural profile, physical unit conversion, threshold clearance, or R21 source-spline intersection test established.

## Downloadable review package

`F5ZP_AXIAL_THRESHOLD_RIB_ONLY_R02_EXPERIMENTAL.zip` — GLB, source-reproducible Python generator, QA JSON, editable SVG diagrams, PNG previews, longitudinal curve path CSV, sources-and-limits README, and SHA-256 manifest. ZIP integrity checked.

**Next required evidence:** When MR COMPUTER is back online, reopen `F5ZP_AXIAL_APPROACH_RIBS_ONLY_R01_EXPERIMENTAL.blend` and validate exact R21 90° endpoints/tangents against the trial connector. Verify physical chapel entrance masonry faces before converting the dotted 1000-unit bearing-level difference into real masonry or responds. No source geometry or generators were modified.
