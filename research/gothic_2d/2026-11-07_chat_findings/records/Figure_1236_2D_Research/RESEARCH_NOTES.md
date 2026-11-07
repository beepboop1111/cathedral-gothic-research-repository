# Figure 1236 — historically grounded 2D reconstruction, first measured stage

**Checkpoint:** 2026-11-04 (source pixels; not architectural scale).  
**Primary historical source:** Georg Gottlob Ungewitter, revised by Karl Mohrmann, *Lehrbuch der gotischen Konstruktionen*, Vol. II (Leipzig, 1892), Plate **CXX**, figure **1236**, construction discussion on printed page **517**. Library record: https://digital.ub.uni-paderborn.de/ihd/content/titleinfo/7359921 . Relevant digitized book section: https://digital.ub.uni-paderborn.de/download/pdf/7403062.pdf . This publicly accessible edition is identified as CC BY 4.0 by the UB Paderborn site. Original cropped image remains an unaltered copy of the user's handoff; identify it by `source_sha256` in `FIG1236_QA.json`.

## 1. What the historical text actually prescribes

A **two-part window with an upper quatrefoil** and **trefoil-shaped subdivision arches** below. The historical chapter says to take `a` and `b` as the centers of the enclosing pointed arch. The placement of the quatrefoil is related to a construction in which **ac = cd**, expressed equivalently by the author as the line **ad at 45 degrees**. The four arc centers are positioned on the construction lines **gf** and **eq** at equal distances from center **d**, while the radius is chosen to achieve an attractive quatrefoil and retain at least the full stone-bar thickness at **n**. Then the quatrefoil is surrounded by a bar profile. The lower trefoil arches are set to maintain the minimum full bar thickness and can use the radius **hi** for their lower arcs; a perpendicular bisector is used to find a tangent-compatible upper trefoil arc center in the author's procedure. The paper also explains two layout sequences: construct center-lines and add thickness, or construct clear openings, surround them with profile width, then close secondary openings.

**Interpretation boundary:** This supports use of circles, equal-distance center placement and tangency constraints. The exact lobe radii, some local construction-point letter identities, and the complete contours cannot be recovered from the text alone. **No claim is made that modern fitted contours equal a uniquely prescribed compass radius.** The draft's letter placements are visually interpreted, not independently verified transcription from a full uncut plate.

## 2. What the supplied crop actually supports

The image measures **355 × 338 source pixels** (X right, Y downward), and is cropped across the two lower trefoil windows. It has no verified architectural length calibration. The upper four-lobed aperture is sufficiently visible to measure **four separate circular arcs**, and its external bar boundary is sufficiently visible to fit another **four related concentric circular arcs**. Full source image or the entire window's lower geometry were NOT supplied in this handoff. The grey axes are analytical constructions: they are not certified as printed source ink.

The V08 `gothic_geometry.circle_fit` routine was applied to **657 selected source-ink positions**, collected near independently designated candidate circles by searching for the dark engraving stroke radially. Table of results:

| Arc | Fitted center (x, y) px | Radius px | Selected-point RMSE px |
|---|---|---:|---:|
| Inner top | (173.611, 88.588) | 41.703 | 0.186 |
| Inner right | (225.414, 141.925) | 41.336 | 0.191 |
| Inner bottom | (171.902, 194.196) | 41.550 | 0.185 |
| Inner left | (120.012, 140.273) | 41.281 | 0.166 |
| Outer top | (173.510, 88.667) | 49.947 | 0.199 |
| Outer right | (225.441, 141.857) | 49.421 | 0.198 |
| Outer bottom | (171.954, 194.533) | 49.563 | 0.199 |
| Outer left | (120.184, 140.276) | 49.534 | 0.179 |

**Important numerical qualification:** These are local radii residuals **only for selected high-contrast pixels within narrow search windows around initial candidates**. They are not a pixelwise whole-image matching score and cannot prove the historical tool path or precision. Selection itself conditions the residual, making the very low numbers unsurprising. The fit center/radius parameters are independent per lobe; they have **not** been artificially made equal by a symmetry constraint.

The inner-circle mean radius is **41.468 px**, the outer mean **49.616 px**. Paired radial offsets are **8.244, 8.085, 8.013, 8.253 px**, mean approximately **8.149 px**. The inner center lattice's horizontal span (right minus left) measures **105.415 px**, and vertical span (bottom minus top) measures **105.622 px**. The midpoints of those two diameters differ by just **0.297 px**. Four adjacent center-to-center separations are approximately **74.35, 74.81, 74.84, 74.46 px**. This is strong evidence for a nearly square regulating lattice *in this reproduction*, but historical instructions themselves must remain the authority for design intent.

## 3. Arc intersections and contour visibility

The 4 inner fitted circles and 4 outer fitted circles each intersect near the four visible concave cusps. A closed true-circular path was produced by selecting the **source-facing intersection** of each adjacent pair, **not** the intersection inside the center square. The inner cusp sites are approximately UL=(133.93,101.41), UR=(212.92,102.52), LR=(211.21,180.75), LL=(133.06,179.44). For the outer profile they are UL=(123.61,90.86), UR=(223.31,92.48), LR=(221.40,191.11), LL=(122.62,189.75). A comparison against hand-selected source-visible cusp estimates is logged in the QA JSON. The true SVG `A` segments each retain separately measurable circular radius and endpoint coordinates.

The optional **analytical** SVG adds the complete eight fitted parent circles as **dotted black lines**, recognizing that those completed circles are **analytical extrapolations**, not fully printed. Grey dashed axial/diamond guides are separate; two **red dashed candidate connector segments** in this analytical-only view are deliberately labeled **uncertain**.

## 4. Important things *not yet measured*

The enclosing pointed arch, the partly cropped twin lower trefoil openings, local fork/stone-joint lines, and decorative spandrels in the clean drawing were **manual, visually guided approximations** in source-pixel coordinates. They do **not** have accepted fitted circular centers or independently demonstrated tangency. Their outermost portions (especially the bottom of each trefoil) are outside the supplied scan and are **not reconstructed beyond y=338**. The present black lines in those groups mean *visually observed source-outline candidates*, not verified exact geometry.

The source text mentions the 45-degree `ad` relation and lower-circle tangencies. The reconstruction **does not force** those conditions into the measured data without confirming which exact pixels represent `a`, `c`, `d`, `h`, `i`, `l`, `m`, `n`, `o`, `p`, `q` and `r` on the full plate. The source-drawn axes/letters must be independently retraced against a higher-resolution plate before rigorous compass reconstruction of the framing/lower arches.

## 5. Previous work recovered, not overwritten

- **Ungewitter 1193:** handoff's original crop + analytical SVG + four fitted circles and measurements, still a separate plate research case.
- **Ungewitter 1194–1198:** handoff has a **generated illustration** across 1193–1198; it is not a point-by-point source trace. The rounded 1193–1195 examples and pointed 1196–1198 remain distinct.
- **Trefoil/quatrefoil generated reference:** useful visual vocabulary, explicitly **not a measured reproduction**.
- **Sexfoil:** six measured circles and **ONE 30-degree rotation only**; the rotated crossing ring is a modern hypothesis. No repeated 15° or recursive rotations.
- **Paynter 1921:** *Practical Geometry for Builders and Architects*: Chapter VI, circles / intersections / centers; Chapter X, ornament, figs. 188–190; Chapter XIV, moulding intersections. His regulating construction-first methods inform interpretation, **not** attribution of the exact 1236 design to Paynter.
- **V08:** `gothic_plate_reader.py`, `gothic_geometry.py`, `gothic_patterns.py`, `gothic_stonework.py`. Isolated preview toolkit tested **11/11 passing**. Only plate reader + geometry fitter used in this case; no stonework or pattern propagation invoked.

## 6. Stage and preserved decisions

**Stage:** 2D Research — measured central quatrefoil with provisional surrounding linework. **No F5ZP architectural dimension is changed.** No prior accepted cathedral plans, 1:1 project baseline, generators, source drawings, vaults, ribs, piers, F5ZN-A data, or G40Q structural studies were altered. Source pixels cannot become authorized cathedral dimensions by implication. No 3D work was undertaken.

**Next bounded stage:** Find the complete original Plate CXX at higher resolution, check the lettered construction lines and lower windows, independently fit the enclosing two-centered pointed arch and lower trefoil curves, then compare the historically specified `45° / equal-distance / tangency / minimum-bar-thickness` relationships numerically. Reject or revise the manually drawn portions only in a new research variant, without changing the current dated result.
