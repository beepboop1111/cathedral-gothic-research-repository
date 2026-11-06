# Cathedral F5ZP — R16 Strict Vault Crown & Locked-Geometry Guard

**Status: isolated experimental generator adapter. NOT a replacement for the
approved cathedral generators, original vaults, or architectural baseline.**

## The new mandatory crown rule

**For every Gothic vault, every time it is generated:**

    vault_crown_Z >= MAX(actual boundary arch apex elevations)

- If crown is **BELOW** any pointed boundary-arch apex: **HARD STOP**.
  The source mesh is not generated or exported.
- If crown is **LEVEL** with the highest apex: **PASS WITH WARNING**
  `LEVEL_CROWN_REDUCES_DOME_EFFECT`. This is allowed for existing
  locked geometry but has reduced crown-to-apex rise.
- If crown is **HIGHER**: passes the crown-height requirement.
  For NEW *unlocked* concepts, the default proposed rise is
  `max(25 native units, 0.08*(highest_apex_Z - spring_Z))`.
  This 8% is a **design preference for new trials**, not an approved
  cathedral dimension and **never** an automatic change to locked geometry.
- Compare to the **highest apex of ALL measured boundary arches**.
  Never assume a regular 4-sector vault: 3, 4, 5, 6, 8 or other
  irregular boundary-arch counts are supported.
- A 1e-8-native-unit tolerance is used only for floating-point
  rounding in analytic arch samples (e.g. 4296.000000000002).
  It is NOT permission to design a lower crown.

**Important:** merely meeting the crown/apex relationship does not
prove a smooth dome; web meridians, groins, springing bearings and
roof clearance require independent tests. The R14 apse has a boss at
Z4296 and an inner web peak around Z4370.34: web peak and boss
height are NOT interchangeable.

## Warnings and locked geometry — always visible

Every PASS report includes `LOCKED_GEOMETRY_WARNING_ALWAYS`,
with these protected families:
- Approved cathedral F5ZK-C floor plan and 1:1 scale.
- F5ZN-A dimension set and **working** inner/middle ambulatory generator.
- Original accepted pointed arches, groins/ogives, responds and bosses.
- Pass 6J source geometry and existing receivers.
- Missing F5ZL-C support schedule — **UNRESOLVED**.

Warnings also report:
- `CROWN_LOCKED_DO_NOT_RAISE`
- `LOCK_REFERENCE_NOT_FULLY_VERIFIED` if authoritative hashes absent.
- `PREFER_HIGHER_CROWN` for new unlocked lower-than-preferred design.
- `LEVEL_CROWN_REDUCES_DOME_EFFECT` when crown and apex are level.
- `CAP_INTERSECTION_OR_INSUFFICIENT_COVER` and other cap issues.

The CLI also records the locked-geometry warning in any **failed**
run's report. The in-memory generator adapter checks reference source
hashes, archived boundary points and any supplied locked baselines
**before generation and again before export**. Even in-place mutation
of an input point array is rejected before any files can be written.

The rule never unlocks or changes existing protected geometry. When a
source baseline is not independently verified, its report explicitly
states so rather than inventing approval.

## Masonry clearance policy

The crown/apex guard is separate from cap and stone thickness:
- Open experimental intrados may carry cap/intersection WARNINGS.
- Export of CLOSED masonry is prohibited unless a positive,
  explicitly reviewed minimum cover is configured and both cap and
  generated web meet the requirement.
- No structural carrying capacity, bonding, historical authenticity
  or roof-bearing certification is claimed by these tests.
- Existing R14 Type A webs still intersect the provisional Z4341 cap
  by ~29.34 native units. R16 does NOT solve that issue by changing
  the approved shape or cap.
- The strict rule applies to the independent boss elevation even
  though the **legacy rectangular source generator couples the
  boundary arch apex and crown parameter**. Raising the legacy
  Bay.crown would also move the original arches: DO NOT do this.
  For a genuinely raised future design, derive an independent boss
  and web/groin geometry from the original protected arch data.

## Implemented scripts and entry points

- `src/strict_crown_guard.py` — architecture-agnostic crown/lock
  policy, apex extraction, positive-rise preference, warning codes.
- `src/guarded_vault_adapter.py` — mandatory PREBUILD/POSTBUILD guard
  around new in-memory procedural builders; source hashes and mesh
  checks before 1:16 STL / full-scale GLB exports.
- `src/preflight_new_vault.py` — CLI accepts measured XYZ arch CSVs
  and explicit source hashes. Runs WITHOUT generating masonry.
- `tests/run_R16_crown_gate_tests.py` — 25 regression tests.
- `tests/run_R16_new_vault_family_mesh_smoke.py` — procedural
  synthetic 3-, 5-, and 8-sector test vaults generated and exported
  through the guarded builder. These are **not cathedral designs**.
- `reference/` — byte-identical archived source generator/kernel
  and original R06/R14 config copies for provenance.

### Use with an actual new Gothic vault type

1. Recover the true full pointed boundary arch profiles and structural
   skeleton first; use >=257 measured XYZ samples per arch or analytic
   extrema.
2. Copy a supplied `configs/R16_..._EXISTING_LOCKED_PREFLIGHT.json`,
   substitute the new **measured** arch CSV paths, true crown elevation,
   spring elevation, roof/cap data and source-hash ledger. If the new
   vault is unlocked and `crown_Z` is omitted, the preflight CLI
   proposes a higher crown. Do not apply this to a locked design.
3. Run preflight:

    python3 src/preflight_new_vault.py --config my_vault.json --output my_QA.json

4. The build script must call `guarded_build(...)` around an
   IN-MEMORY mesh generator and supply actual final arch and crown
   measurements. It exports only AFTER both gate checks succeed.
5. If the crown is level, review the explicit warning before
   proceeding. If below, hard-stop and resolve the design **without
   modifying locked geometry**. Do not mark an experimental option
   approved because this numerical gate passes.

## QA and evidence

`qa/R16_STRICT_CROWN_GUARD_REGRESSION_QA.json`: **25/25 PASS**,
including below-apex rejection, level-crown warnings, higher preference,
all-arch maximum, locked source mutation rejection, roof-cap checks
and prior saved V4 and polygonal R07 geometry inputs.

`qa/R16_GUARDED_NEW_FAMILY_MESH_TEST_QA.json`: three actual synthetic
procedural vault meshes (3/5/8 sectors) generated through strict
prebuild and postbuild checks. Each supplied original pointed
boundary-arch profiles. All STL files are at 1:16 input scale and
all GLBs are in native full 1:1 coordinate units.

`qa/R16_STANDALONE_NEW_FAMILY_REPLAY_QA.json`: 3 generated STLs +
3 generated GLBs replicated **byte-for-byte** with exact SHA-256
from an isolated copy containing only R16 source dependencies.

`qa/R16_FOUR_SECTOR_V4_CLI_PREFLIGHT_QA.json` and
`qa/R16_SIX_SECTOR_R07_CLI_PREFLIGHT_QA.json`: actual original
saved crown/arch input checks. Both correctly warn **LEVEL** rather
than move Z4296. The six-sector source additionally flags the
provisional upper-cap conflict.

`qa/R16_NEGATIVE_CROWN_REJECTION_WITH_LOCK_WARNINGS_QA.json`:
explicit below-apex reject; no geometry written.

The archived originals are not overwritten, nor is the working
ambulatory vault generator or F5ZK-C floor plan modified.

## Architectural checkpoint status

**TECHNICAL:** strict gate code + controlled export/replay tested.
**GEOMETRIC:** representative arch/apex relationships validated;
synthetic meshes only for new topologies.
**ARCHITECTURAL:** no new vault-type geometry approved.
**HISTORICAL:** not claimed.
**STRUCTURAL:** not claimed.

Next task: apply R16 to a **real new Gothic vault type** with its
measured boundary arches, groins, crown, locked bearings and available
roof clearance. Keep this adapter experimental until that real
architectural trial is reviewed.
