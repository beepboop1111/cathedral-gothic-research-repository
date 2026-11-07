#!/usr/bin/env python3
"""tracery_centreline_U06.py -- EXPERIMENTAL U06: bar tracery laid out on centrelines (interdos lines).

Why U06: Hillson's survey of the Reims chevet-chapel windows (Windows on the Past, ADS 2024) shows bars laid out on
centrelines that fork at the mullion and jambs. U01 bar mode lays out the openings and puts each light's band inside
its own half, so it cannot reproduce the survey with realistic bars (first pass 2026-11-07: U01 best fit 17-41 mm RMS,
Hillson's centreline construction 9-15 mm, survey floor 4-6 mm).

Spec ("type": "centreline", units as declared, usually mm):
  centrelines.rule = "hillson_chevet": axis, span, apex, spring, oculus_z
        Hillson's chevet-chapel construction: main arch radius = span, centred on the jamb lines, stilted to the
        apex; two lights each half the span, rise = (apex - spring) / 4, centres on the springing line; oculus
        centred on the axis at oculus_z, tangent to the lancet centrelines.
  centrelines.rule = "circles": main {CL, CR}, lights [{CL, CR}, ...], oculus [x, z, r], impost
        any centreline circles, e.g. survey fits. CL = left half (centre to its right), CR = right half.
  bars: main, light, oculus (+ optional mullion if wider than light) - bar widths centred on the centrelines
  sill, sill_band, oculus_foil (optional, U01 foil rules), spandrels, fork_fill, section, wall, expect - as U01.

Springing rule: every arc springs where its circle meets max(centre height, impost) - at a vertical tangent when the
centre sits at or above that level, otherwise with a kinked impost (as surveyed). Tangent springings are moved 1e-7 r
inside the circle so U01's strict jamb test and its 6-decimal records stay valid (U01 raises on rounding there).

The model presents itself to U02/U03 as U01 bar mode: mode "bar", W (main intrados), O (outline), Wp, members
"frame", "W.Lk.band", "W.O.ring", "W.O.cusps", construction records in U01's schema (arches W / outline / W.Lk as
extrados + band, circles W.O with centre / r_outer / band / foil). U01-U05 code is not modified.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
U15 = HERE.parent.parent / "universal-generator-U01-U05-2026-11-07" / "scripts"
sys.path.insert(0, str(U15))

from shapely.geometry import LineString, Point  # noqa: E402
from shapely.ops import unary_union  # noqa: E402

import tracery_joints_U03 as J  # noqa: E402
import tracery_universal_U01 as T  # noqa: E402

VERSION = "U06-experimental"
NUDGE = 1e-7  # tangent springings: fraction of the radius moved inside the circle


class ArchC(T.Arch):
    """U01 Arch with a rounding-tolerant jamb test; offsets stay ArchC."""

    @staticmethod
    def _jz(c, x):
        h = c.r ** 2 - (x - c.x) ** 2
        if h < -1e-9 * c.r * c.r:
            raise ValueError("arc does not reach its jamb")
        return c.z + math.sqrt(max(h, 0.0))

    def off(self, d):
        return ArchC(self.xl - d, self.xr + d, self.CL.off(d), self.CR.off(d))


def springing_x(c, side, level):
    """Jamb x where circle c = (x, z, r) meets the springing level max(z, level). side -1: left half, +1: right."""
    x, z, r = c
    zs = max(z, level)
    if zs - z <= 1e-12 * r:                      # vertical tangent: move a hair inside the circle
        return x + side * r * (1.0 - NUDGE), True
    return x + side * math.sqrt(r * r - (zs - z) ** 2), False


def hillson_chevet(p):
    """Hillson's chevet-chapel construction (Reims N5.3.n / N4.3.ne / S4.3.se / S5.3.s design-process figure)."""
    xa, x0, yA, s, zO = p["axis"], p["span"], p["apex"], p["spring"], p["oculus_z"]
    zA = yA - math.sqrt(3.0) / 2.0 * x0          # centres on the jamb lines, radius = span, apex at yA
    rise = (yA - s) / 4.0
    u = ((x0 / 4.0) ** 2 + rise ** 2) / (x0 / 2.0)   # lancet radius (centres on the springing line)
    eL = u - x0 / 4.0
    xs, xn = xa - x0 / 4.0, xa + x0 / 4.0
    main = {"CL": (xa + x0 / 2.0, zA, x0), "CR": (xa - x0 / 2.0, zA, x0)}
    lights = [{"CL": (xs + eL, s, u), "CR": (xs - eL, s, u)}, {"CL": (xn + eL, s, u), "CR": (xn - eL, s, u)}]
    L2 = lights[0]["CR"]
    rO = math.hypot(xa - L2[0], zO - L2[1]) - u   # tangent to the lancet centrelines
    derived = dict(main_centre_z=zA, lancet_r=u, lancet_rise=rise, oculus_r=rO)
    return main, lights, (xa, zO, rO), s, derived


class CentrelineModel(T.Model):
    def __init__(self, spec, scale=1.0):
        self.spec, self.k = dict(spec), float(scale)
        self.id, self.mode = spec["id"], "bar"      # downstream stages treat it as bar tracery
        self.construction_mode = "centreline"
        self.tol = self.L(spec.get("tolerance", 0.5))
        self.members, self.seeds, self.checks, self.corrections = [], [], [], []
        self.con = {"arches": {}, "circles": {}, "centrelines": {}}
        self.unseeded = "spandrel"
        L, tol = self.L, self.tol
        main, lights, oculus, impost, rule = self._centrelines()
        bars = spec["bars"]
        wA, wL = L(bars["main"]), L(bars["light"])
        wO = L(bars.get("oculus", bars["light"]))
        self.spec.setdefault("fill", {"type": "lights", "n": len(lights), "band": bars["light"]})  # U03 sill joints

        # main arch: centreline -> intrados W, outline O, frame member (as U01)
        Cm = self._arch(main, impost)
        self.W, self.O = Cm.off(-wA / 2.0), Cm.off(wA / 2.0)
        self.sill = L(spec.get("sill", 0.0))
        self.outline = self.O.polygon(self.sill - L(spec.get("sill_band", bars["main"])), tol)
        self.Wp = self.W.polygon(self.sill, tol)
        b = self.outline.bounds
        self.size = max(b[2] - b[0], b[3] - b[1])
        self.eps = 1e-9 * self.size
        self.members.append(dict(name="frame", kind="frame", poly=self.outline.difference(self.Wp)))
        self.con["arches"]["W"] = self.W.rec()
        self.con["arches"]["outline"] = self.O.rec()
        self._arch_checks("W intrados", self.W)
        self._arch_checks("outline", self.O)
        self.con["centrelines"]["main"] = dict(Cm.rec(), bar=round(wA, 6))

        # lights: bars centred on their centrelines, recorded as U01 extrados + band. Members partition the stone like
        # U01: light bars are kept inside the frame opening and each light owns its side of a shared mullion.
        subs = [self._arch(lc, impost) for lc in lights]
        cuts = [0.5 * (subs[k].xr + subs[k + 1].xl) for k in range(len(subs) - 1)]
        big = 10.0 * self.size
        for k, C in enumerate(subs):
            E, I = C.off(wL / 2.0), C.off(-wL / 2.0)
            nm = f"W.L{k + 1}"
            x0 = cuts[k - 1] if k > 0 else -big
            x1 = cuts[k] if k < len(cuts) else big
            band = E.polygon(self.sill, tol).difference(I.polygon(self.sill, tol))
            band = band.intersection(self.Wp).intersection(T.box(x0, self.sill - big, x1, big))
            # fork at an outer jamb: below its springing the light's jamb bar is part of the main jamb bar
            for first, side in ((k == 0, "l"), (k == len(subs) - 1, "r")):
                if not first:
                    continue
                gap = abs((C.xl - Cm.xl) if side == "l" else (Cm.xr - C.xr))
                if gap <= wA / 2.0:
                    zsp = min(C.sl[1], E.sl[1], I.sl[1]) if side == "l" else min(C.sr[1], E.sr[1], I.sr[1])
                    strip = T.box(E.xl - big, self.sill - big, I.xl, zsp) if side == "l" else \
                        T.box(I.xr, self.sill - big, E.xr + big, zsp)
                    band = band.difference(strip)
                    self.con["centrelines"].setdefault("jamb_forks", {})[f"{nm}.{side}"] = round(gap, 6)
            self.members.append(dict(name=nm + ".band", kind="sub_arch_band", poly=band))
            self.con["arches"][nm] = dict(E.rec(), band=round(wL, 6))
            self.con["centrelines"][nm] = dict(C.rec(), bar=round(wL, 6))
            self._arch_checks(nm + " centreline", C)
            self._arch_checks(nm + " extrados", E)
            zt = min(C.sl[1], C.sr[1])
            self.seeds.append(("light", nm, Point(0.5 * (C.xl + C.xr), self.sill + 0.5 * (zt - self.sill))))
        if "mullion" in bars and L(bars["mullion"]) > wL + tol:
            wM = L(bars["mullion"])
            for k in range(len(subs) - 1):
                xm = 0.5 * (subs[k].xr + subs[k + 1].xl)
                zt = min(subs[k].sr[1], subs[k + 1].sl[1])
                self.members.append(dict(name=f"W.M{k + 1}", kind="mullion",
                                         poly=T.box(xm - wM / 2.0, self.sill, xm + wM / 2.0, zt)))

        self._oculus_c(oculus, wO, spec.get("oculus_foil"))
        self._centreline_checks(rule, Cm, subs, oculus, wA, wL, wO)
        self._topology()

    # ---------------------------------------------------------------- centrelines
    def _centrelines(self):
        c, L = self.spec["centrelines"], self.L
        rule = c["rule"]
        if rule == "hillson_chevet":
            p = {k: L(v) for k, v in c["params"].items()}
            main, lights, oculus, impost, derived = hillson_chevet(p)
            self.con["centrelines"]["rule"] = dict(name=rule, params={k: round(v, 6) for k, v in p.items()},
                                                   derived={k: round(v, 6) for k, v in derived.items()})
        elif rule == "circles":
            S = lambda t: tuple(L(v) for v in t)
            main = {"CL": S(c["main"]["CL"]), "CR": S(c["main"]["CR"])}
            lights = [{"CL": S(l["CL"]), "CR": S(l["CR"])} for l in c["lights"]]
            oculus, impost = S(c["oculus"]), L(c.get("impost", 0.0))
            self.con["centrelines"]["rule"] = dict(name=rule, source=c.get("source", ""))
        else:
            raise ValueError(f"unknown centreline rule {rule}")
        return main, lights, oculus, impost, rule

    def _arch(self, a, impost):
        xl, tl = springing_x(a["CL"], -1, impost)
        xr, tr = springing_x(a["CR"], +1, impost)
        return ArchC(xl, xr, T.Circle(*a["CL"]), T.Circle(*a["CR"]))

    # ---------------------------------------------------------------- oculus (U01 ring + optional U01 foils)
    def _oculus_c(self, oc, wO, fo):
        x, z, r = oc
        tol = self.tol
        rho = r + wO / 2.0
        if r - wO / 2.0 <= tol:
            raise ValueError("oculus bar wider than the oculus")
        ring = T.circle_poly(T.Circle(x, z, rho), tol).difference(T.circle_poly(T.Circle(x, z, rho - wO), tol))
        self.members.append(dict(name="W.O.ring", kind="oculus_ring", poly=ring))
        rec = dict(centre=[round(x, 6), round(z, 6)], r_outer=round(rho, 6), band=round(wO, 6),
                   centreline_r=round(r, 6))
        if fo:
            n, kk, ri = int(fo["n"]), float(fo.get("lobe_ratio", 1.15)), rho - wO
            rc = ri / (1 + kk * math.sin(math.pi / n))
            rl = ri - rc
            ph = math.pi / 2 + (0.0 if fo.get("orient", "lobe_up") == "lobe_up" else math.pi / n)
            lobes = [T.Circle(x + rc * math.cos(ph + 2 * math.pi * j / n), z + rc * math.sin(ph + 2 * math.pi * j / n), rl)
                     for j in range(n)]
            r0 = self.L(fo["centre_r"]) if "centre_r" in fo else rc
            void = unary_union([T.circle_poly(c, tol) for c in lobes] + [T.circle_poly(T.Circle(x, z, r0), tol)])
            cusps = T.circle_poly(T.Circle(x, z, ri), tol).difference(void)
            self.members.append(dict(name="W.O.cusps", kind="foil_cusps", poly=cusps))
            overlap = 2 * rl - 2 * rc * math.sin(math.pi / n)
            self.check("W.O: adjacent foil lobes intersect (cusps form)", overlap > 0, overlap, 0)
            rec["foil"] = dict(n=n, lobe_centre_r=round(rc, 6), lobe_r=round(rl, 6), centre_r=round(r0, 6),
                               lobes=[c.rec() for c in lobes])
            self.seeds.append(("foil", "W.O", Point(x, z)))
        else:
            self.seeds.append(("oculus", "W.O", Point(x, z)))
        self.con["circles"]["W.O"] = rec

    # ---------------------------------------------------------------- centreline checks
    def _centreline_checks(self, rule, Cm, subs, oc, wA, wL, wO):
        lim = 1e-9 * self.size
        x, z, r = oc
        gaps = {}
        # oculus centreline vs lancet centrelines next to the mullion (Hillson: tangent)
        for nm, c in (("L2", subs[0].CR), ("L3", subs[-1].CL)):
            gaps[f"oculus_{nm}"] = math.hypot(c.x - x, c.z - z) - c.r - r
        for nm, c in (("A1", Cm.CL), ("A2", Cm.CR)):
            gaps[f"oculus_{nm}"] = c.r - r - math.hypot(c.x - x, c.z - z)
        gaps["mullion_fork"] = subs[-1].xl - subs[0].xr
        gaps["jamb_fork_left"] = subs[0].xl - Cm.xl
        gaps["jamb_fork_right"] = Cm.xr - subs[-1].xr
        self.con["centrelines"]["gaps"] = {k: round(v, 6) for k, v in gaps.items()}
        self.check("lancet bars merge at the mullion (centreline fork gap <= light bar)",
                   abs(gaps["mullion_fork"]) <= wL, gaps["mullion_fork"], wL, "architectural")
        self.check("outer lancets spring inside the main jamb bars",
                   max(abs(gaps["jamb_fork_left"]), abs(gaps["jamb_fork_right"])) <= 0.5 * (wA + wL),
                   max(abs(gaps["jamb_fork_left"]), abs(gaps["jamb_fork_right"])), 0.5 * (wA + wL), "architectural")
        if rule == "hillson_chevet":
            p = self.con["centrelines"]["rule"]["params"]
            t = max(abs(gaps["oculus_L2"]), abs(gaps["oculus_L3"]))
            self.check("Hillson: oculus centreline tangent to the lancet centrelines", t <= lim, t, lim)
            self.check("Hillson: lancets spring from the mullion centreline (fork)",
                       abs(gaps["mullion_fork"]) <= 2 * NUDGE * subs[0].CR.r + lim, gaps["mullion_fork"],
                       2 * NUDGE * subs[0].CR.r, "historical")
            self.check("Hillson: outer lancets spring from the main jamb lines",
                       max(abs(gaps["jamb_fork_left"]), abs(gaps["jamb_fork_right"])) <= 2 * NUDGE * Cm.CL.r + lim,
                       max(abs(gaps["jamb_fork_left"]), abs(gaps["jamb_fork_right"])), 2 * NUDGE * Cm.CL.r, "historical")
            rise = subs[0].apex[1] - max(subs[0].CL.z, p["spring"])
            want = (p["apex"] - p["spring"]) / 4.0
            self.check("Hillson: lancet rise = (apex - spring) / 4", abs(rise - want) <= lim, abs(rise - want), lim)
            ap = abs(Cm.apex[1] - p["apex"])
            self.check("Hillson: main apex at the given height", ap <= lim, ap, lim)


class CentrelineJointed(J.Jointed):
    """U03 jointing, unchanged, plus one extension: U03 courses only up to the lowest springing. A stilted main arch
    (Reims chevet chapels: main springing ~2 m above the lights) would leave the jamb between as one >3 m stone, so
    the frame keeps its beds up to its own springing."""

    def __init__(self, spec, section, joints, scale=1.0):
        super().__init__(spec, section, joints, scale, model_cls=CentrelineModel)

    def _make_joints(self):
        super()._make_joints()
        m, e = self.m, self.e
        b0 = m.outline.bounds
        recs = m.con["arches"]
        z_lo = min(min(r["spring_l"][1], r["spring_r"][1]) for nm, r in recs.items() if nm != "outline") - self.keep
        z_hi = min(m.W.sl[1], m.W.sr[1]) - self.keep
        if z_hi - z_lo > 0.5 * self.course:
            n = max(1, math.ceil((z_hi - z_lo) / self.course))
            for i in range(1, n + 1):
                z = z_lo + i * (z_hi - z_lo) / n
                self._add("frame", "bed", "course", LineString([(b0[0] - e, z), (b0[2] + e, z)]), None)
            self.notes.append(f"U06: frame coursed up to the stilted main springing ({n} extra beds)")


def build(spec, scale=1.0):
    return CentrelineModel(spec, scale).solids()      # as U01's build
