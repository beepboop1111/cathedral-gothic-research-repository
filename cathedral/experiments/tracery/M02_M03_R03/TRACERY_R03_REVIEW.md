# Gothic Tracery R03 — experimental review

Meaux's reported topology defects are repaired. The original inputs and generation settings were recovered first, and all four original final STLs reproduced byte-for-byte.

| Window | Nonmanifold edges | Degenerate faces | Openings retained | Bounds change |
|---|---:|---:|---:|---:|
| meaux | 6 → 0 | 7 → 0 | 48 | 0 mm |
| haina_1264 | 34 → 0 | 56 → 0 | 21 | 0 mm |
| haina_1265 | 6 → 0 | 10 → 0 | 30 | 0 mm |
| chalons | 0 → 0 | 4 → 0 | 19 | 0 mm |

All four repaired STL/GLB models are closed, consistently wound, one-piece meshes with zero nonmanifold vertices, duplicate triangles or detected self-intersections. Independently reloaded exports pass numerical QA. All four original bounds remain unchanged. Meaux retains 40 enclosed apertures and eight open-edge cutouts at the cropped base, totaling 48 classified openings.

The Meaux repair moves six vertices by at most 0.000009537 mm and removes 18 collapsed triangles. It preserves the existing cusp and moulding geometry; complete depth and longitudinal section comparisons differ by less than 0.000003 mm across all four models.

M03 adds persistent semantic IDs, confidence and evidence, crop flags, guarded correction sidecars and selectable SVGs. All 118 opening IDs pass repeat/reordered-label and exact2x scale tests. Ten mesh tests, nine semantic unit tests and all four full-image semantic regressions pass. A second fresh numeric run reproduced every model byte-for-byte.

The complete ZIP includes scripts, preserved inputs, exact settings, four STL/GLB pairs, the Meaux Blender comparison scene, SVG/JSON semantic registers, comparison images, numerical QA, pinned dependencies and `CHECKPOINT_R03.md` with a reproduction command.

These are nominal-scale raster-derived studies, not historically calibrated cathedral stonework. Exact historical arcs and moulding interpretations remain research work. **Everything stays experimental pending explicit approval; no authoritative generator or protected architecture was changed.**
