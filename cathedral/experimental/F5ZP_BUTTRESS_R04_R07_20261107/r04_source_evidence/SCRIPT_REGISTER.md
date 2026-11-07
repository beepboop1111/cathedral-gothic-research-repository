# Scripts used

| Script | Purpose | Stage |
|---|---|---|
| historical/Simple_Flying_Buttress_Generator_R01.zip → flying_buttress.py | Circular flyer, pier, plinth, wall, repetition and GLB/Blender exports | Original R01 |
| Same ZIP → verify_and_preview.py | Rebuild, preservation, invalid settings, repeats, saved-model and export bounds tests, preview | Original R01 |
| historical/Simple_Flying_Buttress_R02_Tracery_and_Tower.zip → flying_buttress_r02.py | Boolean pierced panel, tower and pinnacle | Original R02 |
| Same ZIP → base_r01.py | Shared R01 geometry implementation | Original R02 |
| Same ZIP → verify_preview.py | Original R02 feature/holes/repeat/export tests | Original R02 |
| current/base_r01.py | Unchanged shared geometric base | Current |
| current/flying_buttress_r02.py | All subsequent modular, R03 and plate-study code | Current |
| tests/test_modular.py | Actual modular combined test/PNG runner; portable paths | Modular stage |
| tests/test_research_system.py | Actual three-variant combined test and matched-scale PNG runner; portable paths | R03 |
| tests/test_plate_892.py | Actual plate fit/mesh test and source-overlay/model PNG runner; portable paths | Plate study |
| sources/make_comparison.py | Earlier historical comparison research script; not used to generate the buttress mesh | Research context |

Temporary code-insertion fragments were merged into the current generator; they are not independent runtime dependencies. Packaging and transfer utilities do not generate geometry and are not part of the modelling workflow.
