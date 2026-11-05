Delivered editable model, full and roof-off GLBs, previews and QA: [F5ZP_Axial_Chapel_R04_EXPERIMENTAL.zip](https://chatgpt.com/library?file_id=libfile_28f4b711c9c481918fa9e47bd7abad4d&account_id=personal).

# F5ZP Axial Chapel R04 — shell winding and exports

Date: 2026-11-05. Status: EXPERIMENTAL; technical repair validated, no architectural promotion.

## Scope and parent

R04 repairs polygon orientation in the actual saved R03 model and supplies its missing full and roof-off GLBs. The architectural model was not regenerated. The original R03 archive and `.blend` remain unchanged.

Parent: `Axial_Chapel_R03_EXPERIMENTAL.blend`, SHA-256 `ba63f8ee1f7527690ffab4a84110c1c9e249cb3ddafeba48a05f21367eabf61e`, from uploaded `axial_chapel_r03.zip` (SHA-256 `54d4c4175fd5ebb09af0d68e77354e90ae387eef0b2e898def0e45c1bd6a3c67`). The complete parent is separately preserved in that archive. Original R03 code, QA, checkpoint and input identity records accompany this package under `inputs/R03/`.

GitHub Master Reference was retrieved again from `cathedral/governance-r01`, blob `1d7e358ff7562fcc64088854baa2abd3d31a729e`. It remains provisional. No live MR COMPUTER inventory was needed or claimed for this isolated saved-model repair.

## Exact delta

- Corrected 1,184 polygon windings across 20 web shells and 13 roof shells. All 33 now have consistent winding, two incident faces at every shell edge and positive signed volume.
- Shared-edge winding inconsistencies: **2014 before → 0 after**.
- Corrected the experimental builder's `shell()` routine to retain directed boundary edges, then orient the closed shell outward. Unordered pairs now count edge incidence only.
- Exported `Axial_Chapel_R04_FULL.glb` and `Axial_Chapel_R04_ROOF_OFF.glb` from the corrected saved meshes.
- Added revision metadata and matched cutaway, interior and exterior studio previews.

No vertex coordinate, vertex count, face membership, transform, material assignment, smoothing flag, collection assignment or bounding box changed across any of the 253 mesh objects. Face direction is intentionally different in the repaired shells. The saved `.blend` was reopened and checked against the original geometry/property snapshots. Neither mesh welding nor architectural remodeling was performed.

## Retained geometry and scale

Native numerical 1:1; Blender X east, Y north, Z up. glTF exports use standard Y-up conversion and return to the same Blender coordinates. Physical metres per native unit remains unresolved; no display rescaling was applied.

| Measurement | R03 retained in R04 |
|---|---:|
| Entrance clear width | 2200 |
| Entrance spring Z | 1800 |
| Entrance soffit crown Z | 3750 |
| Stored entrance back crown Z | 3923.328125 |
| Entrance front/back X | 28000 / 28600 |
| Threshold depth | 600 |
| Ambulatory trial boss | X26700, Y0, Z3620 |
| Chapel bay 1 | X28600–31000; boss Z4150 |
| Chapel bay 2 | X31000–33400; boss Z4400 |
| Apse boss | X33850, Y0, Z4550 |
| Web vertical thickness | 45 |

The plan, profile JSON and dimension CSV bytes match R03. F5ZK-C/F5ZN-A approved architecture, the working inner/middle ambulatory generator and Pass 6J were outside this repair. The discarded outer ring was not reintroduced.

## Fresh validation

**16/16 checks passed**, recorded in `QA_R04.json`.

| Check | Result |
|---|---|
| All 33 shells closed, consistently wound and outward | Pass before export, after reopening, and after each applicable GLB reimport |
| All 253 mesh geometry/property snapshots retained | Pass; vertex arrays and unoriented face hashes identical |
| Corrected shell function against all 33 saved shell fixtures | Pass for topology/orientation; reconstructed vertical-offset coordinates within source float32 rounding |
| Finite coordinates / nondegenerate polygon faces | Pass |
| Actual saved entrance measurements | 2200 clear, Z1800 spring, Z3750 soffit |
| Full GLB round trip | 253 expected / 253 imported meshes; names and all oriented triangle signatures match |
| Roof-off GLB round trip | 240 expected / 240 imported meshes; names and all oriented triangle signatures match; no roof objects |
| World bounding-box error, both exports | 0.0 native units |
| Original R03 saved file hash | Unchanged |

Export triangle signatures compare every oriented world-space triangle at 0.001-native-unit quantization, independently of vertex ordering. Bounding boxes are compared directly. Closure/normal checks are per shell, not a claim that the complete architectural assembly is a boolean-unioned solid.

The shell-function fixtures derive intrados triangles and lower vertex rows from the saved model. Reconstructing their +45 top rows introduces at most 0.000244140625 units of existing float32 rounding; the fixture tolerance is 0.001. This is only a reconstruction check: **the repair does not replace or move any saved vertex**.

The prior R03 analytic web/shaft and sampled roof-clearance results are carried as historical evidence, explicitly labeled `prior_R03_checks_not_rerun`. They were not substituted for the fresh checks above. Three new R04 renders were visually inspected. No Exhibit integration was available; Blender rendering and actual GLB reimports provided the inspection evidence.

## Files and reproduction

Open `Axial_Chapel_R04_EXPERIMENTAL.blend` for editable collections. Use `Axial_Chapel_R04_FULL.glb` for the complete model or `Axial_Chapel_R04_ROOF_OFF.glb` to examine its vaults. `CUTAWAY.png`, `INTERIOR.png` and `EXTERIOR.png` are new R04 studio previews. `REFERENCE_R03_*` drawings are explicitly retained R03 reference drawings, not claimed as newly generated R04 drawings. Their measured geometry remains applicable because the vertices did not change.

`repair_and_export.py` is the executed saved-model repair/export/verification workflow. With Blender4.3.2:

```bash
blender -b -t 4 --python repair_and_export.py -- /absolute/path/Axial_Chapel_R03_EXPERIMENTAL.blend
```

Run in a working copy of this package. It reads the separately preserved R03 model, creates R04, renders, exports both GLBs, reopens the `.blend` and reimports both exports before writing `QA_R04.json` and `GEOMETRY_REGRESSION.json`. The command never saves to the source R03 path. `REPAIR_EXPORT_LOG.txt` records the completed execution.

`build_chapel_r04.py` is the corrected **experimental** procedural builder, included for reproducibility; it is not an approved cathedral-generator replacement. The full builder was not run for this repair. Its shell function was executed independently on all 33 saved shell fixtures. For an optional fresh procedural rebuild in a separate output copy, run that builder, then `extract_sections.py` and `draw_review.py`; the latter requires Python numpy, matplotlib and shapely and updates the rebuild's `QA.json`. The delivered saved-model repair's authoritative QA is `QA_R04.json`.

`GENERATOR_DIFF.patch` isolates the shell implementation and revision-label changes. `SHA256SUMS.txt` lists every packaged file except itself; packaging verification confirmed no missing entries or hash mismatches. The original archives are not duplicated here.

## Remaining boundaries

This completes the requested shell-winding and export correction. It does not resolve middle-vault elevations/receiving masonry, companion-chapel junctions, final profiles and bonding, roof drainage, neighboring window/roof clearances, structural load paths or support capacities. F5ZL-C's support schedule remains missing. New trial webs and profiles remain experimental, with no new historical or structural validation. R04 is not approved architecture.
