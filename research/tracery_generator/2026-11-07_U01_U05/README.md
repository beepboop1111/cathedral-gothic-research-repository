# Universal Gothic tracery generator — U01–U05 handoff (2026-11-07)

**Status: EXPERIMENTAL research code. Not approved cathedral geometry and not a structural sign-off.**
Nothing here changes F5ZK-C, F5ZN-A, Pass 6J, QF-001, the working inner/middle ambulatory generator,
the four repaired M02/M03 windows, or any historical scan. The F5ZL-C support schedule is still missing.

Start here, then read:

| File | What it is |
|---|---|
| `WORKFLOWS.md` | How each stage works, the JSON spec formats, every automated test, and the problems Blender caught (and how they were fixed) |
| `PROGRESS_AND_NEXT_STEPS.md` | What exists now, findings, decisions, open issues, and the plan for pinnacles, buttresses, towers and spires |
| `RESULTS_SUMMARY.md` | Generated table of every QA result from the verified clean rebuild |
| `run_all.sh` | One command that rebuilds everything from scratch and re-checks it in Blender |
| `scripts/` | All generator, QA, Blender and figure scripts plus the JSON specs |
| `results/` | QA reports (JSON), review PNGs, the final U05 GLBs and the U04 rose GLB |
| `SHA256SUMS.txt` | Checksums for every file in this folder |

## What the generator does (one paragraph)

A window (or rose) is described in a small JSON file. **U01** turns it into exact compass geometry
(every arc keeps its centre and radius), explicit stone members with a junction graph, and openings with
persistent IDs; it can rebuild a measured drawing (St-Leu Fig. 80) or build parametric bar tracery
(lights, nested sub-windows, oculi with cusped foils, intersecting tracery). **U02** adds depth: members of
different *orders* step back from each other and every opening edge carries a moulding (fillet, chamfer,
roll, hollow, ogee, groove) that mitres automatically at junctions and cusps. **U03** cuts the stone into
real blocks: coursed jambs and mullions, voussoirs radial to each arc, rings cut at lobe centres, junctions
kept inside single stones, 6 mm open joints. **U04** adds the rose / wheel window (cusped hub, radiating
bars, pointed heads, cusped circles). **U05** makes the tracery its own masonry layer with an open joint
against the wall frame and its own longer stones. Every model is exported as GLB and re-imported into
Blender, where each stone is checked for non-manifold edges, degenerate faces and self-intersections.

## Current results (verified by a clean rebuild on 2026-11-07)

| Stage | Models | Python QA | Blender QA (re-imported GLBs) |
|---|---|---|---|
| U01 topology + plain solids | St-Leu rebuild, St-Leu ideal, 2-light, 4-light, intersecting | all pass; St-Leu fixture regression 3/3 | 15 meshes clean |
| U02 orders + mouldings | St-Leu, 2-light, 4-light, intersecting | all pass | 39 objects clean |
| U03 jointing | 20 / 61 / 113 / 56 stones | all pass | 258 objects clean |
| U04 rose window | rose (85 stones) + 4-light regression | all pass | 202 objects clean |
| U05 tracery as own layer | 20 / 46 / 83 / 48 / 109 stones | all pass | 316 objects clean |

"Clean" = 0 non-manifold edges, 0 degenerate faces, 0 self-intersecting face pairs, vertex/face counts and
bounds identical to the exporter. Rebuilding U01–U03 after the U04/U05 code changes gave identical meshes.

## Validation kept separate

- **Technical** – files, GLB export/re-import, bit-identical rebuilds, reproducible commands.
- **Geometric** – analytic residuals (apex, tangency, radial joints), watertight solids, genus = openings,
  scale tests, fixture regression.
- **Architectural** – connected member graph, minimum stone webs, order depths stepping back, mouldings
  shallower than half-depth, junctions inside single stones, maximum stone length. All sizes are TRIAL.
- **Historical** – only St-Leu uses measured (engraving) data, in uncalibrated source pixels; Moore 139a
  supports the *kind* of chamfer; jointing follows the documented principle (coursed mullions; the stone
  frame of arcs and oculus jointed onto the mullion and cut-back jambs). Rose and bar windows are parametric.
- **Structural** – not assessed anywhere.

## How to run it (Ubuntu, step by step)

These steps assume no prior setup. Type each command in a terminal and press Enter.

1. **Get the files** (skip if you already have the repository):
   ```bash
   cd ~
   git clone --branch cathedral/experimental-tracery-universal-u01-u05-20261107 \
       https://github.com/beepboop1111/cathedral-gothic-research-repository.git
   cd cathedral-gothic-research-repository/cathedral/research/tracery/universal-generator-U01-U05-2026-11-07
   ```
2. **Install `uv`** (a small tool that fetches the right Python version for you):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   source ~/.bashrc
   ```
3. **Make a private Python 3.13 environment in this folder and install the libraries** (Blender's `bpy`
   module is about 400 MB, so this takes a few minutes):
   ```bash
   uv venv --python 3.13 .venv
   source .venv/bin/activate
   uv pip install -r requirements.txt
   ```
   Each new terminal needs `source .venv/bin/activate` again before running anything.
4. **Rebuild and check everything** (about 5 minutes without renders, about 15 with renders):
   ```bash
   RENDER=0 ./run_all.sh      # quick: builds + all QA, no Cycles renders, no PNGs
   ./run_all.sh               # full: also renders and writes the five review PNGs
   ```
   Output goes to `out/U01` … `out/U05` inside this folder. The last lines of each stage print
   `N/N pass` per model; any `FAIL` line names the failed test.
5. **Look at a model in Blender**: open Blender → **File** (top-left menu) → **Import** → **glTF 2.0
   (.glb/.gltf)** → choose e.g. `out/U05/rose_12_chassis.glb`. Each stone is its own object
   (`…__stone_F001` = wall-frame stones, `…__stone_T001` = tracery stones). The saved review scenes
   `out/U0x/*_review.blend` already use your viewport settings (Focal Length 9.3 mm, Clip Start 0.01,
   Clip End 1e11).

**Using the Blender application instead of the `bpy` module** (if step 3 cannot install `bpy`): install the
other libraries only (`uv pip install numpy scipy shapely trimesh triangle matplotlib`) and run the Blender
steps like this, with the script arguments after `--`:
```bash
blender -b --factory-startup --python scripts/blender_U02.py -- out/U05 <render ids> <all ids> <close-up id> qa
```
(`run_all.sh` prints the exact id lists it uses.)

## Folder rules

- `scripts/` is the only source of truth; `out/` is always regenerated and is not committed.
- The St-Leu fixture is read from `../early-fig80-study-2026-11-04/MR_COMPUTER_R03_REPRODUCTION/` and is never
  modified.
- New stages get new version numbers (U06 …); earlier stages stay as regression fixtures.
