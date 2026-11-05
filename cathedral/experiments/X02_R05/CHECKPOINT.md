# X02 R05 — passage bearings, vestibule clearance and roofs

EXPERIMENTAL architectural development, 5 November 2026. No approved baseline promotion.

## Actual saved starting model

R04 east-range 2D model: `sources/R04_GEOMETRY.json`, SHA-256 `54e2066ba97b2b787f2976b07c055fa9a4053087a9d3504f88617a06618c52a5`. Its checkpoint SHA-256 is `7faf6926e2f1c171f35c40bafeb8a0362f3cff7221308e9aa0a9ca83eb2ee889`. All 24 archived R04 manifest entries verified locally, and geometry/checkpoint hashes match the saved copies at `/home/christopher/Desktop/F5ZP_X02_R04_EAST_RANGE_AND_STAIR` on MR COMPUTER. R04 is the current experimental component model, not an approved cathedral master.

The GitHub master reference was retrieved again from `cathedral/governance-r01`, `cathedral/governance/CATHEDRAL_MASTER_REFERENCE.md`, unchanged blob SHA `1d7e358ff7562fcc64088854baa2abd3d31a729e`. Its provisional governance entries are retained with their authority limits. The current user assignment authorizes isolated R05 development from R04.

## Retained controls

Metres, true 1:1. Architectural X east, Z north, Y vertical; GLB uses the same Y-up coordinates. Blender imports to native Z-up with X unchanged and native Y=-architectural Z. No display scaling in exports.

R04 principal footprints, six upper chambers, ground rooms, passages, 4.40 m stair turret, FFL 0.000/+3.600, 180 mm deck, 20 x 180 mm risers and 19 saved treads retained. The protected stair envelope is +5.700 m. R04 source files remain byte-identical. Mesh-only plan coordinates snap to a 0.00001 m grid to remove overlay slivers before float32 GLB export; analytical set-out remains in the JSON.

## Architectural bearing arrangement

Light timber-framed upper passage walls sit over two longitudinal girder lines, X=-29.700/-27.600. Eight new R05 masonry piers, nominal 0.70 x 0.70 m, occur at Z=27.650/32.600/35.400/40.250. Each girder end has 350 mm nominal bearing, 0.105 m² contact area. Three pieces per line span the south gap, vestibule and north gap: clear spans 4.250/2.100/4.150 m.

Nominal girders 300 mm wide x 450 mm deep, top +3.420 and underside +2.970. The 180 mm floor zone brings FFL to +3.600. These are modeling assumptions, not calculated member or bearing capacities. Joists span across the link between girder lines. Foundations, fixings, timber loads/deflection, masonry stresses and lateral stability remain structurally unresolved.

The eight piers are **new experimental R05 supports**. They are not substitutions for the missing F5ZL-C schedule.

## Vestibule clearance

The west vestibule has a flat timber ceiling under the passage; it does not force a shallow pseudo-Gothic masonry arch below the retained floor. Pier faces leave 2.100 m width; the 1.800 m route band avoids all piers. Girder underside gives 2.970 m height. Vestibule walls below the crossing stop below the upper floor rather than penetrating the upper passage. Both ground and upper route volumes were checked against the actual modeled solids.

The eastern approach retains a taller roof, underside eave at the wall +4.000 and ridge +5.750. Window/door head detailing and any future decorative arch or vault remain separate decisions; no historical vault has been invented or replaced.

## Roof composition

Main residential gable: wall-plate underside +6.350, ridge +12.100, 45°. Narrow southern neck: same plate, ridge +9.850. Link: plate +6.350, ridge +7.310, slope 0.8 (38.66°). Night range: plate +6.350, ridge +9.150, 45°. Turret octagon: outer eave underside +6.050, apex +9.550. Chapter pavilion: outer eave underside +5.300, apex +11.600. Roof skin has 180 mm vertical thickness. Roof schedules explicitly distinguish underside from outer top elevations.

Overlapping roof planes are trimmed to their visible upper envelope. Vertical upstands close roof steps at the neck/link/main volume junctions. Their weathering, flashings and drainage remain to detail.

Upper room ceiling control +6.300 gives 2.700 m clear above FFL. Generated roof underside minimum over the upper stair landing is +6.997917, giving 3.397917 m to roof skin; minimum over the saved treads is 3.880739 m. These are checks against the generated roof skin, not promises about future rafters, ties, ceilings or services. All must preserve +5.700 over the stair.

## Validation and review limits

The QA report records every check: recovered source checksum; pier seat containment/contact area; vestibule route; ground/upper 3D clearance volumes; roof coverage/nonoverlap; per-tread roof headroom; upper room ceiling clearance; finite, nondegenerate, closed individual mesh shells; GLB framing. Adjacent components intentionally overlap/contact as an assembly; no unioned fabrication solid is claimed.

The final GLB was imported in Blender 5.0.1, validated without repairs, and saved as an editable scene. Import QA records object count, native axis bounds and metre scale. A native render is included. Exhibit was not available in this session. Architectural set-out and technical/geometric checks do not establish structural adequacy, fire/escape compliance, historical authority or user approval.

## Protection and continuation

F5ZK-C, F5ZN-A, approved cathedral geometry, the working inner/middle ambulatory vault generator and Pass 6J records remain untouched. **F5ZL-C's missing 248-support schedule remains UNRESOLVED.** Existing chevet angle/dimensional authority discrepancies are outside this study.

Next bounded work: assess the proposed timber/masonry support sizing, then detail roof valleys, gutters, flashings and the chapter entrance. Continue in a separate experiment until the user accepts the architectural scheme.

