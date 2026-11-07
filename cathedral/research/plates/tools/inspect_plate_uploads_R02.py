#!/usr/bin/env python3
"""Verify original PNGs and create explicitly derived browsing previews.

The archive itself is never written. Tone statistics do not establish historical
completeness or geometry. Filename page numbers remain unverified hints.
"""
import argparse
import csv
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BATCHES=[('PALEY_UPLOAD_R02','paley.zip'),('BRANDON_V2_UPLOAD_R02','brandon_v2.zip'),
         ('COLLINGS_V2_UPLOAD_R02','collings_v2.zip'),('GOTHIC_PLATES_UPLOAD_R02','gothic_plates.zip')]

def font(size):
    try:return ImageFont.truetype('DejaVuSans.ttf',size)
    except OSError:return ImageFont.load_default(size=size)

def page_hint(name):
    match=re.search(r'_p(\d+)\.[^.]+$',name)
    return int(match.group(1)) if match else None

def run(archives,library):
    archives,library=Path(archives),Path(library)
    target=library/'previews/R02';target.mkdir(parents=True,exist_ok=True)
    allrows=[];summary=[]
    for batch,name in BATCHES:
        manifest=json.loads((library/'batches'/batch/'BATCH_MANIFEST.json').read_text())
        overview=Image.new('RGB',(1500,2020),'white');draw=ImageDraw.Draw(overview)
        draw.text((24,14),name+' | SOURCE SCAN OVERVIEW',font=font(27),fill='#14242c')
        draw.text((24,52),'Derived thumbnails; original scan bytes retained. Folder labels and filenames are unverified metadata.',font=font(18),fill='#465760')
        assets=sorted(manifest['assets'],key=lambda x:(page_hint(x['original_name']) or 0,x['original_name']))
        browsable=[a for a in assets if '_blank' not in Path(a['original_name']).parts]
        selected={a['original_name']:i for i,a in enumerate(browsable[:12])}
        rows=[]
        with zipfile.ZipFile(archives/name) as z:
            for a in assets:
                entry=a['original_name'];raw=z.read(entry)
                if hashlib.sha256(raw).hexdigest()!=a['sha256']:raise ValueError('Source mismatch: '+entry)
                with Image.open(io.BytesIO(raw)) as im:
                    im.load()  # full PNG decode; ZipFile.read validates member CRC
                    histogram=im.convert('L').histogram();levels=sum(x>0 for x in histogram)
                    row={'batch_id':batch,'archive':name,'entry':entry,'asset_id':a['asset_id'],'sha256':a['sha256'],
                         'width_px':im.width,'height_px':im.height,'mode':im.mode,'dpi_metadata':im.info.get('dpi'),
                         'luminance_levels_present':levels,'png_decode':'PASS','zip_crc':'PASS',
                         'folder_blank_label':'_blank' in Path(entry).parts,'blank_visually_confirmed':False,
                         'filename_page_hint':page_hint(entry),'filename_page_hint_verified_as_pdf_page':False,
                         'source_collection_hint':Path(entry).parent.name if name=='gothic_plates.zip' else name.removesuffix('.zip'),
                         'historical_book_identity':'UNRESOLVED; collection hint only',
                         'original_library_url':manifest['origin']['source_url'],
                         'tonal_review_flag':'limited_luminance_levels' if levels<=16 else 'multitone',
                         'quality_interpretation':'Multiple tones retained; line fidelity still requires original/trace comparison' if levels>16 else 'Limited grayscale values; verify fine drawing detail against an earlier scan before tracing'}
                    rows.append(row)
                    if entry in selected:
                        k=selected[entry];col=k%4;rownum=k//4;x=col*375;y=100+rownum*635
                        thumb=im.convert('RGB');thumb.thumbnail((353,570),Image.Resampling.LANCZOS)
                        overview.paste(thumb,(x+(375-thumb.width)//2,y+40))
                        draw.text((x+9,y+8),Path(entry).name,font=font(17),fill='black')
        out=library/'batches'/batch/'READABILITY_R02.json'
        out.write_text(json.dumps({'status':'READ_ONLY_SOURCE_INSPECTION','assets':rows,'preview_is_resampled':True,
                                  'original_images_modified':False,'book_identity_not_verified':True},indent=2)+'\n')
        imagepath=target/(name.removesuffix('.zip')+'_overview_R02.jpg')
        overview.save(imagepath,quality=80,optimize=True)
        summary.append({'batch_id':batch,'archive':name,'pngs':len(rows),'folder_blank_labels':sum(r['folder_blank_label'] for r in rows),
                        'other_pngs':sum(not r['folder_blank_label'] for r in rows),'decoded_pngs':len(rows),
                        'minimum_luminance_levels':min(r['luminance_levels_present'] for r in rows),
                        'maximum_dimensions_px':[max(r['width_px'] for r in rows),max(r['height_px'] for r in rows)],
                        'overview':imagepath.relative_to(library).as_posix(),
                        'archive_library_url':manifest['origin']['source_url']})
        allrows.extend(rows)
    hashes={}
    for row in allrows:hashes.setdefault(row['sha256'],[]).append({'archive':row['archive'],'entry':row['entry']})
    duplicate_groups=[{'sha256':h,'occurrences':p} for h,p in hashes.items() if len(p)>1]
    result={'status':'INTAKE_COMPLETE; reference files, no geometry approval','archives':summary,
            'png_occurrences':len(allrows),'unique_byte_assets':len(hashes),'exact_duplicate_occurrences':len(allrows)-len(hashes),
            'folder_blank_labels':sum(r['folder_blank_label'] for r in allrows),'all_png_decode_and_crc':'PASS',
            'duplicate_groups':duplicate_groups,'original_images_modified':False,
            'all_original_archives_have_persistent_library_links':True,'binary_originals_uploaded_to_github':False,
            'previews_are_derivative_resampled_browsing_views':True,'meaux_source_identified':False}
    (library/'UPLOAD_R02_SUMMARY.json').write_text(json.dumps(result,indent=2)+'\n')
    columns=['batch_id','archive','entry','asset_id','sha256','width_px','height_px','mode','luminance_levels_present',
             'folder_blank_label','filename_page_hint','source_collection_hint','original_library_url']
    with (library/'UPLOAD_R02_CROSSWALK.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=columns);writer.writeheader();writer.writerows({k:r[k] for k in columns} for r in allrows)
    print(json.dumps({k:v for k,v in result.items() if k!='duplicate_groups'},indent=2),flush=True)
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--archives',required=True);parser.add_argument('--library',required=True);a=parser.parse_args();run(a.archives,a.library)
