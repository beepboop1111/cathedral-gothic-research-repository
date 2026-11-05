# R06 overall context review

Open `outputs/F5ZP_X02_R06_OVERALL_CONTEXT_REVIEW.pdf` for the plan, two context views, measured height hierarchy and recommendations. The editable Blender review scene and GLB sit beside it. They preserve R05 architecture and add flat, named diagram guides for the rest of the precinct. These guides do not define building heights.

The review finds a coherent east-range composition, a garth free of R05 roof projection, and a chapter court with approximately 41% of its footprint under R05 roof projection. The residential roof peak is only 0.50 m above the chapter-house peak. The next priority is the actual N4/CH-N5 cathedral connection and the intended openness of the chapter court.

The cathedral reference remains an experimental north-edge fragment. A complete verified cathedral mass in this frame is unavailable, so the review does not claim a full-cathedral silhouette or scale comparison. No roof heights or approved architecture were changed. F5ZL-C remains unresolved.

## Reproduce

`python3 build_review.py` reads copied JSON sources and writes measurements, QA, diagram inputs and the 1:1 SVG. Once the two native render JPGs exist under previews, it also writes the PDF. Requirements are in requirements.txt.

Place this folder beside the saved `F5ZP_X02_R05_BEARINGS_AND_ROOFS` folder on MR COMPUTER and run `blender -b --factory-startup --python build_context_blender.py`. It opens the current saved R05 file read-only, verifies 151 architecture mesh signatures, adds the context guides, and saves new R06 files plus two renders. It never saves over R05. If reproducing elsewhere, point the `source` variable at the R05 Blender scene being reviewed and record its hash.

Source hashes, saved-model comparison, Blender preservation QA, measurements, export QA and the experimental GitHub version receipt support a fresh continuation. No generator replacement or approval promotion is implied.
