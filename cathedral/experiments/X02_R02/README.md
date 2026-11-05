# X02 R02 - Research and Layout Proposal

Status: EXPERIMENTAL NORTHERN PLANNING PROPOSAL FOR ARCHITECTURAL REVIEW. No baseline promotion.

## Research recovered and checked
Two existing project reports (3 November 2026) were read in full from Research_03_Research_and_Tools.zip. Earlier experimental decisions for 3.5 m gallery, 22 x 26 m cloister, 9 x 12 m chapter hall plus 3 m end, northern refectory, eastern dormitory and separate night access were recovered from chat history. Original chat transcripts are not packaged, so these are recorded as retrieved decisions, not independently verified approval of saved geometry.

Targeted primary/institutional checking confirms Noyon circulation-conscious wall supports (Viollet-le-Duc III p.442), Durham's cloister as the hub of nave/chapter/refectory circulation, and Westminster's differentiated chapter/dormitory and secondary cloister access. The Salisbury indexed archive excerpt corroborates the previously researched two-bay vestibule sequence, but live page/PDF retrieval failed. No new historical dimensions are imposed on the project.

## Concrete revision
- Restore the external gallery planning band from 2.70 to 3.50 m; shift its widened center 0.40 m east. Portal center, 1.20 m throat, roots, north cloister, garden and range footprints remain fixed.
- Define a 9.00 x 3.50 m chapter vestibule within the unchanged east range, in two 4.50 m planning bays. These bay dimensions are a new design proposal, not a copied Salisbury measurement.
- Define a 9.00 x 6.60 m night-lobby functional zone; retain R01's night route and hypothetical stair box. No actual stair is designed.
- Add an explicit refectory-route reservation through the existing north/east walks. Public and scholarly access remain separate functional requirements pending their actual site source.

## Numerical comparison
New connector area 17.95125 m2 vs R01 14.56125 m2. Modeled root gap 0.1956 m; garden margin 0.3500 m. No root, garden or conditional chapel-test overlap. The conditional chapel rectangle still does not establish real chapel clearance. Vestibule area 31.50 m2, contained within the east range. Route widths are reservation bands, not verified finished clearances after stonework.

48 preservation / 2D geometry checks pass, 0 fail. No architectural acceptance or structural validation claimed. Screen uses the same 12 transformed X01 roots, not the full 88 roots or missing 248-support F5ZL-C schedule.

## Protected and unresolved
F5ZK-C, F5ZN-A, the working inner/middle vault generator, Pass 6J, southern E5-C3-L1, R01 sources and all original research remain untouched. No Blender or generator operation. The recovered F5I legacy proposal is not a substitute for E5-C3-L1. North E5-R3/E5-S2 remains experimental; no final north-versus-south selection.

Hold physical cathedral cuts until actual CH-N5 exterior and jamb/respond/window geometry are recovered or explicitly redesigned. Original southern site placement, Great Library/public transept source, night stair/floor levels and roof interfaces remain unresolved. Further general historical research cannot recover this project's missing saved geometry.

## Deliverables
Four-page A3 PDF; physical 1:1 SVG (1 coordinate unit=1 metre); full geometry; dimensions/deltas; research evidence ledger; QA; sources; build script. PDF scales are presentation scales.

## Reproduce
Run python3 build_r02.py with shapely and reportlab installed. It reads only retained R01 JSON and research references, writes only outputs/ and this README, and never runs a cathedral generator. PDF visual QA is performed after rendering. SHA256SUMS.txt identifies packaged bytes.

## Next decision
Review the revised connector and chapter vestibule as the northern working planning arrangement. Cathedral masonry opening approval, northern site promotion and replacement of protected southern E5-C3-L1 remain separate protected decisions.
