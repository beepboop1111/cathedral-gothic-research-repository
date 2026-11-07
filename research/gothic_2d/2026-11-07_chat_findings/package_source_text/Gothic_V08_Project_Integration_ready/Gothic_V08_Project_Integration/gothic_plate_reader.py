"""Read-only Gothic plate metadata, calibration and region extraction.

All pixels are image coordinates, X right, Y down.  No historical scale is
inferred unless a user supplies a measured reference.  Does not modify source.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import json
import math
from PIL import Image
import numpy as np


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


@dataclass(frozen=True)
class Calibration:
    """Scale measured by the user between two source image pixel coordinates."""
    p0: tuple[float, float]
    p1: tuple[float, float]
    real_length: float
    unit: str

    @property
    def units_per_pixel(self):
        pixels = math.dist(self.p0, self.p1)
        if pixels <= 0 or self.real_length <= 0 or not self.unit.strip():
            raise ValueError('Calibration requires distinct points, positive length and unit')
        return self.real_length / pixels

    def transform(self, image_pixel):
        scale = self.units_per_pixel
        x, y = image_pixel
        return ((x - self.p0[0]) * scale, (self.p0[1] - y) * scale)


def inspect_plate(path, crop=None, calibration=None):
    path = Path(path)
    with Image.open(path) as im:
        width, height = im.size
        if crop is None: crop = (0, 0, width, height)
        x0, y0, x1, y1 = crop
        if not (0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height):
            raise ValueError('Crop must lie inside plate')
        dpi = im.info.get('dpi')
        mode = im.mode
    return dict(schema='gothic.plate.v08', source=str(path.resolve()),
                sha256=sha256_file(path), size_px=[width, height], crop_px=list(crop),
                original_mode=mode, embedded_dpi=dpi,
                calibration=({**asdict(calibration), 'units_per_pixel': calibration.units_per_pixel}
                             if calibration else None),
                units=('source image pixels' if calibration is None else calibration.unit),
                historical_scale_verified=bool(calibration),
                note=('Calibration supplied by user, not inferred from engraving.' if calibration
                      else 'Image geometry uncalibrated: not 1:1 architectural dimensions.'))


def extract_ink(path, crop=None, threshold=0.6, color='dark', max_side=None):
    """Return boolean source-ink mask and scale metadata; no OCR or joining."""
    meta = inspect_plate(path, crop)
    x0, y0, x1, y1 = meta['crop_px']
    with Image.open(path) as im:
        rgb = im.convert('RGB').crop((x0,y0,x1,y1))
        if max_side and max(rgb.size) > max_side:
            factor = float(max_side) / max(rgb.size)
            rgb = rgb.resize((round(rgb.width*factor),round(rgb.height*factor)),Image.Resampling.LANCZOS)
        else: factor = 1.0
        a = np.asarray(rgb).astype(np.int16)
    r,g,b = a[:,:,0],a[:,:,1],a[:,:,2]
    if color == 'dark':mask = np.min(a,axis=2) < threshold*255
    elif color == 'red':mask = (r-g > 45)&(r-b > 38)&(r > 75)
    elif color == 'blue':mask = (b-r > 35)&(b-g > 16)&(b > 70)
    elif color == 'green':mask = (g-r > 25)&(g-b > 15)&(g > 70)
    else:raise ValueError('color must be dark/red/blue/green')
    return mask, dict(meta, analyzed_size_px=list(rgb.size), analyzed_scale_vs_original=factor,
                      ink_mode=color,threshold=threshold)


def save_metadata(metadata, path):
    Path(path).write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf8')
