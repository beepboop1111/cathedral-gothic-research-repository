# Gothic 2D Depth/Opening Workflow — R01 (for review)

Read `WORKFLOW.md` for the complete lessons, provenance distinctions, production stages and limitations.

Files:
- `depth_classify.py`: real, runnable seed-based raster region-classification script; it does NOT claim to be the script behind previous image-generated results.
- `example_seeds.json`: editable seed coordinates and semantic color palette.
- `experimental_black_line_source.png`: retained unmodified black-line generated study for test input.
- `example_preview.png`: partial proof-of-function; not a fully classified architectural drawing.
- `example_preview.qa.json`: diagnostics.
- `SHA256_MANIFEST.tsv`: byte-level integrity of inputs/results.

Use `python depth_classify.py experimental_black_line_source.png example_seeds.json --out new.png`.
Dependencies: Pillow numpy scipy. No modification to original drawings or cathedral files.
