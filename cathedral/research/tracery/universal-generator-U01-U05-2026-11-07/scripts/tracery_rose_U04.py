#!/usr/bin/env python3
"""tracery_rose_U04.py -- EXPERIMENTAL rose / wheel window for the U01-U03 pipeline.

Construction (bar tracery, circular outline):
  * frame: annulus R_w..R_o (order 0)
  * hub: cusped oculus at the centre (ring + n-foil cusps)
  * n cells between radiating bars. Each cell is a wedge whose sides are the spoke centre-lines,
    headed by a two-centred pointed arch springing on those centre-lines at radius R_s. As in the
    windows, every cell owns a band of width b (extrados - concentric intrados), so two adjacent
    bands form one bar of width 2b along each spoke.
  * cusped circle on every spoke axis, solved tangent to the frame intrados and to the two
    neighbouring arch extrados (with overlap), as the window oculus is.
Then U01 topology (openings, persistent IDs, junctions), U02 orders/mouldings and U03 jointing apply
unchanged; only joint layout rules are rose-specific (radial frame voussoirs, transverse joints on
the bars, voussoirs radial to each head's own centres, rings cut at lobe centres).
Sizes are parametric TRIAL values, not a survey of any rose.
"""
from __future__ import annotations

import math

import numpy as np
import shapely
from scipy.optimize import brentq
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

import tracery_joints_U03 as J
import tracery_section_U02 as U
import tracery_universal_U01 as T


def _rot(theta, cx, cz):
    c, s = math.cos(theta), math.sin(theta)
    return lambda x, z: (cx + x * c - z * s, cz + x * s + z * c)


def _circle_world(C, f):
    x, z = f(C.x, C.z)
    return T.Circle(x, z, C.r)


def _cc_apex(a, b):
    tmp = object.__new__(T.Arch)
    tmp.CL, tmp.CR = a, b
    return tmp._apex()


class RoseModel(T.Model):
    def __init__(self, spec, scale=1.0):
        self.spec, self.k = spec, float(scale)
        self.id, self.mode = spec["id"], "bar"
        self.tol = self.L(spec.get("tolerance", 0.5))
        self.members, self.seeds, self.checks, self.corrections = [], [], [], []
        self.con = {"arches": {}, "circles": {}, "cells": {}}
        self.unseeded = "spandrel"
        o, L = spec["outline"], self.L
        cx, cz = map(L, o.get("centre", [0, 0]))
        self.c0, self.Ro = (cx, cz), L(o["radius"])
        self.Rw = self.Ro - L(o["frame"])
        nsym, ph0 = int(spec["rose"]["n"]), math.radians(spec["rose"].get("spoke_phase_deg", 90.0))
        self.outline = self._cp(cx, cz, self.Ro, ph0, nsym)
        self.Wp = self._cp(cx, cz, self.Rw, ph0, nsym)
        self.W = self.O = None
        self.sill = -1e18
        self.size = 2 * self.Ro
        self.eps = 1e-9 * self.size
        self.members.append(dict(name="frame", kind="frame", poly=self.outline.difference(self.Wp)))
        self._rose()
        self._topology()
        self._symmetry()

    def _cp(self, cx, cz, r, phase, mult):
        """Circle polygon with a vertex count divisible by `mult` and vertices phased from `phase`, so the
        rose's rotational copies coincide exactly."""
        n0 = max(24, math.ceil(2 * math.pi / T._step(r, self.tol)))
        n = mult * math.ceil(n0 / mult)
        t = phase + np.linspace(0, 2 * math.pi, n, endpoint=False)
        return Polygon(np.c_[cx + r * np.cos(t), cz + r * np.sin(t)])

    def _foil(self, path, cx, cz, rho, b, fo, phase):
        L = self.L
        ri = rho - b
        n, kk = int(fo["n"]), float(fo.get("lobe_ratio", 1.15))
        rc = ri / (1 + kk * math.sin(math.pi / n))
        rl = ri - rc
        ph = phase + (0.0 if fo.get("orient", "lobe_out") == "lobe_out" else math.pi / n)
        lobes = [T.Circle(cx + rc * math.cos(ph + 2 * math.pi * j / n), cz + rc * math.sin(ph + 2 * math.pi * j / n), rl)
                 for j in range(n)]
        # lobes cut the ring's inner face by one tolerance step: no zero-width slivers at tangencies
        void = unary_union([self._cp(c.x, c.z, c.r + self.tol, math.atan2(c.z - cz, c.x - cx), 1) for c in lobes]
                           + [self._cp(cx, cz, rc, ph, n)])
        ring = self._cp(cx, cz, rho, ph, n).difference(self._cp(cx, cz, ri, ph, n))
        cusps = self._cp(cx, cz, ri, ph, n).difference(void)
        self.members.append(dict(name=f"{path}.ring", kind="oculus_ring", poly=ring))
        self.members.append(dict(name=f"{path}.cusps", kind="foil_cusps", poly=cusps))
        self.seeds.append(("foil", path, Point(cx, cz)))
        ov = 2 * rl - 2 * rc * math.sin(math.pi / n)
        self.check(f"{path}: adjacent foil lobes intersect (cusps form)", ov > 0, ov, 0)
        self.con["circles"][path] = dict(centre=[round(cx, 6), round(cz, 6)], r_outer=round(rho, 6), band=round(b, 6),
                                         foil=dict(n=n, lobe_r=round(rl, 6), lobe_centre_r=round(rc, 6),
                                                   lobes=[c.rec() for c in lobes]))

    def _rose(self):
        L, r = self.L, self.spec["rose"]
        cx, cz = self.c0
        n, b, Rw = int(r["n"]), L(r["band"]), self.Rw
        a = math.pi / n
        phi0 = math.radians(r.get("spoke_phase_deg", 90.0))
        h = r["hub"]
        rh, bh = L(h["radius"]), L(h["band"])
        self._foil("W.H", cx, cz, rh, bh, h["foil"], phi0)
        hub_hole = self._cp(cx, cz, rh - bh, phi0, n)
        Rs, f = L(r["spring"]), float(r.get("arch_f", 1.0))
        tol, lim = self.tol, 1e-9 * self.size
        pl, pr = (-Rs * math.sin(a), Rs * math.cos(a)), (Rs * math.sin(a), Rs * math.cos(a))
        rE = f * 2 * Rs * math.sin(a)
        CLl, CRl = T.Circle(pl[0] + rE, pl[1], rE), T.Circle(pr[0] - rE, pr[1], rE)
        apexE = _cc_apex(CLl, CRl)
        CLi, CRi = CLl.off(-b), CRl.off(-b)
        apexI = _cc_apex(CLi, CRi)

        def spring_I(C, side):  # offset spoke line (inward by b) meets the intrados circle
            d = np.array([side * math.sin(a), math.cos(a)])
            nrm = np.array([-side * math.cos(a), math.sin(a)])
            p0 = b * nrm - np.array([C.x, C.z])
            A, B_, Cc = 1.0, 2 * d @ p0, p0 @ p0 - C.r ** 2
            t = (-B_ + math.sqrt(B_ * B_ - 4 * A * Cc)) / 2
            return tuple(t * d + b * nrm)

        slI, srI = spring_I(CLi, -1), spring_I(CRi, +1)
        self.check("rose cell: intrados springings lie on offset spoke lines and arcs",
                   abs(CLi.dist(*slI) - CLi.r) <= lim and abs(CRi.dist(*srI) - CRi.r) <= lim,
                   max(abs(CLi.dist(*slI) - CLi.r), abs(CRi.dist(*srI) - CRi.r)), lim)
        E_loc = np.r_[[[0.0, 0.0], pl], T.arc_pts(CLl, pl, apexE, tol)[1:], T.arc_pts(CRl, apexE, pr, tol)[1:]]
        I_loc = np.r_[[[0.0, b / math.sin(a)], slI], T.arc_pts(CLi, slI, apexI, tol)[1:],
                      T.arc_pts(CRi, apexI, srI, tol)[1:]]
        arcE = np.r_[T.arc_pts(CLl, pl, apexE, tol)[1:], T.arc_pts(CRl, apexE, pr, tol)[1:-1]]  # apex kept once
        cr = r["circles"]
        bc, ovc = L(cr["band"]), L(cr.get("overlap", 0.5 * cr["band"]))
        Rt = Rw  # surface the circles touch: wall frame, or the tracery's own ring when a chassis is present
        if "chassis" in r:
            bch = L(r["chassis"]["band"])
            Rt = Rw - bch
            ring = self._cp(cx, cz, Rw, phi0, n).difference(self._cp(cx, cz, Rt, phi0, n))
            self.members.append(dict(name="W.R.ring", kind="oculus_ring", poly=ring))
            self.con["circles"]["W.R"] = dict(centre=[round(cx, 6), round(cz, 6)], r_outer=round(Rw, 6), band=round(bch, 6))
        sd = np.array([math.sin(a), math.cos(a)])  # spoke direction in the cell-local frame (right side)

        def F(R):
            C = R * sd
            return math.hypot(C[0] - CRl.x, C[1] - CRl.z) - (CRl.r + (Rt + ovc - R) - ovc)

        Rc = brentq(F, Rs, Rt - 1e-9 * Rt, xtol=1e-12 * Rt)
        rho_c = Rt + ovc - Rc
        self.check("spoke circle tangent to the ring it springs from (overlap)", abs(Rc + rho_c - (Rt + ovc)) <= lim, 0, lim)
        self.check("spoke circle tangent to neighbouring head extrados (overlap)", abs(F(Rc)) <= lim, F(Rc), lim)
        self.con["rose"] = dict(n=n, band=b, Rs=Rs, rE=rE, Rc=Rc, rho_c=rho_c, Rw=Rw, Ro=self.Ro, hub=rh, hub_band=bh)
        for i in range(n):
            phc = phi0 + (2 * i + 1) * a
            fw = _rot(phc - math.pi / 2, cx, cz)
            th = phc - math.pi / 2
            ct, st = math.cos(th), math.sin(th)
            rot = lambda P: np.c_[cx + P[:, 0] * ct - P[:, 1] * st, cz + P[:, 0] * st + P[:, 1] * ct]
            # spoke points from the spoke angle itself: neighbouring cells share them bit-for-bit
            spk = lambda ang: (cx + Rs * math.cos(ang), cz + Rs * math.sin(ang))
            Ew = np.r_[[[cx, cz], spk(phc + a)], rot(arcE), [spk(phc - a)]]
            band = Polygon(Ew).difference(Polygon(rot(I_loc))).difference(hub_hole)
            nm = f"W.C{i + 1:02d}"
            self.members.append(dict(name=nm + ".band", kind="sub_arch_band", poly=band))
            self.seeds.append(("light", nm, Point(*fw(0.0, 0.5 * (rh + Rs * math.cos(a))))))
            self.con["cells"][nm] = dict(axis=phc, CL=_circle_world(CLl, fw).rec(), CR=_circle_world(CRl, fw).rec(),
                                        band=b, sl=list(fw(*pl)), sr=list(fw(*pr)), apex=list(fw(*apexE)),
                                        apexI=list(fw(*apexI)))
            # cusped circle on the spoke that is the right side of this cell (world angle phc - a)
            phs = phc - a
            ccx, ccz = cx + Rc * math.cos(phs), cz + Rc * math.sin(phs)
            path = f"W.K{i + 1:02d}.O"
            self._foil(path, ccx, ccz, rho_c, bc, cr["foil"], phs)
            self.con["circles"][path]["overlap"] = round(ovc, 6)

    def _symmetry(self):
        n = int(self.spec["rose"]["n"])
        cx, cz = self.c0
        from shapely import affinity
        rot = affinity.rotate(self.stone, 360.0 / n, origin=(cx, cz))
        sd = rot.symmetric_difference(self.stone).area
        self.check(f"{n}-fold rotational symmetry of the stone (sym. diff {sd:.3g})", sd <= 1e-4 * self.stone.area, sd,
                   1e-4 * self.stone.area)


class RoseJointed(J.Jointed):
    simplify_factor = 0.05
    def __init__(self, spec, section, joints, scale=1.0):
        super().__init__(spec, section, joints, scale, model_cls=RoseModel)

    def _zones(self):
        m = self.m
        cx, cz = m.c0
        out = []
        for a_, b_, t in m.junctions:
            A, B = self.mem[a_], self.mem[b_]
            if "foil_cusps" in (A["kind"], B["kind"]) or (t != "overlap" and "frame" in (A["kind"], B["kind"])):
                continue
            I = A["poly"].intersection(B["poly"])
            wid = lambda P: 2 * P.area / P.length
            r = self.kf * min(wid(A["poly"]), wid(B["poly"]))
            if t == "overlap":
                out.append(I.buffer(r))
            else:  # fork = end of the shared edge farthest from the rose centre
                c = np.asarray(I.coords) if I.geom_type == "LineString" else np.vstack(
                    [np.asarray(g.coords) for g in getattr(I, "geoms", []) if hasattr(g, "coords")] or [np.zeros((0, 2))])
                if len(c):
                    far = c[np.argmax(np.hypot(c[:, 0] - cx, c[:, 1] - cz))]
                    out.append(Point(far).buffer(r))
        return out

    def _ring(self, nm, c):
        e = self.e
        cx, cz = c["centre"]
        rho, b = c["r_outer"], c["band"]
        if "foil" not in c:  # plain tracery ring: voussoir-length spacing, junction keep-outs respected
            buf = self.mem[nm + ".ring"]["poly"].buffer(1.5 * e)
            C, rm, acc = T.Circle(cx, cz, rho), rho - b / 2, []
            for th in np.linspace(0, 2 * math.pi, 1440, endpoint=False) + math.pi / 2:
                if self._free(self._radial(C, rho - b, rho, th), buf) and (not acc or (th - acc[-1]) * rm >= 0.9 * self.vous):
                    acc.append(th)
            if len(acc) > 1 and (acc[0] + 2 * math.pi - acc[-1]) * rm < self.lmin:
                acc.pop()
            for th in acc:
                self._add("tracery", "ring", nm, self._radial(C, rho - b, rho, th), C)
            return
        angs = [math.atan2(l[1] - cz, l[0] - cx) for l in c["foil"]["lobes"]]
        buf = self.mem[nm + ".ring"]["poly"].buffer(1.5 * e)
        acc = []
        for th in sorted(x % (2 * math.pi) for x in angs):
            sg = self._radial(T.Circle(cx, cz, rho), rho - b, rho, th)
            if self._free(sg, buf) and (not acc or (th - acc[-1]) * (rho - b / 2) >= self.lmin):
                acc.append(th)
        if len(acc) > 1 and (acc[0] + 2 * math.pi - acc[-1]) * (rho - b / 2) < self.lmin:
            acc.pop()
        for th in acc:
            self._add("tracery", "ring", nm, self._radial(T.Circle(cx, cz, rho), rho - b, rho, th), T.Circle(cx, cz, rho))

    def _make_joints(self):
        m, e = self.m, self.e
        cx, cz = m.c0
        R = m.con["rose"]
        Cw = T.Circle(cx, cz, m.Rw)
        # frame: radial voussoirs through the rose centre
        buf = self.mem["frame"]["poly"].buffer(1.5 * e)
        rm = 0.5 * (m.Rw + m.Ro)
        acc = []
        for th in np.linspace(0, 2 * math.pi, 1440, endpoint=False) + math.pi / 2:
            if self._free(self._radial(Cw, m.Rw, m.Ro, th), buf) and (not acc or (th - acc[-1]) * rm >= 0.9 * self.vous):
                acc.append(th)
        if len(acc) > 1 and (acc[0] + 2 * math.pi - acc[-1]) * rm < self.lmin:
            acc.pop()
        for th in acc:
            self._add("frame", "voussoir", "frame", self._radial(Cw, m.Rw, m.Ro, th), Cw)
        # bars: transverse bed joints at equal spacing between hub and springing
        n, b = R["n"], R["band"]
        cells = list(m.con["cells"].items())
        allb = unary_union([x["poly"] for x in m.members if x["kind"] == "sub_arch_band"]).buffer(1.5 * e)
        for i, (nm, c) in enumerate(cells):
            phs = c["axis"] - math.pi / n
            span = R["Rs"] - R["hub"]
            k = max(1, math.ceil(span / self.course))
            u_ = np.array([math.cos(phs), math.sin(phs)])
            t_ = np.array([-u_[1], u_[0]])
            for j in range(1, k):
                rr = R["hub"] + j * span / k
                P = np.array([cx, cz]) + rr * u_
                sg = LineString([P - (b + e) * t_, P + (b + e) * t_])
                if self._free(sg, allb):
                    self._add("tracery", "bed", f"bar{i + 1:02d}", sg, None)
        # heads: voussoirs radial to each head's own centres
        for nm, c in cells:
            CL, CR = T.Circle(*c["CL"]), T.Circle(*c["CR"])
            ang = lambda C, p: math.atan2(p[1] - C.z, p[0] - C.x)
            unwrap = lambda a0, a1: a0 + ((a1 - a0 + math.pi) % (2 * math.pi) - math.pi)
            l0, l1 = ang(CL, c["sl"]), ang(CL, c["apex"])
            r0, r1 = ang(CR, c["apex"]), ang(CR, c["sr"])
            u_ = np.array([math.cos(c["axis"]), math.sin(c["axis"])])
            crown = LineString([np.array(c["apexI"]) - e * u_, np.array(c["apex"]) + e * u_])
            self._arch_joints(nm, (CL, CL.r - b, CL.r, l0, unwrap(l0, l1)), (CR, CR.r - b, CR.r, r0, unwrap(r0, r1)),
                              crown, self.mem[nm + ".band"]["poly"], "tracery")
        for nm, c in m.con["circles"].items():
            self._ring(nm, c)
