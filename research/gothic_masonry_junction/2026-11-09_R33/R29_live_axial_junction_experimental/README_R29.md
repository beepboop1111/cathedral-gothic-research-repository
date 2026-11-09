# F5ZP — R29 Live Axial Junction (Experimental)

## Open
Open `R29_LIVE_AXIAL_JUNCTION_EXPERIMENTAL_V02.blend` with Blender 5.0.1 on MR COMPUTER.
The add-on `f5zp_live_axial.py` was installed to `~/.config/blender/5.0/scripts/addons/` and enabled in Blender preferences.
In the 3D Viewport press **N** to open the sidebar, select **F5ZP**.
Change parameters and click **Rebuild Axial Junction**. Click **Save New Checkpoint** to create V03, V04 etc. Reopen the newest version for subsequent work.

## Geometry preservation
The 60 R28 objects in collection `00_R28_PROTECTED_REFERENCE_DO_NOT_EDIT` are copies and locked from selection. They include one camera and 59 geometric objects, with F5ZN-A spring/formeret snapshots and R21/R27 trials. This is *not* the complete authoritative F5ZN-A cathedral model. The original R28 file and protected source files are not edited.
Only the 17 objects in `90_R29_LIVE_GENERATED_EXPERIMENTAL` are replaced by the rebuild button. Before each rebuild the add-on checks a coordinate and mesh digest of the protected reference; it refuses to build if that geometry has changed.

## First procedural study
Editable parameters: axial depth/span, half-width, centerline, inner/outer springing Z, transverse pointed rise, longitudinal crown lift, web thickness, rib radius, and experimental receiver block dimensions.
All measurements are in original native 1:1 units; **no physical real-world conversion has been established.** The generated pointed arches use a two-centered construction. The trial webs, ribs and receiver blocks are exploratory and do not reproduce or replace the validated V13 generator.

## Validation, source of truth and limits
- Original R28 file SHA-256: `5fe369f63f10119642a9f7dcc07b111ba1fab93e15f60a17da7e07f247df8587`.
- `R29_LIVE_QA.json`: first build/reference/rebuild validation.
- `R29_REOPEN_QA.json`: fresh-reopen, add-on registration, repeated rebuild and manifold web/receiver checks.
- R28 reference objects remain unaltered, including coordinate transforms and mesh data.
- Architectural and structural validation: **not passed / not performed**.
- Still unresolved: authentic F5ZL-C receiving-masonry schedule, transition to validated V13 webs, 700-native-unit spring difference, chapel arrangement choice, masonry bond, foundation and thrust, physical scale conversion.
- Do not use these objects as an approved M01 model without further evidence and review.

## File preservation
`R29_LIVE_AXIAL_JUNCTION_EXPERIMENTAL_V01.blend` = first procedural build.
`R29_LIVE_AXIAL_JUNCTION_EXPERIMENTAL_V02.blend` = saved checkpoint created by testing the Blender button after fresh reopen.
`f5zp_live_axial.py` = editable source. A copy of its initial text is embedded inside V01/V02, but running the add-on loads the installed Python module. After deliberately editing the add-on source, restart/reload the module and verify its hash tests before saving another checkpoint.

## Next architectural study
Align this procedural interface with measured, approved inner/middle spring boundary curves; test continuity of actual shared pointed arches, web seams and bearing faces. Preserve R28 and all protected cathedral source files. Keep proposed masonry experimental.
