# R15 — Adopt main separator axis as organizing reference, 2D only

Design intent: use the established Q1–Q2 **main-bay separator axis X=4505** for all new studies. The Q1–Q2 aisle opening axis is X=4480; its 25-unit west offset is not silently corrected. R11, R13, R14, historical source footprints and all vault clear spaces remain unchanged.

## Three measured plan reservations
- S0: original R12C major bearing x3925..4725 (800 wide), center x4325, -180 from axis.
- S1: experimental x4105..4905 (800 wide), center x4505; loses original west portion, gains east reservation.
- S2: experimental x3925..5085 (1160 wide), center x4505; retains original footprint and extends to main bay divider endpoints. This is NOT an endorsement of a 1160-wide pier or load path.

Each scenario is projected onto the two existing 320-wide north/south transverse masonry bands: y2933..3253 and y-3253..-2933. All clear spaces and Option B passage footprints remain untouched. A 235-wide purple facing remains a wholly separate visual study.

## Critical limitation
None of the three study bands has a measurable LENGTH of common boundary with the Q1 or Q2 main vault polygon; at most there are corner contacts. This demonstrates why a centered strip alone cannot establish true supports: need to test the actual vault corner, respond, and wall-interface geometry before deciding bearing.

## Validation
All six experimental footprints fit entirely inside current R11 retained choir masonry, do not overlap R11 clear vaults or seven R13-B passages. Geometric validation only; no historical/structural adequacy. F5ZL-C remains missing.

## Reproduction
python3 R15_Q1_Q2_MAIN_AXIS_RESERVATION_2D.py