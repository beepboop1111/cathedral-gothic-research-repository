# Gothic 2D mirrored color/depth workflow R02 — for review

Reruns the experimental R01 depth-classification idea on the complete mirrored black-line PNG. All sources unchanged. **Not approved**.

The files `MIRRORED_DEPTH_COLOR.png` and `MIRRORED_DEPTH_COLOR_EDITABLE.svg` implement colored faces and preserved black linework. `FACE_REGISTER.csv` records every selected face and its candidate class.

## Conventions
- Orange: identified or provisional opening
- Green: provisional closed/spandrel face
- Purple / indigo / blue / cyan: proposed outer-to-inner visual layer order
- Yellow / orange-red: foil rings and inner moulding faces
- Black: source-derived linework
- White: unclassified/background

## Reproduction
`python rebuild_depth.py "SOURCE_MIRRORED_UNMODIFIED.png" --out-dir .`

## QA and limitations
This is **face coloring**, not exact compass construction. Some color-layer assignments are geometric heuristics, not independently verified masonry classifications. Lower cropped openings use provisional masks. Compare each region with the historical source before approval. No cathedral generator or locked dimensions modified.
