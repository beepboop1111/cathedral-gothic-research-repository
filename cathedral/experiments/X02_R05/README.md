# F5ZP X02 R05 — bearings and roofs

The upper passage now has an explicit bearing set-out and a clear western vestibule beneath it. Roof volumes respond to the retained R04 floors and stair. This remains an experimental design study.

Open `outputs/F5ZP_X02_R05_BEARINGS_CLEARANCE_AND_ROOFS.pdf` for the bearing plan, coordinated true sections, roof plan and native model view. Editable metre-scale GLB and Blender scenes are beside it. Bearing/roof schedules, 1:1 SVGs, numerical geometry and complete QA are included.

The west vestibule has 2.10 m between proposed piers, a checked 1.80 m route band and 2.97 m below the girders. Eight new piers and six girder pieces define the architectural load path. Member sizes and foundations remain unverified; consult CHECKPOINT.md for exact assumptions and scope. The support schedule is local to this experiment and does not recover F5ZL-C.

The roof study retains upper FFL +3.600, reserves the +5.700 stair envelope and establishes an upper-room ceiling control +6.300. Roof step upstands are modeled. Flashings, gutters, drainage and carpentry remain detail work. 3D walls are schematic plan-cut extrusions; full windows, door heads and historic details are not finished architectural elevations.

## Reproduce

Install `requirements.txt`, then run `python3 build_r05.py`. This reads the copied R04 numerical geometry and writes within this experiment. It never executes the R04 generator or any vault generator. It writes GLB, schedules, SVGs, numerical QA and PDF. If `outputs/R05_BLENDER_PREVIEW.jpg` is present, it is used on the PDF's final page; otherwise a technical mesh axon is generated.

Run `blender -b --factory-startup --python open_in_blender.py` to import and validate the GLB, save a new experimental Blender scene and render it. Metre scale is retained; Blender changes Y-up to native Z-up. Model validation and architectural/historical/structural approval are distinct.

No protected cathedral files are overwritten. R04 is retained as source. Pass 6J and the working inner/middle vault generator are preserved, and F5ZL-C remains unresolved. GitHub version receipt and file checksums document this package.
