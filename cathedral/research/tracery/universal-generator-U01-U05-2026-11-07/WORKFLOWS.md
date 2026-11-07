# Workflows, spec formats and tests — U01–U05

All scripts are in `scripts/`. Each stage reads JSON specs, builds models, runs automated QA in Python,
exports GLB, then `blender_U01.py` / `blender_U02.py` re-imports every GLB into Blender for structural mesh
checks and (optionally) renders. `run_U0x.py compose` / `run_U04.py` / `run_U05.py` write the single review
PNG per stage.

```
JSON spec ──U01──> analytic construction + members + openings (IDs)
          ──U02──> orders (set-back depths) + mouldings (height field)      [sections_*.json]
          ──U03──> masonry joints -> separate stones                         [joints_*.json]
          ──U04──> rose / wheel window construction (same U02/U03 layers)    [specs_U04.json …]
          ──U05──> tracery as its own masonry layer (chassis joint)          [specs_U05.json …]
          ──GLB──> Blender re-import: per-object QA + Cycles render -> PNG
```

## Scripts

| Script | Role |
|---|---|
| `tracery_universal_U01.py` | Core: `Circle`, `Arch` (two-centred, parametric or measured, concentric offsets), `Model` (plate/bar modes, recursive lights, oculus tangency solver, n-foils, intersecting tracery, topology/IDs, junction graph, webs, chamfered plate solids), mesher `plate_mesh`, `mesh_qa` |
| `run_U01.py` | U01 build + QA + St-Leu fixture regression + hypothesis test + compose PNG |
| `tracery_section_U02.py` | Orders, moulding profiles, order partition, height-field piece mesher |
| `run_U02.py` | U02 build + QA + compose PNG |
| `tracery_joints_U03.py` | Joint layout, junction keep-outs, block splitting with open joints, multi-order block mesher (risers), `chassis_joint` (U05) |
| `run_U03.py` | Build + QA + GLB for U03, U04 and U05 (dispatches `"type": "rose"` specs to U04) + U03 PNG |
| `tracery_rose_U04.py` | `RoseModel` (rose construction) and `RoseJointed` (rose-specific joint rules) |
| `run_U04.py`, `run_U05.py` | Review PNGs for U04 and U05 |
| `blender_U01.py` | Blender QA + row render (U01) |
| `blender_U02.py` | Blender QA (+ optional render and raking close-up) for U02–U05; `qa` mode skips rendering |
| `specs_U01.json` | St-Leu rebuild, St-Leu ideal, 2-light, 4-light, intersecting |
| `sections_U02.json`, `joints_U03.json` | U02 orders/profiles, U03 joint settings |
| `specs/sections/joints_U04.json`, `…_U05.json` | Rose + regression sets |

## U01 — construction, topology, plain solids

**Spec (bar mode)**
```json
{"id": "bar_2light_sexfoil", "mode": "bar", "units": "mm", "tolerance": 0.5,
 "outline": {"arch": {"type": "equilateral", "span": 2400, "spring": 3600, "axis": 0},
             "frame": 160, "sill": 0, "sill_band": 200},
 "fill": {"type": "lights", "n": 2, "band": 80, "sub_arch": {"type": "equilateral"},
          "children": [null, null],
          "head": {"type": "oculus", "band": 80, "overlap": 40,
                   "foil": {"n": 6, "lobe_ratio": 1.18, "orient": "lobe_up"}}},
 "spandrels": "pierced", "fork_fill": 25,
 "section": {"depth": 240, "chamfer": 35},
 "wall": {"margin": 700, "depth": 900, "recess": 250},
 "expect": {"light": 2, "foil": 1}}
```
- Arch types: `equilateral`, `round`, `pointed` with `f` = radius/span and optional `drop` (centres below
  springing), or `measured` with `CL`/`CR` circles `[x, z, r]` (CR may be mirrored with `axis`).
- `fill` types: `lights` (n lights; each child may be another `lights` fill = recursion; `head: oculus`
  for n = 2) and `intersecting` (n lights, arcs concentric with the main arch).
- Oculus: centre and radius solved (Brent) so the ring is tangent to the main intrados and to the
  sub-arch extrados, each with `overlap`. Foil lobes: `lobe_ratio`, `orient` (`lobe_up`/`cusp_up`).
- `spandrels`: `pierced` or `solid` (stone spandrels). `fork_fill`: fills spandrel tips narrower than
  2 × value (tas-de-charge), keeping exact edges elsewhere.

**Spec (plate mode)** — `outline.arch` (usually measured) + `voids`: arch-headed lights (`arch`, `sill`),
`circles` (union of measured circles), or `regular` foils (`centre`, `n`, `ring`, `lobe_r`, `centre_r`).

**Topology rules** — openings = complement components (bar) or explicit voids (plate); seeded openings keep
path IDs (`W.L1`, `W.A2.L1`, `W.O`), unseeded ones get geometric order IDs (`S01`, `E01`); slivers below
`(10·tol)²` are filled and logged; boolean overlay spikes/micro-edges removed (`clean_ring`).

**U01 tests** — springings and apex on their circles (≤1e-9·span); oculus tangency residuals; foil lobes
intersect; seeds inside openings; stone one connected region; holes = openings; no near-pinch outlines;
expected opening counts; minimum stone web ≥ 2·chamfer + 2·tol; member graph connected; front-cap
triangulation area exact; stone/wall watertight, consistent winding, 0 non-manifold/degenerate/loose
vertices, one body, genus = openings; plain volume = area × depth; chamfered volume within 5 % of analytic
removal; GLB reload unchanged; bit-identical rebuild; reordered-spec keys keep IDs and mesh; exact 2× scale.
St-Leu: rebuild vs archived early R03 fixture (IoU ≥ 0.999, Hausdorff ≤ 1 px, volume within 0.1 %).

## U02 — orders and mouldings (`sections_U02.json`)

```json
"bar_4light_recursive": {"orders": [
  {"depth": 340, "profile": [["fillet", 8], ["hollow", 50, 50], ["fillet", 10], ["groove", 8, 5]]},
  {"depth": 280, "profile": [["fillet", 6], ["roll", 16, 14], ["hollow", 28, 26]]},
  {"depth": 220, "profile": [["fillet", 5], ["hollow", 24, 22]]},
  {"depth": 170, "profile": [["chamfer", 14, 14]]}]}
```
- Order of a member: frame 0; sub-arch bands/oculus ring at fill level n → n; foil cusps → ring order + 1;
  intersecting mullions/arcs → 1.
- Profile elements run from the opening arris onto the face: `["fillet", w]`, `["chamfer"|"roll"|"hollow"|"ogee", w, rise]`,
  `["groove", w, depth]`. Depth at the arris = sum of rises (must stay < 0.95 × half-depth).
- Face height = order half-depth − drop(distance to nearest opening, mitred offsets) → mouldings mitre
  along junction bisectors and cusp centre-lines automatically.
- Mesher: constrained triangulation (Triangle, no Steiner points) through the profile iso-lines, kept
  0.05·tol inside each region; vertices closer than tol/50 merged; mirrored back face; vertical walls.

**U02 tests** — order regions tile the U01 stone; no interpenetration (≤ tol/4); depths step back; moulding
depth < half-depth; triangulation covers each region exactly; each piece watertight, one body, genus = holes,
height field never crosses the glazing plane, volume within section bounds; U01 IDs/area unchanged; GLB
reload; bit-identical rebuild; 2× scaling (volume × 8, bounds × 2).

## U03 — masonry jointing (`joints_U03.json`)

```json
"bar_4light_recursive": {"joint_width": 6, "course": 440, "voussoir": 600, "min_block": 220,
                         "keepout": 150, "keepout_factor": 1.6, "sill_max": 2400, "max_block": 2500}
```
- Courses: equal heights from the sill to `min(springing) − keepout` (buttress-generator rule), shared by
  frame jambs and tracery mullions.
- Frame arch and every sub-arch band: voussoir joints radial to that half's own centre, greedy from the
  springing at ≥ 0.9 × `voussoir`, mirrored by fraction on the other half, crown joint where free, last
  stone ≥ `min_block`.
- Oculus rings: joints at lobe centres only (each cusp stays carved with its ring segment).
- Intersecting arcs: radial joints from the foot upward.
- Sill: split under principal mullions when longer than `sill_max`.
- Plate mode: coursed jambs/mullion + rays from the foil centre that reach the outline without crossing
  another opening.
- Junction keep-out radius = `keepout_factor` × width of the narrower member meeting there (overlaps =
  tangencies/crossings; shared-edge tops = springers/forks). No voussoir or ring joint may enter one.
- Open joints: `joint_width` strips removed from the stone; a stone spans every order at its location and the
  orders become risers inside it (block mesher with vertex columns so steps stay conforming).
- U05 options: `"chassis_joint": true` (open joint where the tracery meets the wall frame) and
  `"tracery_course"` (tracery uprights get their own longer stones, beds staggered from the wall courses).

**U03 tests** — stones + open joints account for the stone area; radial joints pass through their centres
(perpendicular offset ≤ 1e-6·size); no joint in a keep-out; largest stone ≤ `max_block`; every stone
triangulated with the full order/moulding linework (no fallback); risers consistent; every stone watertight,
one body, genus = holes, 0 non-manifold/degenerate, volume within section bounds; GLB reload; bit-identical.

## U04 — rose / wheel window (`specs_U04.json`, `"type": "rose"`)

Frame annulus; cusped hub oculus; `n` cells between radiating bars, each a wedge headed by a two-centred
pointed arch springing on the spoke centre-lines at radius `spring`; every cell owns a band so adjacent
bands form one bar of width 2 × `band`; a cusped circle on every spoke axis, solved tangent to the frame
intrados and the two neighbouring head extrados (with `overlap`). Joints: frame voussoirs radial to the rose
centre, bed joints across the bars, head voussoirs radial to their own centres, rings cut at lobe centres.
Tests add exact n-fold symmetry and the tangency residuals of the spoke circles.

## Blender checks (`blender_U01.py`, `blender_U02.py`)

`python3 -I blender_U02.py OUT RENDER_IDS ALL_IDS CLOSEUP_ID [qa|render] [closeup_height_frac] [closeup_width_frac]`
- imports every GLB (one object per stone/part), measures in Blender units: non-manifold edges and vertices,
  degenerate faces (area < 1e-12·size²), self-intersecting face pairs (BVH overlap, faces sharing a vertex
  excluded), vertex/face counts and bounds versus the exporter's report;
- stones get smooth-by-angle 32° (sharp arrises, smooth roll/hollow mouldings);
- renders with Cycles (CPU) unless `qa`, saves `*_review.blend` with the 3D viewport set to Focal Length 9.3 mm,
  Clip Start 0.01, Clip End 1e11.

## Problems Blender caught that the Python checks missed (keep these tests)

| Stage | Problem | Fix |
|---|---|---|
| U01 | collinear sill edges made earcut produce T-junctions | Triangle (conforming CDT) for caps |
| U01 | chamfer bands self-intersected at sharp spandrel tips | stitching by closest-point parameter along the opening |
| U01 | overlay spikes and near-pinches in opening outlines | `clean_ring`, tip fill by `P ∩ opening(P)⁺`, outline QA |
| U02 | walls through faces where iso-lines grazed member edges | iso-lines kept strictly inside each region |
| U02 | cusp pieces touching at foil tangency points; hairline slivers | one object per stone; hairline opening per order |
| U03 | crossing member outlines broke Triangle | exact noding, outlines kept only where orders differ, logged fallback |

## Coordinates and units

GLB: X right, Y up, Z toward the viewer (Blender converts to Z up). St-Leu specs use source pixels of the
545 × 825 engraving with Z = 778 − row (not calibrated). All other specs are parametric millimetres.
