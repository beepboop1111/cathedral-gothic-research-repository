from PIL import Image,ImageOps,ImageDraw,ImageFont
from pathlib import Path
import csv,math,json,hashlib,zipfile
p=Path(__file__).parent
names=['viollet_v04_p309','viollet_v04_p313','viollet_v01_p097','ungewitter_v1_p219','ungewitter_v2_p109','ungewitter_v2_p087','ungewitter_v2_p093','viollet_v01_p098','viollet_v04_p192']
labels=['Apse chapel plan','T-section receiving pier','Flyer / pier plan','Wall buttress plan + elevation','Intermediate flyer piers','Flyer arch and section','Flying buttress comparisons','Two-tier flying buttresses','Vault-to-flyer thrust study']
w,h=510,680; img=Image.new('RGB',(w*3,h*3),'#f4f2ee');d=ImageDraw.Draw(img)
for i,(n,l) in enumerate(zip(names,labels)):
 a=Image.open(p/'sources'/f'{n}.png').convert('RGB');a.thumbnail((w-24,h-68))
 x=(i%3)*w+(w-a.width)//2;y=(i//3)*h+34
 img.paste(a,(x,y));d.text(((i%3)*w+12,(i//3)*h+7),f'{n}: {l}',fill='#111111')
img.save(p/'Historical_Receiving_Pier_Contact_Sheet.jpg',quality=91)
# Diagram explicitly conceptual, not a registered overlay
cx,cy=700,660; r=380
s=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 1130">','<rect width="1400" height="1130" fill="white"/>','<text x="50" y="65" font-size="34" font-family="sans-serif">R21 chapel stations — comparison schematic, NOT surveyed footprint</text>','<text x="50" y="102" font-size="21" font-family="sans-serif">Reference: world X east / Y north; azimuth clockwise from north. Rings schematic only.</text>']
for rad in (250,380,475):s.append(f'<circle cx="{cx}" cy="{cy}" r="{rad}" fill="none" stroke="#888" stroke-dasharray="6 10" stroke-width="2"/>')
for a in (30,50,70,90,110,130,150):
 t=math.radians(a);x=cx+r*math.sin(t);y=cy-r*math.cos(t)
 s.extend([f'<line x1="{cx}" y1="{cy}" x2="{cx+490*math.sin(t):.2f}" y2="{cy-490*math.cos(t):.2f}" stroke="#aaa" stroke-dasharray="5 8"/>',f'<text x="{cx+525*math.sin(t)-20:.0f}" y="{cy-525*math.cos(t):.0f}" font-size="24" font-family="sans-serif" fill="#333">{a}°</text>'])
for a in (50,90,130):
 t=math.radians(a);x=cx+450*math.sin(t);y=cy-450*math.cos(t)
 s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="56" fill="none" stroke="#111" stroke-width="5"/>')
for a in (70,110):
 t=math.radians(a);x=cx+435*math.sin(t);y=cy-435*math.cos(t)
 s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="45" fill="none" stroke="#c43434" stroke-dasharray="10 8" stroke-width="4"/>')
s.extend(['<rect x="60" y="946" width="26" height="26" fill="none" stroke="#111" stroke-width="4"/><text x="100" y="969" font-family="sans-serif" font-size="22">R21 B (50/90/130), recommended experimental candidate</text>', '<rect x="60" y="987" width="26" height="26" fill="none" stroke="#c43434" stroke-dasharray="6 4" stroke-width="4"/><text x="100" y="1010" font-family="sans-serif" font-size="22">R21 A companion stations (70/110); axial 90 shared</text>','<text x="60" y="1072" font-family="sans-serif" font-size="19">No pier footprint, flyer spring, support volume or physical scale is implied.</text>','</svg>'])
(p/'R21_Chapel_Station_Comparison.svg').write_text('\n'.join(s))
rows=[
('VdL IV p309','Apse radial chapel/buttress arrangement','Plan','Useful precedent for separating chapel entrances from outward thrust receivers','No F5ZP receiving polygon or dimension'),
('VdL IV p313','T-shaped buttress pier plan','Plan','Test a T or engaged receiving-wall alternative at individual interfaces','Cannot assign size from ink or prove support'),
('VdL I p097','Receiving-pier / flyer-head plan','Plan','Evidence for distinct flyer-head landing and pier section','F5ZN-A bearing coordinates not present'),
('Ungewitter I p219','Widerlagswände plans/elevations','Plan/elevation','Check possible integrated wall and buttress configurations','Missing local actual wall geometry'),
('Ungewitter II p109','Intermediate flyer piers and calculation','Elevation/sections','Consider staged flyer spans and intermediate receivers','No verified M01 capacity or eccentricity'),
('Ungewitter II p087/p093','Strebebogen arches and sections','Elevation/section','Compare arch rise, spring, thickness and landing orientation','R21 receiving-face and physical conversion unknown'),
('VdL I p098','Two-tier flyer with pinnacle','Elevation/section','Compare double-level envelope with gallery and chapel roofs','Z2300 to Z3000 relation remains unresolved'),
('VdL IV p192','Thrust-transfer diagram','Structural illustration','List needed thrust directions and support contact checks','Cannot substitute for engineering verification')]
with open(p/'HISTORICAL_TO_F5ZP_COMPARISON.csv','w',newline='') as f:
 wr=csv.writer(f);wr.writerow(['source','source feature','drawing class','proposed experiment','evidence gap']);wr.writerows(rows)
# compatibility register expressly not a collision test
cases=[]
for variant,stations,pairs in [('A',[70,90,110],9),('B',[50,90,130],0)]:
 for feature,stat in [('receiving_wall','unverified'),('flyer_landing','unverified'),('upper_roof_clearance','unverified'),('ambulatory_access','unverified'),('load_path','unverified')]:
  cases.append(dict(variant=variant,stations_deg=stations,feature=feature,status=stat,known_cross_chapel_surface_intersection_pairs=pairs))
(p/'UNRESOLVED_BEARING_TEST_MATRIX.json').write_text(json.dumps(cases,indent=2))
