# Gothic Tracery M02 / M03 — Checkpoint R03

**Status: EXPERIMENTAL — no promotion or generator replacement.**  
**Date:** 2026-11-05 project checkpoint label.  
**Scope:** Meaux precision-defect repair, four-window regression, and a parallel semantic face registry. No cathedral component was edited.

## Result

The Meaux reference was recovered and reproduced byte-for-byte before repair. The candidate has zero boundary edges, zero nonmanifold edges or vertices, zero duplicate faces, zero near-zero-area triangles, consistent winding, one connected closed solid, and no self-intersections detected by the independent full-mesh triangle predicate. STL and GLB exports were independently reloaded. The same checks pass for Haina 1264, Haina 1265, and Châlons.

Meaux's bounds remain **139.9436550140381 × 125.12198638916016 × 5.928667053580284 model mm**. The repair merges six near-coincident vertices and removes 18 collapsed triangles; maximum vertex movement is **0.0000095367431640625 mm**. It does not smooth, fill openings, remesh globally, change cleanup settings, or substitute a generator.

All 48 Meaux classified openings remain void: **40 enclosed apertures plus eight open-edge cutouts at the cropped base**. An opening count is not the genus of a cropped window. All 118 classified source openings across the four cases are preserved. Source maps are unchanged.

## Recovered baseline and provenance

- `originals/tracery_kit.zip` is the original user source bundle, SHA-256 `76ec8b247a028b93c05d6028772cc5f6b3546015803b0ec5c3d1881d92608d37`.
- `originals/kit/tracery_build.py`, SHA-256 `0d52ef4630a8234e59a83249e06cd1077479ad236db96f595998a11e44ef5e76`.
- `originals/kit/tracery_regions.py`, SHA-256 `667130b1e1c60cd05a9378e55acc702a5a7b55cd444c9b925df0f681d8d82e1c`.
- Meaux supplied final STL `originals/meaux_reference_R02.stl`, SHA-256 `b32116fb36a59217d6d47c5a7d07328776010e83ad32e0851fc6be4650517ba8`.
- Parent: Master Plan R01 + Runlog Reconciliation R02. The original kit command file omits `--res 0.25`; the recovered final run log establishes this setting. All four final baseline STLs now match the actual corresponding MR COMPUTER files byte-for-byte. The older variants were not selected by timestamp.
- MR COMPUTER final paths: `/home/christopher/Downloads/meaux(2).stl`, `haina_1264(1).stl`, `haina_1265.stl`, `chalons(2).stl`. Hashes, modification times and read-only mesh measurements are in `qa/remote_reference_inventory_R03.json`.
- GitHub governance read succeeded: `cathedral/governance/CATHEDRAL_MASTER_REFERENCE.md`, `cathedral/governance-r01`, blob `1d7e358ff7562fcc64088854baa2abd3d31a729e`. Its provisional architectural entries are not used as tracery dimensions.

These are authoritative **benchmark inputs**, not evidence that the original tracery meshes or the new candidates are architecturally approved.

## Scale, coordinates and settings

Historical plate calibration is **UNRESOLVED**. `--width 150` maps the full input image width to 150 nominal model mm; it does not force the stone's actual bounding width to 150 mm. The working source PNGs are processed crops, not preserved full historical pages with established metric scale. No cathedral 1:1 dimension or LittleTiles conversion was inferred.

- Source image: X right / Y down, image origin at upper left.
- STL: X right / Y up / Z out of the window face; right-handed, coordinates in model mm.
- GLB: same model orientation using glTF meters; positions are exactly converted by 0.001. Blender's importer converts glTF Y-up to Blender Z-up; the review scene applies the documented inverse object rotation to align the comparison plane. This review transform does not alter the exported models.
- Original mesh grid: 0.25 mm; nominal stone thickness 6 mm; both sides chamfered; edge width/depth 1.5 mm; drawn-line groove depth 0.4 mm; `--min-bar 1`, `--min-hole 3` unchanged.
- Source classifier: threshold 0.5, disk 16 px, minimum radius 40 px, maximum compactness 10, bridge reach 50 px, bottom-edge regions are not automatically marked outside (`--open-bottom` remains off). Mirroring unions ink with its reflection and remains an inherited experimental interpretation.
- Exact per-window source hashes, mirror axes, legacy overrides, effective defaults and commands: `BENCHMARK_MANIFEST_R03.json`.
- Architectural elevations, spring points, yaw and block-grid relationships: not applicable to this isolated nominal-scale benchmark.

## Decision ledger

| Property | Value / scope | Status | Evidence |
|---|---|---|---|
| Kit inputs and final STL references | Exact SHA-256-frozen inputs | DERIVED benchmark baseline | Original bundle, R02 log, MR COMPUTER hash matches |
| Repair method | Proximity clusters with original-coordinate representatives; candidate tolerance 0.00001 mm; actual transitive movement separately bounded | EXPERIMENTAL | Versioned repair script, every cluster and deleted face listed |
| Nominal scale and profiles | 150-mm image frame, 6-mm thickness, 0.25-mm grid, original chamfer/groove parameters | EXPERIMENTAL inherited settings | Original generator defaults + reconciled final command |
| Source openings | Meaux48 / Haina1264 21 / Haina1265 30 / Châlons19 | DERIVED classification counts | Unchanged source maps + independent mesh opening audit |
| Semantic IDs and corrections | Source-family-scoped normalized geometric IDs; guarded anchor replay | EXPERIMENTAL | Nine unit tests + four full-image benchmarks |
| Historical dimensions and moulding meaning | Not established by these crops or raster grooves | UNRESOLVED | No dimensional historical source or approved section supplied |
| Existing cathedral architecture and generators | F5ZK-C, F5ZN-A, working ambulatory generator and Pass6J untouched | LOCKED (protected, out of scope) | No operations in their geometry or generator locations |
| F5ZL-C support schedule | Missing support schedule remains unresolved | UNRESOLVED | No invented support data |
| Candidate approval | No promotion granted or implied | EXPERIMENTAL | Current user instruction |

## Authorized delta

| Target | Before | Candidate change | Necessary dependent outputs |
|---|---|---|---|
| Meaux exported topology | Six nonmanifold edges; seven near-zero-area faces | Precision-only welding and collapsed-face removal | Repaired STL, meter-correct GLB, numerical QA and matched views |
| Four-window regressions | Final recorded references | Same isolated precision repair as a regression experiment | Four paired models and source/mesh feature checks |
| M03 semantics | Fragile numeric flood-fill labels | Persistent face IDs, confidence/evidence, crop flags and guarded manual sidecars | Selectable SVG, JSON registry, previews and tests; maps unchanged |

## Mesh and geometric validation

| Window | Nonmanifold edges | Degenerate faces | Candidate triangles | Openings retained | Maximum section deviation mm |
|---|---:|---:|---:|---|---:|
| meaux | 6 → 0 | 7 → 0 | 1,138,006 | 48 (40 enclosed + 8 crop-connected) | 4.05427514e-07 |
| haina_1264 | 34 → 0 | 56 → 0 | 1,692,014 | 21 (17 enclosed + 4 crop-connected) | 1.99503955e-06 |
| haina_1265 | 6 → 0 | 10 → 0 | 1,577,570 | 30 (30 enclosed + 0 crop-connected) | 2.68670765e-06 |
| chalons | 0 → 0 | 4 → 0 | 662,704 | 19 (18 enclosed + 1 crop-connected) | 2.02713247e-06 |

Every repaired STL and GLB has zero boundary/nonmanifold edges, zero disconnected vertex fans, zero duplicate or degenerate triangles, consistent winding, one connected volume, and zero faces selected by the MeshLab self-intersection predicate. All actual STL bounds are unchanged. GLB and Blender import round-trip errors remain below the 0.0001-mm export budget.

Feature checks compare seven complete depth sections (Z=0.25/0.75/1.5/3/4.5/5.5/5.8 mm) and five longitudinal sections at 20/35/50/65/80% of model width. These include the raster cusp outlines and moulding/groove transitions. All section loop counts are retained. The metric is symmetric discrete Hausdorff over every section vertex to the nearest continuous section segment; it is not a continuous global surface-error proof. Maximum measured section deviation across the set is under 0.000003 mm. A local vertex-displacement ledger additionally bounds the repair.

`qa/mesh_regression_tests_R03.log` records ten tests, including a vertex-pinch case that passes edge incidence but must fail vertex manifoldness, a precision sliver, separated solids, overwrite protection, and full four-window evidence assertions. `qa/self_intersections_R03.json` records the full-mesh intersection predicate on originals, repaired STLs and independently reloaded GLBs.

Blender 4.3.2 imported all four candidate GLBs. `qa/blender_import_render_R03.json` records import counts and bounds. The STL importer discards some zero-area faces from the reference on import, so topology claims rely on the untouched STL in the separate numerical reader, not on Blender's cleaned import. The final matched views use Workbench studio/cavity technical shading of the actual meshes. No smoothing modifier was applied. Full reference/candidate montage and Meaux views were visually inspected. Exhibit was not exposed as an accessible review tool in this session; no Exhibit inspection is claimed.

## M03 semantic classification

M03 retains all original map pixels, with 19,683 selectable connected raster faces across the set. This large total includes tiny scan islands and is not a count of architectural panels. All 118 opening IDs remain stable under repeat/reordered labeling and exact nearest-neighbor 2× scaling. Manual corrections live in independent sidecars; source-family, anchor, shape, area, bounds and hole-topology guards reject ambiguous splits or merges.

Nine semantic unit tests and all four full-resolution semantic benchmarks pass. SVG/XML IDs match JSON records, and all four SVG exports were independently rendered in Inkscape. Ink and detached fragments remain uncertain; thin bands are provisional moulding candidates without inferred depth. The 2D semantic layer does not alter the existing 3D generation map.

## Deliverables

- `experimental/models/`: all four repaired `.glb` and `.stl` models; `meaux_M02_R03_REVIEW.blend` keeps the original reference hidden and the candidate visible, with cameras/materials.
- `baseline/models/`: exact original final STL reproductions, retained for comparison.
- `baseline/maps/`: exact classification maps and legacy numbered previews.
- `scripts/`: precision repair, feature comparison, intersection QA, meaningful regression tests, renderer, figure composition and one-command reproduction.
- `semantic/`: M03 source, tests, JSON registers, selectable SVGs, correction templates and comparison images.
- `comparisons/`: paired front/oblique renders, exact mesh-section overlays, Meaux comparison, four-window montage.
- `qa/`: detailed numerical evidence, frozen originals, environment versions and regression matrix.
- `SHA256SUMS_R03.txt`: checksums for the delivered checkpoint contents, excluding the checksum file itself.

## Reproduce

Use Python 3.12 and the pinned `requirements_R03.txt`. Blender 4.3.2 was used for the technical renders; Inkscape renders semantic SVGs when available. Font fallback is supported. The optional unavailable historical `diag.py` and `view/shot.js` are not required; this package supplies new, separately versioned review and QA scripts.

```bash
python3 -m pip install -r requirements_R03.txt
python3 scripts/reproduce_checkpoint_R03.py --output /absolute/path/new_Tracery_R03_run
```

The output directory must not exist. The command copies preserved inputs into a new experiment, reproduces original classifications and STL bytes, repairs, checks features and topology, tests semantics, renders matched views and creates the Meaux Blender review file. `--skip-renders` explicitly selects a numerical-only rerun and makes no Blender-render claim.

A second fresh numerical reproduction was executed during delivery; its outcome and model hash comparison are recorded in `qa/REPRODUCTION_VERIFICATION_R03.json`. Rendering was executed and verified separately on the delivered models.

## Limits and next bounded task

This is technical and geometric preservation against the recovered model. It is not historical compass-construction validation, architecturally approved tracery, calibrated full-scale stonework, CAD-quality arcs, or structural validation. The upstream raster, mirrored ink, gap bridging, 1-mm bar cleanup and scan-based groove interpretation remain inherited experimental assumptions. No topology repair can establish that every engraved line is an authentic moulding.

M04 can next reconstruct one measured sixfoil and one pointed arch from traceable historical samples, carrying these unchanged semantic face IDs and uncertainty flags forward. Promotion of any R03 method, parameters or model still requires explicit user approval.

## Fresh-chat handoff

Read this checkpoint, `BENCHMARK_MANIFEST_R03.json`, the frozen original hashes, and the detailed Meaux mesh/geometry reports. Resume from the **original final reference** for baseline comparisons and retain R03 as an experimental candidate. Do not choose older downloaded variants by filename or overwrite the original scripts. Do not change cathedral geometry or resolve unrelated governance conflicts by inference. Experimental GitHub branch: `cathedral/tracery-m02-m03-r03-20261105`, under `cathedral/experiments/tracery/M02_M03_R03/`; no main/governance architecture promotion.
