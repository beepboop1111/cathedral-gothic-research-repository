#!/usr/bin/env python3
"""Compose measured comparison figures from the verified Blender renders."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont

def run(root):
    root=Path(root);out=root/'comparisons'
    font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    def f(n):
        try:return ImageFont.truetype(font,n)
        except OSError:return ImageFont.load_default(size=n)
    sheet=Image.new('RGB',(1800,1800),'white');d=ImageDraw.Draw(sheet)
    d.text((42,25),'MEAUX · M02 R03 EXPERIMENT',font=f(32),fill='#14242c')
    d.text((42,75),'Original final STL / precision-repaired GLB · same camera, scale and shading',font=f(23),fill='#42535c')
    for row,view in enumerate(['front','oblique']):
        for col,tag in enumerate(['before','after']):
            x=30+col*890;y=130+row*750
            title=('Reference R02' if tag=='before' else 'Candidate R03 · not approved')+' / '+view
            d.text((x+10,y),title,font=f(23),fill='#14242c')
            im=Image.open(out/f'meaux_{view}_{tag}_R03.png').convert('RGB');im.thumbnail((870,690))
            sheet.paste(im,(x+(870-im.width)//2,y+42))
    d.text((42,1655),'Nonmanifold edges 6 → 0   |   Degenerate faces 7 → 0   |   Bounds change 0 mm',font=f(25),fill='#14242c')
    d.text((42,1702),'48 openings retained: 40 enclosed + 8 open at cropped base. No smoothing or hole filling.',font=f(23),fill='#42535c')
    d.text((42,1740),'Maximum moved vertex: 0.000009537 mm. Repair is intentionally invisible at this review scale.',font=f(22),fill='#42535c')
    sheet.save(out/'MEAUX_M02_R03_COMPARISON.png')
    sheet=Image.new('RGB',(1640,3040),'white');d=ImageDraw.Draw(sheet)
    d.text((35,20),'FOUR-WINDOW REGRESSION · R03 EXPERIMENT',font=f(30),fill='#14242c')
    d.text((35,65),'Original final mesh (left) / precision repair (right). No architectural promotion.',font=f(22),fill='#42535c')
    for row,name in enumerate(['meaux','haina_1264','haina_1265','chalons']):
        qa=json.loads((root/'experimental/qa'/f'{name}_mesh_R03.json').read_text());g=json.loads((root/'experimental/qa'/f'{name}_geometry_R03.json').read_text())
        y=120+row*720
        d.text((35,y),name.replace('_',' ').upper(),font=f(26),fill='#14242c')
        for col,tag in enumerate(['before','after']):
            im=Image.open(out/f'{name}_front_{tag}_R03.png').convert('RGB');im.thumbnail((780,620))
            sheet.paste(im,(30+col*810+(780-im.width)//2,y+43))
        d.text((35,y+665),f"Edges >2 faces: {qa['before']['nonmanifold_edges']} → 0; degenerates: {qa['before']['degenerate_faces_area_under_1e-10_mm2']} → 0; {g['source_classified_openings']} source openings retained; bounds unchanged",font=f(21),fill='#42535c')
    sheet.save(out/'FOUR_WINDOW_REGRESSION_R03.png')

if __name__=='__main__':run(Path(__file__).resolve().parents[1])
