# Reims windows through U06 (centreline mode)

Source data: Archaeology Data Service, *Windows on the Past* (John Hillson), collection `arch-7332-1`
(survey traces `window_trace_*`, design drawings `window_design_process_*`). **The dataset licence has not
been confirmed.** The ADS images are NOT in this repo; only numbers derived from them (fits, Hillson's
printed dimensions, presets). Check the licence before any wider reuse.

- `reims_half1_review.png`: choir, chevet chapels, transepts: 7 presets from 19 traces.
- `reims_half2_review.png`: nave aisles N11-N19, clerestory C10-C19 n/s, transept N10.2.w / S10.2.w / S10.2.s: 17 presets from 32 traces.
- `fits/`: per-window circle fits, general-rule fits, survey vs Hillson tables.
- `qa/`: U01/U02/U03 QA results for every preset.
- `scripts/`: marker extraction, grouping, rule fits (`icp_gen.py` = direct fit seeded from good windows), preset writers.
  These were run from a scratch folder; paths inside them point at that layout (data in `/home/claude/data/ads_wotp/`).

Presets: `../scripts/specs_U06_reims_half{1,2}.json` (+ sections/joints). Bar widths, sill, depth are TRIAL values.

U03 joint options added (all opt-in, default off, regression IDENTICAL): `free_right`, `ring_dense`, `sill_split`,
`frame_zone_joints`, `ring_zone_joints` (ring joints cut through the bar shared with the main arch: C18n, C19n, C19s;
the junction keep-out check fails there by design). Half 1 and 2 use `keepout_factor` 0.

Open: C16s-C17s 14 mm^2 U02 residual; C18s U02 order-1 triangulation; outer order arch of N10.2.w / S10.2.w not modelled.
Structural validation not done.
