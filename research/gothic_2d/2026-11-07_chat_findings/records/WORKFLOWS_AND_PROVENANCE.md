# Gothic 2D — consolidated PNG workflows and available scripts R01

**Status:** archival research record for review, NOT a geometrically validated or approved generator release.

## What is preserved

This archive indexes **every distinct top-level PNG that was accessible for the illustrated sequence in this conversation** (see `PNG_REGISTER.csv` and `PNG_CONTACT_SHEET.png`), including your original historical crops and the later image-generated architectural concepts. File bytes and names are preserved; each receives a non-destructive prefixed archive filename. The original ZIP packages for already-existing traced studies, including the V01 tracing pipeline, have also been preserved. These packages include additional historical PNGs, SVGs and validations that are **not** relabeled as part of the image-generation sequence.

## Critical honesty about scripts

**The ChatGPT-generated PNG designs were produced by image generation. No reconstructible Python, SVG, CAD or V08 geometry script generated the original PNGs.** The image-generation process does not provide a runnable construction script, exact radii, true arc definitions or numeric tracing error. Do not promote those visuals as verified geometric traces. The available Python tools below were developed independently for plate tracing, color/ink extraction and vectorization, or for V08 analytic geometry and prior project work. They are bundled for future testing, not falsely credited as having produced each illustration.

## Sequence of workflows

| No. | Historical input or task | Output/process | Tool actually used | Status |
|---|---|---|---|---|
| 01 | Quatrefoil with standard drawing conventions | symmetric_quadrifoil_construction_diagram.png | ChatGPT image generation | Illustrative, unmeasured |
| 02 | Octafoil with outer ring | symmetric_octafoil_construction_diagram.png | ChatGPT image generation | Illustrative, unmeasured |
| 03 | Sexfoil with outer ring | a_clean_black_line_geometric_diagram_on_white_back.png | ChatGPT image generation | Illustrative, unmeasured |
| 04 | Pointed arch over sexfoil | a_clean_technical_black_and_white_line_drawing_wit.png | ChatGPT image generation | Illustrative, unmeasured |
| 05 | Pointed arch over octafoil | a_precise_black_and_white_line_drawing_with_constr.png | ChatGPT image generation | Illustrative, unmeasured |
| 06 | Ungewitter Plate CXVIII page source | lehrbuchdergotis02unge_0283(1).png | Original user supplied | Source evidence |
| 07 | Figure 1207 group black-only variant (first delivered file with reused name) | gothic_trefoil_arch_tracery.png | ChatGPT image generation | Illustrative, unmeasured |
| 08 | Figure 1207c black-only variant | gothic_trefoil_arch_tracery_drawing.png | ChatGPT image generation | Illustrative, unmeasured |
| 09 | Original figure 1207 black-only image | gothic_trefoil_arch_tracery_motif.png | ChatGPT image generation | Illustrative, unmeasured |
| 10 | Figure 1207 black-only variation, overwritten filename in conversation | imagegen.png | ChatGPT image generation | Illustrative, unmeasured |
| 11 | Historical Gothic window source with sexfoil and pointed arch | 1264 Hiana.png | Original user supplied | Source evidence |
| 12 | Haina figure, black tracing-style interpretation | a_clean_black_and_white_line_art_architectural_tra.png | ChatGPT image generation | Illustrative, unmeasured |
| 13 | Trefoil in pointed arch (first version) | a_clean_black_and_white_vector_line_drawing_of_a_g.png | ChatGPT image generation | Illustrative, unmeasured |
| 14 | Trefoil in circular ring, no pointed arch | a_clean_black_line_tracery_drawing_of_a_large_circ.png | ChatGPT image generation | Illustrative, unmeasured |
| 15 | Second complex Gothic window cropped source with repeated sexfoils | Pasted image.png | Original user supplied | Source evidence |
| 16 | Second complex Gothic window tracing-style interpretation | a_crisp_black_and_white_line_drawing_vector_like.png | ChatGPT image generation | Illustrative, unmeasured |

## Previously created *real* tracing/script workflows included

- `Gothic_2D_Tracing_Workflow_V01.zip`: `trace_plates.py` extracts ink edges and produces tracing SVGs; `fit_arcs.py` fits circles to **explicitly measured source points**; `four_circle_analysis.py` is a separate candidate analysis; `test_workflow.py` verifies functionality. Covers 1193–1198, 1236, trefoil/quatrefoil references, four-circle study. Its composite 1193–1198 reference is image-generated, not an original Ungewitter plate.
- `Ungewitter_CXVIII_WHOLE_PAGE_R02_FOR_REVIEW.zip`: `build_cxviii_whole_page.py` performs a whole-page ink vectorization; it preserves printed ink and may add separate visual gray axes. Not compass-center recovery.
- `Gothic_2D_Face_Test_R02.zip`: `build_gothic_svg_test.py` tests selectable face regions in an SVG trace; experimental, not used for image-generated drafts.
- `Gothic_2D_Depth_Workflow_R01_FOR_REVIEW.zip`: `depth_classify.py` is an experimental classification pipeline. Its 2D/3D depth interpretation is not part of the approved 2D vector tracing baseline.
- `Gothic_V08_Project_Integration_ready.zip`: plate reader, circle fits and potential radial transforms, plus 3D tools (not executed to make generated PNGs). Supplied V08 previews do not automatically replace cathedral generators.
- `Gothic_Tracery_New_Chat_Handoff_2026-11-04(2).zip`: prior research handoff including Ungewitter 1193, 1236, sexfoil method, Paynter geometry research, and V08 modules.

`SCRIPT_REGISTER.csv` states where each existing script was found. The package also contains your attached architectural Python scripts in `EXISTING_SCRIPTS/Additional_Existing/` for preservation. These are not proposed changes to the original cathedral scripts.

## Repeatable method for **future** approved tracings

1. Identify the exact original source drawing and preserve its original bytes with SHA-256 provenance.
2. Log every crop and its original source image coordinates. Never use an image-generated composite as proof of historical design geometry.
3. Extract/clean raster ink only in an experimental layer. Preserve historical lettering and construction marks separately.
4. Identify which visible strokes are architecture, construction axes, and uncertain relationships.
5. Recover mathematically true circles and arc segments from measured ink point samples where evidence permits; record centers, radii, endpoints, residuals and tangency checks.
6. Draw black visible outlines; thin light-gray dashed axes; red dashed uncertain hypotheses; black dotted complete construction circles where helpful.
7. Deliver **whole-page black-outline SVG/PNG plus overlay and numerical QA**, rather than a collection of disconnected crops when a whole-page drawing is requested.
8. Ask for user approval. **Only approved scripts and workflows** may become locked project working baselines; preserve previous versions and leave all locked cathedral geometry untouched.

## Known limitations

Some of the multiple images generated with the same display filename (`imagegen.png`, `gothic_trefoil_arch_tracery.png`) were overwritten on the accessible filesystem. This archive preserves the specific files that are presently accessible, not inaccessible overwritten variants. For these, figure identification can be uncertain. The underlying image-generation prompts are summarized by the conversation; no exact runnable model invocation is claimed.

Do not use this package as a calibrated 1:1 drawing or to generate cathedral parts without an explicit geometric reconstruction and approval.
