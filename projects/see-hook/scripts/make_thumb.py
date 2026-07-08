#!/usr/bin/env python3
"""Video thumbnail: white ground, the lake cut-out (silhouette swimmers) covering
the lower part, big centred 'See' in a Helvetica-clone above it, and a small
pastel-orange handwritten scrawl in the bottom-right corner (cursive, not meant
to be legible)."""
import pathlib, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
IMG  = ROOT/"main_assets"/"thumb"
OUT  = ROOT/"out"
W, H = 1920, 1080
INK=(22,22,22)
PASTEL=(243,166,112)                      # pastel orange
LIBB="/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

def _letter(x, base, w, s, typ, rng):
    """one cursive stroke primitive; returns points (pen goes up = -y)."""
    if typ in ("hump","hump2"):
        p=[(x,base),(x+0.15*w,base-0.85*s),(x+0.35*w,base-0.95*s),
           (x+0.5*w,base-0.35*s),(x+0.55*w,base-0.05*s)]
        if typ=="hump2":
            p+=[(x+0.7*w,base-0.85*s),(x+0.9*w,base-0.95*s),(x+w,base-0.2*s)]
        else: p+=[(x+w,base)]
        return p
    if typ=="round":                                   # o / a
        return [(x,base),(x+0.1*w,base-0.55*s),(x+0.3*w,base-0.95*s),(x+0.6*w,base-0.9*s),
                (x+0.72*w,base-0.4*s),(x+0.5*w,base-0.08*s),(x+0.78*w,base-0.25*s),(x+w,base)]
    if typ=="asc":                                     # l / h / b loop
        a=rng.uniform(1.9,2.5)*s
        return [(x,base),(x+0.18*w,base-a*0.55),(x+0.05*w,base-a),(x+0.32*w,base-a*0.9),
                (x+0.34*w,base-a*0.35),(x+0.28*w,base-0.1*s),(x+0.6*w,base-0.85*s),
                (x+0.85*w,base-0.55*s),(x+w,base)]
    if typ=="desc":                                    # g / y / p tail
        dd=rng.uniform(0.9,1.4)*s
        return [(x,base),(x+0.2*w,base-0.8*s),(x+0.42*w,base-0.9*s),(x+0.52*w,base+dd*0.9),
                (x+0.34*w,base+dd),(x+0.58*w,base+dd*0.4),(x+w,base)]
    return [(x,base),(x+0.5*w,base-0.7*s),(x+w,base)]   # fallback

def _cursive(d, x0, y0, width, seed, col, s=13, slant=-0.05):
    """a line of cursive-looking words along a baseline (illegible)."""
    rng=np.random.default_rng(seed)
    x=x0; end=x0+width
    while x < end-18:
        letters=int(rng.integers(3,7)); pts=[]
        for i in range(letters):
            w=s*rng.uniform(0.85,1.25)
            typ=rng.choice(["hump","hump2","round","asc","desc","hump"])
            seg=_letter(x,y0,w,s,typ,rng)
            pts+=seg if not pts else seg[1:]
            x+=w
        pts=[(px, py+slant*(px-x0)) for px,py in pts]
        d.line(pts, fill=col, width=3, joint="curve")
        # dot / accent above some words
        if rng.random()<0.6:
            cx=pts[len(pts)//2][0]; cy=y0+slant*(cx-x0)-2.1*s
            d.ellipse([cx-2,cy-2,cx+2,cy+2],fill=col)
        x+=s*rng.uniform(1.1,2.0)                        # word gap

def make():
    im=Image.new("RGB",(W,H),(255,255,255)).convert("RGBA")
    # lake cut-out (transparent sky -> white shows through), lower part
    lake=Image.open(IMG/"lake.png").convert("RGBA")
    LW=1720; lh=int(lake.height*LW/lake.width); lake=lake.resize((LW,lh),Image.LANCZOS)
    LX=(W-LW)//2; LY=-6
    im.alpha_composite(lake,(LX,LY))
    d=ImageDraw.Draw(im,"RGBA")
    # big centred 'See' in Helvetica-clone, over the white above the treeline
    f=ImageFont.truetype(LIBB,214)
    tw=d.textlength("See",font=f)
    d.text(((W-tw)/2, 46), "See", font=f, fill=INK)
    # pastel-orange cursive scrawl, bottom-right corner (not legible)
    _cursive(d, 1452, 940, 404, 11, PASTEL, s=14)
    _cursive(d, 1500, 990, 356, 23, PASTEL, s=13)
    _cursive(d, 1556, 1038, 300, 31, PASTEL, s=13)
    im.convert("RGB").save(OUT/"thumbnail.png")
    print("->", OUT/"thumbnail.png")

if __name__=="__main__":
    make()
