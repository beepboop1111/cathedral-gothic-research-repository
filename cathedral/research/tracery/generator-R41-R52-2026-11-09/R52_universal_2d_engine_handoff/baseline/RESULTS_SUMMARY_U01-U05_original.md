# Results summary (generated from the verified clean rebuild, 2026-11-07)

Counts are passed/total automated checks per validation kind. Blender = per-object re-import QA.

## U01

| model | geometric | architectural | technical | stones | Blender objects | Blender |
|---|---|---|---|---|---|---|
| stleu_fig80_rebuild | 20/20 | 7/7 | 3/3 | - | 3 | ok |
| stleu_fig80_ideal | 20/20 | 7/7 | 3/3 | - | 3 | ok |
| bar_2light_sexfoil | 26/26 | 8/8 | 3/3 | - | 3 | ok |
| bar_4light_recursive | 40/40 | 12/12 | 3/3 | - | 3 | ok |
| intersecting_3light | 19/19 | 7/7 | 3/3 | - | 3 | ok |

St-Leu rebuild vs archived R03 fixture: IoU 0.999467, Hausdorff 0.578 px, face area 106873.7 vs 106873.0 px², tests 3/3.
Ideal (symmetric + regular sixfold) vs rebuild, max boundary deviation px: L1 1.07, L2 1.07, F1 3.36, outline 0.01.
Baseline comparison: {'stleu_fig80_rebuild': True, 'stleu_fig80_ideal': True, 'bar_2light_sexfoil': True, 'bar_4light_recursive': True, 'intersecting_3light': True}.

## U02

| model | geometric | architectural | technical | stones | Blender objects | Blender |
|---|---|---|---|---|---|---|
| stleu_fig80_rebuild | 8/8 | 3/3 | 3/3 | - | 3 | ok |
| bar_2light_sexfoil | 12/12 | 5/5 | 3/3 | - | 10 | ok |
| bar_4light_recursive | 14/14 | 6/6 | 3/3 | - | 22 | ok |
| intersecting_3light | 10/10 | 4/4 | 3/3 | - | 4 | ok |

## U03

| model | geometric | architectural | technical | stones | Blender objects | Blender |
|---|---|---|---|---|---|---|
| stleu_fig80_rebuild | 10/10 | 5/5 | 2/2 | 20 | 22 | ok |
| bar_2light_sexfoil | 14/14 | 7/7 | 2/2 | 61 | 63 | ok |
| bar_4light_recursive | 16/16 | 8/8 | 2/2 | 113 | 115 | ok |
| intersecting_3light | 12/12 | 6/6 | 2/2 | 56 | 58 | ok |

## U04

| model | geometric | architectural | technical | stones | Blender objects | Blender |
|---|---|---|---|---|---|---|
| rose_12_cusped | 16/16 | 8/8 | 2/2 | 85 | 87 | ok |
| bar_4light_recursive | 16/16 | 8/8 | 2/2 | 113 | 115 | ok |

## U05

| model | geometric | architectural | technical | stones | Blender objects | Blender |
|---|---|---|---|---|---|---|
| stleu_fig80_rebuild | 10/10 | 5/5 | 2/2 | 20 | 22 | ok |
| bar_2light_sexfoil | 14/14 | 7/7 | 2/2 | 46 | 48 | ok |
| bar_4light_recursive | 16/16 | 8/8 | 2/2 | 83 | 85 | ok |
| intersecting_3light | 12/12 | 6/6 | 2/2 | 48 | 50 | ok |
| rose_12_chassis | 16/16 | 8/8 | 2/2 | 109 | 111 | ok |

