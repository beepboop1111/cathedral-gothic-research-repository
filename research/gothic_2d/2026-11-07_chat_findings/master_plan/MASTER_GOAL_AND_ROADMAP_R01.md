# Gothic Tracery Reconstruction System — Master Goal and Roadmap R01

**Prepared:** 2026-11-05  
**Status:** Proposed development charter for user review; **not an approved generator, architectural baseline, or change authorization**.  
**Scope:** Historical 2D scan interpretation and tracing; parallel experimental 3D stonework development; eventual shared parametric 2D/3D generation.  
**Protected:** Historical originals, approved work including F5ZK-C and F5ZN-A, working inner/middle ambulatory generator, Pass 6J record, prior QF-001 record, and all authoritative generators. Missing F5ZL-C support schedule remains unresolved.

## 1 — End goal

Build a **simple, interactive, reliable Gothic architectural geometry system** that can take a historical plate or a user-authored design through the following reversible, inspectable stages:

`source scan → measured 2D geometry → architecturally classified vector faces → user-approved 2D design → matching editable 3D stonework → validated reusable component`.

Develop two tools **in parallel but separately**:

- **2D research/tracing tool:** Preserve the original plate; identify circles, exact arcs where measurable, Gothic arches, cusps, tangencies, divisions, mouldings and labeled features; produce editable 1:1 calibrated SVG where source dimensions support it. Uncalibrated plates retain image/pixel units and measurement uncertainty.
- **3D stonework tool:** Interpret *approved or explicitly experimental* 2D semantic geometry as real pierced stonework with appropriately parameterized thickness, mouldings, edge profiles, responds and interfaces; export editable GLB as the default review format and STL when needed. No manufactured historic thickness or structural capacity claims.

**Unity is the final stage, not the starting shortcut.** Only integrate when each pipeline independently meets its acceptance criteria and shares a documented geometry/face-ID contract.

## 2 — What the work to date actually establishes

| Area | Recovered evidence | Limit |
|---|---|---|
| Historical tracing | V01, Plate CXVIII page, figure studies, R03/R04 editable SVG / circle-fit experiments | Scan vectorization and selected circular fits do not prove complete historical compass constructions |
| Colored interpretation | Black-on-white tracing; openings orange, closed stone green, outer-to-inner purple/indigo/blue/cyan/yellow/orange visual-depth palette | Visual layers are not physical depth measurements |
| Face detection | R02/R03 candidate face registers, semantic region classifiers | Inferred faces, crop-edge ambiguity, and changing numeric IDs remain unresolved |
| New 3D kit | `tracery_regions.py` + `tracery_build.py`, supplied `tracery_kit.zip`, four test cases | Uses raster maps and marching cubes; not a true CAD solid generator; mesh topology needs QA |
| Reproduction provenance | Four-window run logs, corrected `--res 0.25` reproduction commands | User logs are not the same as independent four-model regeneration |

**Four initial benchmarks:** Haina 1264 (21 openings), Haina 1265 (30), Meaux (48), Châlons (19) as recorded in the final command log. Each value is a *run-specific classification count*, not a universal historical count. The complete input image, map, classification overrides, axis and source checksum must accompany every benchmark.

**Current known Meaux issue:** The supplied Meaux STL loads, but earlier welded-mesh QA found 6 nonmanifold edges and 7 near-zero-area faces. `stone: 1 piece(s)` means one connected 2D stone mask, not a watertight 3D model. Investigate rather than assert resolution.

## 3 — Parallel development roadmap

### Phase 0: Preserve and baseline (immediate)

**Outputs:** Unmodified reference copies and SHA-256 hashes for each original plate, source PNG, script, option set, current SVG, region map, STL and validation report; a benchmark manifest; experimental working folder. Verify any approved QF-001 source and V08 version before reuse. Recover exact saved model/generator where work touches a cathedral component.

**Gate:** A fresh machine can find the correct source + command for each benchmark; nothing approved is overwritten.

### Track A — Historical 2D tracing and interpretation

**A1. Reliable scan and linework acquisition**  
Preserve originals; retain page/crop/rotation/mirroring transforms; isolate actual ink from annotations; make stroke cleanup and mirroring optional with before/after difference overlays; always preserve the untouched scan. Support full-page exports when the user asks for a full page.

**A2. Persistent semantic faces**  
Assign stable face IDs from geometry/topology and reference anchors, not transient flood-fill numbers. Store each face as `opening | closed stone | moulding | outside | uncertain`, with confidence and evidence. Detect boundaries that remain open at image edges. Make every face selectable and editable in SVG. Save manual corrections independently of palette and drawing resolution.

**A3. True geometric reconstruction**  
For each confirmed primitive, store radius, center, angles/endpoints, arc direction, intersections, cusp definition, tangency and uncertainty. Validate repeated and mirrored foils without silently imposing ideal symmetry. Separate measured contours from idealized historical-compass hypotheses.

**A4. Standard drawing views**  
From the same saved geometry export: (i) black architectural tracing, (ii) construction view with thin dashed light-gray axes, dotted black recovered full circles and dashed red uncertain constructions, (iii) optional colored face/depth-*interpretation* view, and (iv) source comparison overlay. No redraw between views.

**2D acceptance gate:** No lost/merged approved contours; all intended faces selectable; repeatable stable IDs under unchanged inputs; geometry residuals and ambiguous cusps documented; full-page alignment to the original checked; historical claims supported by their plates or text; reviewer approval before baseline promotion.

### Track B — Reproducible, robust 3D stonework

**B1. Mesh-topology repair experiment (Meaux first)**  
Reproduce the reported Meaux settings in isolation, inspect the original and repaired STL, eliminate nonmanifold/degenerate geometry without sacrificing thin cusps, authentic holes or moulding profiles. Test cleanup parameters (`--min-bar`, `--min-hole`, `--bridge`) against 2D source overlays; do not change defaults in the authoritative scripts.

**B2. Explicit construction input**  
Consume Track A's face IDs and exact outline geometry wherever available, using raster segmentation only as a documented fallback. Expose true stone thickness, inner/outer moulding section and edge treatments as *explicit provisional parameters* until sources provide dimensions. Preserve object/moulding identities through export.

**B3. Geometric and export validation**  
Automate closed-edge manifold checks, winding, degenerate faces, duplicate faces, self-intersections where testable, components, cross-section continuity, scaled bounds, minimum bar width and original-opening retention. Import exported GLB/STL back into a fresh reader; conduct Blender review where authorized.

**3D acceptance gate:** Benchmarks reproduce from recorded commands; zero nonmanifold edges and zero degenerate triangles in finished test meshes; approved openings and narrow connectors preserved against the classified 2D source; dimensions and orientation match explicit input; editable GLB and STL independently inspected/tested. A watertight mesh alone does not prove architectural or structural validity.

### Track C — Integration, ease of use and library

**C1. Shared geometry contract**  
Define one versioned schema with source hashes and transforms, units/calibration, exact 2D curves, profiles, face IDs/classifications, uncertainties, approved/experimental statuses and links to 3D source objects. V08 can serve as a compatibility library; no automatic replacement of its approved neighbors.

**C2. Simple user-facing workflow**  
Aim for: import plate → propose linework → click to correct faces/arcs → review black/construct/color overlays → approve → preview 3D → run QA → export/checkpoint. Provide understandable modes for tracing, floor plans, buttresses, windows and intricate tracery. Keep expert parameters available without making them required for basic use.

**C3. Library expansion and checkpoints**  
Add user-approved templates for trefoils, quatrefoils, sexfoils, octafoils, pointed arches, lancets, windows, buttresses, piers and plans one at a time. Version each approved script, reference geometry, tests and known exceptions. Historical studies do not become cathedral dimensions merely by being traced.

**Final integration gate:** Both 2D and 3D pipelines independently pass regression suites; shared geometry round-trips without changing dimensions, topology, face assignments or locked interfaces; owner explicitly approves promoting the new common workflow.

## 4 — First execution sequence (no architectural approval needed for isolated tests)

1. **M01 — Freeze four-window benchmark R01.** Record originals, exact final commands and map overrides; flag missing raw outputs, `diag.py`, `shot.js` and incomplete Meaux re-run.
2. **M02 — Meaux repair R03 experiment.** Produce before/after mesh QA and matching 2D/3D overlays; demonstrate the repair does not destroy authentic stonework. Preserve previous Meaux STL.
3. **M03 — Stable 2D face record.** Replace shifting flood-fill IDs with repeatable semantic IDs and unit tests on Meaux + Haina 1265.
4. **M04 — Exact arc and cusp trial.** Reconstruct one sixfoil and one pointed arch from source samples; measure residuals and verify connections; compare against copied variants.
5. **M05 — Cross-validate all four windows.** One command per source producing region map, editable SVG, numerical QA, GLB/STL and a comparison panel. No unreviewed geometry changes.
6. **M06 — Human review gate.** User decides which specific methods and parameters may be saved as approved project working baselines.

## 5 — Proposed permanent release checklist

- [ ] Source original preserved and hashed; transformations recorded
- [ ] Current actual baseline identified; experimental output isolated
- [ ] Geometry units and calibration clearly identified
- [ ] Confirmed/uncertain constructions separated according to drawing standards
- [ ] 2D SVG paths, faces, IDs and source overlays generated
- [ ] Numerical fit/intersection/tangency and topology report generated
- [ ] 3D GLB/STL generated when appropriate; import and mesh QA passed
- [ ] Regression comparison against unchanged reference artifacts passed
- [ ] Limitations and provenance described without inflated approval claims
- [ ] Explicit user approval obtained before promoting scripts/workflows
- [ ] Approved copies versioned into the Project without overwriting predecessors

## 6 — Change-control rules

- **Historical / Experimental / Technically validated / Geometrically validated / Architecturally approved / Locked** are separate statuses.
- Approval of a **visual color reference** does not approve source dimensions, stone thickness, construction method or 3D mesh.
- No destructive cleanup, generator replacement, or change to F5ZK-C/F5ZN-A/Pass 6J/working ambulatory vaults without permission.
- Any test that requires unavailable source scans, historic dimensions or saved current cathedral models must explicitly report the gap.
- This R01 charter is for review; it may be adopted after user acceptance, but does not itself modify project files or GitHub.
