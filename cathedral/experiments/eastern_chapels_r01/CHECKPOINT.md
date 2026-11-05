# Eastern three-chapel study R01 — EXPERIMENTAL

2026-11-05. Native numerical scale preserved. No approved architecture changed.

## Sources
Recovered whole-cathedral alignment R01 GLB (crossing masonry plus plan guides); corrected active floor-plan candidate from WORK HANDOFF R03; chevet topology review R04. Governance retrieved from cathedral/governance-r01, CATHEDRAL_MASTER_REFERENCE.md (blob 1d7e358ff7562fcc64088854baa2abd3d31a729e). These sources do not constitute a complete cathedral exterior model.

## Generated trial
Three chapel floors/frontages placed at T3/T4/T5, using exact outer chord endpoints. Central projection 4200 native units, companion projections 2400. Axial two-bay rib indication, companion one-bay indication. Four entrance arch orders. Eaves 2700; axial ridge 3200 to 3700; companion ridge 3200 to 3350. Two freestanding towers at (30500,+/-2600), maximum height 7000. Two flyer tiers per tower, generated as experimental curved beams. These are trial values, not recovered dimensions. Physical metres per unit remains null.

## How to review
EAST_COMPLEX.png: exterior oblique. PLAN.png: common-scale top view. WHOLE_CONTEXT.png: cathedral-wide footprint context. Blend contains source objects prefixed RECOVERED_ and generated objects TRIAL_. Ribs are retained but hidden in exterior render. Roofs are thin massing surfaces; walls are an open window/support skeleton, not complete masonry. GLB is for external viewing; Blender is the editable authority for this experiment.

## Validation and limits
Script executed and all three images rendered; finite coordinate and source-object retention checks recorded in QA.json. Confirmed numerical placement in recovered plan frame. Visual inspection performed on oblique output. This is a preliminary silhouette/massing model, not a completed architectural solution. Shared entrance partitions, complete walls, vault webs, roof valleys, window tracery and actual cathedral receiver contacts remain unfinished. Flyer inner ends intentionally stop at assumed receiving positions with no invented source masonry. Neither geometric interface clearance nor structural capacity is certified. Middle-ambulatory roof/window relationships cannot be verified without its complete exterior geometry and selected vertical schedule. Missing F5ZL-C schedule remains unresolved. No live MR COMPUTER model inspection in this task; source recovery used supplied saved packages.

## Reproduction
Blender 4.3.2: blender -b -t 4 --python build_study.py. Inputs are bundled unchanged. Source SHA256 hashes in QA.json. Blender XYZ = east,north,elevation; exported glTF uses Y-up conversion. Default glTF units must not be interpreted as certified physical metres.
