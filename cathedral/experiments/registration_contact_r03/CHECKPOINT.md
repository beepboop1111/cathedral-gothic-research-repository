# F5ZP R03 experimental checkpoint

Date: 2026-11-05. Parent: WORK HANDOFF R02 and whole-alignment commit `b232d7ac581fed26c1f84ae1c3d72899fd09d260`.

**EXPERIMENTAL, NOT PROMOTED.** No approved geometry, locked dimensions, historical sources or generators changed.

| Register | Status | Decision carried forward |
|---|---|---|
| Crossing Full-Cell R05 | LOCKED PREFERRED CONCEPT | Four entire J11 cells solid; neighboring J12/J13 retained; 4970 native central clearing. Upper cores remain placeholders. |
| F5ZK-C / F5ZN-A | PROTECTED | Original dimensions retained. Angular authority conflict remains explicit. |
| Saved chevet guide registration | GEOMETRICALLY VALIDATED | 24 nodes, maximum residual 0.000899 native units, tolerance 0.002. This does not establish installed masonry. |
| G40 principal saved world frame | DERIVED FROM SAVED GEOMETRY | X east, Y north, Z up. Global scene note is stale for these objects. Per-object transforms govern. |
| Physical metres/native unit | UNRESOLVED | null; older 0.001 declaration unconfirmed, experimental 0.0013 excluded. |
| Crossing masonry contact | EVIDENCE-LIMITED | 24 measured saved-surface pairs, no contact. Adjoining piers/walls missing, so no whole-junction pass. |
| G40 overlap volumes | PARTLY UNRESOLVED | Nonclosed source objects not repaired; undefined solid interiors remain null. |
| F5ZL-C 248 supports | MISSING | No invented schedule, pier sizes or capacity. |
| Working inner/middle generator | PROTECTED / IDENTITY UNRESOLVED | Not rebuilt, modified or rerun. |
| Pass 6J | PROTECTED RECORD | Library inspected read-only; no bearing changes or cleanup restarted. |
| Architecture and structural capacity | NOT VALIDATED | No approval promotion. |

Deliverables: measured plans, two actual sections, native GLB and editable Blender study, station/contact CSVs, JSON QA, source snapshots/hashes, procedural scripts, report and reproduction instructions. All 118 R05 source meshes preserved in the GLB; all 118 original mesh/curve objects preserved in Blender.

See `REPORT.md` for results and limits, `SOURCE_PRESERVATION.json` for verified unchanged MR COMPUTER hashes, `REGRESSION_QA.json` for 126 passed numerical/export checks, and `BLENDER_REGRESSION_QA.json` for world-geometry checks after reopening.

New branch: `cathedral/registration-contact-r03-2026-11-05`. Governance and approved branches are not modified. This is an evidence checkpoint, not a new architectural baseline.

Next bounded recovery: installed adjoining nave/choir/crossing pier-and-wall source with producer and placement; installed chevet mesh matrix and terminal supports; independently linked physical dimensions. Do not repeat the completed R05/F5ZE plan overlay or rebuild working vaults.
