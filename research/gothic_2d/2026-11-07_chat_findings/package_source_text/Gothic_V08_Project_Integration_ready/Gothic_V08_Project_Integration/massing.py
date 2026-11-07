#!/usr/bin/env python3
"""
massing.py - build a 3D massing model, a floor plan and a preview from a
             short text description of a building's blocks.

A single perspective sketch does not hold enough information for a program
to recover the plan behind it, so you read the sketch and write down the
blocks; this script does the rest.

Usage:
    python3 massing.py building.txt
    python3 massing.py building.txt -o laach.stl --preview

Outputs:  laach.stl   laach_plan.svg   laach_plan.png   laach_preview.png

The description file - one block per line, "kind key=value ...":

    # Laach abbey, west front (Ungewitter fig. 1346).  Units: metres.
    box      name=westblock  cx=0   cy=0  w=36 d=12 z0=0  z1=18
    gable    name=westroof   cx=0   cy=0  w=36 d=12 z0=18 z1=25 ridge=x
    box      name=tower      cx=0   cy=0  w=11 d=11 z0=18 z1=38
    helm     name=towerroof  cx=0   cy=0  w=11 d=11 z0=38 z1=52
    cylinder name=stair_n    cx=-19 cy=0  r=3         z0=0  z1=30
    cone     name=stair_n_rf cx=-19 cy=0  r=3         z0=30 z1=37

Kinds and their keys  (cx, cy = centre of the block; z0 = bottom, z1 = top,
or give h = height instead of z1; every key has a default except cx, cy, z1/h):
    box        w d              rectangular block
    prism      w d sides=8      N-sided tower (octagon by default); r instead of w d
    cylinder   r                round tower
    pyramid    w d sides=4      pointed roof: 4 = square pyramid, 8 = octagonal spire
    cone       r                conical roof
    gable      w d ridge=x|y    pitched roof with gables at the ends; ridge=x
                                runs the ridge along the width w
    hip        w d ridge=x|y ridgelen=L   hipped roof; ridgelen 0 = pyramid
    helm       w d peak=0.5     Rhenish helm (rhombic roof): four gables with
                                their peaks at `peak` of the roof height
    rot=DEG    on any block: turn it about its centre

Plan outputs show every block's outline and roof edges seen from above.

Needs: numpy, pillow   (sudo apt install python3-numpy python3-pil)
"""
import argparse, math, struct
import numpy as np
from PIL import Image, ImageDraw


# ---------------------------------------------------------- shapes -------
def ngon(cx, cy, r, n, z, rot=0.0):
    a = np.arange(n) * 2 * np.pi / n + np.radians(rot) + (np.pi / n if n % 2 == 0 else 0)
    return np.column_stack([cx + r * np.cos(a), cy + r * np.sin(a), np.full(n, z)])


def rect(cx, cy, w, d, z, rot=0.0):
    c = np.array([[-w / 2, -d / 2], [w / 2, -d / 2], [w / 2, d / 2], [-w / 2, d / 2]])
    return np.column_stack([rotate_xy(c, rot) + (cx, cy), np.full(4, z)])


def rotate_xy(pts, deg):
    t = np.radians(deg)
    R = np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])
    return pts @ R.T


def fan(idx, reverse=False):
    """Triangulate a convex polygon given its vertex indices."""
    idx = list(idx)
    tris = [(idx[0], idx[i], idx[i + 1]) for i in range(1, len(idx) - 1)]
    return [(a, c, b) for a, b, c in tris] if reverse else tris


def extrude(base_bottom, base_top):
    """Two matching rings of vertices (counter-clockwise seen from above)."""
    n = len(base_bottom)
    V = np.vstack([base_bottom, base_top])
    F = fan(range(n), reverse=True)                    # bottom faces down
    F += fan(range(n, 2 * n))                          # top faces up
    for i in range(n):
        j = (i + 1) % n
        F += [(i, j, n + j), (i, n + j, n + i)]        # outward walls
    return V, np.array(F)


def point_roof(base, apex):
    n = len(base)
    V = np.vstack([base, [apex]])
    F = fan(range(n), reverse=True)
    F += [(i, (i + 1) % n, n) for i in range(n)]
    return V, np.array(F)


def gable_roof(cx, cy, w, d, z0, z1, ridge, rot):
    if ridge == "y":                                   # ridge along the depth
        w, d, rot = d, w, rot + 90
    b = rect(cx, cy, w, d, z0, rot)                    # 0..3 eave corners
    ends = np.column_stack([rotate_xy(np.array([[-w / 2, 0], [w / 2, 0]]), rot) + (cx, cy), [z1, z1]])
    V = np.vstack([b, ends])                           # 4 = west ridge end, 5 = east
    F = [(0, 2, 1), (0, 3, 2),                         # bottom
         (0, 1, 5), (0, 5, 4),                         # south slope
         (2, 3, 4), (2, 4, 5),                         # north slope
         (1, 2, 5), (3, 0, 4)]                         # gable ends
    return V, np.array(F)


def hip_roof(cx, cy, w, d, z0, z1, ridge, ridgelen, rot):
    if ridge == "y":
        w, d, rot = d, w, rot + 90
    L = min(max(ridgelen, 0.0), w)
    b = rect(cx, cy, w, d, z0, rot)
    ends = np.column_stack([rotate_xy(np.array([[-L / 2, 0], [L / 2, 0]]), rot) + (cx, cy), [z1, z1]])
    V = np.vstack([b, ends])
    F = [(0, 2, 1), (0, 3, 2), (0, 1, 5), (0, 5, 4), (2, 3, 4), (2, 4, 5),
         (1, 2, 5), (3, 0, 4)]                         # hips are triangles now
    return V, np.array(F)


def helm_roof(cx, cy, w, d, z0, z1, peak, rot):
    b = rect(cx, cy, w, d, z0, rot)                    # corners 0..3
    zp = z0 + peak * (z1 - z0)
    mids = np.column_stack([rotate_xy(np.array([[0, -d / 2], [w / 2, 0], [0, d / 2], [-w / 2, 0]]), rot)
                            + (cx, cy), np.full(4, zp)])   # gable peaks 4..7
    V = np.vstack([b, mids, [[cx, cy, z1]]])           # apex = 8
    F = [(0, 2, 1), (0, 3, 2)]                         # bottom
    for i in range(4):
        j = (i + 1) % 4
        F += [(i, j, 4 + i)]                           # gable over side i: corners i, j, peak i
        F += [(j, 8, 4 + i), (j, 4 + j, 8)]            # rhombus at corner j, up to the apex
    return V, np.array(F)


def build(kind, k):
    cx, cy = float(k["cx"]), float(k["cy"])
    z0 = float(k.get("z0", 0))
    z1 = float(k["z1"]) if "z1" in k else z0 + float(k["h"])
    rot = float(k.get("rot", 0))
    if kind == "box":
        return extrude(rect(cx, cy, float(k["w"]), float(k["d"]), z0, rot),
                       rect(cx, cy, float(k["w"]), float(k["d"]), z1, rot))
    if kind in ("prism", "cylinder"):
        n = 48 if kind == "cylinder" else int(k.get("sides", 8))
        r = float(k["r"]) if "r" in k else float(k["w"]) / 2 / math.cos(math.pi / n)
        return extrude(ngon(cx, cy, r, n, z0, rot), ngon(cx, cy, r, n, z1, rot))
    if kind in ("pyramid", "cone"):
        n = 48 if kind == "cone" else int(k.get("sides", 4))
        if n == 4 and "w" in k:
            base = rect(cx, cy, float(k["w"]), float(k.get("d", k["w"])), z0, rot)
        else:
            r = float(k["r"]) if "r" in k else float(k["w"]) / 2 / math.cos(math.pi / n)
            base = ngon(cx, cy, r, n, z0, rot)
        return point_roof(base, (cx, cy, z1))
    if kind == "gable":
        return gable_roof(cx, cy, float(k["w"]), float(k["d"]), z0, z1, k.get("ridge", "x"), rot)
    if kind == "hip":
        return hip_roof(cx, cy, float(k["w"]), float(k["d"]), z0, z1, k.get("ridge", "x"),
                        float(k.get("ridgelen", 0)), rot)
    if kind == "helm":
        return helm_roof(cx, cy, float(k["w"]), float(k["d"]), z0, z1, float(k.get("peak", 0.5)), rot)
    raise ValueError(f"unknown block kind '{kind}'")


def read_description(path):
    blocks = []
    for ln, line in enumerate(open(path), 1):
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        kind, kv = parts[0].lower(), {}
        for p in parts[1:]:
            if "=" not in p:
                raise SystemExit(f"line {ln}: expected key=value, got '{p}'")
            key, val = p.split("=", 1)
            kv[key.lower()] = val
        try:
            V, F = build(kind, kv)
        except KeyError as e:
            raise SystemExit(f"line {ln}: block '{kind}' needs {e}")
        blocks.append((kv.get("name", f"{kind}{ln}"), V, F))
    return blocks


# ---------------------------------------------------------- outputs ------
def write_stl(blocks, path):
    T = np.concatenate([V[F] for _, V, F in blocks]).astype(np.float32)
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
    n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
    rec = np.zeros(len(T), dtype=[("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
    rec["n"], rec["v"] = n, T
    with open(path, "wb") as f:
        f.write(b"massing".ljust(80, b" "))
        f.write(struct.pack("<I", len(T)))
        rec.tofile(f)
    return len(T)


def plan_edges(blocks, min_angle=12.0):
    """Edges where the surface actually bends (by more than min_angle degrees),
    seen from above, as (x0, y0, x1, y1).  Vertical edges and the seams
    between the flat facets of a cylinder or cone are left out."""
    segs = set()
    for _, V, F in blocks:
        n = np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]])
        n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
        owner = {}
        for fi, tri in enumerate(F):
            for a, b in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
                owner.setdefault((min(a, b), max(a, b)), []).append(fi)
        for (a, b), faces in owner.items():
            if len(faces) == 2:
                cosang = float(np.clip(n[faces[0]] @ n[faces[1]], -1, 1))
                if np.degrees(np.arccos(cosang)) < min_angle:
                    continue
            p, q = V[a], V[b]
            if np.allclose(p[:2], q[:2], atol=1e-6):
                continue
            key = tuple(sorted([tuple(np.round(p[:2], 4)), tuple(np.round(q[:2], 4))]))
            segs.add(key)
    return [(a[0], a[1], b[0], b[1]) for a, b in segs]


def plan_bounds(blocks, margin=0.05):
    allv = np.concatenate([V for _, V, _ in blocks])
    lo, hi = allv[:, :2].min(0), allv[:, :2].max(0)
    m = margin * (hi - lo).max()
    return lo - m, hi + m


def save_plan_svg(blocks, path):
    lo, hi = plan_bounds(blocks)
    w, h = hi - lo
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.3f} {h:.3f}" width="{w:.3f}" height="{h:.3f}">',
           f'<g fill="none" stroke="black" stroke-width="{0.004 * max(w, h):.4f}" stroke-linecap="round">']
    for x0, y0, x1, y1 in plan_edges(blocks):          # y up in the world -> y down on the page
        out.append(f'<line x1="{x0 - lo[0]:.3f}" y1="{hi[1] - y0:.3f}" x2="{x1 - lo[0]:.3f}" y2="{hi[1] - y1:.3f}"/>')
    out.append("</g></svg>")
    open(path, "w").write("\n".join(out))


def save_plan_png(blocks, path, size=1200):
    lo, hi = plan_bounds(blocks)
    w, h = hi - lo
    s = size / max(w, h)
    im = Image.new("RGB", (int(w * s) + 1, int(h * s) + 1), "white")
    d = ImageDraw.Draw(im)
    P = lambda x, y: ((x - lo[0]) * s, (hi[1] - y) * s)
    # footprints of the ground-level blocks, lightly filled
    for _, V, F in blocks:
        if V[:, 2].min() <= 1e-6:
            ring = V[np.isclose(V[:, 2], V[:, 2].min())]
            if len(ring) >= 3:
                hull = convex_hull(ring[:, :2])
                d.polygon([P(x, y) for x, y in hull], fill=(225, 222, 212))
    for x0, y0, x1, y1 in plan_edges(blocks):
        d.line([P(x0, y0), P(x1, y1)], fill="black", width=max(1, int(size / 400)))
    im.save(path)


def convex_hull(pts):
    pts = sorted(map(tuple, pts))
    if len(pts) <= 2:
        return pts
    cross = lambda o, a, b: (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def render(blocks, path, size=1100, azim=35, elev=28):
    """Flat-shaded orthographic view with a depth buffer."""
    V = np.concatenate([V for _, V, _ in blocks])
    F = np.concatenate([F + off for off, (_, Vb, F) in zip(np.cumsum([0] + [len(Vb) for _, Vb, _ in blocks[:-1]]), blocks)])
    az, el = np.radians(azim), np.radians(elev)
    # camera axes: right, up, toward viewer
    right = np.array([np.cos(az), np.sin(az), 0.0])
    toward = np.array([np.sin(az) * np.cos(el), -np.cos(az) * np.cos(el), np.sin(el)])
    up = np.cross(toward, right)
    sx, sy, sz = V @ right, V @ up, V @ toward
    lo, hi = np.array([sx.min(), sy.min()]), np.array([sx.max(), sy.max()])
    m = 0.05 * (hi - lo).max()
    lo, hi = lo - m, hi + m
    scale = size / (hi - lo).max()
    W, H = int((hi[0] - lo[0]) * scale) + 1, int((hi[1] - lo[1]) * scale) + 1
    px = (sx - lo[0]) * scale
    py = (hi[1] - sy) * scale
    img = np.full((H, W, 3), [0.96, 0.95, 0.92], np.float32)
    zbuf = np.full((H, W), -np.inf)
    light = np.array([-0.4, -0.5, 0.75]); light /= np.linalg.norm(light)
    base = np.array([0.86, 0.82, 0.72])
    tri_n = np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]])
    tri_n /= np.maximum(np.linalg.norm(tri_n, axis=1, keepdims=True), 1e-12)
    for tri, nrm in zip(F, tri_n):
        if nrm @ toward <= 0:
            continue                                   # facing away
        shade = 0.35 + 0.65 * max(0.0, float(nrm @ light))
        if abs(nrm[2]) > 0.95:
            shade = 0.9 if nrm[2] > 0 else 0.3
        col = base * shade
        xs, ys, zs = px[tri], py[tri], sz[tri]
        x0, x1 = int(max(0, np.floor(xs.min()))), int(min(W - 1, np.ceil(xs.max())))
        y0, y1 = int(max(0, np.floor(ys.min()))), int(min(H - 1, np.ceil(ys.max())))
        if x1 < x0 or y1 < y0:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        det = (xs[1] - xs[0]) * (ys[2] - ys[0]) - (xs[2] - xs[0]) * (ys[1] - ys[0])
        if abs(det) < 1e-9:
            continue
        l1 = ((gx - xs[0]) * (ys[2] - ys[0]) - (gy - ys[0]) * (xs[2] - xs[0])) / det
        l2 = ((gy - ys[0]) * (xs[1] - xs[0]) - (gx - xs[0]) * (ys[1] - ys[0])) / det
        l0 = 1 - l1 - l2
        inside = (l0 >= -1e-6) & (l1 >= -1e-6) & (l2 >= -1e-6)
        depth = l0 * zs[0] + l1 * zs[1] + l2 * zs[2]
        zb = zbuf[y0:y1 + 1, x0:x1 + 1]
        win = inside & (depth > zb)
        zb[win] = depth[win]
        blk = img[y0:y1 + 1, x0:x1 + 1]
        blk[win] = col
    # ground shadow line: nothing fancy, just save
    Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).save(path)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("description")
    p.add_argument("-o", "--out")
    p.add_argument("--preview", action="store_true")
    p.add_argument("--azimuth", type=float, default=35, help="preview: turn the view (degrees)")
    p.add_argument("--elevation", type=float, default=28, help="preview: look down this steeply")
    a = p.parse_args()
    blocks = read_description(a.description)
    out = a.out or a.description.rsplit(".", 1)[0] + ".stl"
    stem = out.rsplit(".", 1)[0]
    n = write_stl(blocks, out)
    allv = np.concatenate([V for _, V, _ in blocks])
    span = allv.max(0) - allv.min(0)
    print(f"{len(blocks)} blocks: " + ", ".join(b[0] for b in blocks))
    print(f"wrote {out}: {n} triangles, {span[0]:.1f} x {span[1]:.1f} x {span[2]:.1f} units")
    save_plan_svg(blocks, stem + "_plan.svg")
    save_plan_png(blocks, stem + "_plan.png")
    print(f"plan: {stem}_plan.svg, {stem}_plan.png")
    if a.preview:
        render(blocks, stem + "_preview.png", azim=a.azimuth, elev=a.elevation)
        print(f"preview: {stem}_preview.png")


if __name__ == "__main__":
    main()
