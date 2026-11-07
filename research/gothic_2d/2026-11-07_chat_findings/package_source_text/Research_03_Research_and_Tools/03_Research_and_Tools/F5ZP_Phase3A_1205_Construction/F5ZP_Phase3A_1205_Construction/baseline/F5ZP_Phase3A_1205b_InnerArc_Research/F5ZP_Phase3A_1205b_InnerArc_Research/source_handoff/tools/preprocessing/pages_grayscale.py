#!/usr/bin/env python3
"""Convert raw page scans (including archive.org JP2s renamed .png, which
many tools can't open) into clean grayscale PNGs. No masking, no block
mapping — just readable gray pages.

usage: pages_grayscale.py INDIR OUTDIR [--width N] [--no-normalize]

  --width N       downscale to N px wide (default: keep original size)
  --no-normalize  skip the per-page contrast stretch (normalize maps each
                  page's ink to black and paper to white, which makes
                  faded scans much easier to read)

deps: pip install pillow numpy
"""
import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("indir")
    ap.add_argument("outdir")
    ap.add_argument("--width", type=int, default=0,
                    help="output width in px (0 = keep original size)")
    ap.add_argument("--no-normalize", action="store_true")
    args = ap.parse_args()

    indir, outdir = Path(args.indir), Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    exts = {".png", ".jp2", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}
    files = sorted(f for f in indir.iterdir()
                   if f.is_file() and f.suffix.lower() in exts)
    if not files:
        sys.exit(f"no images found in {indir}")

    done = 0
    for f in files:
        try:
            im = Image.open(f).convert("L")   # decodes by content, not extension
        except Exception as e:
            print(f"SKIP {f.name}: {e}")
            continue

        if args.width > 0 and args.width < im.width:
            h = round(im.height * args.width / im.width)
            im = im.resize((args.width, h), Image.LANCZOS)

        if not args.no_normalize:
            g = np.asarray(im).astype(np.float64)
            p1, p99 = np.percentile(g, [1, 99])
            g = np.clip((g - p1) * 255.0 / max(p99 - p1, 1.0), 0, 255)
            im = Image.fromarray(g.astype(np.uint8))

        out = outdir / f"{f.stem}.png"
        im.save(out)
        done += 1
        print(f"{f.name} -> {out.name}  ({im.width}x{im.height})")

    print(f"\n{done}/{len(files)} pages converted into {outdir}")


if __name__ == "__main__":
    main()
