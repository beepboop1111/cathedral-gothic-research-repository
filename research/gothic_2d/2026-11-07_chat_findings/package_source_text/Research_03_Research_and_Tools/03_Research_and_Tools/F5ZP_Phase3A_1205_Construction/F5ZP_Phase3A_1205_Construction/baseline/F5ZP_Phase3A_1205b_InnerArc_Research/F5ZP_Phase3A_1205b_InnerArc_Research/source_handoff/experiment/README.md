# F5ZP Phase 3A — Ungewitter II, Plate CXVIII, motif 1205b

Original source: `lehrbuchdergotis02unge.pdf`, PDF page **281** (1-based), original plate **CXVIII**, motif **1205b**.

## Completed
- Original source page rendered and retained unchanged.
- One motif cropped without rescaling.
- User-provided `pages_grayscale.py` and `pages_bw.py` executed without editing their source.
- Transparent linework and fixed-threshold alternatives saved.
- V08 `circle_fit` evaluated on pixel samples from the outer circumference.
- Overlay of the fitted circle with the engraving saved.

## Quantitative result
- Approximate fitted outer center: (109.22, 111.24) pixels *within crop*.
- Approximate radius: 93.52 pixels at 144 DPI render.
- Sample count: 360; retained for fit: 339.
- Inlier RMS radial residual: **0.69 pixels**.

## Limitations
This only assesses the outer circular boundary. The intersecting inner arcs and cusps **have not** been reconstructed, isolated, or measured. Inliers were sampled around an approximate, visually specified circle and therefore the residual is a *conditional local fit*, not independent recognition accuracy. Thresholded black lines are not masonry masks. No scale reference has been supplied. This is not validated Gothic tracery, and no STL or architectural geometry is claimed.

## Next recommended operation
Individually segment the nested quatrefoil curves and construction lines; identify circle centers/arcs separately; classify masonry and open regions; then assess overlay accuracy by figure.
