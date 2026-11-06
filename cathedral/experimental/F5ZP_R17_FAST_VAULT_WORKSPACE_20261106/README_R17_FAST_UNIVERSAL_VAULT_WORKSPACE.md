# Cathedral F5ZP — R17 Fast Universal Vault Testing Workspace

**Status: EXPERIMENTAL — functioning live Blender 5.0.1 workspace.
NOT an approved cathedral vault generator, new historical claim, or
replacement for the working F5ZN-A ambulatory system.**

R17 wraps the existing **R16 strict crown and locked-geometry guard**
without modifying the original code. It provides a reusable Blender
sidebar panel, 1:1 procedural test meshes, review cameras, two detail
presets, automatic numerical QA, protected-source SHA-256 verification,
and versioned experimental exports. The tests use synthetic sample
vault layouts; historical accuracy has NOT been established.

## Open the live Blender workspace (MR.COMPUTER)

Open the newest saved file:

`blender/F5ZP_R17_FAST_VAULT_WORKSPACE_REVIEW_READY_V02_EXPERIMENTAL.blend`

The required R17 add-on is already installed and enabled persistently
in MR.COMPUTER's Blender 5.0.1 user preferences.

1. In Blender's 3D View press **N** to open the sidebar.
2. Choose **R17 Vault**.
3. Choose a vault family: **3**, **4**, **5**, **6**, **8** sector, or
   **custom 3–12 sectors**. A regular plan can be perturbed with
   `Plan irregularity` without manually duplicating vertex arrays.
4. Set **FAST (32 divisions)** while experimenting with proportions.
   Switch to **FINAL (128 divisions)** for denser surface geometry.
5. Select the independent crown setting:
   - **Prefer raised (new):** R16 suggests a safe ABOVE-apex crown.
   - **Exact arch apex (warn):** snaps analytically to the measured
     highest pointed arch apex and shows the reduced-dome WARNING.
   - **Manual/locked:** use a specified height; reject if below apex.
   - Check **Crown protected/locked** only with Manual setting. Auto
     selection is explicitly blocked for a locked crown.
6. Adjust pointed arch rise/span, dome convexity and
   apex-to-crown meridian curvature. Preview with one click:
   **REGENERATE TEST VAULT**.
7. Review the same newly regenerated vault in the built-in Axon,
   Plan, Underside and Section scenes. Camera scene switches share
   ONE procedural geometry collection. No mesh duplicates per view.
8. Export just the validated active web in full native **1:1 GLB**,
   or save a **new versioned experimental .blend**. Previous output
   versions are never overwritten by the add-on.

The floating geometry is a visualization and computation sample.
Source arches, radial ogives and web center are represented by their
own distinct colored curves/meshes. No buttress, pier, masonry or
fitted historical moulding is implied.

## Strict R16 policy — always enforced

Crown-height gate:
```
crown_Z >= max(actual apex Z over every boundary pointed arch)
```

The guard runs **before any new mesh is generated**, and once more on
the actual in-memory result, before the original R17 viewport geometry
is replaced or exported. Every build uses 257 real sampled points
for each two-centered Gothic boundary arc.

* Below highest apex: **HARD STOP; existing last-valid R17 mesh survives**.
* Exactly level: **WARNING — reduced dome effect**.
* Higher: permitted, and **preferred for new unlocked studies**.
* Positive preferred rise for new studies:
  `max(25 native units, .08*(highest_apex_Z-spring_Z))`.
  This 8% is a provisional R16 design preference, NOT a locked cathedral
  dimension. Never apply it automatically to a locked crown.
* Any unexpected change to the frozen R16 source or the archived
  boundary-arch inputs triggers a hard stop.
* `LOCKED_GEOMETRY_WARNING_ALWAYS` appears in all successful reports,
  and in failure reports.
* Missing actual roof/masonry envelope is explicitly reported.
  An open intrados never proves valid cover or structural capacity.
* The 1e-8 native tolerance in the R16 guard exists only for
  representation roundoff, NOT as permission to lower a crown.

**Why there is an Exact arch apex option:** Blender FloatProperty values
are stored with float32-style rounding. Merely copying the printed apex
number into a manual height can produce a small unintended BELOW-apex
input. The explicit LEVEL option reads the exact measured apex from
the same source geometry (no altered historical coordinates) so the
strict R16 comparison stays meaningful.

## Geometric method

`addon/r17_core.py` builds each plan with a procedural loop of N
vertices and two-centered true circular pointed boundary arches.
Groins are radially continuous from the perimeter springing points
to an independently controlled central crown (no bending/fan ends).
Every boundary arch is retained exactly; the interior is a smooth
convex interpolation with adjustable curvature.

The web uses a triangular parametric patch per bay:
```
P(r,t) = (1-r) * perimeter_chord(t)
z_base = (1-r)^p * z_pointed_arch(t) + [1-(1-r)^p] * crown_Z
z_web  = z_base + dome_lift * (crown_Z - z_base)
                       * sin(pi*t)^2 * sin(pi*r)^2
```
Here r=0 is the actual Gothic boundary arch, r=1 the independent boss;
t=0 and t=1 are original radial groins. The optional dome correction
vanishes at each boundary and remains below the higher boss, avoiding
the earlier accidental sagging meridian shapes. This is a **generic
experimental surface family**, not a historically reconstructed web.

The mesh shares vertices along rib seams. At FINAL, a four-sector
example has **65,536 web triangles**; at FAST it has **4,096**.
R17 operates entirely at native 1:1 architectural coordinate scale,
with no hidden scaling of the approved cathedral floor plan.

Note that camera and 3D viewport display settings differ. The
user's established 9.3-mm lens and 0.01m to 99,999,997,952m viewport
clipping parameters are preserved. Review cameras use independent,
bounded orthographic clip planes for numerical visibility.

## Performance and testing (MR.COMPUTER Blender 5.0.1)

Headless Blender tests measured:
- FAST 3-sector: 0.028 sec, 3,072 triangles
- FAST 4-sector: 0.035 sec, 4,096 triangles
- FAST 5-sector: 0.048 sec, 5,120 triangles
- FAST 6-sector: 0.050 sec, 6,144 triangles
- FAST 8-sector: 0.068 sec, 8,192 triangles
- FAST irregular CUSTOM 7-sector: 0.059 sec, 7,168 triangles
- FINAL 4-sector: 0.406 sec, 65,536 triangles

These measurements are for in-memory regeneration and QA **only**,
not loading Blender, rendering, waiting for UI, export or disk storage.
They reflect this test machine; they are not performance guarantees.

Automated integration results:
- 7 distinct FAST/FINAL controlled regeneration studies.
- Exact-level warning and reported ratio to apex.
- Below-apex hard stop with no replacement of the prior valid mesh.
- Locked crown AUTO hard stop with no replacement of prior valid mesh.
- All reported R16 baseline SHA-256 source snapshots unchanged.
- 5 reusable named scenes share a single active experimental mesh.
- GLB exported in full 1:1 native dimensions.
- A new numbered Blender checkpoint was saved, preserving V01 bytewise.
- Matched-camera Plan / Axon / Underside / Section renders exported.
- Blender 5.0.1 add-on was reloaded and verified in a **fresh process**.

The Blender glTF exporter reported Draco compression unavailable in
one run; it nonetheless completed a standard uncompressed GLB.
No requirement to install Draco to use R17.

## Where everything is

- `addon/r17_experimental_workspace.py` — reusable R17 sidebar,
  operator, geometry/locks checks and versioned GLB/.blend outputs.
- `addon/r17_core.py` — procedural Gothic 2D/3D geometry.
- `addon/r17_vendor/strict_crown_guard.py` and
  `guarded_vault_adapter.py` — unmodified original R16 dependencies;
  source hashes pinned in `addon/r17_vendor_sha256.json`.
- `scripts/bootstrap_R17_workspace.py` — build new scratch workspace.
- `scripts/install_R17_blender_addon.py` — install persistent UI
  (existing unrelated add-ons never overwritten).
- `scripts/finalize_R17_review_v02.py` — optional camera/backdrop
  refinements in a separate V02 .blend, without changing web geometry.
- `tests/test_R17_blender_live_ops.py` — functional live Blender
  regeneration, strict failed-build preservation and GLB export.
- `configs/R17_R16_ORIGINAL_PROTECTION.json` — exact R16 source ledger.
- `qa/` — test logs, checksum-preservation ledger, Blender workspace
  setup and complete geometry QA per build.
- `screenshots/` — measured camera renders; not arbitrary AI images.
- `outputs/` — numbered per-build QA, one experimental GLB.
- `blender/` — V01 original, first validated checkpoint, V02
  camera-ready checkpoint.

## Reproduction

From the R17 experiment directory on MR.COMPUTER:
```bash
blender -b --factory-startup --python scripts/bootstrap_R17_workspace.py
```
The script refuses to overwrite an existing V01 .blend. To reproduce
independently, use a NEW experiment directory, and copy the source
files and matching R16 vendor/manifest. The original archive contains
the exact scripts and default test settings.

For interactive use, install the isolated R17 add-on in a fresh Blender
user profile or on MR.COMPUTER, then open the V02 .blend. The save
button writes a new `R17_FAST_VAULT_WORKSPACE_CHECKPOINT_NNN` version.

## Validation categories and remaining limitations

- **Technical: passed** for R17 generation, UI, Blender persistence,
  glTF output and reproducible tests.
- **Geometric: passed** for the explicitly tested synthetic pointed
  boundary arcs, radial seams, 1:1 coordinates and crown-height gate.
- **Architectural: NOT validated** against an actual saved F5ZN-A
  historic or approved cathedral vault.
- **Historical: NOT validated**; no claim of historically correct
  Gothic web curvature/proportions for new families.
- **Structural: NOT validated**; no ribs, buttresses, masonry
  thickness, coursing or true thrust paths approved.

F5ZK-C, F5ZN-A, the existing working AMB-I/M generator, V13 webs,
Pass 6J and the unresolved F5ZL-C support schedule are untouched.
The R16 enforcement layer remains an **experimental adapter**, not a
new authority for modifying these locks. R17 may eventually be used
to test real new vault skeletons, but importing official geometry and
changing any locks requires their own recovery/checkpoint and user
approval. Keep completed working generators separate.

**Next safe architectural trial:** choose a real vault type whose
boundary-arch and groin coordinates are fully recovered. Use the
same R16 pre/post guard to evaluate it in a new experiment before
considering any transfer into an approved cathedral model.
