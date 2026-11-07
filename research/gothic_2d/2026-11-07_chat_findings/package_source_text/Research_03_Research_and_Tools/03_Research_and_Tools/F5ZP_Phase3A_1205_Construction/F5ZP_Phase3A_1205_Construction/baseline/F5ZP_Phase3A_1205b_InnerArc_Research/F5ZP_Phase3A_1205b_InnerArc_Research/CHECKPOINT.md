# F5ZP Phase 3A / CXVIII / 1205b — continuation checkpoint

Date: 2026-11-03. Status: EXPERIMENTAL RESEARCH, not user-approved architectural geometry.

## Baseline and lineage

Parent: attached `F5ZP_Phase3A_CXVIII_1205b_NEW_CHAT_HANDOFF(1).zip`, Library file `libfile_27587d8ae9608191a8f4c03066efd514`. Complete unchanged contents are retained in `source_handoff/`; original checksums are in its `MANIFEST_SHA256.json`.

Source: Ungewitter–Mohrmann Volume II (1892), original PDF page 281, Plate CXVIII, figure 1205b. Source-book hash and pixel-exact crop registration are recorded in `derived/source_pdf_verification.json`. No source or existing tool was edited.

## Scale and conventions

- Architectural scale: UNRESOLVED; no physical length calibration supplied.
- Output: original 144-DPI crop pixel coordinates; not mm, Minecraft blocks or 1:1 architectural units.
- Origin: center of first crop pixel, index (0,0); X right, Y down.
- Angles: degrees clockwise from +X.
- Crop to page: add (114,239).
- 432-DPI derivative index to crop: (index − 1)/3, respecting pixel centers.
- No 3D, elevations, sections, stone depth, opening mask or masonry assignment.

## Decision ledger

| Item | Value / scope | Status | Authority |
|---|---|---|---|
| Source drawings, cathedral geometry, dimensions, existing generators | Preserve unchanged | LOCKED for this task | User's explicit instruction |
| Outer reference center | (109.21742236738913,111.23955699522183) crop px | Inherited validated conditional fit; fixed reference | Parent measurements.json |
| Outer reference radius | 93.51694870364518 px | Inherited validated conditional fit; fixed reference | Parent measurements.json |
| Inner segmentation | N, E_upper, E_lower, S, W_lower, W_upper | EXPERIMENTAL | Measured stroke fits |
| Centers, radii, arc spans | Exact values in derived/geometry.json | DERIVED, unapproved candidate | V08 circle_fit and new isolated wrapper |
| Upper cusp candidates | NW (68.2764862991,69.7101323820); NE (151.0280643645,70.4335359962) px | DERIVED | Adjacent fitted-circle intersections |
| Lower joins | Supporting-circle gaps W 8.6174521279, E 9.2190658337 px | DERIVED; do not close | Independent fitted circles |
| Side upper/lower join discrepancies | West 0.8701079638, east 0.5822855331 px | UNRESOLVED at ink scale | Independent fits, not snapped |
| Fine construction arcs and a/b/c identity | Not assigned as verified centers or contour | UNRESOLVED | Explanatory source text not checked |
| Historical intent | Possible comparison of different radius/construction alternatives | EXPERIMENTAL interpretation | Drawing only; not verified from text |

## Authorized delta and verification

The single delta was reconstructing the inner motif as isolated image geometry. No cathedral generator defaults, locks, profiles, piers, vaults or models were changed. New wrappers are confined to `scripts/`; supplied V08 and preprocessing files remain unchanged.

Six independent arcs explain the seeded raw sample set at RMS 0.204514 px, versus 0.667018 px for four circles. Retained per-arc RMS is 0.120–0.162 px. All 11 V08 tests pass. SVG arc radius/endpoint round-trip checks pass; SVG was rendered and visually inspected. Source checksum audit passes. Threshold and angular-block holdout evidence is included; residuals remain conditional on manually selected stroke neighborhoods. Read `REPORT.md` for limitations before using the numbers.

The final export preserves separate paths and open lower ends. No STL is authorized by this research result alone. The SVG display size does not calibrate physical scale. No generated candidate has become APPROVED or LOCKED architectural geometry.

## Fresh-chat instructions

Read `REPORT.md`, `derived/geometry.json`, `derived/validation.json` and this checkpoint. Open `research_report.html` for the offline illustrated report. Preserve the inherited outer circle and this measured six-arc candidate. Continue only on figure 1205b until its construction interpretation is resolved.

Next bounded task: find and translate the explanatory text for figure 1205b, identify the a/b/c construction alternatives, and create separately named constrained comparison variants if supported. Keep measurements separate from historical idealization. Do not invent the lower cusps, force fourfold symmetry, infer physical scale, change the baseline outer circle, or integrate research values into cathedral generators.

Reproduce with `python scripts/reconstruct.py`, then `python scripts/make_report.py`. Optionally recreate the source derivatives first with `python scripts/render_source.py /path/to/lehrbuchdergotis02unge.pdf`. The matching full book is in the Research project; original plate and higher-resolution derivative are bundled here.
