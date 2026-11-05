# F5ZP outer-corner alignment — 2D R01 EXPERIMENTAL

User direction: fix the offset; ignore paired lower entrances, central receivers and upper-window positions. This supersedes the prior recommendation to retain the skew, within this new isolated experiment. It does not promote geometry into the approved cathedral.

## Correction

For T2 and T6, intersect the outward perpendicular through the middle-bay frontage midpoint with the existing Study D outer ellipse, center (20213,0), east semiaxis 7169, north/south semiaxis 6657. Choose the outward intersection. Both corners now have zero lateral offset to numerical precision; each moves approximately 226.235 native units from its prior location. This removes the prior +/-225.879 lateral offset and 7.471-degree divider skew. The ellipse dimensions and middle frontage remain unchanged. Exact old/new coordinates and ellipse parameters are in QA_AND_MOVEMENTS.json.

## Dependent changes

- T2/T6 outer polygon corner and corresponding outer passage nodes updated in separate candidate JSON.
- The same shared point is updated in the four affected lower-cell footprints, retaining all fourteen cells. No entrance, receiver width, upper-window position or vertical-level design is developed here. The midpoint-to-corner line is an alignment axis, not an approved support.
- D2/D8 chapel entry-neck endpoints follow the new corner; their chapel bodies remain unchanged.
- D3/D7 exterior compartment boundary candidates follow the new corner. These are exterior program compartment boundaries, not proposed upper-window positions. Their adjoining side explicitly passes through the fixed chapel-body entry junction before continuing along the original distal side. This introduces a local transition in that boundary instead of moving the chapel body. Both original source bodies remain bundled and unchanged in inputs.
- Other D3/D7 passage entry endpoints are snapped to exact passage nodes within the previously documented 0.005 vector-recovery tolerance, eliminating sub-unit sliver overlaps caused by source rounding.
- Other passage sectors and every inner/middle source cell remain unchanged.

## Evidence and validation

PLAN_GEOMETRY.json is recovered R04 Study D plan evidence; LOW14_GEOMETRY.json is the corrected fourteen-low-vault footprint checkpoint. Parent for this experiment is T2/T6 trial commit 55211c62c2f39c4735b6434a03f0365edaecd19c. Governance master blob 1d7e358ff7562fcc64088854baa2abd3d31a729e remains informational; its sources were recovered earlier in this workflow. This pass changes neither live saved cathedral models nor authoritative generators.

27 geometric checks pass: zero offset, ellipse membership, valid polygons, untouched middle frontage and chapel bodies, pairwise no significant overlap among corrected passage/entry-neck/window compartment, positive shared boundary contacts, all protected inner/middle cells unchanged, other passage sectors unchanged, fourteen lower cells retained, north/south symmetry. Boundary contact uses 1e-6 native-unit tolerance and overlap acceptance 1e-5 native units squared. Final SVG parsing and visual reviews are recorded in DELIVERY_QA.json. No saved masonry mesh, wall thickness, 3D contact or structural capacity test is claimed.

## Reproduction

Python 3 with numpy, shapely and matplotlib. Run `python scripts/fix_corners.py`. Inputs are immutable snapshots; outputs are separate candidate JSON, two editable SVG sheets, PNG previews and numerical QA. All dimensions remain native project units; physical SI coefficient is unresolved. SVG sheets are plotted illustrations with coordinate axes, not calibrated CAD interchange files.

Approved geometry, the working inner/middle ambulatory vault generator, selected R05 crossing and Pass 6J records remain untouched. Missing F5ZL-C support schedule stays unresolved. Architectural approval is still required to adopt this correction. Prior skewed studies remain available but their corner layout is superseded within this candidate.
