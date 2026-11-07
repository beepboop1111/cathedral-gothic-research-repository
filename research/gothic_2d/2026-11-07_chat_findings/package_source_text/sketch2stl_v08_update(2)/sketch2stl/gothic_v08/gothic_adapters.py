"""Adapters between drawings / section PNGs and the V08 vector stonework.

Opt-in helpers; nothing here runs at import time and no original script is
modified.  Everything works in whatever units the caller passes in - scale is
only ever applied explicitly (see gothic_plate_reader.Calibration).

    profile_from_png      moulding-section PNG -> ordered CCW section polygon
    resample_polyline     even stations along a traced line
    rails_from_centerline centre line + width -> outer / inner rails (mitred)
    sweep_centerline      one call: centre line + section -> closed bar mesh
    prism_from_polygon    plan outline -> closed vertical prism (fast ear clip)
"""
from __future__ import annotations
import numpy as np
import trimesh
from PIL import Image
from scipy import ndimage as ndi

from gothic_stonework import sweep_between_rails, polygon_area


# --------------------------------------------------------------- profiles ---
def profile_from_png(path, threshold=0.5, invert=False, max_points=48):
    """Return the outline of the stone in a section drawing as an ordered,
    counter-clockwise Nx2 polygon in pixel units, X right and Y UP.

    The largest dark region is used (holes filled).  The outline is
    simplified until it has at most `max_points` vertices, because every
    vertex becomes a strip of faces along the whole sweep.
    """
    from skimage.measure import find_contours, approximate_polygon
    g = np.asarray(Image.open(path).convert('L'), np.float32) / 255.0
    solid = g < threshold
    if invert:
        solid = ~solid
    lab, n = ndi.label(solid)
    if not n:
        raise ValueError(f'{path}: no dark pixels below threshold {threshold}')
    sizes = ndi.sum(solid, lab, range(1, n + 1))
    solid = ndi.binary_fill_holes(lab == (np.argmax(sizes) + 1))
    c = max(find_contours(np.pad(solid, 1).astype(float), 0.5), key=len)
    H = solid.shape[0] + 2
    tol = 0.5
    while True:
        p = approximate_polygon(c, tolerance=tol)
        if len(p) - 1 <= max_points or tol > 50:
            break
        tol *= 1.4
    p = p[:-1] if np.allclose(p[0], p[-1]) else p
    xy = np.column_stack([p[:, 1], H - p[:, 0]])          # (row, col) -> (x, y up)
    if polygon_area(xy) < 0:
        xy = xy[::-1].copy()
    return xy


def rectangle_profile():
    return np.array([[0, 0], [1, 0], [1, 1], [0, 1]], float)


# ---------------------------------------------------------------- rails ----
def resample_polyline(points, step=None, n=None, closed=False):
    """Evenly spaced stations along an Nx2 polyline (by `step` length or
    `n` stations).  closed=True treats the line as a loop."""
    p = np.asarray(points, float)
    if closed and not np.allclose(p[0], p[-1]):
        p = np.vstack([p, p[:1]])
    seg = np.linalg.norm(np.diff(p, axis=0), axis=1)
    keep = np.concatenate([[True], seg > 1e-9])
    p = p[keep]
    seg = seg[seg > 1e-9]
    if len(p) < 2:
        raise ValueError('polyline has no length')
    s = np.concatenate([[0], np.cumsum(seg)])
    if n is None:
        n = max(3, int(np.ceil(s[-1] / step)) + 1) if step else 3
    t = np.linspace(0, s[-1], max(3, n))
    out = np.column_stack([np.interp(t, s, p[:, 0]), np.interp(t, s, p[:, 1])])
    return out[:-1] if closed else out


def rails_from_centerline(center, width, closed=False, max_mitre=2.5):
    """Offset a centre line by +/- width/2 into (outer, inner) rails.
    Corners are mitred (limited to max_mitre x the half width)."""
    c = np.asarray(center, float)
    if closed:
        prev, nxt = np.roll(c, 1, 0), np.roll(c, -1, 0)
    else:
        prev = np.vstack([2 * c[0] - c[1], c[:-1]])
        nxt = np.vstack([c[1:], 2 * c[-1] - c[-2]])

    def unit(v):
        return v / np.maximum(np.linalg.norm(v, axis=1, keepdims=True), 1e-12)
    t_in, t_out = unit(c - prev), unit(nxt - c)
    n_in = np.column_stack([-t_in[:, 1], t_in[:, 0]])
    n_out = np.column_stack([-t_out[:, 1], t_out[:, 0]])
    nrm = unit(n_in + n_out)
    cosh = np.clip(np.sum(nrm * n_in, axis=1), 1 / max_mitre, 1)
    off = nrm * (width / 2 / cosh)[:, None]
    return c + off, c - off


def sweep_centerline(center, width, height, profile=None, z0=0.0,
                     step=None, closed=False):
    """Centre line -> closed bar mesh with the given section, sitting on z0.
    Returns a trimesh.Trimesh (raises ValueError when the line is too short
    or bends too tightly for its width)."""
    prof = rectangle_profile() if profile is None else np.asarray(profile, float)
    st = resample_polyline(center, step=step or max(width / 2, 1e-6), closed=closed)
    if len(st) < 3:
        raise ValueError('too few stations')
    outer, inner = rails_from_centerline(st, width, closed=closed)
    mesh, _ = sweep_between_rails(outer, inner, prof, height, closed=closed)
    if z0:
        mesh.apply_translation([0, 0, z0])
    return mesh


# --------------------------------------------------------------- prisms ----
def ear_clip(poly):
    """Triangulate a simple CCW polygon.  Same idea as gothic_stonework's
    _ear_clip but with the point-in-triangle test vectorised, so outlines
    with a few hundred vertices take milliseconds rather than minutes."""
    p = np.asarray(poly, float)
    idx = list(range(len(p)))
    tris = []
    guard = 0
    while len(idx) > 3:
        guard += 1
        if guard > 4 * len(p) * len(p):
            raise ValueError('ear clipping did not finish (self-intersecting outline?)')
        m = len(idx)
        P = p[idx]
        prv, nxt = np.roll(P, 1, 0), np.roll(P, -1, 0)
        convex = ((P[:, 0] - prv[:, 0]) * (nxt[:, 1] - P[:, 1])
                  - (P[:, 1] - prv[:, 1]) * (nxt[:, 0] - P[:, 0])) > 1e-12
        found = False
        for k in np.nonzero(convex)[0]:
            a, b, c = prv[k], P[k], nxt[k]
            others = np.delete(P, [(k - 1) % m, k, (k + 1) % m], axis=0)
            if len(others):
                def side(u, v, q):
                    return (v[0] - u[0]) * (q[:, 1] - u[1]) - (v[1] - u[1]) * (q[:, 0] - u[0])
                inside = (side(a, b, others) >= -1e-12) & (side(b, c, others) >= -1e-12) \
                    & (side(c, a, others) >= -1e-12)
                if inside.any():
                    continue
            tris.append((idx[(k - 1) % m], idx[k], idx[(k + 1) % m]))
            idx.pop(k)
            found = True
            break
        if not found:
            raise ValueError('no ear found (self-intersecting outline?)')
    tris.append(tuple(idx))
    return np.asarray(tris, int)


def prism_from_polygon(poly_xy, z0, z1):
    """Closed vertical prism from a simple plan outline (Nx2, any winding)."""
    p = np.asarray(poly_xy, float)
    if np.allclose(p[0], p[-1]):
        p = p[:-1]
    keep = np.concatenate([[True], np.linalg.norm(np.diff(p, axis=0), axis=1) > 1e-9])
    p = p[keep]
    if len(p) < 3 or abs(polygon_area(p)) < 1e-12:
        raise ValueError('degenerate outline')
    if polygon_area(p) < 0:
        p = p[::-1].copy()
    tri = ear_clip(p)
    n = len(p)
    V = np.vstack([np.column_stack([p, np.full(n, z0)]), np.column_stack([p, np.full(n, z1)])])
    F = [tri[:, ::-1], tri + n]
    i = np.arange(n); j = (i + 1) % n
    F += [np.column_stack([i, j, j + n]), np.column_stack([i, j + n, i + n])]
    mesh = trimesh.Trimesh(V, np.vstack(F), process=False)
    if not (mesh.is_watertight and mesh.is_winding_consistent):
        raise ValueError('prism is not closed')
    return mesh
