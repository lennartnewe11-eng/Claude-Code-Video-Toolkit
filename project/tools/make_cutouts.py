#!/usr/bin/env python3
"""Make collage cut-outs: remove background -> trim -> optional B/W -> PNG.

Usage:
  make_cutouts.py <in.jpg> <out.png> [--bw] [--sepia] [--sharp] [--model NAME]

--sharp   use alpha matting for cleaner, sharper edges (slower)
--model   rembg model (default isnet-general-use; u2net is the fallback)
"""
import sys
from rembg import remove, new_session
from PIL import Image, ImageOps

_SESS = {}


def session(name):
    if name not in _SESS:
        _SESS[name] = new_session(name)
    return _SESS[name]


def cutout(src, dst, bw=False, sepia=False, sharp=False, model="isnet-general-use"):
    img = Image.open(src).convert("RGBA")
    kw = {}
    if sharp:
        kw = dict(alpha_matting=True,
                  alpha_matting_foreground_threshold=240,
                  alpha_matting_background_threshold=15,
                  alpha_matting_erode_size=3)
    cut = remove(img, session=session(model), post_process_mask=True, **kw)

    bbox = cut.split()[3].getbbox()
    if bbox:
        cut = cut.crop(bbox)

    if bw or sepia:
        gray = ImageOps.autocontrast(ImageOps.grayscale(cut.convert("RGB")), cutoff=1)
        if sepia:
            toned = ImageOps.colorize(gray, black="#241a0c", white="#efe7d6", mid="#9a7d54")
        else:
            toned = gray.convert("RGB")
        toned = toned.convert("RGBA")
        toned.putalpha(cut.split()[3])
        cut = toned

    cut.save(dst)
    print(f"{dst}: {cut.size} {'bw' if bw else 'sepia' if sepia else 'color'}{' sharp' if sharp else ''}")


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    model = sys.argv[sys.argv.index("--model") + 1] if "--model" in sys.argv else "isnet-general-use"
    cutout(src, dst, "--bw" in sys.argv, "--sepia" in sys.argv, "--sharp" in sys.argv, model)
