import bpy,sys,json
from mathutils.bvhtree import BVHTree
p='/home/christopher/Desktop/F5ZP_BUTTRESS_R07_TESTBAY_EXPERIMENTAL/F5ZP_R07_CHEVET_90_PAIRED_FLYERS_1TO1_EXPERIMENTAL.glb'
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=p)
d=bpy.context.evaluated_depsgraph_get()
obj={o.name:o for o in bpy.context.scene.objects if o.type=='MESH'}
targets=[n for n in obj if n.startswith('R21_SOURCE_') and not any(k in n for k in ('PIER_CORE_', 'TRIAL_PAD_'))]
new=[n for n in obj if n.startswith('R07_') and ('VOUSSOIR' in n or 'RECEIVING_SEAT' in n)]
res={}
for sn in targets:
    bs=BVHTree.FromObject(obj[sn],d,epsilon=0.0001)
    bad=[]
    for nn in new:
        bn=BVHTree.FromObject(obj[nn],d,epsilon=0.0001)
        pairs=bs.overlap(bn)
        if pairs:bad.append({'part':nn,'triangle_pairs':len(pairs)})
    res[sn]=bad
print('R07_COLLISION_REPORT',json.dumps({'mesh_count':len(obj),'checked_source_targets':len(targets),'tested_new_parts':len(new),'source_surface_crossings':res}))
