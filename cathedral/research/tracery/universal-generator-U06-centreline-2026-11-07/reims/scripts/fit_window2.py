#!/usr/bin/env python3
"""Topology-aware grouping of surveyed points for a 2-light + oculus window (replaces blind sequential RANSAC).

1 oculus  = RANSAC circle with the widest angular coverage
2 main arch = on each side of the oculus axis, the circle through the highest points (radius > 0.6 x width)
3 lancets = the rest below the oculus centre: split into the two lights at the axis, each light split at its
            apex (highest lancet point) into the jamb-side and mullion-side arcs
4 iterative nearest-circle reassignment (tolerance relative to window width), contiguity kept
Output format = fit_window.py (features A1 A2 O L1 L2 L3 L4 with idx, cx, cz, r, rms ...).

usage: python3 -I fit_window2.py <points.json> <out.json>
"""
import json
import sys

import numpy as np
from scipy.optimize import least_squares

sys.path.insert(0, sys.argv[0].rsplit("/", 1)[0])
from fit_window import circ3, contiguous, lsq  # noqa: E402

rng = np.random.default_rng(11)


def ransac(P, tol, score="n", iters=5000, rmin=0.2, rmax=12.0, must=None, cx=None, cxtol=None):
    best, bs, bi = None, -1, None
    for _ in range(iters):
        c = circ3(P[rng.choice(len(P), 3, replace=False)])
        if c is None or not rmin < c[2] < rmax:
            continue
        if cx is not None and abs(c[0] - cx) > cxtol:
            continue
        inl = np.abs(np.hypot(P[:, 0] - c[0], P[:, 1] - c[1]) - c[2]) < tol
        if must is not None and not inl[must]:
            continue
        inl = contiguous(P, c, inl, 40.0)
        if inl.sum() < 5:
            continue
        if score == "cover":
            a = np.sort(np.degrees(np.arctan2(P[inl, 1] - c[1], P[inl, 0] - c[0])))
            gaps = np.diff(np.r_[a, a[0] + 360])
            s = (360 - gaps.max()) * inl.sum()
        else:
            s = inl.sum()
        if s > bs:
            best, bs, bi = c, s, inl
    return best, bi


def group(P, seed):
    global rng
    rng = np.random.default_rng(seed)
    W = np.ptp(P[:, 0])
    tol, TOL = 0.005 * W, 0.012 * W
    lab = np.full(len(P), -1)
    C = {}
    # 1 oculus
    lowp = P[P[:, 1] < 0.3 * P[:, 1].max()]
    x_apex = 0.5 * (lowp[:, 0].min() + lowp[:, 0].max())   # window axis from the lower jambs
    c, inl = ransac(P, tol, "cover", rmin=0.15 * W, rmax=0.6 * W, cx=x_apex, cxtol=0.08 * W)
    C["O"], _ = lsq(P[inl], c)
    lab[inl] = 0
    xa = C["O"][0]
    free = lab < 0
    # 2 main arch halves: circle through the highest free point on each side
    for k, (nm, side) in enumerate((("A1", -1), ("A2", +1)), start=1):
        idx = np.flatnonzero(free & (np.sign(P[:, 0] - xa) == side))
        top = idx[np.argmax(P[idx, 1])]
        sub = np.flatnonzero(free & (np.sign(P[:, 0] - xa + side * 0.02 * W) == side))
        c, inl = ransac(P[sub], tol, "n", rmin=0.6 * W, rmax=3 * W, must=int(np.flatnonzero(sub == top)[0]))
        C[nm], _ = lsq(P[sub][inl], c)
        lab[sub[inl]] = k
        free = lab < 0
    # 3 lancets: below the oculus centre, split by light and at each light's apex
    dO = np.abs(np.hypot(P[:, 0] - C["O"][0], P[:, 1] - C["O"][1]) - C["O"][2])
    low = free & (P[:, 1] < C["O"][1]) & (dO > 0.025 * W)   # junction points near the oculus join later
    names = ["L1", "L2", "L3", "L4"]
    for li, side in enumerate((-1, +1)):
        idx = np.flatnonzero(low & (np.sign(P[:, 0] - xa) == side))
        if len(idx) < 8:
            continue
        ap = P[idx[np.argmax(P[idx, 1])], 0]
        for j, part in enumerate((idx[P[idx, 0] <= ap], idx[P[idx, 0] > ap])):
            nm = names[2 * li + j]
            if len(part) >= 3:
                c, inl = ransac(P[part], tol, "n", rmin=0.1 * W, rmax=2 * W, iters=2000)
                if c is not None:
                    C[nm], _ = lsq(P[part][inl], c)
    order = ["O", "A1", "A2", "L1", "L2", "L3", "L4"]
    order = [n for n in order if n in C]
    Cm = np.array([C[n] for n in order])
    C0 = Cm.copy()
    for _ in range(12):
        D = np.abs(np.hypot(P[:, None, 0] - Cm[None, :, 0], P[:, None, 1] - Cm[None, :, 1]) - Cm[None, :, 2])
        lab = D.argmin(axis=1)
        lab[D.min(axis=1) > TOL] = -1
        for j in range(len(Cm)):
            m = contiguous(P, Cm[j], lab == j, 40.0)
            lab[(lab == j) & ~m] = -1
        new = []
        for j in range(len(Cm)):
            c = lsq(P[lab == j], Cm[j])[0] if (lab == j).sum() >= 4 else Cm[j]
            ok = abs(c[2] - C0[j][2]) < 0.25 * C0[j][2] and np.hypot(c[0] - C0[j][0], c[1] - C0[j][1]) < 0.25 * C0[j][2]
            new.append(c if ok else Cm[j])
        Cm = np.array(new)
    return order, Cm, lab, W


def main(src, out):
    d = json.load(open(src))
    P = np.array([[p["x"], p["z"]] for p in d["points"]])
    best = None
    for seed in range(8):
        try:
            order, Cm, lab, W = group(P, seed)
        except Exception:
            continue
        cnt = [(lab == j).sum() for j in range(len(order))]
        key = (len(order) == 7 and min(cnt) >= 4, int((lab >= 0).sum()) - 0.5 * int(sum(c > 0.45 * len(P) for c in cnt)))
        if best is None or key > best[0]:
            best = (key, order, Cm, lab, W)
    _, order, Cm, lab, W = best
    feats = {}
    for j, nm in enumerate(order):
        Q = P[lab == j]
        c = Cm[j]
        res = np.hypot(Q[:, 0] - c[0], Q[:, 1] - c[1]) - c[2] if len(Q) else np.zeros(1)
        a = np.degrees(np.arctan2(Q[:, 1] - c[1], Q[:, 0] - c[0])) if len(Q) else np.zeros(1)
        feats[nm] = dict(cx=float(c[0]), cz=float(c[1]), r=float(c[2]), n=int(len(Q)),
                         xmean=float(Q[:, 0].mean()) if len(Q) else 0.0, zmax=float(Q[:, 1].max()) if len(Q) else 0.0,
                         rms_mm=float(1000 * np.sqrt(np.mean(res ** 2))), max_mm=float(1000 * np.abs(res).max()),
                         ang_span=float(np.ptp(np.unwrap(np.radians(np.sort(a)))) * 57.2958), idx=np.flatnonzero(lab == j).tolist())
    xa = 0.5 * (feats["A1"]["cx"] + feats["A2"]["cx"])
    res = dict(source=d["source"], px_per_m_used=d["px_per_m"], n_points=len(P), width_m=float(W), features=feats,
               axis_from_A_centres=xa, unassigned=int((lab < 0).sum()), complete=len(feats) == 7 and all(f["n"] >= 4 for f in feats.values()))
    json.dump(res, open(out, "w"), indent=1)
    print(f"{d['source'].replace('WotP_Reims_Cathedral_window_trace_', '')[:-4]:8} W {W:4.2f} m  pts {len(P):3d} un {res['unassigned']:2d}  "
          + " ".join(f"{n}:{f['n']}/{f['rms_mm']:.0f}" for n, f in feats.items()) + ("" if res["complete"] else "  INCOMPLETE"))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
