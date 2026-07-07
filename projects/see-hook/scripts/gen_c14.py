#!/usr/bin/env python3
"""Chunk 14 assets (Altarme + Tagebau - 'the other lake-makers, and us').
Both beats are built in the reference collage look: a big torn cut-out subject
sweeping down the RIGHT, editorial typography nested into the LEFT negative
space, and a play of LAYERS - a ghost word baked BEHIND the cut-out, the
masthead/body ON the ground, a red-orange annotation IN FRONT.

- river_frames(): the meandering-river cut-out (Altarme). Ghost word 'SCHLINGEN'
  behind it; masthead ALTARME + a small justified body column on the left; a
  hand-drawn red-orange ring annotating an ox-bow; then the pivot 'WIR SELBST.'
- tagebau_frames(): the Tagebau Hambach time-lapse framed in a torn window on
  the right (year labels intact), editorial type on the left (Lausitz -> See).
"""
import pathlib, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = pathlib.Path(__file__).resolve().parents[1]
IMG  = ROOT/"main_assets"/"c14"/"img"
BUILD= ROOT/"build"
FONTS= ROOT/"fonts"
TRAW = BUILD/"c14_tag_raw"
RF   = BUILD/"c14_river"; RF.mkdir(parents=True, exist_ok=True)
TF   = BUILD/"c14_tag";   TF.mkdir(parents=True, exist_ok=True)
W, H, FPS = 1920, 1080, 30

GROUND=(171,181,182)          # cool editorial paper (from the reference)
INK =(26,28,28); INK2=(78,82,82)
YEL =(252,190,0); ORG=(232,58,26)
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
    """tracked text with a global alpha, composited (for fades)."""
    L=Image.new("RGBA",im.size,(0,0,0,0)); d=ImageDraw.Draw(L)
    _tsp(d,xy,t,f,fill+(alpha,),sp)
    im.alpha_composite(L)
def _body(im,xy,lines,f,fill,lh,sp=0,alpha=255):
    x,y=xy
    for ln in lines:
        _tsp_a(im,(x,y),ln,f,fill,sp,alpha); y+=lh

def _paper(seed=7):
    rng=np.random.default_rng(seed)
    a=np.empty((H,W,3),np.float32); a[:]=np.array(GROUND,np.float32)
    a=a+rng.normal(0,2.2,(H,W,1))                    # neutral luminance grain
    # faint cool blotching for a printed feel
    blob=rng.normal(0,1.0,(H//8,W//8,3)).astype(np.float32)
    blob=np.asarray(Image.fromarray(np.clip(128+blob*18,0,255).astype("uint8")
          ).resize((W,H),Image.BILINEAR),np.float32)-128
    a=np.clip(a+blob*0.5,0,255)
    return Image.fromarray(a.astype("uint8"),"RGB").convert("RGBA")

def _shadow(alpha_img, off=(8,12), blur=9, dark=95):
    """soft drop shadow from an RGBA cut-out's alpha (collage lift)."""
    m=alpha_img.split()[-1]
    sh=Image.new("RGBA",alpha_img.size,(0,0,0,0))
    s=Image.new("L",alpha_img.size,0); s.paste(m,off)
    s=s.filter(ImageFilter.GaussianBlur(blur))
    sh.putalpha(s.point(lambda p:int(p*dark/255)))
    return sh

# ---------- BEAT A : Altarme river -------------------------------------------
D_RIVER=10.0
RH=1180; RW=int(1200*RH/1800); RX=1300-RW//2; RY=(H-RH)//2      # torn river, right
OX=(1196,516); LAB=(1470,300)                                   # ox-bow + label anchor

def _hand_path(p0,p1,seed,npts=90,wob=6.0):
    rng=np.random.default_rng(seed)
    t=np.linspace(0,1,npts)
    # a gently bowed leader line with hand wobble
    mx=(p0[0]+p1[0])/2+rng.uniform(-30,30); my=(p0[1]+p1[1])/2+rng.uniform(-40,-10)
    xs=(1-t)**2*p0[0]+2*(1-t)*t*mx+t**2*p1[0]
    ys=(1-t)**2*p0[1]+2*(1-t)*t*my+t**2*p1[1]
    xs=xs+np.sin(t*11+rng.uniform(0,6))*wob*0.5
    ys=ys+np.cos(t*9 +rng.uniform(0,6))*wob*0.5
    return list(zip(xs.tolist(),ys.tolist()))

def _ring(cx,cy,rx,ry,seed,npts=200,gap=0.5):
    rng=np.random.default_rng(seed)
    a0=-math.pi/2+gap/2
    th=np.linspace(a0,a0+2*math.pi-gap,npts)
    amp=rng.uniform(0.02,0.06,4); ph=rng.uniform(0,2*math.pi,4); frq=np.array([1,2,3,5])
    rad=1+sum(amp[k]*np.sin(th*frq[k]+ph[k]) for k in range(4))
    xs=cx+np.cos(th)*rx*rad; ys=cy+np.sin(th)*ry*rad
    return list(zip(xs.tolist(),ys.tolist()))

def _draw_progress(d,pts,frac,col,w1,w2,a1=235,a2=120):
    k=int(len(pts)*max(0.0,min(1.0,frac)))
    if k<2: return
    seg=pts[:k]
    d.line(seg,fill=col+(a1,),width=w1,joint="curve")
    d.line([(x+1.6,y+1.1) for x,y in seg],fill=col+(a2,),width=w2,joint="curve")

def river_frames():
    base=_paper(7); dbg=ImageDraw.Draw(base)
    # GHOST word behind the river
    _tsp(dbg,(140,606),"SCHLINGEN",_anton(300),(157,166,167),4)
    # torn river cut-out + its drop shadow
    riv=Image.open(IMG/"river.png").convert("RGBA").resize((RW,RH),Image.LANCZOS)
    base.alpha_composite(_shadow(riv,off=(10,14),blur=11,dark=90),(RX,RY))
    base.alpha_composite(riv,(RX,RY))
    # gentle vignette-ish darken at the far edges baked lightly (rest in ffmpeg)
    base_rgb=base.convert("RGB")
    lead=_hand_path((LAB[0]-18,LAB[1]+150),OX,seed=3)
    ring=_ring(OX[0],OX[1],92,74,seed=9)
    n=int(D_RIVER*FPS)
    for i in range(n):
        t=i/FPS; im=base_rgb.copy().convert("RGBA")
        # --- persistent left masthead block ---
        aM=ease((t-0.35)/0.6)
        if aM>0:
            _tsp_a(im,(98,92),"FLUSS · SCHLINGE · ABSCHNÜRUNG",_libb(27),INK,6,int(255*aM))
            _tsp_a(im,(94,132),"ALTARME",_anton(150),INK,2,int(255*aM))
        # --- body column (fades in, then out before the pivot) ---
        aB=ease((t-0.7)/0.7)*(1-ease((t-6.0)/0.5))
        if aB>0.01:
            body=["Ein Fluss pendelt seitlich. An der",
                  "Außenseite jeder Schlinge trägt er ab,",
                  "an der Innenseite lagert er an —",
                  "bis der Bogen sich selbst abschnürt.",
                  "Was bleibt, ist ein stiller, halbmond-",
                  "förmiger See:  der Altarm."]
            _body(im,(100,336),body,_libr(31),INK2,44,0,int(255*aB))
        # --- red-orange ox-bow annotation IN FRONT ---
        d=ImageDraw.Draw(im,"RGBA")
        fr=ease((t-1.6)/1.4)
        if fr>0:
            _draw_progress(d,lead,min(1.0,fr*1.6),ORG,4,3)
            if fr>0.5: _draw_progress(d,ring,ease((fr-0.5)/0.5),ORG,7,4)
        aL=ease((t-2.6)/0.5)
        if aL>0.01:
            _tsp_a(im,(LAB[0]-6,LAB[1]+52),"hier schnürt sich",_libb(26),ORG,2,int(255*aL))
            _tsp_a(im,(LAB[0]-6,LAB[1]+86),"der Bogen ab",_libb(26),ORG,2,int(255*aL))
        # --- pivot statement (replaces the body) ---
        aP=ease((t-6.3)/0.6)
        if aP>0.01:
            _tsp_a(im,(100,336),"der fleißigste Seebauer",_libb(30),INK,1,int(255*aP))
            _tsp_a(im,(100,372),"der Gegenwart —",_libb(30),INK,1,int(255*aP))
            _tsp_a(im,(94,420),"WIR",_anton(190),INK,2,int(255*aP))
            _tsp_a(im,(94,610),"SELBST.",_anton(190),YEL,2,int(255*aP))
        # caption tag, persistent
        if t>0.9:
            _tsp_a(im,(100,1006),"Abb. 14 · Altarm — Oxbow — Bras mort",_libr(24),INK2,2,235)
        im.convert("RGB").save(RF/f"r_{i:04d}.png")
    print("river_frames",n)

# ---------- BEAT B : Tagebau Hambach time-lapse ------------------------------
D_TAG=8.5
TWH=1030; TWW=int(720*TWH/1280); TWX=1332-TWW//2; TWY=(H-TWH)//2   # torn window

def _torn_mask(w,h,seed=5,bite=10):
    rng=np.random.default_rng(seed)
    m=Image.new("L",(w,h),0); d=ImageDraw.Draw(m)
    d.rectangle([bite,bite,w-bite,h-bite],fill=255)
    # eat ragged bites out of each edge
    def edge(n,horizontal,near0):
        for _ in range(n):
            if horizontal:
                x=rng.integers(0,w); r=rng.integers(3,bite+6)
                y=(0 if near0 else h)
                d.ellipse([x-r,y-r,x+r,y+r],fill=0)
            else:
                y=rng.integers(0,h); r=rng.integers(3,bite+6)
                x=(0 if near0 else w)
                d.ellipse([x-r,y-r,x+r,y+r],fill=0)
    for hor,n0 in [(True,True),(True,False),(False,True),(False,False)]:
        edge(60,hor,n0)
    return m.filter(ImageFilter.GaussianBlur(1.2))

def tagebau_frames():
    base=_paper(11); dbg=ImageDraw.Draw(base)
    _tsp(dbg,(120,470),"LAUSITZ",_anton(300),(158,167,168),8)      # ghost behind window
    mask=_torn_mask(TWW,TWH,seed=5,bite=12)
    # a shadow for the window frame (static)
    winshadow=Image.new("RGBA",(W,H),(0,0,0,0))
    tmp=Image.new("RGBA",(TWW,TWH),(0,0,0,0)); tmp.putalpha(mask)
    base.alpha_composite(_shadow(tmp,off=(10,14),blur=12,dark=95),(TWX,TWY))
    base_rgb=base.convert("RGB")
    raws=sorted(TRAW.glob("t_*.png"))
    lead=_hand_path((1140,300),(TWX+TWW*0.42,TWY+TWH*0.42),seed=2)
    n=int(D_TAG*FPS)
    for i in range(n):
        t=i/FPS; im=base_rgb.copy().convert("RGBA")
        # the time-lapse frame into the torn window
        src=raws[min(i,len(raws)-1)]
        clip=ImageOps.fit(Image.open(src).convert("RGB"),(TWW,TWH),Image.LANCZOS).convert("RGBA")
        clip.putalpha(mask)
        im.alpha_composite(clip,(TWX,TWY))
        # left type
        aM=ease((t-0.3)/0.6)
        if aM>0:
            _tsp_a(im,(100,92),"LAUSITZ · RUND UM LEIPZIG",_libb(27),INK,6,int(255*aM))
            _tsp_a(im,(96,132),"TAGEBAU",_anton(150),INK,2,int(255*aM))
            _tsp_a(im,(96,286),"WIRD SEE",_anton(150),INK,2,int(255*aM))
        aB=ease((t-0.9)/0.7)
        if aB>0.01:
            body=["Die alten Braunkohle-Tagebaue",
                  "laufen voll — Grundwasser steigt,",
                  "die Restlöcher werden geflutet."]
            _body(im,(100,470),body,_libr(31),INK2,44,0,int(255*aB))
        # front annotation
        d=ImageDraw.Draw(im,"RGBA")
        fr=ease((t-1.4)/1.3)
        if fr>0: _draw_progress(d,lead,fr,ORG,4,3)
        aL=ease((t-2.4)/0.5)
        if aL>0.01:
            _tsp_a(im,(940,258),"läuft voll",_libb(27),ORG,2,int(255*aL))
            _tsp_a(im,(940,292),"→ neuer See",_libb(27),ORG,2,int(255*aL))
        # yellow punch reveal
        aY=ease((t-4.2)/0.6)
        if aY>0.01:
            _tsp_a(im,(96,640),"RIESIG.",_anton(150),YEL,2,int(255*aY))
            _tsp_a(im,(96,792),"BRANDNEU.",_anton(150),YEL,2,int(255*aY))
        if t>0.9:
            _tsp_a(im,(100,1006),"Abb. 15 · Braunkohletagebau → See · Zeitraffer",_libr(24),INK2,2,235)
        im.convert("RGB").save(TF/f"t_{i:04d}.png")
    print("tagebau_frames",n)

if __name__=="__main__":
    import sys
    steps=sys.argv[1:] or ["river","tag"]
    if "river" in steps: river_frames()
    if "tag"   in steps: tagebau_frames()
