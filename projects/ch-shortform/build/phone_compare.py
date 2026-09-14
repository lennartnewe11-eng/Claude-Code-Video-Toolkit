#!/usr/bin/env python3
"""Der Vergleichsshot: iPhone 1 und iPhone 16 Pro Max, beide gezeichnet und
beide animiert. Keine Scroll-Animation -- animiert wird der Groessenvergleich
selbst.

Ablauf ueber vier Beats:
  Beat 0  das Ur-iPhone baut sich auf
  Beat 1  der 16er schnappt hart auf Beat um es herum auf,
          das Ur-iPhone bleibt als Umriss stehen
  Beat 2  beide Beschriftungen laufen ein
  Beat 3  Halten, Massband zwischen den beiden Hoehen
"""
import os, subprocess, sys, math
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from phones import (PHONES, PX_PER_MM, BW, BH, CX, CY,
                    WHITE, BODY, SCREEN, LABEL, SUB, FONT, FONT_M)

FPS, BEAT, SS = 60, 0.3715, 2
OLD, NEW = PHONES[0], PHONES[-1]
ACCENT = (200, 52, 26)          # dasselbe Rot wie auf der Ansichtsseite

def ease_out(x):  return 1 - pow(1 - max(0.0, min(1.0, x)), 3)

def device(d, s, scale=1.0):
    """Masse in Pixeln (bereits ueberabgetastet)."""
    _, _, h_mm, w_mm, _, rad, bez, home, notch = d
    return (h_mm*PX_PER_MM*s*scale, w_mm*PX_PER_MM*s*scale,
            rad*PX_PER_MM*s*scale, bez*PX_PER_MM*s*scale, home, notch)

def draw_body(dr, d, s, scale, fill=None, outline=None, width=0, screen=False):
    h, w, r, b, home, notch = device(d, s, scale)
    cx, cy = CX*s, CY*s
    box = [cx-w/2, cy-h/2, cx+w/2, cy+h/2]
    if h < 2 or w < 2: return box
    dr.rounded_rectangle(box, radius=max(1, r), fill=fill, outline=outline, width=width)
    if screen and h > 40:
        top = b + (11*PX_PER_MM*s*scale if home else b)
        bot = b + (13*PX_PER_MM*s*scale if home else b)
        sb = [box[0]+b, box[1]+top, box[2]-b, box[3]-bot]
        if sb[2]-sb[0] > 4 and sb[3]-sb[1] > 4:
            dr.rounded_rectangle(sb, radius=max(1, r-b*0.8), fill=SCREEN)
        if home:
            hr = 5.5*PX_PER_MM*s*scale
            hy = box[3] - 7.0*PX_PER_MM*s*scale
            dr.ellipse([cx-hr, hy-hr, cx+hr, hy+hr], outline=(70,72,78),
                       width=max(1, int(2*s)))
        if notch:
            nw, nh = 26*PX_PER_MM*s*scale, 6.5*PX_PER_MM*s*scale
            dr.rounded_rectangle([cx-nw/2, sb[1]-nh*0.1, cx+nw/2, sb[1]+nh],
                                 nh/2, fill=BODY)
    return box

def frame(i, n, out):
    t = i / FPS
    b = t / BEAT                                    # Position in Beats
    im = Image.new("RGB", (BW*SS, BH*SS), WHITE)
    d = ImageDraw.Draw(im)
    s = SS

    # --- Beat 0: Ur-iPhone baut sich auf ---------------------------------
    g_old = ease_out(b / 0.8)
    # --- Beat 1: der 16er schnappt auf -----------------------------------
    g_new = ease_out((b - 1.0) / 0.32) if b >= 1.0 else 0.0

    if g_new > 0.01:
        draw_body(d, NEW, s, g_new, fill=BODY, screen=g_new > 0.6)
    if g_old > 0.01:
        if g_new > 0.35:                            # innen nur noch Umriss
            draw_body(d, OLD, s, 1.0, outline=ACCENT,
                      width=max(3, int(3.0*s)))
        else:
            draw_body(d, OLD, s, g_old, fill=BODY, screen=g_old > 0.6)

    # --- Beat 3: Massband zwischen den beiden Hoehen ---------------------
    if b >= 3.0:
        p = ease_out((b - 3.0) / 0.5)
        ho, _, _, _, _, _ = device(OLD, s); hn, wn, _, _, _, _ = device(NEW, s)
        x = CX*s + wn/2 + 26*s
        y0, y1 = CY*s - hn/2, CY*s + hn/2
        d.line([x, y0, x, y0 + (y1-y0)*p], fill=ACCENT, width=max(2, int(2*s)))
        for yy in (y0, y1):
            if p > 0.9: d.line([x-8*s, yy, x+8*s, yy], fill=ACCENT, width=max(2,int(2*s)))
        yo0, yo1 = CY*s - ho/2, CY*s + ho/2
        xo = CX*s - wn/2 - 26*s
        d.line([xo, yo0, xo, yo0 + (yo1-yo0)*p], fill=ACCENT, width=max(2, int(2*s)))
        if p > 0.9:
            for yy in (yo0, yo1):
                d.line([xo-8*s, yy, xo+8*s, yy], fill=ACCENT, width=max(2,int(2*s)))

    # --- Beat 2: Beschriftungen ------------------------------------------
    f_y   = ImageFont.truetype(FONT_M, int(30*s))
    f_big = ImageFont.truetype(FONT,   int(52*s))
    f_sub = ImageFont.truetype(FONT_M, int(32*s))
    if g_new > 0.5:
        ho, wo, _, _, _, _ = device(OLD, s)
        d.text((CX*s - wo/2 + 16*s, CY*s - ho/2 - 40*s), str(OLD[1]),
               font=f_y, fill=ACCENT)
    if b >= 2.0:
        p = ease_out((b - 2.0) / 0.5)
        rows = [(f"{OLD[0]}  {OLD[1]}", f"{OLD[2]:.0f} × {OLD[3]:.0f} mm", 0),
                (f"{NEW[0]}  {NEW[1]}", f"{NEW[2]:.0f} × {NEW[3]:.0f} mm", 1)]
        for name, dim, k in rows:
            yy = int((1256 + k*86)*s)
            col = tuple(int(c + (255-c)*(1-p)) for c in LABEL)
            sc  = tuple(int(c + (255-c)*(1-p)) for c in SUB)
            for txt, fnt, cc, dx in ((name, f_sub, col, -170*s), (dim, f_sub, sc, 170*s)):
                bb = d.textbbox((0,0), txt, font=fnt)
                d.text((CX*s + dx - (bb[2]-bb[0])/2 - bb[0], yy), txt, font=fnt, fill=cc)
    im.resize((BW, BH), Image.LANCZOS).save(out, quality=95)

def main(beats=4.0):
    n = round(beats * BEAT * FPS)
    tmp = os.path.join(PROJ, "build", "_cmp"); os.makedirs(tmp, exist_ok=True)
    for i in range(n): frame(i, n, os.path.join(tmp, f"f{i:04d}.jpg"))
    out = os.path.join(PROJ, "assets", "generated", "phone_compare.mp4")
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",
        "-framerate",str(FPS),"-i",os.path.join(tmp,"f%04d.jpg"),
        "-c:v","libx264","-crf","12","-preset","medium","-pix_fmt","yuv420p",out],check=True)
    subprocess.run(["rm","-rf",tmp])
    print(f"{n} Frames ({beats} Beats) -> {out}")

if __name__ == "__main__":
    main(float(sys.argv[1]) if len(sys.argv) > 1 else 4.0)
