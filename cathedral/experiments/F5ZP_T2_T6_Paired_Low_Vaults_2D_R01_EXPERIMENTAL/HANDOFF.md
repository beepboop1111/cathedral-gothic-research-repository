# F5ZP T2/T6 paired low vaults — 2D R01 EXPERIMENTAL

## Result

The paired lower entrances and one upper window fit the stated 2D receiving-wall envelope in both irregular bays using the regular T4 trial heights. No height adjustment or footprint change was necessary. This is geometric planning evidence, not approval of architecture, actual masonry clearance or structure.

T2 and T6 are mirrored. Their common divisions follow the existing exterior corners, 225.878922 native units to either side of the normal axis, giving opposite 7.471354 degree skews. Preserve this skew. Equal entrance frontages do not imply identical vaults: lower-cell areas and outer spans differ. Do not replace these cells with rectangular regular-bay copies or propagate an identical web across them.

| Measure | T2 | T6 | Authority |
|---|---:|---:|---|
| Receiving frontage | 2377.732644 | 2377.732644 | Source footprint |
| Each half frontage | 1188.866322 | 1188.866322 | Derived |
| Each clear entrance width | 996.866322 | 996.866322 | Trial |
| Divider outward normal depth | 1722.374619 | 1722.374619 | Source footprint |
| Divider length | 1737.122798 | 1737.122798 | Source footprint |
| Divider lateral offset | +225.878922 | -225.878922 | Derived local frame |
| Straight normal cut plan depth | 1674.433373 | 1674.433373 | Derived; differs from divider length |
| Outer receiver edge spans, in cell order | 2432.193468 / 2373.220930 | 2373.220930 / 2432.193468 | Source footprint |
| Window frame above trial web allowance | 96 | 96 | Trial planning margin |
| Window below provisional upper arch envelope | 71.589946 | 71.589946 | Trial planning margin |

Native units only. Physical metres/native-unit conversion remains unresolved. Exact numerical values are in QA_AND_MEASUREMENTS.json and DIMENSIONS.csv. Local u follows the receiving chord from the first lower cell to the second; v is the outward perpendicular. Global footprint coordinates remain unaltered in inputs/LOW14_GEOMETRY.json.

## Trial levels retained

Lower opening spring 2112; clear crown 2688; third-layer rib/boss crown 2816; web-top allowance 2880. Window clear sill 3072, pointed-arch spring 3456, clear head 3776, clear width 576. Opening rings and window frame have trial normal depth 96. Receiver faces are trial 192: the central face plus 96 of each shared end receiver inside the bay. These widths are face dimensions, not a recovered wall thickness or an approved pier design.

Existing source inner/middle spring 3000 and crown 4296 are preserved. For each bay the recorded R2 reference arch apex is 4136. Its actual intrados/profile orientation is not verified. Subtracting 192 vertically is a provisional planning reserve only. The resulting margin does not establish clearance to actual mouldings, masonry, vault webs or glazing frames in 3D. The gallery 4521/4950 evidence conflict is not resolved or used to alter architecture here.

## Evidence, testing and reproduction

Two editable SVG/PNG sheets show the exact plan beside a developed receiving-wall elevation. They are dimensioned plotted sheets; SVG document units do not establish a physical CAD scale. Black shows protected source set-out and recorded arch reference; gray dashed shows construction; red dashed shows experimental geometry. Both PNG sheets were visually reviewed; corrected T2 annotation follows the same layout as inspected T6.

Run `python scripts/build_study.py` from any directory, with Python 3, numpy, shapely and matplotlib installed. The script reads only bundled inputs and writes this experimental folder. Its 27 numerical checks pass: input hashes, polygon validity, zero lower-cell overlap, no significant middle encroachment, full shared frontage within 1e-6 native unit tolerance, frontage closure, positive clear openings, provisional window fit, level ordering, retained skew and mirror correspondence. Tiny middle intersection area ~1.4e-9 native units squared is floating-point residue; area tolerance is 1e-6. Exact Boolean line coincidence was unsuitable for midpoint roundoff, so shared-frontage coverage uses a documented 1e-6 boundary tolerance. Final SVG XML parsing is separately recorded in DELIVERY_QA.json.

## Baseline and protected decisions

- GitHub Master Reference read from cathedral/governance-r01, path cathedral/governance/CATHEDRAL_MASTER_REFERENCE.md; blob 1d7e358ff7562fcc64088854baa2abd3d31a729e. It remains provisional governance, not geometric authority.
- Parent: regular T4 section checkpoint commit 6d8bd608e9aec5a566be4f33fe961a2f20aef5e2; corrected fourteen-low-vault parent 2251f484e3b1bdafaf065dde8349f483bfa996a5.
- Inputs copied unchanged from the regular section checkpoint: recovered F5ZK-C numeric schedule, exact LOW14 geometry and the same trial parameters. SHA256 source checks are bundled.
- Approved inner/middle architecture, working vault generator, Pass 6J records, Crossing Full-Cell R05, historical originals and numerical scale remain untouched. These are two isolated 2D trials; no 3D modeling or promotion occurred.
- Fourteen low third-layer cells remain the design intent, two per seven parent bays, with a window above each pair. The nine exterior compartments remain a separate program.

## Unresolved and next bounded work

F5ZL-C support schedule stays missing. Actual support/wall thickness, bearing design, web curves, arch intrados, 3D gaps/overlaps, physical-unit coefficient and structural capacity remain unresolved. The parent footprints show plan continuity; actual saved masonry contact is not established by this study.

Next: assemble a consolidated dimensioned 7–7–14 plan retaining these skewed cells, with a receiver and opening register. Any detailed webs, new support dimensions or promotion of trial levels require their own architectural development and approval.
