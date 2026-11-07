# Experimental Sketch2STL / Ungewitter / Haina findings, 2026-11-04

Status: **unapproved workflow and research experiments**. This report indexes early local tests without promoting them over later tracery generators.

## Sketch2STL Gothic window playground
- Created a two-lancet and quatrefoil test with raster-to-STL pierced and relief modes; opening segmentation was substantially more reliable using an explicit black-stone silhouette than thin diagram linework.
- Chamfered and alternate double-sided ogee-edge variants generated technically watertight, consistently wound sample meshes; preliminary examples were approximately 278k triangles each. Mesh integrity is not historical precision.
- Original script kept unchanged; arbitrary 100 mm test width was **not** calibrated to a historic window.

## Ungewitter top-row second panel
- Selected the second pointed window from the top row of the supplied construction-variant plate; user accepted its initial opening arrangement.
- Direct-source automatic hole detection mistook construction circles for masonry. R01 manually interpreted central three-lobe opening with **provisional three overlapping circles**; R02 supersampled/smoothed its raster silhouette, removed a small isolated dot and regenerated chamfer/ogee comparison meshes.
- The R02 high-resolution image still retained jagged line artifacts and did **not** recover true analytical circular arcs. Future work: measured 2D source curves before historically informed 3D sections.
- R01 and R02 ZIPs are checksum-indexed alongside this report, not embedded here.

## Haina tracer stress test on MR.COMPUTER
- Original raster 1,555 × 1,787 pixels; initial STL contained 3,699,880 triangles (~177 MiB binary STL), with recognizable upper octofoil, two lower sexfoils, pointed arcades and engraved concentric lines. It also preserved broken strokes and tiny protrusions; 652 degenerate triangles were detected in the original STL check.
- A **2× Lanczos supersampled** source (3,110 × 3,574) generated 14,275,288 triangles (~681 MiB) in **11.67 seconds** with peak resident memory about **3.30 GiB**. Both detected 32 numbered cutouts with the same two chosen fills; when compared at original pixel sampling, blue-cutout mask IoU was ~0.9623, outside mask IoU ~0.9696, and mean preview RGB difference ~3.65 / 255.
- Upsampling incurred ~3.86× polygon cost for modest visible benefit; no additional historical information was introduced. An input base depth of 1 mm capped the requested 1.5 mm edge cut at only 0.20 mm.
- The Haina stress test is a computational result, not verification of the historic geometry or a real moulding profile. Source and model remain locally preserved; this archive reports findings, not uploaded 681 MiB STL.

## Preservation
- Experiments are separate from approved cathedral architecture. No approved F5ZK-C/F5ZN-A geometry, Pass 6J record, vault generator, or historically original plate is changed by this report.
- See [Early St. Leu Fig. 80 archive](../early-fig80-study-2026-11-04/README.md) for exact early study coordinates, numerical QA and R03 Blender reproduction.
