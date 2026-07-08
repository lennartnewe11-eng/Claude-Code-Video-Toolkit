#!/usr/bin/env python3
"""Video thumbnail: white ground; the lake cut-out fills the FULL WIDTH and
reaches all the way to the bottom, squashed a little so it doesn't climb too
high; big 'See' on the LEFT with a black arrow pointing at the lake; and a real
handwritten note in the bottom-right in an ornate script with a hand-tremor
warp (pastel orange) so it looks written by a very old person."""
import pathlib, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
IMG  = ROOT/"main_assets"/"thumb"; OUT=ROOT/"out"; FONTS=ROOT/"fonts"
W, H = 1920, 1080
INK=(18,18,18)
PASTEL=(242,158,96)
LIBB="/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
HAND=str(FONTS/"Hand.ttf")                      # Kalam handwriting (as in the first version)
HIMG=892; CROP_Y=758                            # lake height on screen / opaque crop

def _arrow(d, p0, p1, p2, col=INK, wdt=13):
    t=np.linspace(0,1,60)
    xs=(1-t)**2*p0[0]+2*(1-t)*t*p1[0]+t**2*p2[0]
    ys=(1-t)**2*p0[1]+2*(1-t)*t*p1[1]+t**2*p2[1]
    d.line(list(zip(xs,ys)), fill=col, width=wdt, joint="curve")
    dx,dy=p2[0]-xs[-6],p2[1]-ys[-6]; L=math.hypot(dx,dy); dx,dy=dx/L,dy/L
    hl,hw=46,30; bx,by=p2[0]-dx*hl,p2[1]-dy*hl; px,py=-dy,dx
    d.polygon([(p2[0],p2[1]),(bx+px*hw,by+py*hw),(bx-px*hw,by-py*hw)],fill=col)

def make():
    im=Image.new("RGB",(W,H),(255,255,255)).convert("RGBA")
    # lake: crop to the last solidly-opaque row, then full width + squashed
    lake=Image.open(IMG/"lake.png").convert("RGBA").crop((0,0,1200,CROP_Y))
    lake=lake.resize((W,HIMG),Image.LANCZOS)
    im.alpha_composite(lake,(0,H-HIMG))
    d=ImageDraw.Draw(im,"RGBA")
    # pastel-orange filled circles as a style element in the top area
    for cx,cy,r in [(1636,150,54),(1180,92,34),(1806,360,30),(772,142,46),(1420,250,25)]:
        d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=PASTEL)
    # 'See' left + black arrow to the lake
    d.text((118,78),"See",font=ImageFont.truetype(LIBB,208),fill=INK)
    _arrow(d,(470,300),(560,300),(628,404))
    # handwritten note in the first version's font (Kalam), pastel orange, bottom-right
    hf=ImageFont.truetype(HAND,74)
    lines=["Wie entsteht","ein See?"]
    lay=Image.new("RGBA",(820,250),(0,0,0,0)); ld=ImageDraw.Draw(lay); y=0
    for ln in lines:
        wln=ld.textlength(ln,font=hf); ld.text((800-wln,y),ln,font=hf,fill=PASTEL); y+=106
    lay=lay.rotate(3.5,expand=True,resample=Image.BICUBIC)
    im.alpha_composite(lay,(W-lay.width-34,H-lay.height-22))
    im.convert("RGB").save(OUT/"thumbnail.png")
    print("->",OUT/"thumbnail.png")

if __name__=="__main__":
    make()
