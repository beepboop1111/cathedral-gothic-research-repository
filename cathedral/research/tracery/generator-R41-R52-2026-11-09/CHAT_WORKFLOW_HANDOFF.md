# R41–R52 Gothic Geometry / Tracery: Conversation Research Handoff (2026-11-09)

**Experimental evidence branch.** This directory records the scripts, GLBs, SVGs, QA files, checkpoints, and selected review PNGs generated across the stone-joint / branching / tracery-engine conversation. The upstream U01–U05 code remains in the **existing sibling directory** `../universal-generator-U01-U05-2026-11-07` and is not changed.

**Use R52 for continuing the 2D construction engine.** Start with `R52_universal_2d_engine_handoff/HANDOFF.md`, the unchanged `baseline/tracery_universal_U01.py` and `R52_2d_only_regression.py`. The standalone original complete handoff archive is `R52_Universal_2D_Engine_HANDOFF_R01.zip`.

## Checkpoint record

| Checkpoint | Technical outcome | Evidence / applicability |
|---|---|---|
| **R41** | Curved/tapered stone generator, experimental two-stone work | Synthetic contact/bedding; not measured archaeological joints. |
| **R42** | 3-stone branching Y-junction, shared contact surfaces, cut rebates, GLB study | Experimental geometry, NOT historical joinery. |
| **R43** | Selectable source-graded section intake, front/rear stations, input rejection | Section selection is synthetic. |
| **R44** | 35°, 42°, 50° branching studies, repaired Boolean-cap GLB export | Technical contact tests; not cathedral bearing validation. |
| **R45** | Modular profile input and 6-stone branching assembly; independent GLB import tests | Synthetic profile fixtures; NOT historically certified. |
| **R46** | Two-lancet 29-stone Gothic head with an enclosing arch and foil | **Retired as a tracery-profile study:** wrongly reused user's rib/arch profiles. Retain ONLY software mesh/topology research. |
| **R47** | Experimental curved physical glazing rebates and contact tests | **Same user-profile misuse.** Rebate dimensions were invented, not sourced. |
| **R48** | External configs, two profile cases, 29 solids, 26 contact checks, regression | **Same user-profile misuse.** Do not reuse as historically suitable tracery mouldings. |
| **R49** | Corrected profile gate, neutral synthetic section; reject user rib profiles | Proper active experimental role; geometric only. |
| **R50** | Brandon M04 R03 2D source-pixel rings and metric display proxy, genus 3 | Actual print/scale bars unregistered; 2400mm width / 180mm depth are hypothetical. |
| **R51** | Brandon/Herne/Sleaford historical plate *image review* | Research only; no calibrated historic geometry, no measured joining/bearing certification. |
| **R52** | **Recovered original U01 analytical 2D engine; 5 verified fixtures, 116 internal checks, 3 invalid-input rejections.** SVG + source hash QA | Best next 2D baseline. One engraved source-pixel St-Leu case, others parametric; historical and structural validity unresolved. |

### Architectural locks and forbidden inferences

- Do not overwrite F5ZK-C, F5ZN-A, saved R28/V03 geometry, Pass 6J, the fourteen validated AMB-I/M vaults, the repaired four M02/M03 windows, original profiles, nor the discarded-outer-ring decision.
- The owner's **French Gothic rib/arch profiles are NOT for tracery**. See R49 scope correction. Never present R46–R48 as correct tracery mouldings.
- No borrowing dimensions from unrelated windows or views. Brandon M04 R03 and St-Leu pixels are not verified metric 1:1 historic drawings.
- Keep **Technical, Geometric, Architectural, Historical and Structural** validation separate; a watertight GLB is not a structurally sound medieval masonry junction.
- Actual 3D archaeological contact faces and historical cross-sections are still missing.
- F5ZL-C support schedule still unresolved. No cathedral insertion/approval implied by this upload.

### Next tasks (2D only)
R53: strict analytic arc/circle/intersection + topology API, stable source/units.
R54: asymmetric, multi-light/foil, and near-pinch rejection suite.
R55: source-specific original drawing registration & scale-bar verification.
R56: **human-reviewed 2D layout lock**, then independent 3D integration.

### Reproduction and artifact layout
Scripts: `RXX*/**/*.py`; configs and QA: `*.json`; generated geometry: `*.glb`, `*.blend`, `*.svg`; one review PNG per major checkpoint. Some intermediate images, logs, and duplicate GLBs are intentionally omitted from the Git branch; all uploaded files have a local SHA-256 manifest. For a byte-preserved R52 stand-alone snapshot, use the ZIP.

**Branch status**: research-only, not merged into protected cathedral geometry. Prepared on MR.COMPUTER from the original local scripts; no automated GitHub Actions/Blender tests claimed during upload beyond the saved QA evidence and file-integrity verification.
