# M04 R03 — Recovered original Pass 6J coordinate registration to the M02 plan

The exact recovered station in original source coordinates is (869.278779,3000,4089.635119), bearing 78 degrees from local north, with radius 4181. The F5ZN-A origin is (20213,0) and original chevet boundary schedule retains 78 degrees. The world-space Blender Z-up transform is (20213+original Z,original X,original Y). This maps R1 78 to the original I_A3/I_A4 support gap. Original nominal R1 radius 4085; +96 radial station discrepancy remains architecturally unexplained.

## Blender glTF import
Source GLB is Y-up. Blender automatically converts it to (srcX,-srcZ,srcY). Thus, the **post-import** Blender transform is (20213 - importedY, importedX, importedZ), NOT the source-space permutation again. The initial incorrect export was quarantined and is NOT included here. The corrected exported GLB was independently re-read, with the true source original 313940 faces and world-coordinate bounds verified within 0.003 source native units. Its original mesh is non-watertight; it has not been remeshed or falsely marked a solid physical support.

## Actual geometry and remaining interfaces
Three original Pass6J source variant GLBs were sliced at 68 horizontal elevations. At tested Y2705–2999, 2D source vault footprints do not overlap original pier shafts. At Y2600 the articulated lower plinth overlaps the protected I_A3 and I_A4 2D vault footprints by 531.08175 native-squared units. The original narrow smooth plinth overlaps by 1743.1344. At Y3259 all three models show a small 37.305236 area overlap of the projected vault footprint; this may correspond to raised spring/tas geometry and must not be called a 3D structural collision without vertical coordination.

**Architectural approval withheld.** The already-approved Pass 6J mesh was not modified and the protected vault polygons were not changed. The 96-radius offset, base clearance, upper joint, physical bearing topology, missing F5ZL-C schedule and actual structural capacity remain open. No generic R1 section was blindly copied to the remaining six internal/terminal supports. Fourteen lower outer experimental subdivisions remain excluded.

## Reproduction
- python3 M04_R03_REGISTER_ORIGINAL_PASS6J.py
- python3 M04_R03_DENSE_SECTION_SWEEP.py
- blender -b --factory-startup --python M04_R03_BLENDER_REGISTER_AUTHENTIC_PIER.py
- python3 M04_R03_PACKAGE_AND_VALIDATE.py

Original files are bundled read-only. The scripts expect the user's existing 1:1 cathedral workspace tree and fail instead of overwriting an existing validated checkpoint. GitHub not used.
