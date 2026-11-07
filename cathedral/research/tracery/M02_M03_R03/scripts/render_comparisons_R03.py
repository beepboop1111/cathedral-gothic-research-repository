"""Run in Blender: matched reference STL / candidate GLB renders and import audit."""
import bpy
import json
import math
import sys
from pathlib import Path
from mathutils import Vector, Matrix

argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
root=Path(argv[0]).resolve()
names=argv[1:] or ['meaux','haina_1264','haina_1265','chalons']
out=root/'comparisons';out.mkdir(exist_ok=True)
auditfile=root/'qa/blender_import_render_R03.json'
audits=json.loads(auditfile.read_text()) if auditfile.exists() else []
audits=[a for a in audits if a['name'] not in names]
for name in names:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene
    scene.render.engine='BLENDER_WORKBENCH'
    shade=scene.display.shading
    shade.light='STUDIO';shade.color_type='MATERIAL'
    shade.show_cavity=True;shade.cavity_type='BOTH'
    shade.curvature_ridge_factor=.8;shade.curvature_valley_factor=1.1
    shade.background_type='VIEWPORT';shade.background_color=(.95,.95,.95)
    scene.display.render_aa='16'
    scene.cycles.device='CPU';scene.cycles.samples=24
    scene.cycles.use_denoising=False
    scene.render.resolution_x=1200;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    scene.render.film_transparent=False
    scene.render.threads_mode='FIXED';scene.render.threads=4
    scene.world=bpy.data.worlds.new('Soft studio')
    scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.78,.80,.82,1)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35
    scene.view_settings.view_transform='AgX'
    scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
    mat=bpy.data.materials.new('Neutral limestone comparison');mat.use_nodes=True;mat.diffuse_color=(.7,.66,.58,1)
    bsdf=mat.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=(.57,.51,.42,1);bsdf.inputs['Roughness'].default_value=.352
    bpy.ops.wm.stl_import(filepath=str(root/'baseline/models'/f'{name}_R02_reproduced.stl'),global_scale=.001)
    before=[o for o in bpy.context.selected_objects if o.type=='MESH'][0];before.name=f'{name}_R02_reference_mm_to_m'
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.import_scene.gltf(filepath=str(root/'experimental/models'/f'{name}_M02_R03.glb'))
    after=[o for o in bpy.context.selected_objects if o.type=='MESH'][0];after.name=f'{name}_M02_R03_EXPERIMENTAL'
    # Blender imports glTF Y-up as Blender Z-up. Inverse rotation aligns the
    # review object to the STL XY plane; exported files are never changed.
    after.matrix_world=Matrix.Rotation(-math.pi/2,4,'X') @ after.matrix_world
    bpy.context.view_layer.update()
    for obj in [before,after]:
        obj.data.materials.clear();obj.data.materials.append(mat)
        obj['status']='Reference reproduction' if obj==before else 'Experimental; no promotion'
        for p in obj.data.polygons:p.use_smooth=False
    def bounds(obj):
        ps=[obj.matrix_world@Vector(c) for c in obj.bound_box]
        return [[min(p[i] for p in ps) for i in range(3)],[max(p[i] for p in ps) for i in range(3)]]
    bb=bounds(before);ab=bounds(after)
    audits.append({'name':name,'blender_version':bpy.app.version_string,'reference_vertices':len(before.data.vertices),'reference_faces':len(before.data.polygons),'candidate_glb_vertices':len(after.data.vertices),'candidate_faces':len(after.data.polygons),'reference_bounds_m':bb,'candidate_glb_bounds_m':ab,'bounds_max_delta_mm':max(abs(bb[j][i]-ab[j][i])*1000 for i in range(3) for j in range(2)),'render_engine':'Blender Workbench studio/cavity; technical shading of the actual triangle mesh', 'view':'matched orthographic camera, material, light; inverse glTF-to-Blender axis rotation on review object only; no geometry modifiers','units':'meters in Blender and GLB; source STL mm converted by 0.001', 'reference_import_note':'Blender STL importer discards some zero-area reference faces; original topology QA uses untouched STL in an independent reader'})
    center=Vector([(bb[0][i]+bb[1][i])/2 for i in range(3)])
    span=max(bb[1][i]-bb[0][i] for i in [0,1])
    bpy.ops.object.camera_add();camera=bpy.context.object;scene.camera=camera;camera.data.type='ORTHO';camera.data.ortho_scale=span*1.23
    def point_camera(position):
        camera.location=position;camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
    for label,offset,energy,size in [('Key',(-.7,.8,1.5),.6,.25),('Fill',(.9,-.4,.8),.2,.2)]:
        bpy.ops.object.light_add(type='AREA',location=center+Vector(offset)*span)
        light=bpy.context.object;light.name=label;light.data.energy=energy;light.data.shape='DISK';light.data.size=size
        light.rotation_euler=(center-light.location).to_track_quat('-Z','Y').to_euler()
    bpy.ops.mesh.primitive_plane_add(size=span*200,location=(center.x,center.y,-.004))
    plane=bpy.context.object;plane.name='Review backdrop (not geometry)';plane.hide_render=True
    backmat=bpy.data.materials.new('Backdrop');backmat.diffuse_color=(.91,.92,.93,1);plane.data.materials.append(backmat)
    views={'front':Vector((0,0,2.8))*span,'oblique':Vector((.48,-.38,2.2))*span}
    for view,delta in views.items():
        point_camera(center+delta)
        bpy.context.view_layer.update()
        local=[camera.matrix_world.inverted()@(before.matrix_world@Vector(c)) for c in before.bound_box]
        projected_width=max(p.x for p in local)-min(p.x for p in local)
        projected_height=max(p.y for p in local)-min(p.y for p in local)
        camera.data.ortho_scale=max(projected_width,projected_height*(scene.render.resolution_x/scene.render.resolution_y))*1.14
        for tag,obj in [('before',before),('after',after)]:
            before.hide_render=obj!=before;after.hide_render=obj!=after
            scene.render.filepath=str(out/f'{name}_{view}_{tag}_R03.png')
            bpy.ops.render.render(write_still=True)
    before.hide_render=True;before.hide_set(True);after.hide_render=False
    if name=='meaux':
        point_camera(center+views['oblique'])
        bpy.context.view_layer.objects.active=after
        bpy.ops.object.select_all(action='DESELECT');after.select_set(True)
        bpy.ops.wm.save_as_mainfile(filepath=str(root/'experimental/models/meaux_M02_R03_REVIEW.blend'),compress=True)
    (root/'qa/blender_import_render_R03.json').write_text(json.dumps(audits,indent=2))
    print('COMPLETED_WINDOW',name,flush=True)
