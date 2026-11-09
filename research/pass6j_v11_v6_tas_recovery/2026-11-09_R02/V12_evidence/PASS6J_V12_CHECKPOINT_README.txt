PASS 6J — V12 DISTANCE-READABLE RIB PROFILE TEST

LOCKED / UNCHANGED
- regenerated V6 arch paths
- true circular half-arches
- exact vertical-tangent springing behavior
- springing datum Y=3000
- straight vertical responds below springing
- Pass 6J asymmetric arrangement
- current local vault web/context
- Pier V2 / tas-de-charge geometry
- U1 longitudinal geometry in the comparison STL is copied unchanged

V12 SECTION CHANGE ONLY
D ogive:
- width envelope: 36.000118 blocks
- depth envelope: 59.892342 blocks
- broad central keel/filet event: 10.008 blocks
  = 27.8% of total width
- each broad flanking shadow channel: 5.688 blocks
  = 15.8% of total width
- lower D-family shoulder/side moulding retained
- fine V11 ridge/lip frequency removed

Doubleau:
- width envelope: 38.160168 blocks
- depth envelope: 64.675593 blocks
- broad central event: 10.609 blocks
  = 27.8% of total width
- each broad flanking channel: 6.029 blocks
  = 15.8% of total width
- same V12 moulding language as D, but remains the modestly heavier member

IMPLEMENTATION
- New V12 cross-sections were mapped onto the exact existing V11/V6 station frames.
- No arch centerline was regenerated, moved, widened, raised, or re-fit.
- Responds are vertical translations of the new spring section.
- Local-vault test replaces exactly one D arch/respond and one doubleau arch/respond.
- All other local-vault components are carried over unchanged, including U1,
  web geometry, Pier V2, and tas-de-charge.

VIEWING TEST
Open R1_78_PASS6J_V12_DISTANCE_READABLE_LOCAL_VAULT_TEST.stl and reuse the same
floor/gallery camera positions used for the V11 screenshots. The acceptance test
is whether the two broad channel shadows remain separable from the central
keel/filet at architectural distance, without increasing rib width.

Triangles:
- comparison STL: 270,800
- local-vault STL: 801,152