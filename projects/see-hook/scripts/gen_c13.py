#!/usr/bin/env python3
"""Chunk 13 assets (Eifel-Vulkanismus / Maare - 'not only the ice').
- volcano_frames(): the user's volcano clip with the SKY keyed to white, laid
  FULL-WIDTH along the bottom; layered yellow editorial type baked in (behind =
  MAGMA, the peak rising in front of it; front = EIFEL over the cone) + kicker.
- maar_hero(): the aerial of the round Dauner Maare, circles highlighting the
  near-circular crater lakes, for the 'kreisrunde Krater / Maare' beat.
"""
import pathlib, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = pathlib.Path(__file__).resolve().parents[1]
IMG  = ROOT/"main_assets"/"c13"/"img"
BUILD= ROOT/"build"
FONTS= ROOT/"fonts"
RAW  = BUILD/"c13_volc_raw"
VF   = BUILD/"c13_volc"; VF.mkdir(parents=True, exist_ok=True)
W, H, FPS = 1920, 1080, 30
BG=(248,247,244); YEL=(252,190,0)
ANTON=str(FONTS/"Anton-Regular.ttf")
LIBB="/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
def ease(x): x=max(0.0,min(1.0,x)); return x*x*(3-2*x)
def _anton(s): return ImageFont.truetype(ANTON,s)
def _libb(s): return ImageFont.truetype(LIBB,s)
def _tsp(d,xy,t,f,fill,sp=0):
    x,y=xy
    for ch in t: d.text((x,y),ch,font=f,fill=fill); x+=d.textlength(ch,font=f)+sp

# ---- volcano on white, full-width bottom, layered yellow type ----------------
D_VOLC=8.0
def _key(im):
    a=np.asarray(im.convert("RGB")).astype(np.float32)
    R,G,B=a[...,0],a[...,1],a[...,2]; br=(R+G+B)/3
    sky=((B-R)>10)|(br>152)                     # blue sky + blue haze (keep the cone)
    m=Image.fromarray(((~sky)*255).astype("uint8"),"L").filter(
        ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(3))
    m=m.filter(ImageFilter.GaussianBlur(2.4))
    rgba=im.convert("RGBA"); rgba.putalpha(m); return rgba

def volcano_frames():
    raws=sorted(RAW.glob("v_*.png")); n=int(D_VOLC*FPS)
    kfont=_libb(30); big=_anton(300); front=_anton(300)
    # precompute static text layers we can alpha-blend
    def make_word(txt,font,pos,fill,hollow=False):
        L=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(L)
        if hollow: d.text(pos,txt,font=font,fill=BG,stroke_width=5,stroke_fill=fill)
        else: d.text(pos,txt,font=font,fill=fill)
        return L
    magma=make_word("MAGMA",big,(150,150),YEL)                 # behind
    eifel=make_word("EIFEL",front,(780,470),YEL,hollow=True)   # front (outline)
    for i in range(n):
        t=i/FPS
        src=raws[min(i,len(raws)-1)]
        vol=_key(Image.open(src))
        VW=W; VH=int(vol.height*VW/vol.width); vol=vol.resize((VW,VH),Image.LANCZOS)
        cv=Image.new("RGBA",(W,H),BG+(255,))
        # kicker (persistent)
        d=ImageDraw.Draw(cv); _tsp(d,(96,86),"NICHT NUR DAS EIS",kfont,(30,28,24),6)
        # behind word fades in
        aB=ease((t-3.9)/0.5)
        if aB>0: cv=Image.alpha_composite(cv, Image.blend(Image.new("RGBA",(W,H),(0,0,0,0)),magma,aB))
        cv.alpha_composite(vol,(0,H-VH))                       # volcano full-width bottom
        # front word fades in
        aF=ease((t-4.4)/0.5)
        if aF>0: cv=Image.alpha_composite(cv, Image.blend(Image.new("RGBA",(W,H),(0,0,0,0)),eifel,aF))
        # small tag
        d=ImageDraw.Draw(cv)
        if t>4.6:
            _tsp(d,(96,980),"MAGMA SPRENGT SICH NACH OBEN",_libb(26),YEL,3)
        cv.convert("RGB").save(VF/f"f_{i:04d}.png")
    print("volcano_frames",n)

# ---- Dauner Maare: round crater lakes ----------------------------------------
def maar_hero():
    im=Image.open(IMG/"maar.jpg").convert("RGB")
    im=ImageOps.fit(im,(W,H),Image.LANCZOS).convert("RGBA")
    # thin red-orange rings emphasising the near-circular crater lakes
    ring=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ring)
    ORG=(232,58,26)
    for cx,cy,rx,ry in [(322,352,168,120),(520,612,215,175),(1628,712,168,150)]:
        for k,al in ((10,70),(0,210)):
            d.ellipse([cx-rx-k,cy-ry-k,cx+rx+k,cy+ry+k],outline=ORG+(al,),width=5)
    im=Image.alpha_composite(im,ring)
    im.convert("RGB").save(BUILD/"c13_maar.png")
    print("maar_hero -> c13_maar.png", im.size)

if __name__=="__main__":
    import sys
    steps=sys.argv[1:] or ["volc","maar"]
    if "volc" in steps: volcano_frames()
    if "maar" in steps: maar_hero()
