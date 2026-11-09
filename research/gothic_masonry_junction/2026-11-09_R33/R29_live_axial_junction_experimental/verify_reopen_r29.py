import bpy,json,hashlib,sys
from pathlib import Path
import bmesh
sys.path.insert(0,"/home/christopher/Desktop/F5ZP_M01_R29_LIVE_AXIAL_EXPERIMENTAL_20261105")
import f5zp_live_axial as live
B=Path("/home/christopher/Desktop/F5ZP_M01_R29_LIVE_AXIAL_EXPERIMENTAL_20261105")
r28=Path("/home/christopher/Desktop/F5ZP_M01_R28_AXIAL_JUNCTION_EXPERIMENTAL_20261105/R28_AXIAL_JUNCTION_EXPERIMENTAL.blend")
scene=bpy.context.scene
data=json.loads((B/"R29_LIVE_QA.json").read_text())
assert bpy.context.preferences.addons.get("f5zp_live_axial"),"Addon not enabled after fresh open"
assert hasattr(scene,"f5zp_axial"),"Properties are not available"
assert live.reference_signature(scene)==data["baseline_sha256"],"Protected reference changed"
assert hashlib.sha256(r28.read_bytes()).hexdigest()==data["r28_input_sha256"]
assert scene["R29_REFERENCE_COUNT"]==60
assert len(live.reference_objects(scene))==60
gen=bpy.data.collections.get(live.GEN_COLL)
assert gen and len(gen.objects)==17
assert not [o.name for o in gen.objects if o.get("F5ZP_OWNER")!=live.OWNER]
report={}
for obj in gen.objects:
 if obj.type=="MESH":
  bm=bmesh.new();bm.from_mesh(obj.data)
  bad=sum(not edge.is_manifold for edge in bm.edges)
  volume=bm.calc_volume(signed=False)
  report[obj.name]={"nonmanifold_edges":bad,"volume":round(volume,3),"verts":len(obj.data.vertices)}
  assert bad==0,(obj.name,bad)
  assert volume>0
  bm.free()
before=live.reference_signature(scene)
assert before==data["baseline_sha256"]
assert bpy.ops.f5zp.rebuild_axial_junction.poll()
assert bpy.ops.f5zp.rebuild_axial_junction()=={"FINISHED"}
assert live.reference_signature(scene)==before
assert len(gen.objects)==17
version=2
assert not (B/"R29_LIVE_AXIAL_JUNCTION_EXPERIMENTAL_V02.blend").exists()
assert bpy.ops.f5zp.save_axial_checkpoint()=={"FINISHED"}
assert bpy.data.filepath.endswith("_V02.blend")
assert (B/"R29_LIVE_AXIAL_JUNCTION_EXPERIMENTAL_V02.blend").exists()
check={"fresh_open_addon_enabled":True,"persistent_params":True,"reference_integrity":True,"generated":len(gen.objects),"panel_registered":"F5ZP_PT_live_axial" in dir(bpy.types),"new_checkpoint":str(B/"R29_LIVE_AXIAL_JUNCTION_EXPERIMENTAL_V02.blend"),"mesh_checks":report}
(B/"R29_REOPEN_QA.json").write_text(json.dumps(check,indent=2))
print("R29_REOPEN_QA",json.dumps({k:check[k] for k in ("fresh_open_addon_enabled","reference_integrity","generated","new_checkpoint")}),flush=True)
