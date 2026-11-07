# Ungewitter 1236 | measured 2D research draft

**Start with** `FIG1236_CLEAN.svg` (editable 2D drawing) or `FIG1236_CLEAN.png` (raster preview). The black central four-lobed inner and outer foils are constructed from **eight separately V08-fitted circles**. The pointed enclosing arch and lower openings are **provisional manual visible-stroke reconstructions**, not measured exact circles. Only the source crop extent is covered. The grey dashed axes are guides, not architectural evidence.

| File | Description |
|---|---|
| FIG1236_CLEAN.svg / .png | Main source-limited 2D black-outline reference, no decorative speculation |
| FIG1236_COMPARISON.svg / .png | Exact supplied original crop as an embedded layer with fitted and manually drawn paths superimposed |
| FIG1236_ANALYTIC.svg / .png | Eight complete black dotted candidate compass circles + grey axes; red dashed low-confidence connectors |
| FIG1236_CIRCULAR_FITS.csv | V08 center, radius and residual of all eight arcs |
| FIG1236_SELECTED_INK_POINTS.csv | 657 sampled ink points used by the fit |
| FIG1236_QA.json | Provenance, numerical fits, intersections, confidence and stop rules |
| RESEARCH_NOTES.md | Historical text comparison, verified versus provisional findings, previous research context |
| reconstruct_1236.py | Standalone, repeatable 2D analysis script |
| ORIGINALS/ | Read-only copies of the unmodified uploaded original crop and historical handoff text |
| V08/ | Unmodified Gothic V08 preview toolkit files |
| PRIOR_WORK/ | Essential previous 1193, sexfoil, generated references (flagged as not measured), and Paynter research notes |

**Rebuild:** in the extracted directory, with Python, NumPy, SciPy, Pillow and CairoSVG installed:

```sh
python reconstruct_1236.py --source ORIGINALS/Ungewitter_1236_original_crop.png --out .
```

The exact image SHA-256 is `96ac684bb02bc330912c46cd03a6d42e3ce93e354d67a5b3bf1f370488b95886`. Units are **pixels in supplied crop, X right, Y down**. All output coordinates are 2D. The original Gothic cathedral geometry and generator programs have not been inspected or modified. This research variant is not an approved architecture revision.
