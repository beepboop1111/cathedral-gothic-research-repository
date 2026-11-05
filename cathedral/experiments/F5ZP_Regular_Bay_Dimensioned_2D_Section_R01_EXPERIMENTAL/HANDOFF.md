# F5ZP regular bay dimensioned 2D section R01 — EXPERIMENTAL

Scope: one regular T4 / M_A4 chevet bay, lower cells L3-07 and L3-08. This develops the user's corrected rhythm: seven inner vaults, seven middle vaults, and fourteen significantly lower third-layer vaults, two per bay with one window above their entrances. No third-layer height is approved or propagated to other bays.

## Drawings

- DIMENSIONED_BAY_SECTION_AA.svg / .png: developed receiving-wall sectional elevation, two pointed lower openings and one upper window, source and trial dimensions.
- RADIAL_SECTION_BB_AND_PLAN.svg / .png: radial level coordination and exact plan locator. Dashed vault zones are projected height envelopes, not recovered vault-web sectional profiles. The central cut crosses the low vaults' common division and the upper window. Wall thickness is unresolved.
- SVG geometry and text are editable. These are dimensioned plotted sheets, not a CAD interchange with an established physical-unit header.

## Dimensions and authority

All dimensions are native project units; physical metres per native unit remains null. Numerical source coordinates retain their original scale. Zero is a working section datum; a surveyed finished-floor level has not been established.

| Item | Native value | Status |
|---|---:|---|
| Bay axis-to-axis chord | 2197.626572 | Recovered plan |
| Each half-bay | 1098.813286 | Derived from plan |
| Each lower clear entrance | 906.813286 | Trial |
| Central receiver width | 192 | Trial |
| Full shared end receiver | 192 | Trial; 96 within this bay |
| Lower entrance spring | 2112 | Trial |
| Lower entrance intrados crown | 2688 | Trial |
| Lower arch ring normal depth | 96 | Trial |
| Third-layer rib/boss crown | 2816 | Trial level only |
| Third-layer web-top allowance | 2880 | Trial envelope only |
| Window clear sill / arch spring / head | 3072 / 3456 / 3776 | Trial |
| Window clear width / height | 576 / 704 | Trial |
| Existing inner/middle spring / rib-boss crown | 3000 / 4296 | Recorded F5ZK-C |
| R2 reference arch apex | 4136 | Recorded; intrados unverified |
| Gallery soffit / floor | 4425 / 4521 | Recorded F5ZK-C; separate 4950 conflict not adopted |

The trial third-layer crown is 1480 below the recorded higher crown. Two-centered circular pointed profiles use exact circle equations. The 96 normal offset of the low entrance arch yields an outer crown of 2786.363496, below the 2816 level. The window frame bottom is 2976, leaving 96 above the trial web-top allowance. Its outer head is 3872.410054. A sampled fit against the source R2 curve minus a provisional 192 vertical planning reserve gives a minimum margin of 71.589946. The reserve is not a measured intrados; this proves only fit inside the stated 2D planning envelope. Rib junction geometry, web curvature, wall depth, loads and structural capacity have not been established.

## Reproduction and QA

Requires Python 3, numpy, matplotlib, shapely. From this extracted folder:

```sh
python scripts/build_section.py
```

Inputs are bundled, with source SHA256 values in inputs/PARENT_HASHES.json. The script checks packaged input integrity, original source integrity when originals are accessible, frontage closure, trial level ordering, circular-arch crowns, provisional frame fit and SVG parsing. See SECTION_QA.json and MEASUREMENTS.json. On the original workspace, all 19 checks pass; on a standalone extraction the 17 portable checks run, with original-path comparisons additionally run when available. Visual review covers both PNG sheets.

## Recovery lineage and protection

- GitHub Master Reference previously recovered from cathedral/governance-r01, cathedral/governance/CATHEDRAL_MASTER_REFERENCE.md, blob 1d7e358ff7562fcc64088854baa2abd3d31a729e.
- Corrected 14-low-vault checkpoint parent commit: 2251f484e3b1bdafaf065dde8349f483bfa996a5.
- LOW14_GEOMETRY.json preserves its exact protected inner/middle footprints and the two-per-bay plan split; F5ZK_C.json supplies recorded dimensions and levels recovered through the R04 package.
- No cathedral mesh, locked dimension, historical original, working inner/middle generator, selected Crossing Full-Cell R05 or Pass 6J record was modified. No 3D output was generated.
- Missing F5ZL-C support schedule remains unresolved. No new structural or architectural approval is implied.

Next architectural review: judge the paired-opening/window proportions and trial levels. After approval, check nonregular T2/T6 footprints separately before applying any levels across all fourteen vaults.
