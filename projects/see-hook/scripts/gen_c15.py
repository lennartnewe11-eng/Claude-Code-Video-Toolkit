#!/usr/bin/env python3
"""Chunk 15 - Part 1 assets (DIE BEDINGUNG, collage rebuild v2).
The basin is carved into a real SOIL cross-section; a real 3-D lake sits in the
mulde: the WATER VIDEO fills the bowl as the lake surface, and the cut-out
VEGETATION (keyed lake photo, trees+banks+hills) forms the FAR SHORELINE rising
above it. Editorial equation + fill/drain stay: 1 BECKEN + 2 WASSER = EIN SEE,
else -> "TROCKENE SENKE".
"""
import pathlib, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
IMG  = ROOT/"main_assets"/"c15"/"img"
BUILD= ROOT/"build"
FONTS= ROOT/"fonts"
BF   = BUILD/"c15_basin"; BF.mkdir(parents=True, exist_ok=True)
WATD = BUILD/"c15_wat"
W, H, FPS = 1920, 1080, 30

WHITE=(255,255,255); GHOST=(219,222,223)
INK=(26,28,28); INK2=(78,82,82)
YEL=(252,190,0); ORG=(232,58,26)
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
# --- 3-D cut-away lake geometry ---------------------------------------------
# generated animated water = the CROSS-SECTION (the hidden underwater wall);
# the boat video = the water SURFACE, laid into the ellipse the curved
# vegetation shoreline encloses (its rounding suggests depth).
CX, WB = 960, 458
RIM, BOT = 562, 816                              # bed rim / bowl bottom (the cross-section bed)
FLOOR = 994
L_FULL, L_EMPTY = 562.0, 817.0
ELCX, ELCY, ELA, ELB = 960, 466, 458, 96         # water-surface ellipse
BOATBAND_TOP=316                                 # boat band row -> ellipse
WAT=(70,120,176)                                 # animated cross-section water
VW=980; SHX=ELCX-VW//2; SVBOT=478                # far-shore veg band width/pos

def _surf():
    x=np.arange(W)
    c=0.5+0.5*np.cos(np.pi*np.clip((x-CX)/WB,-1,1))
    s=RIM+(BOT-RIM)*c; s[np.abs(x-CX)>=WB]=RIM
    return s

def _ellipse():
    x=np.arange(W).astype(np.float32); t=(x-ELCX)/ELA
    inell=np.abs(t)<=1.0
    half=np.zeros(W,np.float32); half[inell]=ELB*np.sqrt(np.clip(1-t[inell]**2,0,1))
    etop=np.full(W,1e9,np.float32); ebot=np.full(W,-1e9,np.float32)
    etop[inell]=ELCY-half[inell]; ebot[inell]=ELCY+half[inell]
    return etop,ebot,inell

def _soil_slab():
    im=Image.open(IMG/"soil.jpg").convert("RGB").crop((0,92,750,489))
    im=im.resize((W,FLOOR-RIM+8),Image.LANCZOS)
    a=np.asarray(im).astype(np.float32)
    return np.clip((a-128)*1.04+128*0.99,0,255)

def _vegshore():
    """cut-out vegetation (banks + far treeline + hills) = the lake's far shore."""
    im=Image.open(IMG/"veg.png").convert("RGB")
    a=np.asarray(im).astype(np.float32); R,G,Bl=a[...,0],a[...,1],a[...,2]
    br=(R+G+Bl)/3; mx=np.maximum(np.maximum(R,G),Bl); mn=np.minimum(np.minimum(R,G),Bl)
    sat=(mx-mn)/(mx+1e-3)
    remove=((br>200)&(sat<0.18))|((br>170)&(sat<0.10))     # sky + bright open water
    m=Image.fromarray(((~remove)*255).astype("uint8"),"L").filter(
        ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(5)).filter(
        ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    rgba=im.convert("RGBA"); rgba.putalpha(m)
    al=np.asarray(m); ys,xs=np.where(al>30)
    rgba=rgba.crop((int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.min())+430))  # banks only
    hh=int(rgba.height*VW/rgba.width); lk=rgba.resize((VW,hh),Image.LANCZOS)
    a=np.asarray(lk).astype(np.float32)
    a[...,:3]=np.clip((a[...,:3]-128)*1.03+128*0.99,0,255)
    xx=np.arange(VW)[None,:].astype(np.float32)
    a[...,3]=a[...,3]*np.clip(np.minimum(xx,VW-1-xx)/34.0,0,1)     # soften side ends
    return Image.fromarray(a.astype("uint8"),"RGBA")

def _veg_layer(etop):
    """full-canvas vegetation, its bottom cut to the ellipse far-rim curve so the
    shoreline is ROUNDED (suggests depth) instead of a straight band."""
    band=_vegshore(); layer=Image.new("RGBA",(W,H),(0,0,0,0))
    layer.alpha_composite(band,(SHX,SVBOT-band.height))
    a=np.asarray(layer).astype(np.float32); Y=np.arange(H)[:,None].astype(np.float32)
    a[...,3]=a[...,3]*np.clip((etop[None,:]-Y)/12.0+1.0,0,1)       # keep only above the far rim
    return a[...,:3], a[...,3]

def _base():
    surf=_surf()
    a=np.empty((H,W,3),np.float32); a[:]=WHITE
    rng=np.random.default_rng(3); a=np.clip(a+rng.normal(0,1.3,(H,W,1)),0,255)
    im=Image.fromarray(a.astype("uint8"),"RGB").convert("RGBA")
    dg=ImageDraw.Draw(im); _tsp(dg,(150,300),"WASSER",_anton(340),GHOST,6)
    a=np.asarray(im.convert("RGB")).astype(np.float32)
    slab=_soil_slab(); Y=np.arange(H)[:,None]
    ground=(Y>=surf[None,:])&(Y<=FLOOR)
    sy=np.clip(np.arange(H)-RIM,0,slab.shape[0]-1); soil=slab[sy]
    for c in range(3): a[...,c]=np.where(ground,soil[...,c],a[...,c])
    im=Image.fromarray(a.astype("uint8"),"RGB").convert("RGBA")
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
def _lakefrac(t): return max(0.0,min(1.0,(L_EMPTY-_level(t))/(L_EMPTY-L_FULL)))

def _compose_lake(im, surf, etop, ebot, inell, L, frac, band, veg_rgb, veg_a, t):
    """blue animated CROSS-SECTION (Y>=L) + boat-video SURFACE in the ellipse +
    curved far-shore vegetation."""
    a=np.asarray(im.convert("RGB")).astype(np.float32)
    Y=np.arange(H)[:,None]
    # cross-section: generated animated water below the level, down to the bed
    water=(Y>=L)&(Y<=surf[None,:])&(surf[None,:]>L)&inell[None,:]
    wl=np.array(WAT,np.float32); sh=0.10*np.sin(np.arange(W)[None,:]*0.05+t*3.0)
    depth=np.clip((Y-L)/260.0,0,1); dk=1-0.34*depth
    for c in range(3):
        a[...,c]=np.where(water, np.clip(wl[c]*(1+sh)*dk,0,255), a[...,c])
    if frac>0.02:
        # water SURFACE = boat video, masked to the ellipse the shore encloses
        ell=(Y>=etop[None,:])&(Y<=ebot[None,:])&inell[None,:]
        brow=np.clip(np.arange(H)-BOATBAND_TOP,0,band.shape[0]-1); bs=band[brow]
        ef=(ell*frac)[...,None]
        a=a*(1-ef)+bs*ef
        # curved vegetation far shore (rounded rim => depth)
        va=(veg_a*frac)[...,None]/255.0
        a=a*(1-va)+veg_rgb*va
    im2=Image.fromarray(np.clip(a,0,255).astype("uint8"),"RGB")
    if L<BOT:                                            # bright near-shore waterline
        d=ImageDraw.Draw(im2,"RGBA"); xs=np.where((surf>L)&inell)[0]
        if len(xs)>4: d.line([(int(x),int(ebot[x])) for x in xs[::3]],fill=(230,238,246,150),width=2)
    return im2

def _cracks(d, surf, a):
    rng=np.random.default_rng(5)
    for _ in range(9):
        x0=int(rng.uniform(CX-WB*0.6,CX+WB*0.6)); y0=int(surf[x0])+int(rng.uniform(6,50))
        pts=[(x0,y0)]
        for _ in range(rng.integers(3,6)):
            x0+=int(rng.uniform(-70,70)); y0+=int(rng.uniform(2,24)); pts.append((x0,y0))
        d.line(pts,fill=(40,32,22,int(210*a)),width=2,joint="curve")

def basin_frames():
    base,surf=_base(); etop,ebot,inell=_ellipse(); veg_rgb,veg_a=_veg_layer(etop)
    n=int(D*FPS); wats=sorted(WATD.glob("w_*.png"))
    for i in range(n):
        t=i/FPS; L=_level(t); lf=_lakefrac(t)
        band=np.asarray(Image.open(wats[min(i,len(wats)-1)]).convert("RGB")).astype(np.float32)
        im=_compose_lake(base,surf,etop,ebot,inell,L,lf,band,veg_rgb,veg_a,t).convert("RGBA")
        d=ImageDraw.Draw(im,"RGBA")
        aH=ease((t-0.3)/0.6)
        if aH>0:
            _tsp_a(im,(96,86),"EGAL, WORAUS ER ENTSTAND —",_libb(28),INK,6,int(255*aH))
            _tsp_a(im,(92,126),"DIE BEDINGUNG",_anton(132),INK,2,int(255*aH))
        a1=ease((t-3.3)/0.6)
        if a1>0.01:
            _tsp_a(im,(1466,210),"1",_anton(58),ORG,0,int(255*a1))
            _tsp_a(im,(1506,206),"EIN",_anton(72),INK,1,int(255*a1))
            _tsp_a(im,(1506,278),"BECKEN",_anton(72),INK,1,int(255*a1))
            _tsp_a(im,(1508,360),"das Wasser hält",_libr(26),INK2,1,int(255*a1))
        a2=ease((t-5.6)/0.6)
        if a2>0.01:
            _tsp_a(im,(1466,398),"2",_anton(58),ORG,0,int(255*a2))
            _tsp_a(im,(1506,394),"GENUG",_anton(72),INK,1,int(255*a2))
            _tsp_a(im,(1506,466),"WASSER",_anton(72),INK,1,int(255*a2))
            _tsp_a(im,(1508,548),"das hineinläuft",_libr(26),INK2,1,int(255*a2))
        aS=ease((t-6.9)/0.5)*(1-ease((t-7.9)/0.4))
        if aS>0.01: _tsp_a(im,(600,646),"= EIN SEE",_anton(120),YEL,2,int(255*aS))
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
