# Cathedral F5ZP M01 — R21 architectural integration review

**Date:** 2026-11-05, America/New_York.  
**Status:** EXPERIMENTAL / M01 OPEN / NO GEOMETRY PROMOTED.

R21 recovers V03, compares two complete three-chapel candidates, and tests fourteen transition web bodies against saved inner/middle reference stations. It corrects a demonstrable experimental setout mismatch without moving the protected geometry. It does **not** establish fourteen architecturally supported Gothic vaults.

## Outcome and recommendation

**Retain B (outer stations 50° / 90° / 130°) as the recommended candidate for architectural review.** The recovered F5ZN-A floor-plan checkpoint records W–C–W–AXIAL C–W–C–W. B preserves that ordinal sequence and separates the companion chapel masonry from the axial chapel in the tested assembly. A (70° / 90° / 110°) remains useful as the earlier grouped entrance-junction experiment; it has nine cross-chapel wall/cheek intersection pairs, some associated with intended shared junctions. Those pairs are not nine proven accidental solid-volume collisions, and a zero count for B is not a whole-cathedral collision pass.

Both candidates are retained. No chapel station choice, new bearing, altered trial web height, or R21 frame operation is approved by this report.

## Recovered baseline and protection

| Record | Verified state / scope |
|---|---|
| Continuation Handoff R02 | Read HANDOFF.md and included R15–R20 portable package. Native V03 is distinct from the earlier portable GLB. |
| Native V03 | MR COMPUTER: `/home/christopher/Desktop/F5ZP_M01_R15_R20_EXPERIMENTAL_20261105/F5ZP_M01_R15_R20_EXPERIMENTAL_V03.blend`; 193 scene objects, 15 linked reference objects; SHA-256 `c1273df02f4a0c6d7db100169b184bef76227c6e0d1df1400951fc22d7fa6527`. Reopened read-only. |
| Protected F5ZN-A | `/home/christopher/Desktop/newgen_F5ZN_A_CHEVET_STUDY_1to1.blend`; SHA-256 `d5ef438c269c99dc27052d26a1885f7965065d52ea51162cca4329d4419174bc`. No write. |
| Saved preliminary rib/pier trial | `/home/christopher/Desktop/newgen_F5ZN_A_GOTHIC_POINTED_ARCH_RIB_TRIAL_1to1.blend`; SHA-256 `f455a9a88727dae3bcf4b3777dfd1c604587e547a26d8153ae61810816b31d7d`. Contains actual saved polygonal core/shaft massing at R5285, but its own manifest labels the piers preliminary and historically unapproved. It is not F5ZL-C. |
| GitHub Master Reference | Recovered from `beepboop1111/cathedral-gothic-research-repository`, `cathedral/governance-r01`, `cathedral/governance/CATHEDRAL_MASTER_REFERENCE.md`; blob `1d7e358ff7562fcc64088854baa2abd3d31a729e`. Provisional governance compilation, not model approval. |
| R15–R20 GitHub checkpoint | Recovered from `cathedral/experimental/f5zp-m01-r15-r20-20261105`; its M01 architectural gate remains open. |
| Working generators and Pass 6J | Existing files inventoried and hashed in `PRESERVED_GENERATOR_AND_PASS6J_INVENTORY.json`; none executed, rewritten or replaced. The exact identity of the previously reported approved inner/middle working generator remains unverified; the recovered V13/recovery scripts must not silently replace it. |
| F5ZL-C physical supports | Still missing. Read-only search of Desktop/Downloads/Documents and 118 ZIP archives found no named F5ZL-C/physical-support schedule. This is a bounded search, not proof no other copy exists. No 248-support reconstruction was invented. |
| Complete cathedral context | G40 working scene was inspected read-only. Its mixed component frames and incomplete applicable chevet masonry do not support a whole-cathedral clearance pass. |
| Discarded outer ring | Not reinstated. R21 retains only the separate trial third-ring outer extent 6685. No historical outer-ring vault geometry was linked or regenerated. |

## Units, identities and the actual setout problem

Work remains in project-native 1:1 units. Physical metres/native unit, Minecraft conversion, LittleTiles grid and voxel pitch are not inferred. World X east, Y north, Z up; chevet center (20213, 0); architectural azimuth clockwise from +Y.

The locked seven outer identities 30°, 50°, 70°, 90°, 110°, 130°, 150° remain unchanged. The **actual saved inner/middle** reference stations are a different nonuniform schedule:

| Ordinal bay | Saved inner boundary angles | Saved inner center | Trial outer center |
|---|---|---:|---:|
| A1 | 0.5°–27.5° | 14° | 30° |
| A2 | 27.5°–53.5° | 40.5° | 50° |
| A3 | 53.5°–78° | 65.75° | 70° |
| A4 | 78°–102° | 90° | 90° |
| A5 | 102°–126.5° | 114.25° | 110° |
| A6 | 126.5°–152.5° | 139.5° | 130° |
| A7 | 152.5°–179.5° | 166° | 150° |

The handoff's regular 20° third-ring bays cannot simply be treated as the same bearing stations as the saved inner/middle bays. This report preserves that authority distinction; it does not supersede a user lock. In V03, inward landing points were 79.077–1046.964 native units from the nearest saved preliminary core **surface** (approximately 184–1151 from core centers). R21 tests a transition between these two setouts rather than moving protected piers or using very large invented receiving pads.

## Precisely what changed

1. The original V03 experimental ring webs, ribs, bosses, ridges, inward arches and inner pads remain geometrically unchanged in `90_V03_UNMODIFIED_RING_ARCHIVE_HIDDEN`. V03 on disk remains unchanged.
2. Fourteen new trial web bodies interpolate from the unchanged trial outer ring to the **saved preliminary** R5285 chordal pointed-arch polylines. The V03 trial web height field is reused, with an inner-edge correction that decays to zero at the outer edge. This changes only experimental web coordinates. It is an analytic interpolation experiment, not a historical vault construction method or a validated generator replacement.
3. The 28 spring-to-boss rib paths and 14 boss positions follow that trial surface. Two explicit rib branches per half-cell are retained. Four independent masonry bearings per half-cell are **not demonstrated**. Adding branches by assumption would not resolve that architectural question.
4. Original outer pads, outer entrance arches, axial chapel walls and two axial sanctuary webs remain unchanged. Candidate A keeps all original chapel placements. Candidate B rotates only the experimental north/south chapel assemblies, including their connector cheeks, by −20°/+20° about the chevet center. No protected object moves.
5. Saved preliminary R5285 arch curves and pier solids are linked as evidence in the working files, and copied with provenance into portable files. Evidence copies remain unapproved.
6. The older R03 V13 registration was found to use +X counterclockwise azimuth while the saved guide uses +Y clockwise. R21 applies `x_out = 20213 + y_in; y_out = x_in − 20213; z_out = z_in` to **comparison instances only**. This XY interchange has determinant −1; it is an explicit experimental reflection, not a rigid rotation. The original V13 source, registered source file and protected generator remain untouched. No conclusion that the original V13 webs are wrong follows from an error in this experimental overlay.

## Measured validation

| Class | Test actually performed | Result and limitation |
|---|---|---|
| Technical | Open V03 and sources in Blender 5.0.1; save/reopen two native R21 candidates | Passed. Each portable scene has 328 objects; all scene objects and their geometry data are local. |
| Technical | Export/reimport each GLB | 228 mesh objects each; maximum world-bound discrepancy A = 0, B = 0.00048828125 native units. Native files require Blender 5.0.1 or compatible newer version; local Blender 4.3.2 could not read the newer native header. |
| Geometric | Fourteen candidate web bodies: edge incidence, winding, triangle area and signed volume | 14/14 closed, zero nonmanifold edges, zero winding conflicts, positive volume; minimum tested triangle area 773.513 square native units. This result does not cover every roof/wall mesh in the assembly. |
| Geometric | Shared web edge vertices | 13/13 adjacent half-cell interfaces coincide; maximum measured delta 0 native units. |
| Geometric | Plan-grid Jacobian sign | No sampled plan-cell folding in any of the 14 trial web grids. Not a general self-intersection proof for every assembly member. |
| Geometric | Candidate inner web boundary against saved trial arch | Analytic boundary residual = 0 at tested source knots. The target is a preliminary saved arch, not an approved V13 surface. |
| Geometric | 28 rib centerlines against their web meshes | Maximum sampled nearest-surface distance 3.320135 native units, below trial sweep radius 31; intersection diagnostics retained. Exact moulded rib/web interface construction remains unresolved. |
| Geometric | 14 inward rib spring points against saved preliminary core top surfaces | 14/14 at zero point-to-surface distance; swept ribs intersect saved core surfaces. This is evidence of contact with **trial solids**, not authentic approved masonry. |
| Geometric | 14 outward rib sweeps against retained trial pads | 14/14 have pad-surface intersections. Trial pads remain unapproved. |
| Geometric | Preliminary pier silhouettes to outer trial-pad envelope | Conservative annular radial reservation 1065.884 native units (radii 5390.858 to 6456.742). Actual floor, door, stair, jamb and accessibility clearances are not established. |
| Geometric | Cross-chapel wall/cheek surface intersections | A: 9 object pairs; B: 0 in tested wall/cheek subset. Shared-junction classification and masonry bonding in A remain unresolved. Roofs, flyers, the entire cathedral and volumes are outside this count. |
| Geometric | Frame-corrected provisional R03 web comparison | 15 candidate/reference web pairs have surface intersections (222 triangle-pair hits). Seven inward arch curves also have sampled nearest-surface gaps up to 145.668 native units. No approved-web fit pass. |
| Architectural | Seven inward/outer thresholds and fourteen supported vault connections | OPEN. Trial arches and surfaces are present; authentic jamb cuts, four-bearing topology and approved receiving-face schedules are not verified. |
| Historical | Gothic web construction, rib profile provenance, chapel type | Not validated in R21. No historical approval inferred from analytic interpolation or an attractive render. |
| Structural | Masonry load path, eccentricity, thrust, compression capacity, buttresses/flyers and foundations | Not validated. Contact/intersection and closed meshes do not establish capacity or stability. |

Maximum candidate third-ring web top is Z4276.941. Candidate boss heights vary by bay: A halves Z3966.060–4025.864, B halves Z4046.060–4105.864; original trial targets were Z3900/Z3980. These changes are experimental and explicitly dependent on the inner-edge fit. The protected spring Z3000, boss reference Z4296, upper-web reference Z4394 and lower gallery floor reference Z4521 are unchanged. Their elevations alone do not prove gallery or window clearance. The trial outer spring remains Z2300, retaining the unresolved 700-unit spring difference.

## M01 gates and approval requirements

| Gate | Current decision | Evidence or decision still required |
|---|---|---|
| Recover and protect V03 / F5ZN-A / governance | PASS within recorded scope | Hashes and read-only recovery recorded. |
| Two three-chapel alternatives compared | REVIEW COMPLETE; selection UNAPPROVED | B recommended; user architectural selection required before baseline adoption. A preserved. |
| Real masonry bearing authority | OPEN | F5ZL-C or an independently identified approved receiving-face model; preliminary cores cannot substitute. |
| Working inner/middle generator authority | OPEN | Locate producer, parameters, original validation outputs and the actual saved working generator without rebuilding it. |
| Fourteen actual architectural vault connections | OPEN | Confirm intended support topology and reconcile candidate arches, webs and approved middle-ambulatory interfaces. |
| Seven actual inward passages and chapel thresholds | OPEN | Installed wall/jamb polygons, opening cuts and circulation evidence for all seven stations. Only three chapel bodies are developed here. |
| Vertical / gallery / windows | OPEN | Resolve the spring-level transition and actual permitted aperture/gallery envelopes. Rejected paired-entrance/upper-window constraints are not reinstated. |
| Chapel roofs, vestibule webs and drainage | OPEN | Axial section exposes the undefined ambulatory-to-sanctuary vestibule roof/web transition. Inherited roof fans and trial buttresses are retained; no drainage or structural sign-off. |
| Full-cathedral collision / registration | OPEN | Complete applicable adjoining masonry and approved web frame required. G40 and R03 comparator inspection are not substitutes. |
| Historical and structural validation | OPEN | Traceable historical construction evidence and independent structural assessment. |
| M01 completion and promotion | NOT AUTHORIZED / NOT SATISFIED | Close architectural gates first; explicit user approval is then required. No acceptance request is implied by this report. |

## Deliverables and reproduction

- `F5ZP_M01_R21_A_PORTABLE_EXPERIMENTAL.blend` and `...B...blend`: editable Blender 5.0.1 candidate scenes, with unchanged V03 ring archive and provenance-tagged source snapshots. The provisional V13 comparator collection is hidden by default.
- Matching `...A_EXPERIMENTAL.glb` and `...B_EXPERIMENTAL.glb`: selected active candidate geometry, excluding the archived prior ring and hidden V13 comparator. Treat all trial and evidence objects according to their labels.
- Matched isometric renders with chapel roofs hidden for inspection; plan comparison, axial section, bearing/web-fit drawings in SVG/PNG, 14-row connection CSV, QA JSON and protected source hashes.
- `build_r21_transition.py`: full procedural build on MR COMPUTER from the pinned original files. It never executes the protected vault generators. Its original source paths and hashes are intentional dependencies; this is not a claim of a source-free rebuild from a ZIP alone.
- `validate_r21_blender.py`, `check_outer_contacts.py`: independent saved-file checks using Blender 5.0.1. Run beside the packaged portable scenes; paths resolve relative to the scripts.
- `export_portable_checkpoint.py`: export a fresh GLB directly from each packaged native checkpoint, without needing linked source files. Both reexports matched the delivered GLB SHA-256 exactly in Blender 5.0.1. Identical binary bytes are not promised across export environments. See `R21_FINAL_REGRESSION.json`.
- `make_review_drawings.py` reads the supplied source audits and measured QA. It requires NumPy, SciPy and Matplotlib. It is a review drawing pipeline, not a geometry generator.

Completed commands: native build; independent reopen/export validation; supplemental outer contact measurements; matched Blender rendering; procedural review drawings. Protected source hashes match before/after. Existing validated generators were not rerun.

**Next work:** resolve the source authority and real receiving masonry, then coordinate the selected chapel arrangement and the vestibule/web transition against those sources. Do not repair experimental comparisons by altering protected geometry. If the actual approved supports remain unavailable, receiving alternatives must be developed as proposals and reviewed explicitly.

**Execution-setting note:** GPT-6 at High was requested. The assistant could not programmatically switch or verify the session model/thinking selector; no claim that this setting was applied is made.
