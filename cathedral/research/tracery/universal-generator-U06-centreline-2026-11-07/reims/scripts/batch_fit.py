#!/usr/bin/env python3
"""Fit construction rules to every grouped window (centreline space, metres).

  free     7 circles (21 values) - survey floor
  hillson  Hillson's chevet-chapel rule (5 values: axis, span x0, apex yA, springing s, oculus height zO)
  family   generalised rule (7 values): + main radius f*x0 (centres keep the arcs tangent to the jamb lines)
           + lancet rise = rho*(yA - s). chevet rule = f 1, rho 1/4
usage: python3 -I batch_fit.py <windows.txt> <out.json>
"""
import json
import math
import sys

import numpy as np
from scipy.optimize import least_squares

NAMES = ["A1", "A2", "O", "L1", "L2", "L3", "L4"]


def family(t):
    xa, x0, yA, s, zO, f, rho = t
    R = f * x0
    eA = R - x0 / 2                       # arc tangent to the jamb line at its centre height
    zA = yA - math.sqrt(max(R * R - eA * eA, 1e-12))
    rise = rho * (yA - s)
    u = ((x0 / 4) ** 2 + rise ** 2) / (x0 / 2)
    eL = u - x0 / 4
    xs, xn = xa - x0 / 4, xa + x0 / 4
    c = {"A1": (xa + eA, zA, R), "A2": (xa - eA, zA, R),
         "L1": (xs + eL, s, u), "L2": (xs - eL, s, u), "L3": (xn + eL, s, u), "L4": (xn - eL, s, u)}
    c["O"] = (xa, zO, math.hypot(xa - c["L2"][0], zO - s) - u)
    return c


def resid(c, G):
    return np.concatenate([np.hypot(G[n][:, 0] - c[n][0], G[n][:, 1] - c[n][1]) - c[n][2] for n in NAMES])


def fit(G, t0, lb, ub, fixed=None):
    idx = [i for i in range(7) if not fixed or i not in fixed]
    def full(v):
        t = np.array(t0, float)
        t[idx] = v
        if fixed:
            for i, val in fixed.items():
                t[i] = val
        return t
    f = lambda v: resid(family(full(v)), G)
    best = None
    for dz in (0.0, -0.1, 0.1):
        v0 = np.array(t0, float)[idx]
        v0[[k for k, i in enumerate(idx) if i == 4]] += dz
        r = least_squares(f, np.clip(v0, np.array(lb)[idx], np.array(ub)[idx]), bounds=(np.array(lb)[idx], np.array(ub)[idx]))
        if best is None or r.cost < best.cost:
            best = r
    t = full(best.x)
    return t, float(1000 * np.sqrt(np.mean(f(best.x) ** 2)))


def main():
    wins, out = open(sys.argv[1]).read().split(), sys.argv[2]
    rep = {}
    for w in wins:
        fj = json.load(open(f"out/fit_{w}.json"))
        pj = json.load(open(f"out/pts_{w}.json"))
        if not fj.get("complete"):
            rep[w] = dict(complete=False, unassigned=fj["unassigned"])
            continue
        k = 1.0 if "marker_r4" in pj else pj["px_per_m"] / 5905.5
        P = np.array([[p["x"] * k, p["z"] * k] for p in pj["points"]])
        F = fj["features"]
        G = {n: P[F[n]["idx"]] for n in NAMES}
        free = {n: (F[n]["cx"], F[n]["cz"], F[n]["r"]) for n in NAMES}
        rms_free = float(1000 * np.sqrt(np.mean(resid(free, G) ** 2)))
        xa = 0.25 * sum(F[n]["cx"] for n in ("L1", "L2", "L3", "L4"))
        x0 = abs(F["A1"]["cx"] - F["A2"]["cx"]) + 0.0
        x0 = max(x0, 0.5 * np.ptp(P[:, 0]))
        yA = float(P[:, 1].max())
        s = float(np.mean([F[n]["cz"] for n in ("L1", "L2", "L3", "L4")]))
        W = float(np.ptp(P[:, 0]))
        t0 = [xa, W * 0.95, yA, s, F["O"]["cz"], 1.0, 0.25]
        lb = [xa - 0.3 * W, 0.6 * W, yA - 0.5, s - 0.6, F["O"]["cz"] - 1.0, 0.75, 0.12]
        ub = [xa + 0.3 * W, 1.3 * W, yA + 0.5, s + 0.6, F["O"]["cz"] + 1.0, 1.4, 0.45]
        th, rh = fit(G, t0, lb, ub, fixed={5: 1.0, 6: 0.25})
        tf, rf = fit(G, list(th[:5]) + [1.0, 0.25], lb, ub)
        cfam = family(tf)
        gO = [1000 * (math.hypot(free[l][0] - free["O"][0], free[l][1] - free["O"][1]) - free[l][2] - free["O"][2]) for l in ("L2", "L3")]
        rep[w] = dict(complete=True, width=W, points=int(len(P)), unassigned=fj["unassigned"],
                      rms=dict(free=rms_free, hillson=rh, family=rf),
                      hillson=dict(zip(["axis", "x0", "yA", "s", "zO"], map(float, th[:5]))),
                      family=dict(zip(["axis", "x0", "yA", "s", "zO", "f", "rho"], map(float, tf))),
                      oculus_pos=float((tf[2] - tf[4]) / (tf[2] - tf[3])), oculus_lancet_gap_mm=gO,
                      oculus_r_over_x0=float(cfam["O"][2] / tf[1]), free={n: list(map(float, free[n])) for n in NAMES})
        r = rep[w]
        print(f"{w:8} W {W:4.2f}  rms free {rms_free:5.1f} hillson {rh:5.1f} family {rf:5.1f}  "
              f"f {tf[5]:.3f} rho {tf[6]:.3f} zO-pos {r['oculus_pos']:.3f} rO/x0 {r['oculus_r_over_x0']:.3f} "
              f"x0 {tf[1]:.3f} H {tf[2] - tf[3]:.3f}")
    json.dump(rep, open(out, "w"), indent=1)


if __name__ == "__main__":
    main()
