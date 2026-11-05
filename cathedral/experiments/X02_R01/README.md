# Cathedral F5ZP X02 R01 - Experimental Floor-Plan Review

Status: VALIDATED PARTIAL EXPERIMENT; NO AUTHORITY PROMOTION.

## Outcome
The independent northern-sector work is delivered. Complete master-precinct integration remains blocked by actual CH-N5 exterior geometry, the original protected southern E5-C3-L1 site file, actual doors/stairs/partitions and Great Library/site inputs. No substitute footprints are presented as recovered architecture.

## Baseline and change
Baseline: completed X01 package `F5ZP_E5_S2_N4_NORTH_GATE_X01_REVIEW.zip`, retained under sources/x01. Governance: cathedral/governance-r01 master reference, blob 1d7e358ff7562fcc64088854baa2abd3d31a729e. Existing X01 coordinates remain unchanged. X02 adds explicit 1.2 m circulation reservations, a hypothetical 2.4 x 2.4 m night-stair zone, route screening, a dimension-only southern comparison, and an evidence/conflict register. These are experimental, unbuilt and unapproved.

Coordinates are metres, X east / Z north; source native architectural units are millimetres. E5-S2 uses X01's 130% design experiment and its additional northern transverse shift. This is not a transform of approved F5ZK-C/F5ZN-A. The SVG is physically 1:1; PDF pages have explicitly labeled presentation scales. Do not import the PDF at 1:1 without its scale conversion.

## Measured results
- Retained N4 portal center: X -34.2277 m, north wall Z 12.0625 m.
- Retained N4 screening root gap: 0.1956 m.
- Garden area: 47.5753 m2; retained root gap 0.2375 m.
- N5 throat / conditional chapel overlap: 2.0353 m2.
- New ceremonial reservation length: 41.1652 m; private night reservation length: 13.0375 m.
- 1.2 m route sweeps: no modeled root/garden overlap or departure from the defined reference domains. No actual door/partition/stair clearance is established.
- South cloister: 20.2 x 22.4 m = 452.48 m2. North: 22 x 26 m = 572 m2, +26.41%. Reported dimensions are comparable; site impacts cannot yet be compared.

## Source evidence and remaining uncertainty
The saved UG variant eb68a0c16ca5... names CH-N5 as a 2304 x 1728 mm vault at lines 701-703. It does not define exterior walls, projection, complete footprint or position. Its F5ZE/V13 identity is separate from the protected unidentified working F5ZN-A 14-vault generator; it was read as evidence and not executed.

The source paths for the E5-C3-L1 lock and original F5ZM-C root JSON are absent on MR COMPUTER. The X01 embedded E5-R3-notes and E5-C3-handoff hashes could not be checked against those missing originals. A recovered E5-R1 handoff records southern morphology, not its exact site placement. Older E5-R1 experimental south coordinates must not be substituted for the protected lock.

Only 12 reconstructed/transformed X01 roots are screened, not the full 88-root source and not the missing 248-support F5ZL-C schedule. Continuous source walls remain continuous. The conditional chapel rectangle is retained in dashed red. N4-west window, N4-east opening, N6 door, chapter corridor, controlled cloister entry and stair zone are planning reservations.

## Preserved work
F5ZK-C, F5ZN-A, all approved architecture, working inner/middle vault generator and Pass 6J are unchanged. No Blender operation, vault regeneration, source replacement or approval promotion occurred. Bay angles, gallery datums and Q1/J1 radii remain unresolved and unselected. Study D/MP-01G were neither regenerated nor installed here.

## Validation
77 technical/2D checks pass; 0 fail. This does not constitute architectural, historical, structural, accessibility or site approval. Checks cover input preservation, X01 metric regressions, polygon validity, JSON round-trip, 1.2 m swept reservations, pairwise known massing overlap and SVG physical scale. PDF visual QA is recorded separately after rendering.

## Deliverables and reproduction
- outputs/F5ZP_X02_R01_FLOOR_PLAN_REVIEW.pdf: four A3 vector pages.
- outputs/X02_NORTH_SECTOR_1to1.svg: metre coordinates; physical 1:1 SVG.
- outputs/X02_GEOMETRY.json: geometry, authority labels and explicit absent placements.
- outputs/X02_QA.json, X02_MEASUREMENTS.csv, X02_SENSITIVITY.json and X02_CONFLICT_REGISTER.csv.
- sources/: retained source package, GitHub reference and MR COMPUTER read-only evidence.

Run `python3 build_x02.py` with Python 3.12+, numpy, shapely, matplotlib and reportlab. No source generator is rebuilt. The script evaluates only X01's checked geometry prefix; original export commands are never run. Outputs are confined to outputs/.

## Next action
Recover actual CH-N5 exterior plan and the original southern E5-C3-L1 lock file/input pair; verify the opening and stair envelopes. Complete the missing site geometry and then review the northern-versus-southern alternative before any precinct-baseline selection.
