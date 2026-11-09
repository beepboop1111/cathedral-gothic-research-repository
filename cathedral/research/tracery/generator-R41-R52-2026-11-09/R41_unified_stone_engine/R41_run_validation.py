"""R41 runner: consolidate baseline R34/R39 and validate curved/tapered experimental stone-body sweep.
Single batch: baseline & synthetic regression, GLB export, render, QA JSON.
"""
import bpy,math,json,hashlib,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from mathutils import Vector
from pathlib import Path
from R41_engine import StoneSpec,read_ayr_r32_profile,build_pair,mesh_info,stock_config,has_self_intersections

HOME=Path('/home/christopher/Cathedral_Research')
OUT=HOME/'R41_unified_stone_engine'
SRC=HOME/'R32/R32_section_trace_samples.csv'
META=HOME/'R32/R32_measurements_and_evidence.json'
LEGACY=json.loads((HOME/'R34/R34_mesh_qa.json').read_text())
R39=json.loads((HOME/'R39_oblique_junction_experiment/R39_qa_evidence_and_joints.json').read_text())
assert SRC.is_file() and (HOME/'R40_joinery_handoff/R40_checkpoint_evidence.json').is_file()
assert LEGACY['source_sha256']==hashlib.sha256(SRC.read_bytes()).hexdigest()
bpy.ops.wm.read_factory_settings(use_empty=True)
profile,provenance=read_ayr_r32_profile(SRC,META)
assert abs(stock_config(profile)['width_mm']-LEGACY['stone_profile_apparent_width_mm'])<.01
SC=bpy.context.scene
SC.unit_settings.system='METRIC';SC.unit_settings.scale_length=1.
C=bpy.data.collections.new('R41_EXPERIMENTAL_ONLY');SC.collection.children.link(C)
def newmat(label,rgb):
 m=bpy.data.materials.new(label);m.diffuse_color=(*rgb,1);m.use_nodes=True
 principled=m.node_tree.nodes.get('Principled BSDF')
 principled.inputs['Base Color'].default_value=(*rgb,1)
 principled.inputs['Roughness'].default_value=.79
 return m
sand=newmat('R41 stone ochre',(.48,.34,.24))
cream=newmat('R41 stone limestone',(.72,.60,.46))
gray=newmat('R41 charcoal studio',(.15,.17,.20))
records=[]
chosen_curved=None
baseline_pair=None
for curvature in (0.,12.,26.):
 for taper in (0.,7.):
  for angle in (-22.5,0.,22.5,38.):
   tag=f'c{curvature:g}_t{taper:g}_a{angle:g}'.replace('-','n').replace('.','p')
   spec=StoneSpec(name='R41_'+tag,joint_deg=angle,curvature_mm=curvature,taper_pct=taper)
   pair,qa=build_pair(profile,provenance,spec,C,(sand,cream))
   assert qa['contact_seam_linear_gap_m']<1e-9
   assert all(z['nonmanifold']==0 for z in qa['objects'])
   records.append(qa)
   if curvature==0 and taper==0:
    assert abs(qa['combined_volume_m3']-LEGACY['signed_mesh_volume_m3'])<1e-8
    old=[a for a in R39['parametric_cases'] if a['angle_deg']==angle]
    assert len(old)==1
    assert abs(qa['contact_area_mm2']-old[0]['surface_area_mm2'])<.05
   if curvature==0 and taper==0 and angle==22.5:
    baseline_pair=pair
   elif curvature==26 and taper==7 and angle==22.5:
    chosen_curved=pair
   else:
    for obj in pair:bpy.data.objects.remove(obj,do_unlink=True)
assert len(records)==24 and baseline_pair and chosen_curved
# Different, entirely synthetic profile family (not an archaeological fixture).
newsec=[]
for i in range(128):
 a=2*math.pi*i/128.
 rr=1.+.16*math.cos(4*a)
 newsec.append((.064*math.cos(a)*rr,.115+.085*math.sin(a)*rr))
assert not has_self_intersections(newsec)
m2=dict(provenance,name='SYNTHETIC_4_LOBED_TEST_FIXTURE',evidence='mathematical artifact only')
syn,synqa=build_pair(newsec,m2,StoneSpec('R41_SYNTHETIC_TEST',length_mm=260.,curvature_mm=18.,taper_pct=-8,joint_deg=12.),C,(sand,cream))
assert synqa['contact_seam_linear_gap_m']<1e-9
for ob in syn:bpy.data.objects.remove(ob,do_unlink=True)
# Negative scenario tests reject inputs rather than silently changing source or scale.
negative=[
 StoneSpec('bad0',length_mm=0.),
 StoneSpec('badangle',joint_deg=70.),
 StoneSpec('badcurve',curvature_mm=200.),
 StoneSpec('badtaper',taper_pct=50.),
 StoneSpec('badjoin',joint_deg=50.,length_mm=40.),
 StoneSpec('badclaim',evidence='CERTIFIED_HISTORIC')]
neg=[]
for spec in negative:
 try:
  spec.validate(stock_config(profile)['height_mm'])
  neg.append({'case':spec.name,'rejected':False})
 except ValueError as ex:
  neg.append({'case':spec.name,'rejected':True,'reason':str(ex)})
assert all(x['rejected'] for x in neg),neg
assert has_self_intersections([(0,0),(.1,.1),(0,.1),(.1,0)])
# Export curved 2-stone assembly ONLY at original parametric coordinates, before studio translation.
bpy.ops.object.select_all(action='DESELECT')
for ob in chosen_curved:ob.select_set(True)
bpy.context.view_layer.objects.active=chosen_curved[0]
GLB=OUT/'R41_Curved_Tapered_Two_Stone_Experiment.glb'
bpy.ops.export_scene.gltf(filepath=str(GLB),export_format='GLB',use_selection=True,
 export_apply=True,export_yup=True,export_extras=True)
assert GLB.stat().st_size>10000
# Build side-by-side studio. Left: baseline 22.5° straight; right: curved/tapered 22.5° with visibly separated blocks.
for obj in baseline_pair:obj.location.x=-.225
for i,obj in enumerate(chosen_curved):
 obj.location.x=.215
 obj.location.y=(-.030 if i==0 else .045)
# Key grouping labels are stored only as custom properties, not on physical stones.
for obj in baseline_pair:obj['comparison_fixture']='LEGACY_R39_22P5_OBLIQUE'
for obj in chosen_curved:obj['comparison_fixture']='R41_CURVED_TAPERED_22P5_EXPERIMENT'
bpy.ops.mesh.primitive_plane_add(size=3,location=(0,0,-.015))
floor=bpy.context.object;floor.name='R41_RENDER_ONLY_FLOOR'
floor.data.materials.append(gray)
def area(name,pos,power,size):
 l=bpy.data.lights.new(name,'AREA');l.shape='DISK';l.size=size;l.energy=power
 ob=bpy.data.objects.new(name,l);SC.collection.objects.link(ob)
 ob.location=pos;ob.rotation_euler=(Vector((0,0,.12))-ob.location).to_track_quat('-Z','Y').to_euler()
area('R41 key',(-.32,-.60,.7),31,.66)
area('R41 fill',(.52,.24,.76),18,.55)
world=bpy.data.worlds.new('R41 Studio')
SC.world=world;world.use_nodes=True
world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.54,.57,.60,1)
world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.16
cd=bpy.data.cameras.new('R41_Ortho')
cam=bpy.data.objects.new('R41_Ortho',cd);SC.collection.objects.link(cam)
cam.location=(.72,-.91,.57);target=Vector((0,0,.137))
cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
cd.type='ORTHO';cd.ortho_scale=.86
SC.camera=cam
SC.render.engine='CYCLES';SC.cycles.samples=24
SC.cycles.use_denoising=True
SC.render.resolution_x=1770;SC.render.resolution_y=1090;SC.render.resolution_percentage=100
SC.render.image_settings.file_format='PNG'
SC.render.filepath=str(OUT/'R41_intermediate_render.png')
SC.view_settings.view_transform='AgX';SC.view_settings.look='AgX - Medium High Contrast'
SC.view_settings.exposure=-.65
# Save experimental scene only; it has its own collection and cannot touch F5ZP.
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'R41_Experimental_Stone_Engine.blend'))
bpy.ops.render.render(write_still=True)
report={'checkpoint':'R41','engine':'R41_engine.py','version':bpy.app.version_string,
 'provenance':provenance,'category':'EXPERIMENTAL_NOT_APPROVED',
 'regression_matrix_cases':len(records),
 'R34_volume_identity_pass':True,'R39_contact_area_regression_pass':True,
 'cases':records,'additional_synthetic_profile_family':synqa,
 'negative_tests':neg,'invalid_profile_rejection_pass':True,
 'glb':str(GLB),'render':str(OUT/'R41_intermediate_render.png'),
 'expected_joint_certification':'NO SOURCE-MEASURED CONTACT SURFACES',
 'Launceston_260_mm_dimension_used_as_Ayr_value':False,
 'source_Buda_0121_scan_acquired':False,
 'preserve_existing_R34_to_R40':True,
 'historical_structural_status':'NOT CERTIFIED'}
(OUT/'R41_generator_qa.json').write_text(json.dumps(report,indent=2))
print('R41_BUILD_PASS',json.dumps({'cases':len(records),'other_profile':synqa['combined_volume_m3'],
 'negative_tests':len(neg),'baseline_vol':LEGACY['signed_mesh_volume_m3'],
 'curved_case':[q for q in records if q['spec']['curvature_mm']==26 and q['spec']['taper_pct']==7 and q['spec']['joint_deg']==22.5][0],
 'blender':bpy.app.version_string}))
