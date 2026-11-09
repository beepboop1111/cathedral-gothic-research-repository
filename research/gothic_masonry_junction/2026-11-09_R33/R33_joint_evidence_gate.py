#!/usr/bin/env python3
"""R33: historical stone-block evidence gate; does not generate cathedral geometry."""
import json
from pathlib import Path
O=Path('/home/christopher/Cathedral_Research/R33')
O.mkdir(exist_ok=True)
def evidence(record):
    reasons=[]
    if not record.get('independent_metric_control'): reasons.append('missing_independent_metric_control')
    if not record.get('registered_front_and_rear'): reasons.append('front_rear_not_registered')
    if not record.get('original_joint_bed_polygons'): reasons.append('original_bed_polygons_not_measured')
    if not record.get('authenticated_mating_contact'): reasons.append('no_authenticated_mating_contact')
    if not record.get('fabric_phases_identified'): reasons.append('original_restoration_not_disambiguated')
    if not record.get('metric_raw_mesh_available'): reasons.append('no_original_metric_mesh_available')
    if record.get('source_type')=='isometric_publication': reasons.append('isometric_not_orthographic_surface_survey')
    return {'specimen':record['specimen'],'certifiable_as_measured_historic_joint':not reasons,
            'blockers':reasons,'usable_for':record['usable_for']}
records=[
 {'specimen':'Ayr #8','source_type':'archaeological_text_and_drawing','independent_metric_control':False,
 'registered_front_and_rear':False,'original_joint_bed_polygons':False,'authenticated_mating_contact':False,
 'fabric_phases_identified':True,'metric_raw_mesh_available':False,
 'usable_for':['2D scaled section trace','front/rear moulding differentiation','incised upper-bed marks described in text']},
 {'specimen':'Ayr #5','source_type':'archaeological_text','independent_metric_control':False,
 'registered_front_and_rear':False,'original_joint_bed_polygons':False,'authenticated_mating_contact':False,
 'fabric_phases_identified':True,'metric_raw_mesh_available':False,
 'usable_for':['original end seating reported','glazing-groove and possible saddle-bar slot']},
 {'specimen':'Buda #0121','source_type':'survey_publication','independent_metric_control':False,
 'registered_front_and_rear':False,'original_joint_bed_polygons':False,'authenticated_mating_contact':False,
 'fabric_phases_identified':False,'metric_raw_mesh_available':False,
 'usable_for':['published structured-light reference metrics','published section survey examples']},
 {'specimen':'Regensburg fig.155','source_type':'isometric_publication','independent_metric_control':False,
 'registered_front_and_rear':False,'original_joint_bed_polygons':False,'authenticated_mating_contact':False,
 'fabric_phases_identified':False,'metric_raw_mesh_available':False,
 'usable_for':['special stone transition typology','1:25 isometric scale as caption metadata']},
 {'specimen':'Launceston #8','source_type':'archaeological_description','independent_metric_control':False,
 'registered_front_and_rear':False,'original_joint_bed_polygons':False,'authenticated_mating_contact':False,
 'fabric_phases_identified':True,'metric_raw_mesh_available':False,
 'usable_for':['published 260mm depth','two orthogonal end-joint directions']},
 {'specimen':'Freiburg fragments','source_type':'physical_stone_report','independent_metric_control':False,
 'registered_front_and_rear':False,'original_joint_bed_polygons':False,'authenticated_mating_contact':False,
 'fabric_phases_identified':True,'metric_raw_mesh_available':False,
 'usable_for':['dorsal seating evidence','front/rear hollows','glazing rebate examples']}
]
out=[evidence(r) for r in records]
assert len(out)==6 and all(not r['certifiable_as_measured_historic_joint'] for r in out)
# Artificial positive case proves code can pass when all independent predicates are supplied.
fixture={k:True for k in ('independent_metric_control','registered_front_and_rear',
'original_joint_bed_polygons','authenticated_mating_contact','fabric_phases_identified','metric_raw_mesh_available')}
fixture.update(specimen='SYNTHETIC QA ONLY',source_type='mock',usable_for=['unit test'])
assert evidence(fixture)['certifiable_as_measured_historic_joint']
# Any single missing gate must reject; no false positives.
for k in ['independent_metric_control','registered_front_and_rear','original_joint_bed_polygons',
'authenticated_mating_contact','fabric_phases_identified','metric_raw_mesh_available']:
 case=dict(fixture);case[k]=False
 assert not evidence(case)['certifiable_as_measured_historic_joint']
report={'pass_id':'R33','status':'EVIDENCE_GATES_TESTED','date':'2026-11-08',
    'historical_cases_checked':len(out),'historical_joint_certifications':0,
    'gate_unit_tests_passed':7,
    'source_constraints':[
     {'source':'Papajanni 2002, Bildband I, fig. 155','claim':'1:25 special-stone isometric at south tower west facade / northern buttress; not a glazed window joint','consequence':'No contact-face normals without registered independent sections'},
     {'source':'Papajanni 2002, Bildband I, fig. 158','claim':'Frieze joints often divide continuous figurative carved motifs','consequence':'Do not derive stone-body boundaries solely from ornamental boundaries'},
     {'source':'Papajanni 2002, Bildband I, fig. 159','claim':'Joints were repointed in 1995; original mortar resembled limestone in color','consequence':'Separate original joint from later pointing/visible seams'},
     {'source':'Papajanni 2002, Bildband I, fig. 160','claim':'Unique green sandstone frieze block at northern tower buttress joint; much surrounding limestone renewed','consequence':'Material and fabric-phase classification required'},
     {'source':'Papajanni 2002, Bildband I, fig. 163','claim':'Map of differing parapet forms and stone cuts','consequence':'No universal repeated-block grammar without bay-specific survey'},
     {'source':'Lindsay 1985, pp. 220-222 fig. 8','claim':'Ayr #8 upper beds are marked and front/back mouldings differ','consequence':'Two bed observations do not provide measured joint polygons'}
    ],
    'cases':out,
    'interoperability_rules':{
      'geometric_layer':'Physical ashlar solids and their contact faces are separate from visible moulding/tracery curves',
      'fabric_phase_layer':'Original/repair/altered/unknown material explicitly tagged',
      'provenance_layer':'Every surface has source ref and either 3D coordinates or unknown, never invented 0',
      'validation_layer':'2D artwork cannot bypass 3D contact and registration gates',
      'baseline':'R19 remains experimental; Pass 6J and F5ZP validated cathedral geometry untouched'
    },
    'live_access':'University Bildband server returning HTTP 503 on 2026-11-08; only captions retrieved at this pass',
    'cathedral_modified':False}
(O/'R33_historic_joint_validation.json').write_text(json.dumps(report,indent=2))
md='''# R33 — stone body versus carved motif
**Historical evidence**: Regensburg Papajanni Bildband 1 figs.155, 158–160, 163 (caption audit). Ayr Stell catalog, pp.220–222. Buda Somogyi et al. 2017.

- Fig. 155: 1:25 isometric of special stones at a buttress transition; not an orthographic face survey and not a glazing detail.
- Fig. 158: joint lines can cross one continuous carved animal/flower motif, so ornament is not the block boundary.
- Fig. 159: restoration pointing can obscure or change visual joint identification.
- Fig. 160: original material and restored material coexist. Record fabric phase before measuring.
- Fig. 163: mapped differences by gallery position must survive any procedural generator.

**Engine consequence**: build the ashlar block (front/rear/contact polygons, bedding planes) independently of its relief. Decorative continuity is not proof of stone continuity. Preserve source identities, unknowns and version status.

**R33 validation**: six historical specimens audited, zero certified historic 3D joints. Six negative cases and seven synthetic gate tests pass. R32 measured section remains illustrative evidence only.

**Remote source blocker**: University server returns 503 when requesting figure image bytes, so original Regensburg isometrics have not been measured here.

No Blender geometry, GLB, GitHub changes or cathedral lock overrides.
'''
(O/'R33_STONE_BODY_JOINERY_FINDINGS.md').write_text(md)
print(json.dumps({'R33_cases':len(out),'historically_certified':sum(v['certifiable_as_measured_historic_joint'] for v in out),'synthetic_gate_tests':'7/7','files':sorted(p.name for p in O.iterdir())}))
