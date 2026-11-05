# F5ZP M01 — R27 receiving-pier study
2026-11-05 · EXPERIMENTAL · M01 OPEN · No architectural promotion

## Result
Wall-engaged masonry remains the preferred next research candidate. Six proposals follow the actual R21 B connector-wall axes, contain the twelve affected outer rib spring points, and preserve the nine measured passage sections. T-derived crossheads also fit those limited checks, but their extra masonry has no demonstrated structural justification. Six detached proposals clear the tested wall/pad footprints after relocation; none receives the existing rib spring points directly. They require a separately justified transfer/flyer arrangement.

These are geometric fit findings for experimental surfaces. They are not approved bearings, masonry bonding, historically reconstructed profiles or structural-capacity findings.

## Baseline and authority
- Read the GitHub Master Reference on cathedral/governance-r01, blob 1d7e358ff7562fcc64088854baa2abd3d31a729e. It remains provisional governance.
- Parent: /home/christopher/Desktop/F5ZP_M01_R21_EXPERIMENTAL_20261105/F5ZP_M01_R21_B_PORTABLE_EXPERIMENTAL.blend.
- Arrangement B: companion chapels 50° / 130°, axial 90°. Arrangement A is preserved and not edited.
- Newly discovered R22/R26 review files were inspected. R22's persistently corrected V13 comparator still reports 15 intersecting object pairs and maximum interface distance 145.6676025390625. Those diagnostics remain separate; no comparator was used to drive receiver setout, and no inner/middle vault fit is asserted.
- Coordinate system: X east, Y north, Z up; chevet center (20213,0); azimuth clockwise from +Y.
- 1:1 project-native values. Metres/native unit and physical compliance thresholds remain undocumented.
- Original R21 object geometry/matrices matched their signatures before save; protected source files matched SHA-256 before/after. Historical originals, working generators and Pass 6J were not modified or executed. Discarded outer ring not reinstated.

| Protected source | SHA-256 before and after |
|---|---|
| /home/christopher/Desktop/F5ZP_M01_R21_EXPERIMENTAL_20261105/F5ZP_M01_R21_B_PORTABLE_EXPERIMENTAL.blend | 69cb086540450358b159d44f9df2d31fc0e00f9605a2bffea6b20a5a8815b881 |
| /home/christopher/Desktop/newgen_F5ZN_A_CHEVET_STUDY_1to1.blend | d5ef438c269c99dc27052d26a1885f7965065d52ea51162cca4329d4419174bc |
| /home/christopher/Desktop/F5ZP_M01_R15_R20_EXPERIMENTAL_20261105/F5ZP_M01_R15_R20_EXPERIMENTAL_V03.blend | c1273df02f4a0c6d7db100169b184bef76227c6e0d1df1400951fc22d7fa6527 |

## Isolated change and assumptions
Only eighteen new receiver solids were added, in three independently selectable proposal collections. Existing trial pads and walls are retained; overlapping additions are deliberate fit-study volumes, not boolean-unioned or construction-ready bonded masonry.

Six landing stations: 40°, 60°, 80°, 100°, 120°, 140°. They flank the three trial chapel thresholds. The outermost 20° / 160° landing stations and the complete fourteen-vault bearing topology are outside this bounded study.

Receiver axes are calculated from actual connector-wall mesh coordinates by principal-axis analysis and oriented outward. Landing-pad widths are measured from their saved meshes.
- Stem width = 0.75 × measured pad width.
- Outward stem length = 2 × measured pad width; inward overlap = 0.35 × pad width.
- Crosshead outer width = 1.5 × pad width; widened solely toward the exterior recess. This is a T-derived, asymmetric adaptation, not a traced historical T.
- Receiver top Z3900 is an explicit trial assumption. It is not a recovered flyer-thrust landing.
- The first centered prototypes reduced passage widths. Final proposals move the added breadth to the recess side; the discarded first prototypes are not authoritative.
- Detached footprints are shifted outward from the passage until their plan polygons no longer intersect the tested wall/pad footprints. This is geometric siting, not an architectural site selection.
- No high-vault thrust endpoints, approved F5ZL-C supports or calibrated flyer sections were recovered. No new flyer was fabricated.

Historical analogy comes from the supplied R02 comparison: Viollet-le-Duc IV p309 fig15 (radial apse), IV p313 fig18 (T-shaped section), Ungewitter I p219 (wall-buttress studies), II p109 (intermediate piers). R27 visually reviewed the supplied nine-plate contact sheet. No plate dimensions were scaled into the cathedral; no new historical arc reconstruction or translation is claimed.

## Measured results

| Check | Wall-engaged | T-derived | Detached |
|---|---:|---:|---:|
| New receiver solids | 6 | 6 | 6 |
| Existing affected rib springs inside proposal volume | 12/12 | 12/12 | 0/12 |
| Actual rib sweep / proposal surface intersections | 12/12 | 12/12 | 0/12 |
| Receivers intersecting saved connector-wall surfaces | 6/6 | 6/6 | 0/6 |
| Tested passage widths reduced, final fit | 0/9 | 0/9 | 0/9 |
| Receiver / chapel-roof surface intersections | 0 | 0 | 0 |
| Reimported local-context GLB mesh objects | 44 | 44 | 44 |
| Maximum GLB world-bound discrepancy | 0.00390625 | 0.00390625 | 0.00390625 |

All eighteen receiver meshes have zero nonmanifold edges by edge-incidence test. The full saved native R27 file reopened with eighteen receivers. Local-context GLBs were exported/reimported in Blender 5.0.1, tolerance 0.02 native unit; maximum measured bound discrepancy 0.00390625. This tests the local-context exports, not every object in the full-assembly GLBs.

### Passage section widths
Sections are at Z1500, depths 0, 500 and 1000 from each pad-center chord, perpendicular to the derived passage axis. Values below round for display; CSV/JSON retain numerical results. All final alternatives give the same measured width as the saved trial baseline at these sections.

| Chapel | Depth 0 | Depth 500 | Depth 1000 |
|---|---:|---:|---:|
| NORTH | 1994.474 | 2062.058 | 1923.324 |
| AXIAL | 1994.474 | 2145.430 | 2094.882 |
| SOUTH | 1994.474 | 2062.058 | 1923.324 |

The minimum sampled width is 1923.3235884172636 native units. No physical accessibility or minimum-clearance compliance claim follows. This is a nine-section result, not a continuous passage sweep or a seven-threshold clearance certificate.

### Roof and vertical limitations
BVH tests found no receiver intersections with the retained chapel roof meshes. Upward rays from receiver footprint vertices/centers do not encounter roofs over the wall-engaged proposals; this exposes missing vestibule roof coverage in the trial context, not a completed roof junction. Some detached sites have sampled roof coverage; individual distances appear in R27_MEASUREMENTS.json. No whole roof envelope, gallery/window or drainage pass is claimed.

Protected inner spring Z3000 and trial outer spring Z2300 remain unchanged: the 700-unit difference is unresolved. Receiver top Z3900 does not resolve it.

## Validation classes and open gates
- Technical: procedural build, native reopen, local-context GLB round trip and local review-scene generation completed.
- Geometric: receiver topology, actual rib contacts, wall surface intersections, sampled passage sections and roof surface diagnostics completed within the stated scope.
- Architectural: OPEN. Trial contacts are not approved receiving masonry; four-bearing topology and all fourteen actual vault connections remain unresolved.
- Historical: analogy only, not a calibrated reconstruction.
- Structural: not assessed. Masonry bonding, thrust lines, eccentricity, foundations and capacity remain unresolved.
- F5ZL-C support schedule, exact approved working-generator identity, whole-cathedral context and M01 acceptance remain OPEN.

## Deliverables
Download package:
- R27_RECEIVERS_LOCAL_CONTEXT_EXPERIMENTAL.blend: editable lightweight review of source wall/pad meshes and eighteen proposals. Toggle the three R27 collections one at a time. It intentionally omits cathedral vaults, roofs and other assembly parts.
- Three R27_*_LOCAL_CONTEXT.glb files: six proposals per variant with the exact selected source wall/pad meshes.
- Measured SVG/PNG plan comparisons, landing coordinates, passage CSV, QA JSON, procedural build/validation/review scripts.
- This report and SHA256SUMS.txt.

Full assembly on MR COMPUTER:
/home/christopher/Desktop/F5ZP_M01_R27_RECEIVERS_EXPERIMENTAL_20261105
- F5ZP_M01_R27_B_RECEIVERS_EXPERIMENTAL.blend: original R21 B context plus separately selectable proposal collections; engaged shown by default.
- R27_B_ENGAGED_EXPERIMENTAL.glb, R27_B_T_PLAN_EXPERIMENTAL.glb, R27_B_DETACHED_EXPERIMENTAL.glb: full-context exports. These were generated; their entire full-context contents were not independently round-tripped.
- This is separate from all protected baseline files.

## Reproduction
On MR COMPUTER with Blender 5.0.1:
1. blender -b --python build_r27.py
2. blender -b --python /home/christopher/Desktop/F5ZP_M01_R27_RECEIVERS_EXPERIMENTAL_20261105/verify_r27.py
3. blender -b --python /home/christopher/Desktop/F5ZP_M01_R27_RECEIVERS_EXPERIMENTAL_20261105/check_rib_contacts.py
The validators must be copied beside the saved R27 study or run from their existing MR paths. Source paths are pinned in the scripts; original source files are dependencies, not embedded in this lightweight package.
For portable review: run create_portable_review.py in Blender with the three supplied local-context GLBs; make_review.py uses NumPy/Matplotlib to regenerate drawings.

## Next bounded work
Resolve the real high-vault thrust/receiving-face evidence and vestibule roof junction before drawing flyers or sizing structural receivers. Continue the wall-engaged option as a research candidate; no approval or baseline change is requested by this checkpoint.
