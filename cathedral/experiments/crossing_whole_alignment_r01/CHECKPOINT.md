# F5ZP — Whole-cathedral 2D alignment / Physical scale gate R01

Date: 2026-11-05
Status: EXPERIMENTAL / numerical alignment VERIFIED; certified physical-metre conversion UNRESOLVED.
No approval promotion and no changes to locked geometry or authoritative generators.

## Baselines and source evidence
- Active preferred crossing concept: Crossing_Full_Cell_R05, selected full J11 masonry in all four crossing corners, J12/J13 remain vaulted, 4,970 native-unit central clearing.
- Parent experimental drawing: F5ZE corrected master 2D plan, not a verified whole-cathedral building-solids model.
- Current R05 GLB and parent geometry are immutable source copies.
- Recovered MR.COMPUTER source: `F5ZE_GLOBAL_COORDINATE_DATA.json` (source SHA256 3c30934df8663e0e13903eca30e192aa9a4313f2822dfcb49615ef51ef06e84f).
- Recovered MR.COMPUTER source: `CATHEDRAL_F5ZE_FULL_CORRECTED_MASTER_PLAN.json` (source SHA256 378d3a7875b98ac0a03c2425ebf71427c9cf9deeb2d33b15d5ae760a65e5d354).
- Reconstructed F5ZE `MasterPlan_V02_Experimental_Geometry.json`: 157 reference objects / 21 chevet cells; 203 project checks reported; this reconstruction is not an approved physical masonry inventory.
- Governance master `cathedral/governance-r01`, SHA 1d7e358ff7562fcc64088854baa2abd3d31a729e.

## Alignment result (native X east, Y north)
The crossing origin is (0,0) in both documents. The source crossing half-width is 2933 in F5ZE and R05. F5ZE first/second lateral bands 4085 and 5429 agree with the R05 J11/J12/J13 sequence. 
Registration matrix R05 -> F5ZE 2D: 
```
[[1,0,0],
 [0,1,0],
 [0,0,1]]
```
No move, rotation, mirroring or size change.

Global F5ZE native 1:1 reference station schedule:
- Nave west-to-crossing: [-40013,-36269,-32597,-28997,-25397,-21797,-18197,-14597,-10853,-6965,-2933]
- Choir crossing-to-chevet: [2933,6965,10709,14165,17333,20213]
- Transept north: [2933,6965,10709]; south mirrored.
- Chevet center (20213,0), MP02 *provisional* radii [2933,4085,5285,6657], angles [0.5,27.5,53.5,78,102,126.5,152.5,179.5].
- The MP02 mapping is not proof of F5ZK-C approved scene yaw. F5ZK-C reported centers 30°,50°,70°,90°,110°,130°,150° are protected and not silently reconciled.

## Explicit SI scale gate
No source establishes a verified *metres per F5ZE project unit*. Earlier X02 cathedral-fragment mapping X=1.3*x/1000, Z=1.3*z/1000+2.7584 is an experimental precinct frame, NOT evidence to rescale whole cathedral. The new alignment holds `physical_m_per_native_unit=null`. No metric scale bar or false dimensional claim. A reusable evidence-gated calibration helper is included in the local ZIP; it takes one positively measured physical datum and source reference to compute a *candidate*, never an auto-approved scale.

## Generated results (local review package)
- `F5ZP_Whole_Cathedral_Alignment_R01_FOR_REVIEW.zip`
- `F5ZP_Whole_Cathedral_Alignment_R01/F5ZP_Whole_Cathedral_Masonry_Overlay_R01.png`, SHA256 c4883de211e6926a3fdc65190f828e5eeb019eb0a72d10647e8773fd71af7668.
- `F5ZP_Whole_Cathedral_Alignment_R01/F5ZP_Whole_Cathedral_Alignment_1to1.svg`, SHA256 23e281d790b077802cb81bb2bc8c9fd4b8166d1f49a9005cc05b642640db9f0f.
- `F5ZP_Whole_Cathedral_Alignment_R01/F5ZP_Whole_Cathedral_Aligned_Study_R01.glb`, SHA256 0b56e85ace3d6ad9bf3030c40da4007e49d47777099fa033e1634ff92e5f917d.
- Reproduction script `build_alignment.py` SHA256 f432091e0ff8fb8b814daf9da419e6d832647930e8926f0acb7bc525f34c9376.
- `ALIGNMENT_QA.json`, SHA256 bac145ae36e43c7b3968494a01d2ead0d1caee81458a4a20d6e3ef1600cb6b6e.
- `REGISTERED_FRAME.json`, `MASTER_STATION_REGISTER.csv`, `calibrate_from_measured_length.py`, `README.md`, `SHA256SUMS.txt`.

## Tests actually performed
- 15/15 explicit native-coordinate/plan-area/adjacency checks PASS.
- Four full J11 masonry cells: 1,327,104 units² each, completely covered (zero missing area).
- Four combined core-and-cell masonry footprints: 1,929,216 units² each.
- Open central crossing: unchanged 4,970-unit width; crossing overlap zero.
- Eight J12/J13 cells: zero source masonry area overlap.
- Source R05 GLB 118 mesh geometries retained, 524 new detached diagram guide meshes, combined GLB 642 meshes, parsed on reimport.
- SVG XML parsed; PNG visual inspected; ZIP integrity tested.
- The GLB is a new reference assembly, not an alteration of source R05.
- No Blender GUI or Exhibit inspection claimed for this new exported GLB.
- This confirms numerical fit only. No structural verification, physical metre calibration, approval of chevet mapping or masonry placement decisions.

## Protected and unresolved
F5ZK-C, F5ZN-A, Pass 6J, confirmed 14 inner/middle ambulatory vaults and generators untouched. F5ZL-C 248-support schedule missing. Q1 radius 5400 vs 5429 and gallery 4521 vs 4950 remain conflicts. Outer ambulatory, F5ZK-C angular mapping, other masonry solids, foundations, high-vault bearings, loads, thrust and whole-building SI units remain unresolved.

**Gate for physical unit conversion:** obtain and verify one actual dimensional reference with measured native endpoints, derive metres/project-unit independently, then compare across second reference dimension before promotion.
