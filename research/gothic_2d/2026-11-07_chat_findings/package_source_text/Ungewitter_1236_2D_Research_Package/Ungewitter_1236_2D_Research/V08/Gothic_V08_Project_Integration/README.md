# Gothic Architectural Reconstruction Toolkit — V08 Project Integration

**Release:** `0.8.0-preview`, 2026-11-03. **Status:** experimental, read-only on original sources. This package is a portable, tested baseline of reusable primitives derived from the MR.COMPUTER V01–V07 development work. It is **not** a claim that the full historically specific V01–V07 workflows have already been migrated or verified on every new plate.

## Included modules

| Module | Main functions | Intended role |
| --- | --- | --- |
| `gothic_plate_reader.py` | `inspect_plate`, `extract_ink`, `Calibration` | Plate hashes, crops, ink-layer separation, optional explicitly supplied scale |
| `gothic_geometry.py` | `circle_fit`, `sample_arc`, `joining_candidates`, `repeated_radius_groups` | Analytic geometry and conservative contour pairing |
| `gothic_patterns.py` | `radial_instances`, `linear_instances`, `rotate_about`, `mirror_about_x`, `preserve_unique_decorations` | One master → selected sectors, copies, or independent ornament slots |
| `gothic_stonework.py` | `normalize_section`, `sweep_between_rails`, `repeat_mesh_radially` | Non-voxel two-rail mesh sweep; reusable 3D instances |

Eleven local automated tests pass. The package includes a dependency declaration and integration example. Modules are importable individually and deliberately **do not overwrite or import the historic project scripts** by default.

## The existing MR.COMPUTER generator scripts (authoritative development originals)

The portable V08 modules are compatible in concept, but the following earlier projects remain separately maintained on MR.COMPUTER:

- `~/Desktop/sketch2stl/sketch2stl.py`: existing raster/voxel relief generator.
- `~/Desktop/sketch2stl/cathedral_geometry/plan2geometry.py`: current extraction schema and geometry candidates.
- `~/Desktop/sketch2stl/cathedral_geometry/geometry2stl.py`: diagrammatic 2.5D STL renderer.
- `gothic_geometry_v01.py`, `_v02.py`: measured curve fitting, conservative contour joins and motif candidates.
- `gothic_cusps_v03.py`, `_v04.py`: Haina guide-dependent octofoil and individual animal-head drawing studies.
- `gothic_sector_v05.py`: Haina one-eighth / quarter / eightfold propagation.
- `gothic_moulded_sector_v06.py`: source PNG profile sweep along measured Haina dual rails.
- `gothic_simple_full_disk_v07r1.py`: separate plain collar, repeated ring and optional experimental disk backing.

**These source files were not bundled from the remote machine into the portable V08 ZIP.** Their exact historical source geometries, high-resolution plates, traced profile PNGs and actual 3D builds still reside on MR.COMPUTER. Copy/attach those separately if full regeneration from original materials is required.

## Example

```python
import numpy as np
from gothic_plate_reader import inspect_plate, Calibration
from gothic_geometry import circle_fit, sample_arc
from gothic_patterns import radial_instances
from gothic_stonework import sweep_between_rails, repeat_mesh_radially

# This is a synthetic example. It does not establish any Haina dimension.
outer = sample_arc((0,0),10,-60,60,101)
inner = sample_arc((0,0),8,-60,60,101)
profile = [[0,0],[1,0],[1,.3],[.5,1],[0,.3]]
mesh, qa = sweep_between_rails(outer,inner,profile,relief_height=1.5)
scene = repeat_mesh_radially(mesh,count=8,master_index=5)
scene.export('example.glb')  # master geometry shared by eight nodes
```

## Install into the Research Project

1. Add `Gothic_V08_Project_Integration.zip` to the Project's files, or unzip and attach the four `.py` modules plus README and tests. If the package appears in your **Library**, it is available for retrieval but is **not automatically attached as Project knowledge**.
2. On the modeling machine, unzip into a new folder (such as `cathedral_geometry/gothic_v08/`). **Do not copy over** the existing generators.
3. Run `python -m unittest discover -s tests -v` from the extracted folder.
4. Migrate the main scripts **one command at a time**, with a CLI opt-in and side-by-side output QA. Do not call V08 at import time from the old scripts.
5. Keep the explicit scale and provenance flags in every output. A historical book plate supplies research evidence, **not authority** to replace locked F5ZP geometry.

## Planned integration routes (not yet switched on)

- `plan2geometry.py --engine v08`: call plate reader / analytic geometry with existing JSON fields preserved.
- `geometry2stl.py --engine v08`: accept verified contours and generate non-voxel two-rail stonework, while leaving the raster default available.
- `sketch2stl.py --mode gothic-silhouette`: use vector outline relief only after user review; no automatic animal face reconstruction.
- `profile_sweep_adapter.py --rail-mode dual`: route measured rail curves into `sweep_between_rails`.

The option names above are **integration proposals**, not commands implemented in the existing scripts.

## What to test with new high-resolution plates

Begin with one carefully cropped plate containing a scale/section and a clearly readable repeated ornamental unit. Record separate image, tracing, and historical source hashes. Benchmark curve fitting and joined contours against explicitly labeled plate evidence before using the new 3D path. Never infer depth from elevation alone, auto-copy distinct animal heads, or certify masonry continuity based solely on a watertight mesh.
