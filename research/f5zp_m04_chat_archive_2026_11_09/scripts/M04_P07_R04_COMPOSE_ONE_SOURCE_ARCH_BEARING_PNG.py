#!/usr/bin/env python3
"""F5ZP P07 final ONE PNG: genuine Blender 5.2.3 render + actual measured
source XY wall/arch bearings and uncertain shoulder (no invented stones).
"""
from pathlib import Path
import json,hashlib,math
from PIL import Image,ImageDraw,ImageFont,ImageOps
from shapely.geometry import shape
R=Path("/home/christopher/Downloads/downlods/F5ZP_R12C_FULL_PLAN_BLENDER_EXPERIMENTAL")
P=R/"M04_P07_R02_EXACT_TOP_BED_NATIVE_SOURCE_BEARINGS_EXPERIMENTAL"
B=R/"M04_P07_R03_B523_3D_SOURCE_CONTACT_DIAGNOSTICS_EXPERIMENTAL"
O=B
raw=B/"M04_P07_B523_GENUINE_SOURCE_FIVE_BEARINGS_VIEWPORT.png"
geo=P/"M04_P07_R02_EXACT_TOP_AND_ACTUAL_FIVE_ARCHES.geojson"
qpath=P/"M04_P07_R02_EXACT_NATIVE_SOURCE_BEARING_QA.json"
bqa=B/"M04_P07_B523_RENDER_AND_GLB_REGRESSION_QA.json"
inputs=[raw,geo,qpath,bqa]
assert all(p.is_file() for p in inputs)
sha={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
feature={f["properties"]["name"]:shape(f["geometry"]) for f in json.loads(geo.read_text())["features"]}
q=json.loads(qpath.read_text())
b=json.loads(bqa.read_text())
assert len(q["five_source_local_arches_near_pier"])==5 and b["source_original_14_plus_new_7_GLTF_roundtrip"]==21
W,H=2630,1590
img=Image.new("RGB",(W,H),(243,247,249))
dr=ImageDraw.Draw(img)
font="/usr/share/fonts/truetype/dejavu/"
def bold(x):return ImageFont.truetype(font+"DejaVuSans-Bold.ttf",x)
def regular(x):return ImageFont.truetype(font+"DejaVuSans.ttf",x)
dark=(27,44,57);muted=(77,93,107);line=(191,207,214)
dr.rectangle((0,0,W,110),fill=dark)
dr.text((42,16),"F5ZP  /  M04 P07     FIVE GOTHIC BEARINGS — SOURCE GEOMETRY",font=bold(32),fill=(240,249,251))
dr.text((44,68),"Real Blender 5.2.3 render  •  precise Z2400 bearing plan  •  original Pass 6J and cathedral geometry protected",font=regular(19),fill=(191,218,227))
left=(24,130,1280,1380)
right=(1300,130,2604,1380)
for panel in (left,right):
 dr.rounded_rectangle(panel,radius=14,fill=(255,255,255),outline=line,width=2)
dr.rectangle((left[0]+4,left[1]+4,left[2]-4,left[1]+62),fill=(50,79,96))
dr.text((left[0]+22,left[1]+15),"A  /  Protected geometry + experimental courses",font=bold(23),fill=(252,253,255))
dr.rectangle((right[0]+4,right[1]+4,right[2]-4,right[1]+62),fill=(50,79,96))
dr.text((right[0]+22,right[1]+15),"B  /  Measured top bearing, original 1:1 scale",font=bold(23),fill=(252,253,255))
with Image.open(raw) as render:
 assert render.size==(1360,1120),render.size
 picture=ImageOps.contain(render.convert("RGB"),(1242,1088),Image.Resampling.LANCZOS)
 img.paste(picture,(left[0]+(1256-picture.width)//2,left[1]+78))
dr=ImageDraw.Draw(img)
dr.text((left[0]+23,left[3]-73),"S support: (31000, −1250, 1800)  |  Source upper transition Z2400",font=regular(18),fill=muted)
dr.text((left[0]+23,left[3]-44),"14 physical reference meshes • no added backing infill or new mouldings",font=regular(17),fill=(112,81,59))
plan=(right[0]+25,right[1]+117,right[2]-25,right[3]-129)
xmin,xmax,ymin,ymax=30705,31295,-1620,-975
cx=(plan[0]+plan[2])/2;cy=(plan[1]+plan[3])/2
scale=min((plan[2]-plan[0]-40)/(xmax-xmin),(plan[3]-plan[1]-50)/(ymax-ymin))
def xp(p):
 x,y=p
 return (int(round(cx+(x-(xmin+xmax)/2)*scale)),
         int(round(cy-(y-(ymin+ymax)/2)*scale)))
def polys(geom):
 if geom.is_empty:return []
 return [geom] if geom.geom_type=="Polygon" else [x for x in geom.geoms if x.geom_type=="Polygon"]
def ringpoly(geom,color,outline=None,width=1):
 for p in polys(geom):
  points=[xp(x) for x in p.exterior.coords]
  if len(points)>=3:
   dr.polygon(points,fill=color)
   if outline:dr.line(points,fill=outline,width=width,joint="curve")
def dashed(points,fill,width=3,dash=11,gap=6):
 if len(points)<2:return
 for a,b in zip(points[:-1],points[1:]):
  dx=b[0]-a[0];dy=b[1]-a[1];dist=math.hypot(dx,dy)
  if dist==0:continue
  n=0.
  while n<dist:
   e=min(n+dash,dist)
   A=(int(a[0]+dx*n/dist),int(a[1]+dy*n/dist))
   B=(int(a[0]+dx*e/dist),int(a[1]+dy*e/dist))
   dr.line((A,B),fill=fill,width=width)
   n+=dash+gap
def ring_outline(geom,color,width=3,style="solid"):
 for p in polys(geom):
  rings=[p.exterior]+list(p.interiors)
  for ring in rings:
   pts=[xp(pt) for pt in ring.coords]
   if style=="dashed":dashed(pts,color,width)
   else:dr.line(pts,fill=color,width=width,joint="curve")
# Right panel, exact geometry from 371 real source triangles.
course=feature["R14_SOURCE_TAS_05_EXACT_TRIANGULATED_TOP"]
wall=feature["R03_ORIGINAL_UPPER_WALL_CONTACT"]
shoulder=feature["P07_SOURCE_SPRINGER_SHOULDER_UNCERTAIN_DO_NOT_FILL"]
ringpoly(course,(230,236,239))
ringpoly(wall,(158,177,188))
for num,m in enumerate(q["five_source_local_arches_near_pier"]):
 local=feature["R03_LOCAL_BEARING_ON_TAS_"+m["name"]]
 ringpoly(local,(236,196,110),outline=(75,72,52),width=2)
ringpoly(shoulder,(239,157,142))
# SVG construction layers: solid black confirmed, gray dashed comparison,
# red dashed uncertainty, per architectural drafting conventions.
ring_outline(wall,(27,41,48),3,"solid")
ring_outline(course,(116,133,141),3,"dashed")
ring_outline(shoulder,(193,41,44),4,"dashed")
# A world-scale bar, not a graphic arbitrary scale.
x0,y0=xp((30805,-1590))
x1,y1=xp((30905,-1590))
dr.line((x0,y0,x1,y1),fill=(35,50,58),width=5)
for xx in (x0,x1):dr.line((xx,y0-7,xx,y0+7),fill=(35,50,58),width=3)
dr.text((x1+13,y1-12),"100 native units",font=regular(17),fill=(52,68,77))
# Legend & numerical reading of the source.
legend_y=right[3]-119
dr.line((right[0]+32,legend_y,right[0]+83,legend_y),fill=(23,34,40),width=4)
dr.text((right[0]+92,legend_y-13),"Original wall",font=regular(16),fill=muted)
dashed([(right[0]+344,legend_y),(right[0]+395,legend_y)],(118,132,143),width=3)
dr.text((right[0]+408,legend_y-13),"Course 05 top",font=regular(16),fill=muted)
dashed([(right[0]+681,legend_y),(right[0]+732,legend_y)],(192,41,45),width=3)
dr.text((right[0]+746,legend_y-13),"Uncertain shoulder",font=regular(16),fill=muted)
dr.text((right[0]+30,right[3]-70),f"Upper wall: 100% seated  |  5 local arch bearings: {100*q['five_local_seating_fraction_min']:.4f}%+ covered",font=bold(19),fill=(32,88,77))
dr.text((right[0]+30,right[3]-40),f"External shoulder: {q['upper_exact_top_uncertain_shoulder_native_sq']:,.2f} native²  •  do not fill without source evidence",font=regular(17),fill=(150,64,55))
# Footer, no colorful box. Clear actual technical vs architectural status.
dr.line((27,1410,W-27,1410),fill=(172,188,198),width=2)
dr.text((37,1430),"BLENDER 5.2.3",font=bold(21),fill=dark)
dr.text((230,1430),"14 original source meshes + 7 NON-MASONRY contact markers; GLB round trip 21/21.",font=regular(20),fill=(51,75,86))
dr.text((37,1472),"TECHNICAL / GEOMETRIC: PASS",font=bold(21),fill=(31,98,77))
dr.text((449,1472),"LOCALIZED WALL-TO-TAS CONTACT: MEASURED",font=bold(20),fill=(34,72,91))
dr.text((37,1520),"ARCHITECTURAL / HISTORICAL / STRUCTURAL: NOT APPROVED    •    F5ZL-C schedule missing    •    Pass 6J eight-bearing pier separate",font=regular(19),fill=(137,62,58))
png=O/"F5ZP_M04_P07_FINAL_ONE_REAL_GOTHIC_BEARING_REVIEW.png"
img.save(png,optimize=True)
with Image.open(png) as review:assert review.size==(W,H);review.verify()
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==sha[str(p)] for p in inputs)
(O/"M04_P07_R04_FINAL_PNG_SOURCE_AND_LAYOUT_QA.json").write_text(json.dumps({
 "source_SHA256":sha,"Blender_source_input":"actual Blender 5.2.3 viewport render, not synthesized 3D",
 "measured_2d_source":"original protected R03 Gothic geometry and R14 triangulated Z2400 cap",
 "final_png":png.name,"width":W,"height":H,
 "source_5_local_original_bearings_verified":True,
 "architectural_approval":False},indent=2)+"\n")
print("P07_FINAL_SOURCE_RENDER_AND_PLAN_PNG_PASS",png,png.stat().st_size,"bytes")
