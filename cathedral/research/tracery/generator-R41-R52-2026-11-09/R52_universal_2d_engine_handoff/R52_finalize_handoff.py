#!/usr/bin/env python3
"""Finalize R52 isolated handoff; never modify archived U01 or cathedral baselines."""
import json,hashlib,zipfile,os
from pathlib import Path
from xml.etree import ElementTree
from PIL import Image
R=Path('/home/christopher/Cathedral_Research/R52_universal_2d_engine_handoff')
R_PARENT=R.parent
report=json.loads((R/'outputs/R52_2D_REGRESSION_QA.json').read_text())
assert report['passing_spec_count']==5
assert sum(z['U01_checks_2D'] for z in report['analytical_numeric_geometric_QA'])==116
assert all(z['failed_checks']==0 and z['stable_against_original'] and z['stable_under_reordered_JSON'] and z['scale_2x_area_4x_pass'] for z in report['analytical_numeric_geometric_QA'])
assert len(report['rejected_malformed_input_cases'])==3 and all(report['rejected_malformed_input_cases'].values())
assert Image.open(R/'R52_FINAL_2D_Construction_Engine_Handoff.png').size==(2300,1520)
original=R/'baseline/tracery_universal_U01.py'
original_sha=hashlib.sha256(original.read_bytes()).hexdigest()
assert original_sha=='9ed6c586d352f5be0fd6be147275cc6155ed809b6e8b06cbc44009d5f8aaa0d3'
ZIP=Path('/home/christopher/Downloads/downlods/3/universal-generator-U01-U05-2026-11-07.zip')
assert ZIP.is_file()
def write(name,contents):
 p=R/name
 if p.exists():raise FileExistsError(str(p))
 p.write_text(contents)
def digest(p):
 return hashlib.sha256(p.read_bytes()).hexdigest()
xml={}
for p in sorted((R/'outputs').glob('*.svg')):
 root=ElementTree.parse(p).getroot()
 tags={x.attrib.get('id') for x in root.iter()}
 assert root.tag.endswith('svg') and {'construction','tracery-stone-region','opening-numbers'}.issubset(tags)
 xml[p.name]='XML_PASS'
assert len(xml)==5
write('SOURCE_PROVENANCE.md',"""# R52 2D Source Register and Exclusions

* Source engine: original U01 from 2026-11-07 U01-U05 archived generator, copied byte-for-byte. All five original U01 specs retained as read-only fixtures.
* St-Leu Fig. 80: previously traced engraving in source pixels, unknown physical scale. Archived R03 comparison IoU ~0.999467 and Hausdorff ~0.578 px (prior archival evidence, NOT retested by R52).
* St-Leu ideal variant: a hypothetical reconstruction and **not** an independent measurement.
* Synthetic two-light, three-light intersecting and four-light recursive fixtures: trial design dimensions, not claims about any medieval window.
* Brandon M04 R03 and R50: historical source drawing registration/scale bars NOT established. R50 2400x180 mm dimensions are an invented display transform.
* Herne/Brandon Plate 20, Sleaford Plate 26: elevation, plan and enlarged section have different scales and must never be naively combined.
* Ungewitter figure 1205b: differential upper/lower candidate foil settings remain uncertain; do not force the lower arc to close to an idealized foil.
* Four repaired M02/M03 window models, F5ZK-C, F5ZN-A, R28/V03, Pass 6J, inner/middle ambulatory vaults, and R34-R51 remain protected.
* Owner's French Gothic rib/arch profiles are **excluded** from the tracery generator. R46-R48 did NOT establish correct tracery profile usage. R49 is a neutral synthetic 3D test fixture only.
* No GitHub access, no source approval, and no project geometry modifications occurred in R52.
""")
write('QA_ACCEPTANCE_MATRIX.md',"""# R52 QA — separate validation vectors

| Dimension | Check | Observed R52 |
|---|---|---|
| Technical | U01 SHA-256 copy and original QA record equality | PASS |
| Technical | SVG well-formed and named geometry layers (5 cases) | PASS |
| Technical | Repeated run stability; reordered JSON stable IDs | PASS |
| Technical | Invalid mode, unreachable circle, missing outline | REJECTED 3/3 |
| Geometric | U01 native internal tests | PASS 116/116 |
| Geometric | Polygon validity and holes = named openings | PASS 5/5 |
| Geometric | Analytical circle/radius/apex residual | PASS within declared numeric tolerance |
| Geometric | 2x dimensions, 4x area, stable IDs | PASS 5/5 |
| Architectural | Member/junction counts and opening identities vs archival fixtures | PASS 5/5 |
| Architectural | Cathedral jamb/mullion/bearing integration | NOT TESTED |
| Historical | Source-scanned ink registration, original scale bars, historic geometric method | UNVERIFIED |
| Structural | Support load path, masonry joints, stresses, thrust | NOT TESTED |
| Downstream 3D | Blender GLB re-run | NOT IN SCOPE. U01-U05 reports archived, not re-run |

Mandatory next failures: circle intersection 0/1/2 cases, 0 radius, inverted tangent, off-arch crown, pinched narrow stone web, reversed winding, duplicate void IDs, wrong source units, unsupported historical approval, non-closed historical gaps, malformed 3/4/5/6/8 foils, asymmetric springings, mismatched nested bearing widths, shape overlap and disconnected components. Accept only exact geometry or explicit rejection with residual.
""")
write('NEXT_PASS_ROADMAP.md',"""# 2D Engine continuation sequence

## R53 — Strict analytical API
Wrap the unchanged U01 Circle/Arch/Model in a small source-graded type-safe interface. Output exact arc segments (centres, radii, start/end angles, tangents), stable IDs, parent relationships and unit authority. Handle NONE/TANGENT/TWO circle intersections. No 3D generator changes.
Gate: original five fixtures unchanged; at least 20 new adversarial primitive tests.

## R54 — Universal layout variations
Test two-light and three-light, 4-light nesting, 3/4/5/6/8 foils, asymmetric axes, blind spandrels, true crossings and near-pinches. Keep outline strokes and centre/radius metadata separate.
Gate: stable geometry graph, valid stone/opening regions or explicit rejection, 2x scaling and repeatable IDs.

## R55 — One historical source registration
Choose ONE plate with verified figure-specific elevation scale and separate enlarged-detail scale. Compare actual source ink with calculated circle/arc residuals. Preserve uncertain portions rather than repairing them.
Gate: source-specific metrology with uncertainty; no dimension transfer between Brandon/Herne/Sleaford/St-Leu or different figure details.

## R56 — 2D layout lock and 3D interface
Only after explicit user approval, publish exact labelled curves, 2D regions, openings, construction graph, springing/tangent/normal anchors, coordinate transforms, dimensional authority and source links.
3D profiles, stone bedding, glazing rebates and structural load checks remain separate and are NOT inferred from 2D geometry.
""")
write('RUNBOOK.md',"""# R52 Quick runbook

Location:
/home/christopher/Cathedral_Research/R52_universal_2d_engine_handoff/

Run under system Python:
    python3 R52_2d_only_regression.py

Requirements: numpy, scipy, shapely, trimesh, Pillow. U01 imports Triangle for 3D cap meshing; when unavailable, R52 creates a harmless import placeholder strictly for 2D Model(spec) execution. NEVER call U01 solids(), U02-U05 or GLB export through this placeholder.

Expected signature: R52_2D_REGRESSION_PASS, fixtures 5, checks 116, negative_cases 3.

Output: outputs/R52_2D_REGRESSION_QA.json, five construction SVGs and one single review PNG.

Read HANDOFF.md (main authority), SOURCE_PROVENANCE.md (evidence), QA_ACCEPTANCE_MATRIX.md (testing), ENGINE_CONTRACT.json (target R53), NEXT_PASS_ROADMAP.md (next steps).

Do not regenerate approved cathedral geometry or the four repaired M02/M03 windows. Do not invoke GitHub. Separate 2D geometry confidence from historical and structural validity.

When eventually launching Blender for a downstream 3D test, load the user's /home/christopher/tab.py keymap, verify active keyconfig, and avoid global preference changes. Blender is NOT required for 2D R52.
""")
contract={
 'schema_version':'R52_HANDOFF_TO_R53_DRAFT',
 'status':'TARGET_API_SPEC_ONLY_NOT_IMPLEMENTED',
 'source_engine':'U01 Circle, Arch, Model(spec), recovered source SHA-256 '+original_sha,
 'coordinate_system':{'axes':['x horizontal rightward','z vertical upward'],
                      'source_units':['px uncalibrated','mm parametric trial','mm verified scale only']},
 'input_required':['id','mode plate/bar','units','source_id','source_file_hash','scale_authority',
                   'construction_tolerance','sampling_sagitta_tolerance','historical_evidence_class',
                   'outline primitives','nested fill/void definitions','spandrel_mode'],
 'output_required':{
    'analytic_curves':['curve_id','centre','radius','start_param','end_param','winding','tangent','source_status'],
    'topology':['stone_region','opening_ids','opening_hierarchy','member_ids','junction_incidence','minimum_web'],
    'geometry_QA':['circle residual','springing/crown residual','tangency residual','closed loop','polygon area','scale invariance'],
    'documentation':['source_SHA256','drawing_view','unit conversion evidence','uncertainty','construction layer labels'],
    'render':['SVG with black confirmed input model, gray construction, red uncertain historic interpretation']
 },
 'forbidden_inference':['mix different historical examples','copy rib or arch moulding profiles as tracery',
 'pretend synthetic millimetres are medieval dimensions','infer 3D depth/rebate from 2D plate',
 'force symmetry where historical ink differs','approve cathedral geometry from numerical tests']
}
write('ENGINE_CONTRACT.json',json.dumps(contract,indent=2)+'\n')
index={
 'handoff':'R52_Universal_2D_Engine_HANDOFF_R01',
 'checkpoint_status':'VALIDATED_EXPERIMENTAL_2D_ONLY',
 'source_engine':'U01',
 'source_sha256':original_sha,
 'source_archive':str(ZIP),
 'archive_sha256':digest(ZIP),
 'regression_fixtures':5,
 'internal_2d_checks_pass':116,
 'external_negative_rejections':3,
 'SVG_XML':xml,
 'QA_json':'outputs/R52_2D_REGRESSION_QA.json',
 'main_handoff':'HANDOFF.md',
 'source_units':'mixed: px/St-Leu versus synthetic trial mm; NO interchange',
 'historical_approval':False,
 'structural_approval':False,
 'prior_U02_to_U05_GLb_QA_rerun':False,
 'user_rib_profiles_used':False,
 'approved_F5ZP_geometry_modified':False,
 'GitHub_accessed':False,
 'next_pass':'R53',
 'Blender_keymap_when_opening':'/home/christopher/tab.py'
}
write('HANDOFF_MANIFEST.json',json.dumps(index,indent=2)+'\n')
# Source is copied as-is; mark only the 7 archived source copies immutable to accidental edits.
for p in (R/'baseline').iterdir():
 if p.is_file():p.chmod(0o444)
print('R52_METADATA_CREATED',len(xml),'SVGs and five supplementary handoff docs')
