"""Direct general-rule fit: seed from good windows, assign each marker to the nearest arc of the rule
(side-restricted), robust least squares, iterate. Fixes mislabelled/incomplete groupings.
usage: python3 -I icp_gen.py <windows.txt> <batch2.json> <out.json>"""
import json, math, sys
import numpy as np
from scipy.optimize import least_squares
sys.path.insert(0, sys.argv[0].rsplit("/", 1)[0])
K = ["xa", "x0", "yA", "f", "sL", "g", "s", "rL", "zO"]
def gen(t):
    xa, x0, yA, f, sL, g, s, rL, zO = t
    rA = f * x0; eA = rA - x0 / 2; zA = yA - math.sqrt(max(rA * rA - eA * eA, 1e-12))
    jS, mS, mN, jN = xa - g / 2 - sL, xa - g / 2, xa + g / 2, xa + g / 2 + sL
    c = {"A1": (xa + eA, zA, rA), "A2": (xa - eA, zA, rA), "L1": (jS + rL, s, rL), "L2": (mS - rL, s, rL),
         "L3": (mN + rL, s, rL), "L4": (jN - rL, s, rL)}
    c["O"] = (xa, zO, math.hypot(xa - c["L2"][0], zO - s) - rL)
    return c, (jS, mS, mN, jN, zA)
def assign(t, P, tol):
    c, (jS, mS, mN, jN, zA) = gen(t); xa, s = t[0], t[6]
    lab = []
    for x, z in P:
        cand = ["O"] + (["A1"] if x <= xa else ["A2"])
        if z >= s - 0.05:
            if jS - .05 <= x <= jS + (mS - jS) / 2: cand.append("L1")
            elif x <= mS + .05: cand.append("L2")
            if mN - .05 <= x <= mN + (jN - mN) / 2: cand.append("L3")
            elif mN + (jN - mN) / 2 <= x <= jN + .05: cand.append("L4")
        d = {n: abs(math.hypot(x - c[n][0], z - c[n][1]) - c[n][2]) for n in cand}
        n = min(d, key=d.get); lab.append(n if d[n] <= tol else None)
    return lab
def res(t, P, lab):
    c, _ = gen(t)
    return np.array([math.hypot(x - c[n][0], z - c[n][1]) - c[n][2] for (x, z), n in zip(P, lab) if n])
wins, B, out = open(sys.argv[1]).read().split(), json.load(open(sys.argv[2])), sys.argv[3]
GOOD = [w for w in B if B[w].get("rms", {}).get("gen") is not None and B[w]["rms"]["gen"] < 30]
R = {}
for w in wins:
    pj = json.load(open(f"out/pts_{w}.json")); k = 1.0 if "marker_r4" in pj else pj["px_per_m"] / 5905.5
    P = np.array([[p["x"] * k, p["z"] * k] for p in pj["points"]])
    fam = [g for g in GOOD if g[0] == w[0]] if len(sys.argv) < 5 else GOOD
    best = None
    for sd in fam:
        t0 = np.array([B[sd]["gen"][q] for q in K])
        # shift seed: axis to the point cloud centre, apex to its top
        t0[0] += 0.5 * (P[:, 0].min() + P[:, 0].max()) - (t0[0])
        dz = P[:, 1].max() - t0[2]; t0[2] += dz; t0[6] += dz; t0[8] += dz
        t = t0.copy()
        for tol in (0.25, 0.15, 0.08, 0.06, 0.06, 0.06):
            lab = assign(t, P, tol)
            if sum(l is not None for l in lab) < 12: break
            try:
                t = least_squares(lambda q: res(q, P, lab), t, loss="soft_l1", f_scale=0.02).x
            except Exception:
                break
        lab = assign(t, P, 0.06); r = res(t, P, lab)
        if len(r) < 12: continue
        feats = {n: lab.count(n) for n in ("A1", "A2", "O", "L1", "L2", "L3", "L4")}
        score = (min(feats.values()) >= 3, len(r), -float(np.sqrt(np.mean(r ** 2))))
        if best is None or score > best[0]: best = (score, t, r, feats, sd)
    if best is None:
        R[w] = dict(ok=False); print(w, "no fit"); continue
    (_, t, r, feats, sd) = best; c, _ = gen(t)
    rms = float(1000 * np.sqrt(np.mean(r ** 2)))
    R[w] = dict(ok=min(feats.values()) >= 3 and rms < 30, gen=dict(zip(K, map(float, t))), rms_mm=rms, inliers=len(r), points=len(P),
                features=feats, seed=sd, rO=float(c["O"][2]), rA=float(t[3] * t[1]))
    print(f"{w:7} {'OK ' if R[w]['ok'] else 'BAD'} rms {rms:5.1f} inl {len(r)}/{len(P)} x0 {t[1]:.3f} yA-s {t[2]-t[6]:.3f} rA {t[3]*t[1]:.3f} "
          f"lights {2*t[4]+t[5]:.3f} g {1000*t[5]:.0f} rL {t[7]:.3f} kO {t[8]-t[6]:.3f} rO {c['O'][2]:.3f} {feats}")
json.dump(R, open(out, "w"), indent=1)
