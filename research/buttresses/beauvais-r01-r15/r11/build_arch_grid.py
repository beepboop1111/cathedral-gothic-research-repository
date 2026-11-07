from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
p=Path('/home/christopher/Desktop/F5ZP_Buttress_R11_EXPERIMENTAL_20261104')
im=Image.open(p/'Beauvais_fig61_Wikimedia_630x1021.png').convert('RGB')
crop=(115,110,430,545)
img=im.crop(crop).resize((630,870))
d=ImageDraw.Draw(img, 'RGBA')
for x in range((crop[0]//20+1)*20,crop[2],20):
 X=(x-crop[0])*2
 d.line([(X,0),(X,img.height)],fill=(15,85,255,80),width=1)
 d.text((X+2,1),str(x),fill=(0,0,180,255))
for y in range((crop[1]//20+1)*20,crop[3],20):
 Y=(y-crop[1])*2
 d.line([(0,Y),(img.width,Y)],fill=(15,85,255,80),width=1)
 d.text((1,Y+1),str(y),fill=(0,0,180,255))
img.save(p/'R11_ARCH_GRID_2X.png')
print('grid saved')
