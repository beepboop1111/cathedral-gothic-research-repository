# R32 — Seven-sided open chancel / first wall / seven inner ambulatory vaults

**Protected input:** read-only R11 218 clear-vault polygons, R31 open purple sanctuary and R30 architectural interpretation, R29B wall section. No 3D rebuild, no generator modifications, no pier source replaced.

**Measured source findings:**
- In order from south to north, seven true sanctuary polygon facets correspond exactly to I_A7, I_A6, I_A5, I_A4, I_A3, I_A2, I_A1.
- Each associated clear-vault inner edge is parallel to its corresponding chancel facet, with **exactly 320 native units of perpendicular separation**, as per saved R11 geometry.
- Source face lengths match their offset vault edges. The end faces I_A7 / I_A1 have ~39.29 units of tangential vertex offset, so the raw corresponding endpoint-to-endpoint vector is ~322.4, **not evidence of a thicker wall**.
- There are six internal corner reference vertices of the actual seven-sided polygon, each with TWO noncoincident offset I-edge endpoints. Record the measured gaps in R32_SIX_INNER_CORNER_JOIN_SURVEY.csv; do NOT replace them with a fabricated shared pier or collapse them to one point.
- The north/south endpoints of the seven-facet chain require later coordination with the straight choir's bearing/interface arrangement. They are not approved support points.

**Artifacts:** one high-contrast dark full plan plus north side detail (PNG and SVG), exact source-derived 1:1 wall face strips and point/gap references (GeoJSON), seven-face and six-corner measurements CSV, QA JSON and procedural script.

**Validation distinctions:** Technical and geometric tests passed; user-approved overall sanctuary openness respected. Geometric wall separation does NOT establish load-bearing pier supports, actual rib springing or architectural approval. Historic and structural validation not performed. F5ZL-C support schedule remains missing. No outer 14-bay design generated.

Reproduce: python3 R32_CHANCEL_INNER_7_FACE_COORDINATION_2D.py