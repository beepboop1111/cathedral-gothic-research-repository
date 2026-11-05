# Axial chapel R03 — complete experimental development package

## Result and status
Generated and inspected: entrance extension into first bay; a second rising bay; five-faced polygonal apse; five ambulatory vault-web panels on four ground bearings; 600-deep threshold barrel web; eight chapel-bay web panels; six apse panels; moulded arch/rib profiles continued into matching engaged shafts; composite respond cores; lancet wall apertures, simple mullions and removable glass; separate pitched and polygonal roofs. All are EXPERIMENTAL, not promoted to approved/locked geometry.

## Governing baseline and changed scope
User freed the old outer ring to work inward. No old T4 edge, T2/T6 corner or 14-cell footprint governs this development. The authority for the inner interface is the exact XY chord of source M_A4 in BASELINE.json (SHA256 066027d5fa0e673b5c267718e906d105c86272b6358fcc8bf2a33a5d3fa92a19). The working inner/middle generator, F5ZK-C/F5ZN-A saved architecture, Pass 6J, Crossing R05 and originals are untouched.

Parent: Axial_Entrance_Bearings_R02_EXPERIMENTAL.zip, latest supplied copy libfile_c695dc21986c819190918b0332c9ea75. Its build script and QA byte-match our prior R02. Parent QA hash eac9818dfe357f5eb44bf3c10c7ec44ddd8b21b00beb984490a0d14951b7de3f. GitHub governance retrieved from branch cathedral/governance-r01, CATHEDRAL_MASTER_REFERENCE.md, blob 1d7e358ff7562fcc64088854baa2abd3d31a729e. Governance is provisional; the current user instruction frees outer geometry. No new live MR COMPUTER inventory was claimed.

## Retained R02 dimensions and dependent changes
Retained: entrance X28000–28600, 600 depth, 2200 clear width, spring Z1800, soffit crown Z3750. Four rectangular depth bands and round ribs are replaced by designed moulded orders and profiles.

The front ambulatory rib spring shifts from X27900 to X28000 to share the actual entrance-arch plane. Ambulatory boss Z3600 becomes Z3620 so those longer circular branches rise monotonically. The axial ridge meets the arch back crown Z3923.328219393, rather than its intrados soffit. This allows the web shell and rib back to share a defined curve while the moulding projects inward below it. These are changes to an unapproved experiment, not to locked architecture.

## Dimension schedule — native 1:1 project units
| Component | X extent / boss X | Crown Z | Notes |
|---|---|---|---|
| Middle receiving chord | X25382.51006987816 approximately | Unresolved actual saved elevation | Exact endpoints in input and QA; XY only |
| Ambulatory boss | 26700 | 3620 | Four ground bearings, five web panels |
| Entrance | 28000–28600 | 3750 soffit | Back crown 3923.328219, 2200 clear |
| First chapel bay | 28600–31000 / boss29800 | 4150 boss | 2400 long, 2500 wall-to-wall |
| Second chapel bay | 31000–33400 / boss32200 | 4400 boss | 2400 long, 2500 wall-to-wall |
| Apse | From33400 / boss33850 | 4550 boss | Five external facets |
| Roof | Eaves4100 | Ridge4500,4600,4900,5150,5350 | Piecewise planar, separate objects |

Spring Z1800 is held throughout this experiment. It is not an assertion that the recovered middle-ambulatory saved vault springs at that elevation. Physical metres/native-unit remains unresolved; glTF's default metre convention must not be mistaken for verified conversion. JSON retains full source precision. Blender/global mesh coordinate storage is single precision; export bounds agree within the measured tolerance, not symbolic exactness.

## Profiles and construction
PROFILES.json and PROFILE_SECTIONS.svg contain new experimental vector sections with paired rolls, hollows and projecting keel: rib141.25 wide x132 deep; major179.3875 wide x150 deep; ridge87.575 wide x81.84 deep. These are designed sections, not recovered historical U1/U4/U5/D profiles or an approved profile substitution. Solid respond cores sit behind engaged shafts; the same profile rows meet at springing with no added fan-shaped transition. Individual meshes intentionally intersect at shared masonry cores and bosses; no boolean-unioned manufacturing mesh is claimed.

Major arches use concentric two-center circular curves and mitred pointed crown intersections. Diagonal branches are circular in vertical planes. The small axial ridge is a smooth interpolation and is not asserted to transfer structural loads as a principal rib.

Web intrados are triangular boundary-interpolated surfaces constrained to their rib/boundary curves; each has a 45-unit vertical extrados offset. They are newly generated studies, not recovered V13 webs, and do not replace the working ambulatory generator. Boundaries agree analytically; the exported tessellations have finite sampling, so this is not a claim of a boolean watertight combined vault. Roof clearance is sampled rather than a proof of continuous minimum.

## Validation actually performed
18/18 recorded checks pass, including profile validity, boundary evaluation, matching spring sections, monotonic circular branches, retained entrance soffit, roof samples, mesh face validity, and GLB reload.

- Maximum analytic web-boundary residual: 4.54747e-13 native units.
- Maximum shaft-to-sweep section residual: 2.27374e-13 native units.
- Minimum sampled web-extrados-to-roof-underside clearance: 221.752691 native units across 4700 sample points.
- Full GLB: 253 source / 253 reimported meshes; world-bound error 0.0.
- Roof-off GLB: 240 meshes; roof objects absent.
- Faces are nondegenerate; mesh coordinates finite. Source input hash rechecked unchanged.
- Exterior, cutaway and interior images visually inspected. Longitudinal section extracted from actual saved mesh triangles at Y=0; not a hand-drawn substitute.

Initial interior preview showed depth/shadow artifacts; camera clipping was adjusted and interior Workbench shadows/cavity disabled. Final view is a geometric studio preview, not a daylight simulation. No Exhibit capability was exposed; validation used Blender rendering and actual GLB reimport.

## Review and reproduction
Open Axial_Chapel_R03_EXPERIMENTAL.blend. Named collections: protected plan, floors, responds, arches, ribs, webs, walls, roof, bosses. Hide ROOF or WEBS for inspection. Full model is saved, while CUTAWAY.png temporarily hides the roof, near wall and selected web panels. Axial_Chapel_R03_FULL.glb and Axial_Chapel_R03_ROOF_OFF.glb are separate views of the same generated geometry.

EXTERIOR.png, CUTAWAY.png, INTERIOR.png, PLAN.png, MEASURED_REVIEW.svg/PNG, PROFILE_SECTIONS.svg, DIMENSIONS.csv, full QA, input records and procedural scripts included. Original R02 is preserved separately.

Reproduce with Blender4.3.2 and Python3+numpy+matplotlib+shapely:
1. `blender -b -t 4 --python build_chapel.py`
2. `blender -b -t 4 --python extract_sections.py`
3. `python draw_review.py`

## Unresolved / no promotion
This establishes a generated spatial/geometry study, not historical or structural validation. F5ZL-C support schedule remains missing. Actual middle-vault spring levels and bearing interfaces, foundation/masonry capacity, spring-cluster bonding, final pier sizes, roof drainage/flashings, companion chapel joins, buttress/flyer landings and whole-cathedral window/roof clearance remain unresolved. The complete axial chapel is not approval to replace the cathedral baseline. Suggested next bounded review: assess the interior progression and entrance scale, then coordinate the actual middle-vault elevation before companion chapel integration.
