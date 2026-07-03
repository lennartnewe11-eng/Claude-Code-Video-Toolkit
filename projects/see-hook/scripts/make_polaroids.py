#!/usr/bin/env python3
"""Turn a list of source images into scattered 'polaroid' PNGs (white border +
rotation + soft drop shadow) for the Chunk-2 collage, in the style of the
reference shot (several small photos floating over a landscape)."""
import sys, pathlib, math
from PIL import Image, ImageOps, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parents[1]
C2 = ROOT/"main_assets"/"c2"
OUTD = ROOT/"build"/"c2_polaroids"; OUTD.mkdir(parents=True, exist_ok=True)

def polaroid(src, out, w=430, angle=-6.0, border=18, bottom=54):
    im = Image.open(src).convert("RGB")
    h = int(w*0.72)
    im = ImageOps.fit(im, (w, h), Image.LANCZOS)
    card = Image.new("RGB", (w+2*border, h+border+bottom), (247, 244, 238))  # warm white
    card.paste(im, (border, border))
    card = card.convert("RGBA")
    # rotate with transparent expand
    rot = card.rotate(angle, expand=True, resample=Image.BICUBIC)
    # soft drop shadow
    pad = 40
    canvas = Image.new("RGBA", (rot.width+2*pad, rot.height+2*pad), (0,0,0,0))
    sh = Image.new("RGBA", canvas.size, (0,0,0,0))
    shm = rot.split()[3].point(lambda a: int(a*0.5))
    black = Image.new("RGBA", rot.size, (0,0,0,255)); black.putalpha(shm)
    sh.paste(black, (pad+8, pad+14), black)
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    canvas = Image.alpha_composite(canvas, sh)
    canvas.paste(rot, (pad, pad), rot)
    canvas.save(out)
    return canvas.size

if __name__ == "__main__":
    # args: src1 src2 ... ; angles cycle for variety
    srcs = sys.argv[1:]
    angles = [-7, 5, -4, 8, -6, 3, -9, 6, -3, 7]
    widths = [440, 400, 470, 380, 430, 410, 450, 390]
    for i, s in enumerate(srcs):
        sz = polaroid(s, OUTD/f"pol_{i:02d}.png",
                      w=widths[i % len(widths)], angle=angles[i % len(angles)])
        print(f"  pol_{i:02d}.png  {sz}  <- {pathlib.Path(s).name}")
    print(f"DONE {len(srcs)} polaroids -> {OUTD}")
