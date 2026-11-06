bl_info={"name":"F5ZP R17 — Fast Experimental Gothic Vault Workspace",
         "author":"Cathedral F5ZP experimental research",
         "version":(0,17,0),"blender":(5,0,0),
         "location":"3D View > Sidebar > R17 Vault",
         "description":"Rebuild experimental vault webs using strict R16 crown and lock guards",
         "category":"3D View"}
import bpy
import pathlib,json,hashlib,sys,math,traceback
from dataclasses import asdict
from bpy.props import (EnumProperty,IntProperty,FloatProperty,
                       BoolProperty,PointerProperty)
ADDON_ROOT=pathlib.Path(__file__).resolve().parent
VENDOR=ADDON_ROOT/'r17_vendor'
sys.path.insert(0,str(VENDOR))
from strict_crown_guard import (enforce,preferred_crown,
    CrownBelowArchApex,LockedGeometryChange)
import r17_core as core

MASTER='R17_WORKSPACE'
GEO_COLLECTION='R17_EXPERIMENTAL_GEOMETRY'
REF_COLLECTION='R17_PROTECTED_BASELINE__READ_ONLY_REGISTER'
WORKSPACE='R17_FAST_UNIVERSAL'
FAMILIES=[('TRI','3 groins','Triangular plan'),
          ('QUAD','4 groins','Four-sector vault'),
          ('PENTA','5 groins','Five-sector test'),
          ('HEXA','6 groins','Six-sector test'),
          ('OCTA','8 groins','Eight-sector test'),
          ('CUSTOM','Custom 3–12','Custom radial plan')]
QUALITY=[('FAST','FAST — 32','Quick web-shape iteration'),
         ('FINAL','FINAL — 128','Detailed surface inspection')]
COLORS={'WEB':(.60,.74,.67,1.),
        'RIB':(.70,.46,.23,1.),
        'BOUNDARY':(.24,.52,.76,1.)}
def current_master():
    sc=bpy.data.scenes.get(MASTER)
    if sc is None:raise RuntimeError('R17_WORKSPACE scene missing; run bootstrap')
    return sc

def _config(props):
    return core.Settings(vault_type=props.vault_type,
       custom_sectors=props.custom_sectors,quality=props.quality,
       radius=props.radius,spring_Z=props.spring_z,
       arch_rise_ratio=props.arch_rise_ratio,
       crown_mode=props.crown_mode,crown_Z=props.crown_z,
       crown_locked=props.crown_locked,irregularity=props.irregularity,
       rotation_degrees=props.rotation_degrees,
       meridian_exponent=props.meridian_exponent,
       dome_lift=props.dome_lift,cap_enabled=props.cap_enabled,
       cap_Z=props.cap_z).check()

def _sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()

def source_snapshot():
    manifest=ADDON_ROOT/'r17_vendor_sha256.json'
    if not manifest.is_file():raise LockedGeometryChange('R17 source manifest missing')
    expected=json.loads(manifest.read_text())
    originals={}
    for name in ('strict_crown_guard.py','guarded_vault_adapter.py'):
        path=VENDOR/name
        if not path.is_file() or _sha(path)!=expected[name]:
            raise LockedGeometryChange('FROZEN_R16_DEPENDENCY_SHA_MISMATCH: '+name)
        originals[name]=_sha(path)
    originals['r17_core.py']=_sha(ADDON_ROOT/'r17_core.py')
    originals['r17_experimental_workspace.py']=_sha(ADDON_ROOT/'r17_experimental_workspace.py')
    # Full archival sources are not treated as new authority; the verified
    # vendored snapshot is compared against the original R16 SHA ledger.
    return originals

def _material(name,rgba):
    m=bpy.data.materials.get(name)
    if m is None:m=bpy.data.materials.new(name)
    m.diffuse_color=rgba
    return m

def _collection(name,parent=None):
    coll=bpy.data.collections.get(name)
    if coll is None:coll=bpy.data.collections.new(name)
    if parent and coll.name not in parent.children:
        try:parent.children.link(coll)
        except RuntimeError:pass
    return coll

def _mesh_metrics(vertices,faces):
    n=len(vertices)
    if n<4 or not faces:raise ValueError('R17 mesh empty')
    counts={}
    a_sum=0.
    for a,b,c in faces:
        if len({a,b,c})<3:raise ValueError('R17_DEGENERATE_TRIANGLE')
        pa=vertices[a];pb=vertices[b];pc=vertices[c]
        u=[pb[j]-pa[j] for j in range(3)]
        v=[pc[j]-pa[j] for j in range(3)]
        cross=(u[1]*v[2]-u[2]*v[1],
               u[2]*v[0]-u[0]*v[2],
               u[0]*v[1]-u[1]*v[0])
        a2=math.sqrt(sum(x*x for x in cross))
        if a2<=1e-9:raise ValueError('R17_ZERO_AREA_WEB_TRIANGLE')
        a_sum+=a2/2.
        for x,y in ((a,b),(b,c),(c,a)):
            edge=(x,y) if x<y else (y,x)
            counts[edge]=counts.get(edge,0)+1
            if counts[edge]>2:raise ValueError('R17_NONMANIFOLD_EDGE')
    Euler=n-len(counts)+len(faces)
    if Euler!=1:raise ValueError('R17_NOT_TOPOLOGICAL_DISK, Euler='+str(Euler))
    return {'vertices':n,'triangles':len(faces),'edges':len(counts),
       'boundary_edges':sum(x==1 for x in counts.values()),
       'Euler':Euler,'all_areas_positive':True,'area_native_sq':a_sum}

def _display_curve(name,points,collection,material,radius=5):
    path=bpy.data.curves.new(name+'_PATH','CURVE')
    path.dimensions='3D'
    path.resolution_u=2
    path.bevel_depth=radius
    path.bevel_resolution=2
    spline=path.splines.new('POLY')
    spline.points.add(len(points)-1)
    for obj,coord in zip(spline.points,points):
        obj.co=(*map(float,coord),1.)
    curve=bpy.data.objects.new(name,path)
    collection.objects.link(curve)
    path.materials.append(material)
    curve['R17_EXPERIMENTAL_ONLY']=True
    return curve

def _replace_text(name,text):
    block=bpy.data.texts.get(name)
    if block is None:block=bpy.data.texts.new(name)
    block.clear();block.write(text)
    return block

def _set_warning(master,report):
    master['r17_last_status']=report.get('status','UNKNOWN')
    master['r17_last_warnings']=', '.join(report.get('warning_codes',[]))
    master['r17_last_crown_Z']=float(report.get('crown_Z',0.))
    master['r17_last_apex_Z']=float(report.get('highest_apex_Z',0.))
    _replace_text('R17_LAST_GUARD_REPORT.json',json.dumps(report,indent=2))

class R17Settings(bpy.types.PropertyGroup):
    vault_type:EnumProperty(name='Vault type',items=FAMILIES,default='QUAD')
    custom_sectors:IntProperty(name='Custom sectors',default=7,min=3,max=12)
    quality:EnumProperty(name='Geometry quality',items=QUALITY,default='FAST')
    radius:FloatProperty(name='Plan radius (native)',default=1200.,min=200.,max=20000.,precision=1)
    spring_z:FloatProperty(name='Springing Z',default=3000.,precision=1)
    arch_rise_ratio:FloatProperty(name='Pointed arch rise/span',
        default=.72,min=.501,max=1.25,precision=3)
    crown_mode:EnumProperty(name='Crown setting',
        items=[('AUTO','Prefer raised (new)','Compute preferred raised crown'),
               ('LEVEL','Exact arch apex (warn)','Use mathematically exact highest arch apex, avoid UI float32 rounding'),
               ('MANUAL','Manual/locked','Use stated crown elevation')],default='AUTO')
    crown_z:FloatProperty(name='Crown Z',default=4400.,precision=2)
    crown_locked:BoolProperty(name='Crown protected/locked',default=False)
    irregularity:FloatProperty(name='Plan irregularity',default=0.,min=0,max=.25)
    rotation_degrees:FloatProperty(name='Plan rotation',default=0.,min=-180,max=180)
    meridian_exponent:FloatProperty(name='Apex-to-crown curvature',default=1.75,min=1.1,max=4.,precision=2)
    dome_lift:FloatProperty(name='Web convexity',default=.3,min=0.,max=.85,precision=2)
    cap_enabled:BoolProperty(name='Reference cap check',default=False)
    cap_z:FloatProperty(name='Provisional cap Z',default=4700.)

class R17_OT_regenerate(bpy.types.Operator):
    bl_idname='r17.regenerate'
    bl_label='Regenerate Experimental Vault'
    bl_description='Protected R16 preflight then build only R17 synthetic geometry'
    bl_options={'REGISTER','UNDO'}
    def execute(self,context):
        master=current_master()
        try:
            p=master.r17_props
            options=_config(p)
            source_before=source_snapshot()
            # No visual mesh is made before strict R16 acceptance.
            arches=core.measured_boundary_arches(options)
            apex=max(max(pt[2] for pt in a['points_xyz']) for a in arches)
            crown=(preferred_crown(boundary_arches=arches,
                          spring_Z=options.spring_Z)
                          if options.crown_mode=='AUTO' else
                          apex if options.crown_mode=='LEVEL' else options.crown_Z)
            cap=options.cap_Z if options.cap_enabled else None
            kwargs=dict(vault_id='R17_'+options.vault_type,
               crown_Z=crown,boundary_arches=arches,
               spring_Z=options.spring_Z,cap_Z=cap,
               crown_locked=options.crown_locked,
               intended_export='open_intrados')
            pre=enforce(**kwargs,locks_before=source_before,
                        locks_after=source_before,phase='PREBUILD')
            shape=core.build_mesh_data(options,crown)
            if arches!=shape['arches']:
                raise LockedGeometryChange('R17 ORIGINAL_ARCH_PROFILE_MUTATION')
            metric=_mesh_metrics(shape['vertices'],shape['faces'])
            if metric['boundary_edges']!=options.sector_count*options.divisions:
                raise ValueError('R17_BOUNDARY_EDGE_COUNT_MISMATCH')
            # Validate original arches and ribs with the generated geometry.
            if shape['seam_gap_native']>1e-7:
                raise ValueError('R17_SEAM_GAP')
            source_after=source_snapshot()
            post=enforce(**kwargs,web_peak_Z=shape['web_peak_Z'],
                 locks_before=source_before,locks_after=source_after,
                 phase='POSTBUILD')
            extra_warnings=[
                {'code':'SYNTHETIC_STUDY_NOT_APPROVED_CATHEDRAL',
                 'message':'R17 is a procedural testing vault, not a '
                   'measured F5ZN-A or approved historical bay.'},
                {'code':'OPEN_INTRADOS_NOT_STRUCTURE',
                 'message':'Open web; no thickness, coursing, '
                   'bearing capacity or architectural approval.'}]
            post['warnings'].extend(extra_warnings)
            post['warning_codes'].extend(w['code'] for w in extra_warnings)
            report={'status':'R17_VALIDATED_EXPERIMENTAL_BUILD',
                'R16_prebuild':pre,'R16_postbuild':post,
                'geometry_QA':metric,
                'source_SHA_before':source_before,
                'source_SHA_after':source_after,
                'config':asdict(options),'resolved_crown_Z':crown,
                'sector_count':shape['sector_count'],
                'quality_divisions':shape['divisions'],
                'seam_gap_native':shape['seam_gap_native'],
                'web_peak_Z':shape['web_peak_Z'],
                'geometry_source':'isolated procedural test, NOT approved',
                'locked_original_geometry_modified':False,
                'technical_validation':True,
                'geometric_validation':True,
                'historical_validation':False,
                'structural_validation':False}
            if source_before!=source_after:raise LockedGeometryChange(
                'R16_SOURCE_HASH_CHANGED_BEFORE_SCENE_COMMIT')
            # Create all new objects BEFORE removing previous generated objects.
            active=bpy.data.collections.get(GEO_COLLECTION)
            if active is None:raise RuntimeError('R17 active collection missing')
            temp=bpy.data.collections.new('R17_PENDING_VALIDATED_TMP')
            master.collection.children.link(temp)
            try:
                mesh=bpy.data.meshes.new('R17_GEOMETRY_'+options.vault_type)
                mesh.from_pydata(shape['vertices'],[],shape['faces'])
                mesh.update(calc_edges=True)
                obj=bpy.data.objects.new('R17_EXPERIMENT_WEB__OPEN_INTRADOS',mesh)
                temp.objects.link(obj)
                mesh.materials.append(_material('R17_LIMESTONE_WEB',COLORS['WEB']))
                for face in mesh.polygons:face.use_smooth=True
                # Preserve deliberate Gothic grooves as sharp mesh edges.
                points=shape['plan_corners']
                keys=set()
                for k in range(len(points)):
                    for j in range(options.divisions):
                        r0=j/options.divisions
                        r1=(j+1)/options.divisions
                        a=core.interpolated_web_point(options,points,k,0.,r0,crown)
                        b=core.interpolated_web_point(options,points,k,0.,r1,crown)
                        keys.add(frozenset((tuple(round(x,7) for x in a),
                                            tuple(round(x,7) for x in b))))
                sharp=mesh.attributes.get('sharp_edge')
                if sharp is None:sharp=mesh.attributes.new(
                         name='sharp_edge',type='BOOLEAN',domain='EDGE')
                xyz=[tuple(round(float(x),7) for x in v.co)
                     for v in mesh.vertices]
                for i,edge in enumerate(mesh.edges):
                    if frozenset((xyz[edge.vertices[0]],
                                  xyz[edge.vertices[1]])) in keys:
                        sharp.data[i].value=True
                mat_b=_material('R17_POINTED_BOUNDARY',COLORS['BOUNDARY'])
                mat_r=_material('R17_INDEPENDENT_GROINS',COLORS['RIB'])
                for a in shape['arches']:
                    _display_curve(a['id'],a['points_xyz'],temp,mat_b,6)
                for a in shape['ribs']:
                    _display_curve(a['id'],a['points_xyz'],temp,mat_r,8)
                obj['R17_NATIVE_1TO1']=True
                obj['R17_LOCKED_ORIGINAL_GEOMETRY_TOUCHED']=False
                obj['R17_CROWN_Z']=crown
                obj['R17_SOURCE_CONFIG_SHA256']=shape['config_SHA256']
                obj['R17_NUM_SECTORS']=options.sector_count
                obj['R17_QUALITY_DIVISIONS']=shape['divisions']
                # Only R17 owned meshes/curves in active collection removed.
                previous=list(active.objects)
                for thing in list(temp.objects):
                    temp.objects.unlink(thing);active.objects.link(thing)
                for thing in previous:
                    bpy.data.objects.remove(thing,do_unlink=True)
            except Exception:
                for thing in list(temp.objects):
                    bpy.data.objects.remove(thing,do_unlink=True)
                raise
            finally:
                bpy.data.collections.remove(temp)
            # Persist complete QA in internal Text and unique per-build file.
            # Checkpoints may coexist from other runs based on this .blend.
            # Advance to the next unused QA index, NEVER overwrite a record.
            folder=pathlib.Path(master['r17_outputs_dir'])
            folder.mkdir(parents=True,exist_ok=True)
            index=int(master.get('r17_build_count',0))+1
            while (folder/f'R17_BUILD_{index:03d}_QA.json').exists():
                index+=1
            master['r17_build_count']=index
            master['r17_last_build_kind']='SYNTHETIC_1_TO_1'
            master['r17_active_quality']=options.quality
            master['r17_last_crown_Z']=crown
            master['r17_last_apex_Z']=apex
            master['r17_last_status']='VALIDATED_EXPERIMENTAL'
            master['r17_last_warnings']=' | '.join(post['warning_codes'])
            master['r17_last_geometry_hash']=shape['config_SHA256']
            _replace_text('R17_LATEST_COMPLETE_QA.json',json.dumps(report,indent=2))
            _replace_text('R17_LATEST_R16_WARNINGS.json',json.dumps(post,indent=2))
            file=folder/f'R17_BUILD_{index:03d}_QA.json'
            with file.open('x') as handle:
                handle.write(json.dumps(report,indent=2))
            if post['crown_relation']=='LEVEL_WARNING':
                self.report({'WARNING'},'LEVEL CROWN: diminished dome effect. '
                   'LOCKED geometry preserved; see R17 R16 warnings.')
            elif 'PREFER_HIGHER_CROWN' in post['warning_codes']:
                self.report({'WARNING'},'R17 favors higher crown. '
                   'Review locked-geometry warning before accepting.')
            else:
                self.report({'INFO'},f'R17 {options.vault_type}: '
                     f'{options.quality} {metric["triangles"]} triangles; '
                     'R16 locks checked.')
            return {'FINISHED'}
        except Exception as exc:
            failure={'status':'HARD_STOP_GEOMETRY_NOT_COMMITTED',
               'code':type(exc).__name__,'message':str(exc),
               'warning_codes':['LOCKED_GEOMETRY_WARNING_ALWAYS'],
               'warnings':[{'code':'LOCKED_GEOMETRY_WARNING_ALWAYS',
                  'message':'Protected original architecture must '
                     'remain untouched; no output permitted.'}]}
            _replace_text('R17_LAST_GUARD_REPORT.json',json.dumps(failure,indent=2))
            master['r17_last_status']='HARD_STOP'
            master['r17_last_warnings']='LOCKED_GEOMETRY_WARNING_ALWAYS | '+str(exc)
            self.report({'ERROR'},'R17 HARD STOP: '+str(exc)[:190])
            return {'CANCELLED'}

class R17_OT_export_glb(bpy.types.Operator):
    bl_idname='r17.export_glb'
    bl_label='Export Current Test GLB'
    bl_description='Export only the validated R17 web in native full 1:1 coordinates'
    def execute(self,context):
        try:
            master=current_master()
            if master.get('r17_last_status')!='VALIDATED_EXPERIMENTAL':
                raise ValueError('Regenerate successfully before export')
            active=bpy.data.collections.get(GEO_COLLECTION)
            objects=[o for o in active.objects if o.name.startswith(
                        'R17_EXPERIMENT_WEB__') and o.type=='MESH']
            if len(objects)!=1:raise RuntimeError('R17 active vault not unique')
            obj=objects[0]
            if obj.get('R17_SOURCE_CONFIG_SHA256')!=master.get('r17_last_geometry_hash'):
                raise LockedGeometryChange('R17 mesh differs from last validated setup')
            dest=pathlib.Path(master['r17_outputs_dir'])
            dest.mkdir(parents=True,exist_ok=True)
            idx=int(master['r17_build_count'])
            path=dest/f'R17_BUILD_{idx:03d}_OPEN_INTRADOS_1TO1.glb'
            if path.exists():raise FileExistsError('GLB exists; no overwrite: '+str(path))
            prior={o.name:o.select_get() for o in context.view_layer.objects}
            for o in context.view_layer.objects:o.select_set(False)
            obj.select_set(True)
            oldactive=context.view_layer.objects.active
            context.view_layer.objects.active=obj
            try:
                bpy.ops.export_scene.gltf(filepath=str(path),
                    export_format='GLB',use_selection=True,
                    export_apply=True)
            finally:
                context.view_layer.objects.active=oldactive
                for o in context.view_layer.objects:
                    o.select_set(prior.get(o.name,False))
            if path.stat().st_size<4096:
                raise RuntimeError('GLB invalid size')
            self.report({'INFO'},'Experimental GLB exported (1:1); '
                'locked cathedral baseline unchanged.')
            return {'FINISHED'}
        except Exception as exc:
            self.report({'ERROR'},'R17 export blocked: '+str(exc)[:190])
            return {'CANCELLED'}

class R17_OT_save_checkpoint(bpy.types.Operator):
    bl_idname='r17.save_checkpoint'
    bl_label='Save Versioned R17 Checkpoint'
    bl_description='Save a new experimental .blend checkpoint; never overwrite earlier versions'
    def execute(self,context):
        try:
            master=current_master()
            if master.get('r17_last_status')!='VALIDATED_EXPERIMENTAL':
                raise RuntimeError('Build a validated experimental vault first')
            root=pathlib.Path(master['r17_checkpoints_dir'])
            root.mkdir(parents=True,exist_ok=True)
            k=int(master.get('r17_checkpoint_count',0))+1
            file=root/f'R17_FAST_VAULT_WORKSPACE_CHECKPOINT_{k:03d}_EXPERIMENTAL.blend'
            if file.exists():raise FileExistsError('Version exists; refusing overwrite')
            master['r17_checkpoint_count']=k
            bpy.ops.wm.save_as_mainfile(filepath=str(file),compress=True)
            if not file.exists():raise RuntimeError('Blender save did not complete')
            self.report({'INFO'},'Saved versioned R17 working file: '+file.name)
            return {'FINISHED'}
        except Exception as exc:
            self.report({'ERROR'},'R17 checkpoint blocked: '+str(exc)[:170])
            return {'CANCELLED'}

class R17_OT_change_view(bpy.types.Operator):
    bl_idname='r17.review_view'
    bl_label='Open Selected R17 Review'
    bl_description='Switch among shared-geometry R17 review camera scenes'
    view:EnumProperty(items=[
       ('R17_WORKSPACE','Working view','Interactive modeling'),
       ('R17_REVIEW_AXON','Axonometric','Overall volume'),
       ('R17_REVIEW_PLAN','Plan','2D bay and rib footprint'),
       ('R17_REVIEW_INTERIOR','Underside','Interior vault view'),
       ('R17_REVIEW_SECTION','Section','Side elevation')])
    def execute(self,context):
        if self.view not in bpy.data.scenes:
            self.report({'ERROR'},'R17 view missing: '+self.view)
            return {'CANCELLED'}
        context.window.scene=bpy.data.scenes[self.view]
        for area in context.screen.areas:
            if area.type=='VIEW_3D':
                region=area.spaces.active.region_3d
                if region:region.view_perspective='CAMERA'
        return {'FINISHED'}

class R17_PT_main(bpy.types.Panel):
    bl_label='R17 Fast Vault Workshop'
    bl_idname='R17_PT_main'
    bl_space_type='VIEW_3D'
    bl_region_type='UI'
    bl_category='R17 Vault'
    def draw(self,context):
        ui=self.layout
        try:
            sc=current_master()
        except RuntimeError:
            ui.label(text='R17 scene missing. Run R17 bootstrap.',icon='ERROR')
            return
        props=sc.r17_props
        header=ui.box()
        header.label(text='EXPERIMENTAL • 1:1 native units',icon='LOCKED')
        header.label(text='R16 crown + locked geometry guard')
        head=ui.column(align=True)
        head.prop(props,'vault_type')
        if props.vault_type=='CUSTOM':head.prop(props,'custom_sectors')
        head.prop(props,'quality',expand=True)
        head.prop(props,'radius')
        head.prop(props,'irregularity')
        head.prop(props,'rotation_degrees')
        arch=ui.box()
        arch.label(text='Pointed arches and crown',icon='CURVE_DATA')
        arch.prop(props,'spring_z')
        arch.prop(props,'arch_rise_ratio')
        arch.prop(props,'crown_mode')
        if props.crown_mode=='MANUAL':
            arch.prop(props,'crown_z')
        arch.prop(props,'crown_locked')
        if props.crown_locked and props.crown_mode!='MANUAL':
            r=arch.row();r.alert=True
            r.label(text='LOCKED crown cannot auto-change!',icon='ERROR')
        shape=ui.box()
        shape.label(text='Smooth web controls',icon='MOD_SMOOTH')
        shape.prop(props,'meridian_exponent')
        shape.prop(props,'dome_lift')
        shape.prop(props,'cap_enabled')
        if props.cap_enabled:shape.prop(props,'cap_z')
        ui.operator('r17.regenerate',text='REGENERATE TEST VAULT',icon='FILE_REFRESH')
        row=ui.row(align=True)
        row.operator('r17.export_glb',text='Export GLB 1:1',icon='EXPORT')
        row.operator('r17.save_checkpoint',text='Save .blend',icon='FILE_TICK')
        status=ui.box()
        current=sc.get('r17_last_status','NO BUILD')
        status.label(text='Status: '+str(current)[:44],
                     icon='CHECKMARK' if current=='VALIDATED_EXPERIMENTAL'
                        else 'ERROR')
        if 'r17_last_apex_Z' in sc:
            status.label(text='Arch apex Z '+format(sc['r17_last_apex_Z'],'.2f'))
            status.label(text='Crown Z '+format(sc['r17_last_crown_Z'],'.2f'))
        codes=str(sc.get('r17_last_warnings','')).split(' | ')
        for code in codes[:5]:
            if code:
                row=status.row()
                row.alert=bool('LEVEL' in code or 'HARD_STOP' in code)
                row.label(text=code[:46],icon='ERROR' if row.alert else 'INFO')
        status.label(text='R16 locked-geometry warning always active',
                     icon='LOCKED')
        reviews=ui.box()
        reviews.label(text='Reusable review scenes',icon='CAMERA_DATA')
        for item,name in [
          ('R17_REVIEW_AXON','Axon'),
          ('R17_REVIEW_PLAN','Plan'),
          ('R17_REVIEW_INTERIOR','Underside'),
          ('R17_REVIEW_SECTION','Section')]:
            op=reviews.operator('r17.review_view',text=name)
            op.view=item
        ui.label(text='Historic vaults and baseline are untouched.')
        ui.label(text='See R17_LATEST_COMPLETE_QA.json (Text Editor).')

CLASSES=(R17Settings,R17_OT_regenerate,R17_OT_export_glb,
         R17_OT_save_checkpoint,R17_OT_change_view,R17_PT_main)
def register():
    for cls in CLASSES:
        try:bpy.utils.register_class(cls)
        except ValueError:pass
    if not hasattr(bpy.types.Scene,'r17_props'):
        bpy.types.Scene.r17_props=PointerProperty(type=R17Settings)

def unregister():
    if hasattr(bpy.types.Scene,'r17_props'):
        del bpy.types.Scene.r17_props
    for cls in reversed(CLASSES):
        try:bpy.utils.unregister_class(cls)
        except RuntimeError:pass

if __name__=='__main__':register()
