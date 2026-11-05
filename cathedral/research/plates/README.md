# Cathedral historical plate catalog — R01

**Reference organization only. Original images, working tracery, generators and approved cathedral geometry are unchanged.**

This catalog is ready for the next uploaded book-plate batch. Its seed is the recovered **existing** consolidated research catalog: **1,449 indexed atlas-page records, 1,549 research claims, 19 source keys**. These are different record types, not 1,549 individually verified historical geometry assets. Existing page and claim IDs are preserved.

## Open here

| Need | File |
|---|---|
| Find book/source and coverage | [SOURCE_COVERAGE.csv](inherited_consolidated/catalogue/SOURCE_COVERAGE.csv) |
| Find historical page, printed page, plate and atlas location | [MASTER_PAGES.csv](inherited_consolidated/catalogue/MASTER_PAGES.csv) |
| Find figure/subject, source claim and prior tracing leads | [MASTER_CLAIMS.csv](inherited_consolidated/catalogue/MASTER_CLAIMS.csv) |
| Retain unresolved historical issues | [RESEARCH_ISSUES.csv](inherited_consolidated/catalogue/RESEARCH_ISSUES.csv) |
| See the prior catalog's scope and limits | [Recovered README](inherited_consolidated/README.md) |
| Locate exact available source files by checksum | [Batch manifests](batches/) |
| Confirm current intake / GitHub storage status | [CATALOG_STATUS_R01.json](CATALOG_STATUS_R01.json) |
| Register another batch without editing images | [Intake script](tools/index_plate_batch_R01.py) |

## Low-interruption workflow

1. Supply plates as an ordinary ZIP, folder or individual file. Keep original grayscale/color scans and original filenames. Book title, edition, volume and page/plate/figure labels help when known; unknown fields stay unresolved.
2. Index the batch once. Every original occurrence gets its filename, SHA-256, file size and image header. Exact byte duplicates share an asset ID, but differing scans of the same drawing remain separate. No images are extracted, renamed, mirrored, thresholded, compressed or resized by the intake script.
3. Associate source metadata and existing page/claim IDs as evidence becomes available. PDF page index, printed book page, plate number and figure number are separate fields. Source acquisition and full-resolution storage are recorded independently from historical validation.
4. Open only the needed source pages for active work. Keep crops, grayscale cleanup, measured SVGs, comparison overlays and 3D results versioned separately, linked back to the original asset ID. Adding a batch never regenerates a model.

The current intake manifests index **254 available image/PDF/SVG/archive file occurrences** from the two already attached research archives. These include source pages, atlases, contact sheets and prior derivatives; they are not 254 newly received plates or automatically approved originals. Nested archives are listed, not recursively expanded.

## Original bytes and large-file storage

The full-resolution binary originals remain in the named, hash-identified project source archives. **This GitHub commit stores catalogs, provenance and intake code; it does not claim those binary originals were uploaded to GitHub.** The incoming large set has not yet appeared in this session's attachment list.

For future binary hosting, Git LFS or release/source-archive links keep high-resolution scans out of ordinary Git history. Use the route supported by the actual connected upload capability when the batch is available. LFS is **not activated by this setup**; never commit stand-alone LFS pointers unless their corresponding objects have actually uploaded and been retrieved successfully. No repository LFS settings, billing settings or existing `.gitattributes` are changed here.

GitHub documentation: [large files](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github), [Git LFS](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage).

## Intake command

```bash
python3 tools/index_plate_batch_R01.py /path/to/book_plates.zip \
  --batch BOOK_PLATES_R01 --out batches/BOOK_PLATES_R01 \
  --origin-json /path/to/batch_origin.json \
  --metadata-json /path/to/optional_known_metadata.json
```

`--origin-json` and `--metadata-json` are optional. The output directory must be new and outside an original input folder. The script uses Python's standard library; Pillow supplies optional image-header dimensions/mode. It performs no remote write or network call. See `INTAKE_EXAMPLES_R01.json` for field examples. Preserve unresolved bibliographic fields rather than deriving them from a generic filename.

## Recovery and preservation

Nine inherited catalog files were recovered **byte-for-byte** from `Research_03_Research_and_Tools.zip`; `RECOVERY_PROVENANCE_R01.json` records exact entries and hashes. Original claims such as “visually inspected” remain inherited statements, not new inspection claims. Historical source PDFs and original artwork are not changed. Meaux R03 and M03 semantic records remain as previously delivered; the next source tracing can link to this catalog without replacing them.

No cathedral dimensions, F5ZK-C/F5ZN-A architecture, ambulatory generator or Pass6J record is modified. F5ZL-C's missing support schedule remains unresolved. An image in this catalog does not establish architectural scale, approval, historic compass construction or structural validity.
