Accompanying report, comparison drawings and audit scripts: [F5ZP_Package_Analysis_R01.zip](https://chatgpt.com/library?file_id=libfile_ffff90c8d0648191b3c918d63c2676e4&account_id=personal). Evidence paths below refer to that delivered bundle.

# F5ZP — Axial and eastern chapel package analysis R01

Date: 2026-11-05. Status: inspection findings only; all supplied chapel development remains EXPERIMENTAL. No geometry, generator or uploaded source was edited or regenerated.

## Assessment

Axial Chapel R03 is the most developed candidate for continued axial-chapel work. Its entrance, two rising vaulted bays and polygonal apse form a coherent spatial progression. It is not yet an architecturally coordinated cathedral connection. Eastern Chapels R01 is useful as a record of the three-chapel silhouette and outward-turning companions, but it must not be inserted unchanged beside R03. It uses a different frontage, lower trial elevations and a faulty pointed-arch routine. R02 remains a useful preserved entrance parent.

The next architectural task is to coordinate R03 against the actual saved middle-ambulatory vault and its receiving masonry before developing the companion junctions and buttress landings. Correct the identified mesh/code defects in a separate revision first.

## Evidence and authority

The three attached ZIPs passed fresh ZIP integrity checks. All contain byte-identical plan inputs, SHA-256 `066027d5fa0e673b5c267718e906d105c86272b6358fcc8bf2a33a5d3fa92a19`. R03's bundled parent QA exactly matches the supplied R02 QA (`eac9818dfe357f5eb44bf3c10c7ec44ddd8b21b00beb984490a0d14951b7de3f`). This establishes shared plan provenance and parent records; it does not approve their architecture.

The GitHub Master Reference was successfully read on `cathedral/governance-r01`, blob `1d7e358ff7562fcc64088854baa2abd3d31a729e`. It explicitly calls itself provisional. The current package checkpoint records the discarded-outer-ring decision. No live MR COMPUTER model or authoritative F5ZN-A 3D vault was inspected in this analysis. No independent claim of whole-cathedral regression protection is made.

Blender 4.3.2 opened the actual supplied R03 and R02 saved models. Fresh inspection counted 253 and 32 mesh objects respectively, with finite vertices and no zero-area polygon faces under the audit's 1e-9 area threshold. Existing PNGs were visually inspected: R03 cutaway and interior, and Eastern R01 exterior. The Eastern pointed function was extracted with Python AST and executed by itself with a point-capturing line function; the study was not rebuilt.

## Geometric compatibility

All dimensions below are native project units. Numerical 1:1 is retained; physical metres per unit remains unspecified.

| Quantity | Eastern Chapels R01 axial | Axial Entrance R02 | Axial Chapel R03 |
|---|---:|---:|---:|
| Entrance front X | 27274.291 approximately | 28000 | 28000 |
| Opening span parameter / clear opening | 1999.237 span parameter | 2200 clear | 2200 clear, freshly measured |
| Threshold/order extent | Four orders at 120 spacing; 360 between first/last planes | 600 total body depth | 600 between first/last order planes |
| Entrance spring Z | 1700 | 1800 | 1800 |
| Entrance intended soffit crown | 3050 parameter target; routine misses it | 3750 | 3750, freshly measured |
| Roof eaves Z | 2700 | Not modeled | 4100 |
| Roof ridge Z | 3200–3700 | Not modeled | 4500–5350 |
| Axial east plan limit X | 31474.291 approximately | Chapel absent | 34588.821 approximately |

R03 shifts the axial front east by 725.709 units and extends the chapel east by about 3114.530 units relative to R01. R01's span parameter excludes the beam/profile widths and is not a certified clear-opening measurement. Its companions retain the old T3/T5 outer-chord origins. These differences require a new coordinated set-out rather than a direct merge. R01 also generates lower-envelope slabs from old outer footprints; its outer geometry must remain reference-only under the discarded-ring decision.

R03's 600-unit threshold gives a clear compression before two bays of 2400 units each, with boss elevations 4150 and 4400 and apse boss 4550. Its arch/respond profile rows meet at springing, and the saved entrance is symmetric to floating-point precision. The overall depth and height progression are promising. The block-like cores and horizontal spring line remain conspicuous in the interior view; final compound-pier articulation, apse support orientation and masonry bonding still need architectural review. The designed profiles are new experiments, not historical U1/U4/U5/D traces.

## Findings requiring correction

### 1. Eastern R01 pointed arches fail their own crown construction

In `build_study.py`, `pointed()` uses `r = span - c` and a matching horizontal offset. For the stated construction, the radius/offset corresponding to its angle is `span/2 - c`. The executed supplied routine's branches therefore do not meet at the intended central apex. `line()` joins them with an additional beam segment across the gap.

For the axial entrance (span 1999.237, spring 1700, requested rise 1350), the left branch ends at Z3366.529 instead of Z3050. The next retained point on the right branch lies about 701.099 horizontal units away. The companion entrances produce approximately 713.945-unit bridges and branch-end Z3373.532. These are directly measured function outputs, not estimates from a render. All calls using this routine, including windows and schematic diagonals, need their own crown/continuity checks after correction. A finite-coordinate test cannot detect this error.

### 2. R03 shells have inconsistent face winding

The saved model contains inconsistent winding in all 20 web shells and all 13 roof shells: 33 affected objects, 2014 shared edges whose adjoining faces traverse the edge in the same direction. No edge with more than two incident faces was found; guides and glass sheets have boundary edges. Thus an object can have two faces per edge while its face orientations remain inconsistent.

The cause is visible in `shell()`: boundary edges are reduced to sorted vertex pairs, losing the directed triangle-boundary order used to orient the closing side faces. This can produce incorrect normals, shading/culling or downstream solid operations. It is a technical defect independent of the intended vault shape. Repair directed boundary winding in a new revision and rerun normal/orientation checks; do not treat the existing 18 passing QA flags as a comprehensive mesh certificate. The R02 model showed zero inconsistent shared-edge windings in this audit. Neither audit proves absence of self-intersection or structural adequacy.

### 3. Deliverable archives omit documented models/exports

R03's SHA256SUMS lists two absent files: `Axial_Chapel_R03_FULL.glb` and `Axial_Chapel_R03_ROOF_OFF.glb`. All 19 listed files that are present match their hashes. Its editable `.blend` is present and opens.

Eastern R01 contains neither `Eastern_Chapels_R01_EXPERIMENTAL.blend` nor `Eastern_Chapels_Context_R01.glb`, although its README describes them. Its bundled `inputs/context.glb` is the recovered source context, not the generated three-chapel study. Scripts, images and QA are present, so recovery is possible, but the supplied archive is not a complete editable study handoff.

R02 includes its documented `.blend` and GLB. No exports were regenerated during this analysis.

## Limits of the recorded QA

R03 records analytic boundary residual 4.54747e-13, profile/shaft residual 2.27374e-13, and sampled web-to-roof minimum clearance 221.752691 across 4700 samples. These are **prior recorded results**, not freshly rerun mathematical/export tests here. The fresh saved-mesh entrance measurements independently confirm 2200 clear, spring Z1800 and crown Z3750 (back crown stored at Z3923.328125).

The boundary tests compare each constructed analytic surface with its own prescribed boundary functions. They do not establish conformity with the saved F5ZN-A vault, welded shared tessellations or actual receiving masonry. The roof test samples webs, not every rib, boss, support or neighboring cathedral window/roof surface. Missing R03 GLBs prevent a fresh verification of its reported export round trip from the supplied exports.

Technical: ZIP integrity, saved-model opening, finite coordinates and face areas passed; R03 winding and archive completeness failed specified checks. Geometric: the measured R03 entrance is consistent with its retained dimensions; Eastern arch crown construction fails. Architectural: actual middle-vault elevations, support interfaces and companion joins remain unresolved. Historical: no plate-derived validation of these new profiles/webs is supplied. Structural: load paths, foundation/support capacities and flyer landings remain unverified; F5ZL-C support schedule remains missing.

## Recommended bounded continuation

1. Preserve all three supplied archives; use R03 as the next experimental axial candidate and R02 as its entrance reference, without promoting either.
2. Correct R03 shell winding in a separately named revision, export full/roof-off GLBs and verify the package includes its promised assets. Repair and validate Eastern R01's arch routine before reusing it.
3. Recover the actual saved M_A4/middle-ambulatory vault, spring elevations and receiving profiles. Overlay exact XY, spring/crown Z and masonry contacts against R03. Keep the working inner/middle generator unchanged; treat R03's trial ambulatory webs separately.
4. Develop companions and shared entrance walls around the reconciled axial interface. Then test roofs/drainage, neighboring windows, exterior recesses, buttress footprints and real flyer contacts. Keep unresolved bearing/capacity questions explicit.

No locked dimensions, approved architecture, original historical sources, Pass 6J records or authoritative generators were changed. This report does not promote experimental work.

## Reproduction and evidence

`evidence/MESH_AUDIT.json` contains per-object topology counts, bounds, source hashes and actual entrance measurements. `evidence/EASTERN_CURVE_AUDIT.json` contains the executed entrance curve coordinates. `evidence/INPUT_ARCHIVES.json` identifies the exact input ZIPs. `COMPARISON.svg` and PNG compare native-plan footprints and expose the generated crown bridge.

To rerun from this report folder, extract the original ZIPs into `analysis/axial_chapel_r03`, `analysis/eastern_chapels_r01` and `analysis/axial_entrance_r02` respectively. Preserve R02's internal `axial_entrance_r02/` folder. Run `blender -b -t 2 --python scripts/inspect_models.py` and `blender -b -t 2 --python scripts/check_eastern_curves.py`. Results go into `audit_work/`; no source file is saved or regenerated by either audit. Requires Blender with its bundled numpy. The included logs record the original executed inspection.
