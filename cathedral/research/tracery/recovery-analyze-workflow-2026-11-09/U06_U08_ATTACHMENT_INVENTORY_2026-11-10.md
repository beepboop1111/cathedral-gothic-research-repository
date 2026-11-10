# Tracery U06–U08 uploaded-attachment integrity inventory — 2026-11-10

Status: source archives inspected in ChatGPT session; **ZIP payloads are not yet on this GitHub branch**. Do not confuse this inventory with a completed archive upload or a fresh Blender 5.1 validation.

| Archive | SHA-256 | Members | Python files | BLEND | GLB |
|---|---|---:|---:|---:|---:|
| TRACERY_U06_R01_EXPERIMENTAL_HANDOFF(1).zip | 262d31c29f8c1213b371b353385247b3aa694014850b775e92966fbeaf8706da | 70 | 11 | 1 | 8 |
| TRACERY_U07_HEAD_R01_HANDOFF(1).zip | fd44649077f8a3964e604ae2b92107b2ee7926149db64ff29cbbba6c8c67f0f7 | 45 | 15 | 2 | 2 |
| TRACERY_U08_MOULDING_R01_HANDOFF(1).zip | 2d6c16bd34b4b93d6b17e8c4f7e2fe24e60efd4184270a7ec587058e287fff6f | 45 | 14 | 2 | 2 |

The combined recovery bundle TRACERY_U06_U08_RECOVERY_BUNDLE_2026-11-10.zip has SHA-256 c99c43b0c764336ea235dce7cec65a67646f2aa2744331e42de01fd17fb795c2 and contains three source ZIPs plus a JSON manifest.

## Source-derived findings

- U06 parent is the original U01-U05 uploaded ZIP SHA-256 411c740189cab347cd02a6b717a5e6ec9781f64b26d739beaf90975e9e876e7a. U06 QA_SUMMARY records experimental compatibility checks, including a narrow clearance 0.02139172528945378 mm for the intersecting case. Its HANDOFF notes that 5.1+ was not confirmed by the available runtimes.
- U07 parent_sha256 is precisely the U06 ZIP hash above. U07 applies 11 experimental tangent-circle transitions to four previously unseeded head openings, preserves primary arcs, retains 1:1 geometry, reports minimum web 79.76015655010625 mm and symmetry error 0.2785457143496422 mm. Its junction design is not historically approved.
- U08 parent_sha256 is precisely the U07 ZIP hash above. U08 subdivides crossings of inherited piecewise-linear moulding-height surfaces; its HANDOFF reports 20 crossing edges repaired, 40 directional violations reduced to zero, and a connected closed profiled body of 11,022 vertices and 22,068 faces. This is C0 closure, not global tangency nor structural approval.
- U08 keeps masonry stone joints excluded. F5ZL-C support schedule remains unresolved.
- ZIP CRC checks passed for each archive and the combined bundle. No executable, Blender, GLB or structural tests were performed in this inspection.

## Workflow

U01-U05 original -> U06 physical export/QA -> U07 head contour candidate -> U08 moulding surface closure. Preserve the protected geometry and branch history. Upload the exact three binaries without rewriting them, and then verify their hashes and rerun Blender 5.1+ QA before promoting any result.

## Project coordination

User identifies a dedicated control board: https://cathedral-f5zp-control.xblox54.chatgpt.site/#board . The board is noted as a reference only; its current contents and any synchronization interface have not been independently verified.
