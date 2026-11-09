# J04 - Isolate first failed intersection, test robust Boolean options.
import bpy,bmesh,os,time,json,math
from mathutils import Vector,kdtree
ROOT='/home/christopher/Cathedral_Experiments/tracery_moulding_J04'
os.makedirs(ROOT,exist_ok=True)
j01=open('/home/christopher/Cathedral_Experiments/tracery_moulding_J01/generate_J01.py').read()
exec(j01[:j01.index('paths=[]')],globals())
exec(j01[j01.index('paths=[]'):j01.index('parts=[sweep(')],globals())
exec(j01[j01.index('def inspect(ob):'):j01.index('for o in parts:')],globals())
ROOT='/home/christopher/Cathedral_Experiments/tracery_moulding_J04'
results=[]
def test(solver, hole=False, epsilon=0.0,full=False):
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    subset=paths if full else paths[:3]
    parts=[sweep(n,p,stone) for n,p in subset]
    if epsilon:
        # Displace branch by a small *depth-only* amount to remove coincident skin
        parts[-1].location.z=epsilon
        bpy.context.view_layer.objects.active=parts[-1]
        bpy.ops.object.select_all(action='DESELECT');parts[-1].select_set(True)
        bpy.ops.object.transform_apply(location=True,rotation=False,scale=False)
    base=parts[0];stages=[]
    for part in parts[1:]:
        bpy.context.view_layer.objects.active=base
        mod=base.modifiers.new('J04_trial','BOOLEAN')
        mod.operation='UNION';mod.solver=solver;mod.object=part
        if solver=='EXACT':mod.use_hole_tolerant=hole
        if solver=='FLOAT':mod.double_threshold=1e-7
        part_name=part.name
        try:
            bpy.ops.object.modifier_apply(modifier=mod.name)
            bpy.data.objects.remove(part,do_unlink=True)
            q=inspect(base)
            stages.append(dict(name=part_name,**q))
        except Exception as e:
            stages.append({'error':str(e),'part':part_name});break
    qa=inspect(base)
    # No silent claims of structural correctness from topology checks.
    out={'solver':solver,'hole_tolerant':hole,'z_epsilon':epsilon,'full':full,'qa':qa,'stages':stages}
    results.append(out);print('J04_RESULT',json.dumps(out),flush=True)
    return qa,base
for solver,hole,eps in [
    ('EXACT',False,0.0),('EXACT',True,0.0),('MANIFOLD',False,0.0),
    ('FLOAT',False,0.0),('EXACT',True,0.002),
    ('MANIFOLD',False,0.002)]:
    test(solver,hole,eps,False)
# Select the best parameter set that genuinely passes isolated FIRST failure.
valid=[r for r in results if r['qa']['boundary_edges']==0 and
       r['qa']['nonmanifold_edges']==0 and r['qa']['connected_components']==1]
best=None
if valid:
    valid.sort(key=lambda r:(r['z_epsilon']!=0,r['qa']['vertices']))
    candidate=valid[0]
    q,base=test(candidate['solver'],candidate['hole_tolerant'],candidate['z_epsilon'],True)
    # A manifold-only mesh is NOT a pass if the solver silently discarded inputs.
    retained=(q['vertices']>2500 and q['volume_abs']>600 and
              all(stage.get('vertices',0)>1020 for stage in results[-1]['stages']))
    results[-1]['input_retention_pass']=retained
    if retained and q['boundary_edges']==0 and q['nonmanifold_edges']==0 and q['connected_components']==1:
        best=base
        bpy.ops.object.select_all(action='DESELECT')
        base.select_set(True);bpy.context.view_layer.objects.active=base
        bpy.ops.export_scene.gltf(filepath=os.path.join(ROOT,'J04_FULL_PASS.glb'),
                                  export_format='GLB',use_selection=True,export_apply=True)
# Render diagnostic of the first junction using best available candidate,
# full if success, isolated if failure.
if best is None:
    _,best=test('EXACT',False,0,False)
status='PASS' if best is not None and any(r.get('full') and r.get('input_retention_pass') for r in results) else 'FAIL_INPUT_LOSS'
best.location.x=0
best.data.materials.clear();best.data.materials.append(stone)
for f in best.data.polygons:f.material_index=0
def label(s,y,size):
    cu=bpy.data.curves.new('label','FONT');cu.body=s;cu.align_x='CENTER';cu.size=size
    o=bpy.data.objects.new('label',cu);bpy.context.collection.objects.link(o);o.location=(0,y,2);cu.materials.append(label_mat)
label('J04  /  FIRST JUNCTION SOLVER DIAGNOSTIC',134 if status=='PASS' else 106,2.0)
label('STATUS: '+status+'  /  NO APPROVED GEOMETRY CHANGED',56 if status=='PASS' else 47,1.6)
bpy.ops.mesh.primitive_plane_add(size=2,location=(0,92,-3.5))
background_plane=bpy.context.object; background_plane.name='Dark presentation backing';background_plane.scale=(32,56,1);background_plane.data.materials.append(background)
world=bpy.context.scene.world or bpy.data.worlds.new('World');bpy.context.scene.world=world
world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.16,.19,.23,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.9
ld=bpy.data.lights.new('review fill','AREA');ld.energy=1200;ld.size=90
light=bpy.data.objects.new('review fill',ld);bpy.context.collection.objects.link(light)
light.location=(-30,60,50);light.rotation_euler=(Vector((0,50,0))-light.location).to_track_quat('-Z','Y').to_euler()
cd=bpy.data.cameras.new('front');cam=bpy.data.objects.new('front',cd);bpy.context.collection.objects.link(cam)
mid=100 if status=='PASS' else 95
cam.location=(0,mid,200);cam.rotation_euler=(0,0,0);cd.type='ORTHO';cd.ortho_scale=145 if status=='PASS' else 107
sc=bpy.context.scene;sc.camera=cam;sc.render.engine='CYCLES';sc.cycles.samples=14
sc.render.resolution_x=1040;sc.render.resolution_y=1000
sc.render.image_settings.file_format='PNG'
sc.render.filepath=os.path.join(ROOT,'J04_FINAL_solver_diagnostic.png')
sc.view_settings.view_transform='AgX'
report={'status':status,'blender':bpy.app.version_string,
        'tests':results,'architectural_validation':False,
        'source_geometry':'J01 synthetic', 'full_model_status':status,'important_note':'Manifold solver discards unmerged swept solids despite watertight output; input retention is mandatory'}
with open(os.path.join(ROOT,'J04_QA.json'),'w') as f:json.dump(report,f,indent=2)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'J04_EXPERIMENTAL.blend'))
bpy.ops.render.render(write_still=True)
print('J04_COMPLETE',status,flush=True)
