"""R18 Blender reload, rejected-build preservation and experimental replay tests."""
import bpy,sys,pathlib,hashlib,json
HERE=pathlib.Path(__file__).resolve().parents[1]
R17=pathlib.Path("/home/christopher/Downloads/F5ZP_UNIVERSAL_GOTHIC_VAULT_GENERATOR_R01_EXPERIMENTAL/experiments/F5ZP_R17_FAST_UNIVERSAL_VAULT_WORKSPACE_EXPERIMENTAL")
sys.path[:0]=[str(HERE),str(HERE/"addon"),str(R17/"addon"),
              str(R17/"addon/r17_vendor")]
import r18_live as r18
import r17_experimental_workspace as r17
r17.register();r18.register()
s=bpy.data.scenes["R17_WORKSPACE"]
bpy.context.window.scene=s
hash_file=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
protected=[HERE/"blender/F5ZP_R18_SKELETON_FIRST_LIVE_V01_EXPERIMENTAL.blend",
 R17/"blender/F5ZP_R17_FAST_VAULT_WORKSPACE_REVIEW_READY_V02_EXPERIMENTAL.blend",
 R17/"addon/r17_core.py",R17/"addon/r17_experimental_workspace.py",
 R17/"addon/r17_vendor/strict_crown_guard.py"]
before={str(p):hash_file(p) for p in protected}
results={}
props=s.r17_props
props.vault_type="CUSTOM";props.custom_sectors=7;props.quality="FAST"
props.irregularity=.1;props.crown_mode="AUTO";props.crown_locked=False
assert bpy.ops.r18.regenerate()=={"FINISHED"}
active=bpy.data.collections["R18_ACTIVE_GEOMETRY"]
web=[o for o in active.objects if o.type=="MESH"][0]
assert len(active.objects)==15
before_fail=(len(web.data.vertices),len(web.data.polygons),web.data.vertices[0].co[:])
results["custom_7_sector"]={"status":"PASS","triangles":len(web.data.polygons)}
props.crown_mode="MANUAL";props.crown_z=3010.
try:
    result=bpy.ops.r18.regenerate()
    assert result=={"CANCELLED"}
except RuntimeError as e:
    assert "HARD STOP" in str(e)
web2=[o for o in active.objects if o.type=="MESH"][0]
assert (len(web2.data.vertices),len(web2.data.polygons),web2.data.vertices[0].co[:])==before_fail
results["below_apex_hard_stop_preserved_mesh"]="PASS"
props.crown_mode="AUTO";props.crown_locked=True
try:
    result=bpy.ops.r18.regenerate()
    assert result=={"CANCELLED"}
except RuntimeError as e:
    assert "HARD STOP" in str(e)
web3=[o for o in active.objects if o.type=="MESH"][0]
assert len(web3.data.polygons)==before_fail[1]
results["locked_crown_auto_hard_stop"]="PASS"
props.crown_locked=False;props.vault_type="HEXA"
props.quality="FINAL";props.irregularity=.08
assert bpy.ops.r18.regenerate()=={"FINISHED"}
mesh=[o for o in active.objects if o.type=="MESH"][0]
assert len(mesh.data.polygons)==6*128*128
results["final_6_irregular"]={"status":"PASS","triangles":len(mesh.data.polygons)}
assert bpy.ops.r18.export_glb()=={"FINISHED"}
index=int(s["r18_build_count"])
glb=HERE/"outputs"/f"R18_BUILD_{index:03d}_WEB_ONLY_1TO1.glb"
assert glb.exists() and glb.stat().st_size>8000
# An independently executed GLB importer validates basic round-trip.
bpy.ops.import_scene.gltf(filepath=str(glb))
imported=[o for o in bpy.context.selected_objects if o.type=="MESH"]
assert imported and max(v.co.z for o in imported for v in o.data.vertices)>3000
for ob in imported:bpy.data.objects.remove(ob,do_unlink=True)
results["gltf_round_trip"]="PASS"
assert bpy.ops.r18.checkpoint()=={"FINISHED"}
candidates=sorted((HERE/"blender").glob("R18_SKELETON_FIRST_CHECKPOINT_*.blend"))
assert candidates and candidates[-1].stat().st_size>30000
results["versioned_blend_checkpoint"]="PASS"
after={str(p):hash_file(p) for p in protected}
assert before==after
record={"status":"R18_BLENDER_FRESH_PROCESS_TEST_PASS",
        "tests":results,"sha_preserved":before==after,
        "validated_6_sector_glb":str(glb),
        "new_blender_checkpoint":str(candidates[-1]),
        "original_R17_and_R18_V01_not_overwritten":True}
out=HERE/"qa/R18_BLENDER_RELOAD_REGRESSION_QA.json"
with out.open("x") as f:json.dump(record,f,indent=2)
print("R18_RELOAD_REGRESSION_PASS",json.dumps(results),flush=True)
