#!/usr/bin/env python3
"""
plan2stl.py - turn a drawn floor plan into a clean plan (PNG / SVG / DXF)
              and a 3D structure (STL).

The drawing is sorted into three kinds of ink:
    PIERS   the solid black masses (piers, columns, wall stubs, detached shafts)
    LINES   the thin lines (vault ribs, bay lines, wall lines)
    JUNK    lettering, numbers, scale bars, specks - thrown away

Then the piers are extruded to a height, and the lines become one of:
    ribs    bars at the top of the piers, like a vault-rib lattice   (default)
    walls   low walls standing on the floor
    floor   thin ridges raised on the floor slab, a "3D drawing"
    none    left out

Usage:
    python3 plan2stl.py plan.png
    python3 plan2stl.py page.png --crop 180 1190 1600 3000 --width 150 -o choir.stl

    measured scale, moulded ribs, and a pier file for sweep2schem.py:
    python3 plan2stl.py page.png --crop 180 1190 1385 3000 \
        --calibrate 357 1920 358 2438 40 --unit blocks \
        --rib-profile rib_section.png --piers-json -o out/choir.stl

Vector or pixel output:
    When the gothic_v08 folder sits next to this script, piers are extruded
    from their traced outlines and ribs are swept along the traced lines
    (clean, small files; ribs broken at crossings are joined back up).
    Without it - or with --raster - the older pixel method is used.
    'walls' and 'floor' line modes always use the pixel method.

Outputs (next to the STL):
    choir.stl           the 3D structure
    choir_plan.png      the cleaned-up plan, black on white
    choir_classes.png   what was called pier (red), line (blue), shaft (dark
                        red), marker dot (orange, left out), junk (grey)
    choir_plan.svg      vector plan  (--svg)
    choir_plan.dxf      the same as DXF, for FreeCAD / CAD   (--dxf)
    choir_preview.png   a shaded 3D view   (--preview)
    choir_meta.json     source file hash, crop, scale and how it was set
    piers.json          pier centres for sweep2schem.py --pier-file  (--piers-json)
    choir_piers.png     which pier got which name (red = pier, blue = shaft)

Options:
    -o / --out         output STL name (default: image name + .stl)
    --crop x0 y0 x1 y1 pixel rectangle of the image to use
    --width W          finished width of the plan, in units (mm, m, blocks...;
                       default 150). All other sizes are in the same units.
    --calibrate X0 Y0 X1 Y1 LENGTH
                       measured scale instead of --width: two points on the
                       ORIGINAL page (pixels, before --crop) and the real
                       distance between them, e.g. two pier centres one bay
                       apart.  Recorded in _meta.json.
    --unit NAME        name of the unit (default blocks with --calibrate)
    --pier-height H    (default 0.3 x width)
    --floor T          floor slab thickness (default 2);  --no-floor to drop it
    --lines MODE       ribs | walls | floor | none   (default ribs)
    --line-width       thickness given to the lines in 3D (default 1.5)
    --rib-depth        depth of the rib bars (default 2)
    --wall-height      height of the walls in 'walls' mode (default 8)
    --relief           height of the ridges in 'floor' mode (default 1)
    --max-size         longest side of the 3D grid in cells (default 1000)
  recognising the drawing (all in pixels of the ORIGINAL image):
    --pier-size R      a black mass counts as a pier if a circle of radius R
                       fits inside it (default 12). Lower it if small piers
                       are missed, raise it if dots/blobs become piers.
    --dot-size R       smaller round blobs (detached shafts, keystone marks)
                       are found with this radius (default pier-size / 2)
    --dots MODE        what to do with those small blobs: near = keep only
                       ones sitting next to a pier (default), keep, drop
    --min-span S       ink pieces smaller than S px across, with no pier in
                       them, are junk (lettering) (default 100)
    --threshold T      grey level below which a pixel is ink (default 0.5)
    --faint T          lighter level for faint lines that connect to real
                       ink (default 0.78)
    --prune N          drop skeleton spurs shorter than N px (default 12)
    --svg --dxf --preview   extra outputs, see above
  vector output (needs the gothic_v08 folder):
    --rib-profile PNG  moulding section to sweep along every rib (black on
                       white, drawn upright: top of the picture = top of the
                       rib).  Its size is stretched to --line-width x --rib-depth
    --raster           use the old pixel method even when gothic_v08 is there
  pier file for sweep2schem.py:
    --piers-json [PATH]  write the pier centres (default: piers.json next to
                       the STL).  x = left to right, z = top to bottom of the
                       drawing (= south in Minecraft)
    --origin X Z       add this to every pier position (default 0 0)
    --datum-y Y        springing level written as geometry.plan_datum_y

Needs: numpy, scipy, pillow, scikit-image  (+ trimesh for vector output)
    sudo apt install python3-numpy python3-scipy python3-pil python3-skimage
    pip install --user --break-system-packages trimesh
"""
import argparse, hashlib, json, os, struct, sys, time
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from skimage.morphology import skeletonize
from skimage.measure import find_contours, approximate_polygon


# ------------------------------------------------------------- V08 link ----
def find_v08():
    """Locate the gothic_v08 folder (vector sweeps).  Looked for in $GOTHIC_V08,
    next to this script, and in cathedral_geometry/ next to this script."""
    here = os.path.dirname(os.path.abspath(__file__))
    for d in [os.environ.get("GOTHIC_V08", ""), os.path.join(here, "gothic_v08"),
              os.path.join(here, "cathedral_geometry", "gothic_v08"), here]:
        if d and os.path.isfile(os.path.join(d, "gothic_adapters.py")):
            if d not in sys.path:
                sys.path.insert(0, d)
            try:
                import gothic_adapters, trimesh                # noqa: F401
                return d
            except ImportError as e:
                print(f"note: found {d} but could not load it ({e})")
                return None
    return None


# ------------------------------------------------------------ helpers -----
def disk(r):
    r = int(round(r))
    y, x = np.ogrid[-r:r + 1, -r:r + 1]
    return x * x + y * y <= r * r


N8 = np.ones((3, 3), bool)


def comp_filter(mask, keep_fn):
    """Keep the connected pieces of mask for which keep_fn(labels, n) is true."""
    lab, n = ndi.label(mask, structure=N8)
    if not n:
        return mask
    keep = keep_fn(lab, n)
    return np.isin(lab, np.nonzero(keep)[0] + 1)


def spans(lab, n):
    sl = ndi.find_objects(lab)
    return np.array([max(s[0].stop - s[0].start, s[1].stop - s[1].start) for s in sl])


# ----------------------------------------------------------- reading ------
def read_ink(path, crop, thr, faint):
    img = Image.open(path).convert("L")
    if crop:
        img = img.crop(tuple(crop))
    g = np.asarray(img, dtype=np.float32) / 255.0
    strong = g < thr
    weak = g < faint
    # faint pixels count only when they touch real ink (hysteresis)
    return ndi.binary_propagation(strong, mask=weak, structure=N8), g.shape


def classify(ink, pier_r, dot_r, dots, min_span):
    """Split ink into piers, small blobs (kept / dropped) and junk."""
    dt = ndi.distance_transform_edt(ink)

    def masses(radius, exclude):
        seed = (dt >= radius) & ~exclude
        core = ndi.binary_propagation(seed, mask=(dt >= max(1.5, 0.6 * radius)) & ~exclude)
        return ndi.binary_dilation(core, disk(0.6 * radius)) & ink & ~exclude

    seed_all = dt >= 3
    lab, n = ndi.label(ndi.binary_propagation(seed_all, mask=dt >= 1.8), structure=N8)
    if n:
        radii = np.sort(ndi.maximum(dt, lab, range(1, n + 1)))
        print("black masses, by the radius of the circle that fits inside (px):",
              " ".join(f"{r:.0f}" for r in radii[radii >= 3]))
        print(f"   -> piers are those >= {pier_r:g} (--pier-size), small blobs >= {dot_r:g} (--dot-size)")
    big = masses(pier_r, np.zeros_like(ink))
    small = masses(dot_r, ndi.binary_dilation(big, disk(2)))
    small &= ~big
    if dots == "drop":
        kept_small = np.zeros_like(small)
    elif dots == "keep":
        kept_small = small
    else:                                            # near: next to a pier
        d_big = ndi.distance_transform_edt(~big)
        near_px = 3 * dot_r
        kept_small = comp_filter(small, lambda lab, n: ndi.minimum(d_big, lab, range(1, n + 1)) <= near_px)
    piers = big | kept_small
    dropped_dots = small & ~kept_small

    # junk: small isolated pieces with no pier in them
    ink = bridge_gaps(ink, piers, min_span)
    def keep_rule(lab, n):
        sp = spans(lab, n)
        has_pier = ndi.maximum(piers, lab, range(1, n + 1)) > 0
        return (sp >= min_span) | has_pier
    kept = comp_filter(ink, keep_rule)
    junk = ink & ~kept
    # (dropped marker dots stay in the line mask so the lines run through them)
    lines = kept & ~ndi.binary_dilation(piers, disk(2))
    return piers, big, kept_small, dropped_dots, lines, junk


def bridge_gaps(ink, piers, min_span, reach=25, thickness=3):
    """Extend short, line-like ink fragments along their own direction and join
    them to whatever ink they reach within `reach` px (closes gaps in broken
    lines without welding neighbouring parallel lines together)."""
    H, W = ink.shape
    base = ink & ~ndi.binary_dilation(piers, disk(2))
    lab, n = ndi.label(base, structure=N8)
    if not n:
        return ink
    sp = spans(lab, n)
    objs = ndi.find_objects(lab)
    im = Image.new("1", (W, H), 0)
    draw = ImageDraw.Draw(im)
    for i in np.nonzero(sp < min_span)[0] + 1:
        sl = objs[i - 1]
        ys, xs = np.nonzero(lab[sl] == i)
        if len(ys) < 4:
            continue
        pts = np.column_stack([xs + sl[1].start, ys + sl[0].start]).astype(float)
        mean = pts.mean(0)
        ev, evec = np.linalg.eigh(np.cov((pts - mean).T))
        if ev[0] > 1e-9 and ev[1] / ev[0] < 6:            # compact blob: a letter
            continue
        d = evec[:, 1]
        proj = (pts - mean) @ d
        for sign in (1, -1):
            end = pts[np.argmax(sign * proj)]
            for t in range(2, reach + 1):
                x, y = np.round(end + sign * d * t).astype(int)
                if not (0 <= x < W and 0 <= y < H):
                    break
                if ink[y, x] and lab[y, x] != i:
                    draw.line([tuple(end), (int(x), int(y))], fill=1, width=thickness)
                    break
    return ink | np.asarray(im, bool)


# ------------------------------------------------------ line tracing ------
def trace_skeleton(skel):
    """1-px skeleton -> list of pixel paths [(row, col), ...] between nodes."""
    H, W = skel.shape
    pts = set(zip(*map(list, np.nonzero(skel))))
    offs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    nbrs = lambda p: [(p[0] + a, p[1] + b) for a, b in offs if (p[0] + a, p[1] + b) in pts]
    deg = {p: len(nbrs(p)) for p in pts}
    nodes = {p for p, d in deg.items() if d != 2}
    seen = set()
    paths = []

    def walk(start, nxt):
        path = [start, nxt]
        seen.add(frozenset((start, nxt)))
        prev, cur = start, nxt
        while cur not in nodes:
            cand = [q for q in nbrs(cur) if q != prev and frozenset((cur, q)) not in seen]
            if not cand:
                break
            prev, cur = cur, cand[0]
            seen.add(frozenset((prev, cur)))
            path.append(cur)
        return path

    for s in nodes:
        for q in nbrs(s):
            if frozenset((s, q)) not in seen:
                paths.append(walk(s, q))
    # closed loops with no node on them
    for p in pts:
        if deg[p] == 2 and not any(frozenset((p, q)) in seen for q in nbrs(p)):
            paths.append(walk(p, nbrs(p)[0]))
    return paths, deg


def lines_to_polylines(lines, prune, min_len=6):
    skel = skeletonize(lines)
    paths, deg = trace_skeleton(skel)
    out = []
    for p in paths:
        n = len(p)
        ends = (deg.get(p[0], 0), deg.get(p[-1], 0))
        dangling = 1 in ends and max(ends) >= 3
        if n < 2:
            continue
        if dangling and n < prune:
            continue
        if ends == (1, 1) and n < min_len:
            continue
        pts = approximate_polygon(np.array(p, float), tolerance=1.2)
        out.append(pts)                               # (row, col) points
    return out


def pier_polygons(piers):
    polys = []
    for c in find_contours(piers.astype(float), 0.5):
        c = approximate_polygon(c, tolerance=1.0)
        if len(c) >= 4:
            polys.append(c)                           # (row, col), closed
    return polys


# ------------------------------------------------------- 2D outputs -------
def rasterize_lines(polys, shape, width_px):
    im = Image.new("1", (shape[1], shape[0]), 0)
    d = ImageDraw.Draw(im)
    w = max(1, int(round(width_px)))
    for p in polys:
        d.line([(float(c), float(r)) for r, c in p], fill=1, width=w, joint="curve")
        for r, c in p[[0, -1]]:                        # round the ends
            d.ellipse((c - w / 2, r - w / 2, c + w / 2, r + w / 2), fill=1)
    return np.asarray(im, bool)


def save_plan_png(piers, polys, shape, path):
    im = Image.new("L", (shape[1], shape[0]), 255)
    d = ImageDraw.Draw(im)
    for p in polys:
        d.line([(float(c), float(r)) for r, c in p], fill=0, width=3)
    a = np.asarray(im).copy()
    a[piers] = 0
    Image.fromarray(a).save(path)


def save_classes_png(ink, big, shafts, dropped, lines, junk, path):
    img = np.full(ink.shape + (3,), 255, np.uint8)
    img[junk] = [190, 190, 190]
    img[lines] = [60, 90, 200]
    img[big] = [160, 30, 30]
    img[shafts] = [110, 20, 20]
    img[dropped] = [240, 150, 40]
    Image.fromarray(img).save(path)


def save_svg(pier_polys, line_polys, shape, px_u, path):
    W, H = shape[1] * px_u, shape[0] * px_u
    f = lambda p: " ".join(f"{c * px_u:.3f},{r * px_u:.3f}" for r, c in p)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.3f} {H:.3f}" '
             f'width="{W:.3f}" height="{H:.3f}">',
             '<g id="piers" fill="black" fill-rule="evenodd" stroke="none">']
    if pier_polys:
        parts.append('<path d="' + " ".join("M" + f(p) + " Z" for p in pier_polys) + '"/>')
    parts.append('</g><g id="lines" fill="none" stroke="black" stroke-width="0.3" '
                 'stroke-linecap="round" stroke-linejoin="round">')
    for p in line_polys:
        parts.append(f'<polyline points="{f(p)}"/>')
    parts.append("</g></svg>")
    open(path, "w").write("\n".join(parts))


def save_dxf(pier_polys, line_polys, shape, px_u, path):
    H = shape[0]
    out = ["0", "SECTION", "2", "HEADER", "9", "$ACADVER", "1", "AC1009", "0", "ENDSEC",
           "0", "SECTION", "2", "TABLES", "0", "TABLE", "2", "LAYER", "70", "2"]
    for name, col in (("PIERS", 1), ("LINES", 5)):
        out += ["0", "LAYER", "2", name, "70", "0", "62", str(col), "6", "CONTINUOUS"]
    out += ["0", "ENDTAB", "0", "ENDSEC", "0", "SECTION", "2", "ENTITIES"]

    def poly(pts, layer, closed):
        o = ["0", "POLYLINE", "8", layer, "66", "1", "70", "1" if closed else "0"]
        for r, c in pts:
            o += ["0", "VERTEX", "8", layer, "10", f"{c * px_u:.4f}",
                  "20", f"{(H - r) * px_u:.4f}", "30", "0"]
        return o + ["0", "SEQEND"]
    for p in pier_polys:
        out += poly(p, "PIERS", True)
    for p in line_polys:
        out += poly(p, "LINES", False)
    out += ["0", "ENDSEC", "0", "EOF"]
    open(path, "w").write("\n".join(out) + "\n")


# ------------------------------------------------------------ meshing -----
def shrink(mask, shape):
    im = Image.fromarray((mask.astype(np.float32) * 255).astype(np.uint8))
    return np.asarray(im.resize((shape[1], shape[0]), Image.BOX), dtype=np.float32) / 255.0 >= 0.5


def no_diagonal_touches(c):
    c = c.copy()
    while True:
        a, b, d, e = c[:-1, :-1], c[:-1, 1:], c[1:, :-1], c[1:, 1:]
        bad = (a & e & ~b & ~d) | (b & d & ~a & ~e)
        if not bad.any():
            return c
        r, k = np.nonzero(bad)
        c[r, k] = c[r, k + 1] = c[r + 1, k] = c[r + 1, k + 1] = True


def mesh_cells(h, solid, px_u, hb=None, smooth_edges=2):
    """Solid cells -> closed mesh (top h, bottom hb, side walls). Returns V, F."""
    H, W = solid.shape
    nv = (H + 1) * (W + 1)
    vid = lambda r, c: r * (W + 1) + c
    pad = np.pad(solid, 1).astype(np.int32)
    cnt = np.maximum(pad[:-1, :-1] + pad[:-1, 1:] + pad[1:, :-1] + pad[1:, 1:], 1)
    hp = np.pad(np.where(solid, h, 0.0), 1)
    vz = (hp[:-1, :-1] + hp[:-1, 1:] + hp[1:, :-1] + hp[1:, 1:]) / cnt
    if hb is None:
        vzb = np.zeros_like(vz)
    else:
        bp = np.pad(np.where(solid, hb, 0.0), 1)
        vzb = (bp[:-1, :-1] + bp[:-1, 1:] + bp[1:, :-1] + bp[1:, 1:]) / cnt
    rr, cc = np.mgrid[0:H + 1, 0:W + 1]
    xy = np.stack([cc * px_u, (H - rr) * px_u], -1).reshape(-1, 2).astype(np.float64)

    r, c = np.nonzero(solid)
    a, b, d, e = vid(r, c), vid(r, c + 1), vid(r + 1, c), vid(r + 1, c + 1)
    F = []
    edges = []
    for dr, dc, p, q in [(-1, 0, (0, 0), (0, 1)), (1, 0, (1, 1), (1, 0)),
                         (0, -1, (1, 0), (0, 0)), (0, 1, (0, 1), (1, 1))]:
        nr, nc = r + dr, c + dc
        inside = (nr >= 0) & (nr < H) & (nc >= 0) & (nc < W)
        empty = ~inside
        empty[inside] = ~solid[nr[inside], nc[inside]]
        rs, cs = r[empty], c[empty]
        u, v = vid(rs + p[0], cs + p[1]), vid(rs + q[0], cs + q[1])
        F += [np.stack([u, v, v + nv], 1), np.stack([u, v + nv, u + nv], 1)]
        edges.append(np.stack([u, v], 1))
    F = np.concatenate(F) if F else np.zeros((0, 3), int)
    if edges and smooth_edges:
        E = np.concatenate(edges)
        on_edge = np.zeros(nv, bool); on_edge[E.ravel()] = True
        for _ in range(smooth_edges):
            s = np.zeros((nv, 2)); k = np.zeros(nv)
            np.add.at(s, E[:, 0], xy[E[:, 1]]); np.add.at(k, E[:, 0], 1)
            np.add.at(s, E[:, 1], xy[E[:, 0]]); np.add.at(k, E[:, 1], 1)
            m = on_edge & (k > 0)
            xy[m] = 0.5 * xy[m] + 0.5 * s[m] / k[m, None]
    # top and bottom faces: split each cell along whichever diagonal keeps
    # both triangles fat (edge smoothing can flatten the other split)
    A, B, D, E = xy[a], xy[b], xy[d], xy[e]
    tri_area = lambda p, q, t: np.abs((q[:, 0] - p[:, 0]) * (t[:, 1] - p[:, 1]) - (q[:, 1] - p[:, 1]) * (t[:, 0] - p[:, 0]))
    s1 = np.minimum(tri_area(A, D, B), tri_area(B, D, E))
    s2 = np.minimum(tri_area(A, D, E), tri_area(A, E, B))
    u = s2 > s1
    top = np.concatenate([np.stack([a, d, b], 1)[~u], np.stack([b, d, e], 1)[~u],
                          np.stack([a, d, e], 1)[u], np.stack([a, e, b], 1)[u]])
    F = np.concatenate([top, top[:, [0, 2, 1]] + nv, F]) if len(F) else top
    V = np.concatenate([np.column_stack([xy, vz.ravel()]), np.column_stack([xy, vzb.ravel()])])
    used = np.unique(F)
    remap = np.full(len(V), -1); remap[used] = np.arange(len(used))
    return V[used], remap[F]


def box_mesh(x0, y0, x1, y1, z0, z1):
    V = np.array([[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
                  [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]], float)
    F = np.array([[0, 2, 1], [0, 3, 2], [4, 5, 6], [4, 6, 7], [0, 1, 5], [0, 5, 4],
                  [1, 2, 6], [1, 6, 5], [2, 3, 7], [2, 7, 6], [3, 0, 4], [3, 4, 7]])
    return V, F


def write_stl(bodies, path):
    tris = [V[F] for V, F in bodies if len(F)]
    T = np.concatenate(tris).astype(np.float32)
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
    n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
    rec = np.zeros(len(T), dtype=[("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
    rec["n"], rec["v"] = n, T
    with open(path, "wb") as f:
        f.write(b"plan2stl".ljust(80, b" "))
        f.write(struct.pack("<I", len(T)))
        rec.tofile(f)
    return len(T)


# ------------------------------------------------------------ preview -----
def render_oblique(layers, px_u, path, ky=0.55, kz=0.7):
    """layers: (mask, top, bottom, colour). Painted back to front, from a
    viewpoint in front of and above the plan (top of the image = far side)."""
    H, W = layers[0][0].shape
    zmax = max(float(t[m].max()) for m, t, b, col in layers if m.any())
    zpx = lambda z: z / px_u * kz
    out_h = int(H * ky + zpx(zmax)) + 3
    img = np.full((out_h, W, 3), 1.0, np.float32)
    img[:, :] = np.array([0.93, 0.93, 0.9])
    for r in range(H):
        y0 = r * ky + zpx(zmax)
        for mask, top, bot, col in layers:
            cols = np.nonzero(mask[r])[0]
            if not len(cols):
                continue
            yt = y0 - zpx(top[r, cols]); yb = y0 - zpx(bot[r, cols])
            lo, hi = int(np.floor(yt.min())), int(np.ceil(yb.max())) + 1
            ys = np.arange(lo, hi)[:, None]
            strip = (ys >= yt[None, :]) & (ys <= yb[None, :])
            # front faces: lighter near the top, darker at the foot
            frac = np.clip((yb[None, :] - ys) / np.maximum(yb - yt, 1)[None, :], 0, 1)
            shade = (0.45 + 0.3 * frac)[..., None] * np.array(col)
            block = img[lo:hi, cols]
            block[strip] = shade[strip]
            img[lo:hi, cols] = block
            img[np.clip(np.round(yt).astype(int), 0, out_h - 1), cols] = col
    Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).save(path)


# --------------------------------------------------------------- main -----
def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("image")
    p.add_argument("-o", "--out")
    p.add_argument("--crop", type=int, nargs=4, metavar=("X0", "Y0", "X1", "Y1"))
    p.add_argument("--width", type=float, default=150)
    p.add_argument("--pier-height", type=float)
    p.add_argument("--floor", type=float, default=2.0)
    p.add_argument("--no-floor", action="store_true")
    p.add_argument("--lines", default="ribs", choices=["ribs", "walls", "floor", "none"])
    p.add_argument("--line-width", type=float, default=1.5)
    p.add_argument("--rib-depth", type=float, default=2.0)
    p.add_argument("--wall-height", type=float, default=8.0)
    p.add_argument("--relief", type=float, default=1.0)
    p.add_argument("--max-size", type=int, default=1000)
    p.add_argument("--pier-size", type=float, default=12)
    p.add_argument("--dot-size", type=float)
    p.add_argument("--dots", default="near", choices=["near", "keep", "drop"])
    p.add_argument("--min-span", type=int, default=100)
    p.add_argument("--threshold", type=float, default=0.5)
    p.add_argument("--faint", type=float, default=0.78)
    p.add_argument("--prune", type=int, default=12)
    p.add_argument("--calibrate", type=float, nargs=5,
                   metavar=("X0", "Y0", "X1", "Y1", "LENGTH"))
    p.add_argument("--unit", default=None)
    p.add_argument("--raster", action="store_true")
    p.add_argument("--rib-profile")
    p.add_argument("--piers-json", nargs="?", const="")
    p.add_argument("--origin", type=float, nargs=2, default=[0.0, 0.0], metavar=("X", "Z"))
    p.add_argument("--datum-y", type=float, default=None)
    p.add_argument("--svg", action="store_true")
    p.add_argument("--dxf", action="store_true")
    p.add_argument("--preview", action="store_true")
    a = p.parse_args()

    out = a.out or a.image.rsplit(".", 1)[0] + ".stl"
    stem = out.rsplit(".", 1)[0]
    if os.path.dirname(out):
        os.makedirs(os.path.dirname(out), exist_ok=True)
    dot_r = a.dot_size if a.dot_size is not None else a.pier_size / 2

    # ---- read and sort the drawing (full resolution)
    ink, shape = read_ink(a.image, a.crop, a.threshold, a.faint)

    # ---- scale: measured (--calibrate) or assumed (--width)
    calib = None
    if a.calibrate:
        x0, y0, x1, y1, length = a.calibrate
        dist = float(np.hypot(x1 - x0, y1 - y0))
        if dist <= 0 or length <= 0:
            sys.exit("--calibrate: the two points must differ and the length must be > 0")
        upp = length / dist
        a.width = shape[1] * upp
        calib = dict(p0=[x0, y0], p1=[x1, y1], real_length=length,
                     unit=a.unit or "blocks", units_per_pixel=upp)
        print(f"scale: {dist:.1f} px = {length:g} {calib['unit']}  ->  "
              f"{upp:.4f} {calib['unit']}/px, plan is {a.width:.1f} wide")
    unit = a.unit or ("blocks" if calib else "units")
    pier_h = a.pier_height if a.pier_height is not None else 0.3 * a.width
    floor_t = 0.0 if a.no_floor else a.floor

    piers, big, shafts, dropped, lines, junk = classify(ink, a.pier_size, dot_r, a.dots, a.min_span)
    line_polys = lines_to_polylines(lines, a.prune)
    pier_polys = pier_polygons(piers)
    full_px_u = a.width / shape[1]                   # units per original pixel
    print(f"piers: {len(pier_polys)} outlines, lines: {len(line_polys)} polylines")

    save_plan_png(piers, line_polys, shape, stem + "_plan.png")
    save_classes_png(ink, big, shafts, dropped, lines, junk, stem + "_classes.png")
    if a.svg:
        save_svg(pier_polys, line_polys, shape, full_px_u, stem + "_plan.svg")
    if a.dxf:
        save_dxf(pier_polys, line_polys, shape, full_px_u, stem + "_plan.dxf")
    if a.piers_json is not None:
        jpath = a.piers_json or os.path.join(os.path.dirname(os.path.abspath(out)), "piers.json")
        save_piers_json(piers, big, shape, full_px_u, a, unit, jpath, stem + "_piers.png")

    # ---- 3D grid (used for raster parts and the preview)
    s = min(1.0, a.max_size / max(shape))
    gshape = (max(2, round(shape[0] * s)), max(2, round(shape[1] * s)))
    px_u = a.width / gshape[1]
    line_full = rasterize_lines(line_polys, shape, a.line_width / full_px_u)
    P = no_diagonal_touches(shrink(piers, gshape))
    L = no_diagonal_touches(shrink(line_full, gshape))
    Wg, Hg = gshape[1] * px_u, gshape[0] * px_u
    ones = np.ones(gshape, bool)
    zeros = np.zeros(gshape)

    mode = a.lines if (a.lines != "floor" or floor_t > 0) else "walls"
    sink = floor_t / 2 if floor_t > 0 else 0.0          # bodies start inside the slab
    v08 = None if (a.raster or mode in ("walls", "floor")) else find_v08()
    if not a.raster and mode in ("ribs", "none") and v08 is None:
        print("note: gothic_v08 folder not found - using the pixel (raster) method. "
              "Put the gothic_v08 folder next to plan2stl.py for clean vector output.")
    if a.rib_profile and (v08 is None or mode != "ribs"):
        print("note: --rib-profile needs vector ribs (--lines ribs and the gothic_v08 folder); ignored")

    bodies, layers, report = [], [], []
    if mode == "floor":
        h = np.full(gshape, floor_t)
        d = ndi.distance_transform_edt(L)
        h += a.relief * np.sqrt(np.clip(d / max(1, a.line_width / px_u / 2), 0, 1)) * L
        h[P] = pier_h
        bodies.append(mesh_cells(h, ones, px_u, smooth_edges=0))
        layers = [(ones, h, zeros, (0.72, 0.68, 0.6)), (P, h, zeros, (0.85, 0.8, 0.7))]
    else:
        if floor_t > 0:
            bodies.append(box_mesh(0, 0, Wg, Hg, 0, floor_t))
            layers.append((ones, np.full(gshape, floor_t), zeros, (0.72, 0.68, 0.6)))
        if mode == "walls":
            solid = no_diagonal_touches(P | L)
            h = np.where(P, pier_h, a.wall_height)
            bodies.append(mesh_cells(h, solid, px_u, hb=np.full(gshape, sink)))
            layers.append((solid, h, zeros, (0.85, 0.8, 0.7)))
        else:
            layers.append((P, np.full(gshape, pier_h), zeros, (0.85, 0.8, 0.7)))
            if v08:
                vb, left, msg = vector_piers(piers, shape, full_px_u, sink, pier_h)
                bodies += vb
                report.append(msg)
                if left.any():                        # the ones that would not trace
                    Pl = no_diagonal_touches(shrink(left, gshape))
                    bodies.append(mesh_cells(np.full(gshape, pier_h), Pl, px_u, hb=np.full(gshape, sink)))
            else:
                bodies.append(mesh_cells(np.full(gshape, pier_h), P, px_u, hb=np.full(gshape, sink)))
            if mode == "ribs":                        # ribs sit a hair proud of the pier tops
                top, bot = np.full(gshape, pier_h + 0.02 * a.rib_depth), np.full(gshape, pier_h - a.rib_depth)
                layers.append((L, top, bot, (0.6, 0.55, 0.48)))
                if v08:
                    rb, msg = vector_ribs(line_polys, shape, full_px_u, a, pier_h)
                    bodies += rb
                    report.append(msg)
                else:
                    bodies.append(mesh_cells(top, L, px_u, hb=bot))
    n = write_stl(bodies, out)
    print(f"wrote {out}: {n:,} triangles, {Wg:.1f} x {Hg:.1f} x {pier_h:.1f} {unit}, "
          f"{len(bodies)} bodies ({'vector' if v08 else 'raster'})")
    for m in report:
        print("  " + m)
    save_meta(a, shape, calib, unit, stem + "_meta.json", out, n, bool(v08))
    if a.preview:
        render_oblique(layers, px_u, stem + "_preview.png")
        print(f"preview: {stem}_preview.png")


# ------------------------------------------------------- vector parts -----
def to_world(rc, H, u):
    """(row, col) pixel points -> plan (x, y) with y up, matching the raster mesher."""
    rc = np.asarray(rc, float)
    return np.column_stack([rc[:, 1] * u, (H - rc[:, 0]) * u])


def vector_piers(piers, shape, u, z0, z1):
    """Each pier outline -> a clean vertical prism.  Returns (meshes, mask of
    piers that could not be traced, report line)."""
    import gothic_adapters as ad
    filled = ndi.binary_fill_holes(piers)
    lab, n = ndi.label(filled, structure=N8)
    meshes, left, holes = [], np.zeros_like(piers), int((filled & ~piers).sum() > 0)
    for i, sl in enumerate(ndi.find_objects(lab), 1):
        comp = lab[sl] == i
        pad = np.pad(comp, 1)
        cs = find_contours(pad.astype(float), 0.5)
        if not cs:
            continue
        c = max(cs, key=len) + [sl[0].start - 1, sl[1].start - 1]
        ok = False
        for tol in (1.0, 0.6, 1.8):
            poly = approximate_polygon(c, tolerance=tol)
            try:
                meshes.append(ad.prism_from_polygon(to_world(poly, shape[0], u), z0, z1))
                ok = True
                break
            except ValueError:
                continue
        if not ok:
            left[sl] |= comp
    msg = f"piers: {len(meshes)} traced as vector prisms"
    if left.any():
        msg += f", {ndi.label(left)[1]} kept as pixels (outline would not trace cleanly)"
    if holes:
        msg += "; holes inside piers were filled"
    return [(m.vertices, m.faces) for m in meshes], left, msg


def vector_ribs(line_polys, shape, u, a, pier_h):
    """Each traced line -> a swept bar with the rib section, hanging from the
    pier tops.  Ends that meet are covered with a small octagonal boss."""
    import gothic_adapters as ad
    prof = None
    if a.rib_profile:
        prof = ad.profile_from_png(a.rib_profile)
        print(f"rib section: {a.rib_profile}  ({len(prof)} outline points)")
    z0 = pier_h - a.rib_depth
    w = a.line_width
    paths = [to_world(p, shape[0], u) for p in line_polys]
    length = lambda xy: float(np.linalg.norm(np.diff(xy, axis=0), axis=1).sum())
    stubs = sum(length(xy) < 0.5 * w for xy in paths)
    chains, links = chain_paths([xy for xy in paths if length(xy) >= 0.5 * w], 1.5 * w)
    meshes, skipped, rings = [], 0, 0
    for xy in chains:
        closed = len(xy) > 3 and np.linalg.norm(xy[0] - xy[-1]) < 0.5 * w
        try:
            m = ad.sweep_centerline(xy, w, a.rib_depth + 0.02 * a.rib_depth, prof, z0=z0,
                                    closed=closed)
            meshes.append((m.vertices, m.faces))
            rings += closed
        except ValueError:
            skipped += 1
    # a boss wherever a run ends (at a pier, a junction or a crossing), to close the joint
    ends = [q for xy in chains if not (len(xy) > 3 and np.linalg.norm(xy[0] - xy[-1]) < 0.5 * w)
            for q in (xy[0], xy[-1])]
    # bosses where lines meet / end, so the joints are closed
    if ends:
        E = np.round(np.array(ends) / (0.25 * w)).astype(int)
        _, first = np.unique(E, axis=0, return_index=True)
        k = np.arange(8) * np.pi / 4 + np.pi / 8
        r = 0.55 * w / np.cos(np.pi / 8)
        ring = np.column_stack([np.cos(k), np.sin(k)]) * r
        for c in np.array(ends)[first]:
            m = ad.prism_from_polygon(ring + c, z0, pier_h + 0.02 * a.rib_depth)
            meshes.append((m.vertices, m.faces))
        nb = len(first)
    else:
        nb = 0
    return meshes, (f"ribs: {len(line_polys)} traced pieces joined into {len(chains)} runs "
                    f"({links} joins, {rings} closed rings)"
                    f"{', section from ' + a.rib_profile if a.rib_profile else ''}; "
                    f"{nb} bosses at joints; {stubs} tiny stubs left to the bosses"
                    + (f"; {skipped} runs too tight to sweep" if skipped else ""))


def chain_paths(paths, max_gap, max_turn=25.0):
    """Join traced pieces that carry on in the same direction across a gap
    (a rib broken at a crossing) into one continuous run, using the V08
    conservative join test (tangent agreement, no ambiguous choices)."""
    import gothic_geometry as geo
    paths = [np.asarray(p, float) for p in paths]
    total = 0
    while True:
        try:
            cands = geo.joining_candidates(paths, max_gap=max_gap, max_turn_degrees=max_turn)
        except ValueError:
            cands = []
        used, merged, done = set(), [], set()
        for c in cands:
            (i, si), (j, sj) = c["a"], c["b"]
            if i in used or j in used:
                continue
            A = paths[i] if si == 1 else paths[i][::-1]       # A ends at the joint
            B = paths[j] if sj == 0 else paths[j][::-1]       # B starts at the joint
            merged.append(np.vstack([A, B]))
            used.update((i, j))
        if not merged:
            return paths, total
        total += len(merged)
        paths = [p for k, p in enumerate(paths) if k not in used] + merged


# ---------------------------------------------------- piers.json / meta -----
def save_piers_json(piers, big, shape, u, a, unit, path, label_png):
    """Pier centres in the format sweep2schem.py reads (--pier-file), with a
    picture showing which name is which."""
    lab, n = ndi.label(piers, structure=N8)
    if not n:
        print("piers.json: no piers found")
        return
    idx = np.arange(1, n + 1)
    cy, cx = np.array(ndi.center_of_mass(piers, lab, idx)).T
    area = ndi.sum(piers, lab, idx)
    is_big = ndi.maximum(big, lab, idx) > 0
    band = max(3 * a.pier_size, 10)
    order = np.lexsort((cx, np.round(cy / band)))
    data = {"schema": "sweep-piers-v1", "units": unit,
            "note": ("x = across the drawing (left to right), z = down the drawing "
                     "(top to bottom, = south in Minecraft); centres of the black masses"),
            "source": os.path.basename(a.image), "crop_px": a.crop,
            "origin": [0, 0, 0], "piers": {}}
    if a.datum_y is not None:
        data["geometry"] = {"plan_datum_y": a.datum_y}
    im = Image.open(stem_plan := label_png.replace("_piers.png", "_plan.png")).convert("RGB")
    d = ImageDraw.Draw(im)
    try:
        from PIL import ImageFont
        font = ImageFont.load_default(size=max(14, shape[1] // 60))
    except TypeError:
        font = None
    for k, i in enumerate(order, 1):
        name = f"P{k:02d}"
        x = cx[i] * u + a.origin[0]
        z = cy[i] * u + a.origin[1]
        data["piers"][name] = {"x": round(float(x), 3), "z": round(float(z), 3),
                               "kind": "pier" if is_big[i] else "shaft",
                               "area": round(float(area[i] * u * u), 3)}
        d.text((cx[i], cy[i]), name, fill=(220, 0, 0) if is_big[i] else (0, 90, 220),
               font=font, anchor="mm",
               stroke_width=2, stroke_fill=(255, 255, 255))
    with open(path, "w") as f:
        json.dump(data, f, indent=1)
    im.save(label_png)
    print(f"piers.json: {path} ({int(is_big.sum())} piers + {int((~is_big).sum())} shafts, {unit}); "
          f"names shown on {label_png} (red = pier, blue = shaft)")
    if unit != "blocks":
        print("  note: sweep2schem works in blocks - use --calibrate (or --unit blocks) "
              "so the numbers are real block positions")


def save_meta(a, shape, calib, unit, path, out, ntris, vector):
    h = hashlib.sha256()
    with open(a.image, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    meta = {"schema": "gothic.plate.v08", "tool": "plan2stl", "time": time.strftime("%Y-%m-%d %H:%M"),
            "source": os.path.abspath(a.image), "sha256": h.hexdigest(),
            "crop_px": a.crop, "analyzed_size_px": [shape[1], shape[0]],
            "units": unit, "width": a.width,
            "calibration": calib, "historical_scale_verified": bool(calib),
            "note": ("Scale measured by the user (--calibrate)." if calib else
                     "Uncalibrated: the size comes from --width, not from the drawing."),
            "output": os.path.abspath(out), "triangles": ntris,
            "method": "vector" if vector else "raster",
            "command": " ".join(sys.argv)}
    with open(path, "w") as f:
        json.dump(meta, f, indent=1)


if __name__ == "__main__":
    main()
