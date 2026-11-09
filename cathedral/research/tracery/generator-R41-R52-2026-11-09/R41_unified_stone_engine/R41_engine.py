"""R41 unified experimental stone-body engine (Blender 5.1+).
Baseline: R32 Ayr fig.8 2D publication tracing; NOT historical joint evidence.
Coordinates in meters, Blender scene scale_length=1.0.
No approval, GitHub, external file modification, or actual cathedral mesh.
"""
from __future__ import annotations
import csv, json, hashlib, math
from dataclasses import dataclass
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
import bpy, bmesh

@dataclass(frozen=True)
class StoneSpec:
    name: str
    length_mm: float=300.
    joint_deg: float=0.
    joint_offset_mm: float=0.
    curvature_mm: float=0.
    taper_pct: float=0.
    evidence: str='EXPERIMENTAL'
    def validate(self, profile_height_mm):
        if not (40.<=self.length_mm<=1500.):raise ValueError('LENGTH_OUT_OF_RANGE')
        if not (-50.<=self.joint_deg<=50.):raise ValueError('ANGLE_OUT_OF_RANGE')
        if abs(self.curvature_mm)>self.length_mm/3:raise ValueError('CURVATURE_TOO_HIGH')
        if abs(self.taper_pct)>30:raise ValueError('TAPER_OUT_OF_RANGE')
        if abs(self.joint_offset_mm)+.5*profile_height_mm*abs(math.tan(math.radians(self.joint_deg)))>=self.length_mm*.45:
            raise ValueError('JOINT_OUTSIDE_BOTH_STONE_ENVELOPES')
        if self.evidence!='EXPERIMENTAL':raise ValueError('NO_CERTIFIED_JOINT_EVIDENCE')

def read_ayr_r32_profile(csv_path: Path, report_path: Path):
    if not csv_path.is_file() or not report_path.is_file():raise FileNotFoundError('R32 input missing')
    rows=list(csv.DictReader(csv_path.open(newline='')))
    meta=json.loads(report_path.read_text())
    scale=meta['calibration']['mm_per_rendered_pixel']/1000.
    xsL=[float(r['source_left_x_px']) for r in rows]
    xsR=[float(r['source_right_x_px']) for r in rows]
    ys=[float(r['source_y_px']) for r in rows]
    assert len(xsL)>50
    center=(min(xsL)+max(xsR))/2
    ztop=max(ys)
    points=[((x-center)*scale,(ztop-y)*scale) for x,y in zip(xsL,ys)]
    points.extend(((x-center)*scale,(ztop-y)*scale) for x,y in zip(reversed(xsR),reversed(ys)))
    if len(points)<6:raise ValueError('PROFILE_TOO_SHORT')
    if abs(polygon_area(points))<1e-8:raise ValueError('PROFILE_ZERO_AREA')
    if polygon_area(points)<0:points.reverse()
    if has_self_intersections(points):raise ValueError('SELF_INTERSECTING_PROFILE')
    return points, {'name':'Ayr fragment 8 / published figure 8, 1985','evidence':'2D scaled publication drawing',
      'profile_sha256':hashlib.sha256(csv_path.read_bytes()).hexdigest(),
      'measurement_limit':'NOT an authenticated 3D stone scan'}

def polygon_area(poly):
    return .5*sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1]))

def orientation(a,b,c):
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])

def has_self_intersections(poly):
    # Fast finite ring self-intersection gate: skip neighboring edges.
    n=len(poly)
    for i in range(n):
        a=poly[i];b=poly[(i+1)%n]
        for j in range(i+2,n):
            if i==0 and j==n-1:continue
            c=poly[j];d=poly[(j+1)%n]
            o1=orientation(a,b,c);o2=orientation(a,b,d)
            o3=orientation(c,d,a);o4=orientation(c,d,b)
            if (o1*o2< -1e-19) and (o3*o4< -1e-19):return True
    return False

def stock_config(points):
    return {'width_mm':(max(p[0] for p in points)-min(p[0] for p in points))*1000.,
            'height_mm':(max(p[1] for p in points)-min(p[1] for p in points))*1000.}

def triangles(points):
    vectors=[Vector((x,z,0)) for x,z in points]
    coords={(round(v.x,10),round(v.y,10)):i for i,v in enumerate(vectors)}
    faces=tessellate_polygon([vectors])
    idx=[]
    for tri in faces:
        indices=list(tri) if isinstance(tri[0],int) else [coords[(round(v.x,10),round(v.y,10))] for v in tri]
        if len(set(indices))==3:idx.append(tuple(indices))
    if len(idx)!=len(points)-2:raise ValueError('INVALID_SECTION_TRIANGULATION')
    return idx

def spec_coords(profile, spec, t):
    # t is a smooth longitudinal coordinate. For curved paths the shared junction
    # becomes a non-planar ruled/tessellated surface; never label this a planar bed.
    length=spec.length_mm/1000.
    amp=spec.curvature_mm/1000.
    base_shift=amp*(1.-(2.*t/length)**2)
    slope=-8.*amp*t/(length**2)
    norm=math.sqrt(1.+slope*slope)
    pct=spec.taper_pct/100.
    width_scale=1.+pct*(2*t/length)
    return base_shift,slope,norm,width_scale

def ring(profile,spec,tfn):
    center_z=(max(z for x,z in profile)+min(z for x,z in profile))*.5
    length=spec.length_mm/1000.
    result=[]
    for x,z in profile:
        t=tfn(z,center_z)
        shift,derivative,norm,width_scale=spec_coords(profile,spec,t)
        ex=x*width_scale/norm
        result.append(Vector((shift+ex,t-x*width_scale*derivative/norm,z)))
    return result

def make_ring_mesh(name,r0,r1,cap_tris,collection,material,source_meta,code='R41',triangulate_sides=False):
    n=len(r0)
    vertices=[tuple(v) for v in r0]+[tuple(v) for v in r1]
    faces=[(i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n)]
    faces.extend(cap_tris)
    faces.extend(tuple(n+i for i in reversed(t)) for t in cap_tris)
    mesh=bpy.data.meshes.new(name+'_mesh')
    mesh.from_pydata(vertices,[],faces)
    mesh.update(calc_edges=True)
    obj=bpy.data.objects.new(name,mesh);collection.objects.link(obj)
    if material:mesh.materials.append(material)
    bm=bmesh.new();bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    if triangulate_sides:
        # GLB silently triangulates non-planar quads with a different diagonal than
        # Blender's polygon-volume calculation. Fix triangulation deterministically
        # in the generator BEFORE volume QA/export. R39 straight baseline unchanged.
        quads=[f for f in bm.faces if len(f.verts)==4]
        if quads:bmesh.ops.triangulate(bm,faces=quads,quad_method='BEAUTY')
    if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
    bm.to_mesh(mesh);bm.free();mesh.update()
    obj['evidence_class']='EXPERIMENTAL'
    obj['original_joint_authenticated']=False
    obj['source_2d_profile_sha256']=source_meta['profile_sha256']
    obj['source_specimen']=source_meta['name']
    obj['consolidated_engine']=code
    return obj

def mesh_info(obj):
    bm=bmesh.new();bm.from_mesh(obj.data)
    non=sum(not e.is_manifold for e in bm.edges)
    count=len(bm.verts)
    volume=bm.calc_volume(signed=True)
    bm.free()
    if non:raise ValueError('MESH_NONMANIFOLD')
    if volume<=0:raise ValueError('MESH_NEGATIVE_VOLUME')
    return {'verts':count,'nonmanifold':non,'volume_m3':volume}

def contact_tris_area_normal(points,tris):
    area=0.;summed=Vector()
    for t in tris:
        a,b,c=(points[i] for i in t)
        n=(b-a).cross(c-a)
        area+=n.length*.5
        summed+=n*.5
    return area,summed.normalized()

def build_pair(profile,source_meta,spec,collection,mats=(None,None)):
    size=stock_config(profile)
    spec.validate(size['height_mm'])
    L=spec.length_mm/1000.
    jo=spec.joint_offset_mm/1000.
    tlo=lambda z,c:-L/2
    thi=lambda z,c:L/2
    tm=lambda z,c:jo+math.tan(math.radians(spec.joint_deg))*(z-c)
    cap=triangles(profile)
    first=ring(profile,spec,tlo)
    seam=ring(profile,spec,tm)
    last=ring(profile,spec,thi)
    # Triangulated side surfaces are essential for curved or tapered non-planar quads.
    use_tri=(abs(spec.curvature_mm)>1e-10 or abs(spec.taper_pct)>1e-10)
    objA=make_ring_mesh(spec.name+'_A',first,seam,cap,collection,mats[0],source_meta,triangulate_sides=use_tri)
    objB=make_ring_mesh(spec.name+'_B',seam,last,cap,collection,mats[1],source_meta,triangulate_sides=use_tri)
    qaA=mesh_info(objA);qaB=mesh_info(objB)
    area,nrm=contact_tris_area_normal(seam,cap)
    # Per-triangle seam geometry is identical in both meshes, despite non-planar curved surfaces.
    assert all((objA.data.vertices[len(profile)+i].co-objB.data.vertices[i].co).length<=1e-9 for i in range(len(profile)))
    return (objA,objB),{'spec':spec.__dict__,'objects':[qaA,qaB],
      'combined_volume_m3':qaA['volume_m3']+qaB['volume_m3'],
      'contact_area_mm2':area*1e6,'contact_vertices':len(seam),
      'contact_seam_linear_gap_m':max((objA.data.vertices[len(profile)+i].co-objB.data.vertices[i].co).length for i in range(len(profile))),
      'shared_contact_normal_mathematical_opposition':True,
      'seam_type':'NONPLANAR_RIBBON' if (abs(spec.curvature_mm)>1e-10 or abs(spec.taper_pct)>1e-10) else 'PLANE',
      'source_category':'2D_SURVEY_PLUS_EXPERIMENT'}
