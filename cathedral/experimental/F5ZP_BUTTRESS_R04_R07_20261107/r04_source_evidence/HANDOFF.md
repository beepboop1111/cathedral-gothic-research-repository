# Flying Buttress Generator — Handoff R04

2026-11-06 · EXPERIMENTAL · standalone research tool · no cathedral integration

## Start here

The working generator is `current/flying_buttress_r02.py`; keep `current/base_r01.py` beside it. The R02 filename is retained for continuity; its contents now include modular details, the R03 research assembly and the figure-892 study. R04 names this handoff, not a newly approved generator release.

Read WORKFLOWS.md for commands, SCRIPT_REGISTER.md for every script, and FUNCTION_INDEX.md for actual entry-point line numbers. Previews contains the three latest review PNGs. Historical contains the original R01 and R02 release ZIPs, including their original generators, tests, parameters, QA, Blender and GLB files.

## Current state

- `build(config)` builds the modular R02 system; `build(config, components=[...])` selectively rebuilds detail components. Core parameter changes require a full build.
- `build_system(config, options)` creates the R03 full research assembly: two flyer tiers, optional intermediate support, rectangular/T/stepped receiver sections, compass-defined upper tracery, joined mouldings, geometric stone courses and downhill open gutter/outlet.
- `proportion_studies(config, variants)` builds independent named R03 configurations at the same scale, separated along Y.
- `build_plate_892(study_span=5000., depth=420.)` generates the Ungewitter Volume II, Plate LXXXIV, figure 892 (Freiburg) study using coarse manual raster picks. It does not use the generic stock flyer curve.
- `HISTORICAL_PRESETS` remains a set of unmeasured research leads. Only `PLATE_892` has raster picks and a fitted circle; neither provides a verified physical calibration.
- No current modular/R03/plate .blend or GLB was exported: the user's request at these stages was local code editing and PNG-only delivery. Old release exports are not current-code outputs.

## Baseline and units

Standalone demonstration coordinates: X from receiver toward wall, Y transverse, Z up. Native units have no verified physical conversion. Figure 892 uses the horizontal pixel span 1388−846 = 542 px mapped to a chosen 5000-unit study span; 420-unit depth is conjectural. Source image is 1934 × 2800 px and is preserved byte-for-byte.

No F5ZK-C, F5ZN-A, Pass 6J, approved generator, cathedral model or historical original was modified. Missing F5ZL-C support schedule remains unresolved; M01 remains open. These experiments have no architectural approval or structural sign-off.

The GitHub Master Reference was read during this work: repository beepboop1111/cathedral-gothic-research-repository, branch cathedral/governance-r01, path cathedral/governance/CATHEDRAL_MASTER_REFERENCE.md, blob 1d7e358ff7562fcc64088854baa2abd3d31a729e. It is provisional governance, not authority for these dimensions. No GitHub checkpoint was pushed during these local-only code/PNG stages.

## Evidence and validation

The original release logs are included unchanged under evidence. The current modular, research-system and plate test scripts are preserved and portable. Their fresh execution logs are included with this handoff.

The plate circle fit uses eight manually chosen soffit points. RMS radial residual 3.0025 px; maximum 4.5783 px; radius 622.1732 px; center (1461.1808, 1390.9708) px. Manual pick uncertainty is estimated at ±5 px, not statistically calibrated. Residuals only compare the chosen samples, not every engraving pixel and not historical intent.

Technical mesh checks count edge incidence and degenerate polygons. They do not prove absence of all self-intersections, positive solid volume, masonry bonding, printable union, adequate stone ligaments, geometric bearing contact, or structural capacity. R03 drainage checks positive longitudinal fall only, not hydraulic capacity or fully coordinated roof drainage. Original GLB round-trip tests apply to original releases only.

## Known limitations / next bounded task

1. Figure 892 needs denser tracing of soffit, extrados, coping and opening before calling it a historical reconstruction. The fitted circle approximates the engraving, including scan/pick uncertainty.
2. The pinnacle, receiver depth, engaged shafts and carved ornaments are simplified. Upper wall is a context block. The outlet is geometric rather than a carved gargoyle reconstruction.
3. R03 lower tracery retains the modular four-lobe treatment; the selected new construction rule affects the upper tier. Intersecting circular lobes are an experimental construction, not verified historical tracery.
4. Moulding union cleanup merges near-coincident vertices, dissolves degenerate edges and fills boundary loops. Mesh closure does not establish the intended carved junction shape; inspect close views before adoption.
5. R03 receiver/tower detailing and intermediate-support contacts need architectural coordination. Separate stones have deliberate joints. Adjacent assembly objects may overlap intentionally; do not infer a bonded load path.
6. R03 is a full-build API. The existing selective rebuild interface applies to the modular R02 details, not arbitrary R03/plate component edits.
7. `main()` still invokes modular `build()` and exports R02. It does not dispatch to R03/plate and its JSON key filter excludes custom detail controls. Use the documented Python API for those features.
8. Once the plate profile is refined, review section depth, coping/gutter seating, opening frame and receiver/pinnacle junction. Keep this independent of cathedral architecture until explicit approval.

## Suggested continuation prompt

Continue the standalone flying-buttress generator from Handoff R04. Read HANDOFF.md, WORKFLOWS.md and the current generator. Preserve the historical source and original releases. Refine Ungewitter Plate LXXXIV figure 892 by denser tracing and uncertainty-aware comparison, keeping the 5000-unit span illustrative and depth conjectural. Do not modify cathedral geometry or promote experimental work. Review the figure-892 model's bearing, coping/gutter and pinnacle junctions before adding carved ornament. Deliver only the artifacts requested in the new task.
