# F5ZP Registration and Crossing Contact — R03

2026-11-05 · **EXPERIMENTAL, FOR REVIEW. No architectural promotion.**

The saved chevet **guide** registers to its F5ZN-A set-out. A trustworthy SI conversion and the complete installed crossing junctions remain unresolved. The recovered files do not contain the adjoining nave/choir/crossing pier and wall solids needed to validate those physical connections. This package completes the accessible measurements and documents the evidence gaps without manufacturing supports.

| Requested check | Result | Evidence and limit |
|---|---|---|
| Chevet to choir registration | **PASS for saved coordination geometry; installed masonry UNRESOLVED** | All 24 saved spring nodes and ring guide coordinates checked. Q5 end and chevet center agree at X20213. No installed approved F5ZK-C wall/pier mesh matrix recovered. |
| Physical conversion | **UNRESOLVED; coefficient remains null** | A prior handoff explicitly declares millimetres, but the saved chevet guide declares Minecraft blocks. No independent second physical measurement linked to these exact native endpoints was recovered. |
| R05 to adjoining masonry | **24 saved-surface comparisons completed; full junction UNRESOLVED** | No tested G40 fragment touches R05. Missing intervening geometry means this is not a clearance or continuity pass for the cathedral. |

## Baselines recovered before study assembly

Read the attached `HANDOFF.md`, current GitHub governance, the prior alignment checkpoint, and the live Master Cathedral Checkpoint introduction. GitHub master blob remains `1d7e358ff7562fcc64088854baa2abd3d31a729e`; governance branch head recovered as `0ea0e9697394abf41035195a9041df8a7ad286c2`. The prior alignment commit is `b232d7ac581fed26c1f84ae1c3d72899fd09d260`.

Actual saved files opened headlessly in Blender 5.0.1:

| MR COMPUTER source | SHA-256 | Scope |
|---|---|---|
| `Desktop/newgen_F5ZN_A_CHEVET_STUDY_1to1.blend` | `d5ef438c269c99dc27052d26a1885f7965065d52ea51162cca4329d4419174bc` | 56 coordination objects plus separate historical scene. No built chevet stone in the F5ZN-A scene. |
| `Desktop/Cathedral_F5ZP_G40_Working.blend` | `9b1d1fac567be1fea1c527582e8be2ad89f6464cae549d582b2e0f6bf7f7a2a9` | 399 objects; mixed generations, hidden alternatives and reference assets. Not a whole-cathedral masonry authority. |
| `Cathedral_STLs/Cathedral_Parts_Library.blend` | `cd97e0803d6afea0230ce3919e3cea6d81f37eb63b53a8a53740720ba81b812a` | 163 library objects, including Pass 6J records. Collection names do not confer approval; local assets do not establish installed coordinates. |
| `Downloads/NE_J11_J12_R04_EDITABLE.blend` | `73fb74d685a4290c432f8c3081228a618a7565699809493e6ac2708ca8422b7d` | Superseded nose/corbel experiment. Inspected for lineage; excluded from the active contact assembly. |
| Handoff `Crossing_Full_Cell_R05.blend` | `0af24a9369925c36618b7afc9aa4407d7cee20c60ae46ba33c9a6dba3861d917` | Selected full-cell source. Identical attached and recovered MR COMPUTER copy. |

Absolute source paths, timestamps, object matrices, properties, counts and bounds are in `inputs/MR_COMPUTER_inventory.json`. Original recovered JSON, producer script, manifest and checkpoint contents are retained in `inputs/MR_COMPUTER_text_sources.json`. The unit declarations and extracted F5ZK-C PDF text are in `inputs/unit_full_sources.json`.

Two additional saved files were checked before closing recovery: `Desktop/cathdedral 3D planning .blend` contains 17 earlier G23–G40 transept/portal proposal objects, not installed adjoining nave/choir/crossing masonry; `Desktop/blender/1Cathedral_Parts_Library.blend` contains 167 older local library objects. Their full inventories and hashes are retained in `inputs/ADDITIONAL_INVENTORY.json`. Targeted filename and unit-evidence searches covered Desktop, Downloads, Documents, the listed safety backup and the parts-library directory; this does not claim every unmounted or unrelated storage location was searched.

The recovered chevet manifest's old result hash/size does **not** match the actual saved guide file. Its viewport-correction note may explain a later save, but does not update that checksum. This study identifies the actual file by the hash above and verifies its saved coordinates; it does not substitute the stale manifest result hash.

## Chevet results

The F5ZN-A saved guide uses `(X,Y,Z)=(20213+r sin θ, r cos θ, elevation)`, with 0° north and 90° east. Its 24 unique spring-node coordinates match the checkpoint formula within **0.000899 native units**. The numerical acceptance tolerance is 0.002 units, appropriate to float32 world coordinates near X27000; it is not a construction tolerance. Ring radial residuals are recorded separately in `CHEVET_QA.json`.

The measured center is consistent with Q5 ending at X20213. Its 0.5°/179.5° terminations are intentionally present in the **saved schedule**, rather than floating-point noise. Their architectural purpose remains unproved.

| Radius | Eastward offset from X20213 | Lateral inset from same-radius north/south datum |
|---:|---:|---:|
| 2933 | 25.595 | 0.112 |
| 4085 | 35.648 | 0.156 |
| 5285 | 46.120 | 0.201 |
| 6657 | 58.093 | 0.253 |

Values are derived at exact scheduled angles and compared with actual guide points; they are **not measured masonry gaps**. Straight F5ZE bands 5429 and 6965 differ from chevet bands 5285 and 6657 by 144 and 308 units. A transition, taper or differing revision cannot be selected without evidence.

The recovered F5ZK-C PDF explicitly gives unequal centers 14°, 40.5°, 65.75°, 90°, 114.25°, 139.5°, 166°, and a diagrammatic orientation. The governance/protected historical record also contains 30°, 50°, 70°, 90°, 110°, 130°, 150°. Both are recorded; neither has been promoted over the other. No approved generator was rerun.

## Unit decision

`UNIT_EVIDENCE.json` retains `physical_m_per_native_unit = null`. The 0.001 m/unit millimetre hypothesis has a documentary declaration, but no independent calibration against these exact saved baselines. The 0.0013 X02 coefficient includes a 130% design experiment and is not transferable. Blender `NONE`, scale_length 1, a Minecraft-block label and the glTF metre convention do not independently prove the intended SI scale.

No metric scale bar or physical measurement is certified. All geometry retains native numerical magnitudes, including the GLB; consumers must not infer physical metres from the GLB container alone.

## Crossing contact and frame correction

The saved principal G40 context/replacement objects already use **X east, Y north, Z height**, with identity object matrices. The G40 scene's global “Y vertical” note is inconsistent with those saved meshes. Geometry landmarks include floor Z0, gallery Z4854–4950 and transept plan terminals at Y±10709. The choir-floor object's existing ×16 matrix was applied exactly once when capturing world vertices. Other small mixed assets were not globally normalized by their labels.

The R05 GLB expresses native geometry as `(X,Zheight,-Ynorth)`. Its inverse is a proper rotation, not a reflection. No translation or numerical scale correction was applied. `FRAME_QA.json` records the evidence and scope.

Three actual saved objects were compared independently against each of four R05 lower full-cell masses and four upper-core placeholders:

- `G40F__G40_CONTEXT_MINUS_G24_ORIGINAL` — saved transept context fragment.
- `G40F__OPTION_C_G24_G25_REPLACEMENTS` — separate provisional replacements, not promoted.
- `G40M2_DERIVED_FULL_CHOIR_FIRST_FLOOR_X2360_TO_X10709_JOIN` — a derived choir gallery-floor trial, not adjoining ground masonry.

| R05 part / source | Minimum saved-surface distance, native units | Result |
|---|---:|---|
| Each lower mass / G40 context | 3568.094 | No surface contact |
| Each upper placeholder / G40 context | 4515.994 | No surface contact |
| Each lower mass / Option C replacements | 5504.423 | No surface contact |
| Each upper placeholder / Option C replacements | 6189.000 | No surface contact |
| NE lower mass / north choir floor trial | 1999.117 | No surface contact |
| NE upper placeholder / north choir floor trial | 2649.000 | No surface contact |

All 24 comparisons and both nearest-point coordinates are recorded in `CONTACT_QA.json` and `CONTACT_REGISTER.csv`. The exact triangle calculation covers vertex/face, edge/edge and segment/face cases; bounding boxes only prune candidates. For example, checking vertices alone overstates the upper-placeholder distance; the reported calculation includes minima inside edges/faces.

Each comparison has zero surface-contact area. The two principal G40 objects are **not watertight**. Their solid overlap volumes remain null where a solid interior cannot be established; no repair or inferred filling was used. The closed choir-floor trial is separated from R05 by its bounds, establishing zero overlap volume for those eight pairs. These are properties of recovered fragments, not evidence that the intended intervening cathedral is empty.

`SECTION_QA.json` contains **132 corner/source/height comparisons at 11 elevations**, including below/above springing, the R05 4392 termination, the distinct gallery datums and the upper cores. No sampled section traces intersect. Missing traces are recorded as null distances, not infinite or verified physical gaps. The whole-triangle tests cover continuous height for these saved surfaces; the sections explain their relationships visually.

The missing adjoining central piers, nave/choir walls and installed chevet masonry prevent a complete physical contact/overlap/continuity conclusion. The F5ZL-C 248-support schedule remains **MISSING**. No load capacity, masonry bonding, foundations, bearing adequacy or actual high-vault springing support is certified.

## Delivered study and validation

`CHEVET_REGISTRATION`, `CROSSING_CONTACT_PLANS` and `CROSSING_SECTIONS` are provided as annotated PNG/SVG pairs. Black solid denotes measured saved traces (not automatic architectural approval), gray dashed denotes construction/datums, and red dashed denotes unresolved interfaces. Upper-core placeholders use gray dashed section outlines.

The GLB retains all 118 R05 source meshes, adds three saved G40 objects and detached chevet guides. Reimport returns 134 geometries. Blender retains all 118 original R05 mesh/curve objects and loads separate G40/chevet collections into a new editable file. Both are native scale studies. Upper R05 cores remain placeholders, exactly as supplied.

Validation actually performed:

- 24 saved chevet nodes and ring coordinates measured.
- 24 exact saved-surface distance comparisons; 132 sectional comparisons.
- 126 numerical/export checks passed, including 118 unchanged R05 mesh vertex/face checks and SVG XML parsing.
- Blender study saved, reopened, rendered, and compared against all 118 source R05 mesh/curve objects using world-coordinate geometry hashes.
- All four principal MR COMPUTER source file hashes remained unchanged after recovery.
- PNG/SVG drawings and the Blender render visually inspected. Exhibit is not exposed in the available tools; no Exhibit or Blender GUI inspection is claimed.

These are technical/geometric checks only. Architectural acceptance and structural validation remain separate.

## Reproduction and next evidence

Run `python scripts/analyze.py`, then `python scripts/verify.py` from the unpacked package. Requirements and exact installed analysis versions are recorded. `scripts/recover_inventory_blender.py` and `recover_meshes_blender.py` reproduce the read-only live probes; `build_editable_blender.py` and `verify_editable_blender.py` reproduce the machine-based editable study from the named source paths. They write only a separate experimental directory and temporary recovery files.

The next bounded task is recovery of the **installed adjoining pier/wall source and its producer/placement**, not another R05 shape change. For SI conversion, recover an explicit dimension contract or two independently established physical lengths with identifiable endpoints. For chevet installation, recover its saved built mesh/transform and the choir terminal supports. The current evidence does not justify rebuilding or promoting geometry.

F5ZK-C, F5ZN-A, the working inner/middle ambulatory generator, historical originals, Pass 6J and the R05 selection remain protected. The exact working 14-vault generator is still not identified in these recovered files and has not been replaced. Gallery 4521 versus 4950, Q1 5400 versus 5429 and both angular records remain explicit unresolved entries.
