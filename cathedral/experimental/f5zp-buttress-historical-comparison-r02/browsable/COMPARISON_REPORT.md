# F5ZP M01 — historical receiving-pier and flying-buttress comparison R02

**2026-11-05 · EXPERIMENTAL RESEARCH / M01 OPEN · NO MODEL MODIFICATIONS**

## Baseline recovery

- GitHub `beepboop1111/cathedral-gothic-research-repository`, branch `cathedral/governance-r01`, `cathedral/governance/CATHEDRAL_MASTER_REFERENCE.md` read successfully, blob SHA `1d7e358ff7562fcc64088854baa2abd3d31a729e` (provisional governance, not design authority).
- MR COMPUTER online; read saved `F5ZP_M01_R21_Architectural_Integration_EXPERIMENTAL/F5ZP_M01_R21_EXPERIMENTAL/R21_ARCHITECTURAL_REVIEW.md`, `R21_DECISION_LEDGER.json`, `R21_OUTER_CONTACTS.json`, `R21_MILESTONE_GATE_MATRIX.csv` in Downloads. These are **saved QA reports**, not independently rerun collision tests in this R02 research pass.
- R21 source identifies protected native F5ZN-A model at `/home/christopher/Desktop/newgen_F5ZN_A_CHEVET_STUDY_1to1.blend`, SHA-256 `d5ef438c269c99dc27052d26a1885f7965065d52ea51162cca4329d4419174bc`; native V03 `/home/christopher/Desktop/F5ZP_M01_R15_R20_EXPERIMENTAL_20261105/F5ZP_M01_R15_R20_EXPERIMENTAL_V03.blend`, SHA-256 `c1273df02f4a0c6d7db100169b184bef76227c6e0d1df1400951fc22d7fa6527`. These hashes are **reported by the R21 checkpoint**, not recomputed in this R02 pass.
- No `.blend`, generator, protected geometry or reference source was written to or modified in this comparison. Historic discarded outer ring remains discarded. Missing F5ZL-C receiving-support schedule remains unresolved.

## Read-only source evidence

Both original uploaded ZIP archives and R01 plate inventory were read without changing their contents. Nine selected original PNG page renders are preserved in `sources/` with their original basenames; `SOURCE_REGISTER.csv` in the package records their SHA-256 values and original archive paths. Historical page descriptions derive from the accompanying `INDEX.txt` text in the original archives. The paired visual sheet is for comparison, **not** an analytically digitized historical drawing.

The most directly applicable source is Viollet-le-Duc IV p309, fig. 15: radial apse and chapel relationships. The buttress-pier plan in IV p313, fig. 18 and the flyer-receiver plan in I p097, fig. 60 show different ways of organizing receiving masonry. Ungewitter I p219 (Plate XXXVI) displays wall and buttress plan/elevation studies. Ungewitter II p109 (Plate LXXXVII) concerns intermediate flyer piers and a calculation; II p087 (Plate LXXXIV) and p093 (Plate LXXXV) illustrate flyer shapes and sections. Viollet-le-Duc I p098, fig. 61 supplies a two-tier flyer reference; IV p192, fig. 101 examines the thrust meeting the vault. These form precedents, not evidence of F5ZP dimensions, connections or strength.

## Comparison with the actually saved R21 junction

| Question | R21 candidate A | R21 candidate B | Result of historical comparison |
|---|---|---|---|
| Companion chapel stations | 70°, 110°; axial 90° | 50°, 130°; axial 90° | Radial apse plan precedents support testing outer stations independently; historical plates do not pick an exact F5ZP azimuth. |
| Ordinal chapel sequence | Earlier grouped entrance study | Preserves recorded W–C–W–AXIAL C–W–C–W | B retains the documented scheme's intended ordinal spacing. |
| Cross-chapel cheek/wall surface intersection pairs | 9 in R21 subset | 0 in R21 subset | B has the cleaner limited tested envelope. These values are **inherited from R21 QA**, not new tests. |
| Flyer receiving pier | Not defined authoritatively | Not defined authoritatively | Test engaged wall, T-section receiver, independent outward pier; no dimensions authorized. |
| Intermediate supports | Not verified | Not verified | Ungewitter II p109 offers a historically illustrated option; not permission to add piers. |
| Roof/gallery envelope | Unverified | Unverified | Two-tier flyers may occupy gallery/roof space; elevation overlay needed. |
| Four-bearing outer half-cell vault connection | Unverified | Unverified | No source resolves the missing F5ZL-C schedule or exact bearing topology. |
| Structural load path | Not checked | Not checked | The presence of a flyer in a plate, surface contact, or valid mesh does not establish structural safety. |

**Provisional architectural direction:** retain B as a candidate; evaluate an *integrated wall-and-receiver* morphology first at each flanking chapel seam because it offers a comparison to historical wall-buttress plans without automatically placing detached piers in the open recesses. This is a research proposal, not verified clearance or a design acceptance. Keep A unchanged for comparison. A T-plan or discrete intermediate receiver remains a separate alternative rather than a presumed replacement.

## Exact R21 technical constraints to carry into future isolated fit tests

- World X east, Y north, Z up; chevet center (20213, 0); azimuth clockwise from +Y.
- Seven protected outer identities: 30°, 50°, 70°, 90°, 110°, 130°, 150°. Saved nonuniform inner/middle station schedule differs; **do not equate them**.
- R21 experimental outer spring Z2300 versus protected inner spring Z3000 (700 native units). R21 reported roof and gallery coordination as OPEN.
- R21 trial 14 web bodies passed limited mesh validation; 13/13 candidate half-cell seams coincided, but approved architectural contact did not pass.
- R21 reported 14/14 rib contacts with **trial** pads and trial pier cores; no verified approved-masonry bearing contacts.
- A previous unapproved frame-corrected V13 comparator had nearest-surface gaps up to 145.668 native units. Do not treat it as a known-good fit.
- Native units are 1:1 project values; physical metres-per-unit remains undocumented. Do not scale historical plates directly into project units.

## Proposed next geometric experiment (not yet executed)

1. Recover the named approved actual outward receiving-face and chapel-wall meshes if present; if absent, retain bearing checks as unresolved.
2. On *copies only* of R21 A and B, compare three independently selectable receiving-pier footprints: wall-engaged, T-shaped, and outward isolated/intermediate. They must be driven by actual trial/junction wall lines and existing vault thrust stations rather than imported page silhouettes.
3. Output transverse plans and elevation sections showing exact spring/landing coordinates, bonded masonry surfaces, passage clear widths, roof envelopes and drainage; run sampled and exact collision checks, with numerical tolerances.
4. Mark geometric fit distinct from historical analogy and structural load-bearing. Do not mark M01 complete or promote a geometry baseline without closing the outstanding evidence gates and explicit approval.

## Tests actually performed in this R02 pass

- R01 review ZIP, two historical source archives: contents read; nine targeted PNG pages decoded and resized for comparison (source bytes copied as received into `sources/`).
- Rendered 3×3 source contact sheet and a **schematic** station-only SVG (no invented receiving polygons or calibrated plan).
- Recovered original GitHub R01 master reference and *read* saved MR COMPUTER R21 report/decision/contact/gate files.
- **NOT performed:** new Blender boolean/intersection tests, full-scene 3D clearances, historical arc fits, new bridge or receiver geometry, structural thrust/capacity calculations, F5ZL-C recovery.

**Disposition: historical comparison delivered; bearing selection and M01 remain OPEN.**
