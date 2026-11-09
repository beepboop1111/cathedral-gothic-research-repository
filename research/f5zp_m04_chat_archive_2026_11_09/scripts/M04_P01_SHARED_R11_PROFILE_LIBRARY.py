#!/usr/bin/env python3
"""M04 P01 uses unchanged R11 profile_input.convert and the source ZIP."""
from pathlib import Path
from collections import Counter
import csv,hashlib,importlib.util,io,json,math,re,sys,zipfile
import cv2,numpy as np
from PIL import Image,ImageDraw
from shapely.geometry import Polygon,shape
from shapely.ops import unary_union
SRC=Path("/home/christopher/Downloads/downlods/3/french gothic profiles with optional soffets.zip")
ENGINE=Path("/home/christopher/Documents/Cathedral/experimental/SPRINGER_PROFILE_INPUT_R11/profile_input.py")
R=Path("/home/christopher/Downloads/downlods/F5ZP_R12C_FULL_PLAN_BLENDER_EXPERIMENTAL")
O=R/"M04_P01_R11_SHARED_PROFILE_LIBRARY_EXPERIMENTAL"
assert not O.exists(),"Earlier experimental output protected"
for folder in ("isolated_source_png","R11_section_json","svg"): (O/folder).mkdir(parents=True,exist_ok=True)
baseline={
 "R06":R/"M04_R06_V12_PROFILE_RECOVERY_EXPERIMENTAL/M04_R06_EIGHT_ORIGINAL_PROFILES_AND_COMPOUND_PIER_1TO1.geojson",
 "R05":R/"M04_R05_R1_78_EXACT_COMPOUND_PIER_2D_FOOTPRINT_EXPERIMENTAL/M04_R05_EIGHT_CURRENT_PLAN_BEARING_AXES_AND_MEASURED_PIER_FACE_CONTACTS.csv",
 "R11":R/"R11_FULL_COORDINATED_2D_EXPERIMENTAL/F5ZP_R11_COORDINATED_NATIVE_2D.geojson",
 "M02":R/"F5ZP_M02_CONSOLIDATED_CHECKPOINT_R01_LOCAL/CHECKPOINT/phase_d/D_WORKING_FLOORPLAN_SEVEN_OUTER_ONLY.geojson"}
inputs={"ZIP":SRC,"EXISTING_R11_IMPORTER":ENGINE,**baseline}
assert all(x.is_file() for x in inputs.values()),inputs
sha={name:hashlib.sha256(p.read_bytes()).hexdigest() for name,p in inputs.items()}
spec=importlib.util.spec_from_file_location("shared_profile_r11_source",str(ENGINE))
module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
def to_csv(p,records):
 fields=sorted(set().union(*(x.keys() for x in records)))
 with p.open("w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(records)
assets=[];inventory=[]
with zipfile.ZipFile(SRC) as z:
 files=sorted(x for x in z.namelist() if x.lower().endswith(".png"))
 assert len(files)==38
 for file in files:
  raw=z.read(file)
  a=cv2.imdecode(np.frombuffer(raw,np.uint8),cv2.IMREAD_UNCHANGED)
  gray=cv2.cvtColor(a[:,:,:3],cv2.COLOR_BGR2GRAY) if a.ndim==3 else a
  alpha=a[:,:,3] if a.ndim==3 and a.shape[2]==4 else np.full(gray.shape,255,np.uint8)
  mask=((gray<128)&(alpha>127)).astype(np.uint8)
  n,labels,stats,_=cv2.connectedComponentsWithStats(mask,8)
  groups=sorted((i for i in range(1,n) if stats[i,4]>=max(1000,int(mask.size*.005))),key=lambda i:(stats[i,1],stats[i,0]))
  kind="optional_soffit" if "soffet" in Path(file).name.lower() else "numbered_profile"
  inventory.append({"file":file,"sha256":hashlib.sha256(raw).hexdigest(),"components":len(groups),"kind":kind,"width":a.shape[1],"height":a.shape[0]})
  for idx,i in enumerate(groups,1):
   x,y,w,h,area=map(int,stats[i])
   pad=4
   crop=np.full((h+2*pad,w+2*pad),255,np.uint8)
   crop[pad:pad+h,pad:pad+w][labels[y:y+h,x:x+w]==i]=0
   id=Path(file).stem.replace(" ","_")+f"__{idx:02}"
   png=O/"isolated_source_png"/(id+".png")
   cv2.imwrite(str(png),crop)
   row={"id":id,"original_file":file,"source_sha256":hashlib.sha256(raw).hexdigest(),
        "component_number":idx,"source_bbox_xywh":str([x,y,w,h]),"source_black_pixels":area,
        "type":kind,"isolated_png":"isolated_source_png/"+id+".png",
        "orientation":"up provisional (NOT validated)","approval":"EXPERIMENTAL"}
   try:
    section=module.convert(png,width=1.0,depth=None,nose="up",mirror=False,threshold=128,simplify=.55)
    poly=Polygon(section["section"])
    assert poly.is_valid and poly.area>0
    section.update({"source_original_file":file,"source_original_sha256":row["source_sha256"],
                    "component_index":idx,"optional_soffit":kind=="optional_soffit",
                    "historical_nose_orientation_validated":False,"source_proportions_flexible":True,
                    "profile_role_assigned":False})
    (O/"R11_section_json"/(id+".json")).write_text(json.dumps(section,indent=2)+"\n")
    points=" ".join(f"{u:.8f},{-v:.8f}" for u,v in section["section"])
    (O/"svg"/(id+".svg")).write_text(
     f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-0.55 {-section["depth"]-.05:.8f} 1.10 {section["depth"]+.10:.8f}"><polygon points="{points}" fill="none" stroke="#000" stroke-width="0.008"/></svg>\n')
    row.update({"state":"PASS","R11_schema":section["schema"],"points":section["vertices"],
                "depth_width_ratio":round(section["depth"]/section["width"],8),
                "contour_area_width1":round(poly.area,8)})
   except Exception as error:row.update({"state":"REVIEW_REQUIRED","error":str(error)})
   assets.append(row)
assert len(inventory)==38
to_csv(O/"source_38_images.csv",inventory)
to_csv(O/"isolated_components_and_contour_measurements.csv",assets)
# Existing original R06 floorplan and original 8 bearing table remain fixtures.
f={x["properties"]["id"].removesuffix("_0"):shape(x["geometry"]) for x in json.loads(baseline["R06"].read_text())["features"]}
core=f["ORIGINAL_PIER_Y2800"]
xy=np.array(json.loads(baseline["R06"].read_text())["properties"]["trial_origin_global_XY"])
bearing=list(csv.DictReader(baseline["R05"].open()))
assert len(bearing)==8
clear=unary_union([shape(x["geometry"]) for x in json.loads(baseline["R11"].read_text())["features"] if x["properties"]["role"]=="CLEAR"])
walls=unary_union([shape(x["geometry"]) for x in json.loads(baseline["M02"].read_text())["features"] if x["properties"]["role"]=="USER_CONFIRMED_FIRST_WALL_MEASURED_BAND"])
dims={"Doubleau":38.159911,"D ogive":35.99999,"U1 longitudinal":33.517707}
ratios={"Doubleau":64.678384/38.159911,"D ogive":59.887163/35.99999,"U1 longitudinal":49.999907/33.517707}
fits=[]
for a in assets:
 if a["state"]!="PASS" or a["type"]=="optional_soffit":continue
 src=np.array(json.loads((O/"R11_section_json"/(a["id"]+".json")).read_text())["section"])
 for factor in (.8,1.,1.2):
  for b in bearing:
   width=dims[b["source_family"]]*factor
   uv=src*width
   depth=float(np.ptp(uv[:,1]))
   theta=math.radians(float(b["F5ZKC_target_plan_heading_from_trial_center_deg"]))
   out=np.array([math.cos(theta),math.sin(theta)])
   side=np.array([-math.sin(theta),math.cos(theta)])
   # A 42%-depth position is a sensitivity assumption, NOT an actual origin
   # or user-approved piercing/bearing relation.
   world=xy+np.outer(uv[:,0],side)+np.outer(uv[:,1]-.42*depth,out)
   poly=Polygon(world)
   pc=poly.intersection(clear).area if poly.is_valid else float("inf")
   wc=poly.intersection(walls).area if poly.is_valid else float("inf")
   overlap=poly.intersection(core).area if poly.is_valid else 0
   status="2D_CLEAR_PROVISIONAL" if pc<.0001 and wc<.0001 and overlap>1 else "REVIEW_REQUIRED"
   fits.append({"id":a["id"],"member":b["name"],"family":b["source_family"],"width_factor":factor,
     "scaled_width_native":round(width,4),"scaled_depth_native":round(depth,4),
     "overlap_original_core_native_sq":round(overlap,5),
     "protected_vault_overlap_sq":round(pc,5),"first_wall_overlap_sq":round(wc,5),
     "status":status,"soffit_attached":False,"orientation":"up provisional",
     "architectural_fit_approved":False})
to_csv(O/"M04_2D_R06_R08_ALTERNATIVE_PROFILE_FIT_MATRIX.csv",fits)
summaries=[]
for a in assets:
 if a["state"]!="PASS" or a["type"]=="optional_soffit":continue
 rows=[x for x in fits if x["id"]==a["id"] and x["width_factor"]==1.0]
 summaries.append({"id":a["id"],"original_file":a["original_file"],
  "width1_depth_ratio":a["depth_width_ratio"],"vertices":a["points"],
  "closest_original_V12_ratio_family":min(ratios,key=lambda r:abs(ratios[r]-a["depth_width_ratio"])),
  "source_original_family_selection_NOT_implied":True,
  "provisional_2d_clear_count_at_reference_scale":sum(x["status"]=="2D_CLEAR_PROVISIONAL" for x in rows),
  "current_8_member_context_tests":len(rows)})
to_csv(O/"M04_profile_family_proportion_comparison.csv",summaries)
# Single actual-source review PNG (no invented reference illustration).
ok=[x for x in assets if x["state"]=="PASS"]
cols=10;cw=150;ch=174
im=Image.new("RGB",(cols*cw,math.ceil(len(ok)/cols)*ch+78),(248,249,251))
draw=ImageDraw.Draw(im)
draw.text((10,12),"M04 P01  |  actual 38 PNG source components / R11 shared converter",fill=(20,32,40))
draw.text((10,35),"Source artwork isolated; proportions preserved; nose direction provisional; optional soffits independent",fill=(70,79,88))
for i,a in enumerate(ok):
 col=i%cols;row=i//cols;x=col*cw;y=row*ch+65
 with Image.open(O/a["isolated_png"]) as item:
  item.thumbnail((135,127),Image.Resampling.LANCZOS)
  im.paste(item,(x+(cw-item.width)//2,y+5+(128-item.height)//2))
 draw.rectangle((x+1,y+1,x+cw-2,y+ch-2),outline=(180,190,196))
 draw.text((x+6,y+137),a["id"],fill=(25,35,45))
 draw.text((x+6,y+151),f"ratio {a['depth_width_ratio']:.2f}",fill=(95,99,103))
im.save(O/"M04_P01_ALL_ORIGINAL_SILHOUETTES_REVIEW.png")
report={"status":"SOURCE LIBRARY VECTOR EXTRACTION AND PROVISIONAL PLAN FIT",
"source_png_count":len(inventory),"isolated_source_component_count":len(assets),
"R11_schema_validated_count":len(ok),"needs_manual_cleanup_count":len(assets)-len(ok),
"rejections":[a for a in assets if a["state"]!="PASS"],
"optional_soffit_components":sum(a["type"]=="optional_soffit" for a in assets),
"alternative_section_plan_tests":len(fits),
"provisionally_plan_clear":sum(x["status"]=="2D_CLEAR_PROVISIONAL" for x in fits),
"scale":"uniform adjustable, preserve original silhouette ratio",
"orientation_verified":False,"historical_member_roles_assigned":False,
"automatic_soffit_merges":False,"source_SHA256":sha,
"existing_R11_converter_unchanged":True,"original_R06_R08_models_unchanged":True,
"structural_and_architectural_approval":False}
(O/"M04_P01_PROFILE_LIBRARY_QA.json").write_text(json.dumps(report,indent=2)+"\n")
(O/"HANDOFF.md").write_text("""# M04 P01 shared original Gothic profiles and sectional fit

Uses original 38-image ZIP and unchanged SPRINGER_PROFILE_INPUT_R11/profile_input.py. Isolate each black source silhouette; independently call the existing converter to produce actual springer_png_section_v1 JSON and SVG, preserving the source raster and SHA256. Optional soffit/face silhouettes stay separate. The default nose=up is a PROVISIONAL conversion direction, not a confirmed historic orientation. Uniform scaling can vary; changing width and depth independently would need a declared deliberate distort operation rather than silently corrupting original proportions.

Reference plan fit tests use the M04 R05 source eight directions and R06 original Y2800 floor footprint. At nominal V12 member widths and ±20% widths, all valid numbered profiles are tried with a provisional 42%-depth anchor, against all original 218 clear vault polygons and seven first-wall bands. This is only 2D screening, not a measured actual future spring connection, soffit fit, pier design or architectural approval. The true F5ZN-A formerets of M04 R08 differ from the older V13 U1 regime; no automatic role assignment. All prior scripts, source geometry, approved cathedral geometry and GitHub remain untouched.
""")
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==sha[k] for k,p in inputs.items())
print("M04_P01_QA",json.dumps({k:report[k] for k in ("source_png_count","isolated_source_component_count","R11_schema_validated_count","needs_manual_cleanup_count","optional_soffit_components","alternative_section_plan_tests","provisionally_plan_clear")}))
