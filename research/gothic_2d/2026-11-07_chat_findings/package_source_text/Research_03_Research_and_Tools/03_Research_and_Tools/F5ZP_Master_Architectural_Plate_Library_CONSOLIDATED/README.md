# F5ZP MASTER ARCHITECTURAL PLATE LIBRARY - Consolidated edition

Built: 2026-11-03. This package consolidates the **actual raw contents** of the earlier Gothic handoff ZIP and the uploaded Phase2 working package.

## Open here

- `F5ZP_Master_Plate_Library_CONSOLIDATED.xlsx` - master workbook and review controls.
- `reports/F5ZP_Master_Library_Consolidation_Report.pdf` - source-backed coverage, issues, and outstanding review.
- `catalogue/MASTER_PAGES.csv` - exactly one row per indexed atlas page, including 10 Phase2 additions.
- `catalogue/MASTER_CLAIMS.csv` - 1,549 normalized claims, with figure/plate/page-level distinction.
- `catalogue/PHASE2_CROSSWALK.csv` - all 89 earlier Phase2 records and their mappings.
- `catalogue/RESEARCH_ISSUES.csv` - open verification items and specific page misclassifications.
- `catalogue/F5ZP_Master_Plate_Library.sqlite` - queryable catalogue for cross-referencing.
- `catalogue/SCRIPT_TO_CLAIM_INDEX.csv` - 4,488 *candidate* script links, not tested geometry.
- `catalogue/PRIORITY_REVIEW_QUEUE.csv` - 140 next-to-check candidates.
- `atlases/` - all 20 original selected-page atlases unchanged, plus 10 original pages in an addendum, plus a smaller curated cross-source browse atlas.
- `catalogue/CURATED_VIEW_ATLAS_MAP.csv` - exact source and atlas references for the curated browse atlas.
- `reference/original_handoff_registers/` - exact, unmodified original source-specific CSV registers for audit.

## Reading the counts

20 original source atlases contain 1,439 selections; a 10-page Phase2 addendum increases the source-page index to **1,449**. The curated browse atlas is just a *view* onto these pages and is not counted as new source evidence. The 1,590 historical staging rows normalize to **1,549** claims by resolving 41 overlap/repeated-claim groups. Of the 1,549, **672** are distinct Choisy captioned figure references, **286** numbered-plate claims, **98** geometric leaves with uncertain original labels, **492** illustrated-page candidates and **1** supporting-text reference. These are not 1,549 verified geometry assets.

For Phase2, **86 of 89 seed rows** map to an original source page or numbered Worringer plate. The three unlinked Hay designations remain unresolved. Ten supplementary original pages have been added, including two that were initially misclassified as Gothic source content: Choisy II, p.370 is tower sections and p.410 is Italian Renaissance.

## Source authority rules

- Pages are **1-based PDF page numbers**; book printed pagination is separate and may be unknown.
- Original PDFs / historical artwork are not edited. The 20 source atlases in this ZIP are byte-for-byte copies of the previous handoff sources.
- Figure caption references may be recoverable from book text even when an image crop has *not* been visually validated.
- A drawing, photograph or axonometric illustration does not automatically constitute measurable geometry.
- F5ZP cathedral design geometry, dimensions, scripts, original modelling files and 1:1 scaling are **unchanged**. F5ZK-C and F5ZN-A remain architectural authorities.
- Hay is correctly titled David Ramsay Hay, *First Principles of Symmetrical Beauty*, not a Hayward Gothic construction treatise.
- Ungewitter/Mohrmann Vol I scan uses the 1901 edition; Vol II the 1892 edition. Do not interchange historical plate numbering.

## Audit/query example

```sql
SELECT claim_id, source_key, original_pdf_page, figure_or_plate, caption_or_subject,
       atlas_file, atlas_page
FROM claims
WHERE recommended_scripts LIKE '%sweep2schem.py%'
ORDER BY source_key, CAST(original_pdf_page AS INTEGER);
```

## Not yet complete

The source book *figure-level visual* survey is not exhaustive, especially for German, Viollet-le-Duc and Parker books. Individual figure crops, dimensional evidence, tracing quality, profile/sweep readiness, duplicate artwork across different historical sources, and Hay's 98-versus-100 plate discrepancy remain open. Consult `catalogue/RESEARCH_ISSUES.csv` and the report.
