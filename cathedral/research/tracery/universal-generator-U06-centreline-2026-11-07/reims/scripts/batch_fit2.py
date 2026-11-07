#!/usr/bin/env python3
"""Generalised Hillson-type rule (9 values) fitted to each grouped window, next to the free fit and the chevet rule.
gen: axis xa, main span x0 (jamb centrelines), apex yA, main radius rA = f*x0 (arcs tangent to the jambs),
     light span sL, mullion gap g, lancet springing s, lancet radius rL (centres on the springing line),
     oculus centre zO on the axis, tangent to the lancet centrelines.
usage: python3 -I batch_fit2.py <windows.txt> <batch_half.json(in, from batch_fit)> <out.json>
"""
import json, math, sys
import numpy as np
from scipy.optimize import least_squares
NAMES = ["A1", "A2", "O", "L1", "L2", "L3", "L4"]
K = ["xa", "x0", "yA", "f", "sL", "g", "s", "rL", "zO"]

def gen(t):
    xa, x0, yA, f, sL, g, s, rL, zO = t
    rA = f * x0; eA = rA - x0 / 2
    zA = yA - math.sqrt(max(rA * rA - eA * eA, 1e-12))
    jS, mS, mN, jN = xa - g / 2 - sL, xa - g / 2, xa + g / 2, xa + g / 2 + sL
    c = {"A1": (xa + eA, zA, rA), "A2": (xa - eA, zA, rA),
         "L1": (jS + rL, s, rL), "L2": (mS - rL, s, rL), "L3": (mN + rL, s, rL), "L4": (jN - rL, s, rL)}
    c["O"] = (xa, zO, math.hypot(xa - c["L2"][0], zO - s) - rL)
    return c

def resid(c, G):
    return np.concatenate([np.hypot(G[n][:, 0] - c[n][0], G[n][:, 1] - c[n][1]) - c[n][2] for n in NAMES])

wins, prev, out = open(sys.argv[1]).read().split(), json.load(open(sys.argv[2])), sys.argv[3]
for w in wins:
    r = prev[w]
    if not r.get("complete"):
        continue
    fj = json.load(open(f"out/fit_{w}.json")); pj = json.load(open(f"out/pts_{w}.json"))
    k = 1.0 if "marker_r4" in pj else pj["px_per_m"] / 5905.5
    P = np.array([[p["x"] * k, p["z"] * k] for p in pj["points"]])
    G = {n: P[fj["features"][n]["idx"]] for n in NAMES}
    F = r["free"]
    jl, jr = F["A1"][0] - F["A1"][2], F["A2"][0] + F["A2"][2]
    x0 = jr - jl; xa = 0.5 * (jl + jr)
    ljS, lmS = F["L1"][0] - F["L1"][2], F["L2"][0] + F["L2"][2]
    lmN, ljN = F["L3"][0] - F["L3"][2], F["L4"][0] + F["L4"][2]
    sL = 0.5 * ((lmS - ljS) + (ljN - lmN)); g = max(lmN - lmS, 0.0)
    t0 = [xa, x0, r["family"]["yA"], 0.5 * (F["A1"][2] + F["A2"][2]) / x0, sL, g,
          np.mean([F[n][1] for n in ("L1", "L2", "L3", "L4")]), np.mean([F[n][2] for n in ("L1", "L2", "L3", "L4")]), F["O"][1]]
    W = r["width"]
    lb = [xa - .2 * W, .7 * W, t0[2] - .6, .7, .3 * W, -.1 * W, t0[6] - .8, .2 * W, t0[8] - 1]
    ub = [xa + .2 * W, 1.3 * W, t0[2] + .6, 1.5, .6 * W, .1 * W, t0[6] + .8, 1.2 * W, t0[8] + 1]
    t0 = np.clip(t0, lb, ub)
    f = lambda t: resid(gen(t), G)
    best = None
    for dz in (0, -.15, .15):
        tt = t0.copy(); tt[8] = np.clip(tt[8] + dz, lb[8], ub[8])
        q = least_squares(f, tt, bounds=(lb, ub))
        if best is None or q.cost < best.cost: best = q
    t = best.x; rms = float(1000 * np.sqrt(np.mean(f(t) ** 2)))
    c = gen(t)
    r["gen"] = dict(zip(K, map(float, t))); r["rms"]["gen"] = rms
    r["gen_derived"] = dict(rA=float(t[3] * t[1]), rO=float(c["O"][2]), yL=float(math.sqrt(max(t[7] ** 2 - (t[7] - t[4] / 2) ** 2, 0))),
                            oculus_pos=float((t[2] - t[8]) / (t[2] - t[6])), light_ratio=float(2 * t[4] / t[1]))
    d = r["gen_derived"]
    print(f"{w:8} rms free {r['rms']['free']:5.1f} chevet {r['rms']['hillson']:6.1f} gen {rms:5.1f} | x0 {t[1]:.3f} yA-s {t[2]-t[6]:.3f} rA/x0 {t[3]:.3f} "
          f"2sL/x0 {d['light_ratio']:.3f} g {t[5]*1000:5.0f}mm rL {t[7]:.3f} rO {d['rO']:.3f} O-pos {d['oculus_pos']:.3f}")
json.dump(prev, open(out, "w"), indent=1)
