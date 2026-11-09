# R52 — Universal Gothic Tracery **2D Construction Engine**
## Comprehensive execution handoff · 2026-11-09

**Scope:** Analytical plan/elevation geometry, opening topology, member/junction graph, reusable 2D source records, SVG and numerical QA. **NOT** moulding-section design, invented 3D depth, stone-joint layout, structural engineering, source-sheet interpretation by guesswork, or insertion into approved cathedral files.

**Checkpoint classification:** **VALIDATED EXPERIMENTAL 2D ENGINE**. The exact archived U01 construction code was copied unchanged and independently exercised; historical authority is not established by a passing numerical test. The main project’s approved work remains **LOCKED**.

**Start:** `python3 R52_2d_only_regression.py` from this folder (or use its absolute path). Review `outputs/R52_2D_REGRESSION_QA.json`, `R52_FINAL_2D_Construction_Engine_Handoff.png`, and the five individual SVGs.

### Executive status
The original **U01–U05 universal traceries** package already has a substantial analytical kernel. Do not discard or replace it. U01 provides circles, two-centred arches, tessellation with bounded sagitta, plate/bar openings, nested sub-lights, oculi, foils, junction graphs, stable opening IDs, and geometry QA. U04 extends the same geometric family to wheel/rose arrangements. U02–U05 add 3D mouldings, orders, masonry joints, and layers, which are **outside the current 2D engine**.

**New R52 independent evidence:** Five archived U01 spec cases run using `Model(spec)` only, without calling its 3D `solids()` function. **116/116 U01 internal 2D checks passed**, plus **3/3 deliberately malformed-spec rejection tests**. Per-fixture opening IDs, circle/arch records, member and junction counts, and source-plane face areas match archived U01 results. The shapes repeat exactly with unchanged inputs, survive reordered JSON keys, and obey area ×4 / bounds ×2 under dimension scale ×2. This is not a newly revalidated U02–U05 GLB build.

### What the file set contains
| Local file | Purpose | Status |
|---|---|---|
| `baseline/tracery_universal_U01.py` | **Unmodified** original U01 geometric source | Recovered / hash-verified |
| `baseline/specs_U01.json` | Five regression fixtures, including St-Leu and bar tracery | Archived, unchanged |
| `baseline/QA_U01_original_report.json` | Archived U01 QA for comparisons | Prior reported QA |
| `baseline/RESULTS_SUMMARY_U01-U05_original.md` | Historical U01–U05 stage results | Archive, not rerun |
| `baseline/WORKFLOWS_U01-U05_original.md` | Original JSON formats, methods, failure cases, QA | Archive |
| `R52_2d_only_regression.py` | **Current executable** 2D-only verification + SVG + one review PNG | Run/verified |
| `outputs/*_2D_construction.svg` | One editable 2D analytic outline per spec, with IDs | Generated / XML check required |
| `outputs/R52_2D_REGRESSION_QA.json` | Reproducible current numerical QA | Generated / passed |
| `ENGINE_CONTRACT.json` | Target API, units, provenance, output contract | Handoff schema |
| `SOURCE_PROVENANCE.md` | Evidence and non-evidence, exclusions, historical gates | Handoff |
| `QA_ACCEPTANCE_MATRIX.md` | Testing vectors, thresholds, regression gates | Handoff |
| `NEXT_PASS_ROADMAP.md` | Implementation order, blockers, rejection conditions | Handoff |
| `RUNBOOK.md` | Commands, reuse rules, desktop Blender keymap rule | Handoff |
| `R52_FINAL_2D_Construction_Engine_Handoff.png` | Single four-family overview | Rendered from current 2D models |

## 1. Immutable authority and scope boundaries

**Protected cathedral data (no rewrite, overwrite or silent regeneration):** F5ZK-C curved-chevet plan organization and authentic architectural bearings; F5ZN-A dimensional baseline; R28/V03 approved Blender checkpoint; all fourteen validated inner/middle ambulatory vaults and their seven shared arches; Pass 6J compound-pier records; preserved moulding profiles and their intended rib/arch use; four repaired M02/M03 window models; archived original Gothic plates and crops; R34–R50 experimental checkpoints. The old discarded outer ring must not be regenerated. No GitHub operations unless specifically requested.

- The R49 scope correction remains **mandatory**: the user’s French Gothic rib/arch moulding archive is **not a tracery cross-section source**. R46–R48 profile suitability claims are withdrawn; those trials retain value only as experimental topology/contact tests. The R49 neutral section is a *3D visual fixture*, not historical tracery evidence.
- **Do not use R50’s provisional 2,400 mm width or 180 mm thickness as a cathedral or historical dimension.** R50 Brandon M04 R03 remains an uncalibrated source-pixel tracing with 3 holes, not an authenticated historic 1:1 drawing.
- Do not merge geometries from Herne Plate 20, Sleaford Plate 26, Brandon M04, St-Leu Figure 80, Ungewitter 1205b, or any different medieval example. Scale bars and construction diagrams belonging to different views must be registered separately.
- The F5ZL-C support schedule remains unresolved. Architectural promotion and loading checks must not be asserted until the actual supporting arrangement is recovered.

## 2. Provenance and current source-of-truth

**Recovered archive** (read-only reference on MR.COMPUTER):

`/home/christopher/Downloads/downlods/3/universal-generator-U01-U05-2026-11-07.zip`

**Current isolated 2D handoff:**

`/home/christopher/Cathedral_Research/R52_universal_2d_engine_handoff/`

Original U01 source SHA-256:

`9ed6c586d352f5be0fd6be147275cc6155ed809b6e8b06cbc44009d5f8aaa0d3`

No U01 source modifications have been made in R52. The archive reports U01–U05 Python/Blender tests from 2026-11-07, but R52 only verifies U01 2D geometry anew. Distinguish **archived claims** from **current independently observed outcomes**.

St-Leu Fig. 80 U01 `stleu_fig80_rebuild` is an engraving/source-pixel fixture. The U01 ideal counterpart is a **construction hypothesis**, not a measured copy. The reported original St-Leu R03 reproduction comparison in the archive (IoU ≈0.999467, Hausdorff ≈0.578 source px) is prior evidence—not a new test in R52. The two are not interchangeable.

## 3. Required engine architecture

### Layer A — sources, constraints and unit provenance
Input: a named window specification with explicit `coordinate_frame`, `units`, `unit_authority`, `source_id`, `evidence_class`, `tolerance`, and `historical_status`. 2D internal coordinates are `x` horizontal, `z` vertical, units inherited from the source. A parametric example in millimetres is a **synthetic measured-length test**, not a medieval survey.

- Prefer explicit analytical primitive parameters instead of inferred positions.
- Do not infer a physical scale from a generic printed plate, PDF pixel resolution, another window, or the viewport.
- Reject missing units, negative/zero radii, inconsistent centres, overlapping voids, invalid nesting, undefined edge authority, and fake historical approval.
- Every transform must record provenance; `source_px -> mm` requires a *verified scale bar belonging to the exact view*.
- Preserve raw source coordinates and uncertainties. Do not force symmetry, closure, tangency, or equality when the historical evidence disagrees.

### Layer B — geometric primitives
Use the already recovered U01 `Circle`, `Arch`, `arc_pts`, `circle_poly`, with *analytical* centres, radii, endpoints and orientation stored independently of sampled render vertices.

Required primitive families:
- lines, segments, rays, circles, radial guides, two-centred Gothic arches, asymmetric/measured arches;
- robust circle-circle and circle-line intersections with 0 / 1 / 2 solutions and explicit rejection of non-intersection;
- tangency: internal/external, common tangent, cusp and foils;
- exact apex / springing / crown relationships, left-right half-arch continuity, vertical responds where specified;
- ordered open/closed curve loops, signed winding, normal/tangent and controlled chordal sampling;
- modular generators for 2–4 lights, nesting, intersecting heads, plate openings, cusps and n-foils.

Sampled polylines are **rendering/boolean approximations**, not replacements for the original compass geometry. Keep the sagitta tolerance separate from the architectural dimensional tolerance.

### Layer C — topology and openings
Use U01 `Model(spec)` as the foundation:

- `plate` mode: explicitly defined holes within the stone boundary.
- `bar` mode: member bands, nested lights, head/oculus unions, and complement-derived openings.
- Stable semantic IDs: `W.L1`, `W.L2`, `W.O`, recursive `W.A1.L1`, and geometric spandrels `S01` / `E01`.
- Treat **voids as first-class components**; they are not all glazing apertures. A solid spandrel is a valid design choice. Blind cusping must not be automatically interpreted as a through-hole.
- Keep member vs opening vs construction-guide geometries distinct.
- Build explicit incidence/junction graph and record degree, connectivity and intersection classification (overlap, shared edge, tangent contact).
- Stone-region polygon(s) must be valid, non-self-intersecting, complete, and satisfy `region + openings = envelope` within the declared tolerance. Check narrow residual webs.

### Layer D — numerical verification and semantic export
Each model must output:
1. `construction`: analytic primitives, centres/radii, arc endpoints, apex/springings, applied constraints and residuals.
2. `topology`: named members and junctions; opening IDs, boundaries, winding, parent path, neighbour/containment graph.
3. `regions`: stone and void polygons with source units, signed area, bbox, minimum separation, edge evidence.
4. `diagnostics`: each requested check, measured residual, pass/fail and correction log.
5. `provenance`: source hash, version hash, dimensional authority, whether scale is measured, derived or assumed.
6. `SVG`: **black solid = confirmed against the entered 2D source/spec**, **gray dashed = construction guides**, **red dashed = uncertain historical interpretation**. Black does *not* certify a real medieval plan.
7. `status`: `EXPERIMENTAL`, `VALIDATED_2D`, or `APPROVED` only after explicit human architectural sign-off.

All lengths/areas must use explicitly named `*_mm`, `*_px`, or `*_source_units`; never move between them implicitly.

### Layer E — downstream handoff boundary (NO 3D assumptions)
Once 2D is accepted, export closed contours, true arc metadata, the semantic graph, locally oriented tangents/normals and *possible* section/joint anchors to U02/U03 and the new procedural stone engine. Do **not** carry over arbitrary R47 rebate dimensions, user rib profiles, 3D stone depths, coursing, bedding faces, mortar widths, hypothetical structural bearings or unvalidated historical measurements.

This separation is intentional: the 2D engine should remain testable with pure Python, SVG and numeric QA without needing Blender. Independent GLB/Blender validation begins only when a *separately approved 3D section and stone-construction decision* exists.

## 4. Current regression fixtures and observed results

| Case | Mode | Openings | Members | Current U01 2D internal checks |
|---|---|---:|---:|---:|
| `stleu_fig80_rebuild` | Plate / engraved source pixels | 3 | 0 | 17/17 |
| `stleu_fig80_ideal` | Plate / hypothetical ideal | 3 | 0 | 17/17 |
| `bar_2light_sexfoil` | Bar / synthetic trial mm | 7 | 5 | 24/24 |
| `bar_4light_recursive` | Bar / synthetic trial mm | 19 | 13 | 42/42 |
| `intersecting_3light` | Bar / synthetic trial mm | 6 | 7 | 16/16 |
| **Total** | | **38** | **25** | **116/116** |

For each, R52 also verified source-record area, opening IDs, construction geometry, named members/junctions, run-to-run repeatability, JSON key-order insensitivity and 2× linear scaling. Three malformed specifications were rejected. These checks deliberately do not regenerate GLBs or count previous U02–U05 tests as new passes.

## 5. Validation matrix — do not collapse categories

**Technical:** Python 2D pure execution, deterministic outputs, archived source hash, JSON schema and SVG parse, stable naming, no input overwrites. **Pass for current five U01 fixtures.**

**Geometric:** analytic apex on both circles, exact tangencies where required, chordal sagitta ≤ tolerance, no invalid self-intersections or microloops, no accidental openings, holes/stone consistent, positive minimum widths, stable scaling. **Pass for current U01 fixture set**, not universal across arbitrary designs.

**Architectural:** all expected openings present, deliberate spandrel vs through-hole distinction, graph connectivity, viable member clearances, proper springing and crown relationships, jamb bearing faces. **U01 fixture design checks reported pass**, but *cathedral-fit and actual stone load transfer are unvalidated*.

**Historical:** source drawings registered, scale calibrated by view, intended section plane established, measured vs reconstructed arcs separated. **NOT VALIDATED.** The plates must not be converted to unstated measurements.

**Structural:** thrust, support continuity, masonry bearing, slenderness and material stress. **NOT EVALUATED.** 2D topology validation is not a structural sign-off.

### Mandatory regression fixtures
- Five U01 geometry cases above (do not delete or alter).
- U01–U05 original QA reports remain read-only references. No mass rebuild until a change demands it.
- All four repaired M02/M03 windows preserved; no replacement just because a general generator exists.
- Brandon M04 R03 and R50 original source-pixel outline preserved; cannot be declared historic 1:1.
- Ungewitter 1205b figure alternatives remain uncertain; do not impose its symmetrical lower foil as a measured historical outline.

## 6. Critical unresolved questions, explicitly tracked
1. **Historical source interpretation:** which ink strokes are construction, contour, glass seats, moulding edges, or repairs? Plate vs section planes must be independent.
2. **Physical scale:** no approved conversion from Brandon M04 R03 tracing pixels to millimetres; St-Leu engraving likewise uncalibrated.
3. **Geometry generality:** U01 2D passes *known fixtures*, not every Gothic foiling or asymmetric branching case. Deep cusps and pinched gaps need adversarial inputs.
4. **Continuous bounding surfaces:** U01 knows openings and members; the future contract must return parametric **boundary segments** with source/derived IDs instead of just Shapely-derived polygon samples.
5. **Disconnected/tangent regions:** distinguish zero-width touch, genuine crossing, shared face, impermissible pinch and separately pierced opening. No automatic visual smoothing that changes design.
6. **Local orientation:** ensure left/right and inward/outward normals survive all nesting and SVG transforms.
7. **Stone interfaces:** true masonry joints, individual blocks, 3D front/rear sections, glazing and bedding are separate later tasks.
8. **Architectural fit:** measured mullion/jamb receptions, springing heights and actual cathedral window bays remain unresolved.
9. **Source authority:** all provisional adjustments must retain a hypothesis label; no source copying between Herne, Sleaford, Brandon M04, St-Leu or the cathedral.

## 7. Immediate continuation — high-value bounded work

**R53 | Public 2D geometry API**  
Build a *new module*, not a rewrite of U01. Accept a strict JSON schema. Return the analytic curve registry + a topology graph and coordinate-frame/units metadata. Keep U01 as regression reference. Add exact segment provenance, side/tangent direction, and robust 0/1/2-solution intersection/tangency handling. Reject invalid specs before any surface construction.

**R54 | Topological adversarial suite**  
Implement 2-, 3-, 4-light, asymmetric and recursive cases, foils 3/4/5/6/8, non-tangent crossings, arc inversion, reversed winding, touching/open gaps, cusp collapse and narrow bars. All must either produce a valid connected region or fail *with an explicit reason*. Build one source-separable SVG per case; never silently repair a historical trace.

**R55 | Evidence-limited source comparison**  
Select ONE relevant measured window source; register its elevation independently from every enlarged section. Compare analytical arcs against *actual original ink* and record residuals in source pixels until the scale bars are verified. Human review distinguishes historically supported relationships from idealized interpolation.

**Gate to 3D | User-approved layout**  
Only after geometric QA and source/scale decisions: freeze named 2D contours, intersection graph, orientations and units as a `2D_LAYOUT_LOCK`. Then permit independent tracery-section work, with a neutral placeholder if necessary. No user's rib/arch profiles.

### Promotion conditions
- Every accepted example has reproducible centres/radii, a valid region/void topology, stable IDs, parameter changes with explainable behaviour, and negative-case rejections.
- Geometric accuracy metrics are **measured residuals**, not merely "looks right".
- Visual proof uses the confirmed/guide/uncertain SVG layering.
- Any historically claimed dimension comes from its specific view and recorded scale.
- The project owner explicitly approves architectural layout/fit before any change touches F5ZP.

## 8. Execution/usage rules
- **No GitHub** unless requested.
- Prefer a single parametric run (rebuild only changed experimental test cases); minimise reading/indexing and parallel duplicate generators.
- Keep working, approved and locked stages separate.
- Save all scripted/generated source outputs in versioned R53+ directories, not over R52/U01 archived references.
- Run 2D geometry and numerical QA first, then 3D GLB validation in Blender only when actual 3D reconstruction is in scope.
- User Blender opening requirement: load `/home/christopher/tab.py` keybind preset. It was restored at R50 from the identical installed Blender 5.2 preset. Import mode may report a benign/compatibility warning about missing "User Interface" keymap; validate active keymap and do not delete the source preset. No GUI launch is required for this 2D-only package.
- Deliver a **single PNG** for visual review in chat; retain source, SVG, JSON, and scripts locally, with numerical QA and clear uncertain-state markers.

---

**Handoff conclusion:** Continue **from recovered U01** with a strict 2D analytical/topological API, not from synthetic R46–R48 mouldings and not from unchecked architectural-plate interpretation. The R52 package is standalone and read-only relative to prior cathedral work. **NEXT PASS: R53.**
