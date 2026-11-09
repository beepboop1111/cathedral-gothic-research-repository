#!/usr/bin/env python3
"""Experimental small raster-hole repair for Gothic profile 11.
Original PNG and P01 rejection remain protected and unchanged.
"""
import sys,hashlib,json,importlib.util
from pathlib import Path
import cv2,numpy as np
from shapely.geometry import Polygon
R=Path("/home/christopher/Downloads/downlods/F5ZP_R12C_FULL_PLAN_BLENDER_EXPERIMENTAL")
P01=R/"M04_P01_R11_SHARED_PROFILE_LIBRARY_EXPERIMENTAL"
P02=R/"M04_P02_R17_TRUE_PROFILE_REGENERATION_EXPERIMENTAL"
ENGINE=Path("/home/christopher/Documents/Cathedral/experimental/SPRINGER_PROFILE_INPUT_R11/profile_input.py")
original=P01/"isolated_source_png/11__01.png"
output=P02/"PROFILE_11_TINY_HOLE_RASTER_REPAIR_CANDIDATE.png"
assert original.is_file() and not output.exists()
before=hashlib.sha256(original.read_bytes()).hexdigest()
image=cv2.imread(str(original),cv2.IMREAD_GRAYSCALE)
foreground=((image<128).astype(np.uint8)*255)
contours,h=cv2.findContours(foreground,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_NONE)
assert h is not None and len(contours)==2
parents=h[0]
hole=[i for i,t in enumerate(parents) if t[3]>=0]
assert len(hole)==1
hole_area=float(cv2.contourArea(contours[hole[0]]))
assert hole_area<=3
clean=foreground.copy()
cv2.drawContours(clean,contours,hole[0],color=255,thickness=-1)
change=(clean!=foreground)
assert not np.any((foreground==255)&change)
count=int(np.count_nonzero(change))
assert 0<count<=9,(count,hole_area)
repaired=255-clean
assert cv2.imwrite(str(output),repaired)
spec=importlib.util.spec_from_file_location("originalR11",str(ENGINE))
mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
result=mod.convert(output,width=141.2507,depth=None,nose="left",mirror=False,threshold=128,simplify=.55)
assert result["schema"]=="springer_png_section_v1"
assert Polygon(result["section"]).is_valid
assert hashlib.sha256(original.read_bytes()).hexdigest()==before
# Record original two contour loops, preserving its topology for future source debate.
paths=[]
for i,c in enumerate(contours):
 pts=c.reshape(-1,2)
 xy=" ".join(f"{int(x)},{int(y)}" for x,y in pts)
 paths.append(f"M {xy.split()[0]} L "+" L ".join(xy.split()[1:])+" Z")
w,h=image.shape[1],image.shape[0]
(P02/"PROFILE_11_UNTOUCHED_SOURCE_HOLE_VECTOR_FOR_REVIEW.svg").write_text(
 f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}"><path d="{" ".join(paths)}" fill="#000" fill-rule="evenodd"/></svg>\n')
qa={"source_profile_id":"11__01",
 "status":"EXPERIMENTAL DERIVATIVE ONLY; original source retained",
 "original_source_png_sha256":before,
 "original_internal_holes":1,"original_contour_hole_area_pixel_sq":hole_area,
 "actual_raster_pixels_white_to_black":count,
 "original_dark_pixel_count":int(np.count_nonzero(foreground)),
 "fraction_total_source_mask_changed":round(count/foreground.size,9),
 "new_derivative_png_SHA256":hashlib.sha256(output.read_bytes()).hexdigest(),
 "new_R11_section_valid":True,"new_section_vertices":result["vertices"],
 "source_engine_unchanged":True,
 "original_profile_interpretation_needs_review":True}
(P02/"PROFILE_11_EXPLICIT_TINY_HOLE_REPAIR_QA.json").write_text(json.dumps(qa,indent=2)+"\n")
print("EXPERIMENTAL_11_TINY_RASTER_REPAIR_PASS",count,"pixels, original area",hole_area,"derivative source R11 valid")
