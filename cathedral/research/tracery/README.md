# Gothic Tracery — Research and Construction Register

**Branch:** `cathedral/experimental-tracery-stleu-r01`  
**Status:** Research and experimental geometry; NOT a replacement for approved architecture.

## Purpose
Develop historically grounded, reproducible Gothic window and buttress tracery from source engravings through calibrated 2D vector construction to separately editable 3D stonework. Preserve the engraving, geometry provenance, explicit solid/void topology, construction parameters, and validation.

## Workstreams
- [Universal generator U01–U05](universal-generator-U01-U05-2026-11-07/README.md): spec-driven construction, orders and mouldings, masonry jointing, rose window, tracery as its own masonry layer; full handoff, scripts, QA and next steps (experimental, 2026-11-07).
- [Saint-Leu-d'Esserent Fig. 80](st-leu-fig80/README.md): wall, pointed enclosing arch, twin lancets, six-lobed oculus, inward-returning arch junctions, experimental V08 sweeps and historically attributed mullion section.
- Ungewitter CXVIII Fig. 1205b: separate existing Phase 3A research; retain its source and unresolved a/b/c construction labels.
- QF-001: earlier user-approved reusable quatrefoil construction, subject to actual file/baseline verification. Do not recreate or overwrite it.
- Other plate tracings: preserve historical source scans and link verified arc reconstructions by source, plate, figure, scale and error.

## Geometry schema
1. **Enclosure:** surrounding wall face, arch envelope, coursing, structural stone.
2. **Facing stone:** solid flat outward-facing masonry, spandrels, mullions, tracery rings and web material.
3. **Voids:** true cut-through lancet and tracery apertures, not merely black contour strokes.
4. **Section/returns:** explicit front-to-back profiles and connection surfaces, with independent solid components.

Black continuous = supported traced contours; gray dashed = construction; red dashed = uncertain or alternative. Source pixel coordinates must never be labelled physical 1:1 units without measured calibration.

## Validation hierarchy
- Technical: files, hashes, imports/exports, reproducibility.
- Geometric: closed solids, nondegenerate faces, exact interfaces, measured fit, continuity.
- Architectural: correct solid/void separation, bearings, reveal and glazing relationship.
- Historical: direct source attribution, limits of section and dimensional evidence.
- Structural: requires independent evidence; watertight geometry alone does not validate capacity.

## Protected boundaries
No modifications to F5ZK-C, F5ZN-A, working inner/middle ambulatory generator, Pass 6J, QF-001 approved construction or historical scans. F5ZL-C support schedule remains unresolved. Experimental construction is not automatically approved.

- `universal-generator-U06-centreline-2026-11-07/` — U06 centreline mode (EXPERIMENTAL): tracery laid out on interdos centrelines (Hillson rule or survey circles), run through unchanged U01-U03; Reims chevet-chapel windows from Hillson, ADS 2024.
