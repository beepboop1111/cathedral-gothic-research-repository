#!/usr/bin/env python3
"""Extract surveyed points from a Windows-on-the-Past trace image (Hillson, ADS 2024).

Each surveyed point is drawn as a circle-with-cross marker. This finds every marker, fits its ring
(robust circle fit, full resolution) and returns the centre in metres:
  x = (col - col0) / px_per_m   (image left = south)
  z = (row_base - row) / px_per_m   (height above the dashed impost line)
px_per_m comes from the 1 m scale bar; row_base from the dashed line.

usage: python3 -I extract_markers.py <trace.jpg> <out.json>
"""
import json
import sys

import numpy as np
from PIL import Image
from scipy import ndimage, signal

Image.MAX_IMAGE_PIXELS = None


def longest_run(row):
    """Length and start of the longest run of True in a 1-D bool array."""
    if not row.any():
        return 0, 0
    d = np.diff(np.r_[0, row.astype(np.int8), 0])
    s, e = np.flatnonzero(d == 1), np.flatnonzero(d == -1)
    k = int(np.argmax(e - s))
    return int(e[k] - s[k]), int(s[k])


def kasa(x, y):
    A = np.c_[x, y, np.ones_like(x)]
    b = x * x + y * y
    c, *_ = np.linalg.lstsq(A, b, rcond=None)
    cx, cy = c[0] / 2, c[1] / 2
    return cx, cy, float(np.sqrt(c[2] + cx * cx + cy * cy))


def main(src, out):
    im = Image.open(src)
    W, H = im.size
    im.draft("L", (W, H))
    g = np.asarray(im.convert("L"))
    ink = g < 128
    del g

    # --- impost (dashed) line: row band with the most separate ink runs, 85-94 % of the height
    lo, hi = int(0.85 * H), int(0.94 * H)
    runs = np.array([np.count_nonzero(np.diff(ink[r].astype(np.int8)) == 1) for r in range(lo, hi)])
    r0 = lo + int(np.argmax(runs))
    band = np.arange(r0 - 30, r0 + 31)
    cnt = ink[band].sum(axis=1).astype(float)
    sel = cnt > 0.5 * cnt.max()
    row_base = float((band[sel] * cnt[sel]).sum() / cnt[sel].sum())

    # --- 1 m scale bar: longest horizontal ink run in the bottom 6 %
    best = []
    for r in range(int(0.94 * H), H):
        n, s = longest_run(ink[r])
        best.append((n, s, r))
    nmax = max(b[0] for b in best)
    rows = [b for b in best if b[0] > 0.95 * nmax]
    px_per_m = float(np.median([b[0] for b in rows]))
    bar = dict(length_px=px_per_m, rows=len(rows), start_col=int(np.median([b[1] for b in rows])))

    # --- marker detection at 1/4 scale (template = ring + cross)
    f = 4
    h4, w4 = H // f, W // f
    ink4 = ink[: h4 * f, : w4 * f].reshape(h4, f, w4, f).mean(axis=(1, 3))
    R4 = 38.75
    rr = int(R4) + 4
    yy, xx = np.mgrid[-rr : rr + 1, -rr : rr + 1]
    rad = np.hypot(xx, yy)
    T = (np.abs(rad - R4) <= 1.2) | (((np.abs(xx) <= 0.8) | (np.abs(yy) <= 0.8)) & (rad <= R4))
    T = T.astype(float)
    score = signal.fftconvolve(ink4, T[::-1, ::-1], mode="same") / T.sum()
    # exclude the fit table (top right), header and footer
    score[: int(0.09 * h4), int(0.66 * w4) :] = 0
    score[: int(0.035 * h4), :] = 0
    score[int(0.935 * h4) :, :] = 0
    peaks = (score == ndimage.maximum_filter(score, size=41)) & (score > 0.45 * score.max())
    pr, pc = np.nonzero(peaks)

    # --- full-resolution refinement: robust ring fit
    Rf = R4 * f
    pts, rej = [], []
    for r4, c4 in zip(pr, pc):
        cy, cx = r4 * f + 1.5, c4 * f + 1.5
        y0, x0 = int(cy - Rf - 60), int(cx - Rf - 60)
        win = ink[max(0, y0) : y0 + int(2 * Rf + 121), max(0, x0) : x0 + int(2 * Rf + 121)]
        ys, xs = np.nonzero(win)
        ys = ys + max(0, y0)
        xs = xs + max(0, x0)
        ok = True
        for it in range(4):
            d = np.hypot(xs - cx, ys - cy)
            m = np.abs(d - Rf) < (0.25 * Rf if it == 0 else 4.0)
            if m.sum() < 200:
                ok = False
                break
            cx, cy, Rf_i = kasa(xs[m].astype(float), ys[m].astype(float))
        if not ok:
            rej.append([int(c4 * f), int(r4 * f), "few ring pixels"])
            continue
        # cross check: ink along the horizontal and vertical lines through the centre
        ic, ir = int(round(cx)), int(round(cy))
        span = np.arange(-int(0.8 * Rf_i), int(0.8 * Rf_i) + 1)
        hcov = ink[ir - 3 : ir + 4, ic + span].any(axis=0).mean()
        vcov = ink[ir + span, ic - 3 : ic + 4].any(axis=1).mean()
        if not (hcov > 0.9 and vcov > 0.9 and abs(Rf_i - Rf) < 12):
            rej.append([round(cx, 1), round(cy, 1), f"cross {hcov:.2f}/{vcov:.2f} R {Rf_i:.1f}"])
            continue
        pts.append(dict(col=round(cx, 2), row=round(cy, 2), ring_r=round(Rf_i, 2),
                        x=(cx) / px_per_m, z=(row_base - cy) / px_per_m))
    res = dict(source=src.split("/")[-1], image=[W, H], px_per_m=px_per_m, scale_bar=bar,
               row_base=row_base, n_points=len(pts), rejected=rej,
               ring_r_px=dict(median=float(np.median([p["ring_r"] for p in pts])),
                              min=float(min(p["ring_r"] for p in pts)), max=float(max(p["ring_r"] for p in pts))),
               points=pts)
    json.dump(res, open(out, "w"), indent=1)
    print(f"{res['source']}: {len(pts)} markers, {len(rej)} rejected, px/m {px_per_m:.1f} "
          f"(150 dpi 1:1 = 5905.5), base row {row_base:.1f}, ring r {res['ring_r_px']}")
    for r in rej:
        print("   rejected", r)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
