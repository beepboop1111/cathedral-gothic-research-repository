"""V19 R02 experimental connected vault network. Run with Blender --python.
The bundled v19_core.py is copied byte-for-byte from the R01 experiment.
"""
import bpy, sys, json, math, copy, hashlib, time, struct
from pathlib import Path
from mathutils import Vector
from bpy.props import FloatProperty, FloatVectorProperty, IntProperty, BoolProperty, CollectionProperty

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import v19_core as core
COL = 'V19_R02_NETWORK_EXPERIMENTAL'
N = 32
BUSY = False

def digest(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True).encode()).hexdigest()

def initial_config(parent):
    c = {k: copy.deepcopy(parent[k]) for k in ('hermite', 'units', 'vertical_axis', 'handedness')}
    c.update(revision='V19_R02_15_VAULTS_EXPERIMENTAL', nodes={}, arches={}, vaults={}, translation=[45,-30,35])
    for j in range(4):
        for i in range(6):
            c['nodes'][f'n{i}_{j}'] = [i*920+45*math.sin(i*1.3+j*.8), j*900+40*math.sin(i*.7-j*1.1), 0]
    c['shared_nodes'] = ['n3_1', 'n3_2']
    for j in range(3):
        for i in range(5):
            ns=[f'n{i}_{j}',f'n{i+1}_{j}',f'n{i+1}_{j+1}',f'n{i}_{j+1}']; es=[]
            for k,a in enumerate(ns):
                b=ns[(k+1)%4]; ends=sorted((a,b)); key=':'.join(ends)
                c['arches'].setdefault(key,dict(ends=ends,rise=.86*math.dist(c['nodes'][a][:2],c['nodes'][b][:2])))
                es.append([key,a!=ends[0]])
            pts=[c['nodes'][n] for n in ns]
            c['vaults'][f'V{j*5+i+1:02d}']=dict(corners=ns,edges=es,
                boss=[sum(p[0] for p in pts)/4+25*math.sin(i+j),sum(p[1] for p in pts)/4+20*math.cos(i-j),1150+45*((i+2*j)%5)],
                meridian_strength=.55+.12*((2*i+j)%6),exponent=1.75,dome_lift=.18)
    c['selected_shared_arch']=':'.join(sorted(c['shared_nodes']))
    c['source_lineage']='V19 R01 kernel + normalized R12B meridian; synthetic 3 x 5 network, not cathedral set-out'
    return c

def plan_checks(g):
    """Convex separating-axis test excludes overlapping web interiors."""
    polys={k:[g.nodes[n] for n in v['corners']] for k,v in g.vaults.items()}
    margins=[]
    for i,(a,P) in enumerate(polys.items()):
        for b,Q in list(polys.items())[i+1:]:
            overlaps=[]
            for poly in (P,Q):
                for k,p in enumerate(poly):
                    q=poly[(k+1)%len(poly)]; ax,ay=p[1]-q[1],q[0]-p[0]; norm=math.hypot(ax,ay)
                    x=[(ax*v[0]+ay*v[1])/norm for v in P]; y=[(ax*v[0]+ay*v[1])/norm for v in Q]
                    overlaps.append(min(max(x),max(y))-max(min(x),min(y)))
            margin=min(overlaps)
            if margin>1e-6: raise ValueError(f'PLAN_INTERIOR_OVERLAP {a} {b}')
            margins.append(margin)
    return dict(pair_count=len(margins),maximum_interior_overlap=max(0,max(margins)),method='Convex separating axes; all web triangles must have positive signed XY area')

def protected():
    for p,h in json.loads((ROOT/'PROTECTED_HASHES.json').read_text()).items():
        if core.sha(p)!=h: raise RuntimeError('PROTECTED_SOURCE_CHANGED '+p)
    return True

def material(name,col):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name); m.diffuse_color=(*col,1); return m

def curve(name,pts,mat,radius,col):
    data=bpy.data.curves.new(name,'CURVE'); data.dimensions='3D'; data.bevel_depth=radius; data.bevel_resolution=1
    s=data.splines.new('POLY'); s.points.add(len(pts)-1)
    for p,v in zip(s.points,pts): p.co=(*v,1)
    data.materials.append(mat); ob=bpy.data.objects.new(name,data); col.objects.link(ob)
    ob['DISPLAY_TUBE_NOT_MASONRY']=True
    return ob

def mesh_signature(g,v,n):
    return digest([v,{k:g.nodes[k] for k in v['corners']},{k:g.arches[k] for k,r in v['edges']},g.cfg['hermite'],n])

def build(sc,cfg,n=N):
    global BUSY
    started=time.perf_counter(); protected()
    g=core.Graph(cfg); sqa=g.validate(); sqa['plan_partition']=plan_checks(g)
    # Preflight is complete before any mesh generation or saved-model mutation.
    prepared={}; metrics={}; reused=[]; old=bpy.data.collections.get(COL)
    try:
        for vid,v in g.vaults.items():
            sig=mesh_signature(g,v,n); existing=old.objects.get('WEB_'+vid) if old else None
            if existing and existing.get('input_signature')==sig:
                prepared[vid]=existing; metrics[vid]=json.loads(existing['mesh_QA']); reused.append(vid); continue
            V,F=g.mesh(v,n); q=g.webqa(v,V,F,n)
            data=bpy.data.meshes.new('NETWORK_'+vid); data.from_pydata(V,[],F); data.update()
            if data.validate(verbose=False): raise ValueError('BLENDER_MESH_REPAIR_REQUIRED')
            for p in data.polygons:p.use_smooth=True
            idx=int(vid[1:]); data.materials.append(material('WEB_COLOR_'+str(idx%5),[(.73,.81,.86),(.85,.76,.61),(.65,.78,.73),(.79,.70,.82),(.78,.80,.62)][idx%5]))
            ob=bpy.data.objects.new('STAGED_WEB_'+vid,data); ob['input_signature']=sig; ob['mesh_QA']=json.dumps(q); ob['OPEN_INTRADOS_NOT_MASONRY']=True
            prepared[vid]=ob; metrics[vid]=q
        seam=0.; matches=0
        for key,users in sqa['shared_registry'].items():
            sets=[{tuple(v.co) for v in prepared[vid].data.vertices} for vid in users]
            for j in range(n+1):
                expected=Vector(g.arch(key,j/n)); rounded=tuple(Vector(expected))
                if any(rounded not in pts for pts in sets): raise ValueError('SHARED_MESH_STATION_MISSING '+key)
                seam=max(seam,math.dist(rounded,g.arch(key,j/n))); matches+=1
        if seam>.002: raise ValueError('FLOAT32_SEAM_TOLERANCE')
    except Exception:
        for ob in prepared.values():
            if ob.name.startswith('STAGED_'):
                data=ob.data; bpy.data.objects.remove(ob,do_unlink=True); bpy.data.meshes.remove(data)
        raise
    stage=bpy.data.collections.new(COL+'_STAGED')
    gold=material('SHARED_ARCH_GOLD',(1,.52,.05)); dark=material('BOUNDARY_ARCH',(.12,.17,.23)); blue=material('GROINS',(.03,.28,.62)); red=material('MERIDIAN_GUIDES',(.7,.04,.05))
    for key in g.arches:
        ob=curve('ARCH_'+key,[g.arch(key,j/128) for j in range(129)],gold if key in sqa['shared_registry'] else dark,5,stage)
        ob['skeleton_id']=key; ob['authoritative']=True
    for vid,v in g.vaults.items():
        for k in range(4):
            curve('GROIN_'+vid+'_'+str(k),[g.groin(v,k,j/96) for j in range(97)],blue,3,stage)
            ob=curve('MERIDIAN_'+vid+'_'+str(k),[g.meridian(v,k,j/64) for j in range(65)],red,1.1,stage); ob.hide_render=True; ob.hide_viewport=True
    for vid,ob in prepared.items(): stage.objects.link(ob)
    sc.collection.children.link(stage)
    if old:
        for ob in list(old.objects):
            if ob in prepared.values(): old.objects.unlink(ob)
            else:
                data=ob.data; bpy.data.objects.remove(ob,do_unlink=True)
                if data.users==0:
                    (bpy.data.meshes if isinstance(data,bpy.types.Mesh) else bpy.data.curves).remove(data)
        bpy.data.collections.remove(old)
    stage.name=COL
    for vid,ob in prepared.items(): ob.name='WEB_'+vid
    qa=dict(status='EXPERIMENTAL_GEOMETRIC_PASS',skeleton=sqa,webs=metrics,actual_float32_arch_residual_native=seam,
        matched_shared_mesh_stations=matches,shared_mesh_neighbor_gap_native=0.,reused_webs=reused,generated_webs=[v for v in g.vaults if v not in reused],
        divisions=n,triangles=sum(q['triangles'] for q in metrics.values()),elapsed_seconds=time.perf_counter()-started,
        technical='Build passed; fresh session and GLB checks recorded separately',geometric='Open surfaces: convex disjoint plans, positive XY triangle areas, disk topology, skeleton and sampled mesh interfaces',
        architectural='Synthetic test only; not approved cathedral set-out',historical='R12B normalized meridian lineage only; new network not historically validated',structural='NOT ASSESSED; no thickness, loads, roofs or neighboring cathedral solids',F5ZL_C='UNRESOLVED')
    sc['network_config']=json.dumps(cfg); sc['network_QA']=json.dumps(qa); sc['network_status']='WEBS_VALIDATED'; sc['network_divisions']=n
    return qa

def inputs(sc):
    cfg=json.loads(sc['network_base_config']); cfg['translation']=[a if b==struct.unpack('f',struct.pack('f',a))[0] else b for a,b in zip(cfg['translation'],sc.network_shift)]
    for p in sc.network_vaults:
        v=cfg['vaults'][p.name]; f32=lambda x:struct.unpack('f',struct.pack('f',x))[0]
        if p.crown!=f32(v['boss'][2]):v['boss'][2]=p.crown
        if p.meridian!=f32(v['meridian_strength']):v['meridian_strength']=p.meridian
    return cfg

def auto_update(self,context):
    if BUSY or not context or not context.scene.get('network_base_config'):return
    sc=context.scene; sc['network_status']='INPUTS_CHANGED'
    if sc.network_auto and not bpy.app.timers.is_registered(timer):bpy.app.timers.register(timer,first_interval=.35)

def timer():
    sc=bpy.context.scene
    try: build(sc,inputs(sc),sc.network_divisions)
    except Exception as e: sc['network_status']='REJECTED; LAST VALID MODEL RETAINED: '+str(e)
    return None

class NetworkVault(bpy.types.PropertyGroup):
    crown:FloatProperty(name='Crown Z',update=auto_update)
    meridian:FloatProperty(name='Meridian amplitude',default=1,min=0,max=2,update=auto_update)

class NetworkBuild(bpy.types.Operator):
    bl_idname='network.rebuild'; bl_label='Validate skeleton and update webs'; bl_options={'REGISTER','UNDO'}
    def execute(self,context):
        try:build(context.scene,inputs(context.scene),context.scene.network_divisions); return {'FINISHED'}
        except Exception as e:self.report({'ERROR'},str(e)); return {'CANCELLED'}

class NetworkPanel(bpy.types.Panel):
    bl_label='V19 R02: 15 connected vaults'; bl_idname='NETWORK_PT_v19'; bl_space_type='VIEW_3D'; bl_region_type='UI'; bl_category='V19 Network'
    def draw(self,context):
        sc=context.scene; l=self.layout
        l.label(text='EXPERIMENTAL | native units | Z up'); l.prop(sc,'network_auto'); l.prop(sc,'network_shift'); l.prop(sc,'network_divisions')
        l.operator('network.rebuild'); l.label(text=sc.get('network_status','READY')[:70])
        for p in sc.network_vaults:
            box=l.box(); box.label(text=p.name); box.prop(p,'crown'); box.prop(p,'meridian')

def register(sc):
    global BUSY
    BUSY=True
    for cls in (NetworkVault,NetworkBuild,NetworkPanel):
        if not cls.is_registered:bpy.utils.register_class(cls)
    if not hasattr(bpy.types.Scene,'network_shift'):
        bpy.types.Scene.network_shift=FloatVectorProperty(name='Selected shared arch XYZ shift',size=3,update=auto_update)
        bpy.types.Scene.network_vaults=CollectionProperty(type=NetworkVault)
        bpy.types.Scene.network_auto=BoolProperty(name='Automatic validated updates',default=True)
        bpy.types.Scene.network_divisions=IntProperty(name='Web subdivisions',default=N,min=16,max=96,update=auto_update)
    cfg=json.loads(sc['network_config']); sc.network_shift=cfg['translation']; sc.network_vaults.clear()
    for vid,v in cfg['vaults'].items():
        p=sc.network_vaults.add(); p.name=vid; p.crown=v['boss'][2]; p.meridian=v['meridian_strength']
    sc.network_divisions=sc.get('network_divisions',N); BUSY=False

def export_glb(sc):
    bpy.ops.object.select_all(action='DESELECT'); temp=[]
    for ob in bpy.data.collections[COL].objects:
        if ob.name.startswith('MERIDIAN_'):continue
        if ob.type=='CURVE':
            data=bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()))
            cp=bpy.data.objects.new(ob.name+'_EXPORT',data); sc.collection.objects.link(cp); cp.select_set(True); temp.append(cp)
        else: ob.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(ROOT/'V19_R02_15_VAULTS_1TO1.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
    for ob in temp:
        data=ob.data; bpy.data.objects.remove(ob,do_unlink=True); bpy.data.meshes.remove(data)
    bpy.ops.object.select_all(action='DESELECT')

def batch():
    cfg=json.loads((ROOT/'NETWORK_CONFIG.json').read_text()); sc=bpy.context.scene; sc.name='V19_R02_15_VAULTS'
    for ob in list(bpy.data.objects):bpy.data.objects.remove(ob,do_unlink=True)
    sc['network_base_config']=json.dumps(cfg); sc['network_config']=json.dumps(cfg); register(sc)
    qa=build(sc,cfg); hashes={v:digest([tuple(x.co) for x in bpy.data.objects['WEB_'+v].data.vertices]) for v in cfg['vaults']}
    # No-op rebuild must reuse every validated web; a crown edit affects one web.
    no_op=build(sc,cfg); assert len(no_op['reused_webs'])==15
    edit=copy.deepcopy(cfg); edit['vaults']['V01']['boss'][2]+=35
    one=build(sc,edit); assert one['generated_webs']==['V01'] and len(one['reused_webs'])==14
    restored=build(sc,cfg); assert restored['generated_webs']==['V01']
    bad=copy.deepcopy(cfg); bad['vaults']['V01']['boss'][2]=-1
    try:build(sc,bad)
    except ValueError:pass
    else:raise AssertionError('INVALID_CROWN_ACCEPTED')
    assert all(hashes[v]==digest([tuple(x.co) for x in bpy.data.objects['WEB_'+v].data.vertices]) for v in cfg['vaults'])
    key=cfg['selected_shared_arch']; base=copy.deepcopy(cfg); base['translation']=[0,0,0]; g=core.Graph(cfg); b=core.Graph(base)
    rigid=max(math.dist(g.arch(key,j/256),core.add(b.arch(key,j/256),cfg['translation'])) for j in range(257))
    assert rigid<1e-7
    qa['regression']=dict(no_op_reused=15,one_crown_edit_regenerated=one['generated_webs'],unaffected_meshes_reused=14,invalid_crown_preserved_last_valid_meshes=True,restoration_exact=True,shared_arch_rigid_translation_max_residual=rigid,source_hashes_unchanged=protected())
    sc['network_QA']=json.dumps(qa)
    V=[v.co for ob in bpy.data.collections[COL].objects if ob.type=='MESH' for v in ob.data.vertices]
    lo=Vector([min(v[i] for v in V) for i in range(3)]); hi=Vector([max(v[i] for v in V) for i in range(3)]); target=(lo+hi)/2
    data=bpy.data.cameras.new('NETWORK_CAMERA'); cam=bpy.data.objects.new('NETWORK_CAMERA',data); sc.collection.objects.link(cam)
    cam.location=target+Vector((3800,-6200,5800)); cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler(); data.type='ORTHO'; data.ortho_scale=7200; data.clip_end=50000; sc.camera=cam
    sc.render.engine='BLENDER_WORKBENCH'; sc.render.resolution_x=1600; sc.render.resolution_y=1100; sc.render.resolution_percentage=100
    sh=sc.display.shading; sh.light='STUDIO'; sh.color_type='MATERIAL'; sh.show_cavity=True; sh.cavity_type='BOTH'; sh.show_shadows=True; sh.background_type='WORLD'
    sc.world.color=(.10,.12,.15)
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                area.spaces.active.clip_end=50000; area.spaces.active.region_3d.view_perspective='CAMERA'; area.spaces.active.shading.color_type='MATERIAL'; area.spaces.active.show_region_ui=True
    export_glb(sc)
    sc.render.filepath=str(ROOT/'V19_R02_REVIEW.png'); bpy.ops.render.render(write_still=True)
    for name in ('network_workspace.py','v19_core.py','NETWORK_CONFIG.json'):
        tx=bpy.data.texts.get(name) or bpy.data.texts.new(name); tx.clear(); tx.write((ROOT/name).read_text())
    tx=bpy.data.texts.new('RUN_NETWORK_UI.py'); tx.write("import bpy,sys\nsys.path.insert(0,"+repr(str(ROOT))+")\nimport network_workspace as nw\nnw.register(bpy.context.scene)\n")
    (ROOT/'NUMERICAL_QA.json').write_text(json.dumps(qa,indent=2)); bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'V19_R02_NETWORK_EXPERIMENTAL.blend'),compress=True)
    print('NETWORK_BUILD_PASS',json.dumps({k:qa[k] for k in ('triangles','actual_float32_arch_residual_native','elapsed_seconds','regression')}),flush=True)

if __name__=='__main__':
    if '--batch' in sys.argv:batch()
    else:register(bpy.context.scene)
