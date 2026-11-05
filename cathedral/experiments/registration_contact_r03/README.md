# F5ZP R03 — Start here

**Experimental review only; native numerical scale preserved, physical SI conversion unresolved.**

Read `REPORT.md` for findings and `CHECKPOINT.md` for authority/status. Open `CROSSING_CONTACT_PLANS.png`, `CROSSING_SECTIONS.png` and `CHEVET_REGISTRATION.png` for annotated drawings. SVG companions are editable vector diagrams; their viewboxes are presentation coordinates, not a 1:1 CAD import contract. Exact native station data are in the CSV/JSON files.

Open `F5ZP_Registration_Contact_R03.blend` in Blender 5.0.1 or compatible. It has separate selected R05, saved G40 fragments and chevet-guide collections, plus crossing aerial, crossing plan and chevet plan cameras. `F5ZP_Registration_Contact_R03.glb` is an alternative native-magnitude scene using glTF Y-up. Its numbers must not be interpreted as calibrated physical metres. No STL was requested.

The original R05 blend/GLB and source decisions are retained in `inputs/`. No source files are overwritten. The original R05 infill top 4392 and upper-core placeholders are preserved; this study does not complete detailed bearings or missing wall solids.

Reproduce the local audit:

```bash
python -m pip install -r requirements.txt
python scripts/analyze.py
python scripts/verify.py
```

Installed package versions are in `ANALYSIS_VERSIONS.json`. The full analysis uses the captured world-geometry snapshot in `inputs/MR_meshes.json.gz`, so it does not require MR COMPUTER access. Re-running writes the derived review outputs within this experimental package only.

To repeat the read-only live probes on MR COMPUTER, run `recover_inventory_blender.py`, then `recover_meshes_blender.py` with `blender -b --python SCRIPT`. Those scripts read the recorded absolute paths and write `/tmp/F5ZP_R03_RECOVERY` only. `build_editable_blender.py` uses those snapshots and the original handoff archive in Downloads, then writes the separate Desktop R03 experimental directory. `verify_editable_blender.py` reopens and compares world geometry; it does not save source files.

The GitHub branch versions the checkpoint, report, numerical results and scripts. The complete review ZIP also carries captured inputs, source R05, editable models and previews. No experimental geometry is promoted.
