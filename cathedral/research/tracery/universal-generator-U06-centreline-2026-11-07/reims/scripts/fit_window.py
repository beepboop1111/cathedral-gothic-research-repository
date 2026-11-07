#!/usr/bin/env python3
"""Group surveyed points into the 7 centreline arcs of a 2-light + oculus window and fit free circles.

Sequential RANSAC on the points (metres), then iterative reassignment to the nearest circle and a
geometric least-squares refit. Labels: A1/A2 = main arch (south/north half), O = oculus,
L1..L4 = lancet arcs from south to north.

usage: python3 -I fit_window.py <points.json> <out.json> [px_per_m_override]
"""
import json
import sys

import numpy as np
from scipy.optimize import least_squares

rng = np.random.default_rng(7)


def circ3(p):
    (x1, y1), (x2, y2), (x3, y3) = p
    a = np.array([[x2 - x1, y2 - y1], [x3 - x1, y3 - y1]])
    b = 0.5 * np.array([x2 ** 2 - x1 ** 2 + y2 ** 2 - y1 ** 2, x3 ** 2 - x1 ** 2 + y3 ** 2 - y1 ** 2])
    if abs(np.linalg.det(a)) < 1e-12:
        return None
    c = np.linalg.solve(a, b)
    return np.r_[c, np.hypot(*(p[0] - c))]


def lsq(P, c0):
    f = lambda c: np.hypot(P[:, 0] - c[0], P[:, 1] - c[1]) - c[2]
    r = least_squares(f, c0, method="lm")
    return r.x, f(r.x)


def contiguous(P, c, inl, gap_deg=30.0):
    """Keep the largest run of inliers that is contiguous along the circle (no angular gap > gap_deg)."""
    idx = np.flatnonzero(inl)
    if len(idx) < 2:
        return inl
    a = np.degrees(np.arctan2(P[idx, 1] - c[1], P[idx, 0] - c[0]))
    o = np.argsort(a)
    a, idx = a[o], idx[o]
    gaps = np.diff(np.r_[a, a[0] + 360.0])
    if gaps.max() <= gap_deg:
        return inl
    cut = np.flatnonzero(gaps > gap_deg)          # runs end after these positions
    runs, start = [], (cut[-1] + 1) % len(idx)
    for e in list(cut) + [None]:
        pass
    # walk the circle starting after the largest gap
    k0 = (int(np.argmax(gaps)) + 1) % len(idx)
    seq = np.r_[idx[k0:], idx[:k0]]
    g = np.r_[gaps[k0:], gaps[:k0]][:-1]
    best, cur = [seq[0]], [seq[0]]
    for j, gg in enumerate(g):
        if gg > gap_deg:
            cur = [seq[j + 1]]
        else:
            cur.append(seq[j + 1])
        if len(cur) > len(best):
            best = list(cur)
    out = np.zeros_like(inl)
    out[best] = True
    return out


def ransac(P, tol, iters=6000, rmax=6.0):
    best, bi = None, None
    for _ in range(iters):
        c = circ3(P[rng.choice(len(P), 3, replace=False)])
        if c is None or c[2] > rmax or c[2] < 0.3:
            continue
        inl = contiguous(P, c, np.abs(np.hypot(P[:, 0] - c[0], P[:, 1] - c[1]) - c[2]) < tol)
        if bi is None or inl.sum() > bi.sum():
            best, bi = c, inl
    return best, bi


def main(src, out, ppm=None):
    d = json.load(open(src))
    k = 1.0 if "marker_r4" in d else (d["px_per_m"] / ppm if ppm else 1.0)  # new extractions are in true metres
    P = np.array([[p["x"] * k, p["z"] * k] for p in d["points"]])
    rest = np.arange(len(P))
    circles = []
    while len(rest) >= 5 and len(circles) < 7:
        c, inl = ransac(P[rest], tol=0.010)
        if c is None or inl.sum() < 5:
            break
        c, _ = lsq(P[rest][inl], c)
        circles.append(c)
        rest = rest[~inl]
    # iterative reassignment + refit
    C = np.array(circles)
    TOL = 0.02
    for _ in range(10):
        D = np.abs(np.hypot(P[:, None, 0] - C[None, :, 0], P[:, None, 1] - C[None, :, 1]) - C[None, :, 2])
        lab = D.argmin(axis=1)
        lab[D.min(axis=1) > TOL] = -1
        for j in range(len(C)):
            m = contiguous(P, C[j], lab == j)
            lab[(lab == j) & ~m] = -1
        C = np.array([lsq(P[lab == j], C[j])[0] if (lab == j).sum() >= 4 else C[j] for j in range(len(C))])
    feats = []
    for j, c in enumerate(C):
        Q = P[lab == j]
        if len(Q) < 4:
            continue
        ang = np.degrees(np.arctan2(Q[:, 1] - c[1], Q[:, 0] - c[0]))
        res = np.hypot(Q[:, 0] - c[0], Q[:, 1] - c[1]) - c[2]
        feats.append(dict(cx=c[0], cz=c[1], r=c[2], n=len(Q), xmean=Q[:, 0].mean(), zmax=Q[:, 1].max(),
                          rms_mm=1000 * np.sqrt((res ** 2).mean()), max_mm=1000 * np.abs(res).max(),
                          ang_span=float(np.ptp(np.unwrap(np.radians(np.sort(ang)))) * 57.2958), idx=np.flatnonzero(lab == j).tolist()))
    # labels
    feats.sort(key=lambda f: -f["ang_span"])
    O = feats[0]                                    # widest angular extent = oculus
    others = feats[1:]
    others.sort(key=lambda f: -f["zmax"])
    A = sorted(others[:2], key=lambda f: f["xmean"])
    Ls = sorted(others[2:], key=lambda f: f["xmean"])
    named = {"A1": A[0], "A2": A[1], "O": O}
    named.update({f"L{i + 1}": f for i, f in enumerate(Ls)})
    unassigned = len(P) - sum(f["n"] for f in named.values())
    # origin: x relative to the south jamb point of A1? keep image x; report axis estimate too
    xa = 0.5 * (named["A1"]["cx"] + named["A2"]["cx"])
    res = dict(source=d["source"], px_per_m_used=ppm or d["px_per_m"], n_points=len(P),
               features={k: {kk: (round(v, 6) if isinstance(v, float) else v) for kk, v in f.items()} for k, f in named.items()},
               axis_from_A_centres=round(xa, 6), unassigned=unassigned)
    json.dump(res, open(out, "w"), indent=1)
    print(f"{d['source']}  px/m {res['px_per_m_used']:.1f}  points {len(P)}  features {len(named)}  unassigned {unassigned}")
    print(f"  {'feat':4} {'n':>3} {'R (m)':>8} {'centre z':>9} {'centre x-axis':>13} {'rms mm':>7} {'max mm':>7} {'span°':>6}")
    for kname in ["A1", "A2", "O", "L1", "L2", "L3", "L4"]:
        f = named.get(kname)
        if f:
            print(f"  {kname:4} {f['n']:3d} {f['r']:8.4f} {f['cz']:9.4f} {f['cx'] - xa:13.4f} {f['rms_mm']:7.2f} {f['max_mm']:7.2f} {f['ang_span']:6.1f}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else None)
