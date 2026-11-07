# V19 R02 — 15-vault connected network — EXPERIMENTAL

Prepared November 6, 2026 (America/New_York).
This is a synthetic kernel and live-editing test, not an approved cathedral arrangement.

## Baseline and protection
The V19 R01 two-vault experiment remains unchanged at:
 /home/christopher/Downloads/F5ZP_V19_CONNECTED_SKELETON_EXPERIMENTAL
Its kernel v19_core.py was copied byte-for-byte, not replaced. R01, V18 V04 and the R07/R12B/R14/R15/R18 source paths covered by PROTECTED_HASHES.json passed hash checks.
F5ZK-C, F5ZN-A, the authoritative inner/middle generator, Pass 6J, and historical originals were outside this edit.
The GitHub Master Reference R01 was read; its governance entries remain provisional and are not an architectural approval.
F5ZL-C support schedule remains UNRESOLVED.

## Scope, units and geometry
- Native 1:1 numerical architectural test units; Z up, right handed. No display scaling or 1:16 conversion.
- These synthetic dimensions do not declare a physical meters-per-unit calibration.
- 15 irregular convex quadrilateral vaults in a 3-row x 5-column connected network.
- 38 unique boundary arches, of which 22 are shared by two vaults.
- Each shared arch has one authoritative registry record; no independently fitted duplicates.
- Selected shared arch: n3_1:n3_2. Both springing endpoints receive [45,-30,35] together.
- Independent boss coordinates, groins and normalized R12B-derived meridian amplitudes per vault.
- Webs are open intrados surfaces; the colored tubes show centerlines and are not masonry profiles.
- NETWORK_CONFIG.json contains exact node, arch and vault data. NUMERICAL_QA.json contains numerical results.

## Execution and use
On MR COMPUTER the working directory is:
 /home/christopher/Downloads/F5ZP_V19_R02_NETWORK_EXPERIMENTAL
Run:
 blender V19_R02_NETWORK_EXPERIMENTAL.blend --python network_workspace.py
Then open N sidebar > V19 Network.
Use the shared XYZ shift and per-vault crown / meridian fields. Automatic updates are debounced, validate the complete skeleton and plan partition first, and stage web meshes before replacement.
A failed geometric edit keeps the last valid displayed model. The field remains visibly invalid until corrected.
Unchanged web input signatures reuse existing mesh objects. A crown change is confined to one vault; a shared-node movement updates all incident dependents.
The supplied RUN_NETWORK_UI.py text can also register the panel after opening the blend, using the adjacent script files.
Save reviewed live edits as another experimental blend. Exports represent the packaged baseline, not subsequent unsaved edits.

Reproduce the packaged baseline on MR COMPUTER:
 blender --background --factory-startup --python-exit-code 1 --python network_workspace.py -- --batch
Verify it without rebuilding the complete network:
 blender --background V19_R02_NETWORK_EXPERIMENTAL.blend --python-exit-code 1 --python verify_network.py
Protected-source paths are intentionally machine-specific. Copying the folder elsewhere requires recovering the listed sources or an explicit documented protection-path remapping; do not silently disable the protection check.

## Evidence
- 61,440 web triangles at 32 subdivisions, plus separate illustrative skeleton tubes.
- Entire initial graph/preflight/web build: approximately 1.16 seconds in this run, excluding export, render and verification.
- All 15 analytic web boundary, groin, seam, meridian and boss residual checks passed.
- All shared mesh stations agree between neighboring webs (zero neighbor gap).
- Maximum actual float32 mesh station residual from analytic shared arch: about 0.000247321 native units; tolerance 0.002.
- Shared arch rigid-translation residual: about 4.55e-13 native units across 257 stations; identical span and curve translated.
- Positive signed XY triangle areas and disk topology verified for each web.
- 105 convex plan-pair separating-axis checks exclude overlapping web interiors; this is an open height-field argument, not a solid/masonry collision test.
- No-op update reused all 15 meshes. One crown edit generated only V01 and reused 14. Restore returned exact saved vertex hashes.
- Invalid crown was rejected; automatic callback scheduling and rejection preserved last valid meshes.
- Fresh Blender session loaded all 15 webs and registered the sidebar.
- GLB imported back into Blender: all 15 web coordinate sets and triangle counts matched; maximum bounds residual 0.
- One review image rendered and visually inspected. No redundant renders.
- Exhibit was not exposed in this session; inspection used Blender render and fresh Blender GLB import.
- UI float precision is preserved without turning unchanged values into needless cache misses.

## Validation categories
| Category | Result |
| --- | --- |
| Technical | PASS for procedural build, sidebar registration, update scheduling/rejection, fresh blend loading and GLB readback |
| Geometric | PASS within the analytic/sampled open-surface scope and recorded tolerances |
| Architectural | EXPERIMENTAL; synthetic set-out, not approved cathedral coordination |
| Historical | R12B meridian lineage retained; the 15-vault arrangement has no new historical validation |
| Structural | NOT ASSESSED; no thickness, loads, support capacity or roof model |

## Files and unresolved matters
The package includes Blender scene, GLB, one PNG, scripts, exact config, numerical QA, source hashes, logs and this handoff.
SOURCE_BASELINE_HASHES.json records original V19 R01 source bytes. OUTPUT_HASHES.json records delivered files before archive creation.
No approved generators were replaced and no experimental architecture was promoted.
Next bounded study: apply this registry and dependency mechanism to recovered, approved cathedral set-out in a new candidate, with the actual receiving geometry and roof limits; approval is needed for any change to locked architecture.
