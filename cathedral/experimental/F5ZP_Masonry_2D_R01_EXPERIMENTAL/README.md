# F5ZP masonry thickness study R01 — experimental

Prepared 6 November 2026. Scope: **2D masonry reservations added outside fixed vault-space references**. No existing cathedral model or generator is altered. This is a complete thickness comparison for the recovered enclosures; it is not a finished cathedral masonry plan.

## Proposed starting schedule

| Masonry use | Thickness, native units | Status and basis |
|---|---:|---|
| Ordinary chapel / enclosure wall | 250 | Proposed working allowance. Matches the recovered axial threshold return depth and makes a continuous outside reservation. |
| Main cathedral perimeter enclosure | 320 | Proposed heavier comparison allowance; selected for plan development, not calculated capacity. |
| Existing R03 chapel wall | 170 | Recovered experimental source parameter, retained as the thin comparison. Not a locked wall size. |
| Primary piers, responds, entrance jambs, buttress towers | Unassigned | Separate bearing footprints required. Wall thickness does not determine their size. |

The alternatives are **170 / 250 / 320**, all added outward. Neither 250 nor 320 is user-approved or historically/structurally certified. The ordinary-wall allowance is demonstrated on the axial chapel only; it is not applied to invented companion chapels or partitions.

## Measured effect of the proposed 320 / 250 combination

| Measurement | Fixed reference reservation | Proposed outside reservation | Increase |
|---|---:|---:|---:|
| Nave transverse band width | 13,930 | 14,570 | 640 / 4.594% |
| North-to-south transept terminal reach | 21,418 | 22,058 | 640 / 2.988% |
| Axial chapel transverse width | 2,500 | 3,000 | 500 / 20% |
| West reference datum to axial apse nose | 74,601.820645 | 75,171.820645 | 570 / 0.764% |

These are reference reaches and local enclosure widths. They **exclude** west towers, porches, side chapels, buttress towers and the unresolved eastern shoulders. They are not certified maximum dimensions of the entire completed cathedral.

The proposed west exterior is X−40333; the apse exterior is X34838.820645. Both chapel bays remain X28600–31000 and X31000–33400; the entrance threshold remains X28000–28600. The 2,500-wide chapel reservation stays fixed. The pre-existing entrance's reported **2,200 clear width** is a different quantity: its original jamb/respond geometry is not rebuilt or revalidated by this study.

## What the lines mean

The F5ZE source describes station and radial grids. R07 is a rib/bay projection, not a complete masonry-face survey. The exact F5ZN-A cell vertices recovered from the R03 input identify protected set-out geometry; the portable R07 cells round them to 0.01 units. Neither source establishes every line as a finished floor-clearance boundary.

For this experiment, the recovered bay footprints are conservatively treated as **do-not-consume plan reservations**. Existing vault dimensions, vertices and interfaces stay fixed. This is a study convention consistent with the user's instruction, not a new assertion about arch intrados, springing-center dimensions or accessible floor clearances. At actual supports, an overhead vault footprint and a ground-level pier can legitimately have overlapping plan projections; those must be resolved by section and by the actual rib/respond profile.

The saved R03 builder places its 170-unit chapel wall from the line at Y±1250 **outward**. Its threshold backing returns occupy Y1250–1500 on each side, i.e. 250 outward. This establishes a concrete source precedent for additive walls and explains the 250-unit chapel trial. The comparison drawings use uniform bands through the threshold and chapel, so the 170 panel is not a byte-for-byte reproduction of all R03 wall solids.

At a shared boundary between two protected cells, the free width is zero. A finite internal wall cannot be inserted there without either consuming a reservation or changing the set-out. This experiment therefore adds **no internal wall strips** on the shared ambulatory arches and does not move or spread the approved 14 cells. The small two-room drawing is a dimensional example for a future new set-out, not a cathedral modification. Its shared wall is counted once.

## Geometry and drawing conventions

- 1:1 numerical native project coordinates: X east, Y north, crossing (0,0); physical metres per native unit unresolved. No LittleTiles or viewing scale is applied to coordinates.
- Black solid: confirmed/reference outlines within the stated scope. Gray dashed: station/rib construction. Red dashed: proposed or unresolved outlines. Tan: proposed masonry reservation.
- Polygonal apse walls are true **perpendicular offsets with mitred corners**. Vertices are not scaled radially.
- The chapel entrance and choir east join remain uncapped.
- The choir outer envelope uses the MP-02 page 3 endpoint description, 6965→6657, with an explicitly **unverified linear interpolation**. It is an overview preview, not recovered bay-by-bay geometry or a revived old outer ambulatory. No R2 taper is fabricated; the 5429 versus Q1 5400 discrepancy is retained as unresolved.
- Transept central cores are shown. Exact lateral complexes, terminal porches and wall apertures are not reconstructed.
- No outer chevet closure, companion chapel station choice, internal pier diameter, buttress footprint, web, height or new 3D geometry is generated.
- Wall bands are reservation envelopes before doors, windows, engaged profiles and bonding are designed. They are not a built-stone plan at a certified cutting elevation.

## Validation actually performed

**49/49** builder checks and **38/38** independent exported-file checks pass. Three rendered PNG sheets were inspected; a dimension-label overlap in the chapel comparison was corrected and the revised sheet inspected.

Checks cover exact preservation of all 14 protected cell arrays and IDs, all seven shared inner/middle edges, original R07 receiving endpoints, nave/choir station chains, threshold/bay dimensions, valid polygons, outward offset distances, zero positive reserved-area intrusion at each of the three trial thicknesses, open entrance/interface, SVG parsing and actual GeoJSON/native-SVG export measurements. Maximum native-SVG coordinate rounding error is **4.775e−8** native units. The original compact R07 cell coordinates differ from the recovered high-precision source by at most **0.005867** units, consistent with their stated 0.01 rounding.

All local source snapshot hashes remain unchanged before/after generation. No approved Blender objects or approved generators were modified or regenerated. No new GLB or Blender file is appropriate for this plan-only assignment.

| Validation category | Result |
|---|---|
| Technical | Scripts execute, SVG/JSON parse, exports reopened numerically; pass. |
| Geometric | Reservation preservation, offsets and stated dimensions; pass within scope. |
| Architectural | Proposed wall schedule and unresolved joins require review; not approved. |
| Historical | Source logic consulted; trial numerical wall thicknesses not authenticated. |
| Structural | Not assessed. F5ZL-C physical support schedule remains missing. |

## Sources and recovery

GitHub Master Reference recovered successfully before substantial work: repository `beepboop1111/cathedral-gothic-research-repository`, branch `cathedral/governance-r01`, `cathedral/governance/CATHEDRAL_MASTER_REFERENCE.md`, blob `1d7e358ff7562fcc64088854baa2abd3d31a729e`. It remains provisional governance.

| Source | SHA-256 | Use |
|---|---|---|
| Original F5ZE global coordinate JSON | `3c30934df8663e0e13903eca30e192aa9a4313f2822dfcb49615ef51ef06e84f` | Whole-plan station chain and nave bands, verified on MR COMPUTER. |
| Original corrected F5ZE master JSON | `378d3a7875b98ac0a03c2425ebf71427c9cf9deeb2d33b15d5ae760a65e5d354` | Cross-check dimensional authority and lineage. |
| F5ZN-A comprehensive checkpoint | `97014cf07fccf1d5ed91e78b5cb20d557d55931cfd706921d46342a35dabb352` | Live recovered compiled reference. Mentions the missing support CSV, but does not supply it. Older outer values are not revived. |
| Original R03 `inputs/BASELINE.json` | `066027d5fa0e673b5c267718e906d105c86272b6358fcc8bf2a33a5d3fa92a19` | Full-precision 14-cell subset only; discarded outer cells excluded. |
| Original R03 `build_chapel.py` | `20f4829794624a6fa72f65663ee93c49225959eaa047256bfe685c12730cee5c` | Read-only lines 184–201 establish 170 outward walls / 250 threshold returns. |
| Original full R07 plan JSON | `6687e9d004b5b7b1ffa2590ad8f224d6c9df2e4343c9b0a69b1ac1942b30b317` | Exact R03 set-out and middle interface; subset retained here. |

Exact source paths, hashes and read-only extracts are in `inputs/RECOVERED_SOURCE_EXTRACT.json`. It is a derivative extraction; its hash is distinct from the original files' hashes. The original F5ZE JSONs were verified inside `~/Desktop/F5ZP_R07_FULL_CATHEDRAL_PLAN_ADDENDUM_R01.zip` on MR COMPUTER. The MP-02 atlas pages 1–4 were text-inspected there; no visual inspection of that original PDF is claimed. The attached coordinated handoff was read locally; historical originals remain untouched.

Historical context: Viollet-le-Duc, *Dictionnaire raisonné*, volume V, article on scale, explains compound piers in relation to the arcs they carry. That supports treating support design separately from a blanket wall width; it does not determine this project's 250/320 allowances. See [primary text, volume V](https://www.gutenberg.org/cache/epub/30785/pg30785-images.html) and [volume IV, printed p.198](https://fr.wikisource.org/wiki/Page:Viollet-le-Duc_-_Dictionnaire_raisonn%C3%A9_de_l%E2%80%99architecture_fran%C3%A7aise_du_XIe_au_XVIe_si%C3%A8cle,_1854-1868,_tome_4.djvu/200), concerning distinct functions and exterior expression. No dimensions have been imported from those books.

## Files and reproduction

Run from any location:

```bash
python build_masonry_study.py
python verify_exports.py
```

Requires Python with numpy, matplotlib and shapely≥2. Exact executed versions are in `outputs/NUMERICAL_QA.json`. `CONFIG.json` records the R01 trial and proposed schedule; R01's mixed-schedule overview is explicitly the 320/250 candidate.

- `outputs/01_WHOLE_CATHEDRAL_MASONRY.png`: full context with limitations printed on the sheet.
- `outputs/02_AXIAL_CHAPEL_THICKNESS_COMPARISON.png`: three matched trials.
- `outputs/03_SPACE_AND_MASONRY_RULES.png`: nave band dimension chain and shared-wall example.
- Each sheet has a matching `_SHEET.svg` for presentation; its viewBox is page layout, not project coordinates.
- `outputs/MASTER_PLAN_NATIVE_1TO1.svg` and `AXIAL_CHAPEL_NATIVE_1TO1.svg`: **one SVG user unit equals one native project unit**. SVG's downward Y is reflected once. Pixel display width is not an SI calibration.
- `outputs/PLAN_GEOMETRY_NATIVE.geojson`: local Cartesian coordinates, not geographical coordinates.
- `outputs/PROTECTED_VAULT_COORDINATES.json`: exact recovered cell IDs/vertices.
- CSV comparison, measurements, source hash record and both QA reports accompany the geometry.

## Checkpoint and remaining decision

**Preserved:** F5ZK-C/F5ZN-A, all 14 original inner/middle set-outs and seven shared interfaces, 1:1 numerical scale, R07 original orange chapel set-out, four-rib approach references, working vault generator, V13 webs and Pass 6J records. The rejected 817.49 chapel translation and discarded outer-ring geometry are not reinstated.

**Proposed delta:** outside plan wall reservations only: main perimeter 320 and axial ordinary enclosure 250, compared with 170/250/320 alternatives. Source geometry is not promoted or replaced.

**Unresolved:** architectural acceptance of the proposed schedule; exact choir bay-by-bay taper and 29-unit R2 discrepancy; missing F5ZL-C support footprints; internal piers/responds and chapel-mouth bearings; actual outer chevet closure and companion-chapel arrangement; final exterior extents, apertures and ground clearances; physical unit calibration; structural capacity. No M01 completion or architectural approval is claimed.

The next bounded design step is to review this wall schedule and then recover the actual pier/respond footprints at shared vault nodes before making a masonry ground plan. Any experiment that changes protected bay positions must remain a separately approved scope.
