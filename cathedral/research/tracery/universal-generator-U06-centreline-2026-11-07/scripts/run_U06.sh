#!/usr/bin/env bash
# Rebuild U06 from scratch: U01 -> U02 -> U03 (+ regression models), Blender checks, one review PNG.
# Run from anywhere:  bash run_U06.sh
set -euo pipefail
cd "$(dirname "$0")"
PY=python3
U15=$(realpath ../../universal-generator-U01-U05-2026-11-07/scripts)
FIX=$(realpath ../../early-fig80-study-2026-11-04/MR_COMPUTER_R03_REPRODUCTION/StLeu_R03_PLAIN_UPRIGHT.stl)
OUT=$(realpath -m ../out)
R6=reims_n53n_hillson_figure,reims_c1e_hillson_fit,reims_c1e_survey
ALL1=stleu_fig80_rebuild,stleu_fig80_ideal,bar_2light_sexfoil,bar_4light_recursive,intersecting_3light,$R6
rm -rf "$OUT"
"$PY" -I run_U06.py --out "$OUT" --fixture "$FIX" | grep -E "^==|regression|FAIL" || true
"$PY" -I "$U15/blender_U01.py" "$OUT/U01" "$R6" "$ALL1" | grep -E "^BLENDER"
"$PY" -I "$U15/blender_U02.py" "$OUT/U03" "$R6" "bar_2light_sexfoil,$R6" reims_c1e_hillson_fit | grep -E "^BLENDER"
"$PY" -I compose_U06.py "$OUT" "$(realpath ..)/U06_review.png"
