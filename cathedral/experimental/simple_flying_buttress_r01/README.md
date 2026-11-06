# Simple Flying Buttress — R01

Experimental standalone Blender generator: one circular curved flyer, outer receiving pier, plinth and wall attachment block. No cathedral files or generators are read or modified. Demonstration dimensions are not approved cathedral dimensions or a historical reconstruction. Geometry tests do not establish structural adequacy.

Open output/flying_buttress.blend to inspect the example, or import output/flying_buttress.glb. Preview camera is included in the Blender scene.

## Editing

Open flying_buttress.py in Blender's Text Editor, edit DEFAULTS and Run Script. It rebuilds only its tagged SIMPLE_FLYING_BUTTRESS_R01 collection. Unrelated objects remain untouched. It writes Blender, GLB, parameters and QA into an output folder beside the script. Saving the Blender file includes the current scene; use a separate working file.

Alternatively edit a copy of output/parameters.json and run:

```
blender -b --python flying_buttress.py -- --config my_parameters.json --out my_output
```

For an empty demonstration scene, first use Blender File > New > General and remove default objects, or run with an empty startup file. The generator deliberately preserves unrelated scene objects, including a default cube if present.

## Parameters

| Parameter | Meaning |
|---|---|
| span | Horizontal distance between support center planes |
| outer_landing_z / wall_landing_z | Absolute soffit endpoint elevations |
| arc_sagitta | Circular soffit's bulge above its sloping chord, measured perpendicular to the chord |
| flyer_thickness | Radial thickness of annular band |
| flyer_width | Transverse width |
| pier_depth / pier_width | Receiver size along/across the flyer |
| pier_headroom | Receiver top above its soffit endpoint |
| wall_depth / wall_width / wall_height | Wall reference block dimensions |
| base_spread / base_height | Plinth projection and height |
| segments | Circle tessellation count, 8–512 |
| repeat_count / spacing | Optional repeated units along Y, 1–20 |

X runs from the outer pier to the wall. Y is transverse. Z is vertical. All values use the same demonstration native unit; physical unit conversion is unspecified. Arc center and radius are derived from the two endpoints and sagitta. End sections must fit inside support envelopes. The closed flyer uses a sampled exact circle, rather than a cubic approximation. No voussoirs, taper, pinnacle, gutter, second tier or cathedral alignment is included in R01.

The pier/plinth and flyer/support volumes overlap intentionally for this assembly study; they are separate objects, not a boolean-unified or print-ready model. No bonding, load path, capacity, thrust, drainage or foundation assessment was performed.

## Checks and provenance

verify_and_preview.py tests repeat builds, unrelated-object preservation, invalid parameter rejection, two-unit repetition, and export/import bounds. output/QA.json contains mesh closure checks and arc endpoint residual. output/VERIFICATION.json contains independently rerun checks. Reproduction requires Blender with its bundled glTF importer/exporter; no other Python dependencies.

Parent: new isolated tool, not a replacement for an approved generator. Governance reference read: cathedral/governance-r01, blob 1d7e358ff7562fcc64088854baa2abd3d31a729e. Existing F5ZK-C, F5ZN-A, Pass 6J, R27 and discarded-outer-ring decisions are outside this script. F5ZL-C support schedule remains unresolved. No M01 completion or geometry promotion is implied.
