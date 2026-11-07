#!/usr/bin/env python3
"""
pages_bw.py - turn grayscale page scans into clean black-and-white.

Everything darker than the threshold becomes pure black (0,0,0).
Everything lighter becomes pure white (255,255,255) - or transparent
with --transparent.

Usage:
    python3 pages_bw.py INPUT OUTPUT [options]

INPUT may be a folder of images or a single image file.
OUTPUT is a folder; it is created if it does not exist.

Options:
    --threshold N     fixed cutoff 0-255 (default: automatic, per image)
    --local           adaptive threshold - use on scans with uneven
                      lighting, shadowed gutters or heavy paper toning
    --radius N        local-threshold window in pixels (default 30)
    --offset N        local-threshold sensitivity (default 10;
                      raise it to drop faint paper texture,
                      lower it to catch faint lines)
    --transparent     white background becomes transparent (RGBA PNG)
    --despeckle       median filter before thresholding, kills paper grain
    --thicken N       grow black lines by N pixels after thresholding;
                      use this if thin guide lines come out broken
    --suffix TEXT     add TEXT to each output filename before .png
    --quiet           only print errors
"""

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image, ImageChops, ImageFilter, ImageOps
except ImportError:
    sys.exit(
        "Pillow is not installed.\n"
        "Install it with:  sudo apt install python3-pil\n"
        "or:               pip install --break-system-packages pillow"
    )

EXTS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".jp2", ".webp"}


def otsu_threshold(hist):
    """Pick a global cutoff from a 256-bin histogram (Otsu's method)."""
    total = sum(hist)
    if total == 0:
        return 128
    sum_all = sum(i * h for i, h in enumerate(hist))
    sum_b = 0.0
    weight_b = 0
    best_var = -1.0
    thresh = 128
    for i in range(256):
        weight_b += hist[i]
        if weight_b == 0:
            continue
        weight_f = total - weight_b
        if weight_f == 0:
            break
        sum_b += i * hist[i]
        mean_b = sum_b / weight_b
        mean_f = (sum_all - sum_b) / weight_f
        var = weight_b * weight_f * (mean_b - mean_f) ** 2
        if var > best_var:
            best_var = var
            thresh = i
    return thresh


def binarize(gray, args):
    """Return an 'L' image containing only 0 (black) and 255 (white)."""
    if args.local:
        # Compare each pixel against the average of its neighbourhood.
        # blurred - gray is large wherever a pixel is darker than its
        # surroundings, i.e. wherever there is ink.
        blurred = gray.filter(ImageFilter.BoxBlur(args.radius))
        diff = ImageChops.subtract(blurred, gray)
        cutoff = args.offset
        return diff.point(lambda d: 0 if d > cutoff else 255, mode="L")

    if args.threshold is None:
        cutoff = otsu_threshold(gray.histogram())
    else:
        cutoff = args.threshold
    return gray.point(lambda p: 0 if p < cutoff else 255, mode="L")


def process(src, dst, args):
    with Image.open(src) as im:
        im.load()
        gray = ImageOps.grayscale(im)

    if args.despeckle:
        gray = gray.filter(ImageFilter.MedianFilter(3))

    bw = binarize(gray, args)

    if args.thicken:
        # MinFilter spreads the darkest value, growing black areas.
        for _ in range(args.thicken):
            bw = bw.filter(ImageFilter.MinFilter(3))

    if args.transparent:
        # alpha 255 where the pixel is black, 0 where it is white
        alpha = ImageChops.invert(bw)
        black = Image.new("L", bw.size, 0)
        out = Image.merge("RGBA", (black, black, black, alpha))
    else:
        out = bw.convert("RGB")

    out.save(dst, "PNG", optimize=True)


def main():
    p = argparse.ArgumentParser(add_help=True)
    p.add_argument("input")
    p.add_argument("output")
    p.add_argument("--threshold", type=int, default=None)
    p.add_argument("--local", action="store_true")
    p.add_argument("--radius", type=int, default=30)
    p.add_argument("--offset", type=int, default=10)
    p.add_argument("--transparent", action="store_true")
    p.add_argument("--despeckle", action="store_true")
    p.add_argument("--thicken", type=int, default=0)
    p.add_argument("--suffix", default="")
    p.add_argument("--quiet", action="store_true")
    args = p.parse_args()

    in_path = Path(args.input).expanduser()
    out_dir = Path(args.output).expanduser()

    if not in_path.exists():
        sys.exit(f"Input not found: {in_path}")

    if in_path.is_dir():
        files = sorted(
            f for f in in_path.iterdir()
            if f.is_file() and f.suffix.lower() in EXTS
        )
    else:
        files = [in_path]

    if not files:
        sys.exit(f"No images found in {in_path}")

    out_dir.mkdir(parents=True, exist_ok=True)

    done = 0
    failed = 0
    for i, src in enumerate(files, 1):
        dst = out_dir / f"{src.stem}{args.suffix}.png"
        try:
            process(src, dst, args)
            done += 1
            if not args.quiet:
                print(f"[{i}/{len(files)}] {src.name} -> {dst.name}")
        except Exception as e:
            failed += 1
            print(f"[{i}/{len(files)}] FAILED {src.name}: {e}", file=sys.stderr)

    print(f"\nDone. {done} written to {out_dir}" + (f", {failed} failed" if failed else ""))


if __name__ == "__main__":
    main()
