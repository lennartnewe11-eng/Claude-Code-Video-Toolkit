#!/usr/bin/env python3
"""Generate a flat-cartoon animation for the bucket metaphor:
two buckets in the rain -- the sealed one (left) fills up, the one with a hole
in the bottom (right) never does. Renders a PNG sequence -> build/c2_buckets."""
import pathlib, random, math
from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUTD = ROOT/"build"/"c2_buckets"; OUTD.mkdir(parents=True, exist_ok=True)
W, H, FPS = 1920, 1080, 30
DUR = 6.3
N = int(DUR*FPS)

SKY   = (214, 226, 232)     # soft overcast paper-blue
GROUND= (196, 204, 190)
BUCKET= (74, 84, 96)        # slate
BUCKET2=(96, 106, 118)
WATER = (58, 150, 196)      # clear blue
WATER2= (92, 178, 214)
RAIN  = (120, 140, 158)
INK   = (40, 46, 54)

random.seed(7)
# rain streaks: (x, y0, len, speed, phase)
RAINDROPS = [(random.randint(0, W), random.randint(-H, H),
              random.randint(26, 46), random.uniform(16, 26), random.random())
             for _ in range(150)]

def bucket_poly(cx, top, w_top, w_bot, ht):
    return [(cx-w_top/2, top), (cx+w_top/2, top),
            (cx+w_bot/2, top+ht), (cx-w_bot/2, top+ht)]

def draw_bucket(d, cx, top, ht, fill_frac, leak=False):
    wt, wb = 260, 190
    # water first (clipped inside), then bucket walls over it
    if fill_frac > 0.01:
        wl = top + ht*(1-fill_frac)
        # trapezoid slice from wl..top+ht
        f = (wl-top)/ht
        wtop = wt + (wb-wt)*f
        d.polygon([(cx-wtop/2, wl),(cx+wtop/2, wl),
                   (cx+wb/2, top+ht),(cx-wb/2, top+ht)], fill=WATER)
        d.line([(cx-wtop/2, wl),(cx+wtop/2, wl)], fill=WATER2, width=6)
    # bucket body outline
    d.polygon(bucket_poly(cx, top, wt, wb, ht), outline=INK, width=9)
    # rim ellipse
    d.ellipse([cx-wt/2, top-20, cx+wt/2, top+20], outline=INK, width=9, fill=None)
    # handle
    d.arc([cx-wt/2, top-70, cx+wt/2, top+40], 200, 340, fill=INK, width=7)
    if leak:
        # hole + drip
        d.ellipse([cx-14, top+ht-10, cx+14, top+ht+14], fill=INK)

def draw(i):
    t = i/FPS
    im = Image.new("RGB", (W, H), SKY)
    d = ImageDraw.Draw(im, "RGBA")
    # ground
    gy = 760
    d.rectangle([0, gy, W, H], fill=GROUND)
    d.line([(0, gy),(W, gy)], fill=INK, width=6)
    # rain
    for (x, y0, ln, sp, ph) in RAINDROPS:
        y = (y0 + t*sp*FPS) % (H+ln) - ln
        d.line([(x, y),(x-6, y+ln)], fill=RAIN+(180,), width=3)
    top, ht = 470, 290
    lx, rx = 660, 1300
    # left sealed bucket: fills up smoothly to ~0.92
    lf = min(0.92, (t/ (DUR*0.8))*0.92)
    draw_bucket(d, lx, top, ht, lf, leak=False)
    # right holed bucket: water tries but leaks -> stays very low, wobbling
    rf = 0.10 + 0.05*math.sin(t*4)
    rf = max(0.0, rf*min(1.0, t/0.8))
    draw_bucket(d, rx, top, ht, rf, leak=True)
    # leak stream + puddle under right bucket
    if t > 0.6:
        for k in range(5):
            yy = top+ht+18 + ((t*520 + k*40) % 120)
            d.line([(rx, yy),(rx-3, yy+16)], fill=WATER, width=5)
        pw = min(150, (t-0.6)*60)
        d.ellipse([rx-pw, gy-10, rx+pw, gy+16], fill=WATER+(200,))
    # tiny labels under each
    return im

if __name__ == "__main__":
    for i in range(N):
        draw(i).save(OUTD/f"b_{i:04d}.png")
    print(f"DONE {N} frames -> {OUTD}")
