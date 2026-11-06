# F5ZP R11 — full coordinated 2D floor plan (experimental)

Date: 2026-11-06
Status: EXPERIMENTAL; geometric checks passed; architectural, historical, and structural approvals not claimed.
Baseline: Saved R12C native GeoJSON, with R10 shifted clear-space geometry. No approved baseline, locked model, master generator, or Pass 6J record replaced.

## Native parameters
- Native coordinate scale 1:1; physical unit conversion unresolved.
- Main straight-bay separators N2–N9, Q2–Q5: 520.
- Choir Q2–Q5 aligned aisle interbay separators: 270, exactly sharing main bay centerline.
- Nave, Q1, Q2–Q5, chevet transverse masonry schedule: 320 / 197 / 292.
- Choir Q2/Q3/Q4/Q5 intra-bay paired aisle gaps after exact alignment: 495 / 250 / 250 / 285.
- Q1–Q2 wide interface: 1160 provisional.
- N9–N10: 800 provisional.
- West-end allowance: 1480 provisional.
- Chevet and Q5 outer registration unchanged.
- Axial threshold reference X=28000; axial chapel model not in this coordinate export.

## R11 QA evidence (MR COMPUTER)
Source workspace: `/home/christopher/Downloads/F5ZP_R12C_FULL_PLAN_BLENDER_EXPERIMENTAL/`
Artifact directory: `R11_FULL_COORDINATED_2D_EXPERIMENTAL/`
Full review PNG: `~/Downloads/F5ZP_R11_FULL_COORDINATED_2D_EXPERIMENTAL.png`
Complete ZIP: `~/Downloads/F5ZP_R11_FULL_COORDINATED_2D_EXPERIMENTAL.zip`
ZIP SHA-256 prefix: `3fd667eb6accd79dd036d3ec`
Outputs in ZIP: source generator `R11_FULL_COORDINATED_2D_PLAN.py`, native GeoJSON, PNG, SVG, 146-item CSV measurement ledger, geometric QA JSON, handoff README.

Validation executed on MR COMPUTER: 218 clear vault polygons, three valid masonry polygons; no clear-space overlap, zero coordinate-axis misalignment across 18 Q2–Q5 placements. Original vault polygon areas unchanged. 68 legacy support geometries included *as unregistered reference overlays only*, not fitted structural supports. PNG 3377×2544. SVG XML verified; ZIP integrity test passed.

## Unresolved
- Crossing three-vault-per-bay support issue retained separate from this floor-plan study.
- Legacy nave and choir support elements require re-registration to newly positioned vaults.
- Wide Q1–Q2 junction and west terminus not finally designed.
- Axial chapel true registered 2D footprint unavailable in R10; don't invent one.
- Missing F5ZL-C support schedule remains unresolved.
- No structural-capacity or entrance-opening validation.

This branch is an isolated reference checkpoint; full binary/coordinate outputs remain on the authorized MR COMPUTER, not uploaded into this repository by this manifest commit. Do not promote without approval.
