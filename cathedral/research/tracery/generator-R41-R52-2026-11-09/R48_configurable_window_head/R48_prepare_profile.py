#!/usr/bin/env python3
"""R48 file-to-profile preparation utility (system Python, Blender not required).
Takes one selected archival PNG or zip member, keeps aspect ratio,
cuts an explicitly experimental rectangular rebate and emits R43 profile JSON.
No user archive, approved section or old checkpoint is modified.
"""
from pathlib import Path
import io,sys,argparse,hashlib,json,zipfile
from PIL import Image
from shapely.geometry import Polygon,box
BASE=Path('/home/christopher/Cathedral_Research')
sys.path.insert(0,str(BASE/'R45_production_candidate'))
from R45_png_profile_converter import convert_png

def prepare(source,out,*,profile_id,width_mm,member=None,rebate_depth_mm=0,rebate_height_mm=0):
 source=Path(source).expanduser().resolve();out=Path(out).expanduser().resolve()
 if not source.is_file():raise FileNotFoundError(source)
 if not out.parent.is_dir():out.parent.mkdir(parents=True)
 if source.suffix.lower()=='.zip':
  if not member:raise ValueError('ZIP_MEMBER_REQUIRED')
  with zipfile.ZipFile(source) as z:
   if member not in z.namelist() or not member.lower().endswith('.png'):
    raise ValueError('INVALID_ZIP_MEMBER')
   raw=z.read(member)
 else:
  if member:raise ValueError('ZIP_MEMBER_FOR_PNG_UNSUPPORTED')
  if source.suffix.lower()!='.png':raise ValueError('SOURCE_MUST_BE_PNG_OR_ZIP')
  raw=source.read_bytes()
 if len(raw)>20_000_000:raise ValueError('SOURCE_PNG_EXCESSIVE_BYTES')
 try:
  im=Image.open(io.BytesIO(raw)).convert('RGB')
 except Exception as exc:
  raise ValueError('CANNOT_PARSE_SOURCE_PNG') from exc
 if min(im.size)<100 or max(im.size)>10000:raise ValueError('SOURCE_RESOLUTION_INVALID')
 # Padding restores a uniform white border for the contour detector without
 # changing source pixel proportions or the located outer foreground contour.
 white=Image.new('RGB',(im.width+60,im.height+60),'white')
 white.paste(im,(30,30))
 tmp=out.parent/(out.stem+'_r48_padded_input.png')
 tmp_base=out.parent/(out.stem+'_r48_extracted.json')
 white.save(tmp)
 result=convert_png(tmp,tmp_base,profile_id=profile_id,
     width_mm=width_mm,evidence_class='EXPERIMENTAL')
 d=json.loads(tmp_base.read_text())
 original=Polygon([(float(x),float(y)) for x,y in d['closed_points_mm']])
 if not original.is_valid or original.area<100:raise ValueError('INVALID_EXTRACTED_STONE_PROFILE')
 if (rebate_depth_mm==0)!=(rebate_height_mm==0):raise ValueError('REBATE_MUST_HAVE_BOTH_DIMENSIONS')
 if rebate_depth_mm or rebate_height_mm:
  if not(3<=rebate_depth_mm<=25 and 3<=rebate_height_mm<=25):
   raise ValueError('REBATE_DIMENSIONS_OUTSIDE_EXPERIMENTAL_RANGE')
  remove=box(original.bounds[2]-rebate_depth_mm,
         -rebate_height_mm/2,original.bounds[2]+5,rebate_height_mm/2)
  modified=original.difference(remove)
  if not(modified.is_valid and modified.geom_type=='Polygon' and len(modified.interiors)==0):
   raise ValueError('REBATe_BROKE_STONE_SECTION')
 else:modified=original
 d.update({
  'source_document':str(source)+('::'+member if member else ''),
  'source_file_SHA256':hashlib.sha256(raw).hexdigest(),
  'original_width_mm':result['width_mm'],'original_height_mm':result['depth_mm'],
  'experimental_clipped_backing_edge':True,
  'experimental_rebate_mm':[rebate_depth_mm,rebate_height_mm],
  'rebate_area_reduction_mm2':float(original.area-modified.area),
  'source_historical_3d_not_verified':True,
  'closed_points_mm':[[round(float(x),5),round(float(y),5)]
                      for x,y in list(modified.exterior.coords)[:-1]]})
 out.write_text(json.dumps(d,indent=2))
 return {'profile_id':profile_id,'profile_file':str(out),
         'original_section_area_mm2':float(original.area),
         'final_section_area_mm2':float(modified.area),
         'rebate_area_mm2':float(original.area-modified.area),
         'historical_status':'EXPERIMENTAL'}
if __name__=='__main__':
 parser=argparse.ArgumentParser()
 parser.add_argument('--source',required=True)
 parser.add_argument('--member')
 parser.add_argument('--out',required=True)
 parser.add_argument('--profile-id',required=True)
 parser.add_argument('--width-mm',required=True,type=float)
 parser.add_argument('--rebate-depth-mm',default=0,type=float)
 parser.add_argument('--rebate-height-mm',default=0,type=float)
 a=parser.parse_args()
 print('R48_PROFILE_PREPARED',json.dumps(prepare(a.source,a.out,profile_id=a.profile_id,
     width_mm=a.width_mm,member=a.member,rebate_depth_mm=a.rebate_depth_mm,
     rebate_height_mm=a.rebate_height_mm)))
