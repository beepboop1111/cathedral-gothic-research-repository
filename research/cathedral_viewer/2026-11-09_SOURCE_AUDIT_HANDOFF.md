# Cathedral Viewer — source audit and adaptation handoff
Date: 2026-11-09
Status: SOURCE AUDIT / PROPOSAL ONLY — no cathedral geometry modified or viewer implementation performed.

## Sources
- Application: https://github.com/ctate/3d-model-generator (main)
- Target research archive: https://github.com/beepboop1111/cathedral-gothic-research-repository
- Reviewed: README.md; package.json; next.config.mjs; tsconfig.json; lib/api-service.ts; lib/form-schema.ts; components/{model-viewer,model-component,scene-setup,rodin,form,options-dialog}.tsx; app/page.tsx; app/api/{rodin,status,download,proxy-download}/route.ts.

## Summary
The application is a Next.js 15 / React 19 frontend for Hyper3D Rodin generation, with a Three.js / React Three Fiber GLB viewer. It is suitable as an *inspection frontend* but not as the authoritative mathematical geometry generator for F5ZP.

### Code findings (source level; not runtime validated)
1. CRITICAL SECURITY: `app/api/proxy-download/route.ts` fetches arbitrary client-supplied URLs. Risk: SSRF. Restrict allowed hosts and redirect targets, reject private addresses, add size/time limits and content-type controls before deployment.
2. HIGH: `next.config.mjs` ignores TypeScript and ESLint build errors. Enable checks; verify lint command compatibility with Next.js.
3. API keys: Rodin routes use literal public demo token `vibecoding`; not a production credential. Move private credentials into server-side environment configuration and enforce access controls.
4. VIEWER SCALE: `components/model-component.tsx` uses `<primitive object={scene} scale={1.5} />` and `<Center>`. Arbitrary scaling / recentering are unsuitable for authoritative 1:1 measurement. Keep vertex coordinates and unit metadata intact; allow explicit reversible view offsets.
5. CAMERA: `model-viewer.tsx` starts camera at [0,0,5], fixed zoom 3–10, disables pan, and autorotates. Replace with bounding-box camera framing, plan/elevation/perspective, and orthographic option.
6. FORMATS: Export choices include GLB, USDZ, FBX, OBJ, STL but `rodin.tsx` finds only a GLB for preview; `useGLTF` loads GLB, not STL/OBJ. Add independent upload/loaders.
7. QUALITY: `rodin.tsx` uses loose `any` API structures, setTimeout polling with no visible cancellation, and unvalidated proxy URLs. Type and cancel asynchronous tasks; validate model download URLs.
8. No measured architecture, section tools, automated geometric QA, or editable construction parameters found in inspected code.

## Architectural integration plan
**Authority:** Existing Blender 5.1+ bpy generators, V13 webs, F5ZK-C floor plan, F5ZN-A dimensions, F5ZP M01, and Pass 6J bearings remain untouched. Treat imported GLBs as review/export meshes; do not replace original curve construction.
**A — Harden:** restrict SSRF, reinstate build checks, type API structures, test existing Rodin workflow.
**B — Viewer V1:** local GLB/STL loading; declared or unknown units (never assume); preserve original coordinates and exact scale; bounding-box camera fit; plan/elevation/perspective; per-object visibility and mesh statistics.
**C — Architectural inspection:** distances, point coordinates, sections, measured SVG overlay, rib/web gap visualization, QA report import.
**D — Research integration:** read-only reference overlays for Ungewitter 1205b, F5ZP ambulatory 14-vault interfaces, and Pass 6J pier/respond junctions.

## Validation gates (distinct)
- Technical: build/type/lint, loader smoke tests, errors and cancellation, safe URL handling.
- Geometric: coordinate and unit preservation, bounds, topology, measurable mesh alignment and regression.
- Architectural: original F5ZK-C / F5ZN-A bearing and junction constraints, ambulatory connections, clearance.
- Historical: source plate attribution; distinguish measured reconstruction from speculative construction.
- Structural: bearing continuity and collision tests; do not infer structural adequacy from visuals.

## First fixture and acceptance
Use a **synthetic** meter-scale asymmetric mesh if authentic cathedral assets are unavailable. Import GLB and STL; verify unmodified vertex positions, known bounding dimensions, and reproducible camera framing. Then review a *copy* of an existing R1 @ 78° or AMB-I/M vault GLB, preserving approved baselines.

## Codex implementation handoff
Work in `ctate/3d-model-generator` on branch `feature/cathedral-viewer` (if available), not on main. Do security/build fixes first, then independent local GLB/STL import, native-coordinate/scale preservation, camera fit, inspectable geometry metadata, and automated regressions. Do not invent or regenerate cathedral source geometry. Review results in a pull request; do not auto-merge.

## Repository governance
This document records an audit and an adaptation proposal, **not** tested code or approved cathedral geometry. No source repository, Blender checkpoint, or cathedral baseline changed during the audit.
