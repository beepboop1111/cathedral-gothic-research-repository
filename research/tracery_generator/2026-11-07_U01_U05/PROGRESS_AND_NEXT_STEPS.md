# Progress, findings, open issues and next steps — 2026-11-07

## Timeline

| When | Step | Where |
|---|---|---|
| ≤ 2026-11-06 | M02/M03 R03 repair + semantic IDs (four windows), early St-Leu R01–R03, Gothic 2D research, buttress R04–R07 | already in the repository |
| previous chat | M04 R01 (window head + six-lobed foil) and R02 (lancet heads, side openings) from Brandon v2 p181 | **not in Git** — package and scan must be attached to continue |
| 2026-11-07 | U01 universal construction + topology + plain solids, St-Leu fixture regression | this folder |
| 2026-11-07 | U02 orders and mouldings | this folder |
| 2026-11-07 | U03 masonry jointing | this folder |
| 2026-11-07 | U04 rose / wheel window | this folder |
| 2026-11-07 | U05 tracery as its own masonry layer | this folder |
| 2026-11-07 | Clean rebuild of U01–U05: identical meshes, all Python + Blender QA pass | this folder |

## Findings worth keeping

1. **St-Leu Fig. 80 rebuild vs the archived early R03 fixture** — IoU 0.99947; maximum boundary difference
   0.58 source px, located at the outer-arch apex where R03 merged a 1.68 px crown seam (≤ 0.42 px elsewhere);
   plain volume within 0.0007 %. The acceptance limit was set to 1 px *after* locating that seam (first trial
   limit 0.5 px).
2. **Construction hypothesis (symmetric arches + regular sixfold foil) vs measured St-Leu** — outer arch
   0.005 px, lancets 1.07 px, foil up to 3.36 px (lower lobes). The drawn foil is not a strictly regular
   sixfold construction at this precision; engraving/tracing error and medieval construction cannot be
   separated from the engraving alone.
3. **Measured relationships** (early R01 fits) — the oculus ring is tangent to the enclosing-arch inner
   contour within 0.6 px and sits 22.8 px clear of the lancet outer contour.
4. **Moulding intersections** need no special junction code: face height as a function of mitred distance to
   the nearest opening produces mitres at junctions and ridges down cusp centres.
5. **Jointing** — fixed-size keep-outs blocked every joint in narrow sub-window members (one 2.8 m stone);
   scaling keep-outs to the narrower member width fixed it (largest stone 2.4 m). Ring joints at lobe
   centres keep each cusp in one stone with its ring segment.
6. **Blender is a necessary test** — it caught six classes of defects that watertightness checks in Python
   did not (see `WORKFLOWS.md`).

## Decisions taken in this work

- U01–U03 remain regression fixtures; new features get new version numbers.
- Stones span every order present at their location (orders are stepped surfaces, not separate stones);
  cusps are carved with their ring.
- Tracery may be its own masonry layer separated from the wall frame by an open joint (U05 option).
- Joint widths, course heights, voussoir lengths, keep-outs, order depths and profiles are TRIAL values.

## Open issues and limitations

- Four repaired M02/M03 windows (Haina 1264/1265, Meaux, Châlons) were untouched; their 288 MB bundle is
  not in Git, so their regression tests were not rerun.
- M04 Brandon R01/R02 (previous chat) and the Brandon p181 scan are not in Git.
- No glazing groove (feuillure), iron armature (vergettes, barlotières), hood moulds/label stops, cusp
  terminations, or wall coursing beyond the frame.
- Open joints are gaps; no mortar solids. Frame/tracery contact is a shared face unless `chassis_joint` is on.
- U02 neighbouring order pieces overlap by at most 0.007 mm; hairline slivers up to 8.2 mm² per window removed.
- U02 2× scaling is checked by volume and bounds, not vertex identity (GEOS noding is not scale-exact).
- One asymmetric voussoir note on the 2-light (a mirrored joint fell in a keep-out).
- St-Leu jointing (rays from the foil centre, one large lower head stone) is a speculative trial.
- Nothing is placed in the cathedral model; nothing is structurally assessed.

## Next steps (proposed order)

The wider scope is Gothic stonework, not only windows: buttresses, towers and pointed spires, stone
spandrels, plate and bar tracery, moulded mullions, and cusped circles with radiating bars. U01–U05 already
cover plate tracery, bar tracery, moulded mullions, cusped circles with radiating bars (rose) and solid
spandrels (`"spandrels": "solid"`, not yet demonstrated). Each new module reuses the same arcs, orders,
mouldings, jointing, QA hierarchy and Blender checks; tracery becomes a *panel* that other elements host.

| # | Module | Content | Reuses | Acceptance |
|---|---|---|---|---|
| N0 | 3D assembly layer | place planar panels (windows, blind tracery, gables) on the faces of massing solids by rigid transforms; massing solids from extruded/lofted polygons; robust unions only where stones are genuinely one piece | U01–U05 panels | panels keep IDs and QA after placement; no interpenetration between neighbouring stones |
| N1 | Blind tracery + stone spandrels | `blind` mode: openings recessed instead of pierced (panels on buttresses, towers, spandrels); carved roundels/quatrefoils in plate spandrels | U01–U03 | recess depth < half-depth; blocks watertight |
| N2 | Pinnacle | square or octagonal shaft, gablets with small tracery, pyramidal spirelet, crockets on arrises, finial; coursed | N0, N1, U02 profiles | symmetric, watertight stones, coursing |
| N3 | Buttress | stages with sloped set-offs (weatherings), blind-tracery faces, pinnacle cap; attach to the existing F5ZP flying-buttress R04–R07 attachment API instead of rebuilding flyers | N1, N2, buttress R04–R07 coursing | stage setbacks, drip slopes > 0, joints coursed with wall |
| N4 | Tower | square stages with string courses, corner buttresses, belfry openings (tall 2-light bar tracery), parapet and pinnacles | N0–N3, U01–U05 windows | stage loads/footprints recorded; openings keep window QA |
| N5 | Spire | octagonal spire on a square tower with broaches or corner-pinnacle transition; pointed pyramid (optional entasis), lucarnes (gabled openings), crockets, finial; openwork option = tracery panels on the inclined faces (Freiburg/Strasbourg type) | N0–N4 | faces planar, transitions closed, openwork panels pass tracery QA |

Cross-cutting items: X1 M04 Brandon measured window (needs the scan + R02 package); X2 measured moulding
sections (calibrate Moore 139a against its scan); X3 glazing groove + iron armature as separate objects;
X4 hood moulds, label stops, cusp terminations; X5 wall coursing bonded to the frame; X6 placement into the
cathedral (e.g. the locked 1,372 mm C-arch openings of the third ring) and any export to Minecraft tools only
after explicit approval; X7 promotion to an approved baseline only at the M06 human review gate.

## Working rules for future chats (as set by the project owner)

No GitHub access unless asked; minimise tool calls and file reads; reuse validated work instead of
regenerating it; test generator output as GLB structures in Blender and deliver one PNG of the result; keep
replies short; always separate technical, geometric, architectural, historical and structural validation;
preserve approved geometry, generators and scale.
