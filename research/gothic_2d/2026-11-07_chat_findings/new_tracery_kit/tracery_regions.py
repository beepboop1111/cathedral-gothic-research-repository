#!/usr/bin/env python3
"""
tracery_regions.py - step 1: turn a black-and-white tracery drawing into a
REGION MAP that says, for every area, whether it is glass, stone or outside.

    python3 tracery_regions.py drawing.png -o drawing_map.png

It writes two pictures:
    drawing_map.png       the region map (this is what tracery_build.py reads)
                            blue  = glass (cut right through)
                            white = stone face,  black = drawn lines (also stone)
                            grey  = outside the window (thrown away)
    drawing_numbers.png   the same map with every glass/candidate area numbered

The guess is automatic.  Fix it either way:
  * by number:  --stone 12 40   (make these areas stone)   --glass 7  (make glass)
  * by hand:    open drawing_map.png in GIMP, bucket-fill an area pure blue
                (0,0,255) for glass or pure white for stone, save, done.

How it decides: a white area counts as glass when a disk of --disk pixels fits
inside it (thin bands between double lines never fit), it is wide enough
(--min-radius) and compact, not long and thin (--max-compact).
Areas touching the top, left or right edge are outside; use --open-bottom to
treat areas running off the bottom edge as outside too (lancet lights).

Needs: numpy, scipy, pillow, scikit-image
"""
import argparse, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi

BLUE = (0, 0, 255); WHITE = (255, 255, 255); BLACK = (0, 0, 0); GREY = (90, 90, 90)


def disk(r):
    y, x = np.ogrid[-r:r + 1, -r:r + 1]
    return x * x + y * y <= r * r


def geodesic_grow(seed, mask, steps):
    """grow seed inside mask by `steps` pixels (does not jump across lines)"""
    st = ndi.generate_binary_structure(2, 1)
    out = seed & mask
    for _ in range(steps):
        out = ndi.binary_dilation(out, structure=st, mask=mask)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('image')
    ap.add_argument('-o', '--out')
    ap.add_argument('--threshold', type=float, default=0.5, help='0-1, darker than this = line (default 0.5)')
    ap.add_argument('--invert', action='store_true', help='drawing is white lines on black')
    ap.add_argument('--disk', type=int, default=16, help='glass must fit a disk of this radius, px (default 16)')
    ap.add_argument('--min-radius', type=float, default=40, help='smallest glass area, as inscribed radius px (default 40)')
    ap.add_argument('--max-compact', type=float, default=10, help='area / radius^2 above this = long thin band = stone (default 10)')
    ap.add_argument('--open-bottom', action='store_true', help='areas running off the bottom edge are outside')
    ap.add_argument('--stone', type=int, nargs='*', default=[], help='area numbers to force to stone')
    ap.add_argument('--glass', type=int, nargs='*', default=[], help='area numbers to force to glass')
    a = ap.parse_args()

    g = np.asarray(Image.open(a.image).convert('L'), float) / 255.0
    ink = g > (1 - a.threshold) if a.invert else g < a.threshold
    H, W = ink.shape
    white = ~ink

    # pieces: white area reachable by a disk of radius --disk
    core = ndi.binary_opening(white, structure=disk(a.disk))
    lab, k = ndi.label(core)
    objs = ndi.find_objects(lab)
    dt = ndi.distance_transform_edt(white)
    area = ndi.sum(core, lab, range(1, k + 1))
    rad = ndi.maximum(dt, lab, range(1, k + 1))

    kind = np.zeros(k + 1, np.uint8)            # 0 stone, 1 glass, 2 outside
    edge = np.zeros(k + 1, bool)
    for i in range(1, k + 1):
        sl = objs[i - 1]
        t, l, r, b = sl[0].start == 0, sl[1].start == 0, sl[1].stop == W, sl[0].stop == H
        edge[i] = t or l or r or (b and a.open_bottom)
    # outside = the big areas beyond the window; thin bands that merely touch
    # the picture edge (e.g. between the outer arch mouldings) are not outside
    big_edge = max([area[i - 1] for i in range(1, k + 1) if edge[i]] or [0])
    for i in range(1, k + 1):
        if edge[i] and area[i - 1] >= 0.05 * big_edge:
            kind[i] = 2
        elif edge[i]:
            kind[i] = 0
        elif rad[i - 1] >= a.min_radius and area[i - 1] / rad[i - 1] ** 2 <= a.max_compact:
            kind[i] = 1
    for i in a.stone:
        if 0 < i <= k and kind[i] != 2: kind[i] = 0
    for i in a.glass:
        if 0 < i <= k: kind[i] = 1

    k_of = kind[lab]
    grow = a.disk + 2
    outside = geodesic_grow(k_of == 2, white, grow)
    glass = geodesic_grow(k_of == 1, white, grow) & ~outside

    img = np.empty((H, W, 3), np.uint8)
    img[:] = WHITE
    img[ink] = BLACK
    img[glass] = BLUE
    img[outside] = GREY
    out = a.out or os.path.splitext(a.image)[0] + '_map.png'
    Image.fromarray(img).save(out)

    # numbered preview: every candidate area (not outside) with its number
    prev = img.copy()
    prev[glass] = (110, 160, 220)
    im = Image.fromarray(prev)
    d = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype('DejaVuSans-Bold.ttf', max(14, W // 90))
    except OSError:
        f = ImageFont.load_default()
    dc = ndi.distance_transform_edt(core)
    for i in range(1, k + 1):
        if kind[i] == 2 or rad[i - 1] < a.disk + 4: continue
        sl = objs[i - 1]
        sub = (lab[sl] == i) * dc[sl]
        y, x = np.unravel_index(np.argmax(sub), sub.shape)
        d.text((x + sl[1].start - 10, y + sl[0].start - 10), str(i),
               fill=(200, 0, 0) if kind[i] == 1 else (0, 140, 0), font=f)
    num = os.path.splitext(out)[0].replace('_map', '') + '_numbers.png'
    im.save(num)
    print(f'wrote {out}  and  {num}')
    print(f'  {int((kind == 1).sum())} glass areas;  red numbers = glass, green = stone')


if __name__ == '__main__':
    main()
