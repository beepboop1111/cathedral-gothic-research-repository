# F5ZP — V19 Two-Generator Full Continuation Handoff
2026-11-07 | Checkpoint V19-HO-R01 | Experimental only

**Environment verified:** MR COMPUTER; Blender 5.0.1, not yet Blender 5.1+.
**Status:** Real Blender regeneration, geometry QA, one-mesh GLB export, and original-V19 numerical comparison PASSED.
**Protected:** F5ZK-C, F5ZN-A, V13 webs, Pass 6J, and the original R12B/R14 apse records. NO GitHub upload.
**Scale:** 1:1 native geometry; NOT proven to be metres or millimetres.

## 1. Exactly two portable generator scripts

1. scripts/v19_rib_arch_generator.py — original-style Gothic pointed boundary arch and independent radial groin / rib curve skeleton generator. It computes true two-centred circular arch geometry, the deterministic irregular plan, the separate R18 circular groins, and R16-style crown geometry guards. In Blender it creates EDITABLE guide curves. These guide paths are NOT physical Gothic rib sections or stone mouldings.
2. scripts/v19_full_vault_generator.py — complete Gothic web generator importing script 1 from the same folder. It uses the same skeleton, R18 base surfaces, and THE ACCEPTED R12B SECTOR02 TYPE-A FOUR-SEGMENT HERMITE MERIDIAN. It creates one editable triangulated open intrados, meridian guides, a .blend, one web-only Blender GLB, numerical QA and optionally a single preview PNG.

Neither script requires the old Blender add-on, an existing .blend, GitHub, a zip file, or an absolute /home/christopher dependency. Both use only Blender 5.0+ and Python standard library. The source algorithms and parameters are visibly included in these two files.

## 2. Original V19 reference dimensions

| Parameter | Native V19 value |
|---|---:|
| Plan | Four-sector irregular quadrilateral |
| Radius parameter | 620.0 |
| Irregularity | 0.12 |
| Rotation | 13 degrees |
| Spring elevation | Z0 |
| Arch rise/chord | 0.92 |
| Crown mode | AUTO, not locked |
| Highest pointed boundary apex | Z884.4340255 (original Blender float) |
| Central boss/crown | Z955.1887475 |
| Maximum open web height | Z970.6726714 |
| Highest web over boss | 15.4839238 |
| Maximum independent groin radial run | 684.9321899 |
| Meridian exponent | 1.75 |
| Dome lift | 0.12 |
| Final triangulation | 128 per sector |
| Final vertices, triangles | 33025 vertices, 65536 triangles |
| Open boundary edges / Euler | 512 / 1 |

Original plan corners at springing (X,Y), in order:
- 00: (666.38032769, 158.33307819)
- 01: (-143.00624633, 565.88965788)
- 02: (-541.62746482, -121.40824991)
- 03: (134.41323515, -642.40916227)

The standalone Python setting uses literal 0.12. Original Blender FloatProperty represented this as approximately 0.1199999973; this causes differences of less than 0.0001 native units.

## 3. Geometry reconstruction — skeleton first

Plan corners: for sector k, phi = 2*pi*k/N. theta = phi + rotationRadians + irregularity*0.18*sin(phi+0.3). radius(k) = radius*(1+irregularity*cos(phi+0.51)). Corner(k) = (radius(k)*cos(theta), radius(k)*sin(theta)). No manually hardcoded mesh vertices.

Boundary Gothic arch: adjacent corner chord L, rise h = arch_rise_ratio*L, and c=L/4 + h^2/L. Let d=L*min(t,1-t). The elevation is spring + sqrt(c^2 - (d-c)^2), with XY interpolated across the chord. These are two circular arcs meeting at the pointed midspan apex, not an ordinary half-circle or generic spline.

Independent groin: for each plan corner (x,y), radial run L and crown rise h, circle center a=max(L,(L^2+h^2)/(2L)), b=(L^2+h^2-2*a*L)/(2*h). Circle radius R=sqrt(a^2+b^2). Groin XY=(1-r)*(x,y). Groin Z=spring+b+sqrt(R^2-(L*r-a)^2), from r=0 at spring to r=1 at boss. V19 requires h >= L at every groin: this preserves the vertical springing tangent and monotone rise. Unsupported shallow circles are REJECTED, not silently substituted with the other R18 fallback.

R16-compatible geometric limits: crown must be at/above every highest boundary arch apex. AUTO crown suggestion is apex+max(25,0.08*(apex-spring)). An explicitly locked crown cannot be auto-shifted. No roof, cap or solid masonry clearance is assumed or fabricated. This portable pair implements the essential R16 geometry rules, but is NOT a replacement for the original complete R16 audit/checksum-governance engine.

## 4. R18 base web formula (before the user red meridian)

At each sector, t runs between the two independent groins, r runs from the boundary to the boss. Let Hleft(r), Hright(r) be independent groin elevations. Radial = (1-t)*Hleft + t*Hright. Let Arch(t) be the two-centred pointed boundary elevation. Let f=clamp((Arch(t)-spring)/(crown-spring),0,1).

Base = Radial + (crown-Radial)*f*(1-r)^meridian_exponent.
Base += dome_lift*(crown-Base)*sin(pi*t)^2*sin(pi*r)^2.

The exact original arch is imposed at r=0, the exact independent groins at t=0 and t=1, and the unchanged boss at r=1.

## 5. CRITICAL — original accepted R12B Sector 02 cubic Hermite meridian

DO NOT OMIT OR REPLACE THIS SECTION with a generic U-shaped arch or dome.

Source is the user's accepted R12B red stroke for original Apse Sector 02. It was fitted with FOUR smoothly joined cubic Hermite segments with common ORIGINAL world-Z endpoints Z4296 and reference mid-arch-to-boss PLAN distance 738.8206500 native units.

Original knots:
- s = [0, .25, .5, .75, 1]
- original world Z = [4296, 4356.254741314415, 4369.825253124143, 4347.047844059482, 4296]
- dZ/ds = [248.97069966590794, 122.45209025304281, -27.85941314245789, -142.1618793549983, -176.04933307532278]
- accepted source peak Z4370.341134563053, or 74.34113456 above endpoints.
- accepted source red-line RMS 0.7371464677 native units.
- embedded source configuration SHA256: a9312346824a17153f7a5eabce488d8f1f0911cac1357d1d4b06d3568eea97b5.

For each segment with local u=(s-si)/(si+1-si) and dt=si+1-si, define height offsets Hi=Zi-4296. Hermite interpolant is:

H = (2u^3-3u^2+1)*Hi + (u^3-2u^2+u)*dt*Mi + (-2u^3+3u^2)*Hi+1 + (u^3-u^2)*dt*Mi+1.

In new V19 bays, DO NOT reuse original Z4296 as a world coordinate. Instead compute an equal-endpoint ZERO-offset Hermite function Hhermite(s). For each experimental sector, use the existing boundary arch mid-apex and unchanged boss as endpoints, with actual midpoint-to-boss plan run D:

TargetMeridian(r) = (1-r)*ArchApex + r*Boss + Hhermite(r)*(D/738.82065).

The complete shaped web is:

FinalWeb(k,t,r) = BaseWeb(k,t,r) + sin(pi*t)^2 * [ TargetMeridian(k,r) - BaseWeb(k,.5,r) ].

The sine-squared term is ZERO on BOTH groins. The zero-endpoint Hermite correction is also ZERO at the pointed boundary and boss. Thus it gives the user's curved center meridian WITHOUT moving the original plan, arches, independent ribs or central crown.

**Historical R14 types remain separate.** The real six-sector apse has Type A on Sectors 00–04 (using Sector02 reference) and a DIFFERENT accepted Type B on Sector05. This four-sector V19 experiment applies the Type A shape to its four SYNTHETIC sectors. It does not replace or reproduce R14's Type B entrance geometry.

## 6. Reproduction commands

Both .py files must be in the SAME scripts folder. Commands run in an ordinary shell on MR COMPUTER, against a NEW empty destination.

A. Standalone arches + groins, editable skeleton .blend and JSON:

    blender -b --factory-startup --python scripts/v19_rib_arch_generator.py -- --out ./skeleton_new

B. COMPLETE vault with the Hermite meridians, editable scene, GLB and one PNG:

    blender -b --factory-startup --python scripts/v19_full_vault_generator.py -- --out ./vault_new

C. Fast QA without a new preview image:

    blender -b --factory-startup --python scripts/v19_full_vault_generator.py -- --out ./vault_fast --quality FAST --no-render

The full script can accept --sectors, --radius, --irregularity, --rotation, --arch-ratio, --spring, --quality FAST|FINAL, and --crown (optional manual value); --locked requires an explicit manual crown. Invalid geometries reject instead of clamping the design or overwriting an approved source.

File output:
- Skeleton: V19_SKELETON_EXPERIMENTAL.blend, V19_SKELETON_QA.json.
- Full: V19_FULL_VAULT_EXPERIMENTAL.blend, V19_OPEN_INTRADOS_BLENDER.glb, V19_FULL_VAULT_QA.json, optionally V19_SINGLE_PREVIEW.png.
- The .blend has hidden original-color arch/groin 3D construction guides and a visible RED Type-A Hermite meridian guide collection. The GLB contains ONLY the web surface: no guides, default Cube, ribs, pier or invented masonry volume.

Files are write-once, refusing any existing named output. Each new generator run uses a new output directory. Do not run the scripts on an important unsaved working scene; use --factory-startup as shown.

## 7. Actual regression and confidence levels

Blender 5.0.1 on MR COMPUTER, two-script handoff independently executed from a blank factory-startup session:
- Python syntax: PASS both scripts.
- Arch/groin curves and skeleton .blend: PASS.
- Complete triangulated web and editable .blend: PASS.
- ONE web-only GLB export: PASS after detecting and FIXING a Blender default-Cube selection issue. The fix exports from a temporary single-object scene and then deletes only that temporary scene.
- Exactly 65,536 mesh faces and no extra GLB primitive: PASS.
- Exact boundary arch, independent groin, boss, plan and user-shaped midpoint meridian tests: PASS, residual <= 1e-6 native.
- Mesh open-disk Euler 1, 512 boundary edges, nondegenerate triangle check: PASS.
- Reproduction compared with ORIGINAL V19 GLB: max nearest vertex deviation 0.0000863168 native units and mean ~0.0000123 native units, with matching bounds, 65536 faces and winding consistency.
- Accepted R12B Hermite normalized peak reproduced to ~74.341134563 native.
- Invalid manual crown below arch apex: REJECTED.
- Auto-shifting locked crown: REJECTED.
- Shallow vertical-spring circle: REJECTED.
- Arch with rise/span <= 0.5: REJECTED.

**Technical validation: PASS.** **Synthetic geometric C0 positional validation: PASS.**
**Architectural integration: NOT VALIDATED. Historical set-out: NOT VALIDATED. Structural and masonry: NOT VALIDATED.**

## 8. Active known limitations and architectural protection

- The resulting model is an OPEN INTRADOS surface, not a watertight roof or physically sectioned vault. No masonry thickness, ribs' user-selected PNG moulding, respond/capital, tas-de-charge or voussoir joints are included.
- Roof clearance is UNRESOLVED. Original R12B Type A apex peaked Z4370.34, about 29.34 above provisional cap Z4341. Original R14 unique Type B peaked ~Z4337.13, about 3.87 below that cap, insufficient to establish physical thickness.
- V19 experimental web peak above its boss by ~15.484 native. With no V19 cap profile, DO NOT call that a roof clearance pass.
- R15 found groin-to-web normal breaks ~35–51 degrees in the DIFFERENT six-sector apse. Exact positional C0 seam welding does NOT imply G1 tangent smoothness in this new V19 study. Repair only when masonry and cross-section requirements justify it; do not flatten or override accepted red curves.
- F5ZK-C chevet 7 centers (30/50/70/90/110/130/150 degrees) and 1:1 scale remain unchanged.
- F5ZN-A and original validated V13 fourteen inner/middle ambulatory vaults remain unchanged; outer ring/AMB-O remains outside this experiment.
- Pass 6J asymmetric R1 78-degree bearing arrangement and pier/springing studies remain locked independently.
- F5ZL-C support schedule is STILL MISSING. No invented supports, loads or capacities.
- True physical rib/ogive and doubleau section profiles still have to be chosen by the user. These scripts provide mathematically sound ARCH and GROIN PATHS, not proven structural solids or completed moulding sweeps.

## 9. Next stage

1. Keep V19-HO-R01 and both scripts as reproducible EXPERIMENTAL checkpoint.
2. Choose actual rib/arch PNG profile family and soffit measurements. Apply a separate vector profile sweep in a later study, preserving original bearing locations.
3. If necessary, isolate one groin/web junction and test its surface-normal transitions (not merely positional seam welding).
4. Resolve masonry cap/roof clearance and support data before approval.
5. Never silently replace F5ZN-A, V13 webs, Pass 6J or the original R12B/R14 meridian curves.

## 10. Source provenance and version hashes

Original reference source versions:
- R17 core SHA256: 58cc8805c6bf74cdafc55a05d529f904dc7d9184986ac4c3e0ff079
- R18 skeleton SHA256: a7e73e5f5f54d729fa17cd9a3cd24b883ad9213c2a28a6cc7c31dd2cdb32457d
- R03 accepted-meridian integrator SHA256: 5662388fb129168667e32f7a44e1b877ad03d922c9602f00eb479188e39b2d22
- R12B original red-line configuration SHA256: a9312346824a17153f7a5eabce488d8f1f0911cac1357d1d4b06d3568eea97b5
- Original source V18 V04 Blender SHA256: 62c9c9cea6f555f9646e371d4aeb8df514049528595dbc9d1a958e86e84fdf73

The two distributed scripts are independent portable DERIVATIONS, not bit-for-bit copies of R17/R18/R03. They embed the original analytic construction and exact accepted R12B knots, making re-generation possible without the old add-on installation. The actual original V19 preserved sources were not overwritten.

**GitHub: not contacted or uploaded for this handoff.**
