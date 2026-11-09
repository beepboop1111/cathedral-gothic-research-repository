# R52 Quick runbook

Location:
/home/christopher/Cathedral_Research/R52_universal_2d_engine_handoff/

Run under system Python:
    python3 R52_2d_only_regression.py

Requirements: numpy, scipy, shapely, trimesh, Pillow. U01 imports Triangle for 3D cap meshing; when unavailable, R52 creates a harmless import placeholder strictly for 2D Model(spec) execution. NEVER call U01 solids(), U02-U05 or GLB export through this placeholder.

Expected signature: R52_2D_REGRESSION_PASS, fixtures 5, checks 116, negative_cases 3.

Output: outputs/R52_2D_REGRESSION_QA.json, five construction SVGs and one single review PNG.

Read HANDOFF.md (main authority), SOURCE_PROVENANCE.md (evidence), QA_ACCEPTANCE_MATRIX.md (testing), ENGINE_CONTRACT.json (target R53), NEXT_PASS_ROADMAP.md (next steps).

Do not regenerate approved cathedral geometry or the four repaired M02/M03 windows. Do not invoke GitHub. Separate 2D geometry confidence from historical and structural validity.

When eventually launching Blender for a downstream 3D test, load the user's /home/christopher/tab.py keymap, verify active keyconfig, and avoid global preference changes. Blender is NOT required for 2D R52.
