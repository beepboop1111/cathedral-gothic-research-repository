# F5ZP R04 — floor plan with vault connections

Start with `WHOLE_FLOOR_PLAN_CONNECTIONS.png`, then `CHEVET_779_CONNECTIONS.png` and `VAULT_CONNECTION_OWNERSHIP.png`. SVG companions are editable presentation drawings. `CHEVET_779_NATIVE_COORDINATES.svg` retains native project coordinate numbers; the SVG group reverses display Y to show north upward. Physical metre conversion remains unset.

The study coordinates the selected **7–7–9 Study D** arrangement with the nave/choir/transept grid and unchanged R05 crossing concept. It does not rebuild vault meshes or the protected generator.

## How seven connects to nine

| Passage panel | Saved middle bay | Exterior frontages |
|---|---|---|
| T1 | M_A7 | D1 |
| T2 | M_A6 | D2, D3 |
| T3 | M_A5 | D4 |
| T4 | M_A4 | D5 |
| T5 | M_A3 | D6 |
| T6 | M_A2 | D7, D8 |
| T7 | M_A1 | D9 |

T2 and T6 have five vertices: two existing inner support endpoints and three outer endpoints. This accommodates the extra outer divisions without adding inner piers. The passage remains a continuous route. T1–T7 are separately named receiving panels; the shorthand 7–7–9 is a program/topology statement, not a certificate that exactly 23 completed vault meshes have been built.

Black outlines reproduce protected set-out or measured working-source boundaries. Thin gray dashed lines are diagram guides, not a recovered detailed rib network. Red dashed outlines show new experimental chapel-entry necks, Q5 receiving strips and shared-owner overlap reservations. The D5 +640 trial outline is gray dashed and **not adopted**.

## What changed

- Recovered the actual selected nine-compartment outer arrangement instead of repeating the old seven-sector outer reference.
- Added five candidate necks joining existing chapel body entry edges to the outer passage frontages. They are parts of their chapel compartment, not extra independent vaults or piers.
- Kept the two recorded Q5 outer collars and represented the four inner/middle boundary offsets with plan-only receiving strips.
- Reserved each positive-area compartment overlap to B1/B3/B6/B8 once; no duplicate ownership. Reservations are not finished stonework or approved divider widths.
- Added the documented transept lateral bands omitted from the previous reconstruction object list; retained the source choir taper and marked unresolved lower subdivisions.
- Preserved the selected R05 full J11 footprints and retained J12/J13 references.

## Recovery accuracy and limits

The original MP-01D PDF survives but its companion native D4/D5 JSON/SVG was not recovered from the searched locations. The script reads the PDF's **vector paths**, not raster pixels, derives the plot transform from R2933 and independently checks R4085/R5285. The recovered coordinate error is below 0.005 native units. The ten outer ellipse entry stations reproduce the source window entry points within that tolerance. These are reconstructed source coordinates, not original generator parameters or new approvals.

Recovered D5 contains the unapproved F5ZN-D6 +640 tip. R04 uses its unchanged entry face only to study a neck; it neither reverses that extension by inference nor promotes its terminal footprint. The selected cap still needs the D4/D5 source.

MP-01D and saved F5ZN-A number the identical symmetric geometry in opposite north/south order. The table above records that mapping. The separate protected 30°–150° historical angular record remains unresolved; it is not silently superseded.

The new necks increase the shared-owner overlap masks beyond the earlier body-only overlaps; exact before/after areas are in `PLAN_QA.json`. They need architectural review. Zero residual duplicate ownership in 2D is not masonry bonding, clear-opening verification, vault-web contact or structural capacity.

The gallery schemes 4521 and 4950, Q1 5400/5429 conflict, physical units and missing F5ZL-C support schedule remain open. Special N10/Q1/T1 lower subdivisions, detailed high-vault rib plans and actual adjoining pier/wall solids are not certified by the macro plan. Gray diagonals are explicitly diagram guides.

## Reproduce

```bash
python -m pip install numpy shapely matplotlib pymupdf
python scripts/build_plan.py
```

The script reads only included inputs and writes only this versioned experimental output directory. It does not run or modify any cathedral generator or source model. `PLAN_QA.json` includes interface, source-footprint and exclusive-ownership checks. `PLAN_GEOMETRY.json` and `CONNECTION_REGISTER.csv` carry measured coordinates, lengths and status.
