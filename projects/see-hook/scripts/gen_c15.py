#!/usr/bin/env python3
"""Chunk 15 - Part 1 assets (DIE BEDINGUNG, collage rebuild).
The basin cross-section is now filled with a real SOIL cross-section texture
(the bowl is carved into the strata); cut-out VEGETATION from a lake photo is
placed perspectively along the rim for a collage look; a green grass fringe
runs along the surface. The editorial equation + water fill/drain stay:
1 EIN BECKEN + 2 GENUG WASSER = EIN SEE, else -> "TROCKENE SENKE".
"""
import pathlib, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = pathlib.Path(__file__).resolve().parents[1]
IMG  = ROOT/"main_assets"/"c15"/"img"
BUILD= ROOT/"build"
FONTS= ROOT/"fonts"
BF   = BUILD/"c15_basin"; BF.mkdir(parents=True, exist_ok=True)
W, H, FPS = 1920, 1080, 30

WHITE=(255,255,255); GHOST=(219,222,223)
INK=(26,28,28); INK2=(78,82,82)
YEL=(252,190,0); ORG=(232,58,26)
WAT=(104,142,178)                              # muted steel water (matches the lake photo)
ANTON=str(FONTS/"Anton-Regular.ttf")
LIBR="/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
LIBB="/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
def ease(x): x=max(0.0,min(1.0,x)); return x*x*(3-2*x)
def _anton(s): return ImageFont.truetype(ANTON,s)
def _libr(s):  return ImageFont.truetype(LIBR,s)
def _libb(s):  return ImageFont.truetype(LIBB,s)
def _tsp(d,xy,t,f,fill,sp=0):
    x,y=xy
    for ch in t: d.text((x,y),ch,font=f,fill=fill); x+=d.textlength(ch,font=f)+sp
def _tsp_a(im,xy,t,f,fill,sp=0,alpha=255):
    L=Image.new("RGBA",im.size,(0,0,0,0)); d=ImageDraw.Draw(L)
    _tsp(d,xy,t,f,fill+(alpha,),sp); im.alpha_composite(L)

D=12.0
CX, WB = 960, 540
RIM, BOT = 628, 838
FLOOR = 994
L_FULL, L_EMPTY = 640.0, 839.0

def _surf():
    x=np.arange(W)
    c=0.5+0.5*np.cos(np.pi*np.clip((x-CX)/WB,-1,1))
    s=RIM+(BOT-RIM)*c; s[np.abs(x-CX)>=WB]=RIM
    return s

def _soil_slab():
    """the soil photo's earth layers, stretched to a full-width slab."""
    im=Image.open(IMG/"soil.jpg").convert("RGB")
    im=im.crop((0,92,im.width,im.height))                 # drop grass+sky, keep earth strata
    im=im.resize((W,384),Image.LANCZOS)
    a=np.asarray(im).astype(np.float32)
    a=np.clip((a-128)*1.04+128*0.99,0,255)                # gentle contrast, hair darker
    return a                                              # slab top maps to y=RIM

# --- the 3D lake (the whole lake photo, only the top white sky keyed) ---
LW=1080                                        # lake width on screen
LCX=960; LBOT_FULL=706                          # lake centre-x, near-shore y when full
def _lake():
    """crop the lake photo below the sky (trees + reflective water kept) and key
    only the near-white gaps, so the surviving image is a 3D lake to lay on the
    bowl. Returns an RGBA scaled to LW."""
    im=Image.open(IMG/"veg.png").convert("RGB").crop((0,628,2521,1664))   # drop sky band
    a=np.asarray(im).astype(np.float32); R,G,Bl=a[...,0],a[...,1],a[...,2]
    br=(R+G+Bl)/3; mx=np.maximum(np.maximum(R,G),Bl); mn=np.minimum(np.minimum(R,G),Bl)
    sat=(mx-mn)/(mx+1e-3)
    white=(br>236)&(sat<0.10)                    # only pure-white sky gaps -> transparent
    m=Image.fromarray(((~white)*255).astype("uint8"),"L").filter(
        ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3)).filter(
        ImageFilter.GaussianBlur(1.2))
    rgba=im.convert("RGBA"); rgba.putalpha(m)
    h=int(rgba.height*LW/rgba.width)
    lk=rgba.resize((LW,h),Image.LANCZOS)
    a=np.asarray(lk).astype(np.float32)          # sit it into the cool editorial grade
    a[...,:3]=np.clip((a[...,:3]-128)*1.03+128*0.99,0,255)
    # feather the pasted edges so it reads as a lake IN the bowl, not a photo card:
    # bottom dissolves into the cross-section water, sides fade out.
    yy,xx=np.mgrid[0:h,0:LW].astype(np.float32); SF,BFp=60.0,90.0
    fx=np.clip(np.minimum(xx,LW-1-xx)/SF,0,1)
    fyb=np.clip((h-1-yy)/BFp,0,1)
    a[...,3]=a[...,3]*fx*fyb
    return Image.fromarray(a.astype("uint8"),"RGBA")

def _base():
    surf=_surf()
    a=np.empty((H,W,3),np.float32); a[:]=WHITE
    rng=np.random.default_rng(3); a=np.clip(a+rng.normal(0,1.3,(H,W,1)),0,255)
    im=Image.fromarray(a.astype("uint8"),"RGB").convert("RGBA")
    dg=ImageDraw.Draw(im); _tsp(dg,(150,300),"WASSER",_anton(340),GHOST,6)  # ghost behind
    a=np.asarray(im.convert("RGB")).astype(np.float32)
    # soil ground: slab masked to the carved basin
    slab=_soil_slab(); Y=np.arange(H)[:,None]
    ground=(Y>=surf[None,:])&(Y<=FLOOR)
    sy=np.clip(np.arange(H)-RIM,0,slab.shape[0]-1)          # slab row per canvas row
    soil=slab[sy]                                           # (H,W,3)
    for c in range(3): a[...,c]=np.where(ground,soil[...,c],a[...,c])
    im=Image.fromarray(a.astype("uint8"),"RGB").convert("RGBA")
    # dark surface line + green grass fringe (tufts) along it
    d=ImageDraw.Draw(im,"RGBA")
    d.line([(x,int(surf[x])) for x in range(0,W,3)],fill=(58,46,34,255),width=3,joint="curve")
    rgf=np.random.default_rng(8)
    for x in range(0,W,7):
        yy=int(surf[x]); hgt=int(rgf.uniform(6,16)); dx=rgf.uniform(-2,2)
        gc=(60+int(rgf.uniform(0,40)),96+int(rgf.uniform(0,46)),44+int(rgf.uniform(0,26)),235)
        d.line([(x,yy),(x+dx,yy-hgt)],fill=gc,width=2)
    return im.convert("RGB"), surf

def _level(t):
    if t<5.7:  return L_EMPTY
    if t<6.9:  return L_EMPTY+(L_FULL-L_EMPTY)*ease((t-5.7)/1.2)
    if t<7.6:  return L_FULL
    if t<9.2:  return L_FULL+(L_EMPTY-L_FULL)*ease((t-7.6)/1.6)
    return L_EMPTY

def _draw_water(im, surf, L, t):
    if L>=BOT: return im
    a=np.asarray(im.convert("RGB")).astype(np.float32); Y=np.arange(H)[:,None]
    water=(Y>=L)&(Y<=surf[None,:])&(surf[None,:]>L)
    wl=np.array(WAT,np.float32); sh=0.12*np.sin((np.arange(W)[None,:]*0.05)+t*3.0)
    for c in range(3):
        a[...,c]=np.where(water, np.clip(wl[c]*(1+sh),0,255)*0.9+a[...,c]*0.1, a[...,c])
    im2=Image.fromarray(a.astype("uint8"),"RGB")
    d=ImageDraw.Draw(im2,"RGBA"); xs=np.where(surf>L)[0]
    if len(xs)>4: d.line([(int(x),int(L)) for x in xs[::3]],fill=(210,232,255,220),width=3)
    return im2

def _cracks(d, surf, a):
    rng=np.random.default_rng(5)
    for _ in range(9):
        x0=int(rng.uniform(CX-WB*0.6,CX+WB*0.6)); y0=int(surf[x0])+int(rng.uniform(6,50))
        pts=[(x0,y0)]
        for _ in range(rng.integers(3,6)):
            x0+=int(rng.uniform(-70,70)); y0+=int(rng.uniform(2,24)); pts.append((x0,y0))
        d.line(pts,fill=(40,32,22,int(210*a)),width=2,joint="curve")

def _arrow(d,x,y0,y1,a):
    d.line([(x,y0),(x,y1)],fill=WAT+(a,),width=6)
    d.polygon([(x-10,y1-14),(x+10,y1-14),(x,y1)],fill=WAT+(a,))

def _lakefrac(t): return max(0.0,min(1.0,(L_EMPTY-_level(t))/(L_EMPTY-L_FULL)))

def basin_frames():
    base,surf=_base(); lake=_lake(); LX=LCX-LW//2; n=int(D*FPS)
    for i in range(n):
        t=i/FPS; L=_level(t)
        im=_draw_water(base.copy(),surf,L,t).convert("RGBA")   # blue cross-section water
        # 3D lake laid on the bowl: fades/rises in as it fills, sinks out on drain
        lf=_lakefrac(t)
        if lf>0.01:
            sink=int((1-lf)*30); yb=LBOT_FULL+sink; yt=yb-lake.height
            lay=lake.copy()
            if lf<0.999:
                al=lay.split()[-1].point(lambda p:int(p*lf)); lay.putalpha(al)
            im.alpha_composite(lay,(LX,yt))
        d=ImageDraw.Draw(im,"RGBA")
        aH=ease((t-0.3)/0.6)
        if aH>0:
            _tsp_a(im,(96,86),"EGAL, WORAUS ER ENTSTAND —",_libb(28),INK,6,int(255*aH))
            _tsp_a(im,(92,126),"DIE BEDINGUNG",_anton(132),INK,2,int(255*aH))
        # equation - narrow right column (clears the centred lake)
        a1=ease((t-3.3)/0.6)
        if a1>0.01:
            _tsp_a(im,(1466,250),"1",_anton(58),ORG,0,int(255*a1))
            _tsp_a(im,(1506,246),"EIN",_anton(72),INK,1,int(255*a1))
            _tsp_a(im,(1506,320),"BECKEN",_anton(72),INK,1,int(255*a1))
            _tsp_a(im,(1508,402),"das Wasser hält",_libr(26),INK2,1,int(255*a1))
        a2=ease((t-5.6)/0.6)
        if a2>0.01:
            _tsp_a(im,(1466,470),"2",_anton(58),ORG,0,int(255*a2))
            _tsp_a(im,(1506,466),"GENUG",_anton(72),INK,1,int(255*a2))
            _tsp_a(im,(1506,540),"WASSER",_anton(72),INK,1,int(255*a2))
            _tsp_a(im,(1508,622),"das hineinläuft",_libr(26),INK2,1,int(255*a2))
        aS=ease((t-6.9)/0.5)*(1-ease((t-7.9)/0.4))
        if aS>0.01: _tsp_a(im,(540,590),"= EIN SEE",_anton(120),YEL,2,int(255*aS))
        aP=ease((t-7.6)/0.5)*(1-ease((t-9.2)/0.4))
        if aP>0.01: _tsp_a(im,(560,556),"FEHLT NUR EINES VON BEIDEM —",_libb(30),INK,2,int(255*aP))
        aD=ease((t-9.3)/0.6)
        if aD>0.01:
            _cracks(d,surf,aD)
            _tsp_a(im,(556,672),'„TROCKENE SENKE"',_anton(96),ORG,2,int(255*aD))
        im.convert("RGB").save(BF/f"b_{i:04d}.png")
    print("basin_frames",n)

if __name__=="__main__":
    basin_frames()
