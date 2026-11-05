# F5ZP entrance-and-bearing plan R01 — EXPERIMENTAL

## Outcome
Generated all seven entrance studies: six mirrored offset O2 ground bearings and one axial entrance without O2. Four lateral entrances and the axial entrance lie on their source frontage planes. **T2 and T6 are unresolved:** their outer frontages have a bend, so the broad proposed opening crosses that bend. A single planar pointed arch cannot follow both segments without a revised threshold/reveal arrangement. The plan flags the conflict rather than silently straightening or moving the corrected corners.

40/40 topology/set-out checks pass. These checks do not include the two failed architectural opening-plane checks. All fourteen plan cells cover their original seven envelopes, share neighboring interfaces, and preserve inner/middle source coordinates. Mirrored O2 residual maximum 0 native units.

## Assumptions
O2 at 72% of outer-frontage arclength on T1–T3, mirrored at 28% on T5–T7. Broad entrance occupies the 72% frontage side; the narrow side is a subsidiary frontage, not a second chapel entrance. Respond reservations are 180 wide x 300 deep; axial threshold 600 deep, lateral 300. These are explicit editable trial values. Clear widths deduct 90 at each bearing center. No SI/accessibility claim. Ground footprints outside frontages are reservations, not final compound pier profiles.

Axial midpoint is an overhead construction target only, **not a ground support**. Its two subsidiary plan cells are not two separate supported vaults. Bosses and spokes are plan construction indicators; curves, crowns, web shapes and structural functions remain unproved. Five-ground-bearing counts at T2/T6 treat the existing frontage bend as an unsupported geometric corner, which must also be resolved with their threshold design.

## Preservation and lineage
Input BASELINE.json is the unmodified active candidate from Floor Plan WORK HANDOFF R03, checked against chevet topology review R04. SHA256 066027d5fa0e673b5c267718e906d105c86272b6358fcc8bf2a33a5d3fa92a19. Corrected T2/T6 corners retained. Inner/middle F5ZK-C/F5ZN-A set-out, working generator, Pass 6J, Crossing R05 and historical sources untouched. Native X east, Y north; numerical 1:1. Physical metres/unit remains null. GitHub governance reread from cathedral/governance-r01; blob 1d7e358ff7562fcc64088854baa2abd3d31a729e. No live MR COMPUTER save reinspection; accessible saved source packages used.

## Deliverables and reproduction
ENTRANCE_BEARING_PLAN.svg is editable; PNG and matched BEFORE_AFTER.png provide review. CANDIDATE.json preserves full precision; MEASUREMENTS.csv schedules all bearings and openings; QA.json records each check. Reproduce with Python 3, numpy, shapely and matplotlib: `python generate_plan.py`. Values are geometric studies, not architectural approval. Existing chapel body model remains separate and has not been refitted to these new entrances.

## Next unresolved work
Resolve T2/T6 planar entrance geometry while preserving corrected corners and passage continuity, then develop engaged masonry and actual pointed arch/rib/web junctions. F5ZL-C support schedule, vertical scheme, structural capacity, shared chapel partitions and roof/window clearance remain unresolved.

