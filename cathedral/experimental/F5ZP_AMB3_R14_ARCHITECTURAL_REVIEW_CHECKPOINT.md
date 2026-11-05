# F5ZP Third Ambulatory — R14 Consolidated Architectural Review

**Date:** 2026-11-05  
**Status:** EXPERIMENTAL, not approved or locked.  
**Branch:** `cathedral/experimental/f5zp-r14-review-20261105`  
**Base:** `cathedral/governance-r01`; the master reference remains provisional governance, not an approved architectural generator.

## Scope

Non-destructive, 2D architectural synthesis of R10–R13: recovered F5ZN-A middle ambulatory, seven radial trial bays, fourteen subsidiary plan compartments, symbolic inward and chapel entrance axes, two-crown R12 trial rib graph, and axial portal detail. The rejected old outer-ring geometry remains discarded.

## Recovered source

- MR COMPUTER saved scene (read-only): `/home/christopher/Desktop/newgen_F5ZN_A_CHEVET_STUDY_1to1.blend`
- SHA-256: `d5ef438c269c99dc27052d26a1885f7965065d52ea51162cca4329d4419174bc`
- Coordinates: `(20213 + r*sin(theta), r*cos(theta))`, theta clockwise from north.
- Seven AMB-M springing curves, eight exact saved radius-5285 node markers, Z=3000; verified reference band radii 4085–5285.
- Note: R14 redraws reference arcs analytically; exact saved marker coordinates are retained in the deliverable. This is not a raw curve-vertex export and **not a masonry-bearing polygon source**.

## Experimental plan

- Seven bay centers: 30°, 50°, 70°, 90°, 110°, 130°, 150°.
- New bay boundaries: 20°, 40°, 60°, 80°, 100°, 120°, 140°, 160°.
- Trial outer radial extent 6685 (does not reinstate the old outer wall).
- Fourteen non-overlapping plan cells, 14 trial bosses, 28 proposed primary rib connections, seven internal crown ridges.
- Seven schematic inward connections and seven schematic chapel entrance axes; actual clear widths and wall openings unverified.
- Axial 90° overhead springer-to-springer chord ~2321.7 project units; not clear width.
- R13 trial outer spring/apex 2300/3550 and crown levels 3900/3980; protected middle reference spring/crown 3000/4296. These new heights are unapproved.

## QA results (R14)

- Saved node max radius residual: 0.0005596 project units.
- Seven major bays / fourteen valid subsidiary plan polygons.
- Overlap within numerical tolerance; coverage gap 0; no sampled plan intrusion into reference middle band.
- 28 candidate corner-to-boss ribs and 0 rib terminations at entrance axes.
- Minimum/maximum distance to nearest existing AMB-M saved station: 184.4719 / 1150.7224 project units.
- **Verified receiving-face polygons: 0; verified rib-to-masonry contacts: 0.**
- Actual 3D vault topology, structural soundness, opening clearances, and F5ZL-C physical supports schedule remain unresolved.

## Deliverable and integrity

Full artifact package generated for the user's ChatGPT session:
`F5ZP_R14_Architectural_Review_EXPERIMENTAL.zip`  
Archive SHA-256: `ecd83a79781257c7b2bc8c8d8bf2d3c1e1f464814a095bb8c98372f9f51f5ccc`

Contains editable consolidated SVG, high-resolution PNG, clean SVG/PNG plan, standalone Python generator, frozen R10–R13 JSON source snapshots, bearing offset CSV, QA JSON, and README. The package is delivered separately in the conversation and is **not** stored in this GitHub commit. This record is an experimental checkpoint manifest, not a file mirror.

**Protection:** No approved geometry, working inner/middle vault generator, Pass 6J source or historical geometry was changed. The missing `CATHEDRAL_F5ZL_C_PHYSICAL_SUPPORTS.csv` remains unresolved.

## Decision gate

Review the 2D architectural rhythm and open circulation. Do not approve actual rib bearings or portal dimensions until masonry receiving-face polygons and chapel/portal jamb footprints can be registered in world space.