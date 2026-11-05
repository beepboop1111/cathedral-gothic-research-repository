# X02 R06 — overall context review

Status: EXPERIMENTAL REVIEW COPY, 5 November 2026. No architectural geometry changed or promoted.

## Sources and current saved model

The actual saved component is `/home/christopher/Desktop/F5ZP_X02_R05_BEARINGS_AND_ROOFS/outputs/F5ZP_X02_R05_EDITABLE.blend`, SHA-256 `8caeef538cc639e4de0ef02390fd8731004aaff159c03f6004f72e6ed844c2e8`. This differs from the delivered file hash. Read-only Blender comparison found all 151 mesh names, world vertex coordinates and polygon indices identical to the delivered R05 GLB. Treat the saved-state change as non-geometric; the user's saved file was preserved. The review copy loads this current saved file.

R03 precinct plan, R04 active footprints, R05 roof planes and the inherited R02 cathedral fragment are copied under sources. SOURCE_HASHES.json records exact bytes. R03 bodies/walls have repeated names; roles are resolved explicitly. R05's 4.40 m turret and developed roof/room/stair geometry remain the active experimental east-range study. Other wings use the R03 footprint references.

The GitHub master reference was retrieved from `cathedral/governance-r01`, `cathedral/governance/CATHEDRAL_MASTER_REFERENCE.md`, unchanged blob SHA `1d7e358ff7562fcc64088854baa2abd3d31a729e`. It remains a provisional governance compilation.

## Coordinate and authority boundary

This review retains metres and 1:1 dimensions within the existing experimental precinct frame: X east, Z north, Y vertical. Blender uses X, -Z, Y. No display scaling was applied to architecture.

The cathedral context is ONLY the inherited X01/R02 north-wall fragment and twelve root polygons. Its source transform is `X=1.3*x/1000`, `Z=1.3*z/1000+2.7584`. It is explicitly experimental and is never applied to approved cathedral geometry. The recovered MasterPlan_V02 report separately states that physical conversion of native project units is not established. A reliable whole-cathedral model aligned in this frame was not recovered for this review. Consequently there is no whole-cathedral roof-height or flying-buttress clearance conclusion.

`Cathedral_F5ZP_G40_Working.blend` was also screened read-only: 399 objects, 377 meshes, Blender units NONE, and mixed labeled 1:16 references/1:1 junction studies. It is not a registered whole-cathedral context source for this review and was not merged or rescaled. Its exact hash, collections and bounds are recorded in sources/G40_CONTEXT_SCREEN.json.

The protected southern scheme remains unplaced: its exact X location and source lock are unresolved in R02. It is not synthesized or merged into the northern experiment.

## Review assembly

The R06 Blender/GLB assembly retains all 151 R05 meshes and adds a separately named collection of 58 display-only plan guides. Other wings, courts, cloister outlines, routes and cathedral fragments are flat footprints/lines at tiny drawing-layer offsets. These offsets distinguish overlapping guides; they are not building heights, floor decisions or terrain. Other-wing/cloister roofs are deliberately unmodeled rather than invented for the review.

Two native renders show the overall plan context and the view toward the east range. The PDF adds an overall 1:250 plan, source-status legend, measured roof hierarchy and review findings. The SVG is physical 1:1 in the inherited precinct frame.

## Findings

1. Retain the R05 composition provisionally. The chapter house remains distinctive by octagonal form and placement. The residential outer ridge is +12.280 m, chapter outer apex +11.780 m: a difference of 0.500 m. These compare developed R05 volumes only. The remaining precinct and cathedral heights are not sufficiently established to justify lowering the residential roof now.
2. The 15 x 19 m garth is 285 m², with no R05 roof projection over it. This is not a claim about future cloister roofs, daylight or shade.
3. The exact named R03 chapter-court polygon is 37.301515 m². R05 roof projection covers 15.211788 m² (40.780616%); 22.089727 m² remains uncovered by R05. These are horizontal plan areas, not daylight metrics. The upper link creates a covered edge and changes this court's open character.
4. The inherited N4 route avoids the twelve available root polygons with a minimum 0.195600 m horizontal margin. The actual portal jambs/opening, CH-N5 exterior and flying support geometry remain unverified. The reference chapel footprint is a red unresolved guide, not the actual recovered chapel.

## Validation actually performed

Twelve focused source/plan checks pass. Blender verifies the original 151 mesh signatures unchanged before and after adding context, and source file bytes unchanged. Review assembly: 209 mesh nodes (151 architecture + 58 diagram objects), metre scale in the stated frame. GLB framing/parsing, finite coordinates, three PDF page bounds, SVG XML and final render/layout review are recorded separately. Display-only footprint surfaces are intentionally not closed building solids.

Technical and geometric review does not establish architectural acceptance, historical authority, structural capacity, drainage adequacy or regulatory approval. No source generator was executed or rebuilt.

## Preserved / unresolved

F5ZK-C, F5ZN-A, approved geometry, the working inner/middle ambulatory generator and Pass 6J remain untouched. F5ZL-C's missing 248-support schedule remains UNRESOLVED. Whole-cathedral scale/frame and height context, actual N4/CH-N5 interface, flying supports, other-wing roof heights, site boundary and structural capacities remain unresolved.

## Next bounded task

Recover and coordinate the actual N4/CH-N5 cathedral entrance and confirm the desired chapter-court openness. Keep R05 roofs unchanged until those context decisions have evidence. If a hierarchy issue remains in verified full context, compare one isolated lower-ridge option in matched views before any promotion. Detailed mouldings and drainage hardware are later tasks.

