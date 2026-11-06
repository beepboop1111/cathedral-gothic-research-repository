# R17 — Sexpartite Gothic double-bay experiment (1:16)

**Status:** Experimental. Not approved architectural construction or structurally validated.

Different Gothic vault family: a rectangular double-bay divided into six web cells using six boundary pointed arches, four diagonal groins and two intermediate groin paths. Its original two-centered boundary-arch curves are derived from a new synthetic test footprint (native length 4400, width 2400); no historical dimensions have been inferred.

**Crown validation:** spring Z3000; highest arch apex Z4320; central crown Z4700, raised 380 native units. R16 strict prebuild/postbuild guard and locked-source hash verification passed. Exact groin/web shared-path numerical gaps = 0; meridian sag = 0. Open intrados: there is no certified masonry thickness, bonded rib structure or historical fidelity.

**Native scale:** All design math uses native units. STL and small GLB are explicitly divided by 16. The Blender file has two scenes: R17_SOURCE_1_TO_16 and R17_RESTORED_NATIVE_X16. The second scene uses the **same Blender mesh datablock** with object.scale=(16,16,16), giving restored width 4400, depth 2400, height 1700 native units. Do not multiply the source coordinates twice. Mesh diameter is not proof of architectural fit.

**Blender file:** F5ZP_R17_SEXPARTITE_DOUBLE_BAY_1_TO_16_LIVE_EXPERIMENTAL.blend

**Source:** scripts/build_R17_sexpartite.py
**Scene builder:** scripts/make_R17_blender_review.py
**R16 dependency:** R16_dependency/ (byte-identical isolated copy).
**QA:** qa/R17_SEXPARTITE_MODEL_QA.json; outputs/guarded/*_CROWN_LOCK_QA.json
**Outputs:** outputs/guarded/R17_SEXPARTITE_SIX_CELL_1to16.stl;
outputs/R17_SEXPARTITE_SIX_CELL_1to16.glb;
outputs/guarded/R17_SEXPARTITE_SIX_CELL_FULL_1to1.glb
**Comparative renders:** renders/R17_SOURCE_1_TO_16_0001.png; R17_RESTORED_NATIVE_X16_0001.png

**Locked-geometry warning:** Never alter the cathedral's F5ZK-C floor plan, F5ZN-A ambulatory vault generator, accepted R14 arches and groins, Pass 6J bearings or existing crown elevations. F5ZL-C remains unresolved. Original R16 guard scripts were copied and SHA-256 recorded; authoritative originals unchanged. Do not promote R17 without architectural approval.

**Next actual test:** measured real vault geometry, not synthetic example. Geometry interface tests passing does not certify historical or structural correctness.
