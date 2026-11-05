# F5ZP — Axial/Northeast Entrance Junction R03
Status: **experimental 2D geometry, not approved, not locked, and not structurally certified**. Prepared 2026-11-05. Detached from live cathedral model.

## Purpose
Two separate chapel entrances, one common compound-pier reservation, and one short shared wall P–Q before the axial and NE chapel bodies diverge. **Exterior chapel first; work inward toward protected middle ring later.** Do not use discarded outer L01–L14 boundary, polygons or T2/T6 corners. Seven major / fourteen subsidiary outer cells remain conceptual.

## Sources / authority
- Governance: cathedral/governance-r01, CATHEDRAL_MASTER_REFERENCE.md blob SHA `1d7e358ff7562fcc64088854baa2abd3d31a729e` — provisional, not a new approved baseline.
- Saved experiment `Eastern_Chapels_R01_EXPERIMENTAL.zip`, QA SHA256 `f16212f083db150ac568ebee59440423bbad206d2607df3c0c59d32f0814b3da`.
- Saved experiment `Axial_Entrance_Bearings_R02_EXPERIMENTAL.zip`, QA SHA256 `eac9818dfe357f5eb44bf3c10c7ec44ddd8b21b00beb984490a0d14951b7de3f`.
- Extracted protected M_A3/M_A4 source SHA256 `0273f64f4e2791ebbb04b014d5d0a48f81043ef6098b4a2213efef0ff803668e`, **not changed**.
- Previous local 2D study R02 supplied wall-length candidate but its old mouth anchor was *not* retained.

## R03 trial coordinates, numeric native project units (X east, Y north)
- R01 axial north corner: (27274.291016, 1149.618652).
- Newer R02 north entrance bearing and R03 P: (28000,1250). The discrepancy is preserved explicitly.
- Trial Q: (28564.920992,1356.160417). P–Q 574.809326 units; 10.642946° north of east (to recorded numeric tolerance).
- Axial entrance clear chord 2200; companion NE entrance clear chord ~2020.392.
- Trial shared pier reservation 320 × 208, with ~43.42-unit positive gap to **clear opening centerline segments**, insufficient for actual masonry clearance.
- Re-registration: trial axial R01 mass X-shifted +725.708984 and Y scaled by 1250/1149.618652; NE R01 mass translated to put its mouth at P. Original source objects are preserved.

## QA
13/13 limited geometric/source checks passed: finite values, valid candidate polygons, zero overlap of interiors, one exact P–Q common boundary, positive clear openings, no opening-line intersection with pier reservation, and preserved M_A3/M_A4 extraction. This **does not** prove pier capacity, physical SI calibration, rib/arch tangency, wall thickness, saved cathedral 3D registration, or flyer/tower clearance. F5ZL-C missing support schedule remains unresolved.

## Deliverable / reproduction
A versioned conversation artifact `F5ZP_Axial_NE_Entrance_Junction_R03_EXPERIMENTAL.zip` contains the editable SVGs, PNG previews, source JSON extracts, unapproved candidate coordinates, `QA_R03.json`, and deterministic `build_junction_r03.py` (`numpy shapely matplotlib`). ZIP SHA256: `a7829c50eea7c00d1b1fb510df2b1b780d50e870e6f3f6c513a7cbc008019d79`. The script is **not** a replacement cathedral generator.

No geometry, generators or protected baseline changed; experiment deliberately remains unpromoted.