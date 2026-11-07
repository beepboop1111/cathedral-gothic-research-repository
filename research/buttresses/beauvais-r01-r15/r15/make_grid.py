from PIL import Image,ImageDraw
from pathlib import Path
src=Path('/home/christopher/Desktop/F5ZP_Buttress_R14_INDEPENDENT_EVIDENCE_20261104/originals/Burges_1870_Beauvais_Plate06.jpg')
dst=Path('/home/christopher/Desktop/F5ZP_Buttress_R15_PHASE_AND_SURVEY_20261104')
im=Image.open(src).convert('RGB')
# original x/y approx full-res scaling = 1793/770 ~2.329
roi=(350,280,1450,1570)
im=im.crop(roi).resize(((roi[2]-roi[0])*1,(roi[3]-roi[1])*1))
d=ImageDraw.Draw(im,'RGBA')
for x in range((roi[0]//50+1)*50,roi[2],50):
 X=x-roi[0]; d.line((X,0,X,im.height),fill=(5,75,195,65));d.text((X+3,1),str(x),fill=(0,45,160,255))
for y in range((roi[1]//50+1)*50,roi[3],50):
 Y=y-roi[1];d.line((0,Y,im.width,Y),fill=(5,75,195,65));d.text((3,Y+2),str(y),fill=(0,45,160,255))
im.save(dst/'BURGES06_SOURCE_GRID_50px.png')
print(im.size)
