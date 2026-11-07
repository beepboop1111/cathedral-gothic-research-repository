#!/usr/bin/env python3
"""
sketch2stl.py - turn black-and-white drawings into 3D STL models.
Works on one picture, several pictures, or a whole folder of pictures.

Two modes:

  RELIEF (default)   Black lines become raised, rounded ridges on a flat plate,
                     like a carved stone panel.

  PIERCED (--pierce) For tracery and other open-work drawings.  The big empty
                     spaces in the drawing (the glass) are cut right through,
                     the area outside the outline is thrown away, and what is
                     left is the stonework, with its moulding lines raised on it.
                     Thin bands between parallel lines stay as stone - only
                     spaces wide enough to fit a circle of --opening pixels
                     radius count as openings.

Usage:
  one picture
    python3 sketch2stl.py drawing.png
    python3 sketch2stl.py drawing.png --pierce --crop 400 0 1555 1787 -o window.stl

  a whole folder (put the folder name in quotes if it has spaces)
    python3 sketch2stl.py "Sketch to Tracery" --make-settings   (writes the settings file)
    python3 sketch2stl.py "Sketch to Tracery"                   (makes every model)
    python3 sketch2stl.py "Sketch to Tracery" --only 1.png 4.png   (just these two)

Folder mode:
    Every picture in the folder (png, jpg, tif, bmp, webp) is made into an STL.
    The models go into a sub-folder called  stl  inside the picture folder
    (change it with --out-dir), together with a summary of the run,
    sketch2stl_summary.txt.  One picture failing does not stop the others.

    Each picture can have its own options, written in a plain text file in the
    picture folder called  sketch2stl_settings.txt.  --make-settings creates
    it, with one line per picture, ready to fill in:
        ALL:     --width 150 --max-size 2000           <- used for every picture
        1.png:   --pierce --fill 16 17 --base 3        <- just for 1.png
        4.png:   --crop 0 0 250 330  -o 4_left.stl     <- two models from 4.png
        4.png:   --crop 250 0 500 330 -o 4_right.stl
        7V99.png: skip                                 <- leave this one out
    Options typed on the command line win over the settings file.

Options (all optional):
    -o / --out        output file name (default: same name as image, .stl)
    --width           finished width of the model in mm   (default 150).  This is
                      the width of the whole picture (or of the --crop area)
    --base            thickness of the flat plate / stone in mm
                      (default 2, or 4 with --pierce)
    --relief          how far the lines stand up, in mm   (default 2.5, or 1.2 with --pierce)
    --thicken         widen thin lines by this many pixels (default 1)
    --round           how rounded the ridges are, 0 = sharp square (default 1.5)
    --max-size        longest side of the mesh grid in pixels (default 800;
                      bigger = more detail but a much bigger file).  It only
                      ever shrinks: above the picture's own size it does nothing
    --max-triangles   upper limit on model size (default 20000000, about 1 GB);
                      the grid is made coarser if a model would be bigger
    --crop x0 y0 x1 y1  only use this pixel rectangle of the image
    --invert          use this if your drawing is WHITE lines on BLACK
    --threshold       how dark a pixel must be to count as a line, 0-1
                      (default 0.6, or 0.8 when the paper is evened out)
    --flatten         even out grey or unevenly lit paper (photos of drawings):
                      auto (default - only when the paper looks uneven), on, off
  pierced mode only:
    --opening         smallest opening to cut, as a radius in pixels of the
                      ORIGINAL image (default 14). Raise it if stone bands get
                      cut; lower it if small openings are left filled in.
    --outside-edges   which image edges count as "outside the object"
                      (default tlrb = top, left, right, bottom).  Use tlr when the
                      drawing is cut off at the bottom, so openings that run off
                      the bottom edge are still treated as glass.
    --keep-labels     keep small separate marks (letters, numbers) as ridges;
                      by default they are left off the stone
    --mask-preview    also save a PNG showing what was kept / cut, with every
                      opening numbered, for checking
    --preview         also save a shaded picture of the finished model
    --fill N N ...    openings (by number from --mask-preview) to leave solid
    --min-opening     openings smaller than this many pixels are left solid
                      (default 1200)
    --edge            profile cut on the edges of the bars:
                      chamfer (default), round, hollow, ogee, or none
    --edge-width      how far in from the edge the profile runs, mm (default 1.5)
    --edge-depth      how far down the profile cuts, mm (default = edge-width).
                      Limited to (base - 0.8) mm, or half that with --both-sides
    --both-sides      cut the edge profile on the back too, like real tracery
                      (the back is then no longer flat)
  folder mode only:
    --out-dir         where to put the models (default: a folder called stl
                      inside the picture folder)
    --only NAME ...   only make these pictures from the folder
    --make-settings   write (or top up) sketch2stl_settings.txt and stop

Needs: numpy, scipy, pillow
    sudo apt install python3-numpy python3-scipy python3-pil
"""
import argparse, math, os, re, shlex, struct, sys, time
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

SETTINGS_NAME = "sketch2stl_settings.txt"
SUMMARY_NAME = "sketch2stl_summary.txt"
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp", ".gif"}


# ---------------------------------------------------------------- image ----
def paper_level(g):
    """Brightness of the bare paper everywhere, with the drawn lines removed."""
    H, W = g.shape
    k = max(1, round(max(H, W) / 400))
    sm = np.asarray(Image.fromarray(g, mode="F").resize(
        (max(1, W // k), max(1, H // k)), Image.BOX), np.float32)
    size = max(15, round(max(sm.shape) / 25))
    bg = ndi.grey_closing(sm, size=(size, size))       # paint over the dark lines
    bg = ndi.gaussian_filter(bg, size / 2)
    return bg


def load_gray(path, crop, invert, flatten, notes):
    """Picture -> grey array, 0 = black, 1 = white paper.  Returns (g, evened)."""
    img = Image.open(path)
    if img.mode in ("RGBA", "LA", "PA") or "transparency" in img.info:
        img = img.convert("RGBA")                       # see-through = white paper
        img = Image.alpha_composite(Image.new("RGBA", img.size, (255, 255, 255, 255)), img)
    img = img.convert("L")
    if crop:
        W, H = img.size
        x0, y0, x1, y1 = crop
        c = (min(max(x0, 0), W), min(max(y0, 0), H), min(max(x1, 0), W), min(max(y1, 0), H))
        if c[2] - c[0] < 2 or c[3] - c[1] < 2:
            raise ValueError(f"--crop {x0} {y0} {x1} {y1} is outside the picture "
                             f"({W} x {H} pixels)")
        if c != tuple(crop):
            notes.append(f"crop trimmed to the picture: {c[0]} {c[1]} {c[2]} {c[3]}")
        img = img.crop(c)
    g = np.asarray(img, dtype=np.float32) / 255.0
    if invert:
        g = 1.0 - g
    if flatten == "off":
        return g, False
    bg = paper_level(g)
    med, low = float(np.median(bg)), float(np.percentile(bg, 2))
    if flatten == "auto" and not (med < 0.8 or med - low > 0.15):
        return g, False
    bg = np.asarray(Image.fromarray(bg, mode="F").resize(
        (g.shape[1], g.shape[0]), Image.BILINEAR), np.float32)
    notes.append("paper evened out" + (" (looked like a photo / uneven scan)"
                                       if flatten == "auto" else ""))
    return np.clip(g / np.maximum(bg, 0.05), 0, 1), True


def shrink(arr, shape):
    """Area-average resize of a float or bool array to shape (rows, cols)."""
    im = Image.fromarray((arr.astype(np.float32) * 255).astype(np.uint8))
    return np.asarray(im.resize((shape[1], shape[0]), Image.BOX),
                      dtype=np.float32) / 255.0


def drop_small(mask, min_px):
    lab, n = ndi.label(mask)
    if not n:
        return mask
    sizes = ndi.sum(mask, lab, range(1, n + 1))
    return np.isin(lab, np.nonzero(sizes >= min_px)[0] + 1)


def ridge_profile(ink, thicken, rounding):
    if thicken > 0:
        ink = ndi.binary_dilation(ink, iterations=int(thicken))
    ink = drop_small(ink, 6)
    if rounding <= 0:
        return ink.astype(np.float32)
    d = ndi.distance_transform_edt(ink)
    prof = np.sqrt(np.clip(d / rounding, 0, 1))      # quarter-round shoulder
    return ndi.gaussian_filter(prof, 0.6) * ink


# ------------------------------------------------------ opening detection ----
def find_stone(g, radius, edges, min_area=1200, fill=(), threshold=0.6):
    """Full-resolution masks: (numbered openings, outside, ink, how many openings)."""
    ink = g < threshold

    def open_space(walls):
        free = ~ndi.binary_dilation(walls, iterations=2)
        # where a disc of `radius` fits entirely in white space
        dt = ndi.distance_transform_edt(np.pad(free, 1, constant_values=True))[1:-1, 1:-1]
        core = dt >= radius
        void = (ndi.distance_transform_edt(~core) <= radius) & free
        # grow back into the corners the disc could not reach
        for _ in range(radius + 2):
            void = ndi.binary_dilation(void) & free
        return void

    void = open_space(ink)
    lab, _ = ndi.label(void)
    sides = {"t": lab[0], "b": lab[-1], "l": lab[:, 0], "r": lab[:, -1]}
    out_ids = np.unique(np.concatenate([sides[e] for e in edges if e in sides] or [[0]]))
    outside = np.isin(lab, out_ids[out_ids > 0])
    glass = void & ~outside
    # trim thin slivers that crept into carved heads and line breaks
    outside = ndi.binary_opening(outside, disk(5), border_value=1)
    glass = ndi.binary_opening(glass, disk(5))
    # number the openings (top to bottom, left to right) and drop tiny ones
    glab, gn = ndi.label(glass)
    n_open = 0
    if gn:
        area = ndi.sum(glass, glab, range(1, gn + 1))
        cy, cx = np.array(ndi.center_of_mass(glass, glab, range(1, gn + 1))).T
        keep = np.nonzero(area >= min_area)[0]
        order = keep[np.lexsort((cx[keep], (cy[keep] // 60)))]
        new = np.zeros(gn + 1, np.int32)
        new[order + 1] = np.arange(1, len(order) + 1)
        glab = new[glab]
        n_open = len(order)
        for i in fill:                              # openings the user wants solid
            glab[glab == i] = 0
        glass = glab > 0
    return glab, outside, ink, n_open


def stone_from(glass, outside):
    """Stone = biggest connected piece of what is not cut away."""
    stone = ~(glass | outside)
    sl, sn = ndi.label(stone)
    if sn:
        sizes = ndi.sum(stone, sl, range(1, sn + 1))
        stone = sl == (np.argmax(sizes) + 1)
    return stone


def disk(r):
    y, x = np.ogrid[-r:r + 1, -r:r + 1]
    return x * x + y * y <= r * r


def clean_ink(ink, keep_labels):
    """Join dashed lines into continuous ones; drop letters and specks.
    Long lines are kept as drawn.  Short pieces are bridged across small gaps;
    the chains that come out long are kept as lines, the short compact blobs
    (letters, numbers, dots) are thrown away."""
    lab, n = ndi.label(ink, structure=np.ones((3, 3)))
    if not n:
        return ink
    area = ndi.sum(ink, lab, range(1, n + 1))
    big = np.isin(lab, np.nonzero(area >= 400)[0] + 1)
    small = ink & ~big
    # bridge each short piece only along its own direction, so dashes join
    # end-to-end without merging with the parallel line next to them
    slab, sn = ndi.label(small, structure=np.ones((3, 3)))
    bridged = small.copy()
    if sn:
        idx = np.arange(1, sn + 1)
        cnt = ndi.sum(small, slab, idx)
        ys, xs = np.mgrid[0:ink.shape[0], 0:ink.shape[1]]
        my = ndi.sum(ys * small, slab, idx) / cnt
        mx = ndi.sum(xs * small, slab, idx) / cnt
        syy = ndi.sum(ys * ys * small, slab, idx) / cnt - my * my
        sxx = ndi.sum(xs * xs * small, slab, idx) / cnt - mx * mx
        sxy = ndi.sum(xs * ys * small, slab, idx) / cnt - mx * my
        ang = 0.5 * np.arctan2(2 * sxy, sxx - syy)          # main axis of each piece
        nbins = 16
        b = np.round((ang % np.pi) / np.pi * nbins).astype(int) % nbins
        b[cnt < 4] = -1                                      # specks: no direction
        lut = np.full(sn + 1, -1); lut[1:] = b
        pb = lut[slab]
        for k in range(nbins):
            part = pb == k
            if part.any():
                bridged |= ndi.binary_closing(part, line_se(k * np.pi / nbins, 13))
    blab, bn = ndi.label(bridged, structure=np.ones((3, 3)))
    if bn:
        sl = ndi.find_objects(blab)
        span = np.array([max(s[0].stop - s[0].start, s[1].stop - s[1].start) for s in sl])
        minspan = 1 if keep_labels else 45
        bridged = np.isin(blab, np.nonzero(span >= minspan)[0] + 1)
    return big | bridged


def line_se(theta, length):
    """Straight-line structuring element at angle theta (radians from +x)."""
    r = length // 2
    t = np.linspace(-r, r, 4 * length)
    xs = np.round(t * np.cos(theta)).astype(int) + r
    ys = np.round(t * np.sin(theta)).astype(int) + r
    se = np.zeros((2 * r + 1, 2 * r + 1), bool)
    se[ys, xs] = True
    return se


def edge_drop(dist_mm, kind, width, depth):
    """How far the stone face drops at a given distance from the cut edge."""
    t = np.clip(dist_mm / max(width, 1e-6), 0, 1)        # 0 at edge, 1 inside
    if kind == "chamfer":
        f = 1 - t
    elif kind == "round":                                # convex quarter-round
        f = 1 - np.sqrt(1 - (1 - t) ** 2)
    elif kind == "hollow":                               # concave cavetto
        f = np.sqrt(np.clip(1 - t * t, 0, 1))
    elif kind == "ogee":                                 # S-curve: roll then hollow
        f = 0.5 * (1 + np.cos(np.pi * t))
    else:
        f = np.zeros_like(t)
    return depth * f


def no_diagonal_touches(c):
    """Fill cells so no two solid cells meet only at a corner (keeps mesh manifold)."""
    c = c.copy()
    while True:
        a, b, d, e = c[:-1, :-1], c[:-1, 1:], c[1:, :-1], c[1:, 1:]
        bad = (a & e & ~b & ~d) | (b & d & ~a & ~e)
        if not bad.any():
            return c
        r, k = np.nonzero(bad)
        c[r, k] = c[r, k + 1] = c[r + 1, k] = c[r + 1, k + 1] = True


def save_preview(g, glab, outside, ink, out):
    from PIL import ImageDraw, ImageFont
    pv = np.full(g.shape + (3,), 255, np.uint8)
    pv[glab > 0] = [120, 170, 220]; pv[outside] = [45, 45, 45]
    pv[ink] = [0, 0, 0]
    im = Image.fromarray(pv)
    dr = ImageDraw.Draw(im)
    try:
        font = ImageFont.load_default(size=max(14, g.shape[1] // 50))
    except TypeError:
        font = ImageFont.load_default()
    for i in np.unique(glab[glab > 0]):
        ys, xs = np.nonzero(glab == i)
        cy, cx = ys.mean(), xs.mean()
        k = np.argmin((ys - cy) ** 2 + (xs - cx) ** 2)   # a pixel inside the opening
        dr.text((xs[k], ys[k]), str(i), fill=(200, 0, 0), font=font,
                anchor="mm", stroke_width=2, stroke_fill=(255, 255, 255))
    prev = out.rsplit(".", 1)[0] + "_mask.png"
    im.save(prev)
    print(f"mask preview: {prev}  (blue = cut through, numbered; dark = discarded)")


def save_shaded(h, solid, out):
    """Quick lit picture of the model seen from the front."""
    hs = ndi.gaussian_filter(np.where(solid, h, 0.0), 0.6)
    gy, gx = np.gradient(hs * 3)
    L = np.array([-1.0, 1.0, 1.3]); L /= np.linalg.norm(L)
    n = np.dstack([-gx, gy, np.ones_like(h)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    lit = np.clip(n @ L, 0, 1)
    sh = ndi.gaussian_filter(ndi.shift(solid.astype(float), (6, 4), order=0), 2)
    bg = np.array([0.62, 0.72, 0.86]) * (1 - 0.5 * sh)[..., None]
    st = (0.25 + 0.75 * lit)[..., None] * np.array([0.88, 0.84, 0.76])
    img = np.where(solid[..., None], st, bg)
    prev = out.rsplit(".", 1)[0] + "_preview.png"
    Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).save(prev)
    print(f"shaded preview: {prev}")


# ------------------------------------------------------------------ mesh ----
def mesh_cells(h, solid, px_mm, smooth_edges=2, hb=None):
    """Solid cells (pixels) -> closed triangle mesh: top, bottom, side walls.
    Returns (V, F) with V in mm."""
    H, W = solid.shape
    nv = (H + 1) * (W + 1)
    vid = lambda r, c: r * (W + 1) + c
    # vertex heights = mean of the solid cells touching that corner
    pad = np.pad(solid, 1).astype(np.int32)
    hp = np.pad(np.where(solid, h, 0.0), 1)
    cnt = pad[:-1, :-1] + pad[:-1, 1:] + pad[1:, :-1] + pad[1:, 1:]
    tot = hp[:-1, :-1] + hp[:-1, 1:] + hp[1:, :-1] + hp[1:, 1:]
    vz = np.where(cnt > 0, tot / np.maximum(cnt, 1), 0.0)
    if hb is None:
        vzb = np.zeros_like(vz)
    else:
        hbp = np.pad(np.where(solid, hb, 0.0), 1)
        vzb = (hbp[:-1, :-1] + hbp[:-1, 1:] + hbp[1:, :-1] + hbp[1:, 1:]) / np.maximum(cnt, 1)
    rr, cc = np.mgrid[0:H + 1, 0:W + 1]
    xy = np.stack([cc * px_mm, (H - rr) * px_mm], -1).reshape(-1, 2).astype(np.float64)

    r, c = np.nonzero(solid)
    a, b, d, e = vid(r, c), vid(r, c + 1), vid(r + 1, c), vid(r + 1, c + 1)
    F = [np.stack([a, d, b], 1), np.stack([b, d, e], 1),               # top
         np.stack([a, b, d], 1) + nv, np.stack([b, e, d], 1) + nv]     # bottom
    edges = []
    # walls: for every cell side that faces an empty cell (or the border)
    for dr, dc, p, q in [(-1, 0, (0, 0), (0, 1)), (1, 0, (1, 1), (1, 0)),
                         (0, -1, (1, 0), (0, 0)), (0, 1, (0, 1), (1, 1))]:
        nr, nc = r + dr, c + dc
        inside = (nr >= 0) & (nr < H) & (nc >= 0) & (nc < W)
        empty = ~inside
        empty[inside] = ~solid[nr[inside], nc[inside]]
        rs, cs = r[empty], c[empty]
        u = vid(rs + p[0], cs + p[1])
        v = vid(rs + q[0], cs + q[1])
        F += [np.stack([u, v, v + nv], 1), np.stack([u, v + nv, u + nv], 1)]
        edges.append(np.stack([u, v], 1))
    F = np.concatenate(F)

    # soften the pixel staircase on cut edges: slide edge vertices along the edge
    E = np.concatenate(edges)
    on_edge = np.zeros(nv, bool); on_edge[E.ravel()] = True
    for _ in range(smooth_edges):
        s = np.zeros((nv, 2)); k = np.zeros(nv)
        np.add.at(s, E[:, 0], xy[E[:, 1]]); np.add.at(k, E[:, 0], 1)
        np.add.at(s, E[:, 1], xy[E[:, 0]]); np.add.at(k, E[:, 1], 1)
        m = on_edge & (k > 0)
        xy[m] = 0.5 * xy[m] + 0.5 * s[m] / k[m, None]

    V = np.concatenate([np.column_stack([xy, vz.ravel()]),
                        np.column_stack([xy, vzb.ravel()])])
    # keep only used vertices
    used = np.unique(F)
    remap = np.full(len(V), -1); remap[used] = np.arange(len(used))
    return V[used], remap[F]


def mesh_full(h, px_mm):
    return mesh_cells(h, np.ones(h.shape, bool), px_mm, smooth_edges=0)


def write_stl(V, F, path):
    T = V[F].astype(np.float32)
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
    n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
    rec = np.zeros(len(T), dtype=[("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
    rec["n"], rec["v"] = n, T
    with open(path, "wb") as f:
        f.write(b"sketch2stl".ljust(80, b" "))
        f.write(struct.pack("<I", len(T)))
        rec.tofile(f)
    return len(T)


# ------------------------------------------------------- one picture ----
def make_model(path, a, out):
    """Turn one picture into one STL.  Returns a dict of results for the summary."""
    notes = []
    base = a.base if a.base is not None else (4.0 if a.pierce else 2.0)
    relief = a.relief if a.relief is not None else (1.2 if a.pierce else 2.5)

    g, evened = load_gray(path, a.crop, a.invert, a.flatten, notes)
    thr = a.threshold if a.threshold is not None else (0.8 if evened else 0.6)
    s = min(1.0, a.max_size / max(g.shape))

    def grid(scale):
        return (max(2, round(g.shape[0] * scale)), max(2, round(g.shape[1] * scale)))

    def cap(scale, tris_per_cell):
        """Make the grid coarser if the model would pass --max-triangles."""
        shape = grid(scale)
        est = tris_per_cell * shape[0] * shape[1]
        if est > a.max_triangles:
            scale *= math.sqrt(a.max_triangles / est)
            shape = grid(scale)
            notes.append(f"grid made coarser ({shape[1]} x {shape[0]}) "
                         f"to stay under --max-triangles {a.max_triangles:,}")
        return shape

    if a.pierce:
        glab, outside, ink, n_open = find_stone(g, a.opening, a.outside_edges.lower(),
                                                a.min_opening, a.fill, thr)
        missing = [i for i in a.fill if not 1 <= i <= n_open]
        if missing:
            notes.append(f"--fill {' '.join(map(str, missing))}: no opening with that "
                         f"number (only 1-{n_open}) - check the _mask.png")
        notes.append(f"{n_open} openings found" +
                     (f", {len(a.fill) - len(missing)} filled" if a.fill else ""))
        glass = glab > 0
        stone = stone_from(glass, outside)
        if not stone.any():
            raise RuntimeError("no stonework left after cutting the openings")
        shape = cap(s, 4.4 * stone.mean())
        ink = clean_ink(ink, a.keep_labels) & stone
        solid = shrink(stone, shape) >= 0.5
        solid = no_diagonal_touches(stone_from(~solid, np.zeros_like(solid)))
        lines = shrink(ink, shape) > 0.25
        px_mm = a.width / shape[1]

        # edge profile, measured from the cut edge at full resolution
        full_mm = a.width / g.shape[1]
        dist = ndi.distance_transform_edt(stone) * full_mm
        dist_s = shrink(np.minimum(dist, 50) / 50, shape) * 50
        both = a.both_sides
        want = a.edge_depth if a.edge_depth is not None else a.edge_width
        limit = max(0.0, (base - 0.8) / (2 if both else 1))
        if a.edge != "none" and want > limit:
            notes.append(f"edge cut limited to {limit:.2f} mm deep by --base {base:g} "
                         f"(--base {want * (2 if both else 1) + 0.8:g} or more gives "
                         f"the full {want:g} mm)")
        depth = min(want, limit)
        drop = edge_drop(dist_s, a.edge, a.edge_width, depth)
        # ridges only on the flat face, not running down the edge profile
        face = np.clip((dist_s - a.edge_width) / max(px_mm, 1e-6), 0, 1)
        h = base - drop + relief * ridge_profile(lines, a.thicken, a.rounding) * face
        hb = drop if both else None
        V, F = mesh_cells(h, solid, px_mm, hb=hb)
        if a.preview:
            save_shaded(h, solid, out)
        if a.mask_preview:
            save_preview(g, glab, outside | ~(stone | glass), ink, out)
    else:
        shape = cap(s, 4.0)
        g_small = shrink(g, shape)
        h = base + relief * ridge_profile(g_small < thr, a.thicken, a.rounding)
        px_mm = a.width / (shape[1] - 1)
        V, F = mesh_full(h, px_mm)
        if a.preview:
            save_shaded(h, np.ones(h.shape, bool), out)

    n = write_stl(V, F, out)
    span = V.max(0) - V.min(0)
    print(f"wrote {out}: {n:,} triangles, "
          f"{span[0]:.0f} x {span[1]:.0f} x {span[2]:.1f} mm")
    for t in notes:
        print(f"  note: {t}")
    return {"tris": n, "span": span, "mb": os.path.getsize(out) / 1e6, "notes": notes}


# ------------------------------------------------------------ options ----
class _Parser(argparse.ArgumentParser):
    """Parser for a settings-file line: report problems instead of quitting."""
    def error(self, message):
        raise ValueError(message)


def add_model_options(p, suppress=False):
    """The options that describe one model.  With suppress=True, options that
    are not typed are left out entirely, so we can tell which ones were typed."""
    D = (lambda v: argparse.SUPPRESS) if suppress else (lambda v: v)
    p.add_argument("-o", "--out", default=D(None))
    p.add_argument("--width", type=float, default=D(150))
    p.add_argument("--base", type=float, default=D(None))
    p.add_argument("--relief", type=float, default=D(None))
    p.add_argument("--thicken", type=int, default=D(1))
    p.add_argument("--round", type=float, default=D(1.5), dest="rounding")
    p.add_argument("--max-size", type=int, default=D(800))
    p.add_argument("--max-triangles", type=int, default=D(20_000_000))
    p.add_argument("--crop", type=int, nargs=4, metavar=("X0", "Y0", "X1", "Y1"), default=D(None))
    p.add_argument("--invert", action="store_true", default=D(False))
    p.add_argument("--threshold", type=float, default=D(None))
    p.add_argument("--flatten", choices=["auto", "on", "off"], default=D("auto"))
    p.add_argument("--pierce", action="store_true", default=D(False))
    p.add_argument("--opening", type=int, default=D(14))
    p.add_argument("--outside-edges", default=D("tlrb"))
    p.add_argument("--keep-labels", action="store_true", default=D(False))
    p.add_argument("--mask-preview", action="store_true", default=D(False))
    p.add_argument("--preview", action="store_true", default=D(False))
    p.add_argument("--fill", type=int, nargs="+", default=D([]))
    p.add_argument("--min-opening", type=int, default=D(1200))
    p.add_argument("--edge", choices=["chamfer", "round", "hollow", "ogee", "none"],
                   default=D("chamfer"))
    p.add_argument("--edge-width", type=float, default=D(1.5))
    p.add_argument("--edge-depth", type=float, default=D(None))
    p.add_argument("--both-sides", action="store_true", default=D(False))


def model_options(tokens, typed):
    """Settings-file words -> options, then the command-line options on top."""
    p = _Parser(prog="sketch2stl", add_help=False)
    add_model_options(p)
    a = p.parse_args(tokens)
    for k, v in typed.items():
        setattr(a, k, v)
    return a


# ------------------------------------------------------------- folders ----
def natural_key(name):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", name)]


def pictures_in(folder):
    names = []
    for f in os.listdir(folder):
        stem, ext = os.path.splitext(f)
        if (ext.lower() in IMAGE_EXT and os.path.isfile(os.path.join(folder, f))
                and not stem.endswith(("_mask", "_preview"))):
            names.append(f)
    return sorted(names, key=natural_key)


def read_settings(folder):
    """-> (path, exists, ALL words, {picture name: [(line number, words), ...]}, problems)"""
    path = os.path.join(folder, SETTINGS_NAME)
    all_words, per, problems = [], {}, []
    if not os.path.isfile(path):
        return path, False, all_words, per, problems
    with open(path, encoding="utf-8") as f:
        for n, raw in enumerate(f, 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if ":" not in line:
                problems.append(f"{SETTINGS_NAME} line {n}: start the line with the "
                                f"picture name and a colon, e.g.   1.png: --pierce")
                continue
            name, rest = line.split(":", 1)
            try:
                words = shlex.split(rest, comments=True)
            except ValueError as e:
                problems.append(f"{SETTINGS_NAME} line {n}: {e}")
                continue
            if name.strip().upper() == "ALL":
                all_words += words
            else:
                per.setdefault(name.strip().lower(), []).append((n, words))
    return path, True, all_words, per, problems


def make_settings(folder, pics):
    """Write sketch2stl_settings.txt, or add lines for pictures not in it yet."""
    path, exists, _, per, _ = read_settings(folder)
    new = [p for p in pics if p.lower() not in per]
    if exists and not new:
        print(f"{path}: already lists every picture - nothing to add")
        return
    width = max(len(p) for p in pics) + 2
    lines = []
    if not exists:
        lines += [
            "# sketch2stl settings for the pictures in this folder",
            "#",
            "# One line per model:   picture-name:  options",
            "#   - the options are the same ones you would type after the picture name",
            "#     on the command line  (python3 sketch2stl.py --help  lists them all)",
            "#   - leave the options empty to use the standard settings",
            "#   - write  skip  instead of options to leave a picture out",
            "#   - to get several models from one picture, list it on several lines,",
            "#     each with its own --crop and its own  -o name.stl",
            "#   - anything after a # is a note and is ignored",
            "#",
            "# ALL: options used for every picture (a picture's own line can change them)",
            "ALL:",
            "",
        ]
    for p in new:
        note = ""
        try:
            im = Image.open(os.path.join(folder, p))
            note = f"# {im.size[0]} x {im.size[1]} pixels"
        except Exception:
            note = "# (could not open this picture)"
        lines.append(f"{(p + ':').ljust(width)}{'':24}{note}")
    with open(path, "a" if exists else "w", encoding="utf-8") as f:
        if exists:
            f.write("\n")
        f.write("\n".join(lines) + "\n")
    print(f"{'added ' + str(len(new)) + ' pictures to' if exists else 'wrote'} {path}")
    print("open it in a text editor, put the options after each picture name, "
          "save, and run the folder again")


def write_summary(out_dir, rows):
    path = os.path.join(out_dir, SUMMARY_NAME)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"sketch2stl run {time.strftime('%Y-%m-%d %H:%M')}\n\n")
        for r in rows:
            f.write(r["text"] + "\n")
            for t in r.get("notes", []):
                f.write(f"      {t}\n")
    return path


# ---------------------------------------------------------------- main ----
def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("inputs", nargs="+", metavar="picture-or-folder")
    p.add_argument("--out-dir")
    p.add_argument("--only", nargs="+", default=[])
    p.add_argument("--make-settings", action="store_true")
    add_model_options(p, suppress=True)
    a = p.parse_args()
    typed = {k: v for k, v in vars(a).items()
             if k not in ("inputs", "out_dir", "only", "make_settings")}

    jobs, problems, skipped = [], [], []
    only = {n.lower() for n in a.only}
    for inp in a.inputs:
        if os.path.isdir(inp):
            pics = pictures_in(inp)
            if not pics:
                problems.append(f"{inp}: no pictures found in this folder")
                continue
            if a.make_settings:
                make_settings(inp, pics)
                continue
            spath, exists, all_words, per, bad = read_settings(inp)
            problems += [f"{inp}/{b}" for b in bad]
            if exists:
                print(f"using settings from {spath}")
                for name in per:
                    if name not in {x.lower() for x in pics}:
                        problems.append(f"{spath}: '{name}' is not a picture in this folder")
            out_dir = a.out_dir or os.path.join(inp, "stl")
            for pic in pics:
                if only and pic.lower() not in only:
                    continue
                lines = per.get(pic.lower()) or [(None, [])]
                stem = os.path.splitext(pic)[0]
                for k, (lineno, words) in enumerate(lines):
                    where = f"{SETTINGS_NAME} line {lineno}" if lineno else "command line"
                    if [w.lower() for w in words] == ["skip"]:
                        skipped.append(f"{pic}  (skip, {where})")
                        continue
                    try:
                        opts = model_options(all_words + words, typed)
                    except ValueError as e:
                        problems.append(f"{pic}, {where}: {e}")
                        continue
                    name = opts.out or (stem + (f"_{k + 1}" if len(lines) > 1 else "") + ".stl")
                    out = name if os.path.isabs(name) else os.path.join(out_dir, name)
                    label = pic + (f" (line {lineno})" if len(lines) > 1 else "")
                    jobs.append({"img": os.path.join(inp, pic), "opts": opts, "out": out,
                                 "label": label, "out_dir": out_dir})
        elif os.path.isfile(inp):
            if a.make_settings:
                problems.append(f"{inp}: --make-settings needs a folder, not a picture")
                continue
            opts = model_options([], typed)
            stem = os.path.splitext(os.path.basename(inp))[0]
            if opts.out:
                out = opts.out
            elif a.out_dir:
                out = os.path.join(a.out_dir, stem + ".stl")
            else:
                out = os.path.splitext(inp)[0] + ".stl"
            jobs.append({"img": inp, "opts": opts, "out": out,
                         "label": os.path.basename(inp), "out_dir": a.out_dir})
        else:
            problems.append(f"{inp}: no such picture or folder")

    if "out" in typed and len(jobs) > 1:
        problems.append("-o names one file, but this run makes several models - "
                        "use --out-dir to choose a folder instead")
    outs = {}
    for j in ([] if "out" in typed else jobs):
        outs.setdefault(os.path.abspath(j["out"]), []).append(j["label"])
    for o, labels in outs.items():
        if len(labels) > 1:
            problems.append(f"{', '.join(labels)} would all be saved as {o} - "
                            f"give each its own  -o name.stl")
    if a.make_settings:
        for pr in problems:
            print(f"problem: {pr}")
        return
    if problems:
        print("Nothing made yet - please fix these first:")
        for pr in problems:
            print(f"  - {pr}")
        sys.exit(1)
    if not jobs:
        print("Nothing to make.")
        return

    rows, t_all = [], time.time()
    for i, j in enumerate(jobs, 1):
        print(f"\n[{i}/{len(jobs)}] {j['label']}  ->  {j['out']}")
        d = os.path.dirname(j["out"])
        if d:
            os.makedirs(d, exist_ok=True)
        t0 = time.time()
        try:
            r = make_model(j["img"], j["opts"], j["out"])
            secs = time.time() - t0
            sx, sy, sz = r["span"]
            mode = "pierced" if j["opts"].pierce else "relief"
            rows.append({"out_dir": j["out_dir"], "notes": r["notes"], "ok": True,
                         "text": f"OK      {j['label']:<22} {mode:<8} {r['tris']:>11,} tri "
                                 f"{sx:6.0f} x {sy:4.0f} x {sz:4.1f} mm {r['mb']:8.1f} MB "
                                 f"{secs:6.0f} s  -> {os.path.basename(j['out'])}"})
        except KeyboardInterrupt:
            print("\nstopped (Ctrl+C) - the models finished so far are kept")
            rows.append({"out_dir": j["out_dir"], "ok": False,
                         "text": f"STOPPED {j['label']}"})
            break
        except MemoryError:
            print("FAILED: ran out of memory - try a smaller --max-size")
            rows.append({"out_dir": j["out_dir"], "ok": False,
                         "text": f"FAILED  {j['label']:<22} ran out of memory - "
                                 f"try a smaller --max-size"})
        except Exception as e:
            print(f"FAILED: {type(e).__name__}: {e}")
            rows.append({"out_dir": j["out_dir"], "ok": False,
                         "text": f"FAILED  {j['label']:<22} {type(e).__name__}: {e}"})

    if len(jobs) > 1 or skipped:
        rows += [{"out_dir": None, "ok": True, "text": f"SKIPPED {s}"} for s in skipped]
        good = sum(r["ok"] for r in rows if not r["text"].startswith("SKIPPED"))
        print(f"\n===== {good} of {len(jobs)} models made in "
              f"{(time.time() - t_all) / 60:.1f} min =====")
        for r in rows:
            print(r["text"])
            for t in r.get("notes", []):
                print(f"      {t}")
        for od in {j["out_dir"] for j in jobs if j["out_dir"]}:
            mine = [r for r in rows if r["out_dir"] in (od, None)]
            if os.path.isdir(od):
                print(f"summary saved: {write_summary(od, mine)}")
    if any(not r["ok"] for r in rows):
        sys.exit(1)


if __name__ == "__main__":
    main()
