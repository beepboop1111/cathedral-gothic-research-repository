# X02 R03 - Architectural precinct redesign

Status: NEW DESIGN STUDY; former precinct layout assumptions reopened by user instruction. This records the requested redesign, not automatic adoption into the cathedral baseline.

The previous plans were functional envelopes. R03 develops a connected architectural composition: arcaded cloister, chamfered entrance hall, octagonal chapter house with buttresses and a short two-bay vestibule, stepped residential range, night stair turret, canted refectory, kitchen range, herb garden and distinct arrival/chapter/service courts. Concept walls have doors and windows cut into them. These are authored proposals, not recovered historical or existing geometry.

User direction: "Locked architecture can be unlocked ... not a huge fan of how the layout looks ... a bunch of squares and rectangles." Scope applied: reconsider the precinct masses, hall form, range arrangement, gateway, courts and arcade rhythm. Source R02 is preserved byte-for-byte. The cathedral vault generators and geometry are not involved in this 2D design change.

## New design values
Octagonal chapter house: 12 m across flats, 119.294 m2 footprint before buttresses. Vestibule 6.5 x 3.5 m in two 3.25 m concept bays, replacing the R02 9 m vestibule. The 22 x 26 m cloister and 15 x 19 m garden remain as useful proportions; arcade rhythm is proposed as 28 bays (6+8+6+8), not inherited as a lock. Wall thicknesses .45 m and chapter .60 m are graphic design-study values with no structural acceptance. The turret stair symbol carries no rise or tread count.

## Drawing convention
Black solid/poche = defined geometry within this authored concept, not source verification or construction approval. Gray dashed = indicative set-out. Red dashed = unresolved cathedral interface / chapel test. All new architecture remains a proposal. Prior schemes and the southern baseline are retained as historical references, rather than used as a prohibition on this design study.

## Validation
64 geometry/preservation checks pass, 0 fail. New bodies, wall cuts and garden are valid; unintended body overlaps screened; chapter vestibule meets hall/walk; root screen unchanged; source hash unchanged. The night room/turret union and gate hall/cloister overlap are deliberate architectural joins. Only 12 transformed X01 roots are available. Stair height, actual chapel footprint, finished openings, roof/flyer interfaces, site boundaries, structural capacity and missing F5ZL-C schedule are not resolved by this concept.

## Reproduction
python3 build_r03.py with shapely and reportlab. Reads sources/R02_GEOMETRY.json only and writes within this experiment. Native coordinates are metres; source reference uses the inherited experimental E5-S2 context. SVG is physical 1:1; PDF scales are 1:250 and 1:350 at A3. PNG is a preview.

## Review
Assess the architectural composition and circulation character before detailed profiles, roofs or additional modeling. The red N4/CH-N5 and N6 interfaces remain named design holds; no cathedral wall opening has been created.
