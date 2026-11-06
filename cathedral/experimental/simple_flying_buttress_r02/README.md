# Simple flying buttress — R02: tracery and receiving tower

R02 adds a pierced spandrel, sloping coping, stepped receiver tower and pyramidal pinnacle. These are experimental design forms using demonstration units. R01 remains unchanged. No cathedral geometry, historical source image or approved generator is edited.

Open output/flying_buttress_r02.blend or import output/flying_buttress_r02.glb. The five quatrefoils are actual through-openings, not surface textures. The circular load-bearing flyer below them retains its R01 vertices. The panel, coping and supports are separate overlapping objects, not bonded construction geometry or a single print-ready solid.

## Run and edit

Keep base_r01.py beside flying_buttress_r02.py. In a separate Blender working scene, open flying_buttress_r02.py in the Text Editor, edit DEFAULTS/OPTIONS and Run Script. Only its own tagged R02 collection is rebuilt. Unrelated objects and any R01 collection remain untouched. Outputs go into output/ beside the script; saving includes the current scene.

Command line:

```
blender -b --python flying_buttress_r02.py -- --config output/parameters.json --out another_output
```

Use an empty Blender startup file for an isolated demonstration; otherwise unrelated starting objects remain in the Blender scene.

## New controls

| Control | Effect |
|---|---|
| tracery | Enable or disable pierced spandrel and coping |
| tracery_count | Number of quatrefoil openings per flyer, 1–12 |
| spandrel_rise | Vertical offset of sloping coping line above the chord of the flyer's upper edge |
| panel_width | Pierced panel thickness across the flyer |
| coping_thickness | Vertical coping thickness |
| tower | Enable receiver stringcourse, upper stage and cap |
| tower_stage_height | Upper tower stage height |
| pinnacle | Enable pyramid when tower is enabled |
| pinnacle_height | Height above tower cap |

R01 span, landings, circular curvature, flyer section, receiver dimensions, wall dimensions and repetition controls remain available. Quatrefoils use the envelope of four overlapping circles. Openings are fitted inside the panel, with expanded-contour containment checks; their size varies with available panel height. This is a procedural interpretation, not measured historical tracery.

When tracery is enabled, the receiver height automatically increases if necessary to contain the coping landing. The wall height must already accommodate the coping; incompatible parameters raise an error. Effective receiver height and other parameters appear in output/QA.json. Pier height is therefore a dependent design change; span and flyer arc remain unchanged. The coping has no drainage channel.

## Validation

verify_preview.py checks feature toggles, repeat builds, unrelated-object preservation, unchanged flyer vertices, two-unit repetition, ray passage through five actual holes, native loading, and GLB export/import world bounds. Generator QA checks closed mesh edge incidence and positive polygon area. These tests do not establish strength, sufficient stone ligaments, structural stability, masonry bonding, drainage or foundations. Extremely dense/small tracery arrangements require architectural review.

The example was built in Blender 4.3.2. No additional Python libraries are required. Physical unit conversion, cathedral receiving-face authority and F5ZL-C remain unresolved. No change to M01 status or architectural approval is implied.
