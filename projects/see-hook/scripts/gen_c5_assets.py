#!/usr/bin/env python3
"""Prep PIL assets for Chunk 5 (Grundwasser):
- b1_bg.png : blue editorial background (ref blue.jpg) with a left vertical
  filmstrip of 3 B&W photos + scattered circles (water gif + type added later).
- mirror_mask.png : oval alpha mask for the mirror's glass (to fill with video).
"""
import pathlib
from PIL import Image, ImageOps, ImageDraw, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parents[1]
C5 = ROOT/"main_assets"/"c5"; IMG = C5/"img"
BUILD = ROOT/"build"; BUILD.mkdir(exist_ok=True)
W, H = 1920, 1080
BLUE = (12, 90, 224)
RED  = (224, 64, 42)
BLUED= (30, 60, 200)

def bw_photo(path, w, h):
    im = ImageOps.grayscale(Image.open(path).convert("RGB"))
    im = ImageOps.autocontrast(im, 1)
    im = ImageOps.fit(im, (w, h), Image.LANCZOS).convert("RGB")
    b = 10
    card = Image.new("RGB", (w+2*b, h+2*b), (245, 243, 238))
    card.paste(im, (b, b))
    return card

YEL  = (240, 210, 0)

def b1_fg():
    # transparent FOREGROUND layer: circles (yellow + blue) + B&W photo strip.
    # Composited on top of white + the water gif, so all objects sit in front.
    fg = Image.new("RGBA", (W, H), (0,0,0,0))
    d = ImageDraw.Draw(fg)
    for (x,y,r,c) in [(300,150,70,YEL),(360,470,44,BLUED),(150,760,52,YEL),
                      (1520,300,120,YEL),(1150,560,60,BLUED),(1640,760,40,YEL)]:
        d.ellipse([x-r,y-r,x+r,y+r], fill=c+(255,))
    photos=["p1.jpg","p2.jpg","p3.jpg"]
    pw,ph = 340,236; x=120; y=150
    for p in photos:
        card=bw_photo(IMG/p, pw, ph).convert("RGBA")
        sh=Image.new("RGBA",(card.width+40,card.height+40),(0,0,0,0))
        s=Image.new("RGBA",card.size,(0,0,0,80)); sh.paste(s,(24,28))
        sh=sh.filter(ImageFilter.GaussianBlur(10))
        fg.alpha_composite(sh,(x-16,y-16)); fg.alpha_composite(card,(x,y))
        y += ph+2*10 - 4
    fg.save(BUILD/"c5_b1_fg.png"); print("b1 fg ok")

def mirror_mask():
    # mirror.png is 426x640; glass oval ~ fractional box below
    mw,mh = Image.open(C5/"mirror.png").size
    m = Image.new("L",(mw,mh),0); d=ImageDraw.Draw(m)
    d.ellipse([mw*0.135, mh*0.155, mw*0.865, mh*0.855], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(3))
    m.save(BUILD/"c5_mirror_mask.png"); print("mirror mask ok", (mw,mh))

if __name__=="__main__":
    b1_fg(); mirror_mask()
