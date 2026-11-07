#!/usr/bin/env python3
"""Optional recreation of bundled 432-DPI derivatives from the supplied source PDF."""
from pathlib import Path
import argparse,hashlib,json
import fitz
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('pdf');a=p.parse_args()
root=Path(__file__).resolve().parents[1];pdf=Path(a.pdf)
meta=json.loads((root/'source_handoff/experiment/measurements.json').read_text())
assert hashlib.sha256(pdf.read_bytes()).hexdigest()==meta['source_pdf_sha256'],'Source PDF differs from handoff'
doc=fitz.open(pdf);page=doc[280]
pix=page.get_pixmap(matrix=fitz.Matrix(2,2));im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
crop=im.crop((114,239,339,465))
import numpy as np
assert np.array_equal(np.array(crop),np.array(Image.open(root/'source_handoff/experiment/1205b_original_crop.png'))),'144-DPI registration does not reproduce supplied crop'
out=root/'derived';page.get_pixmap(matrix=fitz.Matrix(6,6)).pil_save(str(out/'plate_432dpi.png'))
Image.open(out/'plate_432dpi.png').crop((342,717,1017,1395)).save(out/'1205b_crop_432dpi.png')
(out/'source_pdf_verification.json').write_text(json.dumps({'source_pdf_sha256':meta['source_pdf_sha256'],'hash_matches_handoff':True,'rerendered_144dpi_crop_pixel_identical':True,'page_1based':281,'crop_432dpi':[342,717,1017,1395],'pixel_center_mapping':'baseline=(highres_index-1)/3'},indent=2)+'\n')
print('Source hash and pixel-exact 144-DPI registration verified; 432-DPI derivatives recreated.')
