#!/usr/bin/env python3
"""Chunk 15 assets (DIE BEDINGUNG - the universal recipe, on plain white).
The synthesis after all the lake-makers: every lake, whatever built it, comes
down to the same equation - a basin that holds water + enough water flowing in
= a lake; miss one and it stays a dry hollow.

basin_frames(): a Swiss-editorial cross-section of a basin along the bottom that
fills with water (in sync with '...genug Wasser, das hineinläuft'), stamps
'= EIN SEE' in yellow, then drains again ('Fehlt nur eines...') to a dry hollow
with '"TROCKENE SENKE"' in red-orange + fine cracks. The equation builds as a
staggered right-hand column; a ghost word 'WASSER' sits behind.
"""
import pathlib, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
BUILD= ROOT/"build"
FONTS= ROOT/"fonts"
BF   = BUILD/"c15_basin"; BF.mkdir(parents=True, exist_ok=True)
W, H, FPS = 1920, 1080, 30

WHITE=(255,255,255); GHOST=(219,222,223)
INK=(26,28,28); INK2=(78,82,82)
YEL=(252,190,0); ORG=(232,58,26)
GRD=(176,168,152); GRD_D=(150,142,126)        # basin ground + hatch
WAT=(46,116,196)                               # water
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
# --- basin cross-section geometry (full-width ground, bowl carved in centre) ---
CX, WB = 960, 540
RIM, BOT = 628, 838                            # rim y, bowl-bottom y
FLOOR = 992                                    # ground slab bottom
L_FULL, L_EMPTY = 640.0, 839.0                 # water-surface y when full / empty

def _surf():
    x=np.arange(W)
    c=0.5+0.5*np.cos(np.pi*np.clip((x-CX)/WB,-1,1))   # 1 centre -> 0 edge
    s=RIM+(BOT-RIM)*c
    s[np.abs(x-CX)>=WB]=RIM
    return s                                    # surface y per column

def _base():
    """white ground + ghost word + baked terrain slab (no water)."""
    a=np.empty((H,W,3),np.float32); a[:]=WHITE
    rng=np.random.default_rng(3); a=np.clip(a+rng.normal(0,1.3,(H,W,1)),0,255)
    im=Image.fromarray(a.astype("uint8"),"RGB").convert("RGBA")
    dg=ImageDraw.Draw(im); _tsp(dg,(150,300),"WASSER",_anton(340),GHOST,6)   # ghost behind
    a=np.asarray(im.convert("RGB")).astype(np.float32)
    surf=_surf(); Y=np.arange(H)[:,None]
    ground=(Y>=surf[None,:])&(Y<=FLOOR)
    g=np.array(GRD,np.float32)
    for c in range(3): a[...,c]=np.where(ground,g[c],a[...,c])
    # faint diagonal hatch inside the ground
    hatch=(((np.arange(W)[None,:]+np.arange(H)[:,None])%14)<1)&ground
    for c in range(3): a[...,c]=np.where(hatch,GRD_D[c],a[...,c])
    im=Image.fromarray(a.astype("uint8"),"RGB")
    d=ImageDraw.Draw(im)                         # dark surface line
    pts=[(x,int(surf[x])) for x in range(0,W,3)]
    d.line(pts,fill=GRD_D,width=3,joint="curve")
    return im, surf

def _level(t):
    if t<5.7:  return L_EMPTY
    if t<6.9:  return L_EMPTY+(L_FULL-L_EMPTY)*ease((t-5.7)/1.2)
    if t<7.6:  return L_FULL
    if t<9.2:  return L_FULL+(L_EMPTY-L_FULL)*ease((t-7.6)/1.6)
    return L_EMPTY

def _draw_water(im, surf, L, t):
    if L>=BOT: return im
    a=np.asarray(im.convert("RGB")).astype(np.float32)
    Y=np.arange(H)[:,None]
    water=(Y>=L)&(Y<=surf[None,:])&(surf[None,:]>L)
    wl=np.array(WAT,np.float32)
    sh=0.12*np.sin((np.arange(W)[None,:]*0.05)+t*3.0)   # gentle shimmer
    for c in range(3):
        a[...,c]=np.where(water, np.clip(wl[c]*(1+sh),0,255)*0.9+a[...,c]*0.1, a[...,c])
    im2=Image.fromarray(a.astype("uint8"),"RGB")
    d=ImageDraw.Draw(im2,"RGBA")                 # bright water-line at the surface
    xs=np.where(surf>L)[0]
    if len(xs)>4:
        d.line([(int(x),int(L)) for x in xs[::3]],fill=(210,232,255,220),width=3)
    return im2

def _cracks(d, surf, a):
    rng=np.random.default_rng(5)
    for _ in range(9):
        x0=int(rng.uniform(CX-WB*0.7,CX+WB*0.7)); y0=int(surf[x0])+int(rng.uniform(6,60))
        pts=[(x0,y0)]
        for _ in range(rng.integers(3,6)):
            x0+=int(rng.uniform(-70,70)); y0+=int(rng.uniform(2,26)); pts.append((x0,y0))
        col=(120,112,96,int(210*a))
        d.line(pts,fill=col,width=2,joint="curve")

def _arrow(d,x,y0,y1,a):
    d.line([(x,y0),(x,y1)],fill=WAT+(a,),width=6)
    d.polygon([(x-10,y1-14),(x+10,y1-14),(x,y1)],fill=WAT+(a,))

def basin_frames():
    base,surf=_base(); n=int(D*FPS)
    for i in range(n):
        t=i/FPS; L=_level(t)
        im=_draw_water(base.copy(),surf,L,t).convert("RGBA")
        d=ImageDraw.Draw(im,"RGBA")
        # --- header ---
        aH=ease((t-0.3)/0.6)
        if aH>0:
            _tsp_a(im,(96,86),"EGAL, WORAUS ER ENTSTAND —",_libb(28),INK,6,int(255*aH))
            _tsp_a(im,(92,126),"DIE BEDINGUNG",_anton(132),INK,2,int(255*aH))
        # --- inflow arrows while filling ---
        if 5.6<t<7.4:
            aa=int(230*ease((t-5.6)/0.4)*(0.6+0.4*math.sin(t*6)))
            for k,xx in enumerate((CX-120,CX,CX+120)):
                yy0=470+ (math.sin(t*5+k)*8); _arrow(d,xx,yy0,560,aa)
        # --- equation column (right) ---
        a1=ease((t-3.3)/0.6)
        if a1>0.01:
            _tsp_a(im,(1150,214),"1",_anton(64),ORG,0,int(255*a1))
            _tsp_a(im,(1214,232),"EIN BECKEN",_anton(92),INK,1,int(255*a1))
            _tsp_a(im,(1216,338),"das Wasser halten kann",_libr(30),INK2,1,int(255*a1))
        a2=ease((t-5.6)/0.6)
        if a2>0.01:
            _tsp_a(im,(1150,404),"2",_anton(64),ORG,0,int(255*a2))
            _tsp_a(im,(1214,422),"GENUG WASSER",_anton(92),INK,1,int(255*a2))
            _tsp_a(im,(1216,528),"das hineinläuft",_libr(30),INK2,1,int(255*a2))
        # result over the basin (full): '= EIN SEE'
        aS=ease((t-6.9)/0.5)*(1-ease((t-7.9)/0.4))
        if aS>0.01:
            _tsp_a(im,(748,548),"= EIN SEE",_anton(120),YEL,2,int(255*aS))
        # pivot: the basin drains -> dry hollow, labelled INSIDE the empty bowl
        aP=ease((t-7.6)/0.5)
        if aP>0.01:
            _tsp_a(im,(566,596),"FEHLT NUR EINES VON BEIDEM —",_libb(30),INK,2,int(255*aP))
        aD=ease((t-9.3)/0.6)
        if aD>0.01:
            _cracks(d,surf,aD)
            _tsp_a(im,(556,684),'„TROCKENE SENKE"',_anton(92),ORG,2,int(255*aD))
        im.convert("RGB").save(BF/f"b_{i:04d}.png")
    print("basin_frames",n)

if __name__=="__main__":
    basin_frames()
