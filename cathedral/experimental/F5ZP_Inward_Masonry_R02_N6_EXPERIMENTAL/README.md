# N6 inward masonry — R02 local clearance study

6 November 2026. Experimental, plan only. Review checkpoint; no whole-plan propagation.

## User decision

“Keeping everything outside yes and proceed.” All masonry, including shafts and bases, is to remain outside each reserved vault space. The user also requested more pauses/questions in this chat and economical source reads. This package stops after one comparison, before profile fitting or layout propagation.

## Retained reference and experimental interpretation

The recovered F5ZE grid gives N6 X−21797→−18197 (3600), and outer north aisle A3 between Y5429 and Y6965 (1536). The read-only `ug_vault_generator_F5ZE.py` catalogue, lines 484–492, divides ordinary lower nave bays into two longitudinal halves; N6 therefore provides two 1800×1536 cells. That catalogue is secondary dimensional evidence, not an approved replacement generator. Its recorded source SHA-256 is `c55628d9ddfe45af66b5349eaa3edad8008a9bcae0cb78873e61a49d9e306835`, path `/home/christopher/Downloads/F5ZP_3D_PIPELINE_R01_EXPERIMENTAL/2/ug_vault_generator_F5ZE.py`.

The original source does not prove these numbers are finished floor-clearance dimensions. **By the current user decision**, this experiment treats those full rectangles as clear reservations. Their lengths, widths, areas and shape remain identical; the experiment translates their locations to insert new masonry space. No actual saved vault object, arch endpoint, generator or protected coordinate array is changed.

Master Reference was successfully retrieved earlier in this same inward-development exchange: branch `cathedral/governance-r01`, file `cathedral/governance/CATHEDRAL_MASTER_REFERENCE.md`, blob `1d7e358ff7562fcc64088854baa2abd3d31a729e`. It remains provisional. Prior R01 local source snapshots and the immutable R01 checkpoint commit `012fb76271d5bd3cbcbc91053fae10cb35c21fac` are reused without a new archive scan.

## Three space allowances

| Complete inner support/base envelope p | Cell pitch 1800+p | Two-cell module 3600+2p | Local length growth | A2 edge to outer wall |
|---:|---:|---:|---:|---:|
| 320 | 2120 | 4240 | 640 / 17.78% | 2426 |
| 480 | 2280 | 4560 | 960 / 26.67% | 2586 |
| 640 | 2440 | 4880 | 1280 / 35.56% | 2746 |

All values are native project units, numerical 1:1. Physical metre conversion remains unresolved.

Each p is a **trial square bounding reservation for the complete inner pier/base**, not a proposed circular pier diameter, recovered profile, final base outline or assessed structural size. Rectangular/polygonal and directional envelopes may later be appropriate. No variant is selected or approved. The actual asymmetric Pass 6J pier must not be regularized or transplanted into this straight aisle by assumption.

The sample holds the neighboring A2 clear-space edge at local Y0. A complete shared inner-arcade reservation p is inserted outside that edge; A3 clear space begins at Yp and keeps its full 1536 width. Outside A3, a **provisional 250 respond/base projection allowance** precedes a **proposed 320 wall**. Both are explicit study parameters; 250 is not a measured respond or base depth. The external wall/shaft/base fit remains unverified.

Thus the transverse allocation is `p + 1536 + 250 + 320`. Compared with R01's wall immediately outside the original A3 edge, the local outer wall moves outward a further `p+250`: 570, 730 or 890. This does not establish the total new cathedral width: additional inward rows are not yet spaced.

Longitudinal module endpoints are end-support centres. Each module counts half of each end support plus the one full intermediate support, so shared supports are counted once. Full end footprints are shown for context; their complete review extent is one p greater than the tabulated repeating module. The two clear cells fit between the facing support-envelope edges.

The spaces between individual piers remain open arcades at floor level. Dashed bands and rectangles reserve future masonry/arch space; they are not continuous solid floor walls. The transverse doubleaux, profile-to-support contact, masonry bonding and the connections between the newly separated cell boundaries have not been generated or validated.

## Preservation, QA and limits

The 30 recorded checks pass: two exact 1800×1536 clear cells per variant; zero positive-area intrusion from the rectangular support, respond and wall envelopes; valid polygons; shared-gap and support counting; wall/response separation; source hash preservation; saved JSON round trip; SVG parsing. The PNG comparison was visually inspected. These are technical and limited geometric checks only, not historical, architectural or structural validation.

F5ZK-C/F5ZN-A, the 14 saved chevet vaults, seven shared profiles, working ambulatory generator, V13 originals and Pass 6J are preserved. Discarded outer-ring geometry is not reintroduced. F5ZL-C's missing support schedule remains unresolved. No whole nave, choir, crossing or curved chevet has been re-spaced. R01's small outer-wall growth estimate must not be presented as the eventual total after adding all internal reservations.

## Reproduce and review

Run `python build_study.py` with matplotlib and shapely. Source dimensions are bundled in `inputs/`; no remote machine or new file search is required to reproduce the study. Outputs include the matched PNG, three native-coordinate SVGs (one SVG user unit per project unit), exact rectangular geometry JSON, measurements CSV/JSON and QA.

Next: review the spacing shown here, then fit actual saved arch/respond profiles and complete base outlines to the trial reservations before selecting a support size. Pause for user review before propagating any module spacing or changing protected architectural coordinates. The chosen clearance rule is accepted; none of the three numeric support allowances is yet accepted.

The full delivery includes a PNG. The Git checkpoint stores the reproducible text source, native SVGs and numerical outputs; regenerate its PNG with the script.
