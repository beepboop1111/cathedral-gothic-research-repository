"""R50 independent clean-scene GLB round-trip and regression to R03 pixel rings.
Checks 3 through-openings, watertight topology, hypothetical explicit scale,
source-vertex inverse registration and material volume. No other assets changed.
"""
from pathlib import Path
import bpy,bmesh,json,math,hashlib
R=Path('/home/christopher/Cathedral_Research/R50_source_graded_tracery')
q=json.loads((R/'R50_Blender_geometry_QA.json').read_text())
src=json.loads((R/'R50_source_measurements.json').read_text())
pix=json.loads(Path(src['source_file']).read_text())
assert hashlib.sha256(Path(src['source_file']).read_bytes()).hexdigest()==src['source_SHA256']
scale=q['provisional_width_mm']/1000/src['outline_span_pixels']
reference={(round(float(x),3),round(float(y),3)) for loop in pix['rings'] for x,y in loop}
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(R/'R50_Brandon_R03_Hypothetical_Metric_Proxy.glb'))
objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert len(objects)==1
o=objects[0]
bm=bmesh.new();bm.from_mesh(o.data)
raw_count=len(bm.verts)
raw_broken=sum(not e.is_manifold for e in bm.edges)
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
bad=sum(not e.is_manifold for e in bm.edges)
euler=len(bm.verts)-len(bm.edges)+len(bm.faces)
volume=abs(bm.calc_volume(signed=True))
assert bad==0 and euler==-4,('GENUS_OR_NONMANIFOLD_ERROR',bad,euler)
# Verify R03 pixel outlines are recovered in reverse from displayed metric vertices.
actual={(round(float(v.co.x/scale+325),3),round(float(499-v.co.z/scale),3)) for v in bm.verts}
assert actual==reference,('SOURCE_TRACING_ROUNDTRIP_DRIFT',len(actual),len(reference),len(actual.symmetric_difference(reference)))
pos=[o.matrix_world @ v.co for v in bm.verts]
mins=[min(p[i] for p in pos) for i in range(3)]
maxs=[max(p[i] for p in pos) for i in range(3)]
dimensions=[(maxs[i]-mins[i])*1000 for i in range(3)]
expected=[2400.,180.,src['outline_height_pixels']*scale*1000]
for a,b in zip(dimensions,expected):assert abs(a-b)<.025,(a,b)
expected_volume=src['stone_face_area_in_source_px2']*scale**2*.18
assert abs(volume-expected_volume)<1e-8,(volume,expected_volume)
assert abs(volume*1000-q['volume_litres'])<1e-5
assert len(bm.verts)==q['vertex_count']
out={'test':'R50 independent GLB return to R03 source-coordinate tracing',
 'Blender':bpy.app.version_string,
 'objects':1,'source_contour_rings':4,'source_apertures':3,
 'raw_GLB_vertices':raw_count,'welded_vertices':len(bm.verts),
 'raw_nonmanifold_edges':raw_broken,
 'postweld_nonmanifold_edges':bad,
 'Euler_characteristic':euler,
 'physical_dimensions_mm':dimensions,
 'source_visual_width_mm_assumed':2400,
 'display_depth_mm_assumed':180,
 'source_vertex_exact_after_inverse_mapping':True,
 'volume_litres':volume*1000,
 'historical_geometry_certified':False,
 'actual_window_source_scale_verified':False,
 'user_rib_profile_used':False,
 'pass':True}
bm.free()
file=R/('R50_GLb_roundtrip_'+bpy.app.version_string.split()[0].replace('.','_')+'.json')
file.write_text(json.dumps(out,indent=2))
print('R50_IMPORT_PASS',json.dumps({'Blender':out['Blender'],'raw':raw_count,
  'vertices':out['welded_vertices'],'through_holes':3,'source_pixel_trace_match':True,
  'volume_litres':volume*1000}))
