# M04 R03 — Original Pass 6J ↔ F5ZN-A chevet coordinate registration

**Evidence of transform:** F5ZN-A chevet center (20213,0), +X=east,+Y=north; original Pass6J R1 @78° has X869.278779 / vertical Y3000 / horizontal Z4089.635119. Horizontal radius is exactly 4181, bearing 78° measured from the source X axis to Z. The F5ZK-C angle convention and R11 bay numbering require source horizontal X/Z axes interchanged when registered globally. The determinant-positive 3D cyclic transform is **global (X,Y,Z)=(20213+source Z, source X, source Y)**, with vertical world Z representing the original vertical source Y. Registered spring = (24302.635119,869.278779,3000). It lies in the original A3/A4 clear-space gap; the naive no-axis-swap center translation lies **inside I_A1**, demonstrably invalid.

**Ring caveat:** Pass6J horizontal station radius 4181, nominal F5ZN-A R1 radius 4085: +96. This is measurable but neither its physical origin nor formal approval is proven. Do not silently reset a station to radius 4085.

**True source mesh QA:** Three original recovered pier models (articulated, derived, narrow) sectioned directly at five source-vertical Y levels where available. Actual polygonal mesh boundaries, not bounding boxes or re-drawn circles, are transformed and intersected with all 218 saved protected clear-vault polygons. At Y2705–2999 all three sampled shafts fit. At Y2600 the articulated and narrow plinths intersect I_A3/I_A4. These are sampled planes, not a full swept-volume guarantee. The clash is a real unresolved architectural conflict; do not shrink protected vaults or change approved source pier.

**8 original R1 boundary stations:** All eight original F5ZN-A/F5ZK-C angles mapped into global XY at radius 4181, outside saved I-ring clear footprints. This is coordinate/topology evidence, not proof that eight full identical piers fit.

**Status:** Strong registration evidence / geometric diagnosis validated. Physical pier approval withheld; no new profile or masonry bond, historical or structural analysis. F5ZL-C support schedule missing. Fourteen experimental outer subdivisions remain excluded.

Reproduction: python3 M04_R03_REGISTER_ORIGINAL_PASS6J.py
