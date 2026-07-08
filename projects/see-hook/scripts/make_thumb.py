#!/usr/bin/env python3
"""Video thumbnail: white ground; the lake cut-out fills the FULL WIDTH at the
bottom, vertically squashed a bit so it doesn't reach too high; big 'See' in a
Helvetica-clone on the LEFT with a black arrow pointing down at the lake; and a
real handwritten line (Kalam) in pastel orange in the bottom-right corner."""
import pathlib, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
IMG  = ROOT/"main_assets"/"thumb"; OUT=ROOT/"out"; FONTS=ROOT/"fonts"
W, H = 1920, 1080
INK=(18,18,18)
PASTEL=(242,158,96)                       # pastel orange (legible on the dark water)
LIBB="/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
HAND=str(FONTS/"Hand.ttf")                # Kalam handwriting

HIMG=838                                   # squashed height of the full-width lake

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
    # lake cut-out: drop the transparent bottom strip, then full width + squashed
    lake=Image.open(IMG/"lake.png").convert("RGBA").crop((0,0,1200,782))
    lake=lake.resize((W,HIMG),Image.LANCZOS)
    im.alpha_composite(lake,(0,H-HIMG))            # bottom-aligned, fills full width
    d=ImageDraw.Draw(im,"RGBA")
    # 'See' on the left, Helvetica-clone
    f=ImageFont.truetype(LIBB,208)
    d.text((118,78),"See",font=f,fill=INK)
    # black arrow from the word pointing down at the lake
    _arrow(d,(470,300),(560,300),(628,452))
    # real handwritten note, pastel orange, bottom-right
    hf=ImageFont.truetype(HAND,66)
    lines=["Wie entsteht","ein See?"]
    lay=Image.new("RGBA",(760,240),(0,0,0,0)); ld=ImageDraw.Draw(lay)
    y=0
    for ln in lines:
        w=ld.textlength(ln,font=hf); ld.text((740-w,y),ln,font=hf,fill=PASTEL); y+=98
    lay=lay.rotate(3.5,expand=True,resample=Image.BICUBIC)
    im.alpha_composite(lay,(W-lay.width-40,H-lay.height-24))
    im.convert("RGB").save(OUT/"thumbnail.png")
    print("->",OUT/"thumbnail.png")

if __name__=="__main__":
    make()
