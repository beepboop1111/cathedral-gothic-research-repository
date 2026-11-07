#!/usr/bin/env python3
"""
fill_hatching.py - turn hatched (line-shaded) moulding sections into solid
black silhouettes.

Engraved section drawings shade stone with parallel 45-degree hatch lines.
Simply filling enclosed areas does not work, because the hatch lines usually
stop a pixel or two short of the outline, leaving a channel through which the
white background escapes into the figure.

This script closes the image ACROSS the hatch direction first, which welds the
hatch lines into one solid mass and seals the escape channel, then fills any
remaining enclosed white. Closing along a single direction is much gentler
than a round kernel, so cusps, quirks and small hollows survive.

Usage:
    python3 fill_hatching.py INPUT OUTPUT [options]

INPUT may be a folder of images or a single image file.
OUTPUT is a folder; it is created if it does not exist.

Options:
    --angle N         hatch angle in degrees (default: detected per image)
    --length N        closing span in pixels (default: measured per image)
                      raise it if hatch remains, lower it if small hollows
                      are getting closed up
    --disk            use a round kernel instead of a directional one;
                      try this on scans with hatch in two directions
    --smooth N        smooth the outline by N pixels afterwards; removes the
                      sawtooth where hatch lines overshoot the outline.
                      Warning: also erases strokes thinner than 2N pixels,
                      such as dashed dimension lines and small lettering
    --min-area N      drop black blobs smaller than N pixels (default 40)
    --transparent     white background becomes transparent (RGBA PNG)
    --no-fill         only merge the hatch, skip the enclosed-area fill
    --report          print the detected angle and span for each image
    --quiet           only print errors
"""

import argparse
import sys
from pathlib import Path

import numpy as np

try:
    from PIL import Image
    from scipy import ndimage as ndi
    from skimage.morphology import disk, closing, opening
except ImportError as e:
    sys.exit(
        f"Missing dependency ({e.name}).\n"
        "Install with:  sudo apt install python3-pil python3-scipy python3-skimage\n"
        "or:            pip install --break-system-packages pillow scipy scikit-image"
    )

EXTS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".jp2", ".webp"}
# The frame around a plate encloses the whole page. Refuse to fill any
# component whose fill would swallow more than this fraction of the image.
FRAME_GUARD = 0.15


def line_footprint(length, angle_deg):
    """A one-pixel-wide line kernel of the given length and angle."""
    n = max(3, int(length) | 1)  # force odd
    fp = np.zeros((n, n), bool)
    c = (n - 1) / 2.0
    th = np.deg2rad(angle_deg)
    for t in np.linspace(-c, c, n * 4):
        y = int(round(c - t * np.sin(th)))
        x = int(round(c + t * np.cos(th)))
        if 0 <= y < n and 0 <= x < n:
            fp[y, x] = True
    return fp


def detect_angle(ink):
    """Find the hatch direction: the angle whose line opening keeps most ink."""
    small = ink[::2, ::2]
    best_angle, best_score = 45, -1
    for ang in range(0, 180, 15):
        score = opening(small, line_footprint(15, ang)).sum()
        if score > best_score:
            best_score, best_angle = score, ang
    return best_angle


def detect_spacing(ink):
    """Estimate the white gap between neighbouring hatch lines."""
    runs = []
    rows = np.linspace(0, ink.shape[0] - 1, 400).astype(int)
    for y in rows:
        row = ink[y]
        edges = np.flatnonzero(np.diff(row.astype(np.int8)))
        if len(edges) > 4:
            d = np.diff(edges)
            runs.extend(d[d < 60])
    if not runs:
        return 13
    return int(np.percentile(runs, 90) * 1.4) + 3


def solidify(ink, footprint, do_fill):
    merged = closing(ink, footprint)
    if not do_fill:
        return merged
    lab, n = ndi.label(merged)
    out = np.zeros_like(merged)
    guard = FRAME_GUARD * merged.size
    for sl, i in zip(ndi.find_objects(lab), range(1, n + 1)):
        comp = lab[sl] == i
        filled = ndi.binary_fill_holes(comp)
        if filled.sum() - comp.sum() > guard:
            filled = comp  # this is the plate frame, not a section
        out[sl] |= filled
    return out


def process(src, dst, args):
    a = np.array(Image.open(src).convert("L"))
    ink = a < 128

    angle = args.angle if args.angle is not None else detect_angle(ink)
    length = args.length if args.length is not None else detect_spacing(ink)

    if args.disk:
        fp = disk(max(2, length // 2))
    else:
        fp = line_footprint(length, angle + 90)  # close ACROSS the hatch

    solid = solidify(ink, fp, not args.no_fill)

    if args.smooth:
        solid = opening(solid, disk(args.smooth))
        solid = closing(solid, disk(args.smooth))

    if args.min_area:
        # Equivalent to remove_small_objects, written out so it does not
        # break when scikit-image renames its arguments.
        lab_s, _ = ndi.label(solid)
        sizes = np.bincount(lab_s.ravel())
        too_small = np.flatnonzero(sizes < args.min_area)
        solid = solid & ~np.isin(lab_s, too_small)

    if args.transparent:
        alpha = (solid * 255).astype(np.uint8)
        black = np.zeros_like(alpha)
        out = Image.fromarray(np.dstack([black, black, black, alpha]), "RGBA")
    else:
        out = Image.fromarray((~solid * np.uint8(255)).astype(np.uint8), "L")
    out.save(dst, "PNG", optimize=True)
    return angle, length


def main():
    p = argparse.ArgumentParser(add_help=True)
    p.add_argument("input")
    p.add_argument("output")
    p.add_argument("--angle", type=float, default=None)
    p.add_argument("--length", type=int, default=None)
    p.add_argument("--disk", action="store_true")
    p.add_argument("--smooth", type=int, default=0)
    p.add_argument("--min-area", type=int, default=40)
    p.add_argument("--transparent", action="store_true")
    p.add_argument("--no-fill", action="store_true")
    p.add_argument("--report", action="store_true")
    p.add_argument("--quiet", action="store_true")
    args = p.parse_args()

    in_path = Path(args.input).expanduser()
    out_dir = Path(args.output).expanduser()
    if not in_path.exists():
        sys.exit(f"Input not found: {in_path}")

    if in_path.is_dir():
        files = sorted(f for f in in_path.iterdir()
                       if f.is_file() and f.suffix.lower() in EXTS)
    else:
        files = [in_path]
    if not files:
        sys.exit(f"No images found in {in_path}")

    out_dir.mkdir(parents=True, exist_ok=True)

    done = failed = 0
    for i, src in enumerate(files, 1):
        dst = out_dir / f"{src.stem}.png"
        try:
            angle, length = process(src, dst, args)
            done += 1
            if not args.quiet:
                extra = f"  (hatch {angle:g} deg, span {length}px)" if args.report else ""
                print(f"[{i}/{len(files)}] {src.name} -> {dst.name}{extra}")
        except Exception as e:
            failed += 1
            print(f"[{i}/{len(files)}] FAILED {src.name}: {e}", file=sys.stderr)

    print(f"\nDone. {done} written to {out_dir}" + (f", {failed} failed" if failed else ""))


if __name__ == "__main__":
    main()
