#!/usr/bin/env python3
"""
tracery_build.py - step 2: turn a region map (from tracery_regions.py, or one
you painted yourself) into a pierced tracery STL with real moulded edges.

    python3 tracery_build.py drawing_map.png -o window.stl

Region map colours:  blue = glass (cut through),  grey = outside (thrown away),
anything else (white, black lines) = stone.

Options:
    --width        finished width of the model, mm            (default 150)
    --thickness    thickness of the stone, mm                 (default 6)
    --edge         chamfer, round, hollow or none             (default chamfer)
    --edge-width   how far in from the glass the profile runs, mm   (default 1.5)
    --edge-depth   how far down it cuts, mm                   (default = edge-width)
    --one-side     profile only on the front (default: front and back, like real tracery)
    --lines        groove, raise or none: the drawn moulding lines on the stone face
                   (default groove)
    --line-depth   mm (default 0.4)
    --res          size of one grid step, mm (default 0.2; smaller = finer, bigger file)

Needs: numpy, scipy, pillow, scikit-image
"""
import argparse, os, struct
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.measure import marching_cubes


def read_map(path):
    a = np.asarray(Image.open(path).convert('RGB')).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    glass = (b > 150) & (b - r > 80) & (b - g > 40)
    grey = (abs(r - g) < 20) & (abs(g - b) < 20) & (r > 50) & (r < 140)
    ink = (r < 50) & (g < 50) & (b < 50)
    return ~(glass | grey), ink


def write_stl(path, verts, faces):
    tri = verts[faces]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
    rec = np.zeros(len(faces), dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')])
    rec['n'] = n; rec['v'] = tri
    with open(path, 'wb') as f:
        f.write(b'tracery_build'.ljust(80, b' '))
        f.write(struct.pack('<I', len(faces)))
        rec.tofile(f)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('map')
    ap.add_argument('-o', '--out')
    ap.add_argument('--width', type=float, default=150)
    ap.add_argument('--thickness', type=float, default=6)
    ap.add_argument('--edge', choices=['chamfer', 'round', 'hollow', 'none'], default='chamfer')
    ap.add_argument('--edge-width', type=float, default=1.5)
    ap.add_argument('--edge-depth', type=float)
    ap.add_argument('--one-side', action='store_true')
    ap.add_argument('--lines', choices=['groove', 'raise', 'none'], default='groove')
    ap.add_argument('--line-depth', type=float, default=0.4)
    ap.add_argument('--res', type=float, default=0.2)
    a = ap.parse_args()

    stone, ink = read_map(a.map)
    H, W = stone.shape
    # drop loose bits (labels, specks) that are not joined to the tracery
    lab, k = ndi.label(stone, structure=np.ones((3, 3), int))
    if k > 1:
        sz = ndi.sum(stone, lab, range(1, k + 1))
        stone = np.isin(lab, 1 + np.nonzero(sz >= 0.005 * sz.max())[0])
    px = a.width / W                                   # mm per image pixel
    T = a.thickness
    ew = a.edge_width
    ed = a.edge_depth if a.edge_depth is not None else ew
    both = not a.one_side
    ed = min(ed, (T / 2 - 0.4) if both else T - 0.8)

    # signed distance to the stone outline, mm (positive inside stone)
    s = (ndi.distance_transform_edt(stone) - ndi.distance_transform_edt(~stone)) * px
    lines = ndi.gaussian_filter((ink & stone).astype(float), sigma=max(0.12 / px, 0.5))
    lines = np.clip(lines * 2.0, 0, 1)

    # resample to the mesh grid
    f = px / a.res
    s = ndi.zoom(s, f, order=1)
    lines = ndi.zoom(lines, f, order=1)
    ny, nx = s.shape

    # edge profile: drop in height as you approach the glass
    x = np.clip(ew - s, 0, ew) / ew if ew > 0 else np.zeros_like(s)   # 0 inside .. 1 at the edge
    if a.edge == 'chamfer': drop = ed * x
    elif a.edge == 'round': drop = ed * (1 - np.sqrt(np.clip(1 - x * x, 0, 1)))
    elif a.edge == 'hollow': drop = ed * np.sqrt(np.clip(1 - (1 - x) ** 2, 0, 1))
    else: drop = np.zeros_like(s)
    top = T - drop
    bot = drop if both else np.zeros_like(s)
    if a.lines == 'groove': top = top - a.line_depth * lines
    elif a.lines == 'raise': top = top + a.line_depth * lines
    zmax = T + (a.line_depth if a.lines == 'raise' else 0)

    dz = a.res
    zs = np.arange(-dz, zmax + 2 * dz, dz) + 0.37 * dz   # keep flat faces off grid levels
    vol = np.empty((ny + 2, nx + 2, len(zs)), np.float32)
    vol[:] = -1
    for k, z in enumerate(zs):
        vol[1:-1, 1:-1, k] = np.minimum(np.minimum(s, top - z), z - bot)
    vol[:, :, 0] = -1; vol[:, :, -1] = -1

    verts, faces, _, _ = marching_cubes(vol, 0.0, spacing=(a.res, a.res, dz),
                                        gradient_direction='descent')
    # grid (row, col, z) -> model (x right, y up, z out of the face)
    X = verts[:, 1] - a.res
    Y = (ny + 1) * a.res - verts[:, 0]
    Z = verts[:, 2] + zs[0]
    v = np.stack([X, Y, Z], axis=1)
    faces = faces[:, [0, 2, 1]]                         # keep normals outward after the flip
    out = a.out or os.path.splitext(a.map)[0].replace('_map', '') + '.stl'
    write_stl(out, v, faces)
    print(f'wrote {out}: {len(faces):,} triangles, '
          f'{np.ptp(v[:,0]):.0f} x {np.ptp(v[:,1]):.0f} x {np.ptp(v[:,2]):.1f} mm')


if __name__ == '__main__':
    main()
