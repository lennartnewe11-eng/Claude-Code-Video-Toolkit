#!/usr/bin/env python3
"""Turn a list of source images into scattered 'polaroid' PNGs (white border +
rotation + soft drop shadow) for the Chunk-2 collage, in the style of the
reference shot (several small photos floating over a landscape)."""
import sys, pathlib, math
from PIL import Image, ImageOps, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parents[1]
C2 = ROOT/"main_assets"/"c2"
OUTD = ROOT/"build"/"c2_polaroids"; OUTD.mkdir(parents=True, exist_ok=True)

def polaroid(src, out, w=250, angle=0.0, border=6):
    """Small photo with a THIN even white border and a faint shadow, upright
    (no tilt) -- matches the reference collage."""
    im = Image.open(src).convert("RGB")
    h = int(w*0.70)
    im = ImageOps.fit(im, (w, h), Image.LANCZOS)
    card = Image.new("RGB", (w+2*border, h+2*border), (250, 248, 244))  # subtle white
    card.paste(im, (border, border))
    card = card.convert("RGBA")
    rot = card.rotate(angle, expand=True, resample=Image.BICUBIC) if angle else card
    # faint soft drop shadow so it lifts off the landscape a touch
    pad = 26
    canvas = Image.new("RGBA", (rot.width+2*pad, rot.height+2*pad), (0,0,0,0))
    sh = Image.new("RGBA", canvas.size, (0,0,0,0))
    shm = rot.split()[3].point(lambda a: int(a*0.34))
    black = Image.new("RGBA", rot.size, (0,0,0,255)); black.putalpha(shm)
    sh.paste(black, (pad+5, pad+8), black)
    sh = sh.filter(ImageFilter.GaussianBlur(9))
    canvas = Image.alpha_composite(canvas, sh)
    canvas.paste(rot, (pad, pad), rot)
    canvas.save(out)
    return canvas.size

if __name__ == "__main__":
    # args: src1 src2 ...  -- all small, upright, subtle frame (slight size variety)
    srcs = sys.argv[1:]
    widths = [252, 240, 262, 236, 250, 244, 258, 246]
    for i, s in enumerate(srcs):
        sz = polaroid(s, OUTD/f"pol_{i:02d}.png", w=widths[i % len(widths)], angle=0.0)
        print(f"  pol_{i:02d}.png  {sz}  <- {pathlib.Path(s).name}")
    print(f"DONE {len(srcs)} polaroids -> {OUTD}")
