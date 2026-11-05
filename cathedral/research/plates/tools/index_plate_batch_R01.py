#!/usr/bin/env python3
"""Read-only plate intake: hash files, retain names, and write a separate catalog.

No extraction, renaming, resampling, thresholding, generator call or Git upload.
Book/page/plate/figure associations remain unresolved unless explicitly supplied.
"""
import argparse
import csv
import hashlib
import io
import json
import mimetypes
import stat
import warnings
import zipfile
from pathlib import Path, PurePosixPath

SUPPORTED={'.png','.jpg','.jpeg','.tif','.tiff','.jp2','.bmp','.gif','.webp','.pdf','.svg','.zip'}

def sha256(stream):
    digest=hashlib.sha256()
    for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
    return digest.hexdigest()

def image_header(stream):
    try:
        from PIL import Image
        with warnings.catch_warnings(record=True) as caught:
            with Image.open(stream) as im:
                return {'width_px':im.width,'height_px':im.height,'mode':im.mode,'format':im.format,
                        'warnings':[str(w.message) for w in caught],
                        'quality_review':'UNRESOLVED: image mode and dimensions do not establish retained drawing detail'}
    except ImportError:
        return {'status':'Pillow unavailable; checksum and source metadata retained'}
    except Exception as error:
        return {'status':'Header not interpreted','error_type':type(error).__name__}

def index(source, output, batch_id, metadata=None, origin=None):
    source,output=Path(source).resolve(),Path(output).resolve()
    if not source.exists():raise FileNotFoundError(source)
    if output.exists():raise FileExistsError('Use a new batch folder; existing records are never overwritten')
    if source==output or (source.is_dir() and source in output.parents):
        raise ValueError('Output must be outside the original source tree')
    metadata=metadata or {};origin=origin or {}
    rows=[];ids={}
    def add(name,size,opener):
        suffix=PurePosixPath(name).suffix.lower()
        if suffix not in SUPPORTED:return
        with opener() as stream:digest=sha256(stream)
        asset_id='ASSET-'+digest[:24]
        if asset_id in ids and ids[asset_id]!=digest:raise ValueError('Short asset-ID collision')
        ids[asset_id]=digest
        supplied=metadata.get(name,{})
        row={'asset_id':asset_id,'sha256':digest,'original_name':name,'bytes':size,
             'mime_type':mimetypes.guess_type(name)[0] or 'application/octet-stream',
             'batch_id':batch_id,'source_role':supplied.get('source_role','UNRESOLVED'),
             'source_key':supplied.get('source_key'),'original_pdf_page':supplied.get('original_pdf_page'),
             'printed_page':supplied.get('printed_page'),'plate':supplied.get('plate'),'figure':supplied.get('figure'),
             'master_page_ids':supplied.get('master_page_ids',[]),'parent_asset_id':supplied.get('parent_asset_id'),
             'source_url':supplied.get('source_url'),'trace_paths':supplied.get('trace_paths',[]),
             'bibliographic_status':'SUPPLIED_UNVERIFIED' if supplied else 'UNRESOLVED',
             'historical_geometry_validation':False,'architectural_approval':False,
             'original_bytes_uploaded_to_github':False,
             'filename_only_is_not_source_authority':True}
        parts=PurePosixPath(name).parts
        row['unsafe_extraction_path']=PurePosixPath(name).is_absolute() or '..' in parts or '\\' in name
        if suffix not in {'.pdf','.svg','.zip'}:
            with opener() as stream:row['image_header']=image_header(stream)
        rows.append(row)
    source_digest=None
    if source.is_file():
        with source.open('rb') as stream:source_digest=sha256(stream)
    if source.is_file() and zipfile.is_zipfile(source):
        with zipfile.ZipFile(source) as archive:
            seen=set()
            for info in sorted(archive.infolist(),key=lambda x:x.filename):
                if info.is_dir():continue
                if info.filename in seen:raise ValueError('ZIP contains duplicate member names; reconcile explicitly')
                seen.add(info.filename)
                if stat.S_ISLNK(info.external_attr>>16):continue
                add(info.filename,info.file_size,lambda info=info:archive.open(info))
    elif source.is_dir():
        for p in sorted(source.rglob('*')):
            if p.is_file() and not p.is_symlink():add(p.relative_to(source).as_posix(),p.stat().st_size,lambda p=p:p.open('rb'))
    else:add(source.name,source.stat().st_size,lambda:source.open('rb'))
    # Original filename is preserved for every occurrence. Only exact byte
    # duplicates share an asset ID; similar-looking scans are not merged.
    catalog={'schema':'cathedral-plate-intake/1.0','batch_id':batch_id,'status':'REFERENCE_INTAKE_NOT_GEOMETRY_APPROVAL',
             'source_name':source.name,'source_sha256':source_digest,'origin':origin,
             'indexed_file_occurrences':len(rows),'unique_byte_assets':len(ids),
             'new_user_batch':bool(origin.get('new_user_batch',False)),'original_files_modified':False,'original_bytes_uploaded_to_github':False,
             'notes':'Metadata/index only. Full original files remain in the named source archive or source location. No LFS pointer is created.',
             'assets':rows}
    output.mkdir(parents=True)
    (output/'BATCH_MANIFEST.json').write_text(json.dumps(catalog,indent=2,ensure_ascii=False)+'\n')
    columns=['asset_id','original_name','sha256','bytes','source_key','original_pdf_page','printed_page','plate','figure','source_role','bibliographic_status']
    with (output/'ASSET_INDEX.csv').open('w',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=columns);writer.writeheader()
        writer.writerows({k:r.get(k) for k in columns} for r in rows)
    return catalog

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source');parser.add_argument('--out',required=True);parser.add_argument('--batch',required=True)
    parser.add_argument('--metadata-json');parser.add_argument('--origin-json')
    args=parser.parse_args()
    data=index(args.source,args.out,args.batch,
               json.loads(Path(args.metadata_json).read_text()) if args.metadata_json else None,
               json.loads(Path(args.origin_json).read_text()) if args.origin_json else None)
    print(json.dumps({k:v for k,v in data.items() if k!='assets'},ensure_ascii=False))

if __name__=='__main__':main()
