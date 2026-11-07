#!/usr/bin/env python3
"""R14 independent evidence packaging; no edits to source scans or cathedral models."""
from pathlib import Path
import hashlib,json,csv,zipfile
from PIL import Image,ImageDraw,ImageOps
ROOT=Path(__file__).resolve().parent
SRC=Path('/home/christopher/Desktop/F5ZP_Buttress_R11_EXPERIMENTAL_20261104/Beauvais_fig61_Wikimedia_630x1021.png')
SOURCES=[
 ('BURGES05','Burges_1870_Beauvais_Plate05.jpg','William Burges, Architectural Drawing (1870), Beauvais: Section through Aisle and Apsidal Chapel','https://drawingmatter.org/wp-content/uploads/2022/02/burgess_3423.05_cs_19-01-22-scaled.jpg'),
 ('BURGES06','Burges_1870_Beauvais_Plate06.jpg','William Burges, Architectural Drawing (1870), Beauvais: Section through Triforium and Clerestory','https://drawingmatter.org/wp-content/uploads/2022/02/burgess_3423.06_cs_19-01-22-scaled.jpg'),
 ('VLD61','VLD61_630x1021_Unchanged.png','Viollet-le-Duc, Dictionnaire raisonne, I, Arc-boutant, figure 61','https://upload.wikimedia.org/wikipedia/commons/9/9d/Arc.boutant.cathedrale.Beauvais.png')]
originals=ROOT/'originals';originals.mkdir(exist_ok=True)
work=ROOT/'review';work.mkdir(exist_ok=True)
(ROOT/'register').mkdir(exist_ok=True)
(ROOT/'notes').mkdir(exist_ok=True)
assert SRC.exists()
data=SRC.read_bytes()
(originals/'VLD61_630x1021_Unchanged.png').write_bytes(data)
report=[]
for ident,name,title,url in SOURCES:
 p=originals/name if ident=='VLD61' else ROOT/name
 assert p.exists(),str(p)
 if ident!='VLD61':
  dst=originals/name
  dst.write_bytes(p.read_bytes())
  p=dst
 im=Image.open(p)
 report.append({'id':ident,'file':str(p.relative_to(ROOT)),'source':title,'url':url,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'width_px':im.width,'height_px':im.height,'scale_calibrated':False,'integrity':'byte-identical archived copy'})
with open(ROOT/'register/SOURCE_FILES.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(report[0]));w.writeheader();w.writerows(report)
claims=[
 ('BURGES05','Figure identifies apse aisle, chapel, triforium and section','Source drawing and author explanation','DIRECT OBSERVATION','Can identify vertical adjacency; paper scale is drawn but not instrument-calibrated here'),
 ('BURGES06','Two-stage flying-buttress system with intermediate support and exterior receiver','Source drawing and author explanation','DIRECT OBSERVATION','View drawn opposite orientation to VLD61: not overlaid or mirrored'),
 ('BURGES06','Burges surveyed accessible joints and bedding','Burges 1870 accompanying text','AUTHOR-REPORTED SURVEY','Do not generalize to flying-arch joints'),
 ('BURGES06','Only a few flying-buttress measurements could be made','Burges 1870 accompanying text','EXPLICIT SOURCE LIMITATION','Arcs and unseen springings are NOT survey-grade'),
 ('BURGES06','Middle buttress overhangs supporting columns','Burges accompanying text','AUTHOR OBSERVATION','Indicates cantilever relation; dimensions not recovered'),
 ('BURGES06','Clerestory exterior buttress partly modern','Burges accompanying text','HISTORICAL PHASE WARNING','Cannot assume all depicted construction is original Gothic work'),
 ('VLD61','Two sets of large flying arches terminating at inner wall','Viollet-le-Duc figure 61','ILLUSTRATED SCHEME','Not independent measured survey'),
 ('VLD101','Section through Beauvais apse piers drawn same scale as Amiens comparison','Viollet-le-Duc vol. IV, Construction, fig 101 and explanatory text','TEXT CONFIRMED, IMAGE NOT IN PACKAGE','Different authorial figure but still VLD; not independent survey'),
 ('PHILEAS2021','Beauvais cathedral detailed digital survey and cross-sections exist','Université de Picardie Jules Verne, Laboratoire MIS, Phileas','INDEPENDENT MODERN SURVEY INDEX','2D/3D images not licensed for derivative reworking (CC BY-NC-ND); files not acquired here'),
 ('BAUDOT1898','Axial-bay plaster model of choir and chevet buttressing exists','Cité de l’architecture et du patrimoine record','INDEPENDENT HISTORICAL MODEL INDEX','Model not a verified dimensional survey of springing'),
 ('R13','1.33px apparent shared tangent alignment is unstable under point selection','R13 numerical sensitivity experiment','MATHEMATICAL RECONSTRUCTION NOT HISTORICAL','No adoption as a shared springing axis'),
]
with open(ROOT/'register/EVIDENCE_AND_LIMITATIONS.csv','w',newline='') as f:
 w=csv.writer(f);w.writerow(['source_id','claim_or_observation','basis','status','architectural_use_or_caution']);w.writerows(claims)
links=[
 ('Burges 1870 accompanying interpretation','https://drawingmatter.org/excerpts-from-architectural-drawing-1870/'),
 ('Viollet-le-Duc Volume IV page 177 text','https://fr.wikisource.org/wiki/Page:Viollet-le-Duc_-_Dictionnaire_raisonn%C3%A9_de_l%E2%80%99architecture_fran%C3%A7aise_du_XIe_au_XVIe_si%C3%A8cle,_1854-1868,_tome_4.djvu/180'),
 ('Phileas UPJV laser survey sections','https://www.u-picardie.fr/phileas/item/profils-dune-cathedrale/'),
 ('Phileas UPJV open choir','https://www.u-picardie.fr/phileas/item/la-cathedrale-a-choeur-ouvert/'),
 ('Museum 1898 de Baudot model','https://www.citedelarchitecture.fr/fr/oeuvre/travee-daxe-du-choeur-et-du-contrebutement-du-chevet-de-la-cathedrale-saint-pierre-de'),
 ('2025 historical investigation','https://www.mdpi.com/2571-9408/8/6/203')
]
with open(ROOT/'register/SOURCE_URLS.csv','w',newline='') as f:
 w=csv.writer(f);w.writerow(['name','url']);w.writerows(links)
# Curated non-registered contact sheet: each whole source scaled to same height for visual comparison,
# with generous margins and explicit invalid-registration warning.
ims=[Image.open(originals/s[1]).convert('RGB') for s in SOURCES]
H=1200
sized=[]
for im in ims:
 scale=(H-90)/im.height
 sized.append(im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.LANCZOS))
W=sum(im.width for im in sized)+4*34
canvas=Image.new('RGB',(W,H+90),'white');d=ImageDraw.Draw(canvas)
x=34
for s,im in zip(SOURCES,sized):
 d.text((x,10),s[0]+'  ORIGINAL IMAGE',fill=(15,15,15))
 canvas.paste(im,(x,48));x+=im.width+34
d.text((34,H+20),'NOT REGISTERED: historical views depict different projections, orientation, print scales and construction states',fill=(185,15,20))
d.text((34,H+42),'Use source evidence separately; never infer an F5ZP architectural dimension from image widths',fill=(100,100,100))
canvas.save(work/'R14_BURGES05_06_VLD61_SIDE_BY_SIDE_NOT_REGISTERED.png')
# Independent study windows from Burges originals; crop bounds in original pixels preserved in register
regions=[
 ('BURGES05','Burges_1870_Beauvais_Plate05.jpg','B05_APSE_AND_CHAPEL',(170,160,1640,2100)),
 ('BURGES06','Burges_1870_Beauvais_Plate06.jpg','B06_FLYING_ARCHES_AND_PIER_JUNCTIONS',(145,120,1620,1810))
]
for ident,name,n,bbox in regions:
 im=Image.open(originals/name).convert('RGB')
 im.crop(bbox).save(work/(n+'.png'))
with open(ROOT/'register/WORKING_CROPS.csv','w',newline='') as f:
 w=csv.writer(f);w.writerow(['source_id','crop_name','x0','y0','x1','y1','units'])
 for ident,_,name,bbox in regions:w.writerow([ident,name,*bbox,'source pixels'])
readme='''# F5ZP R14 — Independent Beauvais Buttress Evidence (FOR REVIEW)
This is a research audit; NO approved cathedral geometry, dimensions, scripts, or prior R08–R13 output was modified.

## Source groups
- **Burges Plate 05 (1870):** section through aisle and apsidal chapel. Read the stone/chapel/triforium relationships, not as a validated flying-arch profile.
- **Burges Plate 06 (1870):** independent drawing of the triforium and clerestory with two flying-arch stages, intermediate pier and exterior buttress. Burges reports careful measurement of *accessible* parts and explicitly cautions that only a few measurements were obtained on flying buttresses. Thus it cannot certify the exact R13 springing/arc radius.
- **Viollet-le-Duc figure 61:** earlier illustration of the same type of buttress system. Independent in author, but neither image is registered in common world coordinates.
- **Viollet-le-Duc figure 101:** textual description verified, image not included here. It is not an independent survey by Burges.
- **2021 UPJV Phileas digitization:** modern survey source located online, individual relevant 3D dataset not acquired; catalogue marks CC BY-NC-ND.
- **Anatole de Baudot, 1898 model:** independent historical physical model exists; no model coordinates recovered.

## Major architectural correction
The Burges commentary states his main buttress is divided because the chapel junction did not give sufficient foundation; he notes middle buttress overhang and partially modern clerestory exterior masonry. These qualitative relationships matter before any join or load path is adopted.

## Geometric status
- **Observational:** relative support order; separate arched stages; intermediate upright; masonry joint positions where clearly drawn.
- **Measured image-space:** original source image dimensions and crop coordinates, source hashes, no metric calibration.
- **Uncertain:** exact original stone contact, arch springing center/radius, uniform historical phase, real-world masonry thickness and plan registration.
- No numeric pixel fitting to disparate sources; source comparisons are side-by-side ONLY, never metrically aligned.

## Recommended evidence-gathering continuation
Obtain authorized relevant UPJV survey sections of the **chevet** and the matching scanned original Burges plate dimensions. Register the exact chevet bay and date/phase before comparing to VLD 61, which may combine phases or idealizations. Do not confuse transept survey with chevet survey.
'''
(ROOT/'README_R14.md').write_text(readme)
# Reproducible source file/provenance QA independent of network
from collections import Counter
for item in report:
 p=ROOT/item['file']
 assert p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256']
assert len(report)==3 and len(claims)==11
manifest={}
for p in ROOT.rglob('*'):
 if p.is_file() and p.suffix != '.b64' and p.name!='F5ZP_Buttress_R14_Independent_Evidence_FOR_REVIEW.zip':
  manifest[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
(ROOT/'SHA256_MANIFEST.json').write_text(json.dumps(manifest,indent=2))
out=ROOT/'F5ZP_Buttress_R14_Independent_Evidence_FOR_REVIEW.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 for p in ROOT.rglob('*'):
  if p.is_file() and p!=out and p.suffix!='.b64':z.write(p,p.relative_to(ROOT))
with zipfile.ZipFile(out) as z: assert z.testzip() is None
print('R14 VERIFIED',out,round(out.stat().st_size/1024/1024,2),'MiB',len(manifest),'files')
for r in report:print(r['id'],r['width_px'],r['height_px'],r['sha256'][:16])
