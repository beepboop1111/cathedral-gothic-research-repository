# Reproduction workflows

## Runtime

Tested with Blender 4.3.2 in this environment. No add-on required. Current generator uses bpy, bmesh, mathutils, standard Python and NumPy for plate fitting. Combined PNG runners also require Pillow; R03 runner imports NumPy. These must be available to Blender's Python, not just system Python. Other Blender versions are untested. Workbench rendering needs a working graphics context; headless setups may require a display/EGL configuration. Recorded EGL warnings here did not prevent PNG rendering.

Run from the extracted package directory, preferably in separate Blender processes:

```bash
blender -b --factory-startup --python-exit-code 1 --python tests/test_modular.py
blender -b --factory-startup --python-exit-code 1 --python tests/test_research_system.py
blender -b --factory-startup --python-exit-code 1 --python tests/test_plate_892.py
```

These create current/output PNGs, not Blender/GLB exports. R03 and plate runners use temporary panel PNGs under /tmp when composing the final image. They deliberately reset Blender to an empty scene; do not run them in unsaved interactive work.

## Geometry APIs inside Blender

```python
import runpy
from pathlib import Path
# Replace with the actual extracted package path.
root = Path('/absolute/path/Buttress_Generator_Handoff_R04')
g = runpy.run_path(str(root/'current/flying_buttress_r02.py'), run_name='generator_module')

# Choose ONE per working scene:
objects, qa = g['build'](g['DEFAULTS'].copy())
# R02 selective detail update, after matching full build:
objects, qa = g['build'](g['DEFAULTS'].copy(), components=['tower_details'])
# Full R03 assembly:
objects, qa = g['build_system']({}, {'two_tiers': True, 'intermediate': True,
                                    'receiver_section': 'stepped', 'tracery_rule': 'trefoil'})
# Independent plate assembly:
objects, qa = g['build_plate_892'](study_span=5000., depth=420.)
```

R03 options: see SYSTEM_DEFAULTS. Tier landings and sagitta are independent; support stations split the span. Receiver yaw orients its plan in XY. Tracery rules produce editable circle/arc specifications. Boolean unions join overlapping swept bars; the optional boundary-solid intersection API clips junctions. Coursing divides the flyer into radial voussoirs and receiver into horizontal courses with explicit joints.

## What each workflow actually did

1. R01: derive circle from chord/sagitta → annular flyer → supports → validation → Blender/GLB → render.
2. Original R02: retain R01 flyer → pierce spandrel with quatrefoils → coping/tower/pinnacle → feature/holes/export checks → Blender/GLB/render.
3. Modular: reusable polygon-profile sweeps and transport frames → bounded stone-bar inserts → named anchors/repeats → component collections → fit diagnostics → combined test → PNG only.
4. R03: tier and support-station definitions → courser receiver/arch pieces → compass-defined upper inserts and moulding unions → downhill channel/outlet → three proportion configurations → checks → matched PNG only.
5. Figure 892: inspect preserved plate → manually select eight soffit samples → least-squares circle → map pixel span to illustrative study units → voussoirs/solid spandrel → single pierced quatrefoil → coping/receiver/simplified pinnacle → fit and mesh checks → uncertain red-dashed source overlay plus 3D PNG.

## Original releases

Extract each historical ZIP separately to reproduce its own saved model and checks. Use the README inside that ZIP. Do not mix its original verifier or exports with the current expanded generator. The historical README claims describe their original snapshot, not the current API.

## Future exports

No latest-generation GLB or .blend is supplied. To export later, select only the returned objects, export with Blender's glTF exporter and save to a new experimental path; round-trip and measure those new files before calling them validated. Avoid the current CLI for plate/R03 exports: its main() calls the modular R02 builder.
