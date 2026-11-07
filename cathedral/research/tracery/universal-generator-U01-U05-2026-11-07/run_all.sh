#!/usr/bin/env bash
# Rebuild U01-U05 from scratch, run every Python QA test, re-check every GLB in Blender.
#   ./run_all.sh            full run with Cycles renders and the five review PNGs (~15 min)
#   RENDER=0 ./run_all.sh   builds + all QA only (~5 min)
# Optional: PYTHON=/path/to/python  FIXTURE=/path/to/StLeu_R03_PLAIN_UPRIGHT.stl
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="${PYTHON:-python3}"
RENDER="${RENDER:-1}"
FIXTURE="${FIXTURE:-$HERE/../early-fig80-study-2026-11-04/MR_COMPUTER_R03_REPRODUCTION/StLeu_R03_PLAIN_UPRIGHT.stl}"
OUT="$HERE/out"
[ -f "$FIXTURE" ] || { echo "St-Leu fixture not found: $FIXTURE"; exit 1; }
mkdir -p "$OUT/U01"
cp -n "$HERE/results/U01/baseline_U01.json" "$OUT/U01/" 2>/dev/null || true   # compare against the published baseline
cd "$HERE/scripts"
W4="stleu_fig80_rebuild,bar_2light_sexfoil,bar_4light_recursive,intersecting_3light"
U01ALL="stleu_fig80_rebuild,stleu_fig80_ideal,bar_2light_sexfoil,bar_4light_recursive,intersecting_3light"
U05ALL="$W4,rose_12_chassis"
MODE=$([ "$RENDER" = "1" ] && echo render || echo qa)

echo "== U01 construction + topology + plain solids"
"$PY" -I run_U01.py build --specs specs_U01.json --out "$OUT/U01" --fixture "$FIXTURE"
"$PY" -I blender_U01.py "$OUT/U01" "$W4" "$U01ALL" | grep -E "^(BLENDER|stleu|bar_|inter)" | cut -c1-120
[ "$RENDER" = "1" ] && "$PY" -I run_U01.py compose --out "$OUT/U01"

echo "== U02 orders + mouldings"
"$PY" -I run_U02.py build --u01 "$OUT/U01" --out "$OUT/U02"
"$PY" -I blender_U02.py "$OUT/U02" "$W4" "$W4" bar_4light_recursive "$MODE" | grep -E "^BLENDER"
[ "$RENDER" = "1" ] && "$PY" -I run_U02.py compose --out "$OUT/U02"

echo "== U03 masonry jointing"
"$PY" -I run_U03.py build --out "$OUT/U03"
"$PY" -I blender_U02.py "$OUT/U03" "$W4" "$W4" bar_4light_recursive "$MODE" | grep -E "^BLENDER"
[ "$RENDER" = "1" ] && "$PY" -I run_U03.py compose --out "$OUT/U03"

echo "== U04 rose window"
"$PY" -I run_U03.py build --specs specs_U04.json --sections sections_U04.json --joints joints_U04.json --out "$OUT/U04"
"$PY" -I blender_U02.py "$OUT/U04" rose_12_cusped,bar_4light_recursive rose_12_cusped,bar_4light_recursive rose_12_cusped "$MODE" | grep -E "^BLENDER"
[ "$RENDER" = "1" ] && "$PY" -I run_U04.py "$OUT/U04"

echo "== U05 tracery as its own masonry layer"
"$PY" -I run_U03.py build --specs specs_U05.json --sections sections_U05.json --joints joints_U05.json --out "$OUT/U05"
"$PY" -I blender_U02.py "$OUT/U05" bar_2light_sexfoil,bar_4light_recursive,rose_12_chassis "$U05ALL" bar_2light_sexfoil "$MODE" 0.60 1.05 | grep -E "^BLENDER"
[ "$RENDER" = "1" ] && "$PY" -I run_U05.py "$OUT/U05"

echo "== done: outputs in $OUT (each BLENDER line must say all_ok True)"
