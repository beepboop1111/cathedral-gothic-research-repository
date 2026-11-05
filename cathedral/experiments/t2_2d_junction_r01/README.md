# T2 — enlarged 2D junction plan

Open `T2_ENLARGED_PLAN.png` for the middle ambulatory → five-sided passage panel → D2 chapel / D3 window arrangement. `T2_INTERFACE_DETAIL.png` labels the receiving datums and measured edges. Both have editable SVG companions.

`T2_NATIVE_COORDINATES.svg` uses native project coordinate numbers, with only display Y reversed. `POINTS.csv`, `EDGES.csv` and `T2_GEOMETRY.json` retain full numerical values. All dimensional labels are native project units; no SI conversion is established.

Black boundaries preserve the R04 set-out and recovered source-working bodies. Gray dashed branches describe the 2D plan only. Red dashed lines distinguish the unapproved D2 neck and the separately aligned D3 entry. Node dots denote recorded receiver datums, not newly proposed pier footprints.

The shared middle/T2 edge already matches. The D2 neck has full shared edges with T2 and the chapel body. D3's original source-vector corners differ from T2 by less than 0.0005 native units, within the documented 0.005 recovery uncertainty. This candidate aligns those two D3 corners; the original polygon, other D3 corners, T2 and all protected inner/middle points remain unchanged. No original source file is overwritten.

The minimum 1391.117 inner-to-outer boundary separation is **not** a clear opening or passage certification: wall, arch and moulding thicknesses are absent. These plan checks do not establish heights, vault-web contact or structural capacity.

Twenty-seven checks cover source preservation, valid polygons, exact candidate interfaces, five branch containment, correction tolerance and SVG parsing. See `T2_QA.json` for actual results. The working inner/middle generator, selected R05 crossing and Pass 6J are untouched. The missing F5ZL-C schedule remains unresolved.

Reproduce within this separate experimental directory:

```bash
python -m pip install numpy shapely matplotlib
python scripts/build_t2_plan.py
```

The included R04 snapshot is sufficient. Optional parent-file preservation checks use the original recorded absolute paths and do not modify them. No 3D software or vault generator is invoked.
