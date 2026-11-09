# V19 — Gothic arch, rib skeleton and complete meridian-controlled vault

**Status: EXPERIMENTAL / NOT APPROVED ARCHITECTURE**

Isolated handoff within R33 research; no existing masonry junction files modified.

- `scripts/v19_rib_arch_generator.py` — two-centred pointed Gothic boundary arches, independent radial groins and geometry guards.
- `scripts/v19_full_vault_generator.py` — complete open vault web constrained to the original skeleton, including the recovered four-segment R12B Sector 02 **Type A cubic Hermite meridian**.
- `HANDOFF.md` — detailed mathematics, settings, validation and unresolved limitations.
- `validation/` — synthetic geometry test reports and original V19 comparison.
- `F5ZP_V19_TWO_GENERATOR_FULL_HANDOFF_R01_EXPERIMENTAL.zip` — original verified 12-file archival handoff, including two editable Blender scenes, one GLB, PNG and source scripts.

**Reproduce (Blender 5.0.1 actually tested; 5.1+ not verified):**

```bash
blender -b --factory-startup --python scripts/v19_rib_arch_generator.py -- --out ./skeleton_new
blender -b --factory-startup --python scripts/v19_full_vault_generator.py -- --out ./vault_new
```

The new open intrados has 65,536 triangles. Maximum measured vertex difference against the original V19 GLB is approximately 0.0000863 native units. No physical rib cross sections or roof-cover/structural validations are claimed.

**Protected:** F5ZK-C, F5ZN-A, V13 inner/middle vaults, Pass 6J, original R12B/R14 accepted drawings. F5ZL-C support schedule and roof clearance remain unresolved.

Uploaded as a self-contained experimental reference; does not change R33 stone-body research or promote V19 to approved cathedral geometry.
