# Cathedral F5ZP — floor-plan WORK HANDOFF R03

Read this file first. 2026-11-05. 2D continuation only. No experimental geometry has been promoted.

## Latest user direction

1. Work in 2D.
2. Third layer has fourteen significantly lower vaults, two per each of seven bays. Preserve the seven inner and seven middle vaults.
3. Correct the T2/T6 outer-corner offset. Do not carry forward the previous recommendation to preserve the 7.471-degree skew.
4. Ignore paired lower entrances, central receivers and upper-window positions for the present floor-plan work.
5. **Chapel bodies come later.** Existing chapel-body outlines are context from older experiments, not design constraints for the next pass. Do not design them, and do not require the developing floor plan to fit them. Preserve their source records.

The lower third-layer rhythm and relative-height intent remain. Earlier specific entrance widths, receiver widths, window dimensions and height trials are not approved and are not active defaults. No additional architectural approval was granted by the request for a handoff.

## Current carried-forward candidate

`ACTIVE_2D_PLAN_CANDIDATE.json` contains recovered inner/middle set-out and the current experimental outer footprints only. It excludes all chapel bodies, exterior compartment bodies, entrance layouts, receiver dimensions and window positions. `CURRENT_2D_PLAN.svg` / PNG provide an editable reference preview. Their SVG document units are plotted drawing units; coordinates and numerical dimensions are native project units with physical SI conversion unresolved.

Latest corner correction: T2/T6 outer corners lie on the outward normal through their unchanged middle-bay receiving chord midpoint and the unchanged Study D ellipse, center (20213,0), east radius 7169, north/south radius 6657. Prior lateral offsets +/-225.878922 are removed. Movement per corner 226.235464 native units. New corners:

| Sector | X east | Y north |
|---|---:|---:|
| T2 | 24667.709664913700 | -5215.794878321537 |
| T6 | 24667.709664913695 | 5215.794878321537 |

Numerical offset residuals are below 1.4e-12. The normal depth to either corrected corner is 1709.678246. Preserve exact JSON precision; do not round active coordinates to this table's formatting.

## Status ledger

| Item | Status / instruction |
|---|---|
| Approved cathedral architecture, F5ZK-C/F5ZN-A | Protected; do not overwrite from this experimental package |
| Working inner/middle ambulatory vault generator | Preserve; do not rebuild or rerun merely for recovery |
| Pass 6J, R1 @78° records | Preserve |
| Selected Crossing Full-Cell R05 | Preserve |
| T2/T6 corrected corner candidate | Latest experimental continuation; not newly approved/locked |
| Fourteen third-layer footprints | Experimental floor-plan set-out; retained two-per-bay rhythm |
| Chapel bodies | DEFERRED — later design; old outlines are context only |
| Entrance, receiver and upper-window positions | SET ASIDE for present work |
| Prior trial vertical numbers | Inactive experimental evidence; do not automatically apply |
| Missing F5ZL-C support schedule | UNRESOLVED; do not invent |
| Physical metres/native-unit conversion | UNRESOLVED/null; numerical native scale preserved |
| Gallery 4521 vs 4950 and angular source conflicts | Unresolved separate evidence; do not silently reconcile |
| Actual 3D adjoining crossing masonry contacts | Earlier workflow remains incomplete where source geometry was missing; 2D studies do not prove them |

## Evidence and reproduction

`evidence/outer_corner_R01/` preserves the complete last correction study, its inputs, procedural script, numerical QA, editable SVGs and previews. Its 27 geometric checks passed; two SVGs parsed. Earlier drawings show chapel outlines because they were used as context then. **Those outlines and the neck/compartment side transitions are now deferred context, not constraints on future plan work.** The latest user direction above supersedes that study's chapel-preservation design assumption for future development; original bytes remain untouched.

`evidence/recovery_R03/` retains the earlier recovery checkpoint and unit/contact/source-preservation reports. Consult those before repeating recovery, testing, or claiming units/contact resolved. Source references are evidence, not automatic approval.

Run `python scripts/draw_active_plan.py` with Python 3 and matplotlib to regenerate the current plan preview. The corner experiment can be reproduced separately with `python evidence/outer_corner_R01/scripts/fix_corners.py` (numpy, shapely, matplotlib); it reproduces the historical context study, not a new chapel design.

## GitHub and source recovery

Repository: beepboop1111/cathedral-gothic-research-repository. Before substantial new work read branch cathedral/governance-r01, path cathedral/governance/CATHEDRAL_MASTER_REFERENCE.md. Last verified blob: 1d7e358ff7562fcc64088854baa2abd3d31a729e; governance remains provisional.

Latest geometric checkpoint commit: 9582bb60ff5549ceb6ac7369d0369bce8b81117b, branch cathedral/outer-corner-fix-2d-r01-2026-11-05. Earlier lineage: 55211c62c2f39c4735b6434a03f0365edaecd19c (T2/T6 prior skewed trial), 6d8bd608e9aec5a566be4f33fe961a2f20aef5e2 (regular bay trial), 2251f484e3b1bdafaf065dde8349f483bfa996a5 (14 lower footprint correction), 677d66008516bba5ba2c88d1b1702e2227efee68 (R04 plan evidence), e41258ebcac5d45176b3f257d35fb6dd7f3212d4 (registration/contact recovery).

Original WORK HANDOFF R02 Library ID libfile_cdb11cdccea481918a1c707a543c6bd4; duplicate libfile_9c0b8de4ae4c8191b14fda4bbf21aae2. Registration/contact R03 libfile_76eca9c7f32c81919fc959b15b444c90. Corner correction libfile_aa9e50ef2bc88191875adba3c70cd1aa. These packages can recover wider source evidence if needed. No live MR COMPUTER reinspection was performed just to prepare this handoff; do not claim a newly verified live save.

## Next bounded task

Continue the complete 2D chevet floor plan from the corrected corners: check continuity, dimensions and connections of the 7–7–14 vault footprints and outer passage, without chapel bodies or opening/support placement driving the layout. Identify any remaining set-out conflicts. Do not regenerate completed inner/middle work. Keep experiments separate, validate affected interfaces and package results before requesting architectural promotion.

## Ready-to-paste continuation prompt

Continue Cathedral F5ZP from WORK HANDOFF R03. Read HANDOFF.md and recover the bundled current 2D plan and latest GitHub checkpoint. Stay in 2D. Carry forward the corrected T2/T6 outer corners and the 7–7–14 vault footprint rhythm. Chapel bodies come later; their earlier outlines are context only. Ignore paired lower entrances, central receivers and upper-window positions for this stage. Continue dimensioning and checking the whole chevet floor plan and its vault connections. Preserve approved architecture, numerical scale, the working inner/middle generator, Pass 6J and Crossing Full-Cell R05. Keep F5ZL-C and physical-unit conversion unresolved. Do not repeat completed work or promote experimental geometry without approval.
