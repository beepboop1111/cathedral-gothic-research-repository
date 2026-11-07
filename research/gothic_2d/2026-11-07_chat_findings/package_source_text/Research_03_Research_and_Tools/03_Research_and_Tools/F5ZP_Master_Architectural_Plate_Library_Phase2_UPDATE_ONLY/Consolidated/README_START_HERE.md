# Cathedral F5ZP — Master Architectural Plate Library, Phase 2 consolidation

**Date:** 2026-11-03  
**Status:** Source-package integrity verified; page-level catalogue completed; figure-level review still provisional.  
**Architecture:** Research/reference only. No existing F5ZP plans, locked dimensions, script code, STL, or schematic geometry changed.

## Summary

This consolidation starts from the user-provided `Gothic_Master_Architectural_Plate_Library_HANDOFF(1).zip`, not from earlier conversation summaries. It validates the original 37 archive files listed in `FILE_MANIFEST.csv` by SHA-256. The original handoff has 20 PDF atlases, 16 CSV registers, and its own manifests/instructions. Its 1,590 preliminary entries represent a mixture of *historical figure references, whole plate selections, illustration-page candidates, and duplicate research passes*.

The new `Catalogues/Master_Source_Page_Index_1439.csv` enumerates **all 1,439 pages across 20 original atlases**, including 1,417 illustrated source pages represented in staging and 22 supplemental pages (21 Fawcett figure-key leaves and Worringer's frontispiece). One separate Ungewitter supporting text page remains outside the illustrated atlases by design. There are 1,418 unique original source+PDF-page pairs among the 1,590 selections.

The new `Catalogues/Historical_Figure_and_Plate_Leads.csv` has **824 labeled figure/plate leads**, mainly Choisy and original numbered plate sets. These are NOT independently cropped or verified generator-ready silhouettes. Source photo/perspective views must not be mistaken for measurable geometrical drawings.

## Most important correction

Viollet-le-Duc, Tome IX, *VOÛTE*, **Figure 26** (Notre-Dame de Paris ambulatory) is on **original PDF page 522, printed page 512, merged Volume IX atlas page 20**. Previous handoff metadata incorrectly gave original PDF page 532 / atlas 21, which in fact shows Figure 33. The original staging CSV is preserved as an audit trail; corrected locations occur in the derived indexes, shortlist and QA report.

## Contents of NEW derived files

- `Catalogues/F5ZP_Master_Plate_Library_Phase2_Consolidated.xlsx` — searchable, filterable workbook. Sheets: Read Me, Source Pages, Figure Leads, Script Shortlist, Audit Findings, Same Page Overlaps, Original Selections, Source Coverage.
- `Catalogues/Master_Source_Page_Index_1439.csv` — stable ID per included illustrated atlas page, original PDF locator, inherited labels, status, preservation and scale caveats.
- `Catalogues/Historical_Figure_and_Plate_Leads.csv` — stable IDs for indexed historical labels, without pretending every subfigure was individually traced.
- `Catalogues/Selection_Register_1590_Normalized.csv` — original entries normalized by source identity; original metadata preserved in fields.
- `Catalogues/Same_Source_Page_Overlaps.csv` — 165 source/page overlap groups, not assumed image duplicates.
- `Catalogues/Cross_Source_Subject_Comparison_Leads.csv` — analogous subjects needing manual assessment; explicitly no proven duplicate identities.
- `Catalogues/Six_Generator_Reference_Shortlist.csv` — first-review plates for the six named generator scripts, without permission for geometry creation.
- `Catalogues/Priority_Atlas_Page_Map.csv` — source locators for 22 originals copied into a short review PDF.
- `QA/Original_Archive_SHA256_Verification.csv` — all 37 manifest files matched bytes and SHA-256.
- `QA/Verification_Issues_and_Targeted_Passes.csv` — 11 remaining audit topics.
- `QA/Consolidation_Metrics.json` — reproducible summary counts.
- `Reports/F5ZP_Master_Plate_Library_Consolidation_Report.pdf` — illustrated-reference research guidance and verification report.
- `Atlases/F5ZP_22_Original_Source_Pages_Priority_Atlas.pdf` — 22 source pages inserted into a new indexed PDF without altering the original page images; the original page numbers are in the accompanying CSV.
- `Atlases/F5ZP_Priority_Visual_Contact_Sheets.pdf` — quick thumbnails for navigating priority plates.

## Complete archive versus update-only archive

- `F5ZP_Master_Architectural_Plate_Library_Phase2_COMPLETE.zip` includes all 20 original illustrated PDF atlases and original 16 CSV registers unchanged **plus** the derived files above.
- `F5ZP_Master_Architectural_Plate_Library_Phase2_UPDATE_ONLY.zip` contains only this new consolidation and review documents. Keep the original handoff ZIP alongside it for the historical source illustrations.

## Research integrity rules

1. `source_pdf_page` and `atlas_page` are both **1-based**; `printed_page` must not be inferred where uncertain.
2. Multiple figures on one page remain distinct in future subfigure cataloguing. A repeated source page does not automatically equal a duplicate historical drawing.
3. Figure labels, captions, dimensions, drawing boundaries and source edition must be verified against original images before extraction or profile use.
4. Keep original color and construction lines and original PDF artwork unchanged; derivative masks must be separate files.
5. All geometry tags and script recommendations inherited from automated/previous registers remain **candidates**, not certifications.
6. The actual cathedral remains at 1:1 scale with independently approved F5ZK-C / F5ZN-A design dimensions. No historical drawing sets cathedral dimensions by itself.
