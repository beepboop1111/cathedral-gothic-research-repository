# M04 P01 shared Gothic profile library

Real 38-image upload ZIP produced 50 separately identifiable connected dark silhouettes. 49 were vectorized directly by the existing SPRINGER_PROFILE_INPUT_R11 Python converter into its exact springer_png_section_v1 JSON schema, with separate editable SVG. Profile 11 contains an actual internal opening, which R11 rejects: preserve the image and flag for further user review instead of silently filling it.

All five soffits remain separate and optional. Scale is freely adjustable with a single uniform multiplier per section; geometry preserves the raster proportions. Local face/nose direction (R11 provisional up) is not historically verified, so this cannot select a profile automatically.

The original R05 bearing identities, R06 source pier outline and R08 experimental receiver were read only. Against R06 218 protected clear-vault cells and seven confirmed first walls, 1,056 provisional width variations did not intrude. At Y3000/Y3259, 1,056 further tests measure coverage against the incomplete R08 trial receiver. All results use provisional 42%-depth anchoring: do not call them actual Gothic springing fits. The F5ZN-A carrier formerets differ from the older V13 U1 members.

Blender 5.0.1 created a mesh-catalog view of the 49 actual compatible 2D contours; independently reimported GLB confirms 49 geometrically closed solids after welding duplicate glTF normal-seam vertices. This is interoperability QA only, not building the arches. No approved source files or GitHub were modified.

Reproduce: python3 M04_P01_SHARED_R11_PROFILE_LIBRARY.py; python3 M04_P01_R08_PROFILE_BEDDING_COMPARISON.py; blender -b --factory-startup --python M04_P01_BLENDER_R11_CONTOUR_IMPORT.py; python3 M04_P01_PACKAGE_FINAL.py.
