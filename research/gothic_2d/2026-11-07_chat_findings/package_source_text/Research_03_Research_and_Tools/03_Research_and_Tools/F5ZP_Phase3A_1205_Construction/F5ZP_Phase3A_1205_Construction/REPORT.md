# F5ZP Phase 3A — Figure 1205 compass construction study

2026-11-03. Experimental historical research; no cathedral changes. Figure 1205 is the printed identifier. “1205b” remains the inherited identifier of the preserved measured package, not a verified plate suffix.

## Source authority

Ungewitter–Mohrmann, Lehrbuch der gotischen Konstruktionen, Volume II (1892), printed page 510 (PDF page 280), section “Das Austragen der Vielpasse”; diagram Plate CXVIII (PDF page 281). The rendered text page and extracted OCR are retained in evidence/. OCR is a working transcription; relevant wording was checked visually against the print.

Direct passage, German:

“Ganz in derselben Weise lassen sich 4, 5, 6, u. s. w. Nasen erzielen. Fig. 1205 zeigt z. B. das Einsetzen von vier Nasen oder die Bildung des Vier-Passes, wobei je nach der Gestaltung, welche die Nasen erhalten sollen, die Wahl der Mittelpunkte zwischen a und b geschehen kann.”

Translation:

“In precisely the same way, four, five, six, and so on cusps can be obtained. Figure 1205 shows, for example, the insertion of four cusps, or the formation of the quatrefoil; depending on the shape the cusps are to receive, the centers may be chosen between a and b.”

The preceding instructions place the arc centers on the diameters obtained by dividing the enclosing circle. Their distance from its center depends on the desired cusp termination. For pointed cusps the author says that center choice controls sharpness and recommends placing centers nearer a so that the points do not become too long. The surrounding discussion also requires the lobe arcs to touch the enclosing circle. Nasen are inward-projecting cusps; Nasenbögen are their bounding arcs.

The source specifies a construction family, not one compulsory numerical radius ratio. It names a and b as limits of center choice. It does not explicitly define c in this paragraph. The method below is an exact geometric realization of these instructions; its fitted parameter is not an author-prescribed proportion.

## Compass-and-straightedge reconstruction

1. Draw the enclosing circle with center O and radius R. Draw a diameter and construct its perpendicular through O, giving north, east, south and west contact points.
2. On the west radius choose a center P between the marked positions a and b. Let OP=d. This is a selectable design parameter, not a newly locked dimension.
3. Set the compass to PW, the distance from P to the west contact point W. Then r=PW=R−d. Draw the west lobe circle centered at P. It touches the enclosing circle internally at W.
4. Transfer length d from O onto the other three cardinal radii. Draw equal circles of radius r at these three centers. Equal compass openings and center distances establish fourfold symmetry for each individual alternative.
5. If adjacent circles intersect, use their outward intersection on each diagonal as the pointed cusp. Of the two intersections, the outward one lies closer to the enclosing circumference. Keep the lobe arc portions running through the cardinal contacts. Retain all circles as construction guides until the chosen boundary is established.
6. If adjacent circles do not intersect, retain the separation. The figure cannot be converted into a closed four-cusped opening using those circles alone. Any connector, retained outer-circle portion, or blunt termination would need its own explicit design construction.

Analytic check: the four centers are O+(±d,0), O+(0,±d), with r=R−d. Adjacent-center distance is √2 d. The circles intersect when √2 d < 2r, touch when equal, and separate when greater.

The exact transition is d*=(2−√2)R and r*=(√2−1)R. It is constructible with straightedge and compass: construct a square of side R, whose diagonal is √2 R; subtract that length from 2R to obtain d*, and subtract d* from R for r*. This critical case gives touching circles, not an ordinary pointed cusp.

## Comparison against preserved measured SVG

The outer reference is unchanged: O=(109.21742236738913,111.23955699522183) px and R=93.51694870364518 px. Pixel-center coordinates, axes and exact measured arcs are inherited without modification. No physical units or architectural scale are inferred.

Fit one d to N/E_upper/W_upper and a separate d to S/E_lower/W_lower using the same 377 retained stroke samples as the measured reconstruction. For each alternative, the fitted d fixes all four centers and radii exactly. Only three portions of each alternative are sampled in the engraving; the other portions of the symmetric construction are extrapolations, shown as full construction circles rather than recovered ink.

| Exact construction alternative | d (px) | r (px) | d/R | RMS to corresponding selected ink (px) |
|---|---:|---:|---:|---:|
| Upper stroke regime | 50.662147 | 42.854802 | 0.541743 | 0.661 |
| Lower stroke regime | 57.041891 | 36.475058 | 0.609963 | 0.779 |
| Critical touching-circle candidate | 54.780960 | 38.735988 | 0.585786 | Not fitted |

On the identical retained sample set, independent six-circle fits have RMS **0.151 px**; the two-parameter exact construction has RMS **0.729 px**; a single-parameter construction forced across all six pieces has RMS **2.121 px**. These are descriptive, conditional fits with 18, 2 and 1 circle parameters respectively, keeping the outer reference fixed. They are not an independent historical attribution test. Earlier 0.205 px six-arc RMS used all raw samples, including the rejected point, so it must not be directly compared with the retained-sample figures here.

The upper alternative's adjacent circles intersect. Its NE outward intersection is (151.1799043160,69.2770750466) px, compared with the independently measured NE cusp (151.0280643645,70.4335359962) px: approximately 1.17 px apart. The lower alternative's circles remain separated by 7.719 px; independent lower fits give gaps of 8.617 and 9.219 px. The ideal family therefore reproduces the two qualitative regimes without exactly reproducing every engraved stroke.

Exact internal tangency is satisfied algebraically (d+r=R). Intersection circle-equation checks are below 3e-14 px. These are mathematical consistency checks, not scan-accuracy claims. All parameters and numerical comparisons are in results/construction_measurements.json. The three SVGs overlay exact circles with the preserved measured arc geometry.

## What a, b and c support

| Relationship | Evidence and status |
|---|---|
| Centers may move between a and b to change cusp shape | Explicit source text; established |
| Moving toward a shortens the pointed cusp | Explicit preceding text; established |
| Equal circles on cardinal radii, internally tangent to the outer circle | Geometric reconstruction of the division/tangency instructions; supported by the approximately axial centers and matched overlays |
| The upper and lower portions represent differing center choices | Supported interpretation: source permits alternatives and one parameter fits much worse than two; not explicitly a textual assignment of the top and bottom of 1205 |
| Exact fourfold symmetry of each chosen alternative | Construction hypothesis supported approximately by the drawing; not imposed on the preserved measurements |
| Every measured circle is exactly tangent to the inherited reference | Not supported at subpixel precision; previous independent tangency discrepancies are 0.322–1.221 px |
| c marks the touching-circle transition | Plausible geometric hypothesis only; text does not identify c |
| a or b has a particular exact fraction of R | Unresolved; do not invent fixed proportions |
| Lower ends are missing cusps to be automatically filled | Unsupported; source and measurements must retain their alternatives and gaps |

The visually estimated west-axis marks are a≈44, c≈53, b≈64 px (rough uncertainty ±1.5 px; labels and ink thickness limit location). These are manual estimates, not independently detected points. The exact transition predicts a west center at x=54.436 px, about 1.44 px from the estimated c. It lies between a and b. This proximity motivates the c hypothesis but is insufficient to establish its exact meaning. Do not promote c to a historical ratio or a locked dimension.

## Preservation and next bounded step

The original measured ZIP is included byte-for-byte under baseline/. Its original drawings, SVG, centers, source tools and checkpoint are unchanged. This is a new research companion. No cathedral geometry, locked dimensions, generator or source PDF was modified.

The intended procedure is recoverable as a parameterized compass construction, while a unique intended radius is not specified in the passage. The next bounded step is to trace the fine guide curves and mark stems independently, testing whether c geometrically encodes the transition and how a/b were set out. Preserve both exact alternatives and the measured baseline. Any later finished design must explicitly select one alternative and its boundary treatment.

Reproduce numerical outputs and visual comparisons with python scripts/compare.py (numpy, scipy, Pillow, matplotlib). The matching baseline ZIP is bundled. SVG units remain reference image pixels. All exported artifacts are EXPERIMENTAL; none is user-approved cathedral geometry.
