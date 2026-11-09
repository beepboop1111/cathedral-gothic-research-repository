# Tracery research: Freeman, Sharpe, Billings and the generator (2026-11-07)

Full write-up: Claude doc "Window tracery: in-depth research and generator plan" (https://claude.ai/artifact/3mhD9bxBm3G2ECNvVaZZGi).

## Sources read
- Freeman, *Essay on the Origin and Development of Window Tracery in England* (1851): families and sub-families, skeleton-and-pattern combination, two cusp constructions, Perpendicular rules.
- Sharpe, *Treatise on the Rise and Progress of Decorated Window Tracery* (1849): origin of tracery, definition (head pierced to the glass), frame vs panel, order limits, soffit vs chamfer cusps, Curvilinear classes I-III.
- Sharpe, *Decorated Windows* (1849): about 60 engraved elevations at 4 ft to 1 in with printed dimensions (fixtures for layout and proportion).
- Billings, *The Power of Form Applied to Geometric Tracery* (1851): 100 designs, each with a numbered construction diagram; the diagram line is the moulding centreline (same idea as U06).
- Overviews added later the same day: Looking at Buildings, Wikipedia "Tracery", Canterbury Historical and Archaeological Society tracery index. They add Kentish (split cusp), drop, blind and loop tracery; dagger, mouchette and soufflet as the Flamboyant units; Reims bar tracery from about 1215; bar tracery parts cut to standard templates.

## Key rules for the generator
- Non-coinciding arch (separate window arch, figure in the head) vs coinciding (Y / intersecting). A geometrical figure never rests on a single arch.
- Intersecting bars share one radius, taken from the window arch.
- Skeleton of one family filled with patterns of another; each moulding order steps back from the one before.
- Perpendicular: bars from mullions and light crowns = Supermullioned; crowns only = Alternate; mullions only = Panelled.
- Window arch is the only structural arch; tracery is a panel set after it, on separate stones. Order limits: arch 2, tracery 3, foliation 2.
- Cusps: circles inside a figure (truncated open soffit cusp near the glass, often inserted in a groove) vs inscribed foil (pointed cusp, chamfer cusp just below the bar fillet). Kentish split cusps form V-shaped openings.
- Flowing (Freeman ch. II): spaces bounded by lines continued from the mullions. Reticulated = net of ogee vesicas, "to the Flowing style what the circle is to the Geometrical"; short units from one centre, long from two; an infinite expanse cut by the arch, so imperfect units at the sides. Ogee tracery = Arch tracery with ogees (intersecting or not; needs three lights or more). Flowing Wheel = divergent, horizontal convergent, reversed convergent.

## Generator roadmap (phases)
1. Compass-construction kernel with numbered steps. 2. Skeleton-and-pattern grammar with Freeman's rules as checks; blind and drop tracery as frame variants. 3. Foliation (both cusp constructions, depth planes, inserted cusps, Kentish split cusps). 4. Ogee and Flowing families, including daggers, mouchettes, soufflets and loop tracery. 5. Perpendicular. 6. Depth and section (three order hierarchies, rear arch and rear vault, glass position). 7. Masonry and structure (back joints, stone limits, template count, thrust and wind checks). 8. General survey fitting.

## Status at time of writing
U01-U06 cover 8 of 32 capabilities fully and 6 partly; 18 are missing, including everything after Early Geometrical. Reims: one two-light-and-circle rule fits all 51 survey traces (50 within 26 mm rms); oculus is a reused module per series.

## Progress later on 2026-11-07 (U07, local only, not pushed)
Folder `cathedral/research/tracery/universal-generator-U07-construction-kernel-2026-11-07/`; its README has the run steps.
- Phase 1: compass kernel with numbered steps and residual checks (25 programs, worst 9e-13; Reims presets match U06 to 5e-13 mm).
- Phase 2: layout grammar with Freeman's rules as checks (lights, sub-arches, complementary light, circles carried by two supports, three-circle head, spherical triangle, intersecting bars).
- Phase 3: foliation (circles-in-circle and inscribed foil, trefoil heads, free foils, Kentish cusps).
- Handoff: U07 layouts go through U01-U03 as moulded, jointed stone and are checked in Blender. Seven Geometrical windows pass every check; longest stone 2.39 m. U03 gained three opt-in options (split_long, explicit arc angles, face_to_face); regression bar_2light_sexfoil identical.
- Phase 4, part 1: ogee arch kernel and Reticulated net (every bar one radius r = H / (4 sin theta), theta = 2 atan(p/H); H = sqrt(3) p gives the single-centre unit). 2-, 3- and 5-light windows pass every U01-U03 check; whole units 1, 3 and 9; longest stone 1.55 m.
- Still open: phase 4 part 2 (intersecting ogees, Flowing Wheel, daggers, mouchettes, soufflets, loop tracery, cusped units), phases 5-8, and structural checks (none run yet).
