# Saint-Leu-d'Esserent — Figure 80 — Tracery and Twin-Lancet Junction

**Status: EXPERIMENTAL RESEARCH, not architectural approval.**

## Historical evidence
- Original Fig. 80: paired lancets under a six-lobed oculus, pointed enclosing arch, surrounding masonry.
- Charles Herbert Moore, *Development and Character of Gothic Architecture*, Chapter V, Figure 139: **139a = St. Leu mullion section**, chamfered/beveled on exterior and interior; 139b = Reims; 139c = Amiens. This is evidence for a St. Leu *mullion type*, NOT calibrated proof that the precise Fig. 80 central mullion or arch section uses the same dimensions.
- Moore's architectural description supports a recessed pierced masonry plane relative to the wall-facing enclosing arch; numerical depth unresolved.
- Viollet-le-Duc's *Meneau* article documents comparable construction methods, including continuous profiles and glazing rebates, but is not a dimensioned St. Leu survey.

Sources:
- https://en.wikisource.org/wiki/Development_and_Character_of_Gothic_Architecture/Chapter_5
- https://commons.wikimedia.org/wiki/File:Fig_139_-Mullion_sections,_St._Leu_d%27Esserent,_Reims,_Amiens.png
- https://fr.wikisource.org/wiki/Dictionnaire_raisonn%C3%A9_de_l%E2%80%99architecture_fran%C3%A7aise_du_XIe_au_XVIe_si%C3%A8cle/Meneau

## Versioned experiment register

| Version | Main work | Reported validation | Status |
|---|---|---|---|
| R01 | First clean window/tracery tracing and source overlay | source-aligned visual first pass | Experimental |
| R02 | Surrounding wall, courses, joints, impost and jamb stonework | visual overlay; masonry joints simplified | Experimental |
| R03 | Three architectural layers; two lancet voids + six surrounding foil apertures + central aperture = nine candidate voids | 6/6 automated checks reported | Experimental |
| R04 | Resolve false crossing of dual outer lancet contours; separate inward-turning faces and central stone | ~5 px provisional minimum separation; 10/10 reported | Experimental |
| R05 | V08 0.8.1 two-rail sweeps, plain/bevel alternatives, three independent closed solids | 10/10 tests reported, 3 watertight solids per GLB | Experimental |
| R06 | Repeated-roll and glass-rebate comparative sweeps; primary evidence recovery of Moore 139a chamfered mullion | 13/13 tests reported; profiles hypothetical | Experimental |
| R07 | Moore 139a source outline and 3D profile follow-up; ~1 px central top interface correction described in conversation | 8 geometry/provenance checks reported; **complete R07 package not independently recovered here** | Experimental / requires file recovery |

**Do not promote a historical measurement from a reported check without recovering its original QA report.**

## R03 three-layer architectural model
1. Outer enclosure: wall and pointed arch over the complete window.
2. Solid facing masonry: central mullion, spandrels, enclosing circular stone ring and stone webs.
3. Voids: two lancets, six foil apertures and one central circular aperture. The separation between foil apertures and center was an uncalibrated **2.7 image-pixel** experiment, not historic stone thickness.

## R04–R07 connection research
- A false outer-arch crossing in earlier tracings was replaced with independent inward-turning faces.
- R04/R05 minimum center clearance: **5 image pixels**, experimental.
- R05 reference coordinates: source raster 545 × 825; X = image column, Z = 780 − image row, Y = front-to-back trial depth of 12 image-pixel-equivalent units. No real-world calibration.
- R05 front rails preserved across plain and beveled section trials; central strip top slopes to different return endpoint elevations.
- R06 optional rebate belongs on opening-facing edges, **not** stone-to-stone central bearing interfaces.
- R06 rolled profiles are comparative examples only; **Moore 139a chamfered St. Leu section supersedes them as the best directly attributed mullion reference**, but is not automatically an arch profile.
- R07 reportedly corrected a one-pixel provisional top mismatch. Preserve the previous variants; recover the actual R07 script, GLBs and QA before accepting precise coordinates.

## Unresolved
True measured opening width, masonry thickness, section depth, actual Fig.80 profile dimensions, historical arc-center/radius construction, glazing rebates, stone bonding and structural load path. A drawing in source pixels is NOT a 1:1 cathedral-scale model.

## Source artifacts and reproducibility
Available current conversation working files include `St_Leu_Fig80_Trace_R02_FOR_REVIEW`, `F5ZP_StLeu_Fig80_ThreeLayer_R03_EXPERIMENTAL`, `F5ZP_StLeu_Fig80_DualArch_Returns_R04_EXPERIMENTAL`, `F5ZP_StLeu_Fig80_Section_Junction_R05_EXPERIMENTAL`, and `F5ZP_StLeu_Fig80_Profile_Relationships_R06_EXPERIMENTAL`. Their scripts, SVGs, GLBs and QA reports should be uploaded as immutable versioned assets after verifying the actual file bytes; this text-only register is not a substitute for those binaries.

## Next implementation gate
Recover full R07 package and its hashes; verify Moore 139a traced outline against the original scan; use the section as a parameterized, **uncalibrated** central-mullion candidate; separately test any arch-section reuse as a hypothesis; compare against fixed R04 front rails and source overlay. Export named 3D components and measure geometric interface clearance before architectural review.
