# Gothic Architectural Plate → Geometry → Modular 3D Workflow

**Checkpoint:** 2026-11-03  
**Scope:** Research exports 02 (illustrations) and 03 (research/tools), and Gothic V08 portable preview.  
**State:** Intake verified; initial figure-1205 study case seeded. **Not** an architectural geometry approval.

## Project objective

**Historical plate → source-backed geometric interpretation → one representative sector/module → parametric repetition → optional smooth 3D stonework → quality assurance → explicitly approved integration.**

Do not require a full radial motif to be redrawn before testing one 45°, 90°, or other representative sector. Repetition applies only where the source supports a symmetrical module. Decorative heads or irregular carved details are *separate individual modules*, not automatic copies of one head.

## Directory and source rules

- Keep uploaded `.tar.xz` files **read-only**, and refer to `PLATE_AND_TOOL_MANIFEST.json` for SHA-256 and retained archive paths.
- Do not import or execute Python scripts stored in historical archives as part of intake. Run portable V08 tests separately before using the tools.
- The legacy F5ZP geometry, approved dimensions, existing `sketch2stl.py`, `plan2geometry.py`, `geometry2stl.py`, and remote Blender scenes are **not included** in the two tar exports and have not been changed or verified by this workflow.
- The 12 distinct retained entries under `01_Original_Books/` remain outside the two uploaded tar parts. `START_HERE` explicitly warns that some source catalogues have selections only, not complete full editions.
- All SVG/JSON coordinates from old plate scans default to **source image pixels** (Y down). Never equate them to F5ZP blocks, meters, or historical masonry dimensions without explicit scale evidence.
- Source plate, extracted contours, measured fits, proposed construction, and final modeled geometry must have separate identities and filenames. A neatly closed reconstruction is not necessarily a historically documented construction.

## Per-plate operating procedure and stage gates

| Stage | What we do | Saved artifacts | Gate |
|---|---|---|---|
| **00 — Register** | Locate exact archive member, checksum, author, edition, printed figure, page, full/selected status | `source.json`, retained file path | File hash matches source index |
| **01 — Prepare** | Read high-resolution source, crop one well-defined figure, preserve original; generate contrast/ink masks as derivatives | source crop, V08 plate metadata, crop transform | Original pixel coordinates recoverable; no destructive normalization |
| **02 — Interpret** | Read caption and construction instructions; transcribe/translate marks, distinguish facts from hypotheses | `evidence.md`, citations/page pointers | Author's stated method distinguished from inferred relationships |
| **03 — Recover** | Trace ink strokes; fit lines/circles/arcs; identify intersections and candidate cusps; preserve incomplete strokes | measured SVG/JSON, residual plots | Measured source retained, error and rejected alternatives documented |
| **04 — Construct** | Reproduce an exact compass/straightedge family or parametric path from one source-supported module | construction SVG/JSON, parameter manifest | Historical support and parameter assumptions separated |
| **05 — Propagate** | If justified, repeat by rotation, mirror, translation, or path, preserving individual irregular ornament slots | master SVG/JSON, instanced/flattened outputs | Rotation origin, interval and instance count independently checked |
| **06 — Stonework** | Only with a traceable cross-section and scale policy, sweep between measured rails; preserve source rails | STL/GLB/Blender study, geometry metadata | Watertight solids and rail errors checked; dimensions still provisional if uncalibrated |
| **07 — Verify** | Compare overlays with source, validate residuals, seams, topological boundaries, 3D collisions and reproducibility | QA JSON, comparison images, rejected hypotheses | No fabricated historical certainty; mesh seam behavior recorded |
| **08 — Integrate** | Candidate is explicitly reviewed against current cathedral locked baseline and geometrical/collision constraints | integration review, versioned component | **Requires user approval**; never auto-overwrite approved F5ZP geometry |

**Strict stop rules:** An automatic contour join is not a confirmed cusp; a recognized repeated radius is not an original compass radius; a 3D relief is not a surveyed carving; a manifold mesh is not proof of masonry stability; an image-pixel measurement is not a cathedral-scale dimension.

## Which modules participate

- `gothic_plate_reader.py` — SHA-256, metadata, crop, ink and explicit calibration.
- `gothic_geometry.py` — fitted circular geometry, conservative contour pairing, radius groups.
- `gothic_patterns.py` — master sector/partial copy, rotational/linear/mirror instances, separate ornament references.
- `gothic_stonework.py` — non-voxel 3D two-rail sweep and linked scene instances.

**Important:** Gothic V08 is version `0.8.0-preview` and all 11 bundled tests passed in this package. It is not yet a fully integrated GUI/CLI for the old generators and does **not** by itself recognize every cusp, animal head, pier, buttress or stone section.

## Active figure 1205: what is already established

Source: Ungewitter–Mohrmann, *Lehrbuch der gotischen Konstruktionen*, Vol. II, 1892, printed page **510**, corresponding PDF page **280**, with drawing Plate **CXVIII**, PDF page **281**. Printed figure **1205**. **1205b** is the inherited measurement-package identifier, not a confirmed printed suffix.

The text states that four, five, six, etc. cusps may be created and that the centers can be chosen between marks **a** and **b**, changing cusp shape. The exact design radius is **not prescribed**. The source does **not explicitly define c** in the cited paragraph.

**Immutable measured reference:** outer circle O=(109.21742236738913, 111.23955699522183) pixels and R=93.51694870364518 pixels. **Source units** are 144-DPI crop pixels, not architectural dimensions.

| Previous candidate | d/R | RMS (same plate sample regime) | Geometric reading |
|---|---:|---:|---|
| Upper construction | 0.541743 | 0.661 px | Adjacent circles intersect; produces pointed cusp alternative |
| Lower construction | 0.609963 | 0.779 px | Adjacent circles separate by ~7.719 px |
| Exact critical case | 0.585786 | Not fitted to source | Tangency transition; possible **c** interpretation, still unproved |

The full comparison report explains that a two-parameter upper/lower model fits the selected ink substantially better than a single parameter for all six arcs. Both alternatives are **retained as alternatives**, not merged into one idealized figure. Do not fill lower separations with invented cusp arcs.

**Next bounded research pass (Step 01):** Independently trace the thin printed guide curves and letter stems for **a/b/c** on the marks crop. Compare mark estimates with the critical-point calculation; do not declare `c` to equal that construction without stronger evidence. Preserve the baseline and both alternatives.

Existing results have been copied, with hashes verified, to `cases/UM_II_CXVIII_FIG_1205/`. The case is **seeded**, not newly refitted. See `CASE_STATUS.json` and `historical_progress/REPORT.md`.

## Next recommended plate targets after 1205

1. `UM_II_p281_trefoil_quatrefoil.png` — immediate cross-check, same plate family.
2. `UM_II_p273_cusped_window_head.png` — pointed/cusped arch module; does not assume radial symmetry.
3. `UM_II_p313_large_rose_and_intersection.png` — repeated circular construction.
4. `UM_II_p327_pierced_gable_patterns.png` — nonradial repetition and ornamental edges.
5. `UM_I_p167_tas_de_charge_junction.png` — support/springing research, geometry only, **not** automatic structural design.

Source names above are grounded archive members in Part 02. Their quality and use as exact surveys must be verified individually. More high-resolution replacements can be registered without modifying prior original scans.

## Consistency and milestone workflow

- Every case has an immutable **source**, separate **measurements**, separate **construction hypothesis**, and optionally a **build**.
- Every case records `source_sha256`, original page and printed figure, crop-to-page transform, coordinate units, parameter choices, fitting residuals and rejected alternatives.
- Every handoff captures four things: **what is source-established, what is fitted, what is only proposed, and what has been explicitly approved**.
- Model one element; compare it against independent neighboring evidence; repeat only when symmetry is justified. Preserve individual carved terminals separately.
- A checkpoint only supersedes a prior checkpoint after a named and documented review decision. No automatic promotion into F5ZP or silent replacement of locked cathedral geometry.

## Reproducible first actions

From this workflow folder:

```bash
python build_inventory.py
cd Gothic_V08_Project_Integration
python -m unittest discover -s tests -v
cd ..
python start_figure_1205_case.py
```

**Do not run archived `scripts/compare.py` until reviewing its inputs and confirming its output targets are isolated from the preserved archive.** A fresh analysis should write into a new case `working/` folder, leaving `historical_progress/` unchanged.
