PASS 6J — R1 @ 78° SPRING CLUSTER — STUDY S1

Purpose
-------
Start spring-cluster refinement without changing the approved V13 topology or
the approved V12/U1 profile family.

Representative spring
---------------------
R1 @ 78°
X = 869.278779
Y = 3000.000000
Z = 4089.635119

Eight incident services
-----------------------
4 x V12 D ogive:
- inner bay 3
- inner bay 4
- middle bay 3
- middle bay 4

2 x V12 doubleau:
- inner transverse R0↔R1 at 78°
- middle transverse R1↔R2 at 78°

2 x untouched U1 longitudinal:
- R1 bay 3 side
- R1 bay 4 side

Locked / unchanged
------------------
- every member path above Y=3000
- all V12 D profiles
- all V12 doubleau profiles
- U1 profile
- exact V13 orientations
- Y=3000 springing
- no lateral shaft movement
- no fan/easing below springing
- existing Pier V2 geometry
- existing tas-de-charge geometry

S1 change
---------
Baseline:
  all eight complete rib profiles continue vertically from Y=3000 to Y=2700.

S1:
  all eight complete rib profiles remain perfectly vertical but terminate at
  Y=2880, the bottom of the existing tas-de-charge overlap zone.
  Below Y=2880 only the existing Pier V2 core continues.

This is intentionally a single-variable test. There is no scaling, spreading,
profile simplification, or boss redesign in S1.

The branches are shown only to Y=3400 so the spring cluster is easy to inspect.

Files
-----
PASS6J_SPRING_CLUSTER_R1_78_BASELINE_FULL_RESPONDS.stl
  current full-profile-respond behavior + Pier V2/tas
  40,292 triangles

PASS6J_SPRING_CLUSTER_R1_78_S1_TAS_TERMINATION.stl
  S1 termination at Y=2880 + Pier V2/tas
  40,292 triangles

PASS6J_SPRING_CLUSTER_R1_78_S1_MEMBERS_ONLY.stl
  same S1 eight-member cluster without pier/tas
  32,640 triangles