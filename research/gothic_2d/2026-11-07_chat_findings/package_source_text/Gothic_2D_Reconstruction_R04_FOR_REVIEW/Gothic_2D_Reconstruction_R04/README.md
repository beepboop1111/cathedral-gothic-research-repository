# Gothic 2D Reconstruction R04 — Sixfoil circle-arc study

**Status:** experimental, for user review, NOT an approved project generator. All source scans and historical plans remain unchanged.

## Result

Using the unmodified R03 mirrored source PNG (1563 × 1996 pixels), R04 identified the white opening inside each of the seven upper sixfoil roundels, recovered its ink contour, and fitted each lobe's central circular part independently. **42 measured candidate circles** (six per roundel) were recovered. A robust nonlinear least-squares circle fit was used for each selected segment. RMS radial residual range: **0.245–0.400 source pixels**, pooled 0.302 pixels. This describes the selected circular parts only: **not cusp shape error and not entire outline error**.

The main sixfold motif orientation occurs in six positions; the upper middle/central roundel is rotated by 30° relative to these. It also differs in shape/size. Master transfer from U_middle_L to the six others is a *test*; no single common construction is imposed on all.

## Drawings and measurements

- `01_MASTER_SOURCE_CROP.png`: original pixels of selected master U_middle_L, as cropped (never retouched).
- `03_MASTER_FIT_OVERLAY.png`: red fitted arcs over original source ink; diagnostic only.
- `04_ALL_SEVEN_ARC_FIT_OVERLAY.png`: red fitted parts over complete unmodified source for visual QA.
- `02_MEASURED_LOBE_ARCS.svg`: vector construction study; solid black = measured circular arc sections, dotted black = full underlying fitted circles, thin light-gray dashed = axes, red dashed = unresolved cusp outline parts. Other geometry intentionally omitted.
- `06_MASTER_CLOSEUP_CONSTRUCTION.svg` / `.png`: close-up of the above geometry.
- `CIRCULAR_ARC_FITS.csv`: 42 fitted circle center/radius/RMS/selected-sample entries.
- `MASTER_TRANSFER_QA.csv`: scale/rotation and deviation when transferring the master geometry to other upper sixfoils.
- `SOURCE_BLACK_VECTOR_R03.svg`: unchanged prior scan-derived black tracing (not a circle reconstruction).
- `SOURCE_MIRRORED_UNMODIFIED.png`, `R03_RING_FITS_REFERENCE.csv`: unchanged inputs.
- `QA_REPORT.json`: source checksum, counts, measurements and explicit limits.

## Important limits

- **Cusps are not analytically completed.** The short joins and abrupt Gothic returns are retained as red dashed unresolved measured contours. Full compass circles are drawn for examination; they are not proof the medieval work used precisely those circles.
- **The foil contour is not a single six-arc closed shape yet.** The measured segments are independently fitted and compared; red gaps are a required next step.
- Only the upper seven roundels were analyzed. Lower two roundels, pointed arches, spandrels, exact mouldings, historical dimensions and sectional depth have not been reconstructed here.
- None of the measurements are calibrated architectural units; all are in pixels of the supplied modern mirrored image, not verified medieval geometry.
- Rotated center roundel transfers less faithfully than the other six. Preserve its distinctive geometry until independently explained.

## Reproduction

From this directory, with Python packages NumPy, pandas, OpenCV, SciPy, Pillow and CairoSVG installed:

```bash
python reconstruct_r04.py SOURCE_MIRRORED_UNMODIFIED.png R03_RING_FITS_REFERENCE.csv .
python finalize_r04.py
python test_r04.py
```

The input artifacts are copied and retained rather than modified. **Do not promote R04 to an approved script until the user has reviewed its geometry.**
