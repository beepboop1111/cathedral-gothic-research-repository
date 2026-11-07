from PIL import Image, ImageDraw
from pathlib import Path
p=Path('/home/christopher/Desktop/F5ZP_Buttress_R11_EXPERIMENTAL_20261104')
dst=Path('/home/christopher/Desktop/F5ZP_Buttress_R12_EXPERIMENTAL_20261104')
a=Image.open(p/'Beauvais_fig61_Wikimedia_630x1021.png').convert('RGB')
rois={
'01_intermediate_high':(195,130,290,300),
'02_choir_high':(318,99,409,245),
'03_intermediate_low':(195,269,295,433),
'04_choir_low':(313,234,410,392),
'05_outer_pier':(105,161,245,438)
}
for label,box in rois.items():
 im=a.crop(box)
 s=4
 im=im.resize((im.width*s,im.height*s),Image.Resampling.NEAREST)
 d=ImageDraw.Draw(im,'RGBA')
 for x in range((box[0]//10+1)*10,box[2],10):
  X=(x-box[0])*s
  d.line((X,0,X,im.height),fill=(0,80,240,62),width=1)
  d.text((X+2,2),str(x),fill=(20,60,160,255))
 for y in range((box[1]//10+1)*10,box[3],10):
  Y=(y-box[1])*s
  d.line((0,Y,im.width,Y),fill=(0,80,240,62),width=1)
  d.text((2,Y+2),str(y),fill=(20,60,160,255))
 im.save(dst/(label+'.png'))
 print(label,box)
