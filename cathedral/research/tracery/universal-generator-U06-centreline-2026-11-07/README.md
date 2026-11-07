# U06 centreline mode (EXPERIMENTAL, 2026-11-07)

Bar tracery laid out on **centrelines** (Hillson's interdos lines), with the bars added around them. Built because
the U01 bar mode could not reproduce Hillson's survey of the Reims chevet-chapel windows (first pass: U01 best fit
17-41 mm RMS; Hillson's centreline construction 9-15 mm; survey floor 4-6 mm).

* `scripts/tracery_centreline_U06.py` — the U06 model. Centrelines from **Hillson's chevet-chapel rule**
  (`axis, span, apex, spring, oculus_z`) or from **any circles** (e.g. survey fits). Bars are offset both ways,
  forks (lancets springing from the mullion and jambs) are resolved by union, and the result is presented to U02/U03
  exactly like U01 bar mode. One U03 extension: the frame keeps its courses up to a stilted main arch's springing.
* `scripts/run_U06.py` — runs the U01, U02 and U03 runners **unchanged** (it only tells them how to build a
  `"type": "centreline"` spec), together with the regression models.
* `scripts/specs_U06.json`, `sections_U06.json`, `joints_U06.json` — three Reims windows; bars, depth, mouldings and
  joints are TRIAL values (no Reims section data).
* `survey/` — marker extraction and fitting scripts, points and fits from Hillson, *Windows on the Past*, ADS 2024,
  doi:10.5284/1125809 (check the collection licence before committing derived data).
* `U06_review.png` — the review sheet. `out/` is regenerated and not meant for commit.

## Run it (Ubuntu)

1. Install the packages once (same as U01-U05):
   `pip install --break-system-packages -r ../universal-generator-U01-U05-2026-11-07/requirements.txt`
2. From this folder: `bash scripts/run_U06.sh`
   (about 2 minutes; prints the QA and Blender lines and rewrites `U06_review.png`).

## Results (clean rebuild)

| model | U01 | U02 | U03 | stones | largest | survey RMS |
|---|---|---|---|---|---|---|
| N5.3.n, Hillson's figure numbers (placed by translation) | 45/45 | 17/17 | 20/20 | 46 | 1.90 m | 17.5 mm |
| C1.e, Hillson's rule fitted (5 values) | 45/45 | 17/17 | 20/20 | 45 | 2.25 m | 12.4 mm |
| C1.e, surveyed circles | 40/40 | 17/17 | 20/20 | 50 | 2.10 m | 4.5 mm |

All U01 checks 311/311, St-Leu regression 3/3, `bar_2light_sexfoil` U02 and U03 identical to the archived results,
Blender 5.2.3 re-import clean at the U01 and U03 stages. Structural behaviour is not assessed.
