# Axial entrance and bearings R02 — EXPERIMENTAL

## Result
A separate editable 3D model of the axial entrance: one uninterrupted two-center pointed opening, two substantial masonry responds, four depth bands across a 600-native-unit threshold, and an adjacent four-ground-bearing ambulatory rib skeleton. An axial ridge indication joins the trial boss to the entrance crown. No central O2 ground support. Vault webs, final mouldings and chapel bays are outside this small study.

## Governing correction
The user explicitly removed the former outer ring as an experimental constraint and asked to work inward. The old T4 edge, T2/T6 corners, former fourteen footprints and R01 entrance plan are NOT governing geometry. This experiment chooses entrance X=28000 freely, then connects inward to the protected middle M_A4 outer chord. Old outer geometry is not imported. Earlier R01 frontage conflicts do not constrain this model.

## Baseline and preservation
Unmodified input JSON: Floor Plan WORK HANDOFF R03 active candidate, source SHA256 066027d5fa0e673b5c267718e906d105c86272b6358fcc8bf2a33a5d3fa92a19. Only inner/middle plan guides are read from it. Source M_A4 endpoints remain exact in the input/QA; Blender mesh storage has sub-0.001 native-unit floating-point approximation, quantified in QA.json. No source model, working generator, F5ZK-C/F5ZN-A architecture, Pass 6J or Crossing R05 is edited. No live MR COMPUTER inspection in this task. GitHub provisional governance retrieved, blob 1d7e358ff7562fcc64088854baa2abd3d31a729e; user’s current outer-ring instruction governs over older handoff assumptions.

## Trial dimensions — all native project units
- Entrance front X=28000; back X=28600; bearing masses extend X27900–28700.
- Clear opening 2200; bearing centers Y=+/-1250; masses Y1100–1400 and -1400–-1100, height1800.
- Spring Z1800; soffit crown3750; outer arch crown4050.
- Boss X26700, Y0, Z3600. Four circular trial ribs rise monotonically from spring1800 to boss; round radius45, not selected historical profiles.
- Inner ground bearings are blue trial vertical indicators at exact-source XY within model precision. Their heights and details are not recovered architecture.
- Arch inner circle centers Y=+/-1178.409090909091, Z1800, radius2278.409090909091. Arc endpoints have vertical tangents. The two branches form the pointed crown. Outer curve is independently constructed; ring thickness varies.
- Numerical 1:1 X east, Y north, Z up. Physical metres/unit unresolved; exported GLB's standard unit convention is not a certified physical conversion. Vertical placement is a trial, not reconciled with the middle-ambulatory saved 3D spring level.

## Validation
Blender script completed, three views rendered and visually reviewed. QA records mesh export/reimport count, finite coordinates, monotonic rib rise, arch endpoints, crown, opening width, symmetry, source-interface rounding tolerance and no axial ground pier. These are technical/geometric checks, not architectural approval, masonry engineering or evidence of compatible middle-vault heights. Source plan guides are reference geometry; no false complete cathedral model supplied. Curved trial ribs are smooth mesh sweeps; meshes are not certified for printing.

## Files and reproduction
Open Axial_Entrance_Bearings_R02_EXPERIMENTAL.blend or Axial_Entrance_Bearings_R02.glb. See AXIAL_OBLIQUE.png, AXIAL_FRONT.png and AXIAL_PLAN.png. MEASURED_PLAN_SECTION.svg/PNG gives dimensioned plan and entrance elevation. Inputs and QA included.

Reproduce: Blender 4.3.2 `blender -b -t 4 --python build_axial.py`, then Python3 with matplotlib `python draw_measurements.py`. Original source records remain unchanged. Geometry is procedurally generated with functions and loops.

## Unresolved
Final entrance location/width, support profiles and capacities, actual spring-level coordination, webs, adjacent bay interfaces, chapel partition continuity, roof/window relationships and missing F5ZL-C support schedule. No result promoted to approved or locked architecture.
