#!/usr/bin/env python3
"""Experimental, reversible 2D architectural region coloring.

Input: black line artwork with closed ink contours, plus independently reviewed
seed points (x,y) indicating a face. Does NOT discover masonry depth, reconstruct
compass geometry, or change historical images. Keeps black contours on top.

Example:
 python depth_classify.py black_trace.png seeds.json --out preview.png

Requirements: Pillow, numpy, scipy.
"""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

DEFAULT_PALETTE = {
    'open': '#FFA142',       # glass/void, orange
    'closed': '#85D95B',     # visually closed infill: green, not proof of stone
    'outer': '#7832C9',      # uppermost/outermost contour face, violet
    'frame': '#2449BE',      # blue
    'middle': '#3B91E6',     # medium blue
    'inner': '#70D4ED',      # cyan
    'ring': '#FFD34E',       # yellow/gold
    'deep': '#F07837',       # warm orange-red layer
    'unclassified': '#FFFFFF'
}


def hexrgb(h):
    h = h.lstrip('#')
    if len(h) != 6: raise ValueError('Expected #RRGGBB color')
    return np.array(tuple(int(h[i:i+2], 16) for i in (0,2,4)), dtype=np.uint8)


def render(source, config, ink_threshold=140, close_px=1, max_fraction=0.45):
    src = np.asarray(Image.open(source).convert('RGB'))
    hh, ww = src.shape[:2]
    gray = (src[:,:,0].astype(float)*.299 + src[:,:,1]*.587 + src[:,:,2]*.114)
    ink = gray < ink_threshold
    # Bridge hairline raster breaks only; retain the original ink as a top layer.
    barrier = ndi.binary_dilation(ink, iterations=close_px) if close_px > 0 else ink
    regions, num = ndi.label(~barrier, structure=ndi.generate_binary_structure(2,1))
    palette = {**DEFAULT_PALETTE, **config.get('palette', {})}
    result = np.full_like(src, 255)
    warnings, assigned = [], {}
    for s in config.get('seeds', []):
        x, y, cls = int(s['x']), int(s['y']), s['class']
        if cls not in palette:
            warnings.append(f"Unknown class {cls!r} at ({x},{y})"); continue
        if not (0 <= x < ww and 0 <= y < hh):
            warnings.append(f"Seed outside image: ({x},{y})"); continue
        label = int(regions[y,x])
        if label == 0:
            warnings.append(f"Seed on ink/barrier: ({x},{y}) {cls}; move into face"); continue
        if label in assigned and assigned[label] != cls:
            warnings.append(f"CONFLICT: region {label} already {assigned[label]}, requested {cls}"); continue
        frac = (regions == label).sum() / (ww*hh)
        if frac > max_fraction:
            warnings.append(f"LARGE REGION {label}: {frac:.1%} at ({x},{y}); likely leak or exterior. SKIPPED")
            continue
        assigned[label] = cls
    for label, cls in assigned.items():
        result[regions == label] = hexrgb(palette[cls])
    # Only the trace ink itself is black; no generated gradient/shading.
    result[ink] = (0,0,0)
    return Image.fromarray(result), {
        'image_px': [ww, hh], 'ink_threshold': ink_threshold,
        'barrier_dilate_pixels': close_px, 'all_detected_regions': int(num),
        'classified_regions': len(assigned), 'class_counts': {c:sum(v == c for v in assigned.values()) for c in set(assigned.values())},
        'warnings': warnings, 'source_unchanged': True,
        'not_architectural_depth_verified': True
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('trace'); ap.add_argument('seeds'); ap.add_argument('--out', default='depth_preview.png')
    ap.add_argument('--threshold', type=int, default=140)
    ap.add_argument('--barrier', type=int, default=1)
    ap.add_argument('--max-fraction', type=float, default=.45)
    a = ap.parse_args()
    if a.threshold < 1 or a.threshold > 254 or a.barrier < 0: ap.error('Invalid threshold/barrier')
    cfg = json.loads(Path(a.seeds).read_text())
    img, report = render(a.trace, cfg, a.threshold, a.barrier, a.max_fraction)
    img.save(a.out)
    report['source'] = str(a.trace)
    report['seed_file'] = str(a.seeds)
    Path(a.out).with_suffix('.qa.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))

if __name__ == '__main__': main()
