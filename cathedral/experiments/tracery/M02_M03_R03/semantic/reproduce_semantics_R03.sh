#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
for name in meaux haina_1264 haina_1265 chalons; do
    "${PYTHON:-python3}" semantic/tracery_semantics_R03.py "baseline/maps/${name}_map.png" \
        --out-dir "semantic/${name}" --family "$name"
done
"${PYTHON:-python3}" semantic/test_semantics_R03.py -v > semantic/unit_tests_R03.log 2>&1
"${PYTHON:-python3}" semantic/test_semantics_R03.py --benchmarks
"${PYTHON:-python3}" semantic/validate_semantic_exports_R03.py
