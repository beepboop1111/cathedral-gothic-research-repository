# F5ZP R18 — Independent Groin / Constrained Web Generator

**Status:** EXPERIMENTAL V01. Synthetically geometry-validated; NOT approved cathedral architecture or a historically/structurally verified Gothic vault.

## Recovery and protected geometry
- Source checkpoint: R17 V02 F5ZP_R17_FAST_VAULT_WORKSPACE_REVIEW_READY_V02_EXPERIMENTAL.blend.
- R17 two-centred pointed boundary arches and R16 strict crown/lock guard are imported READ ONLY.
- F5ZK-C 1:1 plan, F5ZN-A, working AMB-I/M V13 generator, Pass 6J and existing architecture remain untouched.
- Missing F5ZL-C support schedule remains UNRESOLVED.
- Colored rib/arch paths in R18 are **thin display guides**, NOT masonry sections.

## New geometry
R17 generated radial groins from already-interpolated web boundaries. R18 generates **independent, circular, monotonic radial groin centerlines** FIRST, then fits each sector's web to both groins, the original true-pointed boundary arch and an independently controlled common crown. No web movement on these skeleton edges is permitted.

For radial run L and rise h: set circle center a=max(L,(L²+h²)/(2L)), b=(L²+h²-2aL)/(2h), radius R=sqrt(a²+b²), and z(s)=spring+b+sqrt(R²-(Ls-a)²). For h>=L this matches the earlier R07 circular model; for h<L it avoids a premature high point before the crown. Interior webs use the two independent groin heights plus bounded pointed-arch and curvature controls.

R18 runs with 3–12 synthetic sectors, FAST (32) or FINAL (128), variable rise/span, independent crown, plan irregularity and web curvature. A separate Blender N-panel named R18 Vault provides one-click regeneration, construction-guide toggle, versioned checkpoint and 1:1 GLB export.

## MR COMPUTER outputs
- **Open:** blender/F5ZP_R18_SKELETON_FIRST_LIVE_V01_EXPERIMENTAL.blend (4-sector FINAL).
- **Additional checkpoint:** blender/R18_SKELETON_FIRST_CHECKPOINT_001_EXPERIMENTAL.blend (irregular 6-sector FINAL).
- Generator: r18_core.py
- Blender interface: addon/r18_live.py
- Test suite: scripts/run_R18_validation.py
- Bootstrap: scripts/bootstrap_R18_blender.py (creates V01, refuses overwrite)
- Fresh-process UI tests: tests/test_R18_live.py
- 1:1 GLBs: outputs/R18_BUILD_001_WEB_ONLY_1TO1.glb (65,536 triangles) and outputs/R18_BUILD_004_WEB_ONLY_1TO1.glb (98,304).
- Four actual Blender camera renders: review/R18_axon.png, R18_plan.png, R18_underside.png, R18_section.png.
- Numerical and source-hash evidence: qa/R18_REGRESSION.json, qa/R18_LIVE_BLENDER_BOOTSTRAP_QA.json, qa/R18_BLENDER_RELOAD_REGRESSION_QA.json.

Both GLBs are OPEN intrados, intentionally non-watertight. No unapproved cap, stone thickness, historical profile or support geometry was fabricated.

## Reproduction
MR COMPUTER: open the V01 Blender scene, press N > R18 Vault, change synthetic parameters, then REGENERATE R18; save into a new experimental checkpoint or export web-only 1:1 GLB. The R18 add-on is already installed and enabled. Never run the original V01 bootstrap again against its existing output without first creating a NEW experiment folder.

To run a fresh regression in a copied experiment folder, invoke Python 3 on scripts/run_R18_validation.py. To test Blender, launch with --python tests/test_R18_live.py against the V01 file. Both QA scripts use exclusive output creation to avoid erasing earlier records.

## Validation status
- **Technical:** PASS Blender 5.0.1 generation, plugin reload, GLB export/import, versioned save, source hashes.
- **Geometric:** PASS on synthetic layouts (8 positive builds, 2 invalid-build rejections, 1 level-crown warning; continuous ribs/seams/arch, no overshoot or sag below interpolated groin baseline).
- **Architectural:** PENDING real approved plan and bearings.
- **Historical:** NOT ESTABLISHED.
- **Structural:** NOT ESTABLISHED.
- **Still missing:** actual physical rib mouldings, responding springer joins, real roof cover and F5ZL-C evidence. R18 is NOT a replacement for the working F5ZN-A ambulatory generator.
