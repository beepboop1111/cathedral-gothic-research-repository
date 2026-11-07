# Gothic 2D — five illustrated workflows (research record, pending approval)

**Status:** RECORD CREATED; NOT APPROVED AS HISTORICALLY VERIFIED GEOMETRY OR AS A LOCKED GENERATOR.

These five sequential illustrations were made with the ChatGPT **image-generation tool**, from conversational visual direction. **No Python, SVG, CAD, V08 or other geometric script was executed to produce those five original PNGs.** The creation process did not provide exact original tool prompts, geometric parameter files, or deterministic seeds. Consequently, the PNG images are useful visual references only; they are not dimensionally validated or exact reproducible mathematical outputs.

## Drawing standard (requested and used across the series)

- **Black solid:** principal visible outlines of foils, rings, window frames and pointed arches.
- **Thin dashed light gray:** symmetry, centerlines, dividing axes and sector guides.
- **Dotted black:** complete recovered or proposed compass/construction circles where needed. In these five generated examples they are *illustrative construction circles*, not verified recovered circles.
- **Red dashed:** uncertain or experimental geometry. No red line is necessary unless a specific proposed uncertain construction is shown.
- **Original research material:** preserved as supplied; no historical plate is modified.

## Five operations, in the exact order carried out

| ID | User instruction | Visual result | Procedure captured | Verification status |
|---|---|---|---|---|
| W01 | “make a quad foil with Standard drawing conventions” | Symmetric four-lobed quatrefoil and axes | Four lobes at 90° intervals; black perimeter; dotted circle studies; gray axes; proposed central geometric guide | Image generated; not measured |
| W02 | “build a octafoil with a outer ring” | Eight-lobed octafoil inside two concentric ring outlines | Eight lobes at 45° intervals; radial construction; concentric outer ring | Image generated; not measured |
| W03 | “sextafoil” | Six-lobed sexfoil within outer circular ring | Six lobes at 60° intervals; center marks; dotted circular layout | Image generated; not measured |
| W04 | “add a pointed arch over the sextafoil” | Sexfoil retained in ring, inside layered pointed Gothic window arch and jambs | Compose ring + sixfold foil + symmetrical pointed arch, preserve axes and construction guides | Image generated; not measured |
| W05 | “add a pointed arch over the octafoil” | Octafoil retained in ring, inside layered pointed Gothic window arch and jambs | Compose ring + eightfold foil + symmetrical pointed arch, preserve axes and construction guides | Image generated; not measured |

Each original generated PNG is retained as `source_images/W##_image_generated_reference.png`.

## Scripts and tools actually used to create those five images

1. **ChatGPT image-generation tool:** all five original PNG illustrations.
2. **V08 modules:** **not executed in the creation of these five images**; they exist as separately supplied source material and may serve future 2D reconstruction.
3. **Other Gothic generators and scanning modules:** **not executed in the creation of these five images**.

## New mathematical experimental implementation (created *after* the images)

`rebuild_five_2d.py` is an independently authored Python standard-library research script that produces five **new vector concept studies** in `vector_experiments/`. It is **not** the script that generated the original illustrations, nor is it a pixel-perfect recreation. It expresses repeatable circular lobes, intersections, axes, ring outlines, and two-centered arch frames in SVG, with numeric geometry parameters in CSV.

- Foil centers are evenly spaced on a pitch circle.
- Adjacent congruent construction circles intersect to define candidate cusps.
- Selected outer circular segments define the black foil outline.
- Where requested, a concentric double line defines a ring.
- Window arches use circles centered at opposing springing positions for the two pointed halves.
- Image coordinates are **uncalibrated pixels**, **not architectural units or approved dimensions**.
- The arbitrary lobe-radius multiplier (1.18), pitch radii, ring thickness and arch placement are **new experimental design choices**, not historical findings.
- The generated SVGs are *candidates pending visual inspection and user approval*.

Run `python rebuild_five_2d.py` from any folder. The script only writes into its own `vector_experiments/` folder. It does not alter cathedral geometry, existing generators, historical sources or previous files.

## Approval and versioning policy

1. User reviews the visual reference, construction method, intersections, circle centers, outline quality, and evidence labels.
2. Any revisions produce new versioned drafts; previous drafts and source imagery are retained.
3. Only after explicit user approval may a version be promoted to a project working 2D baseline.
4. Saving this ZIP as a downloadable package is **not equivalent to attaching the script to the Project's file collection**; the latter must be performed through the Project interface.
5. 2D and 3D engines remain separate until each has its own tested and approved workflow.

## Recommended validation before promotion

- Check ring/foil tangency rather than merely approximate visual similarity.
- Check every cusp and the true arc endpoints for positional and tangent continuity.
- Ensure arches and ring geometry connect appropriately without unsupported conjecture.
- Compare historically claimed constructions against a cited original plate and any written set-out directions.
- Include numeric residuals, checksums, and SVG QA on later runs.
