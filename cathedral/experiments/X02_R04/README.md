# F5ZP X02 R04 - East range floors and stair

EXPERIMENTAL ARCHITECTURAL DEVELOPMENT FROM THE PREFERRED R03 COMPOSITION.

Delivered: ground floor, upper floor and stair section A-A; developed walking-line section is shown below the true diameter cut. Plans are 1:100 at A3 portrait. Section is 1:50 at A3 landscape. Editable SVG plans use physical 1:1 dimensions and metre coordinates.

## Proposed arrangement
Ground: night lobby/sacristy and storage; existing chapter vestibule; northern common hall; five rooms (reading parlour, common room, office, linen store, workroom). The western service entrance has its own 1.40 m cross-passage into the 1.50 m central hall.

Upper: six chambers, total net 86.240 m2, around the 1.50 m hall. A new 2.40 m gross / 1.80 m clear study passage links night stair to northern range, above the western portion of the R03 gaps and chapter vestibule. Required open spans are 4.25 m and 4.15 m; their support is unverified. The provisional +3.420 m link soffit requires coordination with the chapter vestibule entry and any vault. This is the dependent change needed to make the preferred separated ranges function upstairs.

## Stair and vertical proposal
Ground FFL 0.000; upper FFL +3.600; slab study .180; soffit +3.420. Turret enlarges from 4.0 to 4.4 m across flats, same center (-23,25.2). Other principal R03 body footprints are unchanged.

20 risers at .180 m; 19 goings at 12 degrees; total rotation 228 degrees. Tread inner/outer radii .620/1.670 m, band 1.050 m before handrail detailing. Mean walking radius 1.145; chord going 0.239370; developed arc going 0.239808. No extra top tread is invented: riser 20 meets the upper landing.

The upper aperture covers all flight treads. A 1.05 x 1.20 m western landing footprint fits outside the flight and newel. The +5.700 control plane gives 2.10 m over upper landing and 2.28 m over highest tread. It is a required unobstructed envelope for future roofs, not verified roof headroom. No existing roof has been silently raised.

## Validation and source limits
123 source-preservation, room fit/access, stair containment, landing/aperture and route-band checks pass; 0 fail. This is technical/geometric checking, not structural, fire/escape or regulatory approval. The chosen tread band is not a finished width after rails. Consult applicable spiral-stair design guidance and usage classification before any physical construction decision. External references are identified in outputs/REFERENCE_AND_LIMITS.json; no compliance conclusion is drawn from a straight-stair table.

Original R03 input hash: f45d36620a57bc671e3d76e3c78ed50c36ee1dca1b76987b5663ae1fa1ca473c. It stays unchanged. All changes are confined to this R04 proposal. No cathedral geometry, vault generator or Pass 6J is rebuilt. F5ZL-C missing schedule remains unresolved. The candidate cathedral entrance and actual CH-N5 interface are outside this east-range task.

## Reproduction
python3 build_r04.py with shapely and reportlab. It reads the role-qualified R03 body/wall model, never executes a source generator, and writes outputs within this experiment. Full source copy and numerical schedules are included. PDF visual QA is performed after rendering.

## Next design stage
Develop bridge bearing and roof volumes around the reserved stair headroom and bedroom floor levels. Confirm the proposed room program and turret enlargement through architectural review. No baseline promotion is implied by the preferred design direction.
