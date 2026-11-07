#!/usr/bin/env python3
"""tracery_universal_U01.py -- EXPERIMENTAL universal Gothic tracery generator (U01).

Pipeline
  JSON spec -> analytic construction (every arc keeps its centre and radius)
            -> explicit members + junction graph
            -> stone/void topology with persistent opening IDs
            -> sectioned 3D solids (square or chamfered reveals) -> GLB + construction record

Modes
  plate : stone = outline - explicit voids (measured circles/arcs or parametric),
          e.g. Saint-Leu Fig. 80 plate tracery.
  bar   : stone = frame + union(members); openings = complement components
          (lights, foils, spandrels/eyes), e.g. Reims/Amiens bar tracery,
          recursive sub-windows, intersecting tracery.

Units are whatever the spec declares. Source-pixel specs are NOT calibrated architecture.
Mesh coordinates follow glTF: X right, Y up, Z toward the viewer (front face at Z = -recess).
"""
from __future__ import annotations

import hashlib
import math
from pathlib import Path

import triangle as tri_lib
import numpy as np
import shapely
import trimesh
from scipy.optimize import brentq
from shapely.geometry import Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

VERSION = "U01-experimental"
ROLE_ORDER = {"light": 0, "foil": 1, "oculus": 2, "spandrel": 3, "eye": 4}
ROLE_PREFIX = {"spandrel": "S", "eye": "E"}


# ----------------------------------------------------------------- primitives
class Circle:
    __slots__ = ("x", "z", "r")

    def __init__(self, x, z, r):
        self.x, self.z, self.r = float(x), float(z), float(r)

    def off(self, d):
        return Circle(self.x, self.z, self.r + d)

    def mirror(self, axis):
        return Circle(2 * axis - self.x, self.z, self.r)

    def dist(self, x, z):
        return math.hypot(x - self.x, z - self.z)

    def rec(self):
        return [round(self.x, 6), round(self.z, 6), round(self.r, 6)]


def _step(r, tol):
    return 2 * math.acos(max(-1.0, 1 - tol / r)) if tol < 2 * r else math.pi / 2


def arc_pts(c, p0, p1, tol):
    """Clockwise arc of circle c from p0 to p1; exact endpoints; sagitta <= tol."""
    a0 = math.atan2(p0[1] - c.z, p0[0] - c.x)
    a1 = math.atan2(p1[1] - c.z, p1[0] - c.x)
    while a1 > a0:
        a1 -= 2 * math.pi
    n = max(1, math.ceil((a0 - a1) / _step(c.r, tol)))
    t = np.linspace(a0, a1, n + 1)
    P = np.c_[c.x + c.r * np.cos(t), c.z + c.r * np.sin(t)]
    P[0], P[-1] = p0, p1
    return P


def circle_poly(c, tol):
    n = max(24, math.ceil(2 * math.pi / _step(c.r, tol)))
    t = np.linspace(0, 2 * math.pi, n, endpoint=False)
    return Polygon(np.c_[c.x + c.r * np.cos(t), c.z + c.r * np.sin(t)])


def dedupe(P, eps):
    P = np.asarray(P, float)
    keep = np.r_[True, np.linalg.norm(np.diff(P, axis=0), axis=1) > eps]
    P = P[keep]
    if len(P) > 2 and np.linalg.norm(P[0] - P[-1]) <= eps:
        P = P[:-1]
    return P


def clean_ring(P, min_edge, spike_deg=1.0):
    """Remove boolean-overlay artefacts: edges shorter than min_edge and needle spikes
    (vertex where the ring doubles back within spike_deg)."""
    P = dedupe(P, min_edge)
    for _ in range(20):
        if len(P) < 4:
            break
        v1, v2 = np.roll(P, 1, 0) - P, np.roll(P, -1, 0) - P
        cs = (v1 * v2).sum(1) / (np.linalg.norm(v1, axis=1) * np.linalg.norm(v2, axis=1))
        spike = cs > math.cos(math.radians(spike_deg))
        if not spike.any():
            break
        P = dedupe(P[~spike], min_edge)
    return P


def ring_defects(P, min_edge, spike_deg=1.0):
    e = np.linalg.norm(np.roll(P, -1, 0) - P, axis=1)
    v1, v2 = np.roll(P, 1, 0) - P, np.roll(P, -1, 0) - P
    cs = (v1 * v2).sum(1) / (np.linalg.norm(v1, axis=1) * np.linalg.norm(v2, axis=1))
    return int((e < min_edge).sum()), int((cs > math.cos(math.radians(spike_deg))).sum())


def polys(g):
    """All non-empty polygons in g, flattening nested multi-part geometries."""
    if g.is_empty:
        return []
    if isinstance(g, Polygon):
        return [g]
    return [p for part in getattr(g, "geoms", []) for p in polys(part)]


def ring_of(poly, sign, eps):
    """Exterior ring, oriented (sign +1 CCW, -1 CW), no closing point."""
    return dedupe(np.asarray(orient(poly, sign).exterior.coords)[:-1], eps)


class Arch:
    """Arch-headed opening. Jambs x = xl, x = xr. Left half = arc of CL (centre to its right),
    right half = arc of CR. Centres may sit below the springing (kinked impost, as drawn)."""

    def __init__(self, xl, xr, CL, CR):
        self.xl, self.xr, self.CL, self.CR = float(xl), float(xr), CL, CR
        self.sl = (self.xl, self._jz(CL, self.xl))
        self.sr = (self.xr, self._jz(CR, self.xr))
        self.apex = self._apex()

    @staticmethod
    def _jz(c, x):
        h = c.r ** 2 - (x - c.x) ** 2
        if h < 0:
            raise ValueError("arc does not reach its jamb")
        return c.z + math.sqrt(h)

    def _apex(self):
        a, b = self.CL, self.CR
        d = math.hypot(b.x - a.x, b.z - a.z)
        if d < 1e-12 * max(1.0, a.r):
            return (a.x, a.z + a.r)
        l = (a.r ** 2 - b.r ** 2 + d * d) / (2 * d)
        h2 = a.r ** 2 - l * l
        if h2 < 0:
            raise ValueError("arch halves do not meet")
        h = math.sqrt(h2)
        ux, uz = (b.x - a.x) / d, (b.z - a.z) / d
        mx, mz = a.x + l * ux, a.z + l * uz
        p1, p2 = (mx - h * uz, mz + h * ux), (mx + h * uz, mz - h * ux)
        return p1 if p1[1] >= p2[1] else p2

    @classmethod
    def pointed(cls, xl, xr, spring, f=1.0, drop=0.0):
        """Two-centred arch: radius = f * span; centres `drop` below springing
        (f = 0.5 round, f = 1 equilateral, f > 1 lancet, 0.5 < f < 1 drop arch)."""
        s, r = xr - xl, f * (xr - xl)
        if r * r - drop * drop < (s / 2) ** 2 - 1e-12 * s * s:
            raise ValueError("radius too small for span")
        a = math.sqrt(r * r - drop * drop)
        return cls(xl, xr, Circle(xl + a, spring - drop, r), Circle(xr - a, spring - drop, r))

    def off(self, d):
        """Concentric offset: + outward (extrados), - inward (intrados)."""
        return Arch(self.xl - d, self.xr + d, self.CL.off(d), self.CR.off(d))

    def ring(self, sill, tol):
        Lh = arc_pts(self.CL, self.sl, self.apex, tol)
        Rh = arc_pts(self.CR, self.apex, self.sr, tol)
        return np.r_[[[self.xl, sill]], Lh, Rh[1:], [[self.xr, sill]]]

    def polygon(self, sill, tol):
        eps = 1e-9 * max(1.0, self.xr - self.xl)
        return orient(Polygon(dedupe(self.ring(sill, tol), eps)), 1.0)

    def rec(self):
        r = lambda p: [round(p[0], 6), round(p[1], 6)]
        return dict(jambs=[round(self.xl, 6), round(self.xr, 6)], CL=self.CL.rec(), CR=self.CR.rec(),
                    spring_l=r(self.sl), spring_r=r(self.sr), apex=r(self.apex),
                    span=round(self.xr - self.xl, 6),
                    r_over_span=round(0.5 * (self.CL.r + self.CR.r) / (self.xr - self.xl), 6))


# ----------------------------------------------------------------- mesh core
def plate_mesh(O, holes, D, z0=0.0):
    """Closed solid between Z = z0 (front, +Z normal) and Z = z0 - D.
    O: CCW outline ring. holes: [(A, B, c, pt)] CW rings; A exact void, B its chamfer-offset
    ring (B is A when c == 0), c chamfer depth, pt a point inside the void.
    Caps use a constrained triangulation (no Steiner points) so collinear sills stay conforming."""
    verts, faces, n = [], [], [0]

    def put(R, Z):
        idx = np.arange(n[0], n[0] + len(R))
        verts.append(np.c_[R, np.full(len(R), Z)])
        n[0] += len(R)
        return idx

    def wall(U, Lw):  # same vertex count; U is front-ward
        j = np.roll(np.arange(len(U)), -1)
        faces.append(np.c_[U, Lw, U[j]])
        faces.append(np.c_[U[j], Lw, Lw[j]])

    def band(Ui, su, Li, sl, per):
        """Stitch two rings by their closest-point parameter along the exact void ring A
        (monotone for mitre offsets): no crossing triangles at bevels or consumed cusps."""
        nu, nl = len(Ui), len(Li)
        su_x, sl_x = np.r_[su, su[0] + per], np.r_[sl, sl[0] + per]
        i = j = 0
        out = []
        while i < nu or j < nl:
            adv_u = (j >= nl) or (i < nu and su_x[i + 1] <= sl_x[j + 1])
            if adv_u:
                out.append((Ui[i % nu], Li[j % nl], Ui[(i + 1) % nu]))
                i += 1
            else:
                out.append((Ui[i % nu], Li[j % nl], Li[(j + 1) % nl]))
                j += 1
        faces.append(np.array(out))

    def params(A, B):
        ring = shapely.LineString(np.r_[A, A[:1]])
        sA = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(A, axis=0), axis=1))]
        sB = shapely.line_locate_point(ring, shapely.points(B))
        k = int(np.argmin(sB))
        B, sB = np.roll(B, -k, axis=0), np.maximum.accumulate(np.roll(sB, -k))
        return B, sA, sB, float(ring.length)

    Of, Ob = put(O, z0), put(O, z0 - D)
    wall(Of, Ob)
    cap_rings, fidx, bidx = [O], [Of], [Ob]
    hole_pts = []
    for A, B, c, pt in holes:
        hole_pts.append(pt)
        if c > 0:
            B, sA, sB, per = params(A, B)
            Bf, Af, Ab, Bb = put(B, z0), put(A, z0 - c), put(A, z0 - D + c), put(B, z0 - D)
            band(Bf, sB, Af, sA, per)
            wall(Af, Ab)
            band(Ab, sA, Bb, sB, per)
            cap_rings.append(B)
            fidx.append(Bf)
            bidx.append(Bb)
        else:
            Af, Ab = put(A, z0), put(A, z0 - D)
            wall(Af, Ab)
            cap_rings.append(A)
            fidx.append(Af)
            bidx.append(Ab)
    P2 = np.vstack(cap_rings)
    segs, off = [], 0
    for r in cap_rings:
        idx = np.arange(off, off + len(r))
        segs.append(np.c_[idx, np.roll(idx, -1)])
        off += len(r)
    inp = dict(vertices=P2, segments=np.vstack(segs))
    if hole_pts:
        inp["holes"] = np.asarray(hole_pts, float)
    res = tri_lib.triangulate(inp, "pQ")
    if len(res["vertices"]) != len(P2) or not np.array_equal(res["vertices"], P2):
        raise RuntimeError("cap triangulation altered or added vertices")
    tri = np.asarray(res["triangles"], dtype=np.int64)
    a = P2[tri]
    s = (a[:, 1, 0] - a[:, 0, 0]) * (a[:, 2, 1] - a[:, 0, 1]) - (a[:, 1, 1] - a[:, 0, 1]) * (a[:, 2, 0] - a[:, 0, 0])
    tri[s < 0] = tri[s < 0][:, ::-1]
    fmap, bmap = np.concatenate(fidx), np.concatenate(bidx)
    faces.append(fmap[tri])
    faces.append(bmap[tri][:, ::-1])
    return np.vstack(verts), np.vstack(faces).astype(np.int64), float(np.abs(s).sum() / 2)


def mesh_qa(m):
    tri = m.triangles
    area2 = np.linalg.norm(np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1)
    _, cnt = np.unique(m.edges_sorted, axis=0, return_counts=True)
    bodies = len(trimesh.graph.connected_components(m.face_adjacency, nodes=np.arange(len(m.faces))))
    chi = len(m.vertices) - len(cnt) + len(m.faces)
    unref = len(m.vertices) - len(np.unique(m.faces))
    return dict(vertices=len(m.vertices), faces=len(m.faces), watertight=bool(m.is_watertight),
                winding_consistent=bool(m.is_winding_consistent), volume=float(m.volume),
                nonmanifold_edges=int((cnt != 2).sum()),
                degenerate_faces=int((area2 < 1e-12 * float(m.extents.max()) ** 2).sum()),
                unreferenced_vertices=int(unref), bodies=int(bodies), euler=int(chi),
                bounds=m.bounds.round(6).tolist())


def mesh_hash(m):
    h = hashlib.sha256()
    h.update(np.round(m.vertices, 9).tobytes())
    h.update(np.asarray(m.faces, np.int64).tobytes())
    return h.hexdigest()


# ----------------------------------------------------------------- model
class Model:
    def __init__(self, spec, scale=1.0):
        self.spec, self.k = spec, float(scale)
        self.id, self.mode = spec["id"], spec["mode"]
        self.tol = self.L(spec.get("tolerance", 0.02))
        self.members, self.seeds, self.checks, self.corrections = [], [], [], []
        self.con = {"arches": {}, "circles": {}}
        self.unseeded = "spandrel"
        self._outline()
        b = self.outline.bounds
        self.size = max(b[2] - b[0], b[3] - b[1])
        self.eps = 1e-9 * self.size
        if self.mode == "bar":
            self.fill(spec.get("fill"), self.W, self.sill, "W")
        elif self.mode == "plate":
            self._plate_voids()
        else:
            raise ValueError(f"unknown mode {self.mode}")
        self._topology()

    # -- helpers
    def L(self, v):
        return float(v) * self.k

    def check(self, name, ok, value, limit, kind="geometric"):
        self.checks.append(dict(name=name, ok=bool(ok), value=float(value), limit=float(limit), kind=kind))

    def _arch(self, a, xl=None, xr=None, spring=None):
        L, t = self.L, a.get("type", "pointed")
        if t == "measured":
            CL = Circle(*map(L, a["CL"]))
            CR = Circle(*map(L, a["CR"])) if "CR" in a else CL.mirror(L(a["axis"]))
            return Arch(L(a["xl"]), L(a["xr"]), CL, CR)
        f = {"equilateral": 1.0, "round": 0.5}.get(t, a.get("f", 1.0))
        if xl is None:
            half, ax = L(a["span"]) / 2, L(a.get("axis", 0.0))
            xl, xr, spring = ax - half, ax + half, L(a["spring"])
        return Arch.pointed(xl, xr, spring, float(f), L(a.get("drop", 0.0)))

    def _arch_checks(self, name, A):
        r = max(abs(A.CL.dist(*A.sl) - A.CL.r), abs(A.CR.dist(*A.sr) - A.CR.r),
                abs(A.CL.dist(*A.apex) - A.CL.r), abs(A.CR.dist(*A.apex) - A.CR.r))
        lim = 1e-9 * max(1.0, A.xr - A.xl)
        self.check(f"{name}: springings and apex lie on their circles", r <= lim, r, lim)
        ok = A.xl < A.apex[0] < A.xr
        self.check(f"{name}: apex between jambs", ok, A.apex[0], 0)

    # -- outline
    def _outline(self):
        o, L = self.spec["outline"], self.L
        if self.mode == "plate":
            self.O, self.W = self._arch(o["arch"]), None
            self.sill = L(o.get("base", 0))
            self.outline = self.O.polygon(self.sill, self.tol)
        else:
            self.W = self._arch(o["arch"])
            fw, self.sill = L(o["frame"]), L(o.get("sill", 0))
            self.O = self.W.off(fw)
            self.outline = self.O.polygon(self.sill - L(o.get("sill_band", o["frame"])), self.tol)
            self.Wp = self.W.polygon(self.sill, self.tol)
            self.members.append(dict(name="frame", kind="frame", poly=self.outline.difference(self.Wp)))
            self.con["arches"]["W"] = self.W.rec()
            self._arch_checks("W intrados", self.W)
        self.con["arches"]["outline"] = self.O.rec()
        self._arch_checks("outline", self.O)

    # -- bar tracery fills (recursive)
    def fill(self, F, W, sill, path):
        L = self.L
        if F is None:
            xm, zt = 0.5 * (W.xl + W.xr), min(W.sl[1], W.sr[1])
            self.seeds.append(("light", path, Point(xm, sill + 0.5 * (zt - sill))))
            return
        t, n, b = F["type"], int(F["n"]), L(F["band"])
        S = W.xr - W.xl
        zs = min(W.sl[1], W.sr[1]) + L(F.get("spring_rise", 0.0))
        if t == "lights":
            kids = F.get("children") or [None] * n
            sa = F.get("sub_arch", {"type": "equilateral"})
            subs = []
            for k in range(n):
                x0, x1 = W.xl + k * S / n, W.xl + (k + 1) * S / n
                E = self._arch(sa, x0, x1, zs)
                I = E.off(-b)
                nm = f"{path}.{'L' if kids[k] is None else 'A'}{k + 1}"
                band = E.polygon(sill, self.tol).difference(I.polygon(sill, self.tol))
                self.members.append(dict(name=nm + ".band", kind="sub_arch_band", poly=band))
                self.con["arches"][nm] = dict(E.rec(), band=round(b, 6))
                self._arch_checks(nm, E)
                self.fill(kids[k], I, sill, nm)
                subs.append(E)
            h = F.get("head")
            if h and h.get("type") == "oculus":
                if n != 2:
                    raise ValueError("oculus head requires n = 2 (group lights into sub-windows)")
                self._oculus(h, W, subs, path)
        elif t == "intersecting":
            self.unseeded = "eye"
            aL, aR = W.CL.x - W.xl, W.xr - W.CR.x
            # clip to the outline, not to W: W - members then trims arcs without coincident-edge overlays
            clip = box(W.xl - S, zs, W.xr + S, W.apex[1] + S).intersection(self.outline)
            for k in range(1, n):
                xk = W.xl + k * S / n
                self.members.append(dict(name=f"{path}.M{k}", kind="mullion", poly=box(xk - b, sill, xk + b, zs)))
                for side, c in (("r", Circle(xk + aL, W.CL.z, W.CL.r)), ("l", Circle(xk - aR, W.CR.z, W.CR.r))):
                    ann = circle_poly(c.off(b), self.tol).difference(circle_poly(c.off(-b), self.tol))
                    self.members.append(dict(name=f"{path}.M{k}{side}", kind="intersecting_arc",
                                             poly=ann.intersection(clip)))
                    self.con["circles"][f"{path}.M{k}{side}"] = dict(centre_line=c.rec(), band=round(b, 6))
            for k in range(n):
                self.seeds.append(("light", f"{path}.L{k + 1}", Point(W.xl + (k + 0.5) * S / n, 0.5 * (sill + zs))))
        else:
            raise ValueError(f"unknown fill type {t}")

    def _oculus(self, h, W, subs, path):
        L = self.L
        b = L(h["band"])
        ov = L(h.get("overlap", 0.5 * h["band"]))
        xm = 0.5 * (W.xl + W.xr)
        main, sub = W.CL, subs[0].CR

        def rho_of(z):
            return main.r + ov - main.dist(xm, z)

        def F(z):
            return sub.dist(xm, z) - (sub.r + rho_of(z) - ov)

        zlo, zhi = subs[0].sr[1], W.apex[1] - 1e-9 * (W.xr - W.xl)
        if not F(zlo) < 0 < F(zhi):
            raise ValueError(f"{path}: oculus tangency not bracketed")
        z = brentq(F, zlo, zhi, xtol=1e-14 * max(1.0, W.xr - W.xl), maxiter=500)
        rho = rho_of(z)
        if rho <= b:
            raise ValueError(f"{path}: oculus band wider than oculus")
        lim = 1e-9 * max(1.0, W.xr - W.xl)
        r1 = abs(main.dist(xm, z) - (main.r - rho + ov))
        r2 = abs(sub.dist(xm, z) - (sub.r + rho - ov))
        self.check(f"{path}.O: tangent to main intrados (overlap {ov:g})", r1 <= lim, r1, lim)
        self.check(f"{path}.O: tangent to sub-arch extrados (overlap {ov:g})", r2 <= lim, r2, lim)
        ring = circle_poly(Circle(xm, z, rho), self.tol).difference(circle_poly(Circle(xm, z, rho - b), self.tol))
        self.members.append(dict(name=f"{path}.O.ring", kind="oculus_ring", poly=ring))
        rec = dict(centre=[round(xm, 6), round(z, 6)], r_outer=round(rho, 6), band=round(b, 6), overlap=round(ov, 6))
        fo = h.get("foil")
        if fo:
            n, kk, ri = int(fo["n"]), float(fo.get("lobe_ratio", 1.15)), rho - b
            rc = ri / (1 + kk * math.sin(math.pi / n))
            rl = ri - rc
            ph = math.pi / 2 + (0.0 if fo.get("orient", "lobe_up") == "lobe_up" else math.pi / n)
            lobes = [Circle(xm + rc * math.cos(ph + 2 * math.pi * j / n), z + rc * math.sin(ph + 2 * math.pi * j / n), rl)
                     for j in range(n)]
            r0 = L(fo["centre_r"]) if "centre_r" in fo else rc
            void = unary_union([circle_poly(c, self.tol) for c in lobes] + [circle_poly(Circle(xm, z, r0), self.tol)])
            cusps = circle_poly(Circle(xm, z, ri), self.tol).difference(void)
            self.members.append(dict(name=f"{path}.O.cusps", kind="foil_cusps", poly=cusps))
            overlap = 2 * rl - 2 * rc * math.sin(math.pi / n)
            self.check(f"{path}.O: adjacent foil lobes intersect (cusps form)", overlap > 0, overlap, 0)
            rec["foil"] = dict(n=n, lobe_centre_r=round(rc, 6), lobe_r=round(rl, 6), centre_r=round(r0, 6),
                               lobes=[c.rec() for c in lobes])
            self.seeds.append(("foil", f"{path}.O", Point(xm, z)))
        else:
            self.seeds.append(("oculus", f"{path}.O", Point(xm, z)))
        self.con["circles"][f"{path}.O"] = rec

    # -- plate tracery voids
    def _plate_voids(self):
        L = self.L
        self.vpolys = []
        for i, v in enumerate(self.spec["voids"]):
            role, name = v["role"], v.get("name", f"V{i + 1}")
            if "arch" in v:
                A, sill = self._arch(v["arch"]), L(v["sill"])
                P = A.polygon(sill, self.tol)
                seed = Point(0.5 * (A.xl + A.xr), sill + 0.5 * (min(A.sl[1], A.sr[1]) - sill))
                self.con["arches"][name] = A.rec()
                self._arch_checks(name, A)
            elif "circles" in v:
                cs = [Circle(*map(L, c)) for c in v["circles"]]
                P, seed = unary_union([circle_poly(c, self.tol) for c in cs]), Point(cs[0].x, cs[0].z)
                self.con["circles"][name] = [c.rec() for c in cs]
            elif "regular" in v:
                g = v["regular"]
                cx, cz = map(L, g["centre"])
                n, rc, rl = int(g["n"]), L(g["ring"]), L(g["lobe_r"])
                ph = math.radians(g.get("phase_deg", 0.0))
                cs = [Circle(cx, cz, L(g["centre_r"]))] + [
                    Circle(cx + rc * math.cos(ph + 2 * math.pi * j / n), cz + rc * math.sin(ph + 2 * math.pi * j / n), rl)
                    for j in range(n)]
                P, seed = unary_union([circle_poly(c, self.tol) for c in cs]), Point(cx, cz)
                self.con["circles"][name] = [c.rec() for c in cs]
            else:
                raise ValueError(f"void {name}: no geometry")
            self.vpolys.append((role, name, P))
            self.seeds.append((role, name, seed))

    # -- topology: openings, persistent IDs, junctions, webs
    def _topology(self):
        tol = self.tol
        if self.mode == "bar":
            raw = polys(self.Wp.difference(unary_union([m["poly"] for m in self.members])))
        else:
            raw = polys(unary_union([p for _, _, p in self.vpolys]))
        min_area = max((10 * tol) ** 2, 1e-7 * self.outline.area)
        fork = self.L(self.spec.get("fork_fill", 0.0))
        found, voids = set(), []
        for P in raw:
            at = [round(v, 3) for v in P.representative_point().coords[0]]
            if P.area < min_area:
                self.corrections.append(dict(type="sliver_filled", area=round(P.area, 6), at=at))
                continue
            hits = [(r, n) for r, n, pt in self.seeds if P.contains(pt)]
            if len(hits) > 1:
                self.corrections.append(dict(type="openings_merged", names=[n for _, n in hits]))
            if hits:
                role, name = hits[0]
                found.update(n for _, n in hits)
                pieces = [P]
            else:
                if self.spec.get("spandrels", "pierced") == "solid":
                    continue
                role, name, pieces = self.unseeded, None, [P]
                if fork > 0:  # tas-de-charge: fill void tips narrower than 2*fork, keep exact edges elsewhere
                    Q = P.buffer(-fork, join_style="mitre", mitre_limit=2.0).buffer(fork, join_style="mitre", mitre_limit=2.0)
                    keep = P.intersection(Q.buffer(0.05 * fork, join_style="mitre", mitre_limit=2.0))
                    if P.area - keep.area > min_area:
                        self.corrections.append(dict(type="fork_tip_filled", area=round(P.area - keep.area, 3), at=at))
                        pieces = [q for q in polys(keep) if q.area >= min_area]
            for q in pieces:
                R0 = np.asarray(q.exterior.coords)[:-1]
                q1 = Polygon(clean_ring(R0, 0.25 * tol))
                if q1.is_valid and abs(q1.area - q.area) <= 1e-3 * q.area:
                    if len(q1.exterior.coords) != len(q.exterior.coords):
                        self.cleaned = getattr(self, "cleaned", 0) + len(q.exterior.coords) - len(q1.exterior.coords)
                    q = q1
                else:
                    self.corrections.append(dict(type="ring_cleanup_refused", at=at))
                voids.append(dict(role=role, name=name, poly=orient(q, 1.0)))
        for r, n, _ in self.seeds:
            self.check(f"seed {n} ({r}) lies in an opening", n in found, 0, 0, "architectural")
        q = 1e-6 * self.size

        def key(v):
            c = v["poly"].centroid
            return (ROLE_ORDER.get(v["role"], 9), v["name"] or "", -round(c.y / q), round(c.x / q))

        voids.sort(key=key)
        cnt = {}
        for v in voids:
            if v["name"]:
                v["id"] = v["name"]
            else:
                cnt[v["role"]] = cnt.get(v["role"], 0) + 1
                v["id"] = f"{ROLE_PREFIX.get(v['role'], 'X')}{cnt[v['role']]:02d}"
        self.voids = voids
        vu = unary_union([v["poly"] for v in voids])
        self.stone = self.outline.difference(vu)
        sp = polys(self.stone)
        self.check("stone is one connected region", len(sp) == 1, len(sp), 1, "geometric")
        self.check("openings have no stone islands", all(len(v["poly"].interiors) == 0 for v in voids),
                   0, 0, "geometric")
        bad = []
        for v in voids:
            R = np.asarray(v["poly"].exterior.coords)[:-1]
            short, spikes = ring_defects(R, 0.25 * tol)
            if short or spikes or not v["poly"].exterior.is_simple:
                bad.append(f"{v['id']}:{short}short/{spikes}spike")
        self.check(f"opening outlines clean: no micro-edges, spikes or self-touching ({bad or 'none'}; "
                   f"{getattr(self, 'cleaned', 0)} overlay artefact vertices removed)", not bad, len(bad), 0)
        if len(sp) == 1:
            self.check("stone holes == openings", len(sp[0].interiors) == len(voids), len(sp[0].interiors),
                       len(voids), "geometric")
        inner = self.outline.buffer(-self.eps)
        self.check("openings enclosed by stone", all(inner.contains(v["poly"]) for v in voids), 0, 0, "geometric")
        roles = {}
        for v in voids:
            roles[v["role"]] = roles.get(v["role"], 0) + 1
        self.roles = roles
        for r, e in self.spec.get("expect", {}).items():
            self.check(f"expected {e} x {r}", roles.get(r, 0) == e, roles.get(r, 0), e, "architectural")
        # webs
        best = (math.inf, None, None)
        for i, a in enumerate(voids):
            d = a["poly"].distance(self.outline.exterior)
            if d < best[0]:
                best = (d, a["id"], "outline")
            for b2 in voids[i + 1:]:
                d = a["poly"].distance(b2["poly"])
                if d < best[0]:
                    best = (d, a["id"], b2["id"])
        c_req = self.L(self.spec.get("section", {}).get("chamfer", 0.0))
        need = self.L(self.spec["min_web"]) if "min_web" in self.spec else 2 * c_req + 2 * tol
        self.web = dict(min=round(best[0], 6), between=[best[1], best[2]], required=round(need, 6))
        self.check(f"minimum stone web {best[0]:.3f} between {best[1]} / {best[2]}", best[0] >= need,
                   best[0], need, "architectural")
        # member / junction graph
        self.junctions = []
        nm = len(self.members)
        parent = list(range(max(nm, 1)))

        def find(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i

        for i in range(nm):
            for j in range(i + 1, nm):
                a, b2 = self.members[i]["poly"], self.members[j]["poly"]
                if not a.intersects(b2):
                    continue
                I = a.intersection(b2)
                kind = "overlap" if I.area > tol * tol else ("shared_edge" if I.length > tol else None)
                if kind:
                    self.junctions.append((self.members[i]["name"], self.members[j]["name"], kind))
                    parent[find(i)] = find(j)
        if nm:
            self.check("member/junction graph connected", len({find(i) for i in range(nm)}) == 1,
                       len({find(i) for i in range(nm)}), 1, "architectural")
            self.check("no empty members", all(not m["poly"].is_empty for m in self.members), 0, 0, "geometric")

    # -- 3D
    def _chamfers(self, c0):
        """Per-opening chamfer guard: halve the chamfer only on openings whose offset reveal would
        leave the outline or come within tol of a neighbouring reveal (mitre limit 1.5 = bevelled
        arrises at acute spandrel tips)."""
        n, inner = len(self.voids), self.outline.buffer(-self.tol)
        cs = [c0] * n
        for _ in range(12):
            Bs = [v["poly"].buffer(c, join_style="mitre", mitre_limit=1.5) if c > 0 else v["poly"]
                  for v, c in zip(self.voids, cs)]
            bad = {i for i, B in enumerate(Bs) if not isinstance(B, Polygon) or B.interiors or not inner.contains(B)}
            for i in range(n):
                for j in range(i + 1, n):
                    if Bs[i].distance(Bs[j]) < self.tol:
                        bad |= {i, j}
            if not bad:
                return cs, Bs
            for i in bad:
                cs[i] = cs[i] * 0.5 if cs[i] * 0.5 >= 2 * self.tol else 0.0
        return [0.0] * n, [v["poly"] for v in self.voids]

    def solids(self):
        L, sec = self.L, self.spec.get("section", {})
        D, c_req = L(sec["depth"]), L(sec.get("chamfer", 0.0))
        wl = self.spec.get("wall", {})
        self.recess = L(wl.get("recess", 0.0))
        cs, Bs = self._chamfers(min(c_req, 0.45 * D))
        for v, c in zip(self.voids, cs):
            v["chamfer"] = c
            if abs(c - c_req) > 1e-12:
                self.corrections.append(dict(type="chamfer_reduced", opening=v["id"], requested=round(c_req, 6),
                                             used=round(c, 6)))
        self.D, self.c, self.Bs = D, max(cs) if cs else 0.0, Bs
        O = ring_of(self.outline, 1.0, self.eps)
        holes = []
        for v, c, B in zip(self.voids, cs, Bs):
            A = ring_of(v["poly"], -1.0, self.eps)
            pt = v["poly"].representative_point()
            holes.append((A, ring_of(B, -1.0, self.eps) if c > 0 else A, c, (pt.x, pt.y)))
        V, F, cap = plate_mesh(O, holes, D, z0=-self.recess)
        self.stone_mesh = trimesh.Trimesh(V, F, process=False)
        front = Polygon(O, [h[1] for h in holes])
        self.cap_check = (cap, front.area)
        self.check("front cap triangulation area == stone face area", abs(cap - front.area) <= 1e-9 * front.area,
                   cap - front.area, 1e-9 * front.area)
        parts = [("stone", self.stone_mesh, (0.80, 0.76, 0.68, 1.0), 0.85)]
        if wl:
            m = L(wl["margin"])
            b = self.outline.bounds
            frame = orient(box(b[0] - m, b[1] - m, b[2] + m, b[3] + m), 1.0)
            Rw = ring_of(frame, 1.0, self.eps)
            Ro = ring_of(self.outline, -1.0, self.eps)
            pt = self.outline.representative_point()
            Vw, Fw, _ = plate_mesh(Rw, [(Ro, Ro, 0.0, (pt.x, pt.y))], L(wl["depth"]), z0=0.0)
            self.wall_mesh = trimesh.Trimesh(Vw, Fw, process=False)
            parts.append(("wall", self.wall_mesh, (0.60, 0.57, 0.52, 1.0), 0.9))
            self.check("tracery sits within wall depth", self.recess + D <= L(wl["depth"]) + 1e-9,
                       self.recess + D, L(wl["depth"]), "architectural")
        g = 0.04 * D
        panes = []
        for v in self.voids:
            Rg = ring_of(v["poly"].buffer(-1e-3 * D, join_style="mitre", mitre_limit=1.5), 1.0, self.eps)
            Vg, Fg, _ = plate_mesh(Rg, [], g, z0=-self.recess - 0.5 * D + 0.5 * g)
            panes.append(trimesh.Trimesh(Vg, Fg, process=False))
        if panes:
            parts.append(("glass", trimesh.util.concatenate(panes), (0.10, 0.17, 0.25, 1.0), 0.15))
        self.parts = parts
        return self

    def export_glb(self, path):
        sc = trimesh.Scene()
        for nm, m, rgba, rough in self.parts:
            mm = trimesh.Trimesh(m.vertices.copy(), m.faces.copy(), process=False)
            mat = trimesh.visual.material.PBRMaterial(name=f"{nm}_mat", baseColorFactor=list(rgba),
                                                      metallicFactor=0.0, roughnessFactor=rough)
            mm.visual = trimesh.visual.TextureVisuals(material=mat)
            sc.add_geometry(mm, node_name=f"{self.id}__{nm}", geom_name=f"{self.id}__{nm}")
        data = sc.export(file_type="glb")
        Path(path).write_bytes(data)
        return data

    def record(self):
        return dict(version=VERSION, id=self.id, mode=self.mode, units=self.spec.get("units"),
                    calibrated=bool(self.spec.get("calibrated", False)), scale=self.k,
                    tolerance=self.tol, construction=self.con,
                    members=[dict(name=m["name"], kind=m["kind"], area=round(m["poly"].area, 6)) for m in self.members],
                    junctions=[dict(a=a, b=b, type=t) for a, b, t in self.junctions],
                    openings=[dict(id=v["id"], role=v["role"], area=round(v["poly"].area, 6),
                                   centroid=[round(c, 6) for c in v["poly"].centroid.coords[0]],
                                   bounds=[round(c, 6) for c in v["poly"].bounds]) for v in self.voids],
                    roles=self.roles, web=self.web, corrections=self.corrections,
                    section=dict(depth=getattr(self, "D", None), chamfer_used=getattr(self, "c", None),
                                 chamfer_per_opening={v["id"]: round(v.get("chamfer", 0.0), 6) for v in self.voids},
                                 recess=getattr(self, "recess", None)),
                    stone_face_area=round(self.stone.area, 6))


def build(spec, scale=1.0):
    return Model(spec, scale).solids()
