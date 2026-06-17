#!/usr/bin/env python3
"""Make collage cut-outs: remove background -> trim -> optional B/W -> PNG.

Usage:
  make_cutouts.py <in.jpg> <out.png> [--bw] [--sepia]

Writes a tightly-cropped transparent PNG ready for the collage style.
"""
import sys
from rembg import remove
from PIL import Image, ImageOps


def main():
    src, dst = sys.argv[1], sys.argv[2]
    bw = "--bw" in sys.argv
    sepia = "--sepia" in sys.argv

    img = Image.open(src).convert("RGBA")
    cut = remove(img)  # RGBA, transparent background

    # trim to the non-transparent bounding box
    bbox = cut.split()[3].getbbox()
    if bbox:
        cut = cut.crop(bbox)

    if bw or sepia:
        rgb = cut.convert("RGB")
        gray = ImageOps.grayscale(rgb)
        gray = ImageOps.autocontrast(gray, cutoff=1)
        if sepia:
            toned = ImageOps.colorize(gray, black="#241a0c", white="#efe7d6",
                                      mid="#9a7d54")
        else:
            toned = gray.convert("RGB")
        toned = toned.convert("RGBA")
        toned.putalpha(cut.split()[3])  # keep original alpha
        cut = toned

    cut.save(dst)
    print(f"{dst}: {cut.size} {'bw' if bw else 'sepia' if sepia else 'color'}")


if __name__ == "__main__":
    main()
