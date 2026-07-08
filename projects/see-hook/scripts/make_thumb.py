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
SCRIPT=str(FONTS/"GreatVibes-Regular.ttf")     # ornate script
HIMG=892; CROP_Y=758                            # lake height on screen / opaque crop

def _arrow(d, p0, p1, p2, col=INK, wdt=13):
    t=np.linspace(0,1,60)
    xs=(1-t)**2*p0[0]+2*(1-t)*t*p1[0]+t**2*p2[0]
    ys=(1-t)**2*p0[1]+2*(1-t)*t*p1[1]+t**2*p2[1]
    d.line(list(zip(xs,ys)), fill=col, width=wdt, joint="curve")
    dx,dy=p2[0]-xs[-6],p2[1]-ys[-6]; L=math.hypot(dx,dy); dx,dy=dx/L,dy/L
    hl,hw=46,30; bx,by=p2[0]-dx*hl,p2[1]-dy*hl; px,py=-dy,dx
    d.polygon([(p2[0],p2[1]),(bx+px*hw,by+py*hw),(bx-px*hw,by-py*hw)],fill=col)

def _tremor(layer, amp=4.4, seed=7):
    """warp with smooth low-frequency displacement -> shaky, aged handwriting."""
    a=np.asarray(layer).astype(np.float32); h,w=a.shape[:2]
    rng=np.random.default_rng(seed)
    def field(sc):
        lo=rng.normal(0,1,(max(2,h//sc),max(2,w//sc)))
        im=Image.fromarray(np.clip(lo*90+128,0,255).astype("uint8")).resize((w,h),Image.BICUBIC)
        return np.asarray(im,np.float32)/90-128/90
    dx=field(24)*amp+field(70)*amp*1.3
    dy=field(24)*amp+field(70)*amp*1.3
    xs,ys=np.meshgrid(np.arange(w),np.arange(h))
    sx=np.clip((xs+dx).round().astype(int),0,w-1); sy=np.clip((ys+dy).round().astype(int),0,h-1)
    return Image.fromarray(a[sy,sx].astype("uint8"),"RGBA")

def make():
    im=Image.new("RGB",(W,H),(255,255,255)).convert("RGBA")
    # lake: crop to the last solidly-opaque row, then full width + squashed
    lake=Image.open(IMG/"lake.png").convert("RGBA").crop((0,0,1200,CROP_Y))
    lake=lake.resize((W,HIMG),Image.LANCZOS)
    im.alpha_composite(lake,(0,H-HIMG))
    d=ImageDraw.Draw(im,"RGBA")
    # 'See' left + black arrow to the lake
    d.text((118,78),"See",font=ImageFont.truetype(LIBB,208),fill=INK)
    _arrow(d,(470,300),(560,300),(628,404))
    # ornate + shaky handwritten note, pastel orange, bottom-right
    hf=ImageFont.truetype(SCRIPT,118)
    lines=["Wie entsteht","ein See?"]
    lay=Image.new("RGBA",(920,320),(0,0,0,0)); ld=ImageDraw.Draw(lay); y=0
    for ln in lines:
        wln=ld.textlength(ln,font=hf); ld.text((900-wln,y),ln,font=hf,fill=PASTEL); y+=138
    lay=_tremor(lay,amp=4.6,seed=5).rotate(3.0,expand=True,resample=Image.BICUBIC)
    im.alpha_composite(lay,(W-lay.width-30,H-lay.height-14))
    im.convert("RGB").save(OUT/"thumbnail.png")
    print("->",OUT/"thumbnail.png")

if __name__=="__main__":
    make()
