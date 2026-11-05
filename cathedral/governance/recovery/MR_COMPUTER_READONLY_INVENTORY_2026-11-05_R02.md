# MR COMPUTER Read-Only Recovery Inventory — 2026-11-05 R02

**Classification:** Reported read-only recovery evidence, pending independent reconciliation. **Not** architectural approval, an authority promotion, a generator replacement, or a model validation certificate.

**Provenance:** User-provided report of a successful MR COMPUTER Desktop Commander read-only inventory, supplied on 2026-11-05. These machine findings were **not independently rerun in the present GitHub-recording turn**. The underlying original files, actual SHA-256 digests, and logs should be consulted for any future approval.

**GitHub master reference at time of report:** `cathedral/governance/CATHEDRAL_MASTER_REFERENCE.md`, branch `cathedral/governance-r01`, blob SHA `1d7e358ff7562fcc64088854baa2abd3d31a729e`, independently confirmed unchanged during this recording.

## 1. Verified-access report, not approval

- MR COMPUTER connection succeeded and accessible local architectural files were inventoried read-only.
- No geometry or generator was executed, regenerated, or saved.
- Five principal Blender files reportedly reopened in Blender 5.0.1 without missing linked libraries, and their existing SHA-256 digests matched a prior inventory.
- Live 14-vault working generator **remains unidentified**.
- Modification times below are transcribed as given. The report calls Nov 4 evening timestamps `EDT`, although New York observed standard time by Nov 4, 2026; timezone labels require verification against file metadata before use as authoritative timestamps.

## 2. Recovered archive and dimensional JSON

Master checkpoint archive:
`/home/christopher/Backups/Cathedral_Project_Safety_2026-11-04/Cathedral_Master_Checkpoint_R01_FOR_REVIEW.zip`
- Reported modified 2026-11-05 00:14 EST; SHA-256 starts `95956bb10c6b` (partial only).
- Introduction: `/home/christopher/Backups/Cathedral_Project_Safety_2026-11-04/MASTER_CATHEDRAL_CHECKPOINT_R01_FOR_REVIEW/START_HERE.md`
- Authority notice: **FOR REVIEW, NO APPROVAL PROMOTION**.

Recovered JSON directory:
`/home/christopher/Desktop/F5ZP_CATHEDRAL_SYSTEM_EXPERIMENTAL/geometry_reconciliation_v02/recovered_original_checkpoints/`

| File | Reported values | Authority caveat |
|---|---|---|
| `CATHEDRAL_F5ZK_C_CURVED_CHEVET_AMBULATORY_IDENTITY.json` | F5ZK-C, radii 2933/4085/5285/6657; spring 3000; crown 4296; gallery floor 4521 | Byte-identical to checkpoint copy; modification time is not approval |
| `F5ZN_A_COMPREHENSIVE_FLOOR_PLAN_CHECKPOINT.json` | F5ZN-A, 1:1 units; chevet center (20213,0); radii 2933/4085/5285/6657/6849 | Byte-identical to checkpoint copy; precedence unresolved |

Both JSON files and saved F5ZK-C architectural PDF reportedly use **seven center angles 14°, 40.5°, 65.75°, 90°, 114.25°, 139.5°, 166°**, whereas Master Reference prose reports **30°, 50°, 70°, 90°, 110°, 130°, 150°**. **Critical unresolved authority conflict. Do not assume either schedule supersedes the other or alter models to match without explicit evidence/approval.**

## 3. Blender files recovered

| Exact saved file | Reported contents / limitation |
|---|---|
| `/home/christopher/Cathedral_STLs/Cathedral_Parts_Library.blend` | Oct 9, 163 objects: 13 in collection `Approved`, 150 in `Source` |
| `/home/christopher/Desktop/blender/1Cathedral_Parts_Library.blend` | Oct 5, older library, 167 objects |
| `/home/christopher/Desktop/Cathedral_F5ZP_G40_Working.blend` | Oct 11, 399-object G40 scene; **not** ambulatory generator |
| `/home/christopher/Desktop/newgen_F5ZN_A_CHEVET_STUDY_1to1.blend` | Oct 10, 57 objects, coordination guides |
| `/home/christopher/Desktop/newgen_F5ZN_A_GOTHIC_POINTED_ARCH_RIB_TRIAL_1to1.blend` | Oct 10, 346 objects, experimental; `web_generation: NONE` |

Collection labels like `Approved` are not user approval evidence. No listed scene establishes the saved working 14-vault producer.

## 4. Vault scripts found; no script executed

Directory `/home/christopher/Desktop/profiles/2/`:

| Filename | SHA-256 prefix | Notes |
|---|---|---|
| `ug_vault_generator.py` | `b69549e43923` | Same bytes as `ug_vault_generator(1).py` |
| `ug_vault_generator(1).py` | `b69549e43923` | Duplicate |
| `ug_vault_generator_F5ZE.py` | `c55628d9ddfe` | Same bytes as `ug_vault_generator(1.py` |
| `ug_vault_generator(1.py` | `c55628d9ddfe` | Duplicate with irregular filename |
| `ug_vault_generator(1)(1).py` | `eb68a0c16ca5` | Third distinct variant |

Three distinct script versions. Python syntax parsed and numpy/matplotlib/trimesh importability was reported. The 67,756-byte F5ZE/V13 variant describes R2=5429, R3=6965 and a different angular schedule; **do not assume it produced the F5ZN-A 14-vault working output**.

Missing historical hard-coded inputs under `Downloads/CATHEDRAL_F5ZN_A_COMPREHENSIVE_FLOOR_PLAN_/` and `Downloads/V13/V13_A4_ORIGINAL_WEBS_ONLY_YUP_FULLSCALE.stl`; recovered F5ZN-A checkpoint JSON exists elsewhere.

## 5. Pass 6J partial recovery

R1/78 spring-cluster variants and V8–V13 assets reportedly survive inside parts libraries. Found:
- `/home/christopher/Cathedral_STLs/Source/R1_78_REGENERATED_TRUE_ARCHES_RIBS_ONLY_V6.stl`
- `/home/christopher/Cathedral_STLs/Source/R1_78_REGENERATED_TRUE_ARCHES_RIBS_ONLY_V6(1).stl` (byte-identical)
- `/home/christopher/Cathedral_STLs/Source/old/R1_78_REGENERATED_ARCHES_WITH_VERTICAL_RESPONDS_V6.stl`

Original Pass 6J eight-bearing CSVs not found in searched paths or ZIP indexes. The Oct 10 eight-carrier F5ZN-A study is a separate experiment.

## 6. Unresolved conflicts and dependencies

| ID | Issue | Required evidence/action |
|---|---|---|
| AUTH-ANG-01 | 30°–150°/20° angular plan in prior governance prose conflicts with 14°–166° unequal schedule in both recovered JSONs and F5ZK-C PDF | Locate explicit approval/lock decisions, compare plate and actual saved coordinates. Neither wins by timestamp alone |
| GEN-AMB-01 | Exact working 14-vault generator/model/inputs/QA unknown | Search file inventories, GLBs/STLs, Blender scene metadata, scripts and QA logs by V13 + 14 vault + 7 shared arches; **read-only** |
| GEN-AMB-02 | Historical producer references missing under Downloads | Find content-identical V13 web source and recovered checkpoint path; record hashes, do not patch authoritative script |
| DIM-01 | Gallery elevations 4521 vs 4950 | Attribute each to a named subsystem and approval scope before reconciling |
| DIM-02 | Q1/J1 radius 5400 vs 5429 | Determine distinct revision/context and approval precedence |
| DIM-03 | Experimental formerets vs F5ZK-C schedule | Preserve both; compare only after source recovery |
| SUP-F5ZL-01 | `CATHEDRAL_F5ZL_C_PHYSICAL_SUPPORTS.csv` for 248 supports missing | **Keep unresolved; do not invent supports, dimensions or capacity** |
| PIER-6J-01 | Pass 6J bearing authority not recovered | Find original eight-bearing CSVs and explicit approval; preserve R1/78 asset evidence |
| AUTH-LEDGER-01 | Approval lineage of saved models and generators incomplete | Cross-reference explicit user approval records to source hashes/models |

## 7. Next authorized work

1. Preserve originals; continue **read-only** search for the actual inner/middle ambulatory 14-vault producer, matching source webs, generated models and QA artifacts.
2. Independently recover plan-approval decisions and compare the conflicting chevet center schedules without promoting either.
3. Recover Pass 6J bearing CSVs and F5ZL-C schedule if possible; leave unresolved otherwise.
4. Only then undertake isolated new architectural development using the exact relevant saved baseline, leaving protected work untouched.

**Checkpoint outcome:** GitHub and Desktop Commander access reported functional; model inventory materially improved. **Generator identity and architectural approval conflicts remain unresolved.** No model validation or authority promotion claimed by this report.
