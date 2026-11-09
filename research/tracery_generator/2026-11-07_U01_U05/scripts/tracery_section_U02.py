#!/usr/bin/env python3
"""tracery_section_U02.py -- EXPERIMENTAL depth + small-detail layer for the U01 generator.

U01 topology (outline, members, openings, persistent IDs) is reused unchanged. U02 adds:
  * ORDERS: every stone member belongs to an order (frame = 0, sub-arches/oculus = 1,
    nested lights/cusps = 2, ...). Each order has its own section depth, symmetric about one
    glazing plane, so subordinate members step back from principal ones on both faces.
  * PROFILES: a moulding section per order, written from the opening arris onto the face as
    elements  fillet | chamfer | roll | hollow | ogee | groove.  The face height is a function of
    distance to the nearest opening (mitred offsets), so mouldings intersect on mitre lines at
    junctions and run down the centre of cusps automatically.
Each order is meshed as a height field over its 2D region (constrained triangulation through the
profile iso-lines; no Steiner points), mirrored to the back and closed with vertical walls.
All profiles and depths are TRIAL values unless a spec cites a measured section.
"""
from __future__ import annotations

import math

import numpy as np
import shapely
from scipy.spatial import cKDTree
import triangle as tri_lib
import trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union

import tracery_universal_U01 as T

VERSION = "U02-experimental"
SHAPES = {"chamfer": lambda s: s,
          "roll": lambda s: math.sqrt(max(0.0, 1 - (1 - s) ** 2)),      # convex quarter round
          "hollow": lambda s: 1 - math.sqrt(max(0.0, 1 - s * s)),       # concave cavetto
          "ogee": lambda s: 0.5 * (1 - math.cos(math.pi * s))}          # S-curve
DEPTH_PALETTE = ["#5b2c83", "#3f3fa3", "#2e6fbf", "#1fa3b8", "#d4b106", "#e0702a"]  # 2D depth-study order


def profile_polyline(elems, L, nseg=6):
    """(distance from arris, drop below the order's face plane) breakpoints."""
    total = sum(L(e[2]) for e in elems if e[0] in SHAPES)
    d, drop, pts = 0.0, total, [(0.0, total)]
    for e in elems:
        t, w = e[0], L(e[1])
        if w <= 0:
            raise ValueError("profile element width must be > 0")
        if t == "fillet":
            d += w
            pts.append((d, drop))
        elif t == "groove":
            pts += [(d + w / 2, drop + L(e[2])), (d + w, drop)]
            d += w
        elif t in SHAPES:
            rise, n = L(e[2]), (1 if t == "chamfer" else nseg)
            for i in range(1, n + 1):
                pts.append((d + w * i / n, drop - rise * SHAPES[t](i / n)))
            d, drop = d + w, drop - rise
        else:
            raise ValueError(f"unknown profile element {t}")
    P = np.array(pts)
    P[-1, 1] = max(P[-1, 1], 0.0) if abs(P[-1, 1]) < 1e-12 else P[-1, 1]
    return P


def member_order(m):
    if m["kind"] == "frame":
        return 0
    dots = m["name"].count(".")
    if m["kind"] in ("mullion", "intersecting_arc"):
        return dots
    return dots - 1 + (1 if m["kind"] == "foil_cusps" else 0)


def _clean(p, tol):
    rings = [T.clean_ring(np.asarray(r.coords)[:-1], 0.25 * tol) for r in [p.exterior, *p.interiors]]
    q = Polygon(rings[0], [r for r in rings[1:] if len(r) >= 3])
    return q if q.is_valid and abs(q.area - p.area) <= 1e-4 * p.area else p


def partition(model):
    """Split the U01 stone into order regions (lowest order wins overlaps); leftovers and
    slivers join the neighbour they share most boundary with."""
    S, tol = model.stone, model.tol
    min_area = max((10 * tol) ** 2, 1e-7 * model.outline.area)
    if model.mode == "plate" or not model.members:
        return {0: T.polys(S)}
    by = {}
    for m in model.members:
        by.setdefault(member_order(m), []).append(m["poly"])
    pieces, taken = [], Polygon()
    for k in sorted(by):
        R = unary_union(by[k]).intersection(S).difference(taken)
        taken = unary_union([taken, R])
        pieces += [[k, p] for p in T.polys(R)]
    loose = [p for p in T.polys(S.difference(taken))]
    keep = []
    for k, p in pieces:
        (keep if p.area >= min_area else loose).append([k, p] if p.area >= min_area else p)
    eps = 2 * tol
    for q in sorted(loose, key=lambda g: -g.area):
        if q.area <= 1e-12:
            continue
        best = max(range(len(keep)), key=lambda i: keep[i][1].intersection(q.buffer(eps)).area)
        keep[best][1] = unary_union([keep[best][1], q])
    regions, dropped = {}, 0.0
    for k, p in keep:
        regions.setdefault(k, []).append(p)
    delta = 0.02 * tol
    for k in regions:  # edge-adjacent pieces of one order become one stone; point contacts stay separate stones
        Uk = unary_union(regions[k]).buffer(0)
        # hairline slivers (< 2*delta wide, e.g. where a foil lobe is tangent to its ring) are not stone
        Ok = Uk.buffer(-delta, join_style="mitre", mitre_limit=2.0).buffer(delta, join_style="mitre", mitre_limit=2.0)
        Ok = Ok.intersection(Uk)  # opening never enlarges a stone into its neighbour
        gs = [_clean(g, tol) for g in T.polys(Ok) if g.area >= min_area]
        dropped += Uk.area - sum(g.area for g in gs)
        regions[k] = sorted(gs, key=lambda g: (-round(g.centroid.y / (1e-6 * model.size)), round(g.centroid.x / (1e-6 * model.size))))
    model.hairline_area = dropped
    return regions


def piece_mesh(P, voids_u, prof, H, zg, size, tol):
    """Closed solid over 2D region P: front z = zg + H - drop(d), back mirrored about zg."""
    ds, drops = prof[:, 0], prof[:, 1]
    q = max(1e-9 * size, 1e-3 * tol)  # merge noding near-duplicates (< tol/1000)
    key = lambda x, y: (round(x / q), round(y / q))
    # iso-lines are clipped strictly inside P, so they never node with or run along its boundary
    # (prevents T-junctions where an iso-line grazes a member edge)
    Pin = P.buffer(-0.05 * tol, join_style="mitre", mitre_limit=2.0)
    lines, level = list(shapely.get_parts(P.boundary)), {}
    for d in ds[1:]:
        iso = voids_u.buffer(d, join_style="mitre", mitre_limit=2.0).boundary.intersection(Pin)
        parts = [g for g in shapely.get_parts(shapely.line_merge(iso) if not iso.is_empty else iso)
                 if g.geom_type in ("LineString", "LinearRing") and g.length > 0]
        for g in parts:
            for x, y in g.coords:
                level[key(x, y)] = d
        lines += parts
    vid, V2, segs = {}, [], []
    for g in lines:
        c = np.asarray(g.coords)
        ids = []
        for x, y in c:
            k = key(x, y)
            if k not in vid:
                vid[k] = len(V2)
                V2.append((x, y))
            ids.append(vid[k])
        segs += [(a, b) for a, b in zip(ids[:-1], ids[1:]) if a != b]
    V2 = np.asarray(V2)
    # cluster noding near-duplicates (< tol/50, far above float32 resolution) onto one vertex
    rep = np.arange(len(V2))
    for i, j in sorted(cKDTree(V2).query_pairs(0.02 * tol)):
        ri, rj = rep[i], rep[j]
        while rep[ri] != ri:
            ri = rep[ri]
        while rep[rj] != rj:
            rj = rep[rj]
        if ri != rj:
            rep[max(ri, rj)] = min(ri, rj)
    for i in range(len(rep)):
        r = i
        while rep[r] != r:
            r = rep[r]
        rep[i] = r
    keep = np.unique(rep)
    remap = -np.ones(len(V2), np.int64)
    remap[keep] = np.arange(len(keep))
    newkey = {}
    for i in range(len(V2)):
        kk = key(*V2[i])
        if kk in level and key(*V2[rep[i]]) not in newkey:
            newkey[key(*V2[rep[i]])] = level[kk]
    level.update(newkey)
    segs = {tuple(sorted((int(remap[rep[a]]), int(remap[rep[b]])))) for a, b in segs}
    segs = [sg for sg in segs if sg[0] != sg[1]]
    V2 = V2[keep]
    inp = dict(vertices=V2, segments=np.asarray(segs, np.int64))
    if P.interiors:
        inp["holes"] = np.asarray([Polygon(r).representative_point().coords[0] for r in P.interiors])
    res = tri_lib.triangulate(inp, "pQ")
    Vt, F = np.asarray(res["vertices"]), np.asarray(res["triangles"], np.int64)
    steiner = len(Vt) - len(V2)
    dist = np.empty(len(Vt))
    known = np.array([level.get(key(x, y), np.nan) for x, y in Vt])
    unknown = np.isnan(known)
    dist[~unknown] = known[~unknown]
    if unknown.any():
        dist[unknown] = shapely.distance(shapely.points(Vt[unknown]), voids_u)
    h = H - np.interp(dist, ds, drops, right=0.0)
    a = Vt[F]
    s = (a[:, 1, 0] - a[:, 0, 0]) * (a[:, 2, 1] - a[:, 0, 1]) - (a[:, 1, 1] - a[:, 0, 1]) * (a[:, 2, 0] - a[:, 0, 0])
    F[s < 0] = F[s < 0][:, ::-1]
    n = len(Vt)
    V = np.r_[np.c_[Vt, zg + h], np.c_[Vt, zg - h]]
    e = np.r_[F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]]
    inner = {(int(x), int(y)) for x, y in e}
    bd = np.array([(x, y) for x, y in e if (int(y), int(x)) not in inner], np.int64)
    walls = np.r_[np.c_[bd[:, 0], bd[:, 0] + n, bd[:, 1]], np.c_[bd[:, 1], bd[:, 0] + n, bd[:, 1] + n]]
    faces = np.r_[F, F[:, ::-1] + n, walls]
    return V, faces, dict(steiner=int(steiner), min_half=float(h.min()), area2d=float(np.abs(s).sum() / 2),
                          area_err=float(abs(np.abs(s).sum() / 2 - P.area) / P.area), walls=len(bd),
                          ring_edges=int(sum(len(r.coords) - 1 for r in [P.exterior, *P.interiors])))


class Sectioned:
    """U01 model + order/profile section -> stepped, moulded stone pieces."""

    def __init__(self, spec, section, scale=1.0, model_cls=None):
        self.m = m = (model_cls or T.Model)(spec, scale)
        self.section, self.k = section, float(scale)
        L = lambda v: float(v) * self.k
        self.L = L
        self.orders = []
        for o in section["orders"]:
            self.orders.append(dict(H=L(o["depth"]) / 2, prof=profile_polyline(o["profile"], L), raw=o["profile"]))
        wl = spec.get("wall", {})
        self.recess = L(wl.get("recess", 0.0))
        self.zg = -self.recess - self.orders[0]["H"]
        self.checks = []
        self.regions = partition(m)
        self._build()

    def order_of(self, k):
        return self.orders[min(k, len(self.orders) - 1)]

    def check(self, name, ok, kind="geometric", detail=""):
        self.checks.append(dict(kind=kind, name=name, ok=bool(ok), detail=detail))

    def _build(self):
        m, L = self.m, self.L
        S = m.stone
        allp = [p for ps in self.regions.values() for p in ps]
        U = unary_union(allp)
        sd = U.symmetric_difference(S).area
        hl = abs(getattr(m, "hairline_area", 0.0))
        self.check(f"order regions tile the U01 stone (sym. diff {sd:.3g}; hairline slivers removed {hl:.3g})",
                   sd <= max(1e-9 * S.area, 2 * hl + 1e-9 * S.area) and hl <= 1e-5 * S.area)
        ov, thick = 0.0, 0.0
        for i in range(len(allp)):
            for j in range(i + 1, len(allp)):
                if allp[i].intersects(allp[j]):
                    I = allp[i].intersection(allp[j])
                    if I.area > 0:
                        ov += I.area
                        thick = max(thick, max(2 * g.area / g.length for g in T.polys(I)) if T.polys(I) else 0.0)
        self.check(f"stones do not interpenetrate: overlap {ov:.3g} total, max thickness {thick:.3g} "
                   f"(<= ring-cleanup tolerance {0.25 * m.tol:.3g})", thick <= 0.25 * m.tol)
        Hs = [o["H"] for o in self.orders]
        self.check("order depths step back monotonically", all(a >= b for a, b in zip(Hs, Hs[1:])), "architectural")
        voids_u = unary_union([v["poly"] for v in m.voids])
        self.parts, self.piece_info, self.piece_meta = [], {}, {}
        for k, ps in self.regions.items():
            touch = sum(1 for i in range(len(ps)) for j in range(i + 1, len(ps))
                        if ps[i].distance(ps[j]) <= m.eps and ps[i].intersection(ps[j]).length > m.tol)
            self.check(f"order {k}: separate stones share no edges ({touch})", touch == 0)
        for k in sorted(self.regions):
            o = self.order_of(k)
            maxdrop = float(o["prof"][:, 1].max())
            self.check(f"order {k}: deepest moulding {maxdrop:.4g} < half-depth {o['H']:.4g}", maxdrop < 0.95 * o["H"],
                       "architectural")
            meshes, holes, info = [], 0, []
            for j, P in enumerate(self.regions[k]):
                V, F, inf = piece_mesh(P, voids_u, o["prof"], o["H"], self.zg, m.size, m.tol)
                mesh = trimesh.Trimesh(V, F, process=False)
                meshes.append(mesh)
                holes += len(P.interiors)
                info.append(inf)
                nm = f"stone_o{k}_{j + 1:02d}"
                self.piece_meta[nm] = dict(order=k, holes=len(P.interiors), area=P.area, min_half=inf["min_half"])
                self.parts.append((nm, mesh, (0.80, 0.76, 0.68, 1.0), 0.85))
            aerr = max(i["area_err"] for i in info)
            bound = max(P.length * 0.02 * m.tol / P.area for P in self.regions[k]) + 1e-9  # vertex-merge radius
            self.check(f"order {k}: front triangulation covers its region (rel. err {aerr:.2g} <= merge bound {bound:.2g})",
                       aerr <= bound)
            self.piece_info[k] = dict(pieces=len(meshes), holes=holes, steiner=sum(i["steiner"] for i in info),
                                      min_half=min(i["min_half"] for i in info),
                                      face_width=round(float(o["prof"][-1, 0]), 6))
        # flat face left on each order after its profile (informative, architectural)
        self.flat = {}
        for k, ps in self.regions.items():
            w = float(self.order_of(k)["prof"][-1, 0])
            face = unary_union(ps).difference(voids_u.buffer(w, join_style="mitre", mitre_limit=2.0))
            self.flat[k] = round(face.area / max(unary_union(ps).area, 1e-12), 4)
        # wall (unchanged U01 rule) and glass at the glazing plane
        wl = m.spec.get("wall", {})
        if wl:
            mg = L(wl["margin"])
            b = m.outline.bounds
            frame = shapely.geometry.polygon.orient(shapely.box(b[0] - mg, b[1] - mg, b[2] + mg, b[3] + mg), 1.0)
            Rw, Ro = T.ring_of(frame, 1.0, m.eps), T.ring_of(m.outline, -1.0, m.eps)
            pt = m.outline.representative_point()
            Vw, Fw, _ = T.plate_mesh(Rw, [(Ro, Ro, 0.0, (pt.x, pt.y))], L(wl["depth"]), z0=0.0)
            self.parts.append(("wall", trimesh.Trimesh(Vw, Fw, process=False), (0.60, 0.57, 0.52, 1.0), 0.9))
            self.check("deepest order sits within the wall", self.recess + 2 * self.orders[0]["H"] <= L(wl["depth"]) + 1e-9,
                       "architectural")
        g = 0.03 * 2 * self.orders[0]["H"]
        panes = []
        for v in m.voids:
            Rg = T.ring_of(v["poly"].buffer(-1e-3 * g, join_style="mitre", mitre_limit=1.5), 1.0, m.eps)
            Vg, Fg, _ = T.plate_mesh(Rg, [], g, z0=self.zg + 0.5 * g)
            panes.append(trimesh.Trimesh(Vg, Fg, process=False))
        if panes:
            self.parts.append(("glass", trimesh.util.concatenate(panes), (0.10, 0.17, 0.25, 1.0), 0.15))

    def export_glb(self, path):
        sc = trimesh.Scene()
        for nm, mesh, rgba, rough in self.parts:
            mm = trimesh.Trimesh(mesh.vertices.copy(), mesh.faces.copy(), process=False)
            mm.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(
                name=f"{nm}_mat", baseColorFactor=list(rgba), metallicFactor=0.0, roughnessFactor=rough))
            sc.add_geometry(mm, node_name=f"{self.m.id}__{nm}", geom_name=f"{self.m.id}__{nm}")
        data = sc.export(file_type="glb", include_normals=False)
        open(path, "wb").write(data)
        return data
