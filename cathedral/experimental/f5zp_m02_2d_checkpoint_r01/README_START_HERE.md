# Cathedral F5ZP M02 — Coordinated 2D Architectural Checkpoint R01

**Status:** Phase B, C, D, E completed for the specific 2D geometric tasks reported. Technical/geometric regression PASS. This does NOT approve physical pier sections, Gothic arches, structural adequacy, historical details or the experimental R11 whole-model baseline.

## Authoritative user-confirmed spatial intent
The main nave, crossing and arms, choir and polygonal **seven-faced chancel are one continuous OPEN interior**. Internal Q5 divisions are planning references, not walls or seven doorways. First actual wall is the **320-native-unit seven-faced boundary from chancel to inner ambulatory**.

## Working floor plan — critical exclusion
Read **phase_d/D_WORKING_FLOORPLAN_SEVEN_OUTER_ONLY.geojson**. It includes the original **7 I, 7 M and 7 T source chevet bays**. It does **NOT** include the experimental paired **14 lower outer vault** subdivisions. Those prior Phase C trials are referenced only by an isolated QA summary; their geometries and scripts are intentionally omitted. Do not revive them without architectural approval.

## Proven measured geometry
The full saved experimental R11 has **218 nonoverlapping valid CLEAR vault polygons**, retained read-only. At each curved sector, I-to-M gap **197** and M-to-T gap **292** native units. The chancel first wall comprises seven **320 perpendicular-unit** strips. The eight experimental Phase B support footprint studies (6 corners + 2 end transitions) are NOT approved physical piers. The working plan only displays moderate provisional envelopes for reference.

## How to review
- drawings/MASTER_CATHEDRAL_DARK.png — Phase E full plan, one primary review image
- drawings/MASONRY_PLAN_DARK.png — Phase D source-only masonry reserve distinctions
- M02_ARCHITECTURAL_CHECKPOINT_REGISTER.json — authoritative status mapping within this local study
- M02_UNRESOLVED_ISSUES.csv — explicit blockers/approval boundaries
- source/R11_ORIGINAL.geojson — read-only saved experiment, source of coordinates
- phase_d/D_WORKING_FLOORPLAN_SEVEN_OUTER_ONLY.geojson — working 2D coordinated plan
- phase_b, phase_c, phase_d, phase_e — numerical evidence and clearly marked experiments

## Reproduce
From the ORIGINAL project workspace directory with shapely, matplotlib and Pillow available:
python3 M02_PHASE_B_R03_WALL_CONNECTED_COMPLETION.py
python3 M02_PHASE_D_MASONRY_RESERVATIONS_NO_OUTER_14.py
python3 M02_PHASE_E_FULL_CATHEDRAL_REGRESSION_2D.py
python3 M02_PHASE_F_CONSOLIDATE_HANDOFF.py

Included scripts retain original workspace-relative input paths. The checkpoint zip is self-contained for inspecting results; re-generating the scripts requires the original workspace layout.

## Separate validations
Technical PASS. Geometric 2D PASS for reported invariants. Architectural: central open area and first wall user-confirmed; piers/masonry joints unapproved. Historical NOT assessed. Structural NOT assessed. Physical unit conversion unresolved; F5ZL-C missing. Approved F5ZK-C and F5ZN-A, the working inner/middle vault generator and Pass 6J preserved.

GitHub intentionally not used.