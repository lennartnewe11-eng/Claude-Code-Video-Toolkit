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
MAARF= BUILD/"c13_maar_f"; MAARF.mkdir(parents=True, exist_ok=True)
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
    # close small holes (bright speckles inside the cone) so they don't flicker,
    # then a light open to drop floating specks -> a temporally stabler matte
    m=Image.fromarray(((~sky)*255).astype("uint8"),"L").filter(
        ImageFilter.MaxFilter(7)).filter(ImageFilter.MinFilter(7)).filter(
        ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))
    m=m.filter(ImageFilter.GaussianBlur(2.8))
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
    eifel=make_word("EIFEL",front,(780,470),YEL)               # front (solid, one colour)
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
D_MAAR=3.6
ORG=(232,58,26)
# the three round Maare (cx,cy,rx,ry) and when each hand-drawn circle starts/ends
MAARE=[(322,352,176,128, 0.30,0.98),      # top-left
       (520,612,224,182, 1.05,1.78),      # centre (big)
       (1628,712,176,158, 1.85,2.55)]     # right

def _hand_circle(cx,cy,rx,ry,seed,npts=240,gap=0.55):
    rng=np.random.default_rng(seed)
    a0=-math.pi/2+gap/2                       # leave an open gap (near the top)
    th=np.linspace(a0, a0+2*math.pi-gap, npts)
    frq=np.array([1,2,3,5]); amp=rng.uniform(0.02,0.055,4); ph=rng.uniform(0,2*math.pi,4)
    rad=1+sum(amp[k]*np.sin(th*frq[k]+ph[k]) for k in range(4))
    jx=cx+rng.normal(0,rx*0.02); jy=cy+rng.normal(0,ry*0.02)
    xs=jx+np.cos(th)*rx*rad; ys=jy+np.sin(th)*ry*rad
    return list(zip(xs.tolist(),ys.tolist()))

def _draw_hand(d, pts, frac, col):
    k=int(len(pts)*max(0.0,min(1.0,frac)))
    if k<2: return
    seg=pts[:k]
    d.line(seg, fill=col+(235,), width=8, joint="curve")          # main marker stroke
    d.line([(x+2.0,y+1.4) for x,y in seg], fill=col+(110,), width=4, joint="curve")
    d.ellipse([seg[-1][0]-4,seg[-1][1]-4,seg[-1][0]+4,seg[-1][1]+4],fill=col+(235,))  # wet tip

def maar_frames():
    base=ImageOps.fit(Image.open(IMG/"maar.jpg").convert("RGB"),(W,H),Image.LANCZOS)
    paths=[_hand_circle(cx,cy,rx,ry,seed=7+i) for i,(cx,cy,rx,ry,_,_) in enumerate(MAARE)]
    n=int(D_MAAR*FPS)
    for i in range(n):
        t=i/FPS; im=base.copy(); d=ImageDraw.Draw(im,"RGBA")
        for j,(cx,cy,rx,ry,t0,t1) in enumerate(MAARE):
            frac=(t-t0)/(t1-t0)
            if frac>0: _draw_hand(d, paths[j], frac, ORG)
        im.save(MAARF/f"m_{i:04d}.png")
    print("maar_frames",n)

if __name__=="__main__":
    import sys
    steps=sys.argv[1:] or ["volc","maar"]
    if "volc" in steps: volcano_frames()
    if "maar" in steps: maar_frames()
