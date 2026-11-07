#!/usr/bin/env python3
"""Fit construction hypotheses to surveyed interdos (moulding-centreline) points.

Models (all in centreline space, metres; x = image left->right = south->north, z above the dashed line):
  free     7 independent circles (21 params) - floor set by survey + execution scatter
  hillson  Hillson's chevet-chapel construction (5 params: axis, span x0, apex yA, lancet springing s,
           oculus centre zO): equilateral arch R = x0 centred on the jambs, lancets x0/2 wide with rise
           (yA - s)/4 and centres on their springing line, oculus tangent to the lancet centrelines
  u01      U01 bar mode as the code builds it (uses U01's own Arch/Circle classes): measured main arch,
           lights splitting the intrados span with pointed sub-arches (f, drop), band b, oculus solved
           tangent to the main intrados and sub-arch extrados (overlap ov, oculus band = b)
           variants: bands free / bands fixed at TRIAL values
  u01eq    U01's Reims-type default: equilateral main arch and equilateral sub-arches (bands free)

usage: python3 -I hypotheses.py <u01_scripts_dir> <out.json> <win1> [<win2> ...]   (reads out/pts_<w>.json, out/fit_<w>.json)
"""
import json
import math
import sys

import numpy as np
from scipy.optimize import brentq, least_squares, minimize

sys.path.insert(0, sys.argv[1])
from tracery_universal_U01 import Arch, Circle  # noqa: E402  (U01's own construction classes)

# U01 finding: Arch._jz raises on rounding when a centre sits exactly one radius from its jamb (drop = 0,
# real-valued inputs). Clamp rounding-level negatives here; the generator itself needs the same fix.
def _jz_tolerant(c, x):
    h = c.r ** 2 - (x - c.x) ** 2
    if h < -1e-9 * c.r * c.r:
        raise ValueError("arc does not reach its jamb")
    return c.z + math.sqrt(max(h, 0.0))
Arch._jz = staticmethod(_jz_tolerant)

PPM = 5905.5          # 150 dpi drawing at 1:1 (matches Hillson's published radii; scale bar reads +0.3 %)
NAMES = ["A1", "A2", "O", "L1", "L2", "L3", "L4"]
BIG = 1.0             # residual (m) returned when a construction is impossible
TRIAL = dict(fw=0.24, b=0.12)   # TRIAL band widths (no Reims section data): frame 240 mm, light/oculus band 120 mm


def load(w):
    pts = json.load(open(f"out/pts_{w}.json"))
    fit = json.load(open(f"out/fit_{w}.json"))
    k = pts["px_per_m"] / PPM
    P = np.array([[p["x"] * k, p["z"] * k] for p in pts["points"]])
    groups = {n: P[fit["features"][n]["idx"]] for n in NAMES}
    free = {n: (fit["features"][n]["cx"], fit["features"][n]["cz"], fit["features"][n]["r"]) for n in NAMES}
    return P, groups, free, len(P) - sum(len(g) for g in groups.values())


def resid(circles, groups):
    out = []
    for n in NAMES:
        cx, cz, r = circles[n]
        g = groups[n]
        out.append(np.hypot(g[:, 0] - cx, g[:, 1] - cz) - r)
    return np.concatenate(out)


def stats(circles, groups):
    r = resid(circles, groups)
    per = {}
    i = 0
    for n in NAMES:
        m = len(groups[n])
        per[n] = round(1000 * float(np.sqrt(np.mean(r[i:i + m] ** 2))), 2)
        i += m
    return dict(rms_mm=round(1000 * float(np.sqrt(np.mean(r ** 2))), 2), max_mm=round(1000 * float(np.abs(r).max()), 2),
                per_feature_rms_mm=per)


# ------------------------------------------------------------------ Hillson
def hillson(t):
    xa, x0, yA, s, zO = t
    zA = yA - math.sqrt(3) / 2 * x0
    rise = (yA - s) / 4
    u = ((x0 / 4) ** 2 + rise ** 2) / (x0 / 2)
    eL = u - x0 / 4
    xs, xn = xa - x0 / 4, xa + x0 / 4
    c = {"A1": (xa + x0 / 2, zA, x0), "A2": (xa - x0 / 2, zA, x0),
         "L1": (xs + eL, s, u), "L2": (xs - eL, s, u), "L3": (xn + eL, s, u), "L4": (xn - eL, s, u)}
    rO = math.hypot(xa - c["L2"][0], zO - s) - u
    c["O"] = (xa, zO, rO)
    return c


# ------------------------------------------------------------------ U01 (built with U01's classes)
def u01(A1, A2, xl, xr, f_sub, drop, b, zs, fw, ov, b_O=None):
    b_O = b if b_O is None else b_O
    W = Arch(xl, xr, Circle(A1[0], A1[1], A1[2] - fw / 2), Circle(A2[0], A2[1], A2[2] - fw / 2))
    S = W.xr - W.xl
    subs = [Arch.pointed(W.xl + k * S / 2, W.xl + (k + 1) * S / 2, zs, f_sub, drop) for k in range(2)]
    xm = 0.5 * (W.xl + W.xr)
    main, sub = W.CL, subs[0].CR
    rho_of = lambda z: main.r + ov - main.dist(xm, z)
    F = lambda z: sub.dist(xm, z) - (sub.r + rho_of(z) - ov)
    zlo, zhi = subs[0].sr[1], W.apex[1] - 1e-9
    if not F(zlo) < 0 < F(zhi):
        raise ValueError("oculus tangency not bracketed")
    z = brentq(F, zlo, zhi, xtol=1e-12)
    rho = rho_of(z)
    if rho <= b_O:
        raise ValueError("oculus band wider than oculus")
    cl = lambda c, d: (c.x, c.z, c.r + d)
    return {"A1": cl(W.CL, fw / 2), "A2": cl(W.CR, fw / 2), "O": (xm, z, rho - b_O / 2),
            "L1": cl(subs[0].CL, -b / 2), "L2": cl(subs[0].CR, -b / 2),
            "L3": cl(subs[1].CL, -b / 2), "L4": cl(subs[1].CR, -b / 2)}, dict(W=W, subs=subs, oculus=(xm, z, rho))


def fit(model, t0, groups, lb, ub, restarts=0, seed=1, starts=()):
    """Multi-start least squares + Powell polish (constructions can be invalid -> penalty)."""
    lb, ub = np.array(lb, float), np.array(ub, float)
    n = sum(len(g) for g in groups.values())

    def f(t):
        try:
            return resid(model(t), groups)
        except (ValueError, ZeroDivisionError):
            return np.full(n, BIG)

    def cost(t):
        t = np.clip(t, lb, ub)
        return float(np.sum(f(t) ** 2))

    rng = np.random.default_rng(seed)
    cands = [np.clip(np.array(t, float), lb, ub) for t in [t0, *starts]]
    for _ in range(restarts):
        cands.append(np.clip(np.array(t0) + rng.normal(0, 0.02, len(t0)) * np.minimum(ub - lb, 2.0), lb, ub))
    best_t, best_c = None, np.inf
    for t in cands:
        if cost(t) >= BIG * n * 0.5:
            continue                                   # invalid start
        r = least_squares(f, t, bounds=(lb, ub), x_scale="jac", max_nfev=3000)
        m = minimize(cost, r.x, method="Powell", options=dict(maxiter=20000, xtol=1e-7, ftol=1e-12))
        tt = np.clip(m.x, lb, ub)
        r2 = least_squares(f, tt, bounds=(lb, ub), x_scale="jac", max_nfev=3000)
        c = cost(r2.x)
        if c < best_c:
            best_t, best_c = r2.x, c
    return best_t, model(best_t)


def main():
    out_path, wins = sys.argv[2], sys.argv[3:]
    report = {}
    for w in wins:
        P, groups, free, unassigned = load(w)
        rep = dict(points=int(len(P)), unassigned_junction_points=int(unassigned))
        rep["free"] = dict(params=21, **stats(free, groups),
                           circles={n: [round(v, 4) for v in free[n]] for n in NAMES})
        # common initial values
        xa0 = 0.25 * (free["L2"][0] + free["L1"][0] + free["L3"][0] + free["L4"][0])
        x00 = abs(free["A1"][0] - free["A2"][0])
        apex0 = max(free["A1"][1] + free["A1"][2] * 0.85, 3.5)
        s0 = float(np.mean([free[n][1] for n in ["L1", "L2", "L3", "L4"]]))
        # Hillson
        th, ch = fit(hillson, [xa0, x00, 4.4, s0, free["O"][1]], groups,
                     [xa0 - 0.5, 2.0, 3.0, -1.0, 1.0], [xa0 + 0.5, 4.0, 6.0, 1.0, 3.5], restarts=4)
        xa, x0, yA, s, zO = th
        rep["hillson"] = dict(params=5, **stats(ch, groups),
                              values=dict(axis=round(xa, 4), span_x0=round(x0, 4), apex_yA=round(yA, 4),
                                          lancet_springing_s=round(s, 4), oculus_centre_zO=round(zO, 4),
                                          oculus_r=round(ch["O"][2], 4), lancet_r=round(ch["L1"][2], 4),
                                          zO_position=round((yA - zO) / (yA - s), 4)),
                              circles={n: [round(v, 4) for v in ch[n]] for n in NAMES})
        # U01 Reims-type default: equilateral main + equilateral sub-arches; t = xa S_W zA fw zs b ov
        def m_eq(t):
            xa, SW, zA, fw, zs, b, ov = t
            W = Arch.pointed(xa - SW / 2, xa + SW / 2, zA, 1.0, 0.0)
            A1t = (W.CL.x, W.CL.z, W.CL.r + fw / 2)
            A2t = (W.CR.x, W.CR.z, W.CR.r + fw / 2)
            return u01(A1t, A2t, W.xl, W.xr, 1.0, 0.0, b, zs, fw, ov)[0]
        teq, ceq = fit(m_eq, [xa0, x00, free["A1"][1], 0.12, s0, 0.08, 0.0], groups,
                       [xa0 - 0.5, 2.0, 0.5, 0.01, -1.0, 0.01, -0.6], [xa0 + 0.5, 4.0, 3.0, 0.8, 1.5, 0.6, 0.6], restarts=6)
        rep["u01eq"] = dict(params=7, **stats(ceq, groups),
                            values=dict(zip(["axis", "intrados_span", "spring", "frame_fw", "sub_spring", "band_b", "overlap_ov"],
                                            [round(float(v), 4) for v in teq])),
                            circles={n: [round(v, 4) for v in ceq[n]] for n in NAMES})
        # U01 measured-arch bar mode; t = A1(3) A2(3) xl xr f_sub drop b zs fw ov
        A1, A2 = free["A1"], free["A2"]
        def pack_u01(t, fixed=None):
            A1t, A2t = t[0:3], t[3:6]
            xl, xr, f_sub, drop, b, zs, fw, ov = t[6:14]
            if fixed:
                fw, b = fixed["fw"], fixed["b"]
            return u01(A1t, A2t, xl, xr, f_sub, drop, b, zs, fw, ov)[0]
        for name, fixed in (("u01_bands_free", None), ("u01_bands_trial", TRIAL)):
            fwi = fixed["fw"] if fixed else 0.12
            xl0 = A1[0] - (A1[2] - fwi / 2) + 0.005
            xr0 = A2[0] + (A2[2] - fwi / 2) - 0.005
            t0 = [*A1, *A2, xl0, xr0, 0.95, 0.0, 0.08, s0, fwi, 0.0]
            lb = [A1[0] - 1, A1[1] - 1, 2.0, A2[0] - 1, A2[1] - 1, 2.0, xl0 - 0.4, xr0 - 0.4, 0.55, -0.5, 0.01, -1.0, 0.01, -0.6]
            ub = [A1[0] + 1, A1[1] + 1, 5.0, A2[0] + 1, A2[1] + 1, 5.0, xl0 + 0.4, xr0 + 0.4, 2.0, 1.5, 0.6, 1.5, 0.8, 0.6]
            starts = []
            # start from the U01-equilateral solution
            xa_, SW, zA_, fwq, zsq, bq, ovq = teq
            Weq = Arch.pointed(xa_ - SW / 2, xa_ + SW / 2, zA_, 1.0, 0.0)
            starts.append([Weq.CL.x, Weq.CL.z, Weq.CL.r + fwq / 2, Weq.CR.x, Weq.CR.z, Weq.CR.r + fwq / 2,
                           Weq.xl, Weq.xr, 1.0, 0.0, bq, zsq, fwq, ovq])
            # start from Hillson's construction (centrelines -> U01 intrados / extrados)
            for bh, fwh in ((0.04, 0.06), (0.08, 0.12)):
                if fixed:
                    bh, fwh = fixed["b"], fixed["fw"]
                hx = hillson(th)
                xa_h, x0_h = th[0], th[1]
                xlh, xrh = xa_h - x0_h / 2 + fwh / 2, xa_h + x0_h / 2 - fwh / 2
                RE = hx["L1"][2] + bh / 2
                a = hx["L1"][0] - xlh
                drop = math.sqrt(max(RE * RE - a * a, 0.0))
                SE = (xrh - xlh) / 2
                starts.append([*hx["A1"], *hx["A2"], xlh, xrh, RE / SE, drop, bh, th[3] + drop, fwh, 0.0])
            starts = [st for st in starts]
            tu, cu = fit(lambda t: pack_u01(t, fixed), t0, groups, lb, ub, restarts=8, starts=starts)
            xl, xr, f_sub, drop, b, zs, fw, ov = tu[6:14]
            if fixed:
                fw, b = fixed["fw"], fixed["b"]
            _, aux = u01(tu[0:3], tu[3:6], xl, xr, f_sub, drop, b, zs, fw, ov)
            W = aux["W"]
            rep[name] = dict(params=14 if not fixed else 12, **stats(cu, groups),
                             values=dict(xl=round(xl, 4), xr=round(xr, 4), f_sub=round(f_sub, 4), drop_sub=round(drop, 4),
                                         band_b=round(b, 4), frame_fw=round(fw, 4), overlap_ov=round(ov, 4),
                                         sub_spring_zs=round(zs, 4), main_spring=[round(W.sl[1], 4), round(W.sr[1], 4)],
                                         spring_rise=round(zs - min(W.sl[1], W.sr[1]), 4), apex=[round(v, 4) for v in W.apex],
                                         W_CL=[round(v, 5) for v in (W.CL.x, W.CL.z, W.CL.r)],
                                         W_CR=[round(v, 5) for v in (W.CR.x, W.CR.z, W.CR.r)]),
                             circles={n: [round(v, 4) for v in cu[n]] for n in NAMES}, t=[float(v) for v in tu])
        # fork geometry from the free fit: where the lancet centrelines meet the mullion / jambs
        def meet(c1, c2):
            (x1, z1, r1), (x2, z2, r2) = c1, c2
            d = math.hypot(x2 - x1, z2 - z1)
            if d > r1 + r2 or d < abs(r1 - r2):
                return None
            a = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
            h = math.sqrt(max(r1 * r1 - a * a, 0))
            mx, mz = x1 + a * (x2 - x1) / d, z1 + a * (z2 - z1) / d
            p = [(mx + h * (z2 - z1) / d, mz - h * (x2 - x1) / d), (mx - h * (z2 - z1) / d, mz + h * (x2 - x1) / d)]
            return min(p, key=lambda q: q[1])          # lower intersection = fork / springing crossing
        def at_z(c, z, side):
            x, zc, r = c
            h = r * r - (z - zc) ** 2
            return None if h < 0 else x + side * math.sqrt(h)
        mull = meet(free["L2"], free["L3"])
        rep["forks"] = dict(
            mullion_L2_L3_meet=[round(v, 4) for v in mull] if mull else None,
            impost_gap_L2_L3=round(at_z(free["L3"], 0.0, -1) - at_z(free["L2"], 0.0, +1), 4),
            jamb_gap_A1_L1=round(at_z(free["L1"], 0.0, -1) - (free["A1"][0] - free["A1"][2]), 4),
            jamb_gap_A2_L4=round((free["A2"][0] + free["A2"][2]) - at_z(free["L4"], 0.0, +1), 4),
            u01_implied=dict(mullion_gap="= band b (two light bands side by side)",
                             jamb_gap="= (frame + band)/2"))
        report[w] = rep
        print(f"\n== {w}: {len(P)} points ({unassigned} junction points left out)")
        for k in ["free", "hillson", "u01_bands_free", "u01_bands_trial", "u01eq"]:
            r = rep[k]
            pf = " ".join(f"{n}:{v:.1f}" for n, v in r["per_feature_rms_mm"].items())
            print(f"  {k:16} p={r['params']:2d}  rms {r['rms_mm']:6.2f} mm  max {r['max_mm']:6.1f}  | {pf}")
        print("  hillson:", rep["hillson"]["values"])
        print("  u01 free bands:", {k: v for k, v in rep["u01_bands_free"]["values"].items() if k in ("f_sub", "drop_sub", "band_b", "frame_fw", "overlap_ov", "spring_rise")})
        print("  u01eq:", rep["u01eq"]["values"])
        print("  forks:", {k: v for k, v in rep["forks"].items() if k != "u01_implied"})
    json.dump(report, open(out_path, "w"), indent=1)


if __name__ == "__main__":
    main()
