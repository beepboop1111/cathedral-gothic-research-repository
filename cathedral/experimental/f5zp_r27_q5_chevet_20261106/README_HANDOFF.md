# F5ZP R27 — Q5 to chevet transition / architectural junction audit

**Baseline:** Read-only R11 coordinated 2D; R13-B Q1 entrance, R26 choir rhythm work, R24 approved Q1 visual Option A. All source file SHA256 values appear in JSON QA. Seven chevet bay identities retained exactly, no new vault shapes; existing saved R11 has 7 I, 7 M and 7 T polygon records. This does not certify the independently discussed 14 outer low-vault rhythm.

## Findings
- Choir masonry and chevet masonry share exactly 9699.2594 native units of edge along X20213, split into north and south seam segments Y±2933..±7782.63, no shared masonry edge on axial Y0.
- Six candidate **solid masonry connection polygons** between the actual Q5 A1/A2/A3 east faces (X20053) and actual sloping west faces of I_A1/A7, M_A1/A7 and T_A1/A7. All six overlap both original masonry polygons, touch both real clear-vault boundaries with positive line lengths, and avoid every clear-vault polygon. North and south are mirror matches.
- Measured closest face-to-face distances approximately A1=224.886, A2=259.128, A3=305.452 native units, increasing outward. Exact measurements in CSV.
- **Unfinished axial entrance:** Q5_MAIN clear vault ends at X19893. The intervening x19893..20213 is a **solid 320-wide masonry terminal band**, with no recorded door opening at the centerline. At y0 the chevet masonry ring begins around X23081.91; the intervening axial approach is not a designed passage or verified clearance. Need architectural design and approval before changing this band.
- The six side connectors are retained masonry **for future receiving/opening studies**, not already open passages or approved piers.

## Validation levels
Technical: source hashes, reproducible generator, PNG and ZIP integrity PASS.
Geometric: existing reserved masonry continuity, actual vault-face edge contacts, symmetry and zero collisions PASS.
Architectural: INCOMPLETE (no designed Q5-to-chevet axial or side openings).
Historical: no new plate-supported interpretation.
Structural: no load path, thrust, masonry thickness adequacy or bearing proof.
F5ZL-C schedule absent. Nothing from R24/R26/R27 promoted to new physical/locked architecture.

## Reproduction
Run: python3 R27_Q5_CHEVET_JUNCTION_2D.py (in the R12C experimental workspace).